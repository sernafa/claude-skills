# phpIPAM API-only Claude Code Skill

Copy the `phpipam-api` directory into `<project>/.claude/skills/` (project-scoped) or `~/.claude/skills/` (personal). Restart/reload Claude Code as needed and invoke `/phpipam-api` or describe a phpIPAM REST API task.

Dependencies: Python 3.9+; standard library only. Set `PHPIPAM_HOST`, `PHPIPAM_APP_ID`, and `PHPIPAM_TOKEN` (or `PHPIPAM_USERNAME` + `PHPIPAM_PASSWORD`) in your shell/session without persisting secrets in the project. Optionally set `PHPIPAM_CA_BUNDLE` to a PEM CA bundle to enable TLS certificate verification.

Target version: **phpIPAM 1.8.x**. HTTPS transport is required; by default certificate verification and certificate warnings are disabled (**server identity is not verified — MITM risk**) unless `PHPIPAM_CA_BUNDLE` is set.

This client permits GET and gated writes against phpIPAM HTTPS API endpoints only. It does not bypass phpIPAM application permissions. Confirm endpoint schemas against your phpIPAM version before use.
