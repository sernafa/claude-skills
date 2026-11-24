# PatchMon Integration API — endpoint catalog

Target: **PatchMon 2.x**, OpenAPI "PatchMon Integration API 1.0.0". Base URL: `https://<host>/api/v1`.
Authoritative machine-readable source: `references/patchmon.openapi.json` (as supplied).
Verify shapes against the installed version before writing; error bodies carry `{"error": ...}` (and a machine-readable `code` on enrollment refusals).

## Auth domains

| Domain | Credential | Where it comes from | Endpoints |
| --- | --- | --- | --- |
| Scoped API | Basic auth `token_key:token_secret`, integration type `api` | Settings → Integrations → API (scopes `host:get`, `host:delete`) | `/api/v1/api/...` |
| GetHomepage | Basic auth, integration type `gethomepage` | Settings → Integrations → GetHomepage | `/api/v1/gethomepage/...` |
| Agent | `X-API-ID` + `X-API-KEY` headers | Per-host, issued at enrollment | `/api/v1/hosts/...`, `/api/v1/integrations/docker` |
| Auto-enrollment | `X-Auto-Enrollment-Key` + `X-Auto-Enrollment-Secret` headers | Settings → Integrations → Auto-Enrollment | `/api/v1/auto-enrollment/script`, `/enroll` |
| Web-UI / admin | `Authorization: Bearer <JWT>` | Signed-in user session token (browser login) | `/api/v1/auto-enrollment/tokens*`, `/api/v1/hosts/{id}/identity-conflict/dismiss` |

Rate limits: general API ~100 requests / 15 min / IP; per-token `max_hosts_per_day` (default 100, range 1–1000) counted only on host **creation**; per-IP agent limit ~1000/min; re-issue cooldown 60 s per host.

## Scoped API (Basic auth, `host:get` unless noted)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/api/hosts` | List hosts; `?hostgroup=` (comma-separated names/UUIDs, OR logic), `?include=stats` |
| GET | `/api/v1/api/hosts/{id}/stats` | Package/repo counters |
| GET | `/api/v1/api/hosts/{id}/info` | Identity, OS, agent + config version, groups |
| GET | `/api/v1/api/hosts/{id}/network` | IP, gateway, DNS, interfaces |
| GET | `/api/v1/api/hosts/{id}/system` | Arch, kernels, CPU/RAM, disks, `needs_reboot` |
| GET | `/api/v1/api/hosts/{id}/packages` | `?updates_only=true`; sorted security-first |
| GET | `/api/v1/api/hosts/{id}/package_reports` | `?limit=` (default 10, max 100) |
| GET | `/api/v1/api/hosts/{id}/agent_queue` | Queue counters + `?limit=` job history |
| GET | `/api/v1/api/hosts/{id}/notes` | Host notes text |
| GET | `/api/v1/api/hosts/{id}/integrations` | Docker integration detail |
| DELETE | `/api/v1/api/hosts/{id}` | **Cascade delete; `host:delete` scope; irreversible** |

`{id}` is a host UUID. Errors: `400` invalid UUID, `401` auth, `403` scope/IP, `404` host not found, `500` server. Observed on a live PatchMon 2.1.x instance: `GET .../stats` for an unknown UUID answers `200` with zeroed counters instead of the documented `404`, while `/info` and the other per-host endpoints do return `404` — validate host IDs with `GET /api/hosts` (or `/info`), never with `/stats`.

Key response fields — `GET /api/hosts?include=stats`: per host `id`, `friendly_name`, `hostname`, `ip`, `host_groups[]`, `os_type`, `os_version`, `last_update`, `status`, `effective_status`, `reporting_state`, `update_state`, `needs_reboot`, `updates_count`, `security_updates_count`, `total_packages`; top level `total` and `filtered_by_groups` (only when filtering).

Status semantics (see SKILL.md): `status` is the enrollment lifecycle (`pending` before first check-in, then `active` forever, never `inactive`); `effective_status` mirrors the web UI (`pending|active|inactive`); `reporting_state` is freshness (`reporting|overdue|stale`); `update_state` is patch position (`up_to_date|updates_pending|security_required`). `effective_status` requires PatchMon ≥ 2.0.3.

