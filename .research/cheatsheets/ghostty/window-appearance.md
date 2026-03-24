# Ghostty — Window & Appearance

How the Ghostty window itself looks — titlebar, padding, transparency, effects. None of this changes terminal behaviour; it's purely visual. Most impactful options first.

---

## Titlebar style

The single biggest visual change you can make to the window.

```
macos-titlebar-style = tabs
```

| Value | What it looks like |
|-------|-------------------|
| `native` | Standard macOS titlebar with title text |
| `transparent` | Titlebar blends with terminal background colour |
| `tabs` | Chrome-style tabs embedded in the titlebar — saves vertical space |
| `hidden` | No titlebar at all, just terminal content |

Use `tabs` if you use tabs. Use `transparent` or `hidden` if you don't. `native` is the default and looks fine — change it only if the titlebar annoys you.

On GTK (Linux), control the tab bar separately:

```
window-show-tab-bar = auto    # Show when there are multiple tabs (default)
# window-show-tab-bar = always
# window-show-tab-bar = never
```

### Titlebar customization

```
window-titlebar-background = #1e1e2e
window-titlebar-foreground = #cdd6f4
window-title-font-family = SF Pro
```

> **About `macos-titlebar-proxy-icon`.** The little folder icon in the titlebar showing the current directory. Set to `hidden` if it bothers you. See [macOS](macos.md) for more macOS-specific options.

---

## Padding

Adds breathing room between the terminal content and the window edge.

```
window-padding-x = 8
window-padding-y = 4
```

Values are in points. Asymmetric padding: `window-padding-x = 8,12` (left, right).

| Key | Default | What it does |
|-----|---------|-------------|
| `window-padding-x` | `0` | Horizontal padding |
| `window-padding-y` | `0` | Vertical padding |
| `window-padding-balance` | `true` | Center content when there's leftover space from cell grid |
| `window-padding-color` | `background` | What fills the padding area |

### Padding colour

| Value | Effect |
|-------|--------|
| `background` | Solid background colour in padding |
| `extend` | Each row's background bleeds into the padding |
| `extend-always` | Same as `extend` but also extends into top/bottom padding |

`extend` is the popular choice — it makes status lines and coloured prompts feel like they reach the window edge. Try it; if it looks messy with your theme, switch back to `background`.

---

## Transparency

```
background-opacity = 0.9
background-blur = true
```

`background-opacity` ranges from `0.0` (fully transparent) to `1.0` (opaque). `background-blur` only takes effect when opacity is below 1.

### macOS glass effects

Instead of basic blur, macOS offers native frosted glass:

```
background-blur = macos-glass-regular    # Frosted glass (like Finder sidebar)
background-blur = macos-glass-clear      # Subtle, less frosting
```

These look more native than a flat opacity + blur combo.

| Key | Default | Notes |
|-----|---------|-------|
| `background-opacity` | `1.0` | Float 0–1 |
| `background-blur` | `false` | `true`, integer, or `macos-glass-*` |
| `background-opacity-cells` | `false` | Apply opacity to cells with background colours too |

> **Quick toggle.** Bind `toggle_background_opacity` to a key to flip transparency on/off without editing config: `keybind = ctrl+shift+o=toggle_background_opacity`

---

## Window size and state

```
window-width = 120
window-height = 35
```

Values are in **cells** (characters), not pixels. Minimum 10 wide, 4 tall.

| Key | Default | What it does |
|-----|---------|-------------|
| `window-width` | System default | Initial width in cells |
| `window-height` | System default | Initial height in cells |
| `maximize` | `false` | Start maximized |
| `fullscreen` | `false` | Start in fullscreen |
| `window-save-state` | `default` | Restore window positions on relaunch (macOS) |
| `window-step-resize` | `true` | Resize snaps to cell boundaries (macOS) |

For fullscreen options, see [macOS](macos.md) — `macos-non-native-fullscreen` has tradeoffs.

---

## Custom shaders

GPU-powered visual effects — CRT scanlines, bloom, chromatic aberration, film grain.

```
custom-shader = /path/to/shader.glsl
custom-shader-animation = true
```

- `custom-shader` is repeatable — stack multiple shaders
- `custom-shader-animation = true` enables animated effects (may use more GPU)
- `custom-shader-animation = always` animates even when the terminal isn't updating
- Community shader collections exist on GitHub — search "ghostty shaders"

> **This is a rabbit hole.** Shaders are fun but purely cosmetic. Only explore if you enjoy tinkering with visual effects.

---

## Background image

```
background-image = ~/Pictures/terminal-bg.png
background-image-opacity = 0.1
background-image-position = center
background-image-fit = cover
```

Supports PNG and JPEG. Keep opacity low (0.05–0.15) or text becomes unreadable.

| Key | Default | Values |
|-----|---------|--------|
| `background-image` | None | File path (repeatable for multiple images) |
| `background-image-opacity` | `1.0` | Float 0.0+ |
| `background-image-position` | `center` | `top-left`, `center`, `bottom-right`, etc. |
| `background-image-fit` | `contain` | `contain`, `cover`, `stretch`, `none` |
| `background-image-repeat` | `false` | Tile the image |

---

## Other visual options

| Key | Default | What it does |
|-----|---------|-------------|
| `window-colorspace` | `srgb` | Set to `display-p3` for wider gamut on macOS |
| `resize-overlay` | `after-first` | Cell count overlay during resize (`always`, `never`, `after-first`) |
| `resize-overlay-position` | `center` | Where the overlay appears |
| `resize-overlay-duration` | `750ms` | How long the overlay stays visible |
| `window-decoration` | `auto` | `none` to remove all window chrome |
| `window-theme` | `auto` | `light`, `dark`, `ghostty`, `system` — controls window frame theme |
