# Ghostty — Behavior & Input

The grab bag: clipboard, scrollback, cursor, mouse, notifications, bell, close behavior. Each is too thin for its own file but worth knowing about. Grouped by theme, most useful first.

---

## Clipboard & security

Programs can request to read or write your clipboard via OSC 52. This is how tmux clipboard sync, nvim `+clipboard`, and similar tools work.

```
clipboard-read = ask
clipboard-write = allow
clipboard-paste-protection = true
copy-on-select = clipboard
```

| Key | Default | What it does |
|-----|---------|-------------|
| `clipboard-read` | `ask` | Programs reading your clipboard — `ask`, `allow`, `deny` |
| `clipboard-write` | `allow` | Programs writing to your clipboard — `ask`, `allow`, `deny` |
| `clipboard-paste-protection` | `true` | Confirm when pasting potentially dangerous text (multiline, suspicious content) |
| `copy-on-select` | `true` | Auto-copy when you select text |
| `clipboard-trim-trailing-spaces` | `false` | Strip trailing whitespace on copy |

### `copy-on-select` values

| Value | Behaviour |
|-------|-----------|
| `true` | Copy to primary selection (X11-style — paste with middle-click) |
| `clipboard` | Copy to system clipboard (paste with `Cmd+V`) |
| `false` | Don't auto-copy; require explicit `Cmd+C` / keybind |

On macOS, `clipboard` is usually what you want — there's no primary selection buffer.

> **Clipboard sync not working?** If tmux or nvim can't access your clipboard, check `clipboard-read` and `clipboard-write`. The default `ask` for reads means you'll get a prompt the first time — easy to miss or accidentally deny.

---

## Scrollback

```
scrollback-limit = 10000000
```

| Key | Default | What it does |
|-----|---------|-------------|
| `scrollback-limit` | Large (system default) | Buffer size per terminal, **in bytes** (not lines) |
| `scroll-to-bottom` | `keystroke` | When to auto-scroll to bottom |
| `scrollbar` | `system` | Scrollbar visibility — `system` or `never` |

The scrollback buffer is allocated lazily — setting it high doesn't waste memory until you actually accumulate that much output.

> **About `scroll-to-bottom`.** By default, new output does NOT scroll you to the bottom — only pressing a key does. This means you can read scrollback while a program produces output without getting yanked down. If you want the traditional auto-scroll behaviour, add `output`: `scroll-to-bottom = keystroke,output`.

There's no unlimited scrollback option yet. For long-running output you need to capture, pipe to a file or use `write_scrollback_file` keybind action.

---

## Cursor

```
cursor-style = bar
cursor-click-to-move = true
```

| Key | Default | What it does |
|-----|---------|-------------|
| `cursor-style` | `block` | `block`, `bar`, `underline`, `block_hollow` |
| `cursor-style-blink` | Unset | `true`, `false`, or unset (respects DEC Mode 12) |
| `cursor-click-to-move` | `false` | Click to reposition cursor at shell prompt |
| `cursor-color` | Auto from theme | Cursor colour |
| `cursor-text` | Auto from theme | Text colour under cursor |
| `cursor-opacity` | `1` | Cursor opacity (0–1) |

> **Shell integration overrides cursor style at the prompt.** It switches to bar at idle prompts and back to your configured style inside programs. If this annoys you, disable with `shell-integration-features = no-cursor`.

---

## Mouse

```
mouse-hide-while-typing = true
```

| Key | Default | What it does |
|-----|---------|-------------|
| `mouse-hide-while-typing` | `false` | Hide mouse cursor while you type |
| `mouse-scroll-multiplier` | `1` (precision), `3` (discrete) | Scroll speed multiplier |
| `mouse-reporting` | `true` | Allow terminal programs to receive mouse events |
| `right-click-action` | `context-menu` | What right-click does |
| `focus-follows-mouse` | `false` | Hover to focus split pane (see [Splits](splits.md)) |

### Right-click action

| Value | Behaviour |
|-------|-----------|
| `context-menu` | Shows context menu (default) |
| `paste` | Pastes clipboard (iTerm2/PuTTY-style) |
| `copy-or-paste` | Copies if selection exists, otherwise pastes |
| `ignore` | Nothing |

### Selection

| Key | Default | What it does |
|-----|---------|-------------|
| `selection-word-chars` | Whitespace + brackets + quotes | Characters that break double-click word selection |
| `selection-clear-on-typing` | `true` | Clear selection when you start typing |
| `selection-clear-on-copy` | `false` | Clear selection after copying |

---

## Notifications

Get a system notification when a long-running command finishes while you're in another app.

```
notify-on-command-finish = unfocused
notify-on-command-finish-after = 10s
```

| Key | Default | What it does |
|-----|---------|-------------|
| `notify-on-command-finish` | `never` | `never`, `unfocused` (only when Ghostty isn't active), `always` |
| `notify-on-command-finish-after` | `5s` | Minimum command duration before notification triggers |
| `notify-on-command-finish-action` | `bell` | `bell`, `notify` (system notification), or both |

This requires [shell integration](shell-integration.md) — Ghostty needs to know when commands start and finish.

> **Recommended setup.** `unfocused` + `10s` means you only get notified for commands that take a while and only when you've switched to another app. Short commands and commands you're watching don't generate noise.

---

## Bell

```
bell-features = no-audio
```

| Key | Default | What it does |
|-----|---------|-------------|
| `bell-features` | System defaults | Comma-separated: `system`, `audio`, `visual`, `unfocused-window-badge`, `unfocused-window-flash` |
| `bell-audio-path` | None | Custom sound file for the bell |
| `bell-audio-volume` | `0.5` | Volume (0.0–1.0) |

Prefix `no-` to disable: `bell-features = no-audio,visual` (disable audio, enable visual flash).

---

## Close & quit behavior

```
confirm-close-surface = false
quit-after-last-window-closed = false
```

| Key | Default | What it does |
|-----|---------|-------------|
| `confirm-close-surface` | `true` | Ask before closing a terminal. `false` to disable, `always` to always ask (even at idle prompt) |
| `quit-after-last-window-closed` | `false` (macOS) | Quit Ghostty when the last window closes |
| `quit-after-last-window-closed-delay` | None | Wait before quitting (Linux, min `1s`) |

> **With [shell integration](shell-integration.md) enabled**, `confirm-close-surface = true` already skips confirmation at idle prompts. Setting it to `false` also skips confirmation when a program is running — only do this if you're comfortable with potentially killing running processes.
