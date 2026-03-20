# Fish Shell — Reversible Experiment Guide

Tailored to your current Zsh setup. Nothing here changes your default shell. To revert: just stop launching Fish.

---

## What You Get For Free (vs your current plugin setup)

| Feature | Your Zsh today | Fish |
|---|---|---|
| Syntax highlighting | `zsh-syntax-highlighting` plugin | Built-in |
| Autosuggestions | `zsh-autosuggestions` plugin | Built-in |
| Tab completions | `zsh-completions` + `fzf-tab` | Built-in (parses man pages automatically) |
| History substring search | `history-substring-search` plugin | Built-in (type + ↑) |
| Vi mode | `vi-mode` plugin | Built-in (`fish_vi_key_bindings`) |
| Sudo prefix (Esc Esc) | `sudo` plugin | Not built-in — but a simple keybinding to add |

Things you'll need to **actively set up** in Fish to match your current experience:
- `z` / directory jumping → install **zoxide** (better than the oh-my-zsh `z` plugin anyway, and works in both shells)
- fzf integration → **fzf.fish** plugin
- direnv → `direnv hook fish | source` (direnv supports Fish natively)
- asdf → Fish support is built into asdf
- Git aliases → Fish plugin or just redefine as **abbreviations** (Fish's killer feature for aliases)
- kubectl completions → `kubectl completion fish | source`
- chezmoi completions → `chezmoi completion fish | source`
- Your custom functions/aliases → need translating (the Claude Code job)

---

## Phase 1: Install (nothing changes)

```bash
# macOS
brew install fish

# Ubuntu/Debian
sudo apt install fish

# Verify
fish --version
```

Your default shell remains Zsh. Nothing changes. You just have a new binary available.

---

## Phase 2: Launch and Explore (zero config)

Just type:

```bash
fish
```

You're now in Fish. Your Zsh config is untouched, running in the background. Type `exit` to go back to Zsh at any time.

### Immediate things to try

**Autosuggestions** — start typing a command you've used before. Fish greys out the rest from history. Press `→` to accept, `Alt+→` to accept one word.

**Syntax highlighting** — type a valid command: it's one colour. Type gibberish: it turns red *before you press enter*.

**Tab completion** — type `git ` then press Tab. Fish shows rich completions with descriptions. Try `ls --` then Tab — it pulls flags from the man page.

**Vi mode** — run this to enable it for the session:

```fish
fish_vi_key_bindings
```

Press Esc, navigate with hjkl, the usual. `k` and `j` do history substring search in normal mode (like your current binding).

**Web config** — run this to see Fish's built-in configuration UI:

```fish
fish_config
```

Opens a browser. You can preview themes, change colours, and browse functions/variables. No dotfiles required.

---

## Phase 3: Minimal Config (still reversible)

Fish config lives in `~/.config/fish/`. Create a starter config:

```fish
# From inside Fish:
mkdir -p ~/.config/fish/functions
mkdir -p ~/.config/fish/conf.d
```

### config.fish (Fish's equivalent of .zshrc)

Create `~/.config/fish/config.fish`:

```fish
# Vi mode
fish_vi_key_bindings

# Locale
set -gx LC_ALL en_US.UTF-8
set -gx LANG en_US.UTF-8

# Editor
set -gx EDITOR vim
set -gx TERM xterm-256color

# Secrets
source ~/.secrets.fish  # You'll need a Fish version of this (just replace export with set -gx)

# AWS
set -gx AWS_PROFILE flokempenich-admin--not-root

# Go
set -gx GOPATH "$HOME/.go"

# Python
set -gx PYTHONSTARTUP ~/.pythonrc

# Homebrew
set -gx HOMEBREW_BUNDLE_FILE "$HOME/.Brewfile"

# PATH additions
fish_add_path /usr/local/sbin
fish_add_path $HOME/.bin
fish_add_path $HOME/.local/bin
fish_add_path $HOME/Dev/Scripts
fish_add_path (brew --prefix asdf 2>/dev/null)/shims  # or however asdf is set up
# Add others as needed — fish_add_path is idempotent and won't duplicate

# direnv
direnv hook fish | source

# asdf (if using the Fish-native integration)
# source (brew --prefix asdf)/libexec/asdf.fish
```

### Abbreviations (Fish's better aliases)

Abbreviations expand inline as you type — you see the full command before pressing enter. This is *much* better than aliases for learning and transparency.

Add to `config.fish` or run interactively (they persist automatically):

```fish
# Chezmoi
abbr -a cm chezmoi
abbr -a cms "chezmoi status"

# Git (a few starters — add what you actually use)
abbr -a g git
abbr -a ga "git add"
abbr -a gc "git commit"
abbr -a gco "git checkout"
abbr -a gst "git status"
abbr -a gd "git diff"

# Docker compose
abbr -a dcu "docker compose up"
abbr -a dcd "docker compose down"

# Tree
abbr -a t "tree -L 2 -I 'node_modules|lib' --noreport"
abbr -a t1 "tree -L 1 -I 'node_modules|lib' --noreport"
abbr -a t3 "tree -L 3 -I 'node_modules|lib' --noreport"

# Claude Code
abbr -a claude "claude --allow-dangerously-skip-permissions"
```



---


## Phase 4: Explore the Plugin Ecosystem

This is the interesting part — seeing what Fish's ecosystem gives you compared to your oh-my-zsh plugins.

### Install Fisher (plugin manager)

```fish
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
```

### Plugins to install and explore

```fish
# fzf integration — the big one to compare against fzf-tab
fisher install PatrickF1/fzf.fish

# Git aliases — closest equivalent to oh-my-zsh git plugin
# Gives you ga, gc, gco, gst, gd, gp, gl, etc.
fisher install jhillyerd/plugin-git

# !! and !$ support (last command / last argument)
fisher install oh-my-fish/plugin-bang-bang

# Esc Esc to prefix with sudo (like oh-my-zsh sudo plugin)
fisher install oh-my-fish/plugin-sudope

# bass — source bash scripts directly from Fish (see explanation below)
fisher install edc/bass

# Universal archive extraction (like oh-my-zsh extract plugin)
fisher install oh-my-fish/plugin-extract

# encode64 / decode64
fisher install oh-my-fish/plugin-encode
```

### Set up zoxide (replaces oh-my-zsh `z` plugin)

Zoxide is a strictly better `z` — uses frecency ranking and works across shells. Worth installing regardless of whether you stay on Fish.

```bash
# Install system-wide (from any shell)
brew install zoxide
```

```fish
# Then in Fish:
zoxide init fish | source
# Add this to config.fish if you keep Fish
```

### Completions that just work without plugins

Fish auto-generates completions by parsing man pages. Try tabbing through these — no plugin needed:

```fish
kubectl completion fish | source
chezmoi completion fish | source
talosctl completion fish | source
poetry completions fish | source
```

For `docker`, `git`, `brew`, `ssh`, `rsync`, and most standard tools — Fish already has completions built in. Just tab and see.

### What `bass` does

Bass bridges the gap between Fish and bash. It lets you run bash commands and captures their side effects (environment variable changes, PATH modifications) back into your Fish session.

The problem: your `.secrets.env` file uses `export VAR=value` — that's bash syntax. Fish doesn't understand `export`. Without bass, you'd need to maintain a separate Fish version of every bash-syntax file.

With bass:

```fish
bass source ~/.secrets.env
```

Bass spins up a hidden bash subshell, runs the command, diffs the environment before and after, and applies the changes to your Fish session. Any `export`, `eval`, `source`, or PATH manipulation from bash-land works transparently.

Also useful for things like:

```fish
bass "$(brew shellenv)"
bass eval '$(ssh-agent -s)'
```

Essentially it's the bridge that means you don't have to rewrite everything on day one.

### Mapping from your oh-my-zsh plugins

| Your oh-my-zsh plugin | Fish equivalent |
|---|---|
| `zsh-syntax-highlighting` | Built in — just works |
| `zsh-autosuggestions` | Built in — just works |
| `history-substring-search` | Built in — type then ↑/↓ |
| `vi-mode` | Built in — `fish_vi_key_bindings` |
| `zsh-completions` | Built in — man page parsing |
| `git` | `jhillyerd/plugin-git` via Fisher |
| `sudo` | `oh-my-fish/plugin-sudope` via Fisher |
| `z` | `zoxide` (better, and shell-agnostic) |
| `extract` | `oh-my-fish/plugin-extract` via Fisher |
| `encode64` | `oh-my-fish/plugin-encode` via Fisher |
| `kubectl` | `kubectl completion fish \| source` |
| `asdf` | Fish support built into asdf |
| `brew` | Define a few abbreviations (`bubu`, etc.) |
| `yarn` | Built-in Fish completions |
| `httpie`, `mvn`, `pep8` | Built-in Fish completions (man page parsing) |
| `fzf-tab` + `fzf-tab-source` | `PatrickF1/fzf.fish` — different UX, see below |
| `singlechar` | Use abbreviations instead |
| `battery` | No equivalent — `pmset -g batt` on macOS |
| `perms` | No equivalent — one-liners if you miss them |
| `systemadmin` | No equivalent — check if you actually use any of it |
| `gitignore` (`gi`) | No maintained equivalent — easy to write as a function |
| `urltools` | No maintained equivalent — python one-liners |
| `copybuffer` | Fish has `fish_clipboard_copy` built in |

### fzf.fish vs fzf-tab — what to expect

fzf-tab replaces the tab key with fzf. fzf.fish takes a different approach — dedicated keybindings:

| Keybinding | What it does |
|---|---|
| `Ctrl+R` | Search command history with fzf |
| `Ctrl+Alt+F` | Search files with fzf |
| `Ctrl+Alt+L` | Search git log with fzf |
| `Ctrl+Alt+S` | Search git status with fzf |
| `Ctrl+Alt+P` | Search processes with fzf |

Tab completion in Fish remains Fish's native system (which is already quite rich). fzf is layered on top for specific search workflows rather than replacing the completion system entirely.

Spend 15 minutes with it and see how the flow compares.

### Quick experiment session (copy-paste this)

```fish
fish

# Install Fisher
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher

# Install plugins
fisher install PatrickF1/fzf.fish
fisher install jhillyerd/plugin-git
fisher install oh-my-fish/plugin-bang-bang
fisher install oh-my-fish/plugin-sudope
fisher install edc/bass

# Enable vi mode
fish_vi_key_bindings

# Set up zoxide if installed
zoxide init fish | source

# Load your secrets via bass
bass source ~/.secrets.env

# Now just use it for 30 minutes — then type exit when done
```

---

## Phase 5: Try It As Default (still reversible)

Once you're comfortable, you can make Fish your default shell:

```bash
# Add Fish to allowed shells (may need this on Linux)
echo (which fish) | sudo tee -a /etc/shells

# Change default shell
chsh -s (which fish)
```

### Revert in one command

```bash
# From Fish or any shell:
chsh -s $(which zsh)
```

Or if you want to nuke the whole Fish experiment:

```bash
chsh -s $(which zsh)          # restore default shell
rm -rf ~/.config/fish          # remove all Fish config
brew uninstall fish            # remove Fish itself (macOS)
# sudo apt remove fish          # (Ubuntu/Debian)
```

Your `.zshrc` was never touched. Everything is exactly as it was.

---

## Quick Reference: Fish Idioms

| What | How in Fish |
|---|---|
| See all abbreviations | `abbr` |
| Add persistent abbreviation | `abbr -a name "command"` |
| Remove abbreviation | `abbr -e name` |
| See all functions | `functions` |
| Edit a function | `funced function_name` then `funcsave function_name` |
| See all variables | `set` |
| Set session variable | `set var value` |
| Set persistent global variable | `set -U var value` (Universal — survives restarts) |
| Drop into bash for a one-liner | `bash -c 'your posix command here'` |

---

## Things That Won't Work / Need Attention

- **`source ~/.secrets.env`** — use `bass source ~/.secrets.env` (see Phase 4 for details on bass).
- **iTerm2 shell integration** — there's a Fish version: `curl -L https://iterm2.com/shell_integration/fish -o ~/.iterm2_shell_integration.fish` then source it in config.fish. (Or skip this if you're also experimenting with Ghostty.)
- **Copy-pasting bash one-liners** — when someone shares `export FOO=bar && ./run.sh`, it won't work in Fish. Either rewrite on the fly, use `bass 'the command'`, or type `bash` to drop into a subshell.
- **Your custom functions (~30 of them)** — these need translating to Fish syntax if you decide to switch permanently. Good Claude Code job. Not needed for the experiment phase.
- **Chezmoi integration** — if you switch, you'd want to manage `~/.config/fish/` alongside your existing dotfiles. Fish config is a separate directory tree, so it coexists cleanly with your Zsh config.
