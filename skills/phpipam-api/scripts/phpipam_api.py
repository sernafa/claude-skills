#!/usr/bin/env python3
"""phpIPAM 1.8 HTTPS REST-only client; token auth; TLS certificate verification optional via PHPIPAM_CA_BUNDLE."""
import argparse
import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

WRITE_METHODS = {"POST", "PATCH", "DELETE"}
MAX_RESPONSE_BYTES = 10_000_000


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(2)


def build_context():
    bundle = os.environ.get("PHPIPAM_CA_BUNDLE", "").strip()
    if bundle:
        return ssl.create_default_context(cafile=bundle)
    return ssl._create_unverified_context()  # Default: server identity not verified (MITM risk; see SKILL.md).


def fetch(method, url, headers, body=None, timeout=20):
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=build_context()) as response:
            status = response.status
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as e:
        status = e.code
        raw = e.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.URLError as e:
        fail(f"HTTPS request failed ({type(e.reason).__name__}); check connectivity and HTTPS settings")
    if len(raw) > MAX_RESPONSE_BYTES:
        fail("Response exceeded 10 MB; narrow the query")
    try:
        parsed = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        fail(f"HTTP {status}: non-JSON response (body suppressed)")
    return status, parsed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("method", choices=["GET", "POST", "PATCH", "DELETE"])
    ap.add_argument("path", help="Documented phpIPAM path beginning with /api/<app>/")
    ap.add_argument("--body-file", default=None)
    ap.add_argument("--confirm-write", action="store_true")
    ap.add_argument("--expected-host", default=None)
    ap.add_argument("--timeout", type=float, default=20)
    args = ap.parse_args()

    host = os.environ.get("PHPIPAM_HOST", "").strip()
    app = os.environ.get("PHPIPAM_APP_ID", "").strip()
    token = os.environ.get("PHPIPAM_TOKEN", "").strip()
    username = os.environ.get("PHPIPAM_USERNAME", "").strip()
    password = os.environ.get("PHPIPAM_PASSWORD", "")
    if not host or not app:
        fail("PHPIPAM_HOST and PHPIPAM_APP_ID must be set")
    if host.startswith(("http://", "https://")) or any(x in host for x in "/?#@\\"):
        fail("PHPIPAM_HOST must be only hostname/IP optionally followed by port")
    if any(not c.isalnum() and c not in "-_" for c in app):
        fail("PHPIPAM_APP_ID must contain only letters, digits, hyphens or underscores")

    prefix = f"/api/{app}/"
    parts = urllib.parse.urlsplit(args.path)
    if not args.path.startswith(prefix) or parts.scheme or parts.netloc or "\\" in args.path \
            or any(seg in (".", "..") for seg in parts.path.split("/")):
        fail(f"Path must be a clean documented path beginning with {prefix}")
    if not parts.path.endswith("/"):
        fail(f"Path must end with '/' (phpIPAM convention, e.g. {prefix}subnets/)")
    if args.method in WRITE_METHODS:
        if not (args.confirm_write and os.getenv("PHPIPAM_ALLOW_WRITE") == "YES" and args.expected_host == host):
            fail("Writes require PHPIPAM_ALLOW_WRITE=YES, --confirm-write, and --expected-host matching PHPIPAM_HOST")
        if not args.body_file and args.method != "DELETE":
            fail("A JSON body file is required for this write")
    elif args.body_file:
        fail("GET requests must not send a body")

    headers = {"Accept": "application/json"}
    if not token:
        if not (username and password):
            fail("Set PHPIPAM_TOKEN, or PHPIPAM_USERNAME and PHPIPAM_PASSWORD for token authentication")
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        status, parsed = fetch("POST", f"https://{host}{prefix}user/",
                               {"Accept": "application/json", "Authorization": f"Basic {credentials}"},
                               timeout=args.timeout)
        if status >= 400 or not isinstance(parsed, dict) or parsed.get("success") is not True:
            print(json.dumps({"http_status": status, "response": parsed}, ensure_ascii=False, indent=2))
            fail("Token authentication failed")
        token = (parsed.get("data") or {}).get("token", "")
        if not token:
            fail("Authentication response contained no token")
    headers["phpipam-token"] = token

    body = None
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        body = json.dumps(payload, separators=(",", ":")).encode()

    path = urllib.parse.quote(parts.path, safe="/._~%-")
    if parts.query:
        path += "?" + urllib.parse.quote(parts.query, safe="=&._~%-")
    status, parsed = fetch(args.method, f"https://{host}{path}", headers, body=body, timeout=args.timeout)
    print(json.dumps({"http_status": status, "response": parsed}, ensure_ascii=False, indent=2))
    if status >= 400 or (isinstance(parsed, dict) and parsed.get("success") is False):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
