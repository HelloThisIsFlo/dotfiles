# Mise CI & Bootstrap — Cheat Sheet

Mise works in CI the same way it works locally: install tools from a config file, run tasks. The main difference is that CI has no interactive shell, so you skip activation and use shims, `mise exec`, or `mise run` instead.

---

## Installing mise in CI

**The problem:** CI runners don't have mise pre-installed. You need a fast, deterministic way to get it.

### Curl installer (universal)

```bash
curl https://mise.run | sh
export PATH="$HOME/.local/bin:$PATH"
```

Control the install with environment variables:

| Variable | Purpose | Example |
|---|---|---|
| `MISE_INSTALL_PATH` | Where the binary lands | `/usr/local/bin/mise` |
| `MISE_VERSION` | Pin a specific release | `v2025.12.0` |
| `MISE_QUIET` | Suppress non-error output | `1` |
| `MISE_DEBUG` | Verbose logging | `1` |

### Bootstrap script (self-contained)

`mise generate bootstrap` creates a script that downloads mise on first run, then acts as the mise binary. Useful for repos where contributors shouldn't need mise pre-installed.

```bash
# Generate once, commit the script
mise generate bootstrap > ./bin/mise
chmod +x ./bin/mise

# In CI or on a new machine
./bin/mise install
./bin/mise run ci
```

Flags:
- `-w, --write <PATH>` — write to file and make executable
- `-l, --localize` — isolate `MISE_DATA_DIR` and `MISE_CACHE_DIR` into `.mise/` (avoids version conflicts)
- `-V, --version <VERSION>` — pin the mise version the script downloads
- `--localized-dir <DIR>` — custom directory for localized data (default: `.mise`)

**Verdict:** Bootstrap script is best for open-source repos where you can't assume contributors have mise. Curl installer is simpler for private CI.

---

## GitHub Actions

**The problem:** You want mise-managed tools available in your workflow without manual install/PATH juggling.

### Official action: `jdx/mise-action`

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v2
        with:
          version: 2025.4.0    # optional, default: latest
          cache: true           # default: true
      - run: node --version    # tools are on PATH via shims
      - run: mise run test
```

Key inputs:

| Input | Default | Notes |
|---|---|---|
| `version` | latest | Pin for reproducibility |
| `install` | `true` | Set `false` to skip `mise install` |
| `install_args` | `""` | Extra args passed to `mise install` |
| `cache` | `true` | Caches mise tool installations |
| `experimental` | `false` | Enable experimental features |
| `tool_versions` | — | Inline tool specs (overrides config files) |
| `mise_toml` | — | Inline TOML config |
| `working_directory` | `.` | Where mise runs |
| `github_token` | `${{ github.token }}` | For GitHub API calls (rate limit) |

The action runs `mise install`, adds shims to `PATH`, and sets environment variables. After the action step, tools are available directly (no `mise exec` needed).

**Verdict:** Use `jdx/mise-action` for GitHub Actions. It handles caching, PATH, and installation in one step.

### Generated workflow: `mise generate github-action`

Generates a workflow file that runs a mise task on push:

```bash
mise generate github-action --write --task=ci
# Creates .github/workflows/ci.yml
```

Flags:
- `-t, --task <TASK>` — task to run (default: `ci`)
- `-w, --write` — write to `.github/workflows/$name.yml`
- `--name <NAME>` — workflow filename (default: `ci`)

The generated workflow uses `jdx/mise-action` internally, then runs `mise run <task>`.

---

## Docker

**The problem:** You need mise-managed tools in container builds.

### Basic Dockerfile

```dockerfile
FROM ubuntu:24.04

# Install mise
RUN apt-get update && apt-get install -y curl
ENV MISE_INSTALL_PATH="/usr/local/bin/mise"
RUN curl https://mise.run | sh

# Copy config and install tools
COPY mise.toml mise.lock ./
ENV MISE_YES=1
RUN mise install

# Add shims to PATH for all subsequent commands
ENV PATH="/root/.local/share/mise/shims:$PATH"

COPY . .
RUN mise run build
```

### Multi-stage build

```dockerfile
# Stage 1: build with mise tools
FROM ubuntu:24.04 AS builder

ENV MISE_INSTALL_PATH="/usr/local/bin/mise"
RUN apt-get update && apt-get install -y curl \
    && curl https://mise.run | sh

COPY mise.toml mise.lock ./
ENV MISE_YES=1
RUN mise install

ENV PATH="/root/.local/share/mise/shims:$PATH"
COPY . .
RUN mise run build

