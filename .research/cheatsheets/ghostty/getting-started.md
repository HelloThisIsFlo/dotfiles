# Ghostty — Getting Started

You installed Ghostty and want to configure it. This page covers the basics — where the config lives, how it works, and the tools Ghostty gives you to explore it. For what to actually put in the config, see the topic-specific sheets linked at the bottom.

---

## Config file

**macOS:** `~/Library/Application Support/com.mitchellh.ghostty/config.ghostty`
**Linux:** `~/.config/ghostty/config.ghostty` (or `$XDG_CONFIG_HOME/ghostty/config.ghostty`)

Format is dead simple — `key = value`, one per line:

```
theme = Catppuccin Mocha
font-size = 15
mouse-hide-while-typing = true
```

- `#` for comments (must be on their own line)
- Empty value resets to default: `font-family =`
- Case-sensitive keys, always lowercase with hyphens
- No TOML, no YAML, no JSON — just flat key-value

---

## Live reload

`Cmd+Shift+,` (macOS) / `Ctrl+Shift+,` (Linux) reloads your config instantly. Most changes take effect immediately — some (like `font-family`) need a new terminal surface.

---

## Including other config files

```
config-file = /path/to/other.conf
```

Paths are relative to the including file. Two special prefixes:

| Prefix | What it does |
|--------|-------------|
| `?` | Optional — silently skip if the file doesn't exist |
| `?auto` | Resolves to Ghostty's auto-managed config directory |

The `?auto/` directory is where Ghostty stores config set through the GUI (like theme selection via the command palette). You'll often see this in your config:

```
config-file = ?auto/theme.ghostty
```

This means: "if I picked a theme through the GUI, load it." Your hand-edited config takes precedence over auto-managed files because it loads after them.

---

## CLI flags

Every config key works as a CLI flag:

```bash
ghostty --font-size=14
ghostty --theme="Catppuccin Mocha"
```

Useful for testing options without editing your config file.

---

## Discovery commands

These are Ghostty's best-kept secret. Run them from any terminal.

| Command | What it does |
|---------|-------------|
| `ghostty +list-themes` | Interactive theme browser with live preview |
| `ghostty +list-fonts` | List available fonts (`--family` to filter) |
| `ghostty +list-keybinds` | Show active keybinds (`--default` for all defaults) |
| `ghostty +list-actions` | List all keybind actions you can bind to |
| `ghostty +show-config` | Dump current config (`--default --docs` for full annotated reference) |
| `ghostty +validate-config` | Check your config for errors |
| `ghostty +edit-config` | Open config in `$EDITOR` |
| `ghostty +show-face --string "abc"` | Show which font renders specific characters |

`ghostty +list-themes` is the standout — it's a full TUI where you scroll through themes and see them applied live.

---

## What to configure

Start with what matters most, skip what doesn't:

| I want to... | Read |
|------|------|
| Understand what Ghostty does "magically" | [Shell Integration](shell-integration.md) |
| Get a dropdown terminal | [Quick Terminal](quick-terminal.md) |
| Pick a theme and font | [Theme, Colors & Font](theme-colors-font.md) |
| Customize keybinds | [Keybinds](keybinds.md) |
| Tweak titlebar, padding, transparency | [Window & Appearance](window-appearance.md) |
| Use split panes | [Splits](splits.md) |
| Configure clipboard, cursor, scrollback, notifications | [Behavior & Input](behavior-input.md) |
| macOS-specific settings | [macOS](macos.md) |
