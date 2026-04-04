# Mise Features Worth Exploring — Cheat Sheet

The first mise cheat sheet — covering features beyond basic tool management (`mise use`, `mise install`). These are the power-user capabilities that make mise more than just "asdf but faster": lockfiles for reproducible installs, file watchers for dev loops, hooks for directory-aware automation, and a shebang trick for self-contained scripts.

---

## `mise lock` — Pin exact versions and download URLs

**The problem:** `mise install` on a fresh machine has to resolve `"latest"` -> `0.19.2` by hitting GitHub APIs. This fails transiently (rate limits, cache bugs, network issues).

```bash
$ mise lock
# Generates mise.lock in the same directory as config.toml
```

**What `mise.lock` contains:**

```toml
[tools."aqua:dandavison/delta"]
version = "0.19.2"
checksums."aarch64-apple-darwin" = "sha256:abc123..."
urls."aarch64-apple-darwin" = "https://github.com/dandavison/delta/releases/download/0.19.2/delta-0.19.2-aarch64-apple-darwin.tar.gz"

[tools.node]
version = "22.14.0"
# ... etc
```

With the lockfile committed, `mise install` skips **all** version resolution and downloads directly. No GitHub API calls, no rate limiting, no transient failures. Your bootstrap becomes deterministic.

**To update:** `mise lock` again (or `mise upgrade` which updates both config and lock).

**Verdict: Use it** — commit `mise.lock` alongside `config.toml`. Directly fixes transient bootstrap failures from version resolution.

---

## `mise watch` — File watcher for tasks

```toml
# In a project's mise.toml (not global config)
[tasks.test]
run = "cargo test"
sources = ["src/**/*.rs", "Cargo.toml"]

[tasks.lint]
run = "eslint src/"
sources = ["src/**/*.{ts,tsx}"]
```

```bash
$ mise watch test    # re-runs cargo test whenever a .rs file changes
$ mise watch lint    # re-runs eslint whenever a .ts/.tsx file changes
```

Uses `watchexec` under the hood (install with `mise use -g watchexec`).

**Verdict: Use it** — in project-level configs, not global. Great for dev loops.

---

## Hooks — Commands on directory change

Mise has two distinct hooks for directory changes:
- **`enter`/`leave`** — fire when entering/leaving a directory that has a mise config file
- **`cd`** — fires on **every** directory change, regardless of mise config

Both work in the **global** config (`~/.config/mise/config.toml`), not just project-level.

**Example — `.env` notification:**

With `env_file = '.env'` in global settings, mise auto-sources `.env` files. Add a visible notification so you know it happened:

```toml
# In ~/.config/mise/config.toml (global)
[hooks]
cd = "[ -f .env ] && echo '⚡ .env loaded in this directory'"
```

This fires on every `cd`. If the directory has a `.env`, you get a one-line notification. If not, silence.

**Multi-line version with more context:**

```toml
[hooks.cd]
script = """
if [ -f .env ]; then
  echo "⚡ .env detected — $(wc -l < .env | tr -d ' ') vars loaded from $(pwd)"
fi
"""
```

**Project-level example — auto-install tools on enter:**

```toml
# In a project's mise.toml
[hooks]
enter = "mise install --quiet"
```

**Verdict: Use it** — the global `cd` hook for `.env` notification is a one-liner with immediate value. Project-level `enter` hooks are great for auto-setup.

---

## Shebang trick — Ad-hoc tool versions in scripts

```bash
#!/usr/bin/env -S mise x node@20 -- node
// This script runs with Node 20, installed on-the-fly if needed
const data = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
console.log(data.map(x => x.name));
```

```bash
#!/usr/bin/env -S mise x python@3.12 -- python3
# This script always uses Python 3.12, regardless of what's globally active
import sys
print(sys.version)
```

The tool is installed automatically if not present. The script is self-contained — no setup needed by whoever runs it.

**Verdict: Use it** — for standalone scripts that need a specific runtime. Especially handy for scripts you share or put in project repos.

---

## Related resources

- [Mise documentation](https://mise.jdx.dev/) — official docs
- [CLI Exploration tracker](../../CLI-EXPLORATION.md) — modern CLI tool evaluations