# Stage 2: runtime (no mise, no build tools)
FROM ubuntu:24.04
COPY --from=builder /app/dist /app
CMD ["/app/server"]
```

**Verdict:** Install mise early, copy config files before source code (better layer caching). Use multi-stage to keep mise out of production images.

---

## Lockfile strictness

**The problem:** Loose version specs (`node = "22"`) can resolve to different patch versions across machines and time. CI builds become non-deterministic.

### `mise.lock`

When `lockfile = true` is set in `mise.toml` settings, mise writes a `mise.lock` file with exact resolved versions, download URLs, and checksums. Commit this file.

```toml
# mise.toml
[settings]
lockfile = true
```

### Strict mode for CI

The `locked` setting makes `mise install` fail if any tool doesn't have a pre-resolved URL in the lockfile. This catches config/lock drift.

```bash
# In CI
MISE_LOCKED=1 mise install
```

| Setting | Env var | Effect |
|---|---|---|
| `lockfile = true` | `MISE_LOCKFILE=1` | Read/write lockfile on install |
| `locked = true` | `MISE_LOCKED=1` | Fail if lockfile is missing or incomplete |
| `locked_verify_provenance = true` | `MISE_LOCKED_VERIFY_PROVENANCE=1` | Re-verify supply-chain signatures |

**Verdict:** Use `lockfile = true` in your config, commit `mise.lock`, and set `MISE_LOCKED=1` in CI. This gives you loose specs for convenience locally with pinned versions in CI.

---

## Running tools in CI: exec vs activate vs shims

**The problem:** `mise activate` hooks into your shell prompt. CI doesn't have a prompt. You need another way to run mise-managed tools.

### Option 1: `mise exec` (explicit, no setup)

```bash
mise exec -- node build.js
mise exec -- pytest
mise exec python@3.12 -- python script.py
```

Loads tools and env vars for a single command. No PATH modification. Good for one-off commands.

### Option 2: Shims on PATH (set once, use everywhere)

```bash
export PATH="$HOME/.local/share/mise/shims:$PATH"
node build.js   # uses the shim
pytest           # uses the shim
```

Shims are small executables that delegate to mise. Once on PATH, tools work as if natively installed. This is what `jdx/mise-action` does internally.

### Option 3: `mise run` (task runner)

```bash
mise run test
mise run build --force
mise run lint test  # runs multiple tasks
```

Tasks defined in `mise.toml` run with mise's environment automatically loaded. Dependencies between tasks are handled.

### Comparison

| Approach | Setup | Best for |
|---|---|---|
| `mise exec` | None | One-off commands, scripts |
| Shims on PATH | One `export` | Multi-step CI where many commands need tools |
| `mise run` | Task definitions in `mise.toml` | Structured CI pipelines with dependencies |
| `mise activate` | Shell hook | **Not for CI** — requires interactive shell |

**Verdict:** Use `mise run` for structured CI tasks. Use shims for simple workflows where you just need tools on PATH. Avoid `mise activate` in CI entirely.

---

## Environment variables for CI

**The problem:** CI is non-interactive. Mise prompts for trust confirmation, tool installation consent, etc. These block CI.

### Essential CI variables

| Variable | Value | Why |
|---|---|---|
| `MISE_YES` | `1` | Auto-answer yes to all prompts (trust, install, etc.) |
| `MISE_TRUSTED_CONFIG_PATHS` | `/path/to/project` | Pre-trust config files without prompting |
| `MISE_LOCKED` | `1` | Fail if lockfile doesn't cover all tools |

### Useful but optional

| Variable | Value | Why |
|---|---|---|
| `MISE_QUIET` | `1` | Suppress non-error output (cleaner CI logs) |
| `MISE_SILENT` | `1` | Suppress all output including task output (except errors) |
| `MISE_OFFLINE` | `1` | Block all HTTP requests (air-gapped builds) |
| `MISE_DATA_DIR` | custom path | Control where tools are cached (for CI cache keys) |
| `MISE_PARANOID` | `1` | Extra security: verify provenance on every install |
| `MISE_AUTO_INSTALL` | `0` | Disable auto-install (force explicit `mise install`) |
| `MISE_LOG_LEVEL` | `debug` | Verbose output for debugging CI failures |

### Example: GitHub Actions env block

```yaml
env:
  MISE_YES: "1"
  MISE_LOCKED: "1"
  MISE_TRUSTED_CONFIG_PATHS: ${{ github.workspace }}
