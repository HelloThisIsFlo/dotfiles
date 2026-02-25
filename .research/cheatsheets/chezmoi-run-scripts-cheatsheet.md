# Chezmoi Run Scripts — Cheat Sheet

Run scripts are shell scripts that chezmoi **executes** during `chezmoi apply` instead of copying to your home directory. They live in your source directory with special prefixes that control *when* and *how often* they run.

---

## The building blocks

The filename is built by chaining prefixes together. Think of it like LEGO:

```
run_  +  [once_ | onchange_]  +  [before_ | after_]  +  name.sh
```

### Frequency (how often does it run?)

| Prefix | Behaviour |
|---|---|
| `run_` | Runs **every single time** you `chezmoi apply` |
| `run_once_` | Runs **once ever**, then never again (chezmoi tracks this) |
| `run_onchange_` | Runs **only when the script's contents change** |

### Ordering (when does it run relative to file operations?)

| Prefix | Behaviour |
|---|---|
| *(none)* | Runs **during** file operations, interleaved alphabetically alongside file creates/updates/deletes |
| `before_` | Runs **before** any files are copied/updated |
| `after_` | Runs **after** all files are copied/updated |

> **Important:** If you don't specify `before_` or `after_`, the script doesn't run "at some magic time" — it runs **mixed in with the file operations**, sorted alphabetically by name alongside everything else. In practice, this means the execution order relative to specific files is unpredictable. If your script depends on a file already being in place, use `after_`. If files depend on your script, use `before_`. When in doubt, always pick one explicitly.

> **Need something to run before templates are even parsed?** Run scripts can't do this — they all execute during `chezmoi apply`, after source state is already read. If a template calls `{{ rbw "..." }}` and `rbw` isn't installed, chezmoi fails before any run script gets a chance. For that, you need [hooks](chezmoi-hooks-cheatsheet.md).

### Combining them

You chain frequency + ordering together:

```
run_once_before_install-packages.sh
run_onchange_after_brew-bundle.sh
run_after_set-defaults.sh
```

---

## Every valid combination with examples

### `run_something.sh` — runs every apply, during file operations

Every single `chezmoi apply` executes this. It runs **interleaved with file operations** (not before, not after — see ordering note above). Use sparingly — it slows down apply and the execution order relative to specific files is unpredictable.

```bash
# run_check-disk-space.sh
#!/bin/bash
df -h / | tail -1
```

**Good for:** Health checks, printing status info. Rarely what you want.

---

### `run_before_something.sh` — runs every apply, before files

```bash
# run_before_ensure-directories.sh
#!/bin/bash
mkdir -p ~/.config/nvim
mkdir -p ~/.local/bin
```

**Good for:** Creating directories that must exist before config files are written.

---

### `run_after_something.sh` — runs every apply, after files

```bash
# run_after_reload-shell.sh
#!/bin/bash
echo "Don't forget to restart your shell!"
```

**Good for:** Notifications, reloading services after config changes. But runs every time, so consider `run_onchange_after_` instead.

---

### `run_once_something.sh` — runs once ever, during file operations

Chezmoi records that this script has run. It will never run again on this machine, even if you `chezmoi apply` 100 more times. Without `before_` or `after_`, it runs interleaved with file operations.

```bash
# run_once_install-oh-my-zsh.sh
#!/bin/bash
if [ ! -d "$HOME/.oh-my-zsh" ]; then
  sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi
```

**Good for:** One-time setup on a new machine — installing frameworks, creating SSH keys, initialising databases.

---

### `run_once_before_something.sh` — runs once, before files

```bash
# run_once_before_install-homebrew.sh
#!/bin/bash
if ! command -v brew &> /dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
```

**Good for:** Installing package managers or tools that the rest of your setup depends on. Runs before files are written, and only once.

---

### `run_once_after_something.sh` — runs once, after files

```bash
# run_once_after_configure-git-credential-helper.sh
#!/bin/bash
git credential-manager configure
```

**Good for:** One-time configuration that depends on dotfiles already being in place.

---

### `run_onchange_something.sh` — runs when script content changes, during file operations

This is the clever one. Chezmoi hashes the script contents. If the hash matches last time, it skips it. If you edit the script (or a template variable it uses changes), it runs again. Without `before_` or `after_`, it runs interleaved with file operations.

```bash
# run_onchange_after_brew-bundle.sh.tmpl
#!/bin/bash
# Brewfile hash: {{ include "dot_Brewfile" | sha256sum }}
brew bundle --file=~/.Brewfile
```

**Good for:** Package installation. The `{{ include ... | sha256sum }}` trick in the comment means the script re-runs whenever your Brewfile changes, even though the actual `brew bundle` command hasn't changed. The hash comment changes → chezmoi sees new content → re-runs.

