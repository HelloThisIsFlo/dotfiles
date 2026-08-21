# Mise Tool Management — Cheat Sheet

You want every project and machine to use the right tool versions without
manually juggling installers or PATH entries. This covers the practical
lifecycle: declare, install, upgrade, lock, run temporarily, and clean up.

---

## Daily workflow (opinionated)

> **For a reproducible project:** enable auto-locking in the project's config so
> `mise.lock` stays in sync automatically.
>
> ```toml
> # mise.toml
> [settings]
> lockfile = true
> ```
>
> Global config is different: create its separate lockfile explicitly with
> `mise lock --global` if you actually want to maintain one.

### Install from config

You just cloned a repo, pulled changes, or edited `mise.toml` by hand. Sync your tools to match:

```bash
mise install                  # install tools from the active config stack
mise install --dry-run        # preview what would be installed
```

### Add a new tool

For a project, let mise update the config and install the tool:

```bash
mise use eza@latest           # writes to mise.toml + installs + updates lockfile
```

For your chezmoi-managed global config, keep the source of truth in chezmoi:

```bash
chezmoi edit ~/.config/mise/config.toml
chezmoi apply
```

The full apply deploys the config, then your run-on-change script runs
`mise install` automatically when that config changed.

### Upgrade within constraints

Stays within your version spec. `python = '3.14'` gets the latest eligible
3.14.x. `node = 'lts'` follows the current eligible LTS release, which can move
to a newer LTS major:

```bash
mise upgrade                  # upgrade all tools
mise upgrade node             # upgrade just node
mise upgrade --dry-run        # preview first
```

### Upgrade past constraints

Jumps to the latest eligible version and rewrites the config at the same
precision:

```bash
mise upgrade --bump           # upgrade all + update config
mise upgrade node --bump      # bump just node
```

### Try a version temporarily

`mise x` is the short alias for `mise exec`. It uses the version for one command
and touches neither config nor lockfile:

```bash
mise x node@22 -- node -v
mise x python@3.12 -- python script.py
```

### After any change

For a project using a lockfile, commit both `mise.toml` and `mise.lock`. On
another machine, `mise install` reuses the locked versions and available
artifact metadata. Strict mode is required if you also want to forbid provider
API resolution.

---

## `mise use` — declare which version you want

**The problem:** You want to add a tool (or change its version) and have it tracked in config so your team/machines stay in sync.

`mise use` both installs the tool and writes the version spec to `mise.toml`.

### Local vs global

```bash
mise use node@20              # writes to ./mise.toml (project-local)
mise use -g rust@stable       # writes to ~/.config/mise/config.toml (global)
mise use -p ~/work/mise.toml node@20  # writes to a specific file
mise use -e local node@20     # writes to .mise.local.toml (git-ignored)
```

### Version specifiers

All of these work — pick the granularity you need:

| Spec | Meaning | Example from your config |
|------|---------|--------------------------|
| `latest` | newest eligible release | `delta = 'latest'` |
| `lts` | latest LTS release (node-specific) | `node = 'lts'` |
| `stable` | latest stable release | `rust = 'stable'` |
| `3` | latest 3.x.x (prefix match) | `ruby = '3'` |
| `3.14` | latest eligible 3.14.x | `python = '3.14'` |
| `1.20.1-otp-29` | exact version with variant | `elixir = '1.20.1-otp-29'` |
| `temurin-21` | named distribution + version | `java = 'temurin-21'` |

### Fuzzy vs pinned

```bash
mise use node@20              # saves "20" in config (fuzzy — default)
mise use --pin node@20        # saves "20.15.1" in config (exact resolved version)
```

- **Fuzzy** (default): stores the prefix you gave. On next install, resolves to latest match.
- **Pinned** (`--pin`): stores the exact version that was resolved at `use` time.
- To make `--pin` the default, set `pin = true` in `[settings]` or `MISE_PIN=1`.

### Other useful flags

