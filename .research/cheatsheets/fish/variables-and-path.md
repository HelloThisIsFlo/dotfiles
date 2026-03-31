# Fish Variables and PATH — Cheat Sheet

Fish has four variable scopes, and picking the wrong one is the #1 cause of "it works in my terminal but not after restart" or the reverse — "I deleted that variable but it keeps coming back." This sheet explains which scope to use, why universal variables are a trap, and how to manage PATH entries correctly with `fish_add_path`.

---

## Scopes

Every `set` call targets a scope. Get this wrong and your variable either vanishes on restart or haunts you forever.

### The four scopes

| Flag | Scope | Lifetime | Visible to child processes? |
|------|-------|----------|----------------------------|
| `-l` | Local | Current block/function | No |
| `-g` | Global | Current session | No |
| `-gx` | Global exported | Current session | Yes |
| `-U` | Universal | Forever (survives restarts) | No |
| `-Ux` | Universal exported | Forever + exported | Yes |

### Decision tree

1. Need it in child processes (compilers, scripts, `$EDITOR`)? You need `-x` (export).
2. Need it to persist across sessions? Use `conf.d/` files with `-gx`, NOT `-U`. See below.
3. Scoping within a function? `-l` (local) — the default when no flag is given.
4. Temporary session override? `-g` or `-gx`.

```bash
# Local — dies when the function exits
function greet
    set -l name "Flo"
    echo "Hello, $name"
end

# Global exported — lives for this session, visible to subprocesses
set -gx EDITOR vim

# Universal — DON'T DO THIS (explained below)
set -Ux GOPATH $HOME/.go  # seems convenient, is actually a trap
```

> **Gotcha:** With no flag at all, `set` defaults to `-l` inside functions and `-g` at the top level. Always be explicit.

---

## Universal variables are an anti-pattern

This is the most important thing in this sheet. Universal variables (`-U`, `-Ux`) seem great — set once, persist forever. In practice they cause subtle, maddening bugs.

### Why they break things

- Stored in `~/.config/fish/fish_variables`, a binary-ish file that is NOT in version control
- Silently override anything set in `conf.d/` files — universals win over globals
- Cannot be reproduced on another machine without manually re-running every `set -U` command
- Invisible: `set -U EDITOR vim` leaves no trace in your config files. Six months later you have no idea why `$EDITOR` is `vim` when your `conf.d/` says `nvim`.
- Shared across all running sessions in real-time — change it in one terminal, it changes everywhere instantly (sounds cool, causes chaos)

### The right way

Set everything in `conf.d/` files with `-gx`:

```bash
# ~/.config/fish/conf.d/02__shell-env.fish
set -gx EDITOR vim
set -gx LC_ALL en_US.UTF-8
set -gx LANG en_US.UTF-8
```

This is explicit, version-controlled, reproducible, and runs on every shell startup. The "cost" of running on every startup is negligible — these are instant operations.

### Cleaning up accidental universals

```bash
# List all universal variables
set -U

# Nuke a specific one
set -eU EDITOR
set -eU GOPATH

# Nuclear option — erase ALL universals (careful)
for var in (set -Un)
    set -eU $var
end
```

> **Gotcha:** If you have both `set -Ux EDITOR vim` (universal) and `set -gx EDITOR nvim` in conf.d, the universal wins. You'll edit your conf.d, restart fish, and nothing changes. Run `set -eU EDITOR` first.

> **Gotcha:** `fish_add_path` without `--global` defaults to universal scope. Always pass `--global`.

---

## Environment variables

Every `export FOO=bar` from zsh/bash translates to `set -gx FOO bar` in a `conf.d/` file. No quoting surprises, no `${}` expansion — fish variables are lists, not strings.

### Direct translations from zsh

