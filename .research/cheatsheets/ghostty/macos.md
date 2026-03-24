# Ghostty — macOS

macOS-specific options, gathered in one place. Some of these also appear in other sheets with cross-references — this is the "I'm on a Mac, what should I know?" overview.

---

## Option key as Alt

The single most important macOS setting. Without it, `Option+key` sends Unicode characters instead of `Alt+key` escape sequences, breaking readline shortcuts, tmux keybinds, and vim mappings.

```
macos-option-as-alt = true
```

| Value | Behaviour |
|-------|-----------|
| `true` | Both Option keys act as Alt |
| `false` | Both send Unicode characters (macOS default) |
| `left` | Left Option = Alt, Right Option = Unicode |
| `right` | Right Option = Alt, Left Option = Unicode |

> **About the default.** US Standard and US International keyboard layouts default to `true`. All other layouts default to `false`. If your Alt keybinds aren't working, this is the first thing to check.

`left` or `right` is useful if you need both behaviours — Alt for terminal shortcuts on one key, Unicode for special characters (accented letters, symbols) on the other.

---

## Titlebar

```
macos-titlebar-style = tabs
```

See [Window & Appearance](window-appearance.md) for full details. Quick summary:

| Value | Look |
|-------|------|
| `native` | Standard macOS titlebar |
| `transparent` | Blends with terminal background |
| `tabs` | Chrome-style tabs in titlebar |
| `hidden` | No titlebar |

Related options:

| Key | Default | What it does |
|-----|---------|-------------|
| `macos-titlebar-proxy-icon` | `visible` | The folder icon showing current directory — `visible` or `hidden` |
| `macos-window-buttons` | `visible` | Traffic light buttons — `visible` or `hidden` |
| `macos-window-shadow` | `true` | Window drop shadow |

---

## Fullscreen

```
macos-non-native-fullscreen = true
```

| Value | Behaviour |
|-------|-----------|
| `false` | Native macOS fullscreen (slide animation, own Space) |
| `true` | Instant fullscreen, no animation, stays on current Space |
| `visible-menu` | Non-native but keeps the menu bar visible |
| `padded-notch` | Non-native with padding for the notch on newer MacBooks |

Non-native fullscreen is faster and less disruptive (no Space-switching animation). But:

> **Tabs break in non-native fullscreen.** The titlebar is removed, and tabs live in the titlebar. If you use `macos-titlebar-style = tabs`, stick with native fullscreen or accept that tabs won't be visible in fullscreen mode.

---

## Secure input

```
macos-auto-secure-input = true
macos-secure-input-indication = true
```

Ghostty detects password prompts and automatically enables macOS Secure Input, which prevents other apps from reading keystrokes. The lock icon in the titlebar shows when it's active.

Both are on by default. You'd only disable these if secure input interferes with another tool (some keyboard managers, text expanders, or Karabiner-Elements can be affected).

---

## Dock and app visibility

```
macos-hidden = never
```

| Value | Behaviour |
|-------|-----------|
| `never` | Normal — Ghostty in Dock and Cmd+Tab |
| `always` | Hidden from Dock and Cmd+Tab entirely |
| `if-other-instances` | Hidden only when other Ghostty windows exist |

`always` is for [Quick Terminal](quick-terminal.md)-only setups where you don't want a Dock icon.

> **Gotcha.** `macos-hidden = always` disables automatic keyboard layout switching — macOS can't switch layouts for an app hidden from the app switcher. If you use multiple keyboard layouts, use `if-other-instances` instead.

| Key | Default | What it does |
|-----|---------|-------------|
| `macos-dock-drop-behavior` | `new-tab` | What happens when you drop a file on the Dock icon — `new-tab` or `new-window` |

---

## App icon

Pure cosmetic — Ghostty ships with several icon variants.

```
macos-icon = hologram
```

Options: `official`, `blueprint`, `chalkboard`, `microchip`, `glass`, `hologram`, `paper`, `retro`, `xray`, and more.

```
macos-icon-frame = aluminum       # Frame material around the icon
macos-custom-icon = /path/to.icns # Use your own icon (PNG, JPEG, or ICNS)
```

---

## Other macOS options

| Key | Default | What it does |
|-----|---------|-------------|
| `macos-applescript` | `true` | Enable AppleScript dictionary for automation |
| `window-save-state` | `default` | Restore windows on relaunch — `default`, `never`, `always` |
| `window-step-resize` | `true` | Resize snaps to cell boundaries |
| `window-colorspace` | `srgb` | Set to `display-p3` for wider colour gamut |

---

## Quick reference

The "just make macOS work" config block:

```
macos-option-as-alt = true
macos-titlebar-style = tabs
macos-auto-secure-input = true
```

Everything else is preference. Most macOS defaults are sensible.
