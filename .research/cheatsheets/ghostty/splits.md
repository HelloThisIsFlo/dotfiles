# Ghostty — Splits

Ghostty has built-in split panes — no tmux needed for basic multi-pane layouts. If you already use tmux for splits, you might not need these. But if you want splits without the overhead of a terminal multiplexer, Ghostty's are solid.

---

## Creating splits

Splits are created via keybind actions, not config options. Default keybinds depend on your platform — run `ghostty +list-keybinds --default | grep split` to see yours.

```
# Common custom bindings
keybind = ctrl+a>v=new_split:right
keybind = ctrl+a>s=new_split:down
```

| Direction | What it does |
|-----------|-------------|
| `right` | Split vertically, new pane on the right |
| `down` | Split horizontally, new pane below |
| `left` | Split vertically, new pane on the left |
| `up` | Split horizontally, new pane above |
| `auto` | Ghostty picks based on available space |

---

## Navigating

```
keybind = ctrl+a>h=goto_split:left
keybind = ctrl+a>j=goto_split:down
keybind = ctrl+a>k=goto_split:up
keybind = ctrl+a>l=goto_split:right
```

| Direction | What it does |
|-----------|-------------|
| `left`, `right`, `up`, `down` | Move focus in that direction |
| `previous` / `next` | Cycle through splits in order |

Or skip keybinds entirely and use `focus-follows-mouse`:

```
focus-follows-mouse = true
```

Hover over a split to focus it. Simple, but can be surprising if you're used to click-to-focus.

---

## Resizing

```
# Resize with a key table (vim-style)
keybind = ctrl+a>r=key_table:resize
keybind = resize/h=resize_split:left,20
keybind = resize/j=resize_split:down,20
keybind = resize/k=resize_split:up,20
keybind = resize/l=resize_split:right,20
keybind = all:escape=end_key_sequence
```

`resize_split:direction,pixels` — the number is pixels to move the divider. Using a [key table](keybinds.md) means you press `Ctrl+A, R` once, then tap `h/j/k/l` repeatedly to resize, and `Escape` to exit.

Reset all splits to equal size:

```
keybind = ctrl+a>==equalize_splits
```

---

## Zoom

Temporarily maximize a split to fill the entire window:

```
keybind = ctrl+a>z=toggle_split_zoom
```

Press again to restore the original layout. By default, navigating to another split (`goto_split`) unzooms. If you want to stay zoomed when navigating:

```
split-preserve-zoom = navigation
```

This is a 1.3.0+ feature. It lets you peek at other splits without losing your zoom state.

---

## Config options

```
unfocused-split-opacity = 0.7
split-inherit-working-directory = true
```

| Key | Default | What it does |
|-----|---------|-------------|
| `unfocused-split-opacity` | `0.8` | Dim inactive splits (range 0.15–1.0). Lower = more obvious which split is focused |
| `unfocused-split-fill` | Background colour | Colour used for the dimming overlay |
| `split-divider-color` | Auto-chosen | Colour of the divider line between splits |
| `split-inherit-working-directory` | `false` | New splits start in the same directory as the current one |
| `focus-follows-mouse` | `false` | Hover to focus a split |
| `split-preserve-zoom` | Unset | `navigation` to keep zoom when switching splits |

> **Working directory inheritance requires [shell integration](shell-integration.md).** Without it, Ghostty doesn't know your current directory, so new splits always open in `$HOME`. Shell integration is on by default, so this usually just works — but if it isn't working, that's the first thing to check.

---

## Splits vs tmux

| | Ghostty splits | tmux |
|---|---|---|
| Persistence | Gone when window closes | Survives terminal close, SSH disconnect |
| Remote sessions | Local only | Works over SSH |
| Config complexity | A few lines | Significant config ecosystem |
| Session management | None | Named sessions, detach/attach |
| Performance | Native rendering | Extra layer, potential rendering overhead |

Use Ghostty splits for quick local multi-pane work. Use tmux when you need persistence, remote sessions, or complex window management. They can coexist — just be aware that nesting keybinds (Ghostty splits inside tmux) can get confusing.
