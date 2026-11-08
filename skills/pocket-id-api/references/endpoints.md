# Pocket-ID REST API endpoint catalog

Source: https://pocket-id.org/docs/api/endpoints (documentation for the latest
version). All requests carry the `X-API-KEY: <api key>` header.
Listings accept `pagination[page]` and `pagination[limit]` and respond with
`{"data": [...], "pagination": {"totalPages","totalItems","currentPage","itemsPerPage"}}`.

> Some endpoints may not exist in older Pocket-ID versions. If you get
> `404 {"error":"API endpoint not found"}`, check `GET /api/version/current`
> and contrast with the official docs for your version.

## Versions

- `GET /api/version/current` — installed version
- `GET /api/version/latest` — latest published version

## Users

- `GET /api/users` — list (paginated)
- `POST /api/users` — create (verify schema in the official docs)
- `GET /api/users/{id}` — get
- `PUT /api/users/{id}` — update
- `DELETE /api/users/{id}` — delete
- `GET /api/users/{id}/groups` — user's groups
- `GET /api/users/{id}/webauthn-credentials` — registered passkeys
- `DELETE /api/users/{id}/webauthn-credentials/{credentialId}` — delete passkey
- `GET /api/users/{id}/profile-picture.png` — profile picture
- `PUT /api/users/{id}/profile-picture` — upload picture
- `DELETE /api/users/{id}/profile-picture` — reset picture
- `POST /api/users/{id}/one-time-access-token` — create one-time access token (admin)
- `POST /api/users/{id}/one-time-access-email` — send one-time access email (admin)

## Current user (`/me`)

- `GET /api/users/me`
- `GET /api/users/me/email-change` — pending email change
- `DELETE /api/users/me/email-change` — cancel email change
- `PUT /api/users/me/profile-picture` · `DELETE /api/users/me/profile-picture`
- `POST /api/users/me/send-email-verification` · email verification

## User groups

- `GET /api/user-groups` — list (paginated)
- `POST /api/user-groups` — create
- `GET /api/user-groups/{id}` — get
- `PUT /api/user-groups/{id}` — update
- `DELETE /api/user-groups/{id}` — delete
- `PUT /api/user-groups/{id}/users` — update group members
- `PUT /api/user-groups/{id}/allowed-oidc-clients` — OIDC clients allowed for the group

## OIDC clients

- `GET /api/oidc/clients` — list (paginated)
- `POST /api/oidc/clients` — create
- `GET /api/oidc/clients/{id}` — get (includes `allowedUserGroups`)
- `PUT /api/oidc/clients/{id}` — update
- `DELETE /api/oidc/clients/{id}` — delete
- `PUT /api/oidc/clients/{id}/allowed-user-groups` — groups with access
- `GET /api/oidc/clients/{id}/secrets` — list client secrets
- `POST /api/oidc/clients/{id}/secrets` — add secret
- `DELETE /api/oidc/clients/{id}/secrets/{secretId}` — delete secret
- `GET /api/oidc/clients/{id}/logo` · `POST .../logo` · `DELETE .../logo`
- `GET /api/oidc/logo-presets` — search predefined logos
- `GET /api/oidc/clients/{id}/preview/{userId}` — preview claims a user will receive
- `POST /api/oidc/clients/{id}/refresh` — refresh metadata document (CIMD)
- `GET /api/oidc/clients/{id}/scim-service-provider` — client's SCIM config

## OIDC general

- `POST /api/oidc/introspect` — token introspection
- `GET /api/oidc/userinfo` — userinfo (with an OIDC access token)
- `GET /api/oidc/users/me/clients` — clients accessible to the current user
- `GET /api/oidc/users/me/authorized-clients` — apps authorized by the current user
- `DELETE /api/oidc/users/me/authorized-clients/{clientId}` — revoke authorization
- `GET /api/oidc/users/{id}/authorized-clients` — apps authorized by a user (admin)

## APIs and permissions (v2.x feature)

- `GET /api/apis` — list registered APIs
- `POST /api/apis` — create
- `GET /api/apis/{id}` · `PUT /api/apis/{id}` · `DELETE /api/apis/{id}`
- `GET /api/apis/{id}/permissions` — API permissions
- `GET /api/apis/{id}/clients` · `/assignable-clients` — clients with/with permission to access
- `PUT /api/apis/{id}/clients/{clientId}` · `DELETE ...` — grant/revoke client access
- `PUT /api/apis/{id}/cimd-access` — access for metadata document clients
- `GET /api/api-access/{clientId}/apis` · `/assignable-apis` — APIs of an OIDC client

## API keys

- `GET /api/api-keys` · `POST /api/api-keys`
- `DELETE /api/api-keys/{id}` — revoke
- `POST /api/api-keys/{id}/renew` — renew
- **Note:** these endpoints reject requests authenticated with an API key
  (403 `api_key_auth_not_allowed`). Manage them only from the admin UI,
  or set `STATIC_API_KEY` per environment.

## Application configuration

- `GET /api/application-configuration` — public keys
- `GET /api/application-configuration/all` — all keys (includes SMTP/LDAP; mask passwords)
- `POST /api/application-configuration/test-email` — test SMTP delivery
- `POST /api/application-configuration/sync-ldap` — manual LDAP sync
- Branding images: `GET /api/application-images/{logo,background,favicon,email,default-profile-picture}`
  and `DELETE` for logo/background/default-profile-picture

## Audit

- `GET /api/audit-logs` — events of the authenticated user
- `GET /api/audit-logs/all` — events of all users
- `GET /api/audit-logs/filters/users` — users with events (id→username map)
- `GET /api/audit-logs/filters/client-names` — clients with events

## Signup

- `GET /api/signup-tokens` · `POST /api/signup-tokens` · `DELETE /api/signup-tokens/{id}`
- `POST /api/signup` — signup with token
- `POST /api/signup/setup` — initial administrator setup

## One-time access

- `POST /api/one-time-access-email` — request a one-time access email
- `POST /api/one-time-access-token/{token}` — redeem token for a session

## Device login

- `POST /api/device-login/requests` — create request
- `POST /api/device-login/requests/{id}/exchange` — exchange for tokens
- `POST /api/device-login/verification` — inspect pending request
- `POST /api/device-login/verification/decision` — approve/deny

## Custom claims

- `GET /api/custom-claims/suggestions`
- `GET /api/custom-claims/user/{userId}` — claims of a user
- `GET /api/custom-claims/user-group/{userGroupId}` — claims of a group

## SCIM provisioning (v2.14+ approx.)

- `GET /api/scim/service-provider` · `POST /api/scim/service-provider`
- `DELETE /api/scim/service-provider/{id}`
- `POST /api/scim/service-provider/{id}/sync` — trigger synchronization

## Other

- `GET /api/storage/sqlite-warning` — SQLite usage warning
