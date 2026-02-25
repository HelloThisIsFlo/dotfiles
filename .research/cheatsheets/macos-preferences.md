# Chezmoi macOS Preferences (plist) — Cheat Sheet

macOS apps store their preferences in plist files, usually in `~/Library/Preferences/`. These files are tempting to manage with chezmoi — just `chezmoi add` the file, right? Don't. This cheat sheet explains why and what to do instead.

---

## Why you can't manage plist files directly

Two problems make raw plist management unworkable:

**1. The noise problem.** Apps constantly write to their plists — window positions, timestamps, internal counters, cache state. You care about maybe 5-10 settings out of hundreds. If you manage the whole file, your git history is just noise from the app's internal bookkeeping.

**2. The daemon problem.** macOS runs a daemon called `cfprefsd` that caches preferences in memory. Apps read from and write to this cache, not the file on disk. If chezmoi overwrites the plist file, the daemon doesn't know — its cached version wins, and your changes get silently overwritten the next time it flushes. So even if you manage the file, it doesn't stick.

---

## The solution: `defaults write` in run scripts

Instead of managing the plist *file*, you manage a *script* that sets the preferences you care about using `defaults write`. This command goes through the proper macOS API, which updates both the cache and the file atomically. (For general background on how run scripts work, see the [Run Scripts cheat sheet](run-scripts.md).)

### A basic example

Source directory file: `run_onchange_after_macos-defaults.sh.tmpl`

```bash
#!/bin/bash

{{ if eq .chezmoi.os "darwin" -}}

# ============================================
# Dock
# ============================================
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock tilesize -int 48
defaults write com.apple.dock show-recents -bool false

# ============================================
# Finder
# ============================================
defaults write com.apple.finder AppleShowAllExtensions -bool true
defaults write com.apple.finder ShowPathbar -bool true
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"  # list view

# ============================================
# Trackpad
# ============================================
defaults write com.apple.AppleMultitouchTrackpad TrackpadThreeFingerDrag -bool true

# ============================================
# Keyboard
# ============================================
defaults write -g KeyRepeat -int 2
defaults write -g InitialKeyRepeat -int 15
defaults write -g ApplePressAndHoldEnabled -bool false

# ============================================
# Restart affected apps
# ============================================
killall Dock || true
killall Finder || true
killall SystemUIServer || true

{{ end -}}
```

### Why this works

- **Goes through the proper API** — no cache conflicts with `cfprefsd`
- **Selective** — you only declare the settings you intentionally chose
- **Human-readable** — each line is self-documenting
- **Clean git history** — diffs show "added autohide to Dock", not 47 keys changing for no reason
- **Idempotent** — `defaults write` sets the value regardless of current state, safe to run repeatedly

---

## Run script naming strategy

### For most preferences: `run_onchange_after_`

```
run_onchange_after_macos-defaults.sh.tmpl
```

- **`onchange`** — only re-runs when the script content changes (i.e., when you add or modify a setting)
- **`after`** — runs after all files are applied (your shell config, app configs, etc. are in place first)
- **`.tmpl`** — needed for the `{{ if eq .chezmoi.os "darwin" }}` guard, so the script is skipped entirely on Linux

### For one-time setup: `run_once_after_`

If you have preferences that should only be set on initial machine setup (and then the user might customise them), use `run_once_after_` instead. Chezmoi tracks that it ran and won't run it again.

### Splitting into multiple scripts

You can split preferences into separate scripts if you want independent change tracking:

```
run_onchange_after_macos-dock.sh.tmpl
run_onchange_after_macos-finder.sh.tmpl
run_onchange_after_macos-keyboard.sh.tmpl
run_onchange_after_macos-safari.sh.tmpl
```

This way, changing a Dock setting only re-runs the Dock script, not everything. Whether you prefer one big file or several small ones is a matter of taste — one file is simpler to maintain, multiple files give finer-grained control.

---

## The `defaults` command — quick reference

### Value types

| Type | Flag | Example |
|---|---|---|
| Boolean | `-bool` | `defaults write com.apple.dock autohide -bool true` |
| Integer | `-int` | `defaults write com.apple.dock tilesize -int 48` |
| Float | `-float` | `defaults write -g com.apple.trackpad.scaling -float 1.5` |
| String | `-string` | `defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"` |
| Array | `-array` | `defaults write com.apple.dock persistent-apps -array` (clears the array) |
| Dict | `-dict` | Rarely needed directly |

### Reading current values

```bash
# Read a specific key
defaults read com.apple.dock autohide

# Read all keys for a domain (useful for discovering settings)
defaults read com.apple.dock

# Read a specific key and show its type
defaults read-type com.apple.dock autohide
```

### Common domains

