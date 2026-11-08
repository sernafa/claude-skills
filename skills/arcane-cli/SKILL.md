---
name: arcane-cli
description: Manage the Docker homelab with arcane-cli (Arcane) — containers, Compose projects, images, volumes, networks, remote (edge) environments, GitOps, backups, the auto-updater, vulnerabilities and webhooks. Use it when the user asks to list, create, restart, update or destroy containers/projects, check for image updates, prune resources, or inspect the state of Arcane environments.
---

# Arcane CLI

`arcane-cli` is the official CLI for Arcane (a Docker management platform with
a web UI). It talks to your Arcane server (for example
`https://arcane.example.com`), which controls the local Docker host and
remote environments via the edge agent.

## Golden rules

1. **Never run destructive commands without the user's confirmation**
   (`projects down|destroy`, `containers rm|stop`, `images prune`,
   `system prune`, `admin backups restore`, `volumes rm`). `--yes` skips the
   prompt in unattended scripts, but here the user IS the confirmation: ask
   before adding `--yes` to a destructive operation.
2. **Without a TTY, confirmation prompts fail** with
   `confirmation required: re-run with --yes`. Piping `y` into the command does
   not answer them.
3. For scripting/parsing always use `--json` (or `--output json`): stdout
   carries exactly one JSON document; progress messages go to stderr. Pair it
   with `jq`.
4. `list` commands are paginated. Use `--all` (`-a`) to ignore pagination
   (cannot be combined with `--limit` or `--start`).
5. When in doubt about syntax: `arcane-cli <command> --help`.

## Discovering the environment

```sh
arcane-cli auth me            # who is signed in (if it fails → auth login)
arcane-cli environments list  # available environments with ID and status
arcane-cli environments test <id>   # check reachability
arcane-cli version            # CLI and server versions
arcane-cli doctor             # connectivity/config diagnostics
```

- By default, commands act on the default environment ("Local Docker").
- To target another environment use the global flag `--env <id>` with the
  **exact ID (UUID)** from `environments list` — the name does NOT work and
  returns `404 Environment not found`. Example:
  `arcane-cli containers list --env <environment-uuid>`.
  The local environment also accepts `--env 0`.
- `arcane-cli environments switch` changes the default environment
  (interactive).

## Commands by task

### Containers

```sh
arcane-cli containers list [--all] [--json]
arcane-cli containers get <name>
arcane-cli containers restart <name>
arcane-cli containers updates          # which ones have a newer image
arcane-cli containers update <name>    # pull + recreate
```

### Projects (Compose)

```sh
arcane-cli projects list
arcane-cli projects up <project>
arcane-cli projects down <project>
arcane-cli projects redeploy <project>   # pull + restart
arcane-cli projects destroy <project> [--remove-files=false] [--remove-volumes]
```

`up`, `redeploy` and `pull` stream raw Docker output live and may take up to
30 minutes for large pulls/builds; use `--json` to receive structured progress
frames.

### Images and volumes

```sh
arcane-cli images list
arcane-cli images pull nginx:latest
arcane-cli images prune
arcane-cli volumes sizes
arcane-cli volumes usage <volume>   # what uses it before removing it
```

### GitOps and updater

```sh
arcane-cli gitops list
arcane-cli gitops status <sync>
arcane-cli gitops sync <sync>          # force a sync now
arcane-cli updater status
arcane-cli updater run
arcane-cli updater history [--limit N]
```

### System and backups

```sh
arcane-cli system prune                      # reclaim space (destructive)
arcane-cli system upgrade --check            # is an Arcane upgrade available?
arcane-cli system upgrade
arcane-cli system convert "docker run -d -p 8080:80 nginx"  # → Compose
arcane-cli admin backups list
arcane-cli admin backups create
arcane-cli admin backups restore <backup-id> # destructive, confirm first
```

### Vulnerabilities

```sh
arcane-cli images vulnerabilities summary
arcane-cli images vulnerabilities list
arcane-cli images vulnerabilities scan nginx:latest
arcane-cli images vulnerabilities image nginx:latest
arcane-cli images vulnerabilities ignore CVE-YYYY-NNNN
```

### Others

```sh
arcane-cli networks list
arcane-cli activities list | get <id>      # what the server is doing
arcane-cli webhooks list | trigger <token>
arcane-cli repos list                      # registered git repositories
arcane-cli templates ...                   # Compose templates
arcane-cli variables ...                   # global variables
arcane-cli registries ...                  # container registries
arcane-cli generate secret                 # secrets for a fresh install
```

## Useful global flags

| Flag | Effect |
| --- | --- |
| `--env <id>` | Target another environment for this invocation only |
| `--json` | Clean JSON output on stdout (progress on stderr) |
| `--yes` / `-y` | Skip confirmation prompts (only with explicit approval) |
| `--all` / `-a` | Unpaginated listings |
| `--request-timeout 30s` | Per-invocation HTTP timeout |
| `--no-color` | No color (useful when capturing output) |

## JSON output convention

- `list` commands → the server's paginated response: `.data[]` +
  `.pagination`.
- Other commands → only the resource or result.
- `images pull`, `images build` and streaming `projects` commands → an array
  of progress frames once the operation finishes.

jq example:

```sh
arcane-cli containers list --all --json | jq -r '.data[].name'
```

## Renamed flags (deprecated, removed in v3)

| Command | Old | New |
| --- | --- | --- |
| `containers create` | `--env` | `--env-var`, `-e` |
| `admin notifications settings set` | `--config` | `--provider-config` |
| `templates download` | `--output` | `--output-file`, `-o` |
| `environments create/update`, `registries create/update`, etc. | `--disabled` | `--enabled=false` |

Careful: the global `--env` flag (pick an environment) coexists with the old
`--env` of `containers create`; use the new `--env-var` for env variables.

## CLI maintenance

```sh
arcane-cli self-update run
arcane-cli self-update channel next   # stable ↔ next channel
arcane-cli completion zsh             # shell completion
```
