#!/usr/bin/env python3
"""FortiOS 7.4 HTTPS REST-only client; TLS certificate verification disabled by request."""
import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

ALLOWED_PREFIXES = ("/api/v2/cmdb/", "/api/v2/monitor/")
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    ap.add_argument("path", help="Documented FortiOS /api/v2/cmdb/ or /api/v2/monitor/ path; three-word CLI nodes use dotted paths, e.g. /api/v2/cmdb/firewall.service/custom/<name>/")
    ap.add_argument("--vdom", default=None)
    ap.add_argument("--body-file", default=None)
    ap.add_argument("--confirm-write", action="store_true")
    ap.add_argument("--expected-host", default=None)
    ap.add_argument("--timeout", type=float, default=20)
    args = ap.parse_args()

    host = os.environ.get("FORTIGATE_HOST", "").strip()
    token = os.environ.get("FORTIGATE_API_TOKEN", "")
    if not host or not token:
        fail("FORTIGATE_HOST and FORTIGATE_API_TOKEN must be set")
    if host.startswith(("http://", "https://")) or any(x in host for x in "/?#@\\"):
        fail("FORTIGATE_HOST must be only hostname/IP optionally followed by port")
    if not args.path.startswith(ALLOWED_PREFIXES) or "?" in args.path or "#" in args.path:
        fail("Path must be a clean /api/v2/cmdb/ or /api/v2/monitor/ path; supply VDOM separately")
    parts = urllib.parse.urlsplit(args.path)
    if parts.scheme or parts.netloc or any(p in (".", "..") for p in args.path.split("/")):
        fail("Invalid path")
    if args.method in WRITE_METHODS:
        if not (args.confirm_write and os.getenv("FORTIGATE_ALLOW_WRITE") == "YES" and args.expected_host == host):
            fail("Writes require FORTIGATE_ALLOW_WRITE=YES, --confirm-write, and --expected-host matching FORTIGATE_HOST")
        if not args.body_file and args.method != "DELETE":
            fail("A JSON body file is required for this write")
    elif args.body_file:
        fail("GET requests must not send a body")
    if args.vdom and any(c in args.vdom for c in "\r\n"):
        fail("Invalid VDOM")

    data = None
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    query = urllib.parse.urlencode({"vdom": args.vdom}) if args.vdom else ""
    url = f"https://{host}{urllib.parse.quote(args.path, safe='/._~%-')}" + (f"?{query}" if query else "")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=args.method, headers=headers)
    context = ssl._create_unverified_context()  # User-requested: no CA or certificate warning.
    try:
        with urllib.request.urlopen(request, timeout=args.timeout, context=context) as response:
            status = response.status
            body = response.read(2_000_001)
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read(2_000_001)
    except urllib.error.URLError as e:
        fail(f"HTTPS request failed ({type(e.reason).__name__}); check connectivity and HTTPS settings")
    if len(body) > 2_000_000:
        fail("Response exceeded 2 MB; narrow the query")
    try:
        parsed = json.loads(body) if body else None
    except json.JSONDecodeError:
        fail(f"HTTP {status}: non-JSON response (body suppressed)")
    print(json.dumps({"http_status": status, "response": parsed}, ensure_ascii=False, indent=2))
    if status >= 400 or (isinstance(parsed, dict) and parsed.get("status") == "error"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
