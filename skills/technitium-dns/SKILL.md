---
name: technitium-dns
description: Manage a Technitium DNS Server through its HTTP API — authoritative zones and resource records, DNSSEC, conditional forwarders, DNS cache, allowed and blocked zones, block lists, DNS apps, server settings and backups, DHCP leases and scopes, users and permissions, cluster operations, and query logs. Use it when the user asks to create, update or delete zones or records, block or allow domains, flush the cache, check dashboard stats, resolve test queries, manage DHCP, inspect logs, or automate anything otherwise done in the Technitium web console.
---

# Technitium DNS Server API

Technitium DNS Server exposes an HTTP API which is the same one its web console
uses: any action doable in the console is automatable here with `curl` + `jq`.

- Default address: `http://localhost:5380`. Use the hostname/IP and port of the
  actual instance.
- Full upstream reference: `APIDOCS.md` in
  `github.com/TechnitiumSoftware/DnsServer` (this skill covers the common
  calls; the docs have every parameter).

## Golden rules

1. **Never run destructive calls without the user's confirmation**:
   `zones/delete`, `zones/dnssec/unsign`, `blocked/flush`, `allowed/flush`,
   `cache/flush`, `logs/deleteAll`, `dashboard/stats/deleteAll`,
   `settings/restore` (with `deleteExistingFiles=true`), `admin/users/delete`,
   and all cluster membership calls (`cluster/init`, `secondary/leave`,
   `primary/removeSecondary`, ...).
2. **Credentials and tokens never go into the repo.** Use environment
   variables: `TECHNIUM_URL` (default `http://localhost:5380`) and
   `TECHNIUM_TOKEN`. If they are unset, ask the user — do not guess.