| zsh (`~/.zshrc`) | fish (`conf.d/` file) |
|---|---|
| `export LC_ALL=en_US.UTF-8` | `set -gx LC_ALL en_US.UTF-8` |
| `export LANG=en_US.UTF-8` | `set -gx LANG en_US.UTF-8` |
| `export EDITOR=vim` | `set -gx EDITOR vim` |
| `export GOPATH="$HOME/.go"` | `set -gx GOPATH $HOME/.go` |
| `export PYTHONSTARTUP=~/.pythonrc` | `set -gx PYTHONSTARTUP ~/.pythonrc` |
| `export PIPENV_SHELL_FANCY=1` | `set -gx PIPENV_SHELL_FANCY 1` |
| `export AWS_PROFILE=flokempenich-admin--not-root` | `set -gx AWS_PROFILE flokempenich-admin--not-root` |
| `export HASS_SERVER="http://thehome-haos.neko-hoki.ts.net:8123"` | `set -gx HASS_SERVER "http://thehome-haos.neko-hoki.ts.net:8123"` |
| `export QMK_HOME=~/Work/Private/Dev/Keyboards/The-QMK-Config` | `set -gx QMK_HOME ~/Work/Private/Dev/Keyboards/The-QMK-Config` |

### Organized into conf.d files

```bash
# conf.d/02__shell-env.fish — base environment
set -gx LC_ALL en_US.UTF-8
set -gx LANG en_US.UTF-8
set -gx EDITOR vim
if test "$TERM_PROGRAM" != ghostty
    set -gx TERM xterm-256color
    set -gx COLORTERM truecolor
end
if command -q bat
    set -gx MANPAGER "sh -c 'col -bx | bat -l man -p'"
end

# conf.d/23__python.fish
set -gx PYTHONSTARTUP ~/.pythonrc
set -gx PIPENV_SHELL_FANCY 1

# conf.d/24__go.fish
set -gx GOPATH $HOME/.go
```

> **Gotcha:** Fish does not expand `~` inside quotes. `set -gx FOO "~/something"` sets FOO to the literal string `~/something`. Either drop the quotes (`set -gx FOO ~/something`) or use `$HOME`.

---

## fish_add_path

This is the right way to manage PATH in fish. It is idempotent — adding the same path twice is a no-op. It checks that the directory exists before adding.

### Flags that matter

| Flag | What it does | When to use |
|------|-------------|-------------|
| `--global` | Store in global scope (session) | Always. Without this, defaults to universal scope. |
| `--move` | If path already exists, move it to front | When ordering matters (homebrew, asdf shims) |
| `--path` | Add to end of PATH instead of beginning | Low-priority paths that should not override system tools |
| `--prepend` | Add to beginning of PATH (the default) | High-priority paths — default behavior, rarely spelled out |
| `--append` | Same as `--path` | Alias for `--path` |

### The critical flags: `--global` and `--move`

```bash
# WRONG — saves to universal variables, haunts you forever
fish_add_path $HOME/.bin

# RIGHT — session-scoped, reproducible via conf.d
fish_add_path --global --path $HOME/.bin

# RIGHT — prepend AND reorder if already present
fish_add_path --global --move $HOME/.local/bin
```

`--move` matters when multiple conf.d files or plugins might add the same path. Without `--move`, the path stays wherever it was first inserted. With `--move`, it jumps to the front (or back with `--path`) regardless of existing position.

---

## PATH ordering

PATH order determines which binary wins when the same name exists in multiple locations. In fish with conf.d, the numbered file prefix controls execution order, which controls PATH order.

### The numbering scheme

```
conf.d/
  02__shell-env.fish        # base env vars (no PATH)
  13__asdf.fish             # asdf shims — needs to be early + --move
  23__python.fish           # python env vars (no PATH)
  24__go.fish               # go env vars (no PATH)
  81__core-paths.fish       # ~/.local/bin, ~/.bin — highest priority
  82__language-paths.fish   # go, krew, rust — after core
  83__app-paths.fish        # GUI app CLIs — lowest priority
```

### How the actual files work

```bash
# 13__asdf.fish — must win over system binaries
set -gx ASDF_DATA_DIR "$HOME/.asdf"
fish_add_path --global --move --path $ASDF_DATA_DIR/shims
```

asdf uses `--move` because plugins and other conf.d files might also add shim paths. `--move` guarantees asdf shims land where you want them regardless of load order.

```bash
# 81__core-paths.fish — personal scripts override everything
fish_add_path --global --move --path $HOME/.local/bin
fish_add_path --global --move --path $HOME/.bin
```

