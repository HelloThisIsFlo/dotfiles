# Chezmoi Hooks — Cheat Sheet

Run scripts cover most automation needs, but they all share one limitation: they execute *during* `chezmoi apply`, after chezmoi has already read and parsed your source directory. If a template calls `{{ rbw "some-secret" }}` and `rbw` isn't installed yet, chezmoi fails before any script gets a chance to run. Hooks solve this by letting you execute commands at lifecycle points that run scripts can't reach.

---

## How hooks differ from run scripts

This is the most important thing to understand. Run scripts are files in your source directory with `run_` prefixes. Hooks are configured in `chezmoi.toml`. They serve different purposes and fire at different times.

| | Run scripts | Hooks |
|---|---|---|
| Defined in | Source directory (files) | `chezmoi.toml` (config) |
| Controlled by | Filename prefixes (`run_once_before_`) | Config sections (`[hooks.apply.pre]`) |
| When they run | During `chezmoi apply` only | Before/after specific events |
| Respect `--dry-run`? | Yes — skipped in dry run | **No — always run, even with `--dry-run`** |
| Can run before source state is read? | No | Yes (`read-source-state.pre`) |
| Tracked by chezmoi? | Yes (`run_once_`, `run_onchange_`) | No — always run every time |

The `--dry-run` behaviour is the gotcha that catches people. If your hook has side effects (installing packages, modifying files), it will do those things even when you're just previewing with `chezmoi apply --dry-run`.

> **Hooks should be fast and idempotent.** Because they run every time and ignore `--dry-run`, a slow or non-idempotent hook will make every chezmoi command painful. Check whether work is needed before doing it.

---

## The four event types

Hooks fire on four categories of event, each with a `.pre` and `.post` variant:

| Event | Trigger | When you'd use it |
|---|---|---|
| `read-source-state` | Chezmoi reads and parses templates | Ensure dependencies exist before templates are evaluated |
| *command* (e.g. `apply`, `add`, `diff`) | Any chezmoi command | Run something before/after a specific command |
| `git-auto-commit` | Auto-commit is generated | Customise commit behaviour (sign, lint, validate) |
| `git-auto-push` | Auto-push runs | Run checks before pushing, notify after push |

The first one is the important one. `read-source-state.pre` fires before chezmoi evaluates any templates — this is the only way to ensure a tool exists before a template function tries to call it.

The *command* event is a wildcard — it's not a single event but any chezmoi command name. So `hooks.apply.pre`, `hooks.diff.post`, `hooks.add.pre` are all valid. This means the total number of hook points is much larger than four.

---

## Configuring hooks

Hooks live in `chezmoi.toml` (or `.chezmoi.toml.tmpl`). Each hook specifies either a `command` (executed directly) or a `script` (executed via the configured interpreter for its extension).

### Command form

```toml
[hooks.read-source-state.pre]
command = ".install-password-manager.sh"
args = []
```

The `command` is executed directly — no shell involved. If you need shell features (pipes, redirects, variable expansion), use the script form or point to a shell script.

### Script form

```toml
[hooks.add.post]
script = "post-add-hook.sh"
```

Scripts are executed using the interpreter configured for their file extension. See the [Configuration cheat sheet](config.md) for interpreter setup.

---

## The canonical use case: password manager bootstrap

This is why hooks exist in practice. If your templates use `{{ rbw "some-secret" }}` or `{{ bitwarden ... }}`, chezmoi needs that tool available *before* it reads source state. A `run_once_before_` script is too late — it runs during apply, after templates have already been parsed.

The solution is a `read-source-state.pre` hook that installs the password manager if it's missing:

```toml
[hooks.read-source-state.pre]
command = ".install-password-manager.sh"
```

The script (stored in your source directory root):

```bash
#!/bin/bash
set -euo pipefail

# Already installed? Done.
if command -v rbw &> /dev/null; then
  exit 0
fi

# Install rbw
if [[ "$(uname)" == "Darwin" ]]; then
  brew install rbw
elif [[ "$(uname)" == "Linux" ]]; then
  # Adjust for your distro
  cargo install rbw
fi
```

> **The idempotency check matters.** Without the `command -v rbw` guard, this would try to install rbw on every single chezmoi command — `chezmoi diff`, `chezmoi status`, `chezmoi data`, everything. The `read-source-state` event fires constantly.

### The chicken-and-egg problem

Here's the execution order that makes this necessary:

