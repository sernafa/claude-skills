# FortiGate API-only Claude Code Skill

Copy the `fortigate-api` directory into `<project>/.claude/skills/` (project-scoped) or `~/.claude/skills/` (personal). Restart/reload Claude Code as needed and invoke `/fortigate-api` or describe a FortiGate REST API task.

Dependencies: Python 3.9+; standard library only. Set `FORTIGATE_HOST`, `FORTIGATE_API_TOKEN`, in your shell/session without persisting secrets in the project.

Target version: **FortiOS 7.4.x**. HTTPS transport is required, but certificate verification and certificate warnings are disabled; **server identity is not verified (MITM risk)**. No `ca.pem` is necessary.

This client permits GET and gated writes against native FortiOS HTTPS API endpoints only. It does not bypass FortiGate permissions. Confirm endpoint schemas against your FortiOS version before use. Note: the source user PDF documents FortiPortal, which is a different REST API.
