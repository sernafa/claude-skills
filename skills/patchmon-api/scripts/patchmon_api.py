#!/usr/bin/env python3
"""PatchMon 2.x HTTPS REST-only client; scoped/GetHomepage Basic, agent, auto-enrollment and JWT auth profiles; TLS certificate verification optional via PATCHMON_CA_BUNDLE."""
import argparse
import base64
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

WRITE_METHODS = {"POST", "PATCH", "PUT", "DELETE"}
MAX_INLINE_BYTES = 10_000_000
MAX_DOWNLOAD_BYTES = 1_000_000_000
API_PREFIX = "/api/v1"
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
SECRET_KEYS = {"api_key", "apiKey", "token_secret", "tokenSecret"}
CREDENTIAL_QUERY_PARAMS = {"token_key", "token_secret", "api_key", "apikey", "api_id", "key", "secret"}
SCRIPT_ENDPOINTS = {
    f"{API_PREFIX}/hosts/install",
    f"{API_PREFIX}/hosts/agent/download",
    f"{API_PREFIX}/auto-enrollment/script",
}
AUTH_PROFILES = ("scoped", "gethomepage", "agent", "enroll", "bearer", "none")


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(2)


SKILL_NAME = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read_env_file(path):
    """Yield KEY=VALUE pairs from a dotenv-style file; blanks and # comments ignored.
    ${VAR} references in values are expanded against already-known values, so a
    shared secrets file can alias the skill's variable names."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                    value = value[1:-1]
                value = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
                               lambda m: os.environ.get(m.group(1), ""), value)
                if key:
                    yield key, value
    except OSError:
        return


def load_secrets():
    """Fill connection variables missing from the environment: exported
    environment wins, then ~/.config/secrets/.env.<skill-name>, then
    ~/.config/secrets/.env. Write-approval flags are never loaded from files."""
    secrets_dir = os.path.join(os.path.expanduser("~"), ".config", "secrets")
    for filename in (f".env.{SKILL_NAME}", ".env"):
        for key, value in _read_env_file(os.path.join(secrets_dir, filename)):
            if key.endswith("_ALLOW_WRITE"):
                continue
            os.environ.setdefault(key, value)


def build_context():
    bundle = os.environ.get("PATCHMON_CA_BUNDLE", "").strip()
    if bundle:
        return ssl.create_default_context(cafile=bundle)
    return ssl._create_unverified_context()  # Default: server identity not verified (MITM risk; see SKILL.md).


def parse_target_path(raw):
    """Return (path, query) for a documented PatchMon endpoint.

    Accepts the full documented form (/api/v1/api/hosts) and the OpenAPI
    spec-relative form (/api/hosts, /gethomepage/stats, /hosts/ping, ...),
    prefixing the latter with /api/v1. Rejects URLs, traversal and
    credential-looking query parameters (auth always travels in headers)."""
    split = urllib.parse.urlsplit(raw)
    if split.scheme or split.netloc or split.fragment or "\\" in raw:
        fail("Path must be a documented PatchMon path, not a URL")
    path = split.path
    if not path.startswith("/"):
        fail("Path must begin with /")
    if path != API_PREFIX and not path.startswith(API_PREFIX + "/"):
        path = API_PREFIX + path
    if any(seg in (".", "..") for seg in path.split("/")):
        fail("Path must not contain '.' or '..' segments")
    if split.query:
        names = {name.lower() for name, _ in urllib.parse.parse_qsl(split.query, keep_blank_values=True)}
        forbidden = names & CREDENTIAL_QUERY_PARAMS
        if forbidden:
            fail(f"Credential query parameters are not allowed ({', '.join(sorted(forbidden))}); "
                 "this client authenticates via headers only")
    return path, split.query


def detect_profile(path):
    """Pick the auth profile a documented path belongs to; None when unknown."""
    if path.startswith(f"{API_PREFIX}/api/"):
        return "scoped"
    if path.startswith(f"{API_PREFIX}/gethomepage/"):
        return "gethomepage"
    if path == f"{API_PREFIX}/auto-enrollment/tokens" or path.startswith(f"{API_PREFIX}/auto-enrollment/tokens/"):
        return "bearer"
    if path.startswith(f"{API_PREFIX}/auto-enrollment/"):
        return "enroll"
    if path == f"{API_PREFIX}/hosts/bootstrap/exchange":
        return "none"
    parts = path.split("/")
    if (len(parts) == 7 and parts[1:4] == ["api", "v1", "hosts"] and UUID_RE.match(parts[4])
            and parts[5] == "identity-conflict" and parts[6] == "dismiss"):
        return "bearer"  # web-UI endpoint living under /hosts/, not an agent endpoint
    if path.startswith(f"{API_PREFIX}/hosts/") or path.startswith(f"{API_PREFIX}/integrations/"):
        return "agent"
    return None


def _require(name):
    value = os.environ.get(name, "").strip()
    if not value:
        fail(f"{name} must be set for this auth profile (see SKILL.md credential discovery order)")
    return value


def build_headers(profile):
    headers = {"Accept": "application/json"}
    if profile == "scoped":
        credentials = base64.b64encode(
            f"{_require('PATCHMON_TOKEN_KEY')}:{_require('PATCHMON_TOKEN_SECRET')}".encode()
        ).decode()
        headers["Authorization"] = f"Basic {credentials}"
    elif profile == "gethomepage":
        credentials = base64.b64encode(
            f"{_require('PATCHMON_GETHOMEPAGE_KEY')}:{_require('PATCHMON_GETHOMEPAGE_SECRET')}".encode()
        ).decode()
        headers["Authorization"] = f"Basic {credentials}"
    elif profile == "agent":
        headers["X-API-ID"] = _require("PATCHMON_API_ID")
        headers["X-API-KEY"] = _require("PATCHMON_API_KEY")
    elif profile == "enroll":
        headers["X-Auto-Enrollment-Key"] = _require("PATCHMON_ENROLL_KEY")
        headers["X-Auto-Enrollment-Secret"] = _require("PATCHMON_ENROLL_SECRET")
    elif profile == "bearer":
        headers["Authorization"] = f"Bearer {_require('PATCHMON_JWT')}"
    return headers


def stream_to_file(response, output_path):
    fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    written = 0
    with os.fdopen(fd, "wb") as out:
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            out.write(chunk)
            written += len(chunk)
            if written > MAX_DOWNLOAD_BYTES:
                fail("Download exceeded 1 GB; aborting")
    return written


def fetch(method, url, headers, body=None, timeout=30, output_path=None):
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=timeout, context=build_context())
    except urllib.error.HTTPError as e:
        status = e.code
        content_type = (e.headers or {}).get("Content-Type", "")
        raw = e.read(MAX_INLINE_BYTES + 1)
        e.close()
        return status, content_type, raw, None
    except urllib.error.URLError as e:
        fail(f"HTTPS request failed ({type(e.reason).__name__}); check connectivity and HTTPS settings")
    with response:
        status = response.status
        content_type = response.headers.get("Content-Type", "")
        if output_path is not None:
            return status, content_type, None, stream_to_file(response, output_path)
        raw = response.read(MAX_INLINE_BYTES + 1)
        return status, content_type, raw, None


def mask_value(value):
    if len(value) < 12:
        return "****"
    return f"{value[:4]}...{value[-4:]} (masked)"


def mask_secrets(obj):
    if isinstance(obj, dict):
        return {
            key: (mask_value(value) if key in SECRET_KEYS and isinstance(value, str) else mask_secrets(value))
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [mask_secrets(item) for item in obj]
    return obj


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("method", choices=["GET", "POST", "PATCH", "PUT", "DELETE"])
    ap.add_argument("path", help="Documented PatchMon path, e.g. /api/v1/api/hosts "
                                 "(OpenAPI spec-relative forms such as /api/hosts are accepted and prefixed with /api/v1)")
    ap.add_argument("--auth", choices=AUTH_PROFILES, default=None,
                    help="Override the auth profile inferred from the path "
                         "(scoped|gethomepage|agent|enroll|bearer|none)")
    ap.add_argument("--body-file", default=None,
                    help="Local JSON file with the request body (no credentials inside)")
    ap.add_argument("--empty-body", action="store_true",
                    help="Allow a body-less POST/PATCH (agent heartbeat)")
    ap.add_argument("--confirm-write", action="store_true")
    ap.add_argument("--expected-host", default=None)
    ap.add_argument("--output", default=None,
                    help="Write the raw response body to this file (created 0600); required in practice for "
                         "scripts and agent binaries, which are never printed inline")
    ap.add_argument("--reveal-secrets", action="store_true",
                    help="Print credential fields in full instead of masking (only at the user's explicit request)")
    ap.add_argument("--timeout", type=float, default=30)
    args = ap.parse_args()

    load_secrets()
    host = os.environ.get("PATCHMON_HOST", "").strip()
    if not host:
        fail("PATCHMON_HOST must be set")
    if host.startswith("https://"):
        host = host[len("https://"):].rstrip("/")  # tolerate the https://host[:port] URL form
    expected = args.expected_host or ""
    if expected.startswith("https://"):
        expected = expected[len("https://"):].rstrip("/")
    if not host or host.startswith("http://") or any(x in host for x in "/?#@\\"):
        fail("PATCHMON_HOST must be hostname/IP optionally followed by port, or an https://host[:port] URL (no path)")

    path, query = parse_target_path(args.path)
    profile = args.auth or detect_profile(path)
    if profile is None:
        fail(f"Cannot infer the auth profile for {path}; pass --auth (one of: {', '.join(AUTH_PROFILES)})")

    if args.method in WRITE_METHODS:
        if not (args.confirm_write and os.getenv("PATCHMON_ALLOW_WRITE") == "YES" and expected == host):
            fail("Writes require PATCHMON_ALLOW_WRITE=YES, --confirm-write, and --expected-host matching PATCHMON_HOST")
        if args.method != "DELETE" and not args.body_file and not args.empty_body:
            fail("A JSON body file is required for this write (or --empty-body for a body-less agent heartbeat)")
    elif args.body_file or args.empty_body:
        fail("GET requests must not send a body")

    headers = build_headers(profile)

    body = None
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        body = json.dumps(payload, separators=(",", ":")).encode()
        headers["Content-Type"] = "application/json"

    url_path = urllib.parse.quote(path, safe="/._~-")
    if query:
        url_path += "?" + urllib.parse.quote(query, safe="=&,._~%-")
    url = f"https://{host}{url_path}"

    status, content_type, raw, written = fetch(
        args.method, url, headers, body=body, timeout=args.timeout, output_path=args.output
    )

    if args.output is not None:
        summary = {
            "http_status": status,
            "content_type": content_type,
            "bytes_written": written,
            "written_to": args.output,
        }
        if path in SCRIPT_ENDPOINTS:
            summary["note"] = ("Response body may embed credentials; file written with 0600 permissions; "
                               "never execute it")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        if len(raw) > MAX_INLINE_BYTES:
            fail("Response exceeded 10 MB; use --output or narrow the query")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            # Script or binary body: may embed credentials, so it is never printed inline.
            print(json.dumps({
                "http_status": status,
                "content_type": content_type,
                "bytes": len(raw),
                "note": "Non-JSON body (script or binary) is not printed; save it with --output",
            }, ensure_ascii=False, indent=2))
            if status >= 400:
                raise SystemExit(1)
            return
        payload = parsed if (args.reveal_secrets or parsed is None) else mask_secrets(parsed)
        print(json.dumps({"http_status": status, "response": payload}, ensure_ascii=False, indent=2))

    if status >= 400:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
