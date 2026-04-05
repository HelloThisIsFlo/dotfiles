# Mise Tool Management — Cheat Sheet

Managing tool versions with mise: installing, upgrading, pinning, pruning, and running tools ad-hoc. Covers the full lifecycle from "I need node 20" to "clean up old versions."

---

## Daily workflow (opinionated)

**One-time setup:** enable auto-locking so `mise.lock` stays in sync automatically.

```toml
# ~/.config/mise/config.toml (or project mise.toml)
[settings]
lockfile = true
```

**From here, the core loop is three commands:**

| What | Command | What happens |
|---|---|---|
| Install everything from config | `mise install` | Reads `mise.toml`, installs missing tools, auto-updates `mise.lock` |
| Upgrade within constraints | `mise upgrade` | e.g. `python = '3.13'` gets latest 3.13.x, lockfile updates |
| Upgrade past constraints | `mise upgrade --bump` | Jumps to latest major/minor, rewrites `mise.toml` + lockfile |
| Try a version temporarily | `mise x node@22 -- node -v` | Uses node 22 for one command, touches nothing |
| Add a new tool | `mise use eza@latest` | Installs + writes to `mise.toml` + updates lockfile |

After any change, commit both `mise.toml` and `mise.lock`. On another machine, `mise install` reproduces the exact same versions — no resolution, no API calls.

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
| `latest` | absolute latest release | `delta = 'latest'` |
| `lts` | latest LTS release (node-specific) | `node = 'lts'` |
| `stable` | latest stable release | `rust = 'stable'` |
| `3` | latest 3.x.x (prefix match) | `ruby = '3'` |
| `3.13` | latest 3.13.x | `python = '3.13'` |
| `1.19.5-otp-28` | exact version with variant | `elixir = '1.19.5-otp-28'` |
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
- `--before <date>` — restrict to versions released before a date (`2024-06-01` or `90d`)

**Verdict:** This is the primary command for managing tools. Use it instead of editing `mise.toml` by hand + running `mise install`.

---

## `mise install` — download without changing config

**The problem:** You want to install a specific version without writing it to any config file. Or you want to install everything declared in config.

```bash
mise install                  # install all tools from mise.toml
mise install node@20.15.1     # install a specific version (doesn't touch config)
mise install --force          # reinstall even if present
mise install --dry-run        # preview what would be installed
```

