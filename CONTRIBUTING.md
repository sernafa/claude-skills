# Contributing

Thank you for your interest in contributing to `sernafa/claude-skills`.

---

## Adding a New Skill

### 1. Create the skill directory

```bash
mkdir -p skills/<your-skill-name>
```

Skill names must:
- Use lowercase letters, numbers, and hyphens only
- Be descriptive and unique within this repo
- Match the `name` field in the SKILL.md frontmatter exactly

### 2. Create `skills/<your-skill-name>/SKILL.md`

Required frontmatter:

```markdown
---
name: your-skill-name
description: One-sentence capability statement. Use when [triggering conditions]. Max 1024 characters.
---

# Your Skill Title

[Skill body here]
```

**Frontmatter rules:**
- `name` — must match the directory name exactly
- `description` — describes WHAT the skill does and WHEN to use it, not how. Max 1024 chars.

**Optional frontmatter:**

```yaml
license: MIT
metadata:
  author: https://github.com/sernafa
  version: "1.0.0"
  domain: devops|infrastructure|security|backend|frontend|data-ml|documentation|architecture
  triggers: keyword1, keyword2, keyword3
  role: specialist|expert|architect|engineer
  scope: implementation|review|design|analysis
```

### 3. Validate your skill

```bash
node scripts/validate-skills.js
```

All checks must pass before submitting a PR.

### 4. Update `version.json`

Increment `skillCount` and add your skill name to the `skills` array.

---

## Skill Body Guidelines

- Keep SKILL.md under 500 lines for fast loading
- If the skill needs deep reference material, create a `skills/<name>/references/` subdirectory with focused topic files (100–600 lines each)
- Focus the description on outcomes and context, not process steps
- Use second-person imperative voice ("Run:", "Analyze:", "Focus on:")
- Structure with H1 (title), H2 (major sections), H3 (subsections)

---

## Pull Request Checklist

- [ ] Skill directory name uses lowercase-hyphen format
- [ ] `name` in frontmatter matches directory name exactly
- [ ] `description` is under 1024 chars and describes capability + triggers
- [ ] `node scripts/validate-skills.js` exits 0
- [ ] `version.json` updated
- [ ] `CHANGELOG.md` updated with the new skill under `[Unreleased]`

---

## Reporting Issues

Open an issue at [github.com/sernafa/claude-skills/issues](https://github.com/sernafa/claude-skills/issues).

Include:
- Skill name
- What you expected
- What happened instead
- Claude Code version (`claude --version`)
