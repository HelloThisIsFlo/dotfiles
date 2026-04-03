---
name: mise migration status
description: asdf→mise migration state, pending work items, and architecture decisions for version management
type: project
---

## Migration completed (2026-04-03)

asdf fully removed, mise is the version manager. Branch: `asdf-to-mise`.

### Architecture decisions

- **Explicit activation over auto-activate** — `MISE_FISH_AUTO_ACTIVATE=0` in `12__mise.fish`, manual `mise activate fish | source` in `89__mise-paths.fish`. Reason: auto-activate magically adds paths at end of PATH; explicit keeps load order visible in conf.d numbering.
- **Split config: 12__ (early) + 89__ (late)** — env vars set early (12__), PATH activation runs late (89__) so mise manages PATH after other tools are configured.
- **`MISE_CONFIG_DIR` set explicitly** — defaults to `~/.config/mise` but made explicit for cross-machine consistency.
- **Global config uses `config.toml`** not `.tool-versions` — supports comments, grouping, fuzzy versions.
- **Elixir pinned with OTP suffix** (`1.19.5-otp-28`) — must match erlang version. Update both together.
- **Java uses `temurin-21`** not shorthand `21` — OpenJDK shorthand stops getting updates after 6 months.

### Pending work

- **Java macOS integration** — `sudo mkdir` + `sudo ln -s` to register JDK with `/usr/libexec/java_home`. Only needed for IDE discovery. Decision: deferred, do it if/when needed.
- **`cargo:git-delta`** — hard requirement, currently installed via Homebrew. Could move to `mise use cargo:git-delta` in config.toml.
- **`go:github.com/cheat/cheat/cmd/cheat@latest`** — currently manually installed. Could move to mise.
- **pip/npm tools** — historical list in `.research/2026-02-26/Dev Environment Steps (from Notion).md`. Most likely stale. Review before adding to mise as `pipx:` / `npm:` backends.
- **Language paths review** — `82__language-paths.fish` unchecked in FISH-MIGRATION.md. Go path (`$GOPATH/bin`) and krew path (`$HOME/.krew/bin`) may no longer be needed now that mise manages tool PATHs.
- **Mise replaces the planned `[data.tools]` + `run_onchange_after_install-*` pattern** from MIGRATION.md Phase 6. One config file instead of per-ecosystem chezmoi scripts.