This is almost certainly what your `brew-bundle.sh` does.

> **`run_onchange_` without the hash trick:** You don't always need the hash trick. If the script body itself *is* the changing content, `run_onchange_` works naturally. For example, a script that lists packages to install — when you add a new package to the script, the content changes, so chezmoi re-runs it:
>
> ```bash
> # run_onchange_install-apt-packages.sh
> #!/bin/bash
> sudo apt install -y \
>   git \
>   curl \
>   ripgrep \
>   fd-find \
>   jq
> ```
>
> Add `bat` to the list → the script content changes → chezmoi re-runs it on next apply. No hash trick needed because the script *is* the manifest.

---

### `run_onchange_before_something.sh` — runs when changed, before files

```bash
# run_onchange_before_install-apt-packages.sh.tmpl
#!/bin/bash
# packages hash: {{ include "dot_config/packages.txt" | sha256sum }}
sudo apt update
xargs -a ~/.config/packages.txt sudo apt install -y
```

**Good for:** Installing system packages that config files might depend on.

---

### `run_onchange_after_something.sh` — runs when changed, after files

```bash
# run_onchange_after_reload-tmux.sh.tmpl
#!/bin/bash
# tmux config hash: {{ include "dot_tmux.conf" | sha256sum }}
tmux source-file ~/.tmux.conf 2>/dev/null || true
```

**Good for:** Reloading a service only when its config file actually changed.

---

## The `.tmpl` suffix

Any run script can also be a template by adding `.tmpl`:

```
run_onchange_after_brew-bundle.sh.tmpl
```

This means chezmoi renders Go template expressions (`{{ ... }}`) before executing. This is essential for:

- The `sha256sum` hash trick (triggering `onchange` based on another file)
- OS-conditional logic (`{{ if eq .chezmoi.os "darwin" }}`)
- Skipping the script entirely on certain machines

> **The hash trick requires `.tmpl`.** Without the `.tmpl` suffix, chezmoi does not render `{{ }}` expressions — they stay as literal text. This means `{{ include "dot_Brewfile" | sha256sum }}` would never change, and `run_onchange_` would never re-trigger. If you're using the hash trick, you **must** have the `.tmpl` suffix.

---

## How ordering actually works

Within the same phase (before/during/after), scripts run in **alphabetical order** by filename. Some people use numeric prefixes to control order:

```
run_once_before_01-install-homebrew.sh
run_once_before_02-install-packages.sh
run_once_before_03-setup-rbw.sh
```

The full execution order during `chezmoi apply`:

1. All `run_*_before_*` scripts (alphabetical)
2. All file/directory create/update/delete operations
3. All `run_*_after_*` scripts (alphabetical)
4. Scripts without `before_` or `after_` run interleaved with file operations (as explained above)

---

## Quick decision guide

| I want to... | Use |
|---|---|
| Install something once on new machines | `run_once_before_` |
| Run `brew bundle` when Brewfile changes | `run_onchange_after_` with hash trick |
| Reload a service when its config changes | `run_onchange_after_` with hash trick |
| Create directories before files are written | `run_before_` |
| Run a setup step that depends on dotfiles existing | `run_once_after_` |
| Do something every single apply (think twice) | `run_` or `run_after_` |

---

## Gotcha: `run_once` tracks by script name

If you rename a `run_once_` script, chezmoi treats it as a new script and runs it again. The tracking is by filename, not content. You can see what's been tracked with:

```bash
chezmoi state dump
```

And reset a specific script to make it run again with:

```bash
chezmoi state delete-bucket --bucket=scriptState
```

---

## Footnote: scripts don't have to be bash

Run scripts work with any language. Chezmoi uses the file extension to pick the interpreter:

```
run_once_setup.py     → runs with python3
run_once_setup.rb     → runs with ruby
run_after_check.pl    → runs with perl
```

You can also use a shebang line as usual:

```python
#!/usr/bin/env python3
import subprocess
subprocess.run(["defaults", "write", "com.apple.dock", "autohide", "-bool", "true"])
```

In practice, bash covers nearly everything. But if you have a complex setup step that's easier in Python (parsing JSON, making API calls, etc.), it's there.

---

## Related

- [Hooks cheat sheet](chezmoi-hooks-cheatsheet.md) — for when you need something to run *before* chezmoi reads source state (e.g., installing a password manager so templates can call it)
- [macOS Preferences cheat sheet](chezmoi-macos-preferences-cheatsheet.md) — the main use case for `run_onchange_after_` scripts with templates
- [Templates cheat sheet](chezmoi-templates-cheatsheet.md) — template syntax used in `.tmpl` run scripts
