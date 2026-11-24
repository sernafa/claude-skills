# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- `patchmon-api` skill: administers PatchMon 2.x patch-management servers exclusively through the authenticated HTTPS REST API — read-only by default, writes gated behind an explicit preview-and-approval flow with cascade deletes (hosts, enrollment tokens) needing their own confirmation. Bundled stdlib-only Python client (`scripts/patchmon_api.py`) covering all five auth domains (scoped Basic, GetHomepage Basic, agent `X-API-ID`/`X-API-KEY`, auto-enrollment headers, admin JWT), with auth-profile inference from the path (override via `--auth`), `PUT` support for the JWT web-UI endpoints, credential masking in responses, script/binary bodies saved (never printed or executed) via `--output`, and credential-looking query parameters rejected. `PATCHMON_HOST` accepts a bare host or an `https://host[:port]` URL, and secret-file values expand `${VAR}` references so a shared secrets file can alias the skill's variable names. Includes curated endpoint catalog and the OpenAPI spec as references, plus a live-observed quirk (unknown-host `/stats` returns zeroed 200 instead of the documented 404).
- All API skills (`fortigate-api`, `phpipam-api`, `pocket-id-api`, `technitium-dns`): shared credential discovery order — exported environment variables first, then `~/.config/secrets/.env.<skill-name>`, then `~/.config/secrets/.env`, and only then ask the user. The bundled Python clients of `fortigate-api` and `phpipam-api` implement it natively (environment always wins over file values; `_ALLOW_WRITE` approval flags are never loaded from secret files)

### Changed

- `technitium-dns` skill: golden rules upgraded to read-only by default — every mutating call (`add`/`create`/`set`/`delete`/`import`/`sign`/flushes/cluster changes) now requires an explicit preview-and-approval; destructive calls keep their separate confirmation
- `arcane-cli` skill: golden rules upgraded to read-only by default — every mutating command (`up`/`redeploy`/`pull`/`create`/`restart`/`update`/`switch`/`sync`/`run`/`trigger`) now requires an explicit approval; destructive commands keep their separate confirmation, and `--yes` is now also gated on mutations
- `fortigate-api` skill: documents the dotted REST path convention for three-word CLI nodes (`firewall.service/custom/`, `vpn.ipsec/phase1-interface/`, ...), where the flat `a/b/c` form fails with HTTP 400 and an empty error body that is easy to misread as an access-profile problem; the bundled client's `path` help now states the convention (verified against FortiOS 7.4.7)

## [1.4.0] - 2026-11-08

### Added

- `phpipam-api` skill: administers phpIPAM servers exclusively through the authenticated HTTPS REST API — read-only by default, writes gated behind an explicit preview-and-approval flow, token auth via `PHPIPAM_TOKEN` or `PHPIPAM_USERNAME`/`PHPIPAM_PASSWORD`, and a bundled stdlib-only Python client (`scripts/phpipam_api.py`) for sections, subnets, addresses, VLANs, VRFs, devices and automated subnet/address allocation
- `pocket-id-api` skill: administers Pocket-ID IdP servers exclusively through the authenticated REST API — users, user groups, OIDC clients, application configuration, audit logs, signup tokens and version checks; read-only by default, destructive writes gated behind explicit confirmation, `X-API-KEY` auth with credentials kept in environment variables (`POCKET_ID_BASE_URL`, `POCKET_ID_API_KEY`)

### Fixed

- npx installer (`bin/cli.js`) now copies the entire skill directory instead of only `SKILL.md`; previous installs silently dropped the bundled Python clients of `fortigate-api` and `phpipam-api` and would have dropped the `pocket-id-api` endpoint catalog. Reinstalling a skill also replaces stale files removed upstream

## [1.3.0] - 2026-10-25

### Added

- `fortigate-api` skill: administers FortiGate/FortiOS 7.4.x devices exclusively through the authenticated HTTPS REST API — read-only by default, writes gated behind an explicit preview-and-approval flow, API token kept out of the repo via `FORTIGATE_API_TOKEN`, and a bundled stdlib-only Python client (`scripts/fortigate_api.py`)

## [1.2.0] - 2026-10-24

### Added

- `technitium-dns` skill: manages a Technitium DNS Server over its HTTP API — authoritative zones and records, DNSSEC, conditional forwarders, DNS cache, allowed/blocked zones, block lists, DNS apps, settings and backups, DHCP, users and permissions, clustering and query logs

## [1.1.0] - 2026-10-24

### Added

- `arcane-cli` skill: manages the Docker homelab with arcane-cli (Arcane) — containers, Compose projects, images, volumes, networks, remote (edge) environments, GitOps, backups, the auto-updater, vulnerabilities and webhooks

## [1.0.0] - 2026-05-27

### Added

- Initial release of `sernafa/claude-skills` marketplace
- `senior-commit-writer` skill: produces senior-level commit messages and branch descriptions for all Git-managed work domains (application dev, IaC, Kubernetes, GitOps, CI/CD, security, observability, data, documentation, architecture)
- `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` for Claude Code CLI compatibility
- `bin/cli.js` CLI for npx-based skill installation
- `scripts/list-skills.js` — lists all available skills with descriptions
- `scripts/validate-skills.js` — validates SKILL.md frontmatter and required fields
- `docs/installation.md` — full installation walkthrough
- `docs/publishing.md` — guide for forking and publishing your own marketplace
- MIT License
- Contributing guide