`GET .../info`: adds `machine_id`, `agent_version`, `config_version` (config.yml schema version last reported, agents ≥ 2.1.4; empty string when unknown).
`GET .../packages`: package objects with `name`, `description`, `category`, `current_version`, `available_version`, `needs_update`, `is_security_update`, `last_checked`.
`GET .../package_reports`: reports with `status`, `date`, `total_packages`, `outdated_packages`, `security_updates`, `payload_kb`, `execution_time_seconds`, `error_message`.
`GET .../agent_queue`: `queue_status` (`waiting/active/delayed/failed`) + `job_history[]` (`job_name`, `status`, `attempt`, `created_at`, `completed_at`, `error_message`).

DELETE response: `{"message", "deleted": {"id", "friendly_name", "hostname"}}`. The cascade removes packages, repositories, update history, Docker data, job history and group memberships.

## GetHomepage (Basic auth, `gethomepage` integration type)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/gethomepage/stats` | Widget payload |
| GET | `/api/v1/gethomepage/health` | Liveness: `{"status": "ok", "timestamp", "api_key": <token name>}` |

`stats` fields: `total_hosts` (includes created-but-never-enrolled hosts), `total_outdated_packages`, `total_repos`, `hosts_needing_updates`, `up_to_date_hosts`, `security_updates`, `hosts_with_security_updates`, `recent_updates_24h`, `os_distribution[]` (`name`, `count`, `os_type`, `os_version`), `top_os_1..3_name/_count`, `last_updated`. A `gethomepage` credential is rejected on scoped endpoints and vice versa.

## Agent endpoints (`X-API-ID` + `X-API-KEY`)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/hosts/install?force=&arch=` | Install script (text/plain; embeds a single-use bootstrap token, 5-min expiry; save with `--output`) |
| GET | `/api/v1/hosts/agent/version?arch=&type=&currentVersion=` | Agent version check: `currentVersion`, `latestVersion`, `hasUpdate`, `autoUpdateDisabled`, `downloadUrl`, `releaseNotes`, `hash` |
| GET | `/api/v1/hosts/agent/download?force=&arch=` | Agent binary (application/octet-stream; `--output`) |
| POST | `/api/v1/hosts/ping` | Heartbeat; body optional (`--empty-body`); optional body fields `triggerCrontabUpdate`, `hostId`, `configVersion`, `machineId`. Response always carries `hostId`; `hostIdMismatch: true` flags a config/credentials mismatch |
| POST | `/api/v1/hosts/update` | Full/partial agent report: `packages[]` (max 10 000: `name`, `currentVersion`, `availableVersion`, `needsUpdate`, `isSecurityUpdate`), `agentVersion`, `osType/osVersion`, `hostname`, `ip`, hardware, network, kernels, `machineId`, `hostId`, `configVersion`, `needsReboot`, `rebootReason`, `repositories`, `executionTime`. Response: counts + `hostId` |
| GET | `/api/v1/hosts/integrations` | `{"integrations": {"docker": bool, "compliance": bool}, "compliance_mode", ...}` |
| POST | `/api/v1/integrations/docker` | Body `{"containers": [], "images": []}`; response carries received counts |
| POST | `/api/v1/hosts/integration-status` | Free-form object status report |
| POST | `/api/v1/hosts/bootstrap/exchange` | Body `{"token": ...}` (bootstrap token, no auth headers) → `{"apiId", "apiKey"}` — **plaintext credentials** |

`POST /hosts/update` and `POST /hosts/ping` accept a `hostId` differing from the authenticated host: the report succeeds but the host is flagged with a host ID mismatch (possible clone). Do not treat that as a failure.

## Auto-enrollment (enrollment token headers)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/auto-enrollment/script?type=direct-host\|proxmox-lxc&force=` | Enrollment script (text; embeds token credentials; save with `--output`; never execute without approval). Auth via headers or query params — this client only uses headers |
| POST | `/api/v1/auto-enrollment/enroll` | Enroll a host, or re-issue credentials for a never-reported host created by the same token |

`POST /enroll` body: `friendly_name` (required, max 255), `machine_id` (optional, dedupe key), `host_id` (optional, 1–64 letters/digits/hyphens, from the machine's `config.yml` — never used as a new host's ID), `metadata` (optional object).

