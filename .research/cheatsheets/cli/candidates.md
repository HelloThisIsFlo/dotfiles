# Candidates to Explore

Tools not yet installed but worth seriously evaluating. Each one directly improves or replaces something already in the Brewfile.

---

## television — fuzzy finder with channels

**Replaces/complements:** fzf (partially) | `brew install television` | Binary: `tv`

The pitch: fzf requires you to pipe data in and wire up previews yourself. television ships with 80+ pre-configured "channels" — each a TOML file defining a data source, preview, and actions. No shell glue needed.

### Shell integration

```bash
# Add to config.fish (replaces fzf's Ctrl+R and Ctrl+T)
tv init fish | source
```

Provides **Ctrl+T** (smart autocomplete) and **Ctrl+R** (history search) — same keybinds as fzf.

### Usage

```bash
tv                       # default: file search
tv text                  # search file contents (ripgrep + fuzzy)
tv git-log               # browse git log interactively
tv git-repos             # find git repos across your machine
tv env                   # search environment variables
tv docker-containers     # list/manage docker containers
tv fish-history          # search shell history
tv brew-packages         # browse installed brew packages
tv just-recipes          # pick a just recipe to run
tv channels              # meta-channel: pick which channel to launch
```

### The old way vs television

```bash
# fzf: wire up a git log browser yourself
git log --oneline | fzf --preview 'git show {1}'

# tv: built-in channel, preview included
tv git-log

# fzf: custom file search with bat preview
fd -t f | fzf --preview 'bat --color=always {}'

# tv: just works
tv
```

### Custom channels

Create `~/.config/television/cable/my-projects.toml`:

```toml
[[cable_channel]]
name = "my-projects"
source_command = "fd -t d -d 1 . ~/projects"
preview_command = "eza --tree --level=2 --icons {0}"
```

Then: `tv my-projects`

### vs fzf — honest assessment

