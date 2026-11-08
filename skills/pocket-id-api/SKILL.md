---
name: pocket-id-api
description: Administer the Pocket-ID IdP instance (pocket-id.example.com) through its REST API — users, user groups, OIDC clients, app configuration, audit logs, signup tokens and version checks. Use when the user asks to inspect, create, modify or delete Pocket-ID resources, check the IdP version, or troubleshoot Pocket-ID.
---

# Pocket-ID Administration (pocket-id.example.com)

Guide for administering the user's Pocket-ID instance via its REST API.

## Connection and authentication

- **Base URL:** `$POCKET_ID_BASE_URL` (defaults to `https://pocket-id.example.com`)
- **API key:** `$POCKET_ID_API_KEY`
- **Auth header:** `X-API-KEY` — **NEVER** use `Authorization: Bearer`, it
  returns `401 {"error":"You are not signed in"}`.

```sh
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" "$POCKET_ID_BASE_URL/api/users"
```

**If `$POCKET_ID_API_KEY` is not set in the environment:** ask the user for the
key (it is found in Pocket-ID → Administration → API Keys). Never repeat it in
full in your replies or write it to any file; use it only in memory for the API
calls.

## API conventions

- Listings are paginated: `?pagination[page]=1&pagination[limit]=20`
  (URL-encode the brackets: `pagination%5Bpage%5D`). The response carries
  `{"data": [...], "pagination": {...}}`.
- Errors: `{"error": "...", "code": "...", "request_id": "..."}`. Trust `code`,
  not the message.
- `404 {"error":"API endpoint not found"}` = the route does not exist in the
  installed version. Check the version and review the available endpoints in
  `references/endpoints.md` and at https://pocket-id.org/docs/api/endpoints
- For the exact schema of POST/PUT bodies, consult the official docs before
  writing the request.

## Security rules

1. **Read-only by default.** Any POST/PUT/DELETE requires explicit user
   confirmation. Destructive DELETEs (users, OIDC clients, groups) require
   double confirmation.
2. **Never show full secrets** (API keys, client secrets, SMTP passwords):
   mask them, showing only the first/last 4 characters.
3. `/api/api-keys` **cannot be managed** while authenticated with an API key
   (403 `api_key_auth_not_allowed`). Direct the user to the admin UI to
   create/renew/revoke API keys.
4. If the user pastes an API key into the chat, suggest rotating it when the
   work is done if it is long-lived.

## Quick endpoint map

| Area | Endpoints |
|---|---|
| Version | `GET /api/version/current` · `GET /api/version/latest` |
| Users | `GET/POST /api/users` · `GET/PUT/DELETE /api/users/{id}` · `GET /api/users/{id}/groups` · `GET /api/users/{id}/webauthn-credentials` · `DELETE /api/users/{id}/webauthn-credentials/{credentialId}` · `POST /api/users/{id}/one-time-access-token` · `GET /api/users/me` |
| Groups | `GET/POST /api/user-groups` · `GET/PUT/DELETE /api/user-groups/{id}` · `PUT /api/user-groups/{id}/users` · `PUT /api/user-groups/{id}/allowed-oidc-clients` |
| OIDC clients | `GET/POST /api/oidc/clients` · `GET/PUT/DELETE /api/oidc/clients/{id}` · `PUT /api/oidc/clients/{id}/allowed-user-groups` · `GET/POST /api/oidc/clients/{id}/secrets` · `POST /api/oidc/clients/{id}/refresh` |
| Configuration | `GET /api/application-configuration/all` (all keys, incl. private ones) · `POST /api/application-configuration/test-email` · `POST /api/application-configuration/sync-ldap` |
| Audit | `GET /api/audit-logs/all` (all users) · `GET /api/audit-logs` (own) · filters: `/api/audit-logs/filters/users`, `/api/audit-logs/filters/client-names` |
| Signup | `GET/POST /api/signup-tokens` · `DELETE /api/signup-tokens/{id}` |
| APIs/permissions | `GET/POST /api/apis` · `/api/apis/{id}/permissions` · `/api/apis/{id}/clients` |
| Images | `GET /api/application-images/{logo,background,favicon,email,default-profile-picture}` |
| Other | `GET /api/storage/sqlite-warning` · `GET /api/custom-claims/suggestions` |

Full catalog with methods and notes: `references/endpoints.md`.
For the up-to-date catalog per version: https://pocket-id.org/docs/api/endpoints

## Ready-to-use examples

```sh
# Installed version vs latest
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" "$POCKET_ID_BASE_URL/api/version/current"
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" "$POCKET_ID_BASE_URL/api/version/latest"

# Users and groups
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" "$POCKET_ID_BASE_URL/api/users"
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" "$POCKET_ID_BASE_URL/api/user-groups"

# OIDC clients with allowed groups (per-client detail)
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" "$POCKET_ID_BASE_URL/api/oidc/clients"
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" "$POCKET_ID_BASE_URL/api/oidc/clients/{id}"

# Full configuration (includes SMTP/LDAP — mask passwords when displaying)
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" "$POCKET_ID_BASE_URL/api/application-configuration/all"

# Latest audit events from all users
curl -sS -H "X-API-KEY: $POCKET_ID_API_KEY" \
  "$POCKET_ID_BASE_URL/api/audit-logs/all?pagination%5Blimit%5D=10"
```
