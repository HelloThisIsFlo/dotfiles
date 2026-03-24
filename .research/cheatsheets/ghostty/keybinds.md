# Ghostty — Keybinds

Ghostty's keybind system goes deeper than most terminals. Beyond simple shortcuts, it supports chord sequences (tmux-style prefix keys), modal key tables, conditional triggers, and chained actions. This sheet covers the full system.

---

## Basics

```
keybind = trigger=action
```

```
keybind = ctrl+shift+c=copy_to_clipboard
keybind = cmd+t=new_tab
keybind = ctrl+shift+n=unbind
```

- `unbind` removes a default binding and lets the key pass through to the program
- `ignore` swallows the key without doing anything
- Repeat a keybind key to add multiple bindings; later ones override earlier ones for the same trigger

### Modifiers

| Modifier | Aliases |
|----------|---------|
| `ctrl` | `control` |
| `alt` | `opt`, `option` |
| `shift` | — |
| `super` | `cmd`, `command` |

The fn/"globe" key cannot be used as a modifier.

---

## Prefixes

Prefixes change *when* and *where* a keybind fires. Combine them with `+` in any order.

### `global:`

Works even when Ghostty isn't focused — system-wide hotkey. Essential for [Quick Terminal](quick-terminal.md).

```
keybind = global:ctrl+grave_accent=toggle_quick_terminal
```

Requires Accessibility permissions on macOS. Cannot be used with chord sequences.

### `performable:`

Only triggers if the action can actually execute right now. The key passes through to the program otherwise.

```
# Copy if there's a selection, otherwise send Ctrl+C to the program
keybind = performable:ctrl+c=copy_to_clipboard
```

This is the way to have a single key that copies when text is selected and sends the interrupt signal when it isn't.

### `unconsumed:`

Triggers the action but also sends the key to the running program.

```
keybind = unconsumed:ctrl+shift+e=open_config
```

### `all:`

Applies to all key tables, not just the default one. Useful for "escape" bindings that should work everywhere.

---

## Chord sequences

Press a key, then another key — like tmux's `Ctrl+B` prefix.

```
# Press Ctrl+A, then N → new window
keybind = ctrl+a>n=new_window

# Press Ctrl+A, then 1 → go to tab 1
keybind = ctrl+a>1=goto_tab:1
```

The `>` separates keys in the sequence. No timeout between keypresses — Ghostty waits indefinitely for the next key.

> **Gotcha.** Binding `ctrl+a` as a standalone key disables all sequences starting with `ctrl+a`. If you want sequences, don't also bind the prefix key to an action.

Cancel an in-progress sequence with the `end_key_sequence` action (bind it to `escape` or similar).

---

## Key tables (modal keybinds)

Named groups of keybinds that activate on demand — like vim modes or tmux's various key tables.

```
# Enter the "resize" key table with Ctrl+A, then R
keybind = ctrl+a>r=key_table:resize

# Keys active only in the "resize" table
keybind = resize/h=resize_split:left,20
keybind = resize/j=resize_split:down,20
keybind = resize/k=resize_split:up,20
keybind = resize/l=resize_split:right,20

# Escape exits the table (use all: so it works from any table)
keybind = all:escape=end_key_sequence
```

You enter a key table with `key_table:name`, and any key not bound in that table exits back to the default.

---

## Chained actions

Run multiple actions from a single keybind:

```
keybind = ctrl+a=new_window
keybind = chain=goto_split:left
```

The `chain` keyword appends an action to the previous keybind. Both actions fire on `ctrl+a`.

---

## Special actions

| Action | What it does | Example |
|--------|-------------|---------|
| `unbind` | Remove binding, key passes to program | `keybind = ctrl+shift+n=unbind` |
| `ignore` | Swallow the key, do nothing | `keybind = cmd+q=ignore` |
| `text:` | Send literal text (Zig string syntax) | `keybind = ctrl+shift+u=text:\x15` |
| `csi:` | Send CSI escape sequence | `keybind = alt+up=csi:1;3A` |
| `esc:` | Send raw escape sequence | `keybind = alt+x=esc:x` |

`text:` is powerful for sending arbitrary input — function key sequences, Unicode characters, or control codes.

---

## Practical recipes

```
# Quick terminal (system-wide)
keybind = global:ctrl+grave_accent=toggle_quick_terminal

# Copy only if selection exists, else send Ctrl+C
keybind = performable:ctrl+c=copy_to_clipboard

# Tmux-style prefix for splits
keybind = ctrl+a>v=new_split:right
keybind = ctrl+a>s=new_split:down
keybind = ctrl+a>h=goto_split:left
keybind = ctrl+a>l=goto_split:right

# Tab navigation
keybind = cmd+1=goto_tab:1
keybind = cmd+2=goto_tab:2
keybind = cmd+3=goto_tab:3

# Disable Cmd+Q to prevent accidental quit
keybind = cmd+q=ignore

# Toggle transparency on/off
keybind = ctrl+shift+o=toggle_background_opacity
```

---

## All keybind actions

Run `ghostty +list-actions` for the full list. Here are the most useful:

### Clipboard & selection

| Action | What it does |
|--------|-------------|
| `copy_to_clipboard` | Copy selection |
| `paste_from_clipboard` | Paste |
| `copy_url_to_clipboard` | Copy URL under cursor |
| `select_all` | Select all text |

### Navigation

| Action | What it does | Parameter |
|--------|-------------|-----------|
| `scroll_to_top` / `scroll_to_bottom` | Jump to top/bottom | — |
| `scroll_page_up` / `scroll_page_down` | Page scroll | — |
| `scroll_page_lines` | Scroll N lines | Integer (+/-) |
| `jump_to_prompt` | Jump between prompts | Offset integer |
| `start_search` | Open search | — |

### Windows, tabs & splits

| Action | What it does | Parameter |
|--------|-------------|-----------|
| `new_window` | New window | — |
| `new_tab` | New tab | — |
| `goto_tab` | Go to tab | Tab number (1-based) |
| `previous_tab` / `next_tab` | Cycle tabs | — |
| `new_split` | Create split | `right`, `down`, `left`, `up`, `auto` |
| `goto_split` | Focus split | `left`, `right`, `up`, `down`, `previous`, `next` |
| `resize_split` | Resize split | `direction,pixels` |
| `toggle_split_zoom` | Maximize/restore split | — |
| `equalize_splits` | Equal-size all splits | — |
| `close_surface` | Close focused surface | — |
| `close_tab` | Close tab | — |

### Display

| Action | What it does |
|--------|-------------|
| `increase_font_size` / `decrease_font_size` | Adjust font size |
| `reset_font_size` | Reset to configured size |
| `toggle_fullscreen` | Enter/exit fullscreen |
| `toggle_background_opacity` | Toggle transparency |
| `toggle_window_decorations` | Show/hide titlebar |
| `toggle_window_float_on_top` | Pin window on top |
| `toggle_command_palette` | Open command palette |

### System

| Action | What it does |
|--------|-------------|
| `toggle_quick_terminal` | Show/hide quick terminal |
| `toggle_visibility` | Show/hide all windows |
| `open_config` | Open config file |
| `reload_config` | Reload config |
| `inspector` | Toggle terminal inspector |

---

## Quick reference

```bash
ghostty +list-keybinds            # Show your current bindings
ghostty +list-keybinds --default  # Show all default bindings
ghostty +list-actions             # List all bindable actions
```
