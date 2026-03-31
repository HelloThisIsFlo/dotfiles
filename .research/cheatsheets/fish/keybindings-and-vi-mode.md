# Fish Keybindings and Vi Mode — Cheat Sheet

Fish ships with emacs keybindings. Switching to vi mode gives you modal editing, but it silently drops a bunch of muscle-memory emacs bindings (Ctrl+A, Ctrl+E, word deletion). You end up with vi normal mode that works great and an insert mode that feels broken. This sheet covers how vi mode actually works, how to fix what it breaks, and how the platform-aware deletion system ties it all together.

---

## Vi mode

### Enabling vi mode

One function call in a `conf.d/` file. This replaces the default emacs bindings with vi-style modal bindings.

```bash
# In conf.d/00-keybinds-and-vi-mode.fish
if status is-interactive
    fish_vi_key_bindings
end
```

The `if status is-interactive` guard prevents this from running during scripts, subshells, or non-interactive contexts (like `fish -c "some command"`).

> **Gotcha:** `fish_vi_key_bindings` wipes all emacs-mode bindings and installs vi bindings from scratch. Any bindings you define before this call get destroyed. Always call it first, then add your custom bindings after.

### Bind modes

Vi mode introduces four bind modes. Every key you press is dispatched through whichever mode is currently active.

| Mode | Name in `bind -M` | Entered by | Cursor shape |
|---|---|---|---|
| Normal | `default` | Escape, or startup | Block |
| Insert | `insert` | `i`, `a`, `A`, `o`, `O`, etc. | Line (beam) |
| Visual | `visual` | `v`, `V` | Block (underline on some terminals) |
| Replace | `replace` / `replace_one` | `R` / `r` | Underline |

The cursor shape changes automatically — fish handles this with `fish_vi_cursor`. No configuration needed unless your terminal doesn't support DECSCUSR sequences (Ghostty, iTerm2, and Kitty all do).

```bash
# Check what mode you're in
fish_bind_mode  # prints current mode name

# List all bindings for a specific mode
bind -M insert
bind -M default
bind -M visual
```

### What vi mode gives you for free

In normal mode: `h j k l w b e 0 $ f t d c y p` — the full vi motion and operator vocabulary. `dd`, `yy`, `cc`, `diw`, `ci"`, etc. all work.

In insert mode: basic typing. That's about it. Most of the emacs convenience bindings are gone, which is why the next sections exist.

---

## Bind syntax

### Basic structure

```bash
bind [options] KEY_SEQUENCE COMMAND [COMMAND...]
```

The three things you always specify:

1. **Mode** — which vi mode the binding applies to (`-M insert`, `-M default`, etc.)
2. **Key sequence** — what you press
3. **Command** — the fish input function to run

```bash
# Bind Ctrl+A to beginning-of-line in insert mode
bind -M insert ctrl-a beginning-of-line

# Bind Alt+Backspace to backward-kill-word in insert mode
bind -M insert alt-backspace backward-kill-word

# Bind in normal mode (mode name is "default", not "normal")
bind -M default ctrl-r history-pager
```

> **Gotcha:** Normal mode is called `default`, not `normal`. `bind -M normal` silently creates a new mode called "normal" that nothing ever activates. You won't get an error — the binding just never fires.

### Key names: descriptive vs escape sequences

Fish supports descriptive key names for most common keys. Always prefer these — they're readable and portable.

| Descriptive name | What it means |
|---|---|
| `ctrl-a` | Ctrl+A |
| `alt-backspace` | Option+Backspace (macOS) / Alt+Backspace (Linux) |
| `ctrl-backspace` | Ctrl+Backspace |
| `alt-delete` | Option+Delete (forward) |
| `ctrl-delete` | Ctrl+Delete (forward) |
| `ctrl-alt-h` | Ctrl+Alt+H |
| `escape` | Escape key |
| `enter` | Enter/Return |
| `tab` | Tab |

Fish resolves these to the actual byte sequences your terminal sends. This is better than hardcoding escape sequences because different terminals send different bytes for the same key.

```bash
# Prefer this
bind -M insert alt-backspace backward-kill-word

# Over this (terminal-specific, fragile)
bind -M insert \e\x7f backward-kill-word
```

> **Gotcha:** `ctrl-backspace` may not work in all terminals. Some terminals send the same sequence for Ctrl+Backspace as plain Backspace. Ghostty distinguishes them correctly. If a binding doesn't fire, use `fish_key_reader` to see what your terminal actually sends.

### Listing available input functions

```bash
# All available input functions (the commands you can bind to)
bind --function-names

# Useful ones for keybinding work
# backward-kill-word          — delete word backward (stops at punctuation)
# backward-kill-path-component — delete backward (stops at / = :)
# backward-kill-token         — delete backward (stops at whitespace only)
# kill-word                   — delete word forward (stops at punctuation)
# kill-token                  — delete token forward (stops at whitespace only)
# beginning-of-line           — move to start of line
# end-of-line                 — move to end of line
# history-pager               — open the interactive history search
```

### Debugging key sequences

