# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed

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