- **television wins:** Out-of-the-box experience. 80+ channels means you get git, docker, k8s, env, history, brew, etc. without writing any shell. Custom channels are trivial TOML files.
- **fzf wins:** Ecosystem depth. Every tool has fzf integration (vim, tmux, shell completions). Battle-tested since 2013. More flexible for ad-hoc piping.
- **Coexistence:** They can run side-by-side with different keybinds. Use tv for structured searches (git, docker, env), fzf for ad-hoc pipes and vim integration.
- **Caveat:** Younger project (~5k stars vs fzf's 68k). Shell integrations aren't as deep yet. The `tv` binary name conflicts with `tidy-viewer`.

---

## atuin — shell history, reinvented

**Replaces:** ctrl+r / built-in shell history | `brew install atuin`

The pitch: Your shell history is a flat text file with no context. atuin stores every command in SQLite with metadata — exit code, duration, working directory, hostname, session — then gives you a full-screen interactive search TUI. Optional encrypted sync across machines.

### Shell integration

```bash
# Add to config.fish
atuin init fish | source

# Import your existing history first
atuin import auto
```

Rebinds **Ctrl+R** and **Up arrow** to atuin's interactive search.

### Usage

```bash
# Interactive search (replaces Ctrl+R)
# Just press Ctrl+R — full-screen TUI with fuzzy search
# Filter by: current directory, session, host, exit code

# CLI commands
atuin search "docker"              # search history for "docker"
atuin history list                 # recent history with metadata
atuin history list --cwd           # only commands run in current directory
atuin stats                        # command usage statistics
```

### The old way vs atuin

```bash
# Old: ctrl+r, type fragment, ctrl+r again to cycle... hope you find it
# Also: history is per-session, lost on crash, no context

# Atuin: full-screen search with context
# - See exit code (did this command succeed last time?)
# - See duration (how long did it take?)
# - Filter by directory (what did I run HERE?)
# - Search across all machines (if sync enabled)
```

### Sync (optional)

```bash
atuin register -u <username> -e <email>   # create account
atuin login -u <username>                  # authenticate
atuin sync                                 # push/pull history

# Or self-host the sync server:
# docker run -d ghcr.io/atuinsh/atuin:latest server start
```

All data is encrypted client-side before sync. The server never sees plaintext commands.

### vs built-in history — honest assessment

- **atuin wins:** Context is the killer feature. "What did I run in this directory last week that succeeded?" is unanswerable with plain history. The interactive TUI is dramatically better than ctrl+r cycling. Sync across machines is genuinely useful.
- **Built-in wins:** Zero setup, zero dependencies, zero risk. Works everywhere, even on servers you SSH into for 5 minutes.
- **Caveat:** Another thing rebinding Ctrl+R (alongside fzf/television). Need to decide which tool owns that keybind. SQLite database grows over time (~50MB for heavy users after a year).
- **Privacy consideration:** Even with encryption, syncing shell history to a third-party server requires trust. Self-hosting is straightforward if that matters.

---

## mise — polyglot version manager — INTEGRATED (April 2026)

> **Decided.** mise replaced asdf. Keeping the full writeup here as a reference for why and how.

**Replaces:** asdf (+ partially direnv) | `brew install mise`

mise is a drop-in replacement for asdf, written in Rust. It reads `.tool-versions` files, uses asdf plugins, but runs 10x faster and adds built-in environment variables and a task runner. One tool instead of asdf + direnv + Make.

### Shell integration

```bash
# conf.d/12__mise.fish
mise activate fish | source
```

### Usage

```bash
mise use node@20                    # project-local (.mise.toml)
mise use --global node@20           # global default
mise use node@20 python@3.12        # multiple tools at once
mise exec node@22 -- node -v        # run with specific version without installing globally
mise ls                             # all tools and versions
mise install                        # install everything from config
```

### Environment variables (replaces direnv for simple cases)

```toml
# mise.toml
[env]
DATABASE_URL = "postgres://localhost/mydb"
NODE_ENV = "development"
AWS_PROFILE = "dev"

[tools]
node = "20"
python = "3.12"
```

Environment is activated when you `cd` into the directory — same as direnv, but declared alongside your tool versions.

### Task runner (replaces Make/just for simple cases)

```toml
[tasks.build]
description = "Build the project"
run = "npm run build"

[tasks.test]
description = "Run tests"
run = "npm test"
depends = ["build"]

[tasks.dev]
description = "Start dev server"
run = "npm run dev"
```

```bash
mise run test          # runs build first (dependency), then test
mise run dev           # start dev server
mise tasks             # list available tasks
```

### vs asdf — why we switched

- **Speed:** 5-10ms vs asdf's ~120ms per command invocation
- **UX:** `mise use` vs asdf's three-step plugin-add/install/local dance
- **Fewer tools:** Built-in env vars and tasks mean you don't need direnv + Make for simple cases
- **Zero migration:** Reads `.tool-versions` natively, same plugin ecosystem
- **No PATH hacks:** `mise activate` manages PATH dynamically — no shim fights with Homebrew

### vs direnv

mise handles simple `KEY=VALUE` env vars. For complex cases (sourcing files, conditional logic, `layout python`), direnv is still more powerful. They can coexist — mise for tool versions + simple env, direnv for complex env logic.

### vs just

mise's task runner is basic — fine for `run = "npm test"`. For anything with arguments, dependencies, recipes, conditionals — just is significantly more capable. They coexist well.

---

## zellij — terminal multiplexer

**Replaces:** tmux | `brew install zellij`

The pitch: tmux is powerful but hostile to newcomers — every keybind must be memorised or looked up. zellij shows available keybinds in the status bar, has floating panes, auto-layout, and WebAssembly plugins. Written in Rust.

### Quick start

```bash
zellij                          # start a new session
zellij -s myproject             # named session
zellij attach myproject         # reattach
zellij list-sessions            # list active sessions
```

### Key navigation

zellij uses a **modal** system — press a leader key to enter a mode, then press the action key:

```
Ctrl+p  →  Pane mode
            n  new pane (auto-placed)
            d  down, u  up, l  right, h  left (navigate)
            f  toggle floating pane
            x  close pane

Ctrl+t  →  Tab mode (like tmux windows)
            n  new tab
            1-9  switch to tab
            r  rename tab

Ctrl+n  →  Resize mode
            h/j/k/l  resize in direction

Ctrl+s  →  Scroll mode (like tmux copy mode)
            j/k  scroll, /  search

Ctrl+o  →  Session mode
            d  detach
            w  session manager
```

The status bar shows all available keys in the current mode — no memorisation needed.

### The old way vs zellij

```bash
# tmux: split pane vertically
Ctrl+b %

# zellij: enter pane mode, new pane
Ctrl+p n    # zellij auto-places it intelligently

# tmux: floating pane? Not built in. Need popup (tmux 3.2+)
# zellij: toggle floating pane
Ctrl+p f

# tmux: what keybinds are available again?
# ...check .tmux.conf or tmux list-keys
# zellij: look at the status bar — it's right there
```

### Layouts

Define reusable workspace layouts in `~/.config/zellij/layouts/`:

```kdl
// dev.kdl
layout {
    pane split_direction="vertical" {
        pane command="nvim"       // editor on the left
        pane split_direction="horizontal" {
            pane command="cargo" args=["watch", "-x", "test"]   // tests top-right
            pane                                                 // shell bottom-right
        }
    }
}
```

```bash
zellij --layout dev     # launch with layout
```

### vs tmux — honest assessment

- **zellij wins:** Discoverability (status bar keybinds). Floating panes are first-class. Auto-layout is smart. WebAssembly plugin system is genuinely novel. Configuration is YAML/KDL instead of tmux's arcane syntax.
- **tmux wins:** Ecosystem. 17 years of plugins, integrations, muscle memory, and Stack Overflow answers. Every remote server has tmux. `tpm` plugin manager is mature. If you SSH into servers regularly, tmux is already there — zellij isn't.
- **Migration path:** zellij has a `tmux` keybind mode (`Ctrl+b` prefix) to ease the transition.
- **Caveat:** Not available on most servers via package managers (you'd need to install it). If you split time between local dev and remote servers, maintaining two multiplexer configs is friction. The modal system (press leader, then action) is an extra keypress vs tmux's prefix+key.
- **Coexistence:** Use zellij locally for its UX, tmux on remote servers. Or just stick with tmux everywhere for consistency — that's a valid choice.
