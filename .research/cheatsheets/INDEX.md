# Cheatsheets

Reference material organised by topic. Each sheet is self-contained — start with whichever you need.

---

## Chezmoi

- [Templates](chezmoi/templates.md) — conditionals, whitespace, `lookPath`, secrets, debugging
- [Template Fragments](chezmoi/template-fragments.md) — shared config across OS-specific paths, DRY reusable blocks, `{{ template }}` vs `{{ include }}`
- [Run Scripts](chezmoi/run-scripts.md) — frequency prefixes, ordering, change detection
- [Secrets](chezmoi/secrets.md) — rbw setup, template syntax, age encryption
- [Configuration](chezmoi/config.md) — encryption, git, diff/merge tools, `[data]`
- [Data Sources](chezmoi/data-sources.md) — built-in variables, prompts, `.chezmoidata`
- [macOS Preferences](chezmoi/macos-preferences.md) — `defaults write` scripts, discovery, app restarts
- [Naming Conventions](chezmoi/naming.md) — prefixes, stacking, deployment control
- [Externals](chezmoi/externals.md) — `.chezmoiexternal.toml`, archives, git repos
- [Brew Management](chezmoi/brew-management-approaches.md) — three patterns compared
- [Hooks](chezmoi/hooks.md) — vs run scripts, event types, bootstrap use case
- [Merge Explainer ↗](chezmoi/chezmoi-merge.html) — 3-way merge visual guide (open in browser)
- [Merge Simulator ↗](chezmoi/chezmoi-merge-interactive.html) — interactive merge sandbox
- [Status Columns](chezmoi/chezmoi-status.md) — what `MM`, ` M`, `M ` actually mean
- [Tips & Escape Hatches](chezmoi/tips.md) — doctor, merge, forget, debug templates

## Ghostty

- [Getting Started](ghostty/getting-started.md) — config format, file locations, `?auto`, live reload, CLI discovery commands
- [Shell Integration](ghostty/shell-integration.md) — auto-injection, prompt features, SSH terminfo, working dir tracking
- [Quick Terminal](ghostty/quick-terminal.md) — dropdown terminal setup, `global:` keybind, QT-only mode
- [Keybinds](ghostty/keybinds.md) — syntax, prefixes, chord sequences, key tables, all actions
- [Theme, Colors & Font](ghostty/theme-colors-font.md) — theme browser, dark/light auto-switch, font setup, codepoint mapping
- [Window & Appearance](ghostty/window-appearance.md) — titlebar, padding, transparency, shaders, background image
- [Splits](ghostty/splits.md) — creating, navigating, resizing, zoom, vs tmux
- [Behavior & Input](ghostty/behavior-input.md) — clipboard, scrollback, cursor, mouse, notifications, bell
- [macOS](ghostty/macos.md) — option-as-alt, fullscreen, secure input, dock visibility, app icon

## NeoVim

- [LazyVim Configuration](neovim/lazyvim-config.md) — file-by-file guide to the LazyVim config directory, layering model, what to track

## Zsh Plugins

- [fzf-tab](zsh-plugins/fzf-tab.md) — fuzzy completion menu, path drilling, previews, config
