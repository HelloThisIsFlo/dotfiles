# Zsh → Fish Migration

Tracking the port from zsh (oh-my-zsh + antigen + custom functions) to fish. Source of truth for what's been migrated and what remains.

Reference: `private_dot_zshrc` (the original zsh config, still in the repo).

## Done

### Shell fundamentals
- [x] Vi mode + word-deletion keybindings (`01__keybinds-and-vi-mode.fish`)
- [x] Ctrl-A / Ctrl-E line navigation in insert mode
- [x] Greeting disabled
- [x] Locale (`LC_ALL`, `LANG`)
- [x] Editor (`EDITOR=nvim`)
- [x] TERM fallback (Ghostty-aware)
- [x] Colored man pages via bat (`MANPAGER`)

### Package managers & version managers
- [x] Homebrew (`11__homebrew.fish`)
- [x] ~~asdf shims (`13__asdf.fish`)~~ — removed, replaced by mise (`12__mise.fish`)

### Tool integrations
- [x] direnv (`21__direnv.fish`) — **want to replace with mise** (only using direnv for `.env` loading, not `.envrc`)
- [x] zoxide (`22__zoxide.fish`) — replaces oh-my-zsh `z` plugin
- [x] fzf.fish (`27__fzf.fish`) — eza previews, delta diffs, hidden files, history timestamps
- [x] Python env vars (`23__python.fish`) — `PYTHONSTARTUP`, `PIPENV_SHELL_FANCY`
- [x] Go env vars (`24__go.fish`) — `GOPATH`
- [x] AWS (`25__aws.fish`) — profile + fish-aws plugin

### PATH
- [x] Core paths (`81__core-paths.fish`) — `~/.local/bin`, `~/.bin`
  - ⚠️ Missing from zshrc: `$HOME/Dev/Scripts` (still have scripts there?), `/usr/local/sbin` (likely not needed on Apple Silicon)
- [ ] Language paths (`82__language-paths.fish`) — review: Go and krew paths may no longer be needed
  - Rust PATH removed (mise handles this via `mise activate`)
  - ⚠️ `$GOPATH/bin` and `$HOME/.krew/bin` — still relevant? Review before re-checking
- [x] App paths (`83__app-paths.fish`) — LM Studio, Obsidian, VS Code, Windsurf
  - Garmin SDK & Android platform-tools from zshrc not ported (likely stale)

### Aliases, functions, abbreviations
- [x] Core (`41__core.fish`) — vi/vim→nvim, mkcd, x, vix, rm/cp/ln/mkdir defaults, clipboard
- [x] Git (`42__git.fish`) — comprehensive abbreviation set + helper functions
- [x] Docker (`42__docker.fish` + `44__docker.fish`) — abbreviations + compose + utilities
- [x] Kubernetes (`42__k8s.fish`)
- [x] Terraform (`42__terraform.fish`)
- [x] Chezmoi (`43__chezmoi.fish`) — abbreviations + `cmfish`
- [x] Claude Code (`45__claude.fish`)
- [x] Network (`46__network.fish`) — local-ip, nmap scan, ports, termbin
- [x] System (`48__system-utilities.fish`) — updateall
- [x] Misc utilities (`50__utilities.fish`) — serve-current-dir, pdf2blue
- [x] eza (`51__eza.fish`) — replaces custom tree aliases
- [x] Docker droplets (`52__droplets.fish`)
- [x] transfer.sh (`53__transfer-sh.fish`)
- [x] TADL (`54__tadl.fish`)

### Plugins (Fisher)
- [x] Fisher (plugin manager)
- [x] Tide (prompt — replaces custom zsh theme)
- [x] Sponge (clean failed commands from history)
- [x] fzf.fish (replaces fzf-tab + fzf-tab-source)
- [x] fish-aws (AWS profile/region switching)
- [x] puffer-fish (replaces bang-bang: `!!`, `!$`, `...` expansion)