```

---

## `mise generate` — code generation utilities

**The problem:** You want to generate boilerplate for CI, hooks, and docs from your mise config.

| Command | Output | Key flags |
|---|---|---|
| `mise generate github-action` | `.github/workflows/*.yml` | `-t <task>`, `-w` (write), `--name` |
| `mise generate git-pre-commit` | `.git/hooks/pre-commit` | `-t <task>`, `-w` (write), `--hook <hook>` |
| `mise generate bootstrap` | Self-installing mise script | `-w <path>`, `-l` (localize), `-V <version>` |
| `mise generate task-docs` | Markdown docs for your tasks | |
| `mise generate config` | Starter `mise.toml` | `-n` (dry-run), `-t` (tool-versions input) |

### Git pre-commit hook

```bash
mise generate git-pre-commit --write --task=pre-commit
```

Creates `.git/hooks/pre-commit` that runs `mise run pre-commit`. Staged files are available via the `STAGED` env var in your task.

For more sophisticated pre-commit tooling, see [hk](https://hk.jdx.dev/) (mise's companion project).

---

## Self-bootstrapping patterns

**The problem:** On a fresh machine, you need tools to install tools. The bootstrap chain matters.

### Flo's dotfiles chain

```
chezmoi apply
  -> run_once_before_0001: curl-install mise (no dependencies)
  -> chezmoi applies all config files (mise.toml lands on disk)
  -> run_onchange_after_0001-CORE: brew bundle (macOS packages)
  -> run_onchange_after_0002-CORE: mise install (right after brew)
```

Key design decisions:
- **Mise self-bootstraps** via curl installer in a `run_once_before` script (no Homebrew dependency)
- **`mise install` runs right after brew** (`0002`, after `0001` brew) because it needs `mise.toml` and potentially Homebrew-installed dependencies in place first. (Not "last" — the requirement was always *after brew*, not dead-last.)
- **`run_onchange_after`** keyed on config sha256 — re-runs when config changes, not on every apply
- **`mise_install_path` in chezmoidata** — single source of truth shared by bootstrap scripts and fish config

### General pattern for any bootstrap system

```bash
#!/bin/bash
# 1. Install mise itself
curl https://mise.run | sh
export PATH="$HOME/.local/bin:$PATH"

# 2. Trust the config (non-interactive)
export MISE_YES=1

# 3. Install tools
mise install

# 4. Run setup tasks
mise run setup
```

### Bootstrap in Makefile/Justfile

```just
bootstrap:
    curl https://mise.run | sh
    ~/.local/bin/mise install
    ~/.local/bin/mise run setup
```

---

## Caching strategies

**The problem:** `mise install` downloads and builds tools. This is slow. Cache it.

### GitHub Actions

`jdx/mise-action` caches automatically when `cache: true` (the default). It caches the mise data directory keyed on `mise.toml` and `mise.lock`.

For manual caching:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.local/share/mise
    key: mise-${{ runner.os }}-${{ hashFiles('mise.toml', 'mise.lock') }}
    restore-keys: mise-${{ runner.os }}-
```

### GitLab CI

```yaml
variables:
  MISE_DATA_DIR: "$CI_PROJECT_DIR/.mise-data"

cache:
  key:
    files:
      - mise.toml
      - mise.lock
  paths:
    - .mise-data/
```

**Verdict:** Always cache `~/.local/share/mise` (or `$MISE_DATA_DIR`) keyed on your config + lock files.

---

## Decision guide

| Scenario | Approach |
|---|---|
| GitHub Actions, simple | `jdx/mise-action@v2` with `cache: true` |
| GitHub Actions, task-based | `jdx/mise-action` + `mise run ci` |
| GitLab CI | Curl install + cache `MISE_DATA_DIR` |
| Docker build | Curl install, shims on PATH, multi-stage |
| Open-source repo | `mise generate bootstrap` committed to repo |
| Deterministic CI | `mise.lock` + `MISE_LOCKED=1` |
| Single command in CI | `mise exec -- <cmd>` |
| Multi-command CI | Shims on PATH |
| Structured pipeline | `mise run` with task dependencies |
| Fresh machine bootstrap | Curl install -> `mise install` -> `mise run setup` |

---

## Related

- [Security & Trust](security-trust.md) — `MISE_LOCKED=1` and trust in CI
- [Shims vs Activation](shims-vs-activation.md) — why shims are simpler in CI
- [Tasks](tasks.md) — `mise run` for CI task execution
- [Chezmoi run scripts](../chezmoi/run-scripts.md) — bootstrap chain integration
