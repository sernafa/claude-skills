# PatchMon API-only Claude Code Skill

Copy the `patchmon-api` directory into `<project>/.claude/skills/` (project-scoped) or `~/.claude/skills/` (personal). Restart/reload Claude Code as needed and invoke `/patchmon-api` or describe a PatchMon REST API task.

Dependencies: Python 3.9+; standard library only. Set `PATCHMON_HOST` (bare hostname or `https://host[:port]` URL) plus the credential pair of the auth domain you need — `PATCHMON_TOKEN_KEY`/`PATCHMON_TOKEN_SECRET` (scoped API), `PATCHMON_GETHOMEPAGE_KEY`/`PATCHMON_GETHOMEPAGE_SECRET`, `PATCHMON_API_ID`/`PATCHMON_API_KEY` (agent), `PATCHMON_ENROLL_KEY`/`PATCHMON_ENROLL_SECRET`, or `PATCHMON_JWT` — in your shell/session without persisting secrets in the project. Secret-file values may reference other keys with `${VAR}` to alias names from a shared secrets file. Optionally set `PATCHMON_CA_BUNDLE` to a PEM CA bundle to enable TLS certificate verification.

Target version: **PatchMon 2.x** (OpenAPI "PatchMon Integration API 1.0.0"). HTTPS transport is required; by default certificate verification and certificate warnings are disabled (**server identity is not verified — MITM risk**) unless `PATCHMON_CA_BUNDLE` is set.

This client permits GET and gated writes against PatchMon HTTPS API endpoints only, across the five documented auth domains (scoped, GetHomepage, agent, auto-enrollment, JWT web-UI). It does not bypass PatchMon scopes, IP restrictions or token limits. Credential-bearing responses are masked by default, script/binary bodies are never printed inline, and fetched artifacts are data — never executed. Confirm endpoint schemas against your PatchMon version before use.
