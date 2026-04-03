# CLI Exploration Tracker

Parallel track to the Mackup → chezmoi migration. Evaluating, learning, and integrating modern CLI tools for an upgraded terminal experience.

> **This is not migration work.** Migration lives in `MIGRATION.md`. Reference material for individual tools lives in `cheatsheets/cli/`.

---

## To Explore

### Fuzzy finding & search
- **fzf (deep dive)** — Installed via fzf.fish, but only using defaults. Want to explore: custom keybindings, writing fzf-powered fish functions, integrating with other tools (git, docker, aws)
- **television** — Fuzzy finder with 80+ pre-built channels (git-log, docker-containers, brew-packages, etc.). Complement to fzf — no shell glue needed. [GitHub](https://github.com/alexpasmantier/television)
- **navi** — Interactive cheatsheet & snippet manager. Added to Brewfile, not yet configured for fish. [GitHub](https://github.com/denisidoro/navi)

### Navigation & file management
- **zoxide** — cd replacement, learns frecency. Installed but not configured (22__zoxide.fish is a placeholder). Need to run `zoxide init fish | source`
- **yazi** — Terminal file manager. Installed but not configured. Integrates with bat, fd, rg
- **broot** — Interactive tree explorer with fuzzy search. Not installed

### Editor
- **neovim + LazyVim** — Already set up, want to go deeper

### Terminal multiplexer
- **tmux vs zellij** — Evaluate whether to switch. tmux is current (with iTerm2 integration), zellij has discoverable keybinds and floating panes

### Version management
- ~~**mise**~~ — moved to Integrated (see below)

### Text & data processing
- **sd** — Intuitive sed replacement, sane regex syntax. Not installed
- **difftastic** — Structural/syntax-aware diffs. Not installed
- **grex** — Generate regex from examples. Not installed
- **xh** — curl with better UX for API work. Not installed

### System monitoring & diagnostics
- **btop** — System monitor TUI. Installed, not actively explored
- **viddy** — Modern watch with diff highlighting and history. Installed, not explored
- **hyperfine** — Statistical benchmarking. Installed, not explored
- **dust** — Visual disk usage (du replacement). Not installed
- **duf** — Modern df. Not installed
- **procs** — Colorized ps with keyword search. Not installed
- **bandwhich** — Per-process network bandwidth. Not installed
- **gping** — Ping with real-time graph. Not installed

### Git
- **lazygit** — Git TUI for staging, interactive rebase, etc. Installed, not explored

### Shell & data
- **nushell** — Structured data pipelines. Installed, worth exploring for data wrangling
- **choose** — Human-friendly cut/awk column selection. Not installed
- **tokei** — Fast code statistics. Not installed

### Muscle memory
- **ripgrep/rg** — Installed, need to build the habit of reaching for it instead of grep

### Configuration
- **bat** — Using for years (MANPAGER, fzf previews), but could configure themes/options better

---

## Integrated (done exploring, decision made)

### Fish plugins
- **fish-aws** (remmercier/fish-aws) — AWS profile/region switching via `asp`/`asr`. Decided 2026-04-01. Config: `25__aws.fish`
- **fish-git-abbr** (lewisacidic/fish-git-abbr) — Git abbreviations. Decided 2026-03-31. Preferred over migrating zsh git aliases
- **fzf.fish** (PatrickF1/fzf.fish) — fzf integration for fish. Basic config done

### CLI tools (fully set up)
- **mise** — Polyglot version manager, replaced asdf. Config: `12__mise.fish` (activation pending), global tools in `~/.config/mise/config.toml`. Decided 2026-04-03
- **eza** — ls replacement. Configured in `51__eza.fish` with curated aliases
- **git-delta** — Diff pager. Configured in `.gitconfig`
- **fish** — Daily shell, conf.d fully organized
- **just** — Task runner, used in projects
- **jq** — JSON processing, long-time user