Responses:
- `201` — new host: `host` object with `id`, `friendly_name`, `api_id`, **`api_key` (plaintext, shown once)**, `host_group` (null when the token has no default group), `status: "pending"`.
- `200` — credentials re-issued for the host named by `host_id` (same token, never reported, same `machine_id`): same shape plus `reenrolled: true`; the host keeps its ID and `api_id`; the old key stops working; the daily limit is neither checked nor consumed.
- `409` — refused, nothing created. `code`: `machine_id_match` (no `host_id` sent; a host with the same `machine_id` and name exists), `host_reporting` (the `host_id` host already reported or connected — never re-keyed by enrollment), `host_not_reenrollable` (created by another token, in the UI, before 2.1.4, or different `machine_id`). Bodies carry `host_id` and, when applicable, `friendly_name`.
- `429` — `reenrol_cooldown` (re-issue < 60 s ago; do not auto-retry) or the token's `max_hosts_per_day` limit (`"error": "Rate limit exceeded"`).
- `400` — validation (missing `friendly_name`; invalid `host_id`). `401` — missing/invalid/inactive/expired token. `403` — IP not in the token's allowlist.

Scripts re-run on an enrolled host skip working agents, reuse accepted credentials, and otherwise re-enroll via `host_id` so a never-reported host gets new credentials instead of a duplicate. `FORCE_NEW_HOST=true` forces a brand-new host and moves the old config aside. On hosts without `/etc/machine-id`, a stable ID is kept in `/var/lib/patchmon/machine-id`.

## Admin / web-UI endpoints (JWT Bearer, user session)

Not in the OpenAPI file; documented in the integrations guide (Auto-Enrollment API, chapter 6). Requires a signed-in user session token and, unless noted, the `can_manage_settings` permission.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/auto-enrollment/tokens` | List tokens (descending creation; never includes `token_secret`): `token_name`, `token_key`, `is_active`, `max_hosts_per_day`, `hosts_created_today`, `last_used_at`, `expires_at`, `allowed_ip_ranges`, `default_host_group_id`, `metadata` |
| POST | `/api/v1/auto-enrollment/tokens` | Create token: `token_name` (required), `max_hosts_per_day` (1–1000, default 100), `default_host_group_id`, `allowed_ip_ranges[]`, `expires_at`, `metadata`; response includes **`token_secret` once** |
| GET | `/api/v1/auto-enrollment/tokens/{tokenId}` | Token detail |
| PATCH | `/api/v1/auto-enrollment/tokens/{tokenId}` | Update any subset: `token_name`, `is_active`, `max_hosts_per_day`, `allowed_ip_ranges`, `default_host_group_id` (empty string clears), `expires_at`, `scopes` |
| DELETE | `/api/v1/auto-enrollment/tokens/{tokenId}` | **Delete token — all future enrollments with it fail; separate confirmation** |
| POST | `/api/v1/hosts/{hostId}/identity-conflict/dismiss` | Clear the possible-clone flag (`can_manage_hosts`). Dismissing does not change credentials; the flag returns if two machines keep alternating |

## Common error reference

| Message | HTTP | Cause / fix |
| --- | --- | --- |
| `Missing or invalid authorization header` | 401 | No `Authorization: Basic` header; check credential pairing |
| `Invalid API key` / `Invalid token` | 401 | Key not found, disabled or expired |
| `Invalid API key type` | 401 | Credential integration type does not match the endpoint domain |
| `Invalid API secret` / `Invalid token secret` | 401 | Secret mismatch (bcrypt; not recoverable — recreate) |
| `IP address not allowed` / `not authorized for this token` | 403 | Client IP outside the credential/token allowlist |
| `Access denied: does not have permission to {action} {resource}` | 403 | Missing scope, e.g. `host:delete` |
| `Host not found` | 404 | Unknown host UUID |
| `Invalid host ID format` | 400 | Not a UUID |
| `Rate limit exceeded` | 429 | General API limit (100/15 min/IP) or token daily limit |
| `Too many requests. Try again later.` | 429 | Per-IP agent limit; `Retry-After` header set |
