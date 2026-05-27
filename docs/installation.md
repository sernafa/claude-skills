# Installation Guide

This document covers all supported installation methods for `sernafa/claude-skills`.

---

## Method 1: Claude Code Plugin Marketplace (recommended)

This installs the entire skill collection and keeps it up to date via `/plugin update`.

### Step 1 — Register the marketplace

In Claude Code:

```
/plugin marketplace add sernafa/claude-skills
```

This fetches the repo and registers it under the `sernafa` marketplace name.

### Step 2 — Install the plugin

```
/plugin install claude-skills@sernafa
```

This installs all skills in the collection. Skills become available in the current Claude Code session after installation.

### Update

```
/plugin update claude-skills@sernafa
```

### Remove

```
/plugin remove claude-skills@sernafa
```

---

## Method 2: npx (single skill, no marketplace)

Copies a specific skill directly to `~/.claude/skills/` without registering a marketplace.

```bash
npx @sernafa/claude-skills add --skill senior-commit-writer
```

Or if you have the repo cloned locally:

```bash
node bin/cli.js add --skill senior-commit-writer
```

List available skills:

```bash
npx @sernafa/claude-skills list
```

After installation, restart Claude Code to activate the skill.

> **Note:** The `npx skills add <url>` format shown in some documentation requires a separate `skills` CLI package published on npm. Use `npx @sernafa/claude-skills` as the direct form for this repository.

---

## Method 3: Manual copy

Clone the repo and copy skills directly:

```bash
git clone https://github.com/sernafa/claude-skills
cp -r claude-skills/skills/senior-commit-writer ~/.claude/skills/
```

Restart Claude Code to activate.

---

## Verifying Installation

After installing, open Claude Code and type:

```
/senior-commit-writer
```

Or invoke it naturally by describing a commit task. The skill auto-triggers when generating commit messages or branch descriptions.

---

## Troubleshooting

**Skill not found after installation**
- Ensure you restarted Claude Code — skills load at session start
- Check that the SKILL.md is at `~/.claude/skills/senior-commit-writer/SKILL.md`

**Marketplace registration fails**
- Verify you have network access to GitHub
- Check that the repo is public: `https://github.com/sernafa/claude-skills`

**npx fails**
- Requires Node.js 18+
- Try `node bin/cli.js add --skill senior-commit-writer` as a fallback
