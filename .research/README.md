# Chezmoi Research & Reference

Reference material for the chezmoi dotfiles repo. Nothing here is deployed to the target — it's all for humans and AI assistants working on the repo.

---

## Living documents

- **[MIGRATION.md](MIGRATION.md)** — Mackup → chezmoi migration tracker. Current status, phase checklists, what's broken, what's next. **Start here** when returning to the repo after a break.

---

## Cheatsheets

Timeless reference docs for chezmoi concepts. See **[cheatsheets/INDEX.md](cheatsheets/INDEX.md)** for detailed descriptions of each sheet.

- [Templates](cheatsheets/templates.md) — `{{ }}` syntax, conditionals, functions, real-world examples
- [Run Scripts](cheatsheets/run-scripts.md) — `run_once_before_`, `run_onchange_after_`, execution order
- [Secrets](cheatsheets/secrets.md) — rbw setup, template syntax for secrets, age as escape hatch
- [Configuration](cheatsheets/config.md) — `chezmoi.toml` settings: git, diff, merge, encryption
- [Data Sources](cheatsheets/data-sources.md) — `.chezmoi.toml.tmpl`, `.chezmoidata`, prompts, data merging
- [macOS Preferences](cheatsheets/macos-preferences.md) — `defaults write` in run scripts instead of managing plists
- [Naming Conventions](cheatsheets/naming.md) — `dot_`, `private_`, `encrypted_`, `modify_` — the full prefix system
- [Externals](cheatsheets/externals.md) — `.chezmoiexternal.toml` for third-party repos and archives
- [Hooks](cheatsheets/hooks.md) — `read-source-state.pre` for password manager bootstrap, git hooks
- [Tips & Escape Hatches](cheatsheets/tips.md) — `chezmoi doctor`, `forget`, `merge`, debugging, recovery

---

## Session notes

### 2026-02-17

- [Migration Status](2026-02-17/migration-status.md) — Full audit: what chezmoi manages, what's still Mackup-symlinked, plist deep dive with recommendations
- [Original CLAUDE.md](2026-02-17/ORIGINAL_CLAUDE.md) — Snapshot of CLAUDE.md before migration planning began
- [Plist Tutorial](2026-02-17/plist-chezmoi-tutorial.html) — HTML reference on managing plists with chezmoi

### 2026-02-25

- [Decisions](2026-02-25/decisions.md) — Architecture decisions: rbw-only secrets, edit→apply workflow, no age for v1
- [Next Actions](2026-02-25/next-actions.md) — Phased plan from clean foundation through multi-machine setup
- [Conversation Summary](2026-02-25/conversation-summary.md) — Context behind the rbw decision, options considered and eliminated
- [Assistant Skill Rationale](2026-02-25/assistant-skill-rationale.md) — Why a Claude Code skill (not MCP), what it does, when to build it