Core paths use `--move` for the same reason — these are your personal overrides and should always win.

```bash
# 82__language-paths.fish — language toolchains
fish_add_path --global --path $GOPATH/bin
fish_add_path --global --path $HOME/.krew/bin
fish_add_path --global --path $ASDF_DATA_DIR/installs/rust/stable/bin
```

Language paths use `--path` (append) without `--move` — they don't need to override system tools, just be available.

```bash
# 83__app-paths.fish — GUI app command-line interfaces
fish_add_path --global --path $HOME/.lmstudio/bin
fish_add_path --global --path /Applications/Obsidian.app/Contents/MacOS
fish_add_path --global --path "/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
fish_add_path --global --path $HOME/.codeium/windsurf/bin
```

App paths are lowest priority — you want `code` to resolve to VS Code, but never to shadow a real binary.

### Resulting PATH priority (highest to lowest)

1. `~/.local/bin`, `~/.bin` (core, `--move`)
2. asdf shims (toolchain manager, `--move`)
3. System paths (from `/etc/paths`, `/etc/paths.d/`)
4. `$GOPATH/bin`, `~/.krew/bin`, rust stable (language tools, `--path`)
5. App bundles like Obsidian, VS Code, LM Studio (GUI CLIs, `--path`)

### Translating zsh PATH manipulation

| zsh pattern | fish equivalent |
|---|---|
| `export PATH="$HOME/.bin:$PATH"` (prepend) | `fish_add_path --global --move $HOME/.bin` |
| `export PATH="$PATH:$HOME/.bin"` (append) | `fish_add_path --global --path $HOME/.bin` |
| `export PATH="${ASDF_DATA_DIR}/shims:$PATH"` (prepend) | `fish_add_path --global --move $ASDF_DATA_DIR/shims` |
| `export PATH="$PATH:${GOPATH}/bin"` (append) | `fish_add_path --global --path $GOPATH/bin` |

> **Gotcha:** `fish_add_path` silently skips directories that don't exist. If `$GOPATH/bin` hasn't been created yet, it won't appear in PATH. This is usually what you want, but can be confusing when debugging.

> **Gotcha:** The zsh `${GOPATH//://bin:}/bin` trick (replace colons) is unnecessary in fish. `$GOPATH` is a single string, not a colon-separated list. Just use `$GOPATH/bin`.

---

## Erasing variables

```bash
# Erase from current session (global scope)
set -eg EDITOR

# Erase a universal (the one that haunts you)
set -eU EDITOR

# Erase a local
set -el my_var

# Erase an exported global
set -egx EDITOR

# Check if a variable exists before erasing
set -q EDITOR; and set -eg EDITOR
```

### Common cleanup tasks

```bash
# Find universals that shadow your conf.d settings
# (run this, then check each one against your conf.d files)
set -Un

# Remove a path from PATH
set PATH (string match -v "$HOME/.old-thing/bin" $PATH)

# Remove all fish_add_path universals (reset PATH to system default)
set -eU fish_user_paths
```

> **Gotcha:** `set -e PATH` erases your entire PATH. Don't do that. To remove a single entry, filter it out with `string match -v`.

---

## Quick reference

| Task | Command |
|------|---------|
| Set env var for session | `set -gx VAR value` |
| Set env var permanently | `set -gx VAR value` in a `conf.d/` file |
| Add to front of PATH | `fish_add_path --global --move /path` |
| Add to end of PATH | `fish_add_path --global --path /path` |
| Remove a PATH entry | `set PATH (string match -v /path $PATH)` |
| Erase a universal | `set -eU VAR` |
| List all universals | `set -U` |
| List universal names only | `set -Un` |
| Check if var exists | `set -q VAR` |
| Show current PATH | `echo $PATH` (one per line) or `string join \n $PATH` |
| Debug: where is a var set? | `set -S VAR` (shows scope and value) |
| Inspect PATH ordering | `printf '%s\n' $PATH` |

---

## See also

- [Config structure](../fish/config-structure.md) — where to place conf.d files and how numbering works
- [Syntax rosetta](../fish/syntax-rosetta.md) — variable expansion and quoting differences from bash/zsh