3. **Always check the response envelope.** Every call returns JSON with
   `status`: `ok` on success, `error` (read `errorMessage`),
   `invalid-token` (session expired — re-authenticate),
   `2fa-required` (retry with the user's OTP code).
4. **`set` calls overwrite; `add` calls append.** Read the current value
   (`*/get`) before writing (`*/set`) so you don't wipe unrelated settings.
5. Almost every call accepts `GET` or `POST` with
   `Content-Type: application/x-www-form-urlencoded`. File uploads (zone
   import, settings restore) are always `POST` `multipart/form-data`.
6. **URL-encode every query parameter.** Prefer
   `curl -G "$BASE_URL/api/..." --data-urlencode "qname=$VALUE"` over manual
   string interpolation.
7. Prefer a **non-expiring API token** created once (see below) over session
   logins; a session token expires 30 minutes after the last call.

## Environment setup

Export before the first call (ask the user for values you don't have):

```sh
BASE_URL="${TECHNIUM_URL:-http://localhost:5380}"
TOKEN="${TECHNIUM_TOKEN:?TECHNIUM_TOKEN is not set — ask the user}"
api() { curl -fsS -H "Authorization: Bearer $TOKEN" "$@"; }
```

Discovering the server:

```sh
api "$BASE_URL/api/status"                    # no auth needed; warns hasDefaultCredentials
api "$BASE_URL/api/user/session/get"          # validate the token; shows username + permissions
api "$BASE_URL/api/settings/get" | jq '.response | {version, dnsServerDomain, uptimestamp}'
api "$BASE_URL/api/dnsClient/healthCheck"     # process up AND resolving
```

## Authentication

Create a non-expiring API token once (recommended for automation):

```sh
# 1. Log in to get a session token
api "$BASE_URL/api/user/login" -G \
  --data-urlencode "user=admin" \
  --data-urlencode "pass=$PASSWORD" | jq -r .token

# 2. Exchange it for a permanent API token
api -X POST "$BASE_URL/api/user/createToken" \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  --data-urlencode "tokenName=automation" | jq -r .token
```

If the account has 2FA, add `--data-urlencode "totp=$CODE"` to the login call.

## Zones and records

```sh
api -G "$BASE_URL/api/zones/list" --data-urlencode "filterName=example.com"
api "$BASE_URL/api/zones/create?zone=example.com&type=Primary"   # type: Primary, Secondary, Stub, Forwarder, Catalog, ...
api -G "$BASE_URL/api/zones/records/get" --data-urlencode "domain=example.com" | jq '.response.records[]'
api "$BASE_URL/api/zones/records/delete?domain=old.example.com&type=A"  # destructive
api "$BASE_URL/api/zones/export?zone=example.com" > zone.example.com   # zone file download
```

Add records with `zones/records/add` — params depend on the type:

```sh
# A / AAAA (ipAddress required; "request-ip-address" = caller IP, handy for DDNS)
api "$BASE_URL/api/zones/records/add?domain=www.example.com&type=A&ipAddress=192.168.1.10&ttl=300"

# CNAME / MX / TXT / SRV / CAA use their own params
api "$BASE_URL/api/zones/records/add?domain=docs.example.com&type=CNAME&cname=host.example.com"
api "$BASE_URL/api/zones/records/add?domain=example.com&type=MX&exchange=mail.example.com&preference=10"
api "$BASE_URL/api/zones/records/add?domain=example.com&type=TXT&text=v=spf1 -all"
```

Useful `records/add` options: `overwrite=true` (replace the record set
instead of adding), `ptr=true` + `createPtrZone=true` (auto reverse record),
`expiryTtl=<seconds>` (auto-delete), `comments`.

Conditional forwarders are `Forwarder` zones, or `FWD` records inside a zone:

```sh
api "$BASE_URL/api/zones/create?zone=internal.lan&type=Forwarder&forwarder=192.168.1.1&protocol=Udp&dnssecValidation=false"
```

## DNSSEC

```sh
api "$BASE_URL/api/zones/dnssec/sign?zone=example.com"
api "$BASE_URL/api/zones/dnssec/viewDS?zone=example.com"       # DS records for the parent
api "$BASE_URL/api/zones/dnssec/properties/get?zone=example.com"
```

`unsign` and the private-key/rollover calls under
`zones/dnssec/properties/*` change cryptography state — confirm first.

## Cache and filtering

```sh
api -G "$BASE_URL/api/cache/list" --data-urlencode "domain=google.com"   # inspect cache
api "$BASE_URL/api/cache/delete?domain=google.com"                        # evict one domain
api "$BASE_URL/api/cache/flush"                                           # destructive: clears everything

api "$BASE_URL/api/blocked/add?domain=ads.example.com"      # block a domain
api "$BASE_URL/api/blocked/delete?domain=ads.example.com"
api -G "$BASE_URL/api/blocked/list" --data-urlencode "domain=example.com"
api "$BASE_URL/api/allowed/add?domain=example.com"          # allow-list wins over blocking

api -X POST "$BASE_URL/api/settings/forceUpdateBlockLists"          # re-download block lists now
api "$BASE_URL/api/settings/temporaryDisableBlocking?minutes=15"    # pause filtering
```

`blocked/import` and `allowed/import` take a zone-file upload as
`multipart/form-data`; `blocked/export` / `allowed/export` return files.

## Resolve and dashboard

```sh
api -G "$BASE_URL/api/dnsClient/resolve" \
  --data-urlencode "server=this-server" \
  --data-urlencode "domain=example.com" \
  --data-urlencode "type=A" | jq '.response.result | {RCODE, Answer}'

# server: "this-server" (own config), "recursive-resolver", "system-dns", or a name server address
# protocol: Udp, Tcp, Tls, Https, Quic; add dnssec=true for validation
```

```sh
api "$BASE_URL/api/dashboard/stats/get" | jq '.response.stats'   # queries, rcodes, cached/blocked...
api "$BASE_URL/api/dashboard/stats/getTop"                       # top clients/domains/records
api "$BASE_URL/api/dashboard/metrics/json"                       # lifetime counters (experimental)
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/dashboard/metrics/text"  # Prometheus format
```

## Settings and backup

```sh
api "$BASE_URL/api/settings/get" > current-settings.json   # always read first
# then settings/set with ONLY the params being changed — it is a merge of the given fields
api -X POST "$BASE_URL/api/settings/set" --data-urlencode "dnsServerDomain=ns1.example.com"
```

Backups: `settings/backup` returns a zip (pick items with
`zones=true&scopes=true&dnsSettings=true&...`); `settings/restore` uploads it
back as `multipart/form-data` — destructive when `deleteExistingFiles=true`.

## DHCP

```sh
api "$BASE_URL/api/dhcp/leases/list"
api "$BASE_URL/api/dhcp/leases/convertToReserved?hardwareAddress=AA-BB-CC-DD-EE-FF"
api -G "$BASE_URL/api/dhcp/scopes/get" --data-urlencode "name=Default"
api -X POST "$BASE_URL/api/dhcp/scopes/set" -G --data-urlencode "name=Default" ...  # read scope first, send full object
api "$BASE_URL/api/dhcp/scopes/addReservedLease?name=Default&hardwareAddress=AA-BB-CC-DD-EE-FF&ipAddress=192.168.1.50&hostName=nas"
```

## Administration

Users, groups and permissions: `admin/users/*`, `admin/groups/*`,
`admin/permissions/*` (each with `list`, `get`, `create`/`set`, `delete`).
Sessions: `admin/sessions/list` and `admin/sessions/delete` to kick one.
Cluster (HA): `admin/cluster/state` to inspect; `init`, `join`, `leave`,
`promote`, `resync` change cluster membership — always confirm with the user.

## Query logs

Query logs are stored by a **DNS app** (the store ships "Query Logs
(Sqlite)") — a fresh server has none installed and `logs/query` fails with
`DNS application was not found` until one is installed:

```sh
api "$BASE_URL/api/apps/list" | jq -r '.response.apps[] | "\(.name)\t\(.classPath)"'

# then query with that app's exact name and classPath:
api -G "$BASE_URL/api/logs/query" \
  --data-urlencode "name=<app-name>" \
  --data-urlencode "classPath=<app-class-path>" \
  --data-urlencode "pageNumber=1" \
  --data-urlencode "entriesPerPage=50" \
  --data-urlencode "descendingOrder=true" \
  --data-urlencode "qname=example.com" | jq '.response.entries'
```

Optional filters: `start`/`end` (`yyyy-MM-dd HH:mm:ss`), `clientIpAddress`,
`protocol`, `responseType` (`Blocked`, `Cached`, `Recursive`, ...), `rcode`,
`qtype`. `logs/list` + `logs/download` handle the server's own text logs;
`logs/deleteAll` is destructive.

## Response conventions

- Success envelope: `{ "response": {...}, "status": "ok" }`; some calls return
  only `status`.
- List endpoints nest the payload under `response`:
  - `zones/list`, `zones/catalogs/list` → `.response.zones[]`
  - `zones/records/get`, `cache/list`, `allowed/list`, `blocked/list` →
    `.response.records[]`
  - `dashboard/stats/get` → `.response.stats` (plus `topClients`,
    `topDomains`, `topBlockedDomains`)
  - `apps/list` → `.response.apps[]`; `apps/listStoreApps` →
    `.response.storeApps[]`
  - `logs/query` → `.response.entries[]`
- Pagination: `pageNumber`, `totalPages` (`zones/list`, `logs/query`). Omit
  `pageNumber` on `zones/list` to get all zones in one shot.

## Name server address format

The API expects forwarders and `server` values in this text format:

- Plain IP or host: `1.1.1.1`, `dns.quad9.net:853`
- Host pinned to an IP: `dns.quad9.net (9.9.9.9)`
- DoH URL: `https://cloudflare-dns.com/dns-query (1.1.1.1)`
- IPv6 with port goes in brackets: `[2606:4700:4700::1111]:853`
- `this-server` means "this Technitium instance itself".
