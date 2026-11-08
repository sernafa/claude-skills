# Pocket-ID Claude Code Skill

Copy the `pocket-id-api` directory into `<project>/.claude/skills/` (project-scoped) or `~/.claude/skills/` (personal). Restart/reload Claude Code as needed and invoke `/pocket-id-api` or describe a Pocket-ID REST API task.

Dependencies: none beyond `curl`. Set `POCKET_ID_BASE_URL` and `POCKET_ID_API_KEY` in your shell/session without persisting secrets in the project.

Authentication uses the `X-API-KEY` header — `Authorization: Bearer` is rejected with 401. The skill is read-only by default: writes require explicit user confirmation, and destructive DELETEs (users, OIDC clients, groups) require double confirmation.

Endpoint catalog per version: https://pocket-id.org/docs/api/endpoints
