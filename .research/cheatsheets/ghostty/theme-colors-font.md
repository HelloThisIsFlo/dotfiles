# Ghostty — Theme, Colors & Font

How your terminal looks at a glance — colours and typeface. Theme has the biggest impact (it changes everything), font is second. Fine-tuning is at the bottom.

---

## Theme

### Picking a theme

```bash
ghostty +list-themes
```

This opens an interactive TUI browser — scroll through hundreds of built-in themes and see them applied live. When you find one you like, note the name and add it to your config.

```
theme = Catppuccin Mocha
```

Theme names are **Title Case** since Ghostty 1.2 (not `catppuccin-mocha`).

### Dark/light auto-switching

Match your system appearance automatically:

```
theme = dark:Catppuccin Mocha,light:Catppuccin Latte
```

When macOS switches between dark and light mode, Ghostty follows. No restart needed.

### Custom themes

Drop a file in `~/.config/ghostty/themes/` (or `$XDG_CONFIG_HOME/ghostty/themes/`). Theme files are just normal config files that set colour values:

```
# ~/.config/ghostty/themes/My Theme
background = #1e1e2e
foreground = #cdd6f4
palette = 0=#45475a
palette = 1=#f38ba8
# ... etc
```

Ghostty loads themes before your main config, so your config overrides theme values.

> **Security warning.** Theme files can set ANY config option, not just colors. A malicious theme could change your shell command, keybinds, or other settings. Review third-party theme files before using them.

### The `auto/` directory

When you pick a theme through Ghostty's GUI (command palette or `+list-themes`), it writes to `auto/theme.ghostty`. Include it in your config with:

```
config-file = ?auto/theme.ghostty
```

The `?` makes it optional — no error if the file doesn't exist yet.

---

## Font

### The recommendation

Don't overthink it. **JetBrains Mono** is Ghostty's built-in default — it's excellent, supports ligatures, and requires zero installation. Use it unless you have a reason not to.

If you want Nerd Font icons (for starship, powerlevel10k, etc.), use **MesloLGS Nerd Font Mono** — install via `brew install font-meslo-lg-nerd-font`.

```
# Option A: Built-in default, nothing to install
font-family = JetBrains Mono
font-size = 15

# Option B: Nerd Font for icons
font-family = MesloLGS Nerd Font Mono
font-size = 15
```

Other solid choices if you have a preference: **Fira Code** (best ligatures), **Monaspace** (GitHub's variable font family), **Iosevka** (narrow, high density).

```bash
ghostty +list-fonts              # What's installed on your system
ghostty +list-fonts --family     # Just font family names
```

### Font thickening (macOS)

macOS Retina renders thin fonts *very* thin. If your font looks wispy:

```
font-thicken = true
```

This is macOS-only. On Linux, use `freetype-load-flags` instead.

### Fallback chains

`font-family` is repeatable. Ghostty tries each font in order per glyph:

```
font-family = JetBrains Mono
font-family = Symbols Nerd Font Mono
```

This gives you JetBrains Mono for text and Nerd Font symbols for icons — best of both worlds without switching your primary font.

---

## Font fine-tuning

For most people, `font-family` + `font-size` is enough. These are for when you need more control.

### Ligatures and OpenType features

```
# Disable ligatures (contextual alternates)
font-feature = -calt

# Disable all ligatures
font-feature = -liga
font-feature = -calt

# Enable a specific stylistic set
font-feature = ss01
```

### Codepoint mapping

Route specific Unicode ranges to a different font. The clean way to get Nerd Font icons without making a Nerd Font your primary:

```
# Private Use Area → Nerd Font symbols
font-codepoint-map = U+E000-U+F8FF=Symbols Nerd Font Mono

# Emoji → Apple Color Emoji
font-codepoint-map = U+1F600-U+1F64F=Apple Color Emoji
```

### Variable fonts

If your font supports variable axes:

```
font-variation = wght=500          # Weight
font-variation-bold = wght=700     # Bold weight
```

### Per-style overrides

```
font-family-bold = JetBrains Mono
font-style-bold = ExtraBold
font-synthetic-style = no-bold     # Don't synthesize, use the real bold
```

---

## Color overrides

Override individual colors from your theme:

```
foreground = #cdd6f4
background = #1e1e2e
cursor-color = #f5e0dc

# Override specific palette entries (0-255)
palette = 0=#45475a
palette = 1=#f38ba8

# Selection colors
selection-foreground = #1e1e2e
selection-background = #f5e0dc
```

Special values for selection colors: `cell-foreground` and `cell-background` use the cell's own colours (inverted selection).

---

## Quick reference

| I want to... | Use |
|------|-----|
| Browse themes interactively | `ghostty +list-themes` |
| Auto-switch dark/light | `theme = dark:X,light:Y` |
| See available fonts | `ghostty +list-fonts` |
| Get Nerd Font icons with any font | `font-codepoint-map = U+E000-U+F8FF=Symbols Nerd Font` |
| Disable ligatures | `font-feature = -calt` |
| Fix thin fonts on Retina | `font-thicken = true` |
| Check which font renders a character | `ghostty +show-face --string "icon"` |
