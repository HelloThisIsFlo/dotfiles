# Keybinds — macOS Movement & Deletion

Where every Option+Backspace and Option+Arrow config lives. For *why* these choices were made, see the [research doc](../../2026-03-25/opt-backspace-binding-research--fish-vi-etc.md).

---

## Config files at a glance

| Layer | File | What it handles |
|---|---|---|
| Ghostty | `~/.config/ghostty/macos` | `macos-option-as-alt = true` — makes Option send `\x1b` prefix |
| Ghostty | `~/.config/ghostty/features/keybinds` | No custom keybinds needed (built-in `esc:b`/`esc:f` handles arrows) |
| Fish | `~/.config/fish/conf.d/00-keybinds-and-vi-mode.fish` | Word-deletion bindings, `Ctrl+A`/`Ctrl+E` for vi insert mode |
| NeoVim | `~/.config/nvim/lua/config/keymaps.lua` | Insert-mode `<M-BS>`, `<M-b>`, `<M-f>`, `<C-a>`, `<C-e>` |
| Zsh | `~/.zshrc` | **TODO** — `WORDCHARS=''` + keybinds |
| Vim | `~/.vimrc` | **TODO** — `inoremap <M-BS> <C-w>`, `inoremap <M-b>` / `<M-f>` |

Chezmoi source paths:

| Layer | Source path |
|---|---|
| Ghostty macos | `private_Library/Application Support/com.mitchellh.ghostty/macos` |
| Ghostty keybinds | `private_Library/Application Support/com.mitchellh.ghostty/features/keybinds` |
| Fish | `dot_config/private_fish/conf.d/00-keybinds-and-vi-mode.fish` |
| NeoVim | `dot_config/nvim/lua/config/keymaps.lua` |

---

## What each layer does

### Ghostty

`macos-option-as-alt = true` — Option+key sends `\x1b` + key instead of Unicode characters.

This is the foundation. Without it, Option+Backspace sends a special character (like `´`) instead of `\x1b\x7f`.

Built-in keybinds handle Option+Arrow automatically:

```
alt + arrow_left   →  esc:b   (sends \x1b b)
alt + arrow_right  →  esc:f   (sends \x1b f)
```

No custom keybind config needed.

### Fish

Word-deletion uses a soft/hard variable system with platform-aware swapping:

```
soft = backward-kill-word           (stops at punctuation)
mid  = backward-kill-path-component (stops at / = :)        ← Ctrl+W on both platforms
hard = backward-kill-token          (stops at whitespace only)

macOS:  alt = soft,  ctrl = hard
Linux:  alt = hard,  ctrl = soft
```

Bindings are set for both emacs mode and vi insert mode (`-M insert`).

Word-movement (Option+Arrow) works via Fish presets — no custom config needed.

Line navigation (`Ctrl+A`/`Ctrl+E`) is re-added for vi insert mode (emacs presets don't carry over):

```fish
bind -M insert ctrl-a beginning-of-line
bind -M insert ctrl-e end-of-line
```

### NeoVim (LazyVim)

```lua
vim.keymap.set("i", "<M-BS>", "<C-w>", { desc = "Delete word backward" })
vim.keymap.set("i", "<M-b>", "<C-o>b", { desc = "Move word backward" })
vim.keymap.set("i", "<M-f>", "<C-o>w", { desc = "Move word forward" })
vim.keymap.set("i", "<C-a>", "<Home>", { desc = "Beginning of line" })
vim.keymap.set("i", "<C-e>", "<End>", { desc = "End of line" })
```

Only needed in insert mode — normal mode has `b`, `w`, `dB`, `0`, `$`, etc.

### Zsh — TODO

Not yet configured. When needed:

```zsh
# In ~/.zshrc
WORDCHARS=''   # Every non-alphanumeric char is a word boundary
```

### Vim (not NeoVim) — TODO

Not yet configured. When needed:

```vim
" In ~/.vimrc
inoremap <M-BS> <C-w>
inoremap <M-b> <C-o>b
inoremap <M-f> <C-o>w
```

---

## What works out of the box

| Context | Deletion | Movement | Notes |
|---|---|---|---|
| Fish emacs mode | Yes (preset) | Yes (preset) | No config needed |
| Fish vi insert mode | Yes (custom) | Yes (preset) | Deletion + `Ctrl+A`/`E` in `00-keybinds-and-vi-mode.fish` |
| SSH / bash / zsh | Yes (readline) | Yes (readline) | `\x1b\x7f` and `\x1b b`/`\x1b f` handled natively |
| NeoVim insert mode | Yes (custom) | Yes (custom) | Keymaps in `keymaps.lua` |
| Claude Code | Yes (token-level) | Unknown | Not configurable — baked into Ink framework |
| TUI apps (lazygit, etc.) | Varies | Varies | Each app implements its own input handling |

---

## ESC notation by tool

The same byte (ASCII 27) written differently everywhere:

| Notation | Used by | Example |
|---|---|---|
| `\x1b` | Ghostty, C, hex | `\x1b\x7f` |
| `\e` | Fish, bash | `\e\x7f` |
| `<M-...>` | Vim / NeoVim | `<M-BS>` |
| `M-` | Readline (.inputrc) | `M-DEL` |
| `^[` | Terminal output, stty | `^[\x7f` |
| `\033` | Octal, older scripts | `\033\177` |

---

## Debugging

```bash
# Fish — list all active bindings
bind
bind -M insert                    # vi insert mode only
bind | grep backspace             # filter

# Ghostty — list all active keybinds
ghostty +list-keybinds
ghostty +list-keybinds --default  # defaults only

# NeoVim — check a specific mapping
:verbose imap <M-BS>
:verbose imap <M-b>
:imap                             # list all insert-mode maps
```
