# Ghostty — Quick Terminal

You want a terminal that appears instantly with a hotkey — like Quake-style dropdown terminals (iTerm2's hotkey window, Guake, Yakuake). Ghostty has this built in. No third-party tool, no extra app.

---

## Setup

There's no default keybind — you have to add one. This is the most common reason people miss that the feature exists.

```
keybind = global:ctrl+grave_accent=toggle_quick_terminal
```

> **The `global:` prefix is critical.** Without it, the keybind only works when Ghostty is already focused — defeating the purpose. `global:` makes it system-wide, even from other apps. On macOS, this requires **Accessibility permissions** (System Settings > Privacy & Security > Accessibility).

Pick whatever key you like. `ctrl+grave_accent` (backtick) is popular because it mirrors Quake. Other common choices: `` ctrl+` ``, `ctrl+space`, `alt+space`.

---

## Recommended config

```
keybind = global:ctrl+grave_accent=toggle_quick_terminal
quick-terminal-position = top
quick-terminal-size = 40%
quick-terminal-autohide = true
quick-terminal-animation-duration = 0
```

Setting `animation-duration = 0` makes it appear instantly. The default `200ms` slide animation is smooth but adds latency if you're toggling frequently.

---

## All options

| Key | What it does | Default | Values |
|-----|-------------|---------|--------|
| `quick-terminal-position` | Which edge it slides in from | `top` | `top`, `bottom`, `left`, `right`, `center` |
| `quick-terminal-screen` | Which monitor | `main` | `main`, `mouse`, `macos-menu-bar` |
| `quick-terminal-size` | How much screen it covers | Platform default | Percentage (`40%`) or pixels (`500px`) |
| `quick-terminal-autohide` | Hide when you click away | `true` (macOS) | Boolean |
| `quick-terminal-animation-duration` | Slide animation speed | `200ms` | Duration (`0` to disable) |
| `quick-terminal-space-behavior` | Follow across macOS Spaces | `move` | `move`, `remain` |

- `screen = mouse` puts the quick terminal on whichever monitor your mouse is on — useful with multi-monitor setups.
- `space-behavior = remain` keeps the quick terminal on its original Space instead of following you.

---

## The "QT-only" setup

If you only want Ghostty as a quick terminal (no regular windows, no Dock icon):

```
macos-hidden = always
keybind = global:ctrl+grave_accent=toggle_quick_terminal
```

`macos-hidden = always` removes Ghostty from the Dock and `Cmd+Tab` switcher entirely. You interact with it exclusively through the quick terminal hotkey.

> **Gotcha.** `macos-hidden = always` disables automatic keyboard layout switching — macOS can't switch layouts for an app that's hidden from the app switcher. If you use multiple keyboard layouts, use `macos-hidden = if-other-instances` instead (hides only when other Ghostty windows exist).