| Domain | What it controls |
|---|---|
| `com.apple.dock` | Dock behaviour and appearance |
| `com.apple.finder` | Finder behaviour and appearance |
| `NSGlobalDomain` (or `-g`) | System-wide settings (keyboard, appearance, etc.) |
| `com.apple.Safari` | Safari settings |
| `com.apple.desktopservices` | Desktop/volume behaviour |
| `com.apple.screencapture` | Screenshot settings |
| `com.apple.AppleMultitouchTrackpad` | Trackpad gestures |
| `com.apple.systempreferences` | System Preferences |
| `com.apple.ActivityMonitor` | Activity Monitor |
| `com.apple.mail` | Apple Mail |

### The `NSGlobalDomain` shorthand

`NSGlobalDomain` is the system-wide domain — it's where system-level settings live (keyboard repeat, appearance, file extensions). It's verbose, so use the `-g` shorthand:

```bash
defaults write -g KeyRepeat -int 2
```

> **Edge case: per-app overrides.** macOS merges an app's own domain with `NSGlobalDomain`, with the app's domain taking priority. This means you can override a global setting for a specific app. You almost never need this, but here's the one example where it's genuinely useful:
>
> ```bash
> # Globally: keep the accent picker when holding a key
> defaults write -g ApplePressAndHoldEnabled -bool true
>
> # But in VS Code: disable it so holding j/k gives key repeat (vim navigation)
> defaults write com.microsoft.VSCode ApplePressAndHoldEnabled -bool false
> ```
>
> Every other app sees the accent picker; VS Code gets key repeat. Neat, but rarely needed.

---

## Discovering preferences you want to manage

The hardest part is figuring out which `defaults write` command corresponds to the setting you just changed in System Settings. Here's the workflow:

### Method 1: Snapshot and diff

```bash
# Before changing a setting
defaults read com.apple.dock > /tmp/dock-before.plist

# Change the setting in System Settings / the app

# After changing
defaults read com.apple.dock > /tmp/dock-after.plist

# See what changed
diff /tmp/dock-before.plist /tmp/dock-after.plist
```

### Method 2: Watch for changes in real time

```bash
# Watch all defaults changes (noisy but comprehensive)
# In one terminal:
while true; do
  defaults read com.apple.dock > /tmp/dock-current.plist
  sleep 1
done

# In another terminal, make your change, then check recent file modification
```

### Method 3: Search online

For common settings, someone has already figured out the `defaults write` command. Search for "defaults write [what you want]" — there are comprehensive lists online, and the macOS community has documented most system preferences.

### Method 4: Global defaults dump

```bash
# Nuclear option — dump everything, change something, dump again
defaults read > /tmp/all-before.plist
# Make your change
defaults read > /tmp/all-after.plist
diff /tmp/all-before.plist /tmp/all-after.plist
```

---

## Apps that need a restart

Some apps only read preferences at launch. After writing defaults, you need to restart them:

```bash
killall Dock            # Dock relaunches automatically
killall Finder          # Finder relaunches automatically
killall SystemUIServer  # Menu bar items relaunch automatically
```

Other apps need a full quit and reopen. For these, just note it in a comment:

```bash
defaults write com.apple.Safari ShowFullURLInSmartSearchField -bool true
# Requires Safari restart to take effect
```

Always add `|| true` after `killall` in scripts to prevent the script from failing if the app isn't running:

```bash
killall Dock || true
```

---

## Machine-specific preferences

Using chezmoi template conditionals, you can vary preferences per machine type:

```bash
{{ if eq .chezmoi.os "darwin" -}}

# All Macs
defaults write -g AppleShowAllExtensions -bool true

{{ if eq .machine_type "personal" -}}
# Personal Mac only
defaults write com.apple.dock tilesize -int 48
defaults write com.apple.dock autohide -bool true
{{ end -}}

{{ if eq .machine_type "work" -}}
# Work Mac only
defaults write com.apple.dock tilesize -int 36
defaults write com.apple.dock autohide -bool false
{{ end -}}

killall Dock || true

{{ end -}}
```

---

## What about apps that don't use `defaults`?

Some apps store preferences in their own config files (JSON, YAML, TOML) rather than plists. These are regular files and can be managed normally with chezmoi — as templates if they contain secrets or machine-specific values, or as plain files if they're the same everywhere.

The rule of thumb: if the config is in `~/Library/Preferences/*.plist`, use `defaults write`. If it's in `~/.config/` or `~/Library/Application Support/`, it's probably a regular file you can manage directly.

---

## Quick reference

| Task | How |
|---|---|
| Set a preference | `defaults write <domain> <key> -<type> <value>` |
| Read a preference | `defaults read <domain> <key>` |
| Read all preferences for an app | `defaults read <domain>` |
| Check a value's type | `defaults read-type <domain> <key>` |
| Delete a preference (reset to default) | `defaults delete <domain> <key>` |
| Find what changed | Snapshot before/after with `defaults read > file` and diff |
| Manage with chezmoi | `run_onchange_after_` script with `defaults write` commands |
| Guard for macOS only | `{{ if eq .chezmoi.os "darwin" }}` template conditional |
| Restart affected apps | `killall <app> \|\| true` |