### Oh-my-zsh plugins → fish equivalents
- [x] `zsh-syntax-highlighting` → built into fish
- [x] `zsh-autosuggestions` → built into fish
- [x] `history-substring-search` → built into fish (type + ↑)
- [x] `vi-mode` → built into fish (`fish_vi_key_bindings`)
- [x] `zsh-completions` → built into fish (man page parsing)
- [x] `git` → hand-managed abbreviations (`42__git.fish`)
- [x] `kubectl` → hand-managed abbreviations (`42__k8s.fish`)
- [x] `z` → zoxide
- [x] `sudo` (Esc×2) → puffer-fish `!!` covers the main use case
- [x] `brew` → abbreviations as needed
- [x] ~~`asdf`~~ → replaced by mise


## Remaining

### Placeholders to fill
- [ ] **Secrets** (`03__secrets.fish`) — decide: `bass source ~/.secrets.env` or fish-native `~/.secrets.fish`
- [ ] **Home Assistant** (`26__home-assistant.fish`) — `HASS_SERVER`, `HASS_TOKEN` (depends on secrets)
- [ ] **tmux** (`49__tmux.fish`) — `ta`, `ts`, `td`, `tl`, `tk` + session completions. Or drop if not using tmux anymore
- [ ] **mise** (`12__mise.fish`) — asdf removed, mise activation pending (using `mise activate fish | source`)

### Missing env vars
- [x] `HOMEBREW_BUNDLE_FILE=$HOME/.Brewfile` — added to `11__homebrew.fish`
- [ ] `ALTERNATE_EDITOR=""` (needed for emacsclient fallback — skip if not using emacs)

### Completions (`99__completions.fish`)
- [x] kubectl — already working (fish built-in or man page parsing)
- [ ] talosctl — verify if already working, add to `cache_completions` if not
- [ ] poetry
- [ ] AWS CLI (needs fish-specific completer, not just `cache_completions`)
- [ ] gita (python-argcomplete — investigate)

### Oh-my-zsh plugins not yet ported
- [ ] **`extract`** — universal archive extraction, used a lot. Find fish equivalent or port as function
- [ ] **`copybuffer`** (Ctrl+O) — copies the current *command line buffer* to clipboard. Investigate: is this the same as `fish_clipboard_copy`? (fish's version copies selected text, not the whole line — may need a custom keybinding)

### Linux compatibility
- [ ] **Linux wrappers** — single conf.d file (e.g. `47__linux-compat.fish`) with:
  - `bat`→`batcat`, `fd`→`fdfind` wrappers (Ubuntu names differ from Homebrew)
  - `pbcopy`/`pbpaste` aliases to `xclip -selection clipboard`
  - Guard with `if not test (uname) = Darwin` or similar

### Features to port
- [ ] **Scratch** — Obsidian scratch file quick-open (`scratch NAME` → opens `~/...Obsidian.../Scratch/NAME.md`, `scratch-list` to browse). Decide: keep MacVim or switch to nvim. Could also become a standalone fish function file
- [ ] **gitignore** (`gi`) — generates `.gitignore` from templates (was oh-my-zsh `gitignore` plugin, calls gitignore.io API). Find a fish-native CLI or write a function
- [ ] **watchandrun** — `fswatch FILE | xargs COMMAND` wrapper. Interesting utility, low priority

### Intentionally dropped from zsh
Not migrating — confirmed dead or irrelevant:
- Spacemacs (`e` function) — using nvim/Cursor
- MyFitnessPal CLI — unmaintained
- DnD (`dnd-on`/`dnd-off`) — broken on modern macOS
- Remarkable streaming — hardware-specific
- Clear Mind service — old project, hardcoded paths
- Serveo SSH tunnels
- `arm`/`intel` arch switch — launches zsh specifically
- `clitool-cat` (asdf shim inspector — asdf removed, no longer relevant)
- `singlechar` plugin env vars
- `OPENAI_ENGINE_ID=davinci` — ancient
- `QMK_HOME` — keyboard firmware
- `PIPENV_DEFAULT_PYTHON_VERSION` — referenced `$PYTHON3_VERSION` from secrets
- Java (`list-all-java-versions`, jenv PATH)
- Travis CI
- iTerm2 shell integration — using Ghostty
- Docker completion fpath hack — fish has built-in docker completions
- `encode64` plugin
- `urltools` plugin
- `perms` plugin
- `systemadmin` plugin
- `battery` plugin
- `httpie`/`mvn`/`pep8`/`yarn`/`yum` plugins (completion-only — fish parses man pages)