`fish_key_reader` shows exactly what bytes your terminal sends when you press a key. Essential for debugging bindings that don't fire.

```bash
fish_key_reader
# Now press the key combo you're investigating
# Output shows: hex bytes, bind-compatible sequence, and caret notation
```

---

## Soft/hard deletion — the platform-aware three-tier system

Fish has three levels of backward word deletion, each stopping at different boundaries. The config maps these to modifier keys in a platform-aware way.

### The three tiers

| Fish function | Stops at | Example: `foo/bar.baz` with cursor at end |
|---|---|---|
| `backward-kill-word` (soft) | Punctuation (`.`, `-`, `_`, `/`) | Deletes `baz` |
| `backward-kill-path-component` (mid) | Path separators (`/`, `=`, `:`) | Deletes `bar.baz` |
| `backward-kill-token` (hard) | Whitespace only | Deletes `foo/bar.baz` |

Forward deletion works the same way: `kill-word` (soft) and `kill-token` (hard). There's no forward equivalent of `backward-kill-path-component`.

### Platform mapping

macOS has a system-wide convention: Option+Backspace does soft deletion (in Finder, Safari, text fields everywhere). Linux has no such convention, so the mapping is flipped to put the more aggressive action on the more accessible modifier.

```
macOS:   Alt (Option)  = soft     Ctrl = hard
Linux:   Alt            = hard     Ctrl = soft
```

### How the config implements this

```bash
# Variables hold the function names — swapped per platform
set -l soft backward-kill-word
set -l hard backward-kill-token
set -l soft_fwd kill-word
set -l hard_fwd kill-token

if fish_in_macos_terminal
    bind -M insert alt-backspace $soft       # Option+Backspace → soft
    bind -M insert ctrl-backspace $hard      # Ctrl+Backspace → hard
    bind -M insert alt-delete $soft_fwd      # Option+Delete → soft forward
    bind -M insert ctrl-delete $hard_fwd     # Ctrl+Delete → hard forward
else
    bind -M insert alt-backspace $hard       # Alt+Backspace → hard (flipped)
    bind -M insert ctrl-backspace $soft      # Ctrl+Backspace → soft (flipped)
    bind -M insert alt-delete $hard_fwd
    bind -M insert ctrl-delete $soft_fwd
end
```

Bindings are set in both normal (`default`) and insert mode so deletion works regardless of which mode you're in.

> **Gotcha:** `ctrl-alt-h` is bound as a fallback for `ctrl-backspace`. Some terminal/OS combos don't distinguish Ctrl+Backspace from plain Backspace. Ctrl+Alt+H always works because it sends a unique sequence (`\x1b\b`).

> **Gotcha:** `fish_in_macos_terminal` is a fish built-in function — it checks `$TERM_PROGRAM` and `uname`, not just `uname -s`. It correctly returns false when SSH'd from macOS into a Linux box.

