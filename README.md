# sernafa/claude-skills

> Reusable senior-level skills for [Claude Code CLI](https://claude.ai/code)

A marketplace-ready collection of Claude Code skills covering commit writing, architecture, DevOps, IaC, and engineering best practices.

---

## Skills

| Skill | Description |
|-------|-------------|
| [senior-commit-writer](skills/senior-commit-writer/SKILL.md) | Produces senior-level commit messages and branch descriptions for any Git-managed work (app dev, IaC, Kubernetes, GitOps, CI/CD, security, observability, data, docs, architecture) |
| [arcane-cli](skills/arcane-cli/SKILL.md) | Manages the Docker homelab with arcane-cli (Arcane): containers, Compose projects, images, volumes, networks, remote environments, GitOps, backups, auto-updater, vulnerabilities and webhooks |
| [technitium-dns](skills/technitium-dns/SKILL.md) | Manages a Technitium DNS Server over its HTTP API: zones and records, DNSSEC, forwarders, cache, allowed/blocked zones, block lists, DNS apps, settings and backups, DHCP, users and permissions, clustering and query logs |

---

## Installation

### Option 1 — Plugin Marketplace (recommended)

Installs the full collection. Supports `/plugin update` for future updates.

```
/plugin marketplace add sernafa/claude-skills
/plugin install claude-skills@sernafa
```

### Option 2 — npx (single skill)

Copies one skill directly to `~/.claude/skills/` — no marketplace registration needed.

```bash
# Install a skill
npx @sernafa/claude-skills add --skill senior-commit-writer

# List available skills
npx @sernafa/claude-skills list
```

### Option 3 — Manual

```bash
git clone https://github.com/sernafa/claude-skills
cp -r claude-skills/skills/senior-commit-writer ~/.claude/skills/
```

Restart Claude Code after any manual install to activate skills.

> See [docs/installation.md](docs/installation.md) for a detailed walkthrough and troubleshooting.

---

## Usage

Once installed, skills activate automatically when relevant — or invoke them explicitly:

```
/senior-commit-writer
```

Example: ask Claude Code to write a commit for your current branch and it will use the `senior-commit-writer` skill to produce a conventional commit message focused on intent, impact, and operational consequences — not a diff summary.

---

## Adding Skills

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the skill spec and PR checklist.

```bash
# Validate all skills
node scripts/validate-skills.js

# List all skills
node scripts/list-skills.js
```

---

## Publishing Your Own Marketplace

Fork this repo and follow [docs/publishing.md](docs/publishing.md) to publish your own Claude Code skill marketplace under your GitHub username.

---

## License

[MIT](LICENSE)
