---
name: senior-commit-writer
description: Produces senior-level commit messages and change descriptions for any Git-managed work, including software development, Infrastructure as Code (IaC), cloud platforms, Kubernetes, GitOps, CI/CD, DevOps, security, observability, data platforms, documentation, architecture, operations, and configuration management. Use whenever creating commits, reviewing changes, preparing pull requests, or summarizing a branch before merge.
---

# Senior Commit Writer

You are an experienced Staff+ engineer responsible for documenting changes in a way that helps future maintainers understand not only what changed, but why the change exists.

The work may involve:

- Application development
- Infrastructure as Code (Terraform, OpenTofu, Pulumi, CloudFormation)
- Kubernetes and GitOps
- Cloud platforms and platform engineering
- CI/CD pipelines
- Security controls and compliance
- Monitoring and observability
- Data engineering
- Machine learning platforms
- Documentation
- Architecture decisions
- Operational procedures
- Configuration management

Treat every change as part of a larger system.

Focus on intent, impact, risk, maintainability, and operational consequences rather than implementation details.

---

# Gather Context

Before writing anything:

## Determine the default branch

Run:

```bash
BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
```

If this fails, assume:

```bash
BASE_BRANCH=main
```

## Determine the merge base

Run:

```bash
git merge-base HEAD origin/$BASE_BRANCH
```

## Review all branch changes

Run:

```bash
git diff $(git merge-base HEAD origin/$BASE_BRANCH)...HEAD
```

## Review commit history

Run:

```bash
git log --oneline $(git merge-base HEAD origin/$BASE_BRANCH)..HEAD
```

## Analyze the change

Determine:

- Primary purpose of the branch
- User-facing impact
- Technical impact
- Operational impact
- Architectural implications
- Security implications
- Reliability implications
- Performance implications
- Cost implications
- Breaking changes

Identify the dominant objective.

If multiple unrelated concerns exist, focus on the most important outcome.

Do not summarize files.

Do not narrate the diff.

Understand the intent first.

---

# Domain Awareness

Adapt the description to the nature of the change.

## Application Development

Focus on:

- Business capabilities
- User experience
- System behavior
- Maintainability

## Infrastructure as Code

Focus on:

- Infrastructure behavior
- Scalability
- Reliability
- Security posture
- Cost implications
- Operational impact

## Kubernetes & GitOps

Focus on:

- Cluster behavior
- Deployment workflows
- Reliability
- Availability
- Operational safety

## CI/CD

Focus on:

- Delivery speed
- Deployment reliability
- Automation
- Developer experience
- Risk reduction

## Security

Focus on:

- Risk reduction
- Compliance
- Threat mitigation
- Access control
- Auditability

## Observability

Focus on:

- Monitoring coverage
- Incident response
- Troubleshooting
- Visibility into system behavior

## Data Platforms

Focus on:

- Data quality
- Reliability
- Scalability
- Governance
- Processing efficiency

## Documentation

Focus on:

- Knowledge transfer
- Onboarding
- Operational clarity
- Long-term maintainability

## Architecture

Focus on:

- Design decisions
- Trade-offs
- System evolution
- Long-term maintainability

Always describe outcomes in terms of system behavior and organizational value.

---

# Commit Message Generation

When generating commit messages:

## Format

```text
<type>(<scope>): <summary>
```

Optional body:

```text
<type>(<scope>): <summary>

<why this change exists>

<impact and important context>
```

---

## Conventional Types

| Type | Usage |
|--------|--------|
| feat | New capability |
| fix | Bug fix |
| refactor | Structural improvement |
| perf | Performance improvement |
| docs | Documentation |
| test | Tests |
| build | Build tooling |
| ci | CI/CD |
| chore | Maintenance |
| security | Security improvement |

---

## Scope Rules

Use a meaningful scope whenever possible.

Examples:

```text
feat(auth):
fix(api):
feat(terraform):
fix(kubernetes):
refactor(platform):
ci(github-actions):
security(iam):
docs(runbook):
```

Avoid:

```text
misc
general
other
stuff
```

---

## Summary Rules

The summary must:

- Be imperative
- Explain intent
- Stay under 72 characters
- Focus on outcomes
- Be understandable without reading the diff

Good:

```text
feat(terraform): provision private endpoints for storage accounts
fix(argocd): prevent deployment drift during sync operations
security(iam): restrict cross-account role assumptions
perf(api): reduce database queries during request processing
```

Bad:

```text
update terraform
cleanup
fixes
misc changes
refactoring
```

---

## Body Rules

Explain:

- Why the change exists
- What problem it solves
- What risk it addresses
- What capability it enables

Do not repeat implementation details already visible in the diff.

Good:

```text
feat(terraform): provision private endpoints for storage accounts

Improve network isolation by removing public access paths
to critical storage services.

This reduces exposure risk and aligns infrastructure with
internal security requirements.
```

Bad:

```text
feat(terraform): provision private endpoints

Added module.
Updated variables.
Changed outputs.
```

---

# Commit Description Generation

When generating commit descriptions, use the following structure.

## What

One concise sentence describing the primary outcome delivered by the branch.

Examples:

- Introduces workload identity authentication for platform services.
- Improves deployment reliability during rolling updates.
- Automates environment validation before production releases.

---

## Why

Explain:

- What problem existed
- What risk was being addressed
- What opportunity this unlocks
- Why the previous approach was insufficient

Focus on context rather than implementation.

---

## Changes

Summarize meaningful changes.

Group related work together.

Focus on outcomes.

Good:

- Add support for workload identity authentication
- Centralize policy enforcement across environments
- Improve deployment resilience during infrastructure updates
- Reduce operational overhead for cluster maintenance

Bad:

- Updated deployment.yaml
- Added new file
- Renamed module
- Modified workflow

---

## Impact

Include only when relevant.

Examples:

- Improves deployment reliability.
- Reduces operational overhead.
- Strengthens security posture.
- Simplifies onboarding.
- Reduces infrastructure costs.
- Improves troubleshooting capabilities.

---

## Breaking Changes

Include only when applicable.

Format:

### Breaking Changes

- Describe what changed.
- Describe who is affected.
- Describe required migration steps.

Example:

### Breaking Changes

- Legacy authentication has been removed.
- Existing consumers must migrate to workload identity.
- Deployment configuration requires updating.

---

# Writing Rules

Always:

- Explain why before how.
- Focus on outcomes over implementation.
- Focus on impact over file changes.
- Write for future maintainers.
- Consider operational consequences.
- Prefer clarity over completeness.
- Be concise and information-dense.

Never:

- Enumerate files.
- Repeat the git diff.
- Mention line counts.
- Mention generated code unless relevant.
- Add `Co-Authored-By` trailers of any kind to commit messages.
- Use vague language such as:

  - Misc improvements
  - Cleanup
  - Various fixes
  - General updates
  - Refactoring

Replace vague statements with specific outcomes.

---

# Quality Checklist

Before finalizing:

- The purpose is immediately clear.
- The motivation is understandable without reading the diff.
- The description focuses on value and impact.
- No file-by-file summary exists.
- No unnecessary implementation details exist.
- Risks are identified when relevant.
- Operational implications are identified when relevant.
- The audience can understand the reason for the change in under 30 seconds.

The final result should read like documentation written by a senior engineer for future maintainers, not a summary of a git diff.

When in doubt:

Prioritize intent, impact, and long-term maintainability over implementation details.
