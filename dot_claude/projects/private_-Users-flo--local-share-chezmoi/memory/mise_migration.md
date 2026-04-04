---
name: mise migration status
description: asdf→mise migration completed, architecture decisions, and remaining deferred items
type: project
---

## Migration completed (2026-04-03) — merged to main

asdf fully removed, mise is the version manager. Branch `asdf-to-mise` merged.

### Architecture decisions

- **Explicit activation over auto-activate** — `MISE_FISH_AUTO_ACTIVATE=0` in `12__mise.fish`, explicit `mise_bin activate fish | source` in `89__mise-paths.fish.tmpl`. Reason: auto-activate magically adds paths at end of PATH; explicit keeps load order visible in conf.d numbering.
- **Split config: 12__ (early) + 89__ (late)** — env vars set early (12__), PATH activation runs late (89__) so mise manages PATH after other tools are configured.
- **`MISE_CONFIG_DIR` set explicitly** — defaults to `~/.config/mise` but made explicit for cross-machine consistency.
- **Global config uses `config.toml`** not `.tool-versions` — supports comments, grouping, fuzzy versions.
- **Elixir pinned with OTP suffix** (`1.19.5-otp-28`) — must match erlang version. Update both together.
- **Java uses `temurin-21`** not shorthand `21` — OpenJDK shorthand stops getting updates after 6 months.
- **CLI tools use aqua backend** (delta, cheat) — pre-built binaries from GitHub releases, no compilation. Removed from Brewfile.
- **`mise_install_path` in chezmoidata** — single source of truth for mise binary location, used in bootstrap scripts and fish config via `joinPath .chezmoi.homeDir .mise_install_path`.
- **Mise self-bootstraps** — `run_once_before` curls installer (cross-platform, no Homebrew). Mise removed from Brewfile.
- **`run_onchange_after` for `mise install`** — triggered by config.toml sha256 hash, runs last (0999) to ensure all config files are in place.
- **Direnv replaced by mise** — `env_file = '.env'` in config.toml settings. Direnv removed.
- **Ruby precompiled** — `ruby.compile = false` in settings.

### Bootstrap chain (chezmoi apply on fresh machine)

```
A--BEFORE/run_once_before_0000  → start message
A--BEFORE/run_once_before_0001  → curl-install mise
A--BEFORE/run_once_before_0020  → set fish as default shell
  ... chezmoi applies all files ...
Z--AFTER/run_onchange_after_0010  → brew bundle (macOS only)
Z--AFTER/run_onchange_after_0021  → Fisher plugins
Z--AFTER/run_onchange_after_0022  → Tide config
Z--AFTER/run_onchange_after_0023  → Tide dotenv
Z--AFTER/run_onchange_after_0999  → mise install (last — all config in place)
Z--AFTER/run_once_after_9999      → success message
```

### Remaining deferred items

- **Java macOS integration** — `sudo mkdir` + `sudo ln -s` to register JDK with `/usr/libexec/java_home`. Only needed for IDE discovery. Do if/when needed.
- **pip/npm tools** — historical list in `.research/2026-02-26/Dev Environment Steps (from Notion).md`. Mostly stale. Review before adding to mise as `pipx:` / `npm:` backends.