```
1. chezmoi init / apply starts
2. → read-source-state.pre hook fires     ← installs rbw
3. → chezmoi reads source directory
4. → templates are parsed and evaluated    ← {{ rbw "..." }} now works
5. → run_once_before_ scripts execute
6. → files are applied
7. → run_once_after_ scripts execute
```

Without the hook, step 4 would fail because `rbw` doesn't exist yet. `run_once_before_` (step 5) is too late.

See the [Secrets cheat sheet](secrets.md) for how to use `rbw` in templates once it's installed.

---

## Git hooks

If you have `autoCommit` and/or `autoPush` enabled in your config, these hooks let you customise what happens around those operations.

```toml
[git]
autoCommit = true
autoPush = false

# Run before auto-commit (e.g., lint dotfiles)
[hooks.git-auto-commit.pre]
command = "echo"
args = ["about to auto-commit"]

# Run after auto-push (e.g., notify)
[hooks.git-auto-push.post]
command = "echo"
args = ["push complete"]
```

Realistic uses: signing commits, running a linter on your source directory before committing, sending a notification after push. Most people with `autoCommit = true` won't need these — they're there if you want fine-grained control.

---

## Per-command hooks

You can hook into any chezmoi command by name. These are genuinely niche — most of the time, run scripts or the `read-source-state` hook cover your needs.

```toml
# Run something after every `chezmoi add`
[hooks.add.post]
command = "echo"
args = ["file added to source state"]

# Run something before `chezmoi diff`
[hooks.diff.pre]
command = "echo"
args = ["about to diff"]
```

The main reason you'd use these: if you need to do something that isn't tied to file application (which is what run scripts handle) but to a specific chezmoi operation. For example, `hooks.add.post` could auto-format a file you just added, or `hooks.apply.pre` could pull state from an external source before apply runs. In practice, most people never need these.

---

## Environment variables

When hooks run, chezmoi sets these environment variables:

| Variable | Value |
|---|---|
| `CHEZMOI` | `1` (always) |
| `CHEZMOI_COMMAND` | The command being run (e.g., `apply`, `add`) |
| `CHEZMOI_COMMAND_DIR` | Directory where chezmoi was invoked |
| `CHEZMOI_ARGS` | Full argument string, starting with the chezmoi executable path |

These are the same variables available to run scripts. You also get the standard `CHEZMOI_*` template data variables (`CHEZMOI_OS`, `CHEZMOI_ARCH`, etc.).

Additionally, any variables you define in `[scriptEnv]` in your config are available to hooks:

```toml
[scriptEnv]
MY_DOTFILES_DIR = "/path/to/dotfiles"
```

---

## When not to use hooks

Hooks are the wrong tool when:

- **You want frequency control** — hooks run every time, unconditionally. If you need "run once" or "run when changed" semantics, use `run_once_` or `run_onchange_` scripts instead.
- **You want ordering relative to file operations** — hooks fire before/after events, not before/after specific files. For "install packages, then apply configs", use `run_once_before_` scripts.
- **You want dry-run safety** — hooks ignore `--dry-run`. If your action has destructive side effects, a run script that respects dry-run is safer.

The only situation where hooks are genuinely necessary: you need something to happen before chezmoi reads your source state. That's the password manager bootstrap pattern above. Everything else is a convenience — handy, but run scripts can usually do it.

---

## Quick reference

| I want to... | Use |
|---|---|
| Install a tool before templates are parsed | `[hooks.read-source-state.pre]` |
| Run something before/after `chezmoi apply` | `[hooks.apply.pre]` / `[hooks.apply.post]` — but consider a run script instead |
| Customise auto-commit behaviour | `[hooks.git-auto-commit.pre]` / `.post` |
| Customise auto-push behaviour | `[hooks.git-auto-push.pre]` / `.post` |
| Run after `chezmoi add` | `[hooks.add.post]` |
| Run something once only | Use a `run_once_` script, not a hook |
| Run when a script's content changes | Use a `run_onchange_` script, not a hook |

**Config syntax:**

```toml
# Command form (executed directly)
[hooks.EVENT.pre]
command = "my-command"
args = ["arg1", "arg2"]

# Script form (uses configured interpreter)
[hooks.EVENT.post]
script = "my-script.sh"
```

Replace `EVENT` with: `read-source-state`, `git-auto-commit`, `git-auto-push`, or any chezmoi command name (`apply`, `add`, `diff`, `edit`, etc.).