- `--force` — reinstall even if already installed
- `--remove <tool>` — remove a tool from config
- `--dry-run` — preview what would happen
- `--minimum-release-age <age-or-date>` — ignore newer releases when the backend provides release timestamps (`12h`, `2026-08-01`)

**Verdict:** This is the primary command for project or unmanaged config. For
your chezmoi-managed global config, use the repo's `edit → apply` workflow
instead; the apply hook installs changed tools automatically.

---

## `mise install` — download without changing config

**The problem:** You want to install a specific version without writing it to any config file. Or you want to install everything declared in config.

```bash
mise install                  # install all tools from active configs
mise install node@20.15.1     # install a specific version (doesn't touch config)
mise install --force          # reinstall even if present
mise install --dry-run        # preview what would be installed
```

- **With no args:** installs everything resolved from the active config stack.
- **With args:** installs the specified version to `~/.local/share/mise/installs/<tool>/<version>`.
- **Important:** installing alone does NOT activate the tool (won't appear in PATH). Use `mise use` to activate, or `mise exec` for one-off runs.

### Auto-install

Mise auto-installs missing tools by default when you:
- Run `mise exec` / `mise x`
- Run `mise run` (tasks)
- Type a command handled by the "command not found" hook

Each path has its own setting: `exec_auto_install`, `task.run_auto_install`, and
`not_found_auto_install`. The broader `auto_install` setting is also enabled by
default.

**Good for:** Pre-fetching a version you're not ready to switch to, or bootstrapping a fresh machine (`mise install` with no args).

---

## `mise ls` — see what's installed

**The problem:** You want to know which versions are installed, which are active, or which are missing.

```bash
mise ls                       # all installed tools + their source config
mise ls node                  # just node versions
mise ls --current             # only tools active in the current context
mise ls --global              # only tools from global config
mise ls --missing             # tools declared in config but not installed
mise ls --installed           # opposite — only show what's actually on disk
mise ls --outdated            # flag which versions have newer releases
mise ls --prunable            # versions safe to remove (not referenced by any config)
mise ls --json                # structured output
```

**Good for:** Quick sanity checks. `mise ls --missing` after cloning a repo tells you what to install. `mise ls --prunable` before `mise prune` tells you what will be cleaned.

---

## `mise outdated` — check for newer versions

**The problem:** You want to know if newer versions exist for your tools, without changing anything.

```bash
mise outdated                 # show all outdated tools
mise outdated node            # check a specific tool
mise outdated --bump          # also show versions beyond your constraint
mise outdated --json          # structured output
```

Output columns:
- **Requested** — what your config says (e.g. `3.14`)
- **Current** — what's installed (e.g. `3.14.1`)
- **Latest** — newest eligible version matching your constraint (or beyond it with `--bump`)

The difference between default and `--bump`:
- Default: `python = '3.14'` only shows newer eligible 3.14.x releases
- `--bump`: also shows eligible releases beyond the 3.14 constraint

**Good for:** Periodic maintenance. Run `mise outdated` to see what's stale, then decide what to upgrade.

---

## `mise upgrade` — update to newer versions

**The problem:** You want to upgrade installed tools to newer versions.

```bash
mise upgrade                  # upgrade all tools within their version constraints
mise upgrade node             # upgrade just node
mise upgrade --dry-run        # preview what would change
mise upgrade --interactive    # pick which tools to upgrade from a menu
mise upgrade --exclude go     # upgrade everything except go
```

### `--bump` — break out of your constraint

```bash
mise upgrade --bump           # upgrade AND update mise.toml to new major/minor
mise upgrade node --bump      # bump just node
```

Without `--bump`: respects your config constraint. `python = '3.14'` stays on
3.14.x. Dynamic selectors such as `node = 'lts'` continue to follow their
eligible channel and may cross a major boundary.

With `--bump`: upgrades to the latest eligible version and rewrites the config
selector while preserving its precision. An exact selector remains exact; a
major/minor selector remains major/minor.

### Lockfile interaction

See [`mise lock`](#mise-lock--pin-versions-for-reproducible-installs) below. When `lockfile = true`, `mise upgrade` auto-updates `mise.lock`.

**Good for:** Routine updates. Run `mise upgrade` weekly/monthly. Use `--bump` when you're ready for a major version jump.

---

## `mise lock` — pin versions for reproducible installs

**The problem:** Fuzzy specs like `node = 'lts'` and `python = '3.14'` can resolve
to different releases over time. `mise lock` records the current resolution.

```bash
mise lock                     # generate/update mise.lock from current mise.toml
```

### What `mise.lock` contains

```toml
[[tools.node]]
version = "22.14.0"
backend = "core:node"

[tools.node.platforms.macos-arm64]
checksum = "sha256:abc123..."
size = 30485721
url = "https://nodejs.org/dist/v22.14.0/node-v22.14.0-darwin-arm64.tar.gz"
```

Each entry pins an **exact version**. Supported backends can also record the
platform's download URL, checksum, and size. Backend support varies, so an
ordinary lockfile does not guarantee that every install avoids provider APIs.

### The workflow

1. `mise use node@lts` — writes fuzzy spec to `mise.toml`
2. `mise lock` — resolves and freezes to `mise.lock`
3. Commit both `mise.toml` + `mise.lock`
4. On another machine: `mise install` reuses the recorded resolution and any available artifact metadata

### Auto-locking

```toml
# In ~/.config/mise/config.toml or project mise.toml
[settings]
lockfile = true
```

With `lockfile = true`, install and version-changing commands create or maintain
the project lockfile. Without it, mise still reads and updates an existing
lockfile, but does not create one automatically. A global lockfile is created
explicitly with `mise lock --global`.

### Strict mode (`MISE_LOCKED=1`)

Requires a locked URL for the current platform and avoids provider resolution
APIs. The artifact can still require a network download unless it is cached.

**Verdict:** Use and commit it for projects where reproducibility matters. Treat
the global lockfile as an explicit choice rather than an automatic companion to
your chezmoi-managed global config. See [Security & Trust](security-trust.md)
for checksums, provenance verification, and strict mode details.

---

## `mise prune` — remove unused versions

**The problem:** Old tool versions pile up in `~/.local/share/mise/installs/`. You want to reclaim disk space.

```bash
mise prune                    # remove all unused versions
mise prune node               # prune only node versions
mise prune --dry-run          # preview what would be deleted
mise prune --tools            # only prune unused tool versions
mise prune --configs          # only prune broken config links
```

A version is "unused" if it is not referenced by a tracked config file (mise
checks `~/.local/state/mise/tracked-configs`). Versions used only through
`MISE_<TOOL>_VERSION` or a one-off `mise exec` can still be considered prunable.

Preview first: `mise ls --prunable` shows what would go.

**Good for:** Periodic cleanup. Preview first if you rely on environment-only or
one-off versions.

---

## `mise exec` / `mise x` — run with a specific version

**The problem:** You want to run a command with a particular tool version without changing your shell or config.

```bash
mise exec node@20 -- node -v                # run node 20, don't touch config
mise x node@20 -- node -v                   # same, shorter alias
mise x python@3.12 -- python script.py      # use python 3.12 for one command
mise x node@20 python@3.12 -- npm test      # multiple tools at once
mise exec node@20 -c "node -v && npm -v"    # pass command as string
```

- Auto-installs the tool if not present (controlled by `exec_auto_install` setting).
- Does NOT modify your shell environment or config files.
- Other tools from your `mise.toml` remain active alongside the specified ones.

**Good for:** Testing against a different version, CI scripts, one-off commands where you don't want to switch your project's version.

---

## `mise where` — find the install path

**The problem:** You need the filesystem path where a tool is installed (for linking, debugging, setting `JAVA_HOME`, etc.).

```bash
mise where node               # path to currently active node
mise where node@20            # path to installed node 20.x
mise where java               # e.g. ~/.local/share/mise/installs/java/temurin-21.0.3+9.0.LTS
```

Returns the full path to the install directory, e.g. `~/.local/share/mise/installs/node/20.15.1`.

**Good for:** Setting env vars that need absolute paths, debugging "which binary is actually running."

---

## `mise bin-paths` — list all active bin directories

**The problem:** You want to see which directories mise is adding to your PATH.

```bash
mise bin-paths                # all active tool bin directories
mise bin-paths node           # just node's bin directory
```

Output is one path per line — the directories containing the actual executables for each active tool.

**Good for:** Debugging PATH issues, understanding which binary wins when multiple tools provide the same command.

---

## Version resolution — how mise decides which version to use

**The problem:** You have `mise.toml` in your project, a global config, and maybe a `.python-version` file. Which one wins?

Mise merges global config, ancestor directories, the project directory, local
overrides, environment-specific config, and enabled idiomatic version files.
Closer or higher-precedence sources win per tool, while non-conflicting entries
continue to merge.

### Config file precedence

Within one directory, these are checked from highest to lowest precedence:

| Priority | File |
|---|---|
| 1 | `mise.local.toml` |
| 2 | `mise.toml` |
| 3 | `mise/config.toml` |
| 4 | `.mise/conf.d/*.toml` (alphabetical) |
| 5 | `.config/mise.toml` |
| 6 | `.config/mise/config.toml` |
| 7 | `.config/mise/conf.d/*.toml` (alphabetical) |

> **Dotfile and environment variants.** Paths beginning with `mise` can also
> begin with a dot, such as `.mise.toml`. `MISE_ENV` adds environment-specific
> variants such as `mise.production.toml`; local variants take precedence.

### Directory precedence

Mise walks upward from your current directory. A config in the current project
overrides a conflicting value from its parent directory or the global config,
but all non-conflicting values still merge.

### Idiomatic version files

`.python-version`, `.node-version`, `.ruby-version`, `.java-version` — disabled by default since mise 2025.10.0. Your config enables them selectively:

```toml
# From your ~/.config/mise/config.toml
[settings]
idiomatic_version_file_enable_tools = ['python', 'node', 'ruby', 'java']
```

When enabled, these files are evaluated alongside mise config at the same
directory level. Mise config wins for the same tool.

Use `mise config ls` to see loaded config files, `mise ls --current` to see the
resolved tools, and `mise which <tool>` to see the selected binary. See
[Config Hierarchy](config-hierarchy.md) for the full merge rules and
environment-specific resolution.

---

## Related

- [Backends](backends.md) — aqua, cargo, npm, and other install backends
- [Config Hierarchy](config-hierarchy.md) — config file resolution and merge semantics
- [Language Features](language-features.md) — Python, Node, Ruby, Java-specific settings
- [Security & Trust](security-trust.md) — lockfile checksums, provenance verification, strict mode
- [Settings](settings.md) — auto_install, pin, and other tool management settings

---

## Quick reference

| I want to... | Use |
|---|---|
| Add a tool to my project | `mise use node@20` |
| Add a tool to chezmoi-managed global config | `chezmoi edit` → `chezmoi apply` |
| Pin exact version in config | `mise use --pin node@20` |
| Install without changing config | `mise install node@20.15.1` |
| Install everything from config | `mise install` |
| See what's installed | `mise ls` |
| See what's missing | `mise ls --missing` |
| Check for updates | `mise outdated` |
| Upgrade within constraints | `mise upgrade` |
| Upgrade past constraints | `mise upgrade --bump` |
| Clean up old versions | `mise prune` (preview with `--dry-run`) |
| Run one command with a specific version | `mise x node@20 -- node -v` |
| Find where a tool is installed | `mise where node` |
| Debug PATH issues | `mise bin-paths` |
| See what version would be used here | `mise ls --current` |
| Lock a project for reproducible installs | `mise lock` (commit `mise.lock`) |
| Lock the global config explicitly | `mise lock --global` |