- **With no args:** installs everything in the current `mise.toml`.
- **With args:** installs the specified version to `~/.local/share/mise/installs/<tool>/<version>`.
- **Important:** installing alone does NOT activate the tool (won't appear in PATH). Use `mise use` to activate, or `mise exec` for one-off runs.

### Auto-install

Mise auto-installs missing tools by default when you:
- Run `mise exec` / `mise x`
- Run `mise run` (tasks)
- Type a command handled by the "command not found" hook

Controlled by `auto_install = true` (default) in settings. Disable per-tool with `auto_install_disable_tools`.

**Good for:** Pre-fetching a version you're not ready to switch to, or bootstrapping a fresh machine (`mise install` with no args).

---

## `mise ls` — see what's installed

**The problem:** You want to know which versions are installed, which are active, or which are missing.

```bash
mise ls                       # all installed tools + their source config
mise ls node                  # just node versions
mise ls --current             # only tools specified in a mise.toml
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
- **Requested** — what your config says (e.g. `3.13`)
- **Current** — what's installed (e.g. `3.13.1`)
- **Latest** — newest version matching your constraint (or absolute latest with `--bump`)

The difference between default and `--bump`:
- Default: `python = '3.13'` only shows newer 3.13.x releases
- `--bump`: also shows 3.14.x, 3.15.x, etc.

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

Without `--bump`: respects your config constraint. `node = 'lts'` stays on current LTS line, `python = '3.13'` stays on 3.13.x.

With `--bump`: upgrades to absolute latest AND rewrites `mise.toml` to match. Preserves your precision — if config says `'3'`, it writes `'3'` (not `'3.15.2'`). If config says `'3.13'`, it writes `'3.15'`.

### Lockfile interaction

See [`mise lock`](#mise-lock--pin-versions-for-reproducible-installs) below. When `lockfile = true`, `mise upgrade` auto-updates `mise.lock`.

**Good for:** Routine updates. Run `mise upgrade` weekly/monthly. Use `--bump` when you're ready for a major version jump.

---

## `mise lock` — pin versions for reproducible installs

**The problem:** Fuzzy specs like `node = 'lts'` and `python = '3.13'` resolve to whatever the latest matching release is *today*. Tomorrow a new patch ships, and your teammate gets a different binary. `mise lock` freezes the resolution.

```bash
mise lock                     # generate/update mise.lock from current mise.toml
```

### What `mise.lock` contains

```toml
[tools.node]
version = "22.14.0"

[tools.node.assets."macos-arm64"]
checksum = "sha256:abc123..."
url = "https://nodejs.org/dist/v22.14.0/node-v22.14.0-darwin-arm64.tar.gz"
```

Each entry pins the **exact version**, **download URL**, and **checksum** — per platform. With a lockfile present, `mise install` skips all version resolution and API calls entirely.

### The workflow

1. `mise use node@lts` — writes fuzzy spec to `mise.toml`
2. `mise lock` — resolves and freezes to `mise.lock`
3. Commit both `mise.toml` + `mise.lock`
4. On another machine: `mise install` reads `mise.lock` — no resolution, no API calls, same binary

### Auto-locking

```toml
# In ~/.config/mise/config.toml or project mise.toml
[settings]
lockfile = true
```

With `lockfile = true`, `mise use`, `mise upgrade`, and `mise install` all auto-update `mise.lock` — no need to run `mise lock` manually.

### Strict mode (`MISE_LOCKED=1`)

Refuses to install any tool not in the lockfile. Zero network resolution. Ideal for CI where you want fully reproducible, offline-capable installs.

**Verdict: Use it.** Commit `mise.lock` alongside `mise.toml` — it's your `package-lock.json` equivalent. See [Security & Trust](security-trust.md) for checksums, provenance verification, and strict mode details.

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

A version is "unused" if it's not referenced by any tracked config file (mise checks `~/.local/state/mise/tracked-configs`).

Preview first: `mise ls --prunable` shows what would go.

**Good for:** Periodic cleanup. Safe to run regularly — it won't touch anything actively referenced.

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

## Version resolution order — how mise decides which version to use

**The problem:** You have `mise.toml` in your project, a global config, and maybe a `.python-version` file. Which one wins?

### Config file precedence (highest to lowest, per directory)

1. `mise.local.toml` (git-ignored local overrides)
2. `mise.toml`
3. `mise/config.toml`
4. `.mise/config.toml`
5. `.config/mise.toml`
6. `.config/mise/config.toml`
7. `.config/mise/conf.d/*.toml` (alphabetical)

### Directory tree resolution

Mise walks **up** from your current directory to `/`. Closer configs win:

```
~/src/work/myproj/mise.toml    <-- wins for this project
~/src/work/mise.toml            <-- applies if myproj doesn't override
~/.config/mise/config.toml      <-- global fallback
```

### Idiomatic version files

`.python-version`, `.node-version`, `.ruby-version`, `.java-version` — disabled by default since mise 2025.10.0. Your config enables them selectively:

```toml
# From your ~/.config/mise/config.toml
[settings]
idiomatic_version_file_enable_tools = ['python', 'node', 'ruby', 'java']
```

When enabled, these files are evaluated alongside `mise.toml` at the same directory level. The `mise.toml` entry wins if both exist in the same directory.

### Environment-specific configs

Set `MISE_ENV=production` and mise also loads `mise.production.toml`, which overrides the base `mise.toml`.

**Key insight:** The resolution is always "most specific directory + most specific file wins." Global config is just the fallback, not a floor.

---

## Quick decision guide

| I want to... | Use |
|---|---|
| Add a tool to my project | `mise use node@20` |
| Add a tool globally | `mise use -g node@lts` |
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
| Pin exact versions for reproducible installs | `mise lock` (commit `mise.lock`) |

---

## Related

- [Backends](backends.md) — aqua, cargo, npm, and other install backends
- [Config Hierarchy](config-hierarchy.md) — config file resolution and merge semantics
- [Language Features](language-features.md) — Python, Node, Ruby, Java-specific settings
- [Security & Trust](security-trust.md) — lockfile checksums, provenance verification, strict mode
- [Settings](settings.md) — auto_install, pin, and other tool management settings
