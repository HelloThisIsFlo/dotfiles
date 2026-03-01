# Chezmoi Dotfiles — Agent Memory

## User preferences

- **Flo values understanding over speed.** Don't rush through steps. Let him explore edge cases and ask questions — that's how he builds confidence with the tooling. Never skip ahead or make decisions for him without asking.
- **Flo wants to run key commands himself** (like `chezmoi add`, `chezmoi init`) to build muscle memory. Offer the command, let him execute it.
- **Semantic commits preferred** — autoCommit is OFF. Group related changes into meaningful commits with clear messages.
- **Open files in Cursor** with `cursor <path>` — the CLI is available at `/usr/local/bin/cursor`.

## Architecture decisions (session 2026-02-28)

- **Delta is a hard requirement** — no `lookPath` guards anywhere (config or templates). Phase 6.5 will ensure delta is installed on all platforms via cargo install script. It's already broken on servers without delta, so no regression.
- **CLAUDE.md layout:** Root `CLAUDE.md` = repo instructions (ignored by chezmoi via `.chezmoiignore`). Home directory instructions live at `~/.claude/CLAUDE.md` (will be managed as `dot_claude/CLAUDE.md`). This works because chezmoi ignores literal dot-prefixed dirs in source (`.claude/` is invisible to chezmoi, only `dot_claude/` maps to `~/.claude/`).
- **Plists forgotten** — all removed from chezmoi via `chezmoi forget`. Will be re-added as `defaults write` scripts in Phase 5. This keeps `chezmoi status` clean.

## Template knowledge confirmed

- `lookPath "binary"` — returns path string or empty string. Idiomatic for checking if software exists.
- `.chezmoi.toml.tmpl` is evaluated at `chezmoi init` time only (not every apply). Template files (`.tmpl`) are evaluated at every `chezmoi apply`.
- Go template variables (`$hasDelta := ...`) are scoped to a single file — can't share across templates.
- `chezmoi data` values in `[data]` section are shared across all templates but are also init-time only.
- `chezmoi execute-template '{{ ... }}'` — great for testing template expressions interactively.
- Empty string is falsy in Go templates, so `{{ if lookPath "delta" }}` works directly — no `ne "" ` needed.

## Migration status

See `.research/MIGRATION.md` for full details. Quick reference:
- **Phase 1:** Done
- **Phase 1.5 (housekeeping):** Done — plists forgotten, `.chezmoiignore` created, autoCommit off
- **Phase 2 (next):** `.gitconfig` done. Remaining: `.gitignore_global`, `.ssh/config`, `~/.claude/CLAUDE.md`
- Mackup dotfiles repo (`~/config-in-the-cloud/dotfiles/`) cleanup deferred to Phase 7

## File migration pattern (established with .gitconfig)

1. Break symlink: `target=$(readlink ~/.file) && rm ~/.file && cp "$target" ~/.file`
2. Add to chezmoi: `chezmoi add --template ~/.file`
3. Edit template: templatise variables (email, homeDir, etc.)
4. Verify: `chezmoi cat ~/.file` then `chezmoi apply ~/.file`
5. Clean Mackup: delete from `~/config-in-the-cloud/dotfiles/restored_via_mackup/`
6. Verify: confirm regular file, no dangling symlink, tool reads config correctly
