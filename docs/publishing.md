# Publishing Your Own Marketplace

This guide explains how to fork `sernafa/claude-skills` and publish your own Claude Code skill marketplace.

---

## Fork and Rename

```bash
# Fork via GitHub UI, then clone
git clone https://github.com/<your-username>/claude-skills
cd claude-skills
```

---

## Update Marketplace Identity

### `.claude-plugin/marketplace.json`

Change the `name` field to your GitHub username (or a descriptive marketplace name):

```json
{
  "name": "<your-username>",
  "owner": { "name": "<your-username>" },
  "plugins": [{
    "name": "claude-skills",
    "repository": "https://github.com/<your-username>/claude-skills",
    ...
  }]
}
```

The `name` value becomes the marketplace identifier in Claude Code — users will install with `/plugin install claude-skills@<your-username>`.

### `package.json`

```json
{
  "name": "@<your-username>/claude-skills",
  "author": { "name": "<your-username>" },
  "repository": "https://github.com/<your-username>/claude-skills.git"
}
```

---

## Add Your Skills

Follow the [Contributing guide](../CONTRIBUTING.md) to add skills in `skills/<name>/SKILL.md`.

Run validation before publishing:

```bash
node scripts/validate-skills.js
```

---

## Update `version.json`

```json
{
  "version": "1.0.0",
  "skillCount": 3,
  "skills": ["senior-commit-writer", "your-skill-1", "your-skill-2"]
}
```

---

## Publish to GitHub

```bash
git add .
git commit -m "feat: initial marketplace release"
git push origin main
```

Ensure the repository is **public**.

---

## Register with Claude Code

Once published, any user can add your marketplace:

```
/plugin marketplace add <your-username>/claude-skills
/plugin install claude-skills@<your-username>
```

---

## Publish to npm (optional)

Publishing to npm allows users to install skills via `npx`:

```bash
npm login
npm publish --access public
```

Users can then run:

```bash
npx @<your-username>/claude-skills add --skill <skill-name>
```

---

## Versioning

Use [Semantic Versioning](https://semver.org):

- `patch` — bug fix or skill content update
- `minor` — new skill added
- `major` — breaking change to skill names or marketplace structure

Update `version.json`, `package.json`, `.claude-plugin/marketplace.json`, and `CHANGELOG.md` on each release. Tag releases with `git tag v<version>`.