For the terminal side of this (Ghostty's `macos-option-as-alt` and how key bytes flow from terminal to shell), see [macOS Movement & Deletion](../keybinds/macos-movement-and-deletion.md).

---

## Missing emacs bindings in vi insert mode

When `fish_vi_key_bindings` runs, it replaces the emacs keymap. These commonly-used bindings disappear from insert mode:

| Binding | Emacs function | Status in vi insert mode |
|---|---|---|
| Ctrl+A | `beginning-of-line` | Gone — must re-add |
| Ctrl+E | `end-of-line` | Gone — must re-add |
| Ctrl+W | `backward-kill-path-component` | Present (vi mode keeps this) |
| Ctrl+U | `backward-kill-line` | Present (vi mode keeps this) |
| Ctrl+K | `kill-line` | Gone — rarely missed |
| Ctrl+L | `clear-screen` | Present |

The fix is two lines:

```bash
bind -M insert ctrl-a beginning-of-line
bind -M insert ctrl-e end-of-line
```

These go after `fish_vi_key_bindings` in the same `conf.d/` file. They only affect insert mode — normal mode has `0` and `$` for the same operations.

> **Gotcha:** You might be tempted to add `ctrl-k` (kill-line) too. Don't — in vi insert mode Ctrl+K is used for digraph entry by some terminal configurations. Stick to the two that matter.

---

## History search

Fish has multiple history search mechanisms. Here's what's available in each mode.

### Normal mode — `k` and `j`

In normal mode, `k` and `j` move through history (like zsh's vi-mode `history-substring-search-up/down`). Fish does prefix-based matching: if you type `git`, press Escape to enter normal mode, then press `k`, it cycles through commands starting with `git`.

### Insert mode — up/down arrows and Ctrl+R

| Key | Function | Behavior |
|---|---|---|
| Up arrow | `up-or-search` | Prefix search (type `git` then Up → cycles `git` commands) |
| Down arrow | `down-or-search` | Reverse direction |
| Ctrl+R | `history-pager` | Full interactive fuzzy search (fzf-like, built into fish) |

The `history-pager` (Ctrl+R) is fish 3.6+ and is the most powerful option — it opens a full-screen search with fuzzy matching, preview, and multi-line command support. No plugin needed.

### Fish vs zsh history search

In zsh, you needed `history-substring-search` (an antigen/oh-my-zsh plugin) and explicit bindkey configuration for both vi normal and insert modes. Fish ships with prefix search and history-pager built in.

```bash
# zsh — all of this was needed:
antigen bundle robbyrussell/oh-my-zsh plugins/history-substring-search
bindkey "$terminfo[kcuu1]" history-substring-search-up
bindkey "$terminfo[kcud1]" history-substring-search-down
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down
bindkey -M vicmd 'k' history-substring-search-up
bindkey -M vicmd 'j' history-substring-search-down
```

```bash
# fish — zero config. All built in.
# Up/Down do prefix search. Ctrl+R opens history pager. k/j work in normal mode.
```

> **Gotcha:** Fish's prefix search matches from the start of the line, not substring. If you typed `docker compose up` and search with `compose`, Up arrow won't find it — you need `docker`. Use Ctrl+R for substring/fuzzy matching.

---

## Differences from zsh vi-mode

If you're coming from zsh with `oh-my-zsh/plugins/vi-mode`, here's what's different.

### Syntax

| Concept | zsh | fish |
|---|---|---|
| Enable vi mode | `antigen bundle vi-mode` or `bindkey -v` | `fish_vi_key_bindings` |
| Add a binding | `bindkey -M viins '^A' beginning-of-line` | `bind -M insert ctrl-a beginning-of-line` |
| Mode names | `viins`, `vicmd`, `visual` | `insert`, `default`, `visual` |
| Key notation | Escape sequences (`'^A'`, `'\e\x7f'`) | Descriptive names (`ctrl-a`, `alt-backspace`) |
| List bindings | `bindkey -M viins` | `bind -M insert` |
| Key debug | `cat -v` or `showkey` | `fish_key_reader` |

### Behavior differences

- **Cursor shape changes automatically** in fish. zsh requires manual `KEYTIMEOUT` and cursor escape sequences in `zle-keymap-select`.
- **No `KEYTIMEOUT` tuning** — fish doesn't have the escape-key delay problem that plagues zsh vi-mode. Mode switching is instant.
- **`Escape` in insert mode** — immediately enters normal mode. In zsh, there's a default 40ms delay (or whatever `KEYTIMEOUT` is set to) before the mode switch registers, causing that sluggish feeling.
- **No mode indicator needed** — the cursor shape IS the indicator. In zsh you had to set up `RPS1` or a custom prompt segment. Fish just changes the cursor.
- **Visual mode `v`** opens `$EDITOR` in zsh (via `edit-command-line`). In fish, `v` enters visual selection mode. To edit in `$EDITOR`, press `Alt+E` or `Alt+V` in fish.

> **Gotcha:** Fish's `Alt+E` (edit command in editor) works in both normal and insert mode. This is the replacement for zsh's `v` in normal mode opening the editor.

### What you lose

- **Text objects are limited** — `ciw`, `diw`, `ci"` work, but complex vim text objects (`cit` for HTML tags, `ci{` for braces across lines) don't.
- **No ex-mode commands** — can't `:s/foo/bar/` on the command line.
- **No registers** — `"ay` / `"ap` don't work. Fish has a single kill ring.
- **No macro recording** — `q` does nothing.

These are shell-readline limitations, not fish-specific. Zsh vi-mode had the same constraints.

---

## Quick reference

### Config location

File: `~/.config/fish/conf.d/00-keybinds-and-vi-mode.fish`
Chezmoi source: `dot_config/private_fish/conf.d/00-keybinds-and-vi-mode.fish`

See [config-structure.md](config-structure.md) for where this fits in the fish config loading order.

### All custom bindings at a glance

| Key | Insert mode | Normal mode | Function |
|---|---|---|---|
| Ctrl+A | beginning-of-line | (use `0`) | Go to start of line |
| Ctrl+E | end-of-line | (use `$`) | Go to end of line |
| Alt+Backspace | soft/hard delete back (platform) | same | Delete word backward |
| Ctrl+Backspace | hard/soft delete back (platform) | same | Delete word backward (other tier) |
| Ctrl+Alt+H | same as Ctrl+Backspace | same | Fallback for Ctrl+Backspace |
| Alt+Delete | soft/hard delete forward (platform) | same | Delete word forward |
| Ctrl+Delete | hard/soft delete forward (platform) | same | Delete word forward (other tier) |
| Up | prefix history search | (use `k`) | Search history |
| Ctrl+R | history-pager | history-pager | Fuzzy history search |
| Escape | → normal mode | — | Switch to normal mode |

### Debugging commands

```bash
bind -M insert                 # list all insert mode bindings
bind -M default                # list all normal mode bindings
bind | grep kill               # find all deletion bindings
fish_key_reader                # see what bytes a keypress sends
fish_bind_mode                 # print current mode name
bind --function-names          # list all available input functions
```

### Cross-references

- [macOS Movement & Deletion](../keybinds/macos-movement-and-deletion.md) — Ghostty and terminal config for key bytes
- [Config structure](config-structure.md) — where keybinding config fits in fish's `conf.d/` load order
