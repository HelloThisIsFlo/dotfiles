# fzf-tab — Cheat Sheet

> **⚠️ Work in progress.** Still experimenting with fzf-tab — this sheet may change as the setup solidifies.

You press `<tab>` in zsh and get a flat list of completions you can barely navigate. fzf-tab replaces that menu with fzf — fuzzy search, preview, and multi-select on every tab press, for every command. No per-command configuration needed.

---

## How it works

fzf-tab hooks into zsh's `compsys` (the completion system). Any completion that feeds candidates to `compadd` — whether it's built-in, from oh-my-zsh, or your own custom function — automatically gets the fzf treatment. You don't rewrite completions; you upgrade the UI layer.

The completion logic stays the same. fzf-tab just changes how the results are presented and filtered.

---

## Navigation

Once the fzf popup appears:

| Key | Action |
|-----|--------|
| Type anything | Fuzzy-filter the list |
| `Enter` | Accept selection |
| `Esc` | Cancel |
| `Tab` | Mark item for multi-select |
| `Shift+Tab` | Unmark item |
| `/` | Triggers deeper path completion (drill into directories) |
| `Ctrl+Space` | Toggle selection (alternative multi-select) |
| `F1` / `F2` | Switch between completion groups (e.g., files vs directories) |
| Up/Down | Navigate the list |

> **About multi-select.** When you mark multiple items and press Enter, they're all inserted space-separated. Useful for `git add <tab>` — select several files at once.

---

## Path drilling

This is the killer feature for file completions. Type `cd <tab>`, select a directory, and fzf-tab automatically triggers another completion round for the next path segment. It feels like navigating a file picker, not fighting a flat list.

For custom completions (like `cma <tab>` with chezmoi managed files), path drilling works if the completion function uses `_multi_parts / array` — which yours does.

---

## Previews

fzf-tab can show previews alongside completions. These are configured per-context with `zstyle`:

```bash
# Preview directory contents when completing cd
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'ls --color=always $realpath'

# Preview file contents when completing cat/bat/less
zstyle ':fzf-tab:complete:(cat|bat|less):*' fzf-preview 'bat --color=always --style=plain $realpath 2>/dev/null || cat $realpath'

# Preview for kill — show process info
zstyle ':fzf-tab:complete:kill:argument-rest' fzf-preview 'ps -p $word -o pid,stat,comm,args'

# Preview for chezmoi shortcuts — show what chezmoi would render
zstyle ':fzf-tab:complete:(cma|cmd|cme|cmm|cmc|cmra):*' fzf-preview 'chezmoi cat ~/$word 2>/dev/null || cat ~/$word'
```

Previews are optional — fzf-tab works fine without any `zstyle` configuration.

> **About `$realpath` vs `$word`.** `$realpath` is the resolved filesystem path (set by fzf-tab for file completions). `$word` is the raw completion text. Use `$realpath` for actual files, `$word` for everything else.

---

## Configuration

All config is via `zstyle` under the `:fzf-tab:` namespace. None of this is required — defaults are sane.

```bash
# Switch between groups with < and > instead of F1/F2
zstyle ':fzf-tab:*' switch-group '<' '>'

# Minimum number of candidates before fzf kicks in (default: 0 = always)
# Set to e.g. 4 if you want small lists to use the regular menu
zstyle ':fzf-tab:*' ignore false

# Disable fzf-tab for a specific command (falls back to regular completion)
zstyle ':fzf-tab:complete:some-command:*' disabled-on any

# Pass extra flags to fzf (e.g., change layout)
zstyle ':fzf-tab:*' fzf-flags --height=40% --layout=reverse
```

---

## Interaction with vi-mode

If you use oh-my-zsh's `vi-mode` plugin, fzf-tab works — but load order matters:

```
antigen bundle zsh-users/zsh-completions   # completions first
antigen bundle Aloxaf/fzf-tab              # fzf-tab after completions
antigen bundle zsh-users/zsh-syntax-highlighting
antigen bundle zsh-users/zsh-autosuggestions  # widget-wrappers last
```

If tab stops working after adding fzf-tab, the most likely cause is a load order issue or fzf not being installed (`brew install fzf`).

> **About Escape delay.** In vi-mode, Escape has an inherent delay (zsh waits to see if it's a multi-key sequence). If the fzf popup feels sluggish to dismiss, add `KEYTIMEOUT=1` to your zshrc to shorten the delay to 10ms.

---

## Quick reference

```
Installation:    antigen bundle Aloxaf/fzf-tab
Dependency:      brew install fzf
Load order:      completions → fzf-tab → syntax-highlighting → autosuggestions

In the popup:
  type          fuzzy filter
  Enter         accept
  Esc           cancel
  Tab           multi-select toggle
  /             drill into directory
  F1/F2         switch completion groups

Config:          zstyle ':fzf-tab:...' key value
Previews:        zstyle ':fzf-tab:complete:CMD:*' fzf-preview 'COMMAND'
Disable for cmd: zstyle ':fzf-tab:complete:CMD:*' disabled-on any
```
