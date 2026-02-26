# Mackup → Chezmoi Migration Tracker

Living document. Updated as migration progresses. Any agent or returning human should read this first.

> **This repo is in transitionary mode.** The migration from Mackup symlinks to fully chezmoi-managed config is in progress. See [Post-Migration Transition](#post-migration-transition) for what changes when it's done.

---

## Current State

Last verified: 2026-02-26

### Summary


| Area                                          | Status            | Notes                                                                      |
| --------------------------------------------- | ----------------- | -------------------------------------------------------------------------- |
| chezmoi config (`.chezmoi.toml.tmpl`)         | Done              | `[data]` prompts for email/machine_type/is_headless, rbw hook, comments    |
| Install hook (`.ensure-password-manager-installed.sh`) | Done     | Installs `rbw`, replaces old `.install-password-manager.sh`                |
| `rbw` on machine                              | Configured        | v1.15.0, email/lock-timeout/pinentry-mac set, wired into chezmoi           |
| Shell config (`.zshrc`)                       | Managed           | `private_dot_zshrc` — working, no templates yet                            |
| Homebrew bundle                               | Managed           | `dot_Brewfile` + `run_onchange_after_` script — working                    |
| Mackup public dotfiles                        | Still symlinked   | ~20 files in `~/config-in-the-cloud/dotfiles/restored_via_mackup/`         |
| Mackup secret dotfiles                        | Still symlinked   | ~6 files in `~/config-in-the-cloud/dotfiles-secret/restored_via_mackup/`   |
| macOS plists                                  | Partially managed | 6 plists in chezmoi, 5 show MM (modified-modified) drift                   |
| Ice.plist                                     | Broken            | `DA` status — deleted from source but exists on disk                       |
| `.gitconfig`                                  | Not in chezmoi    | Still a Mackup symlink                                                     |
| `.ssh/config`                                 | Not in chezmoi    | Not managed by either tool                                                 |


### What works

- `chezmoi apply` runs successfully (ignoring plist drift)
- `autoCommit` on add/apply — every change tracked
- `delta` diff pager — readable diffs
- `plutil` textconv — binary plists shown as XML in diffs
- Brewfile workflow (`cmbrew` alias)
- Shell config, vim, bash, direnv all managed
- `chezmoi data` returns correct email, machine_type, is_headless values

### What's broken or degraded

- **5 plists show MM drift** — apps write runtime data (GPS, timestamps, window state) into the same files chezmoi tracks. `chezmoi apply` would silently overwrite target changes.
- **Ice.plist DA** — deleted from chezmoi source, file exists on disk. Needs `chezmoi add` or `chezmoi forget`.
- **Mackup symlinks are a ticking clock** — macOS 14+ (Sonoma) breaks `cfprefsd` symlinks in `~/Library/Preferences`. See [migration-status.md known issue](2026-02-17/migration-status.md#important-going-back-to-mackup-is-not-viable).

---

## Progress Checklist

At-a-glance view of every task. Check items off as they're completed.

### Phase 1: Foundation ✅

- [x] Install `rbw` via Homebrew
- [x] Configure `rbw` (email, lock timeout, pinentry-mac)
- [x] Rewrite `.chezmoi.toml.tmpl` — `[data]` prompts, rbw references, comments
- [x] Rename + rewrite install hook → `.ensure-password-manager-installed.sh`
- [x] Run `chezmoi init --prompt` and verify with `chezmoi data`

### Phase 2: First Templates ⬜ ← next

- [ ] Replace `.gitconfig` Mackup symlink with real file
- [ ] `chezmoi add --template ~/.gitconfig` and templatise (email, name)
- [ ] Add `.ssh/config` as template with machine-type conditionals
- [ ] Add `.chezmoiignore` rules for machine-specific files

### Phase 3: Triage + Migrate Mackup Symlinks ⬜

- [ ] Triage ~20 Mackup-symlinked files (keep/drop/migrate decisions)
- [ ] Migrate decided files into chezmoi
- [ ] Remove resolved Mackup symlinks

### Phase 4: Wire Secrets into Templates ⬜

- [ ] Identify files containing secrets
- [ ] Organise Bitwarden vault items for chezmoi naming
- [ ] Convert secret files to `.tmpl` with `{{ (rbw "...") }}` syntax
- [ ] Verify `secrets = "error"` catches missed plaintext

### Phase 5: Volatile Plists → `defaults write` Scripts ⬜

- [ ] Start with simplest app (Mos or Clocker) to learn the pattern
- [ ] Discover keys with `prefsniff` or `defaults read` diffing
- [ ] Create `run_onchange_after_configure-<app>.sh.tmpl` for each app
- [ ] `chezmoi forget` raw plist files as scripts replace them
- [ ] Apps: Moom, Raycast, Bartender, iStat Menus, Clocker, Ice

### Phase 6: Multi-Machine Testing ⬜

- [ ] Test `chezmoi init --apply` on a second Mac (or VM)
- [ ] Test on headless Linux
- [ ] Fix whatever breaks

### Phase 7: Post-Migration Transition ⬜

- [ ] Build Claude Code assistant skill for health checks
- [ ] Rewrite CLAUDE.md — remove migration section
- [ ] Archive this file
- [ ] Clean up `~/config-in-the-cloud/*/restored_via_mackup/`

---

## Target End State

When migration is complete:

- All config files managed by chezmoi (no Mackup symlinks remain)
- Secrets injected via `rbw` templates — no plaintext secrets in source
- Volatile plists replaced by `run_onchange_` scripts with `defaults write`
- `.chezmoi.toml.tmpl` prompts for machine type, email, headless flag
- `chezmoi init --apply <github-user>` works from scratch on Mac + Linux
- A Claude Code skill handles ongoing health checks and triage
- `~/config-in-the-cloud/*/restored_via_mackup/` directories cleaned up or archived

---

## Migration Phases

Detailed instructions for each phase live in [next-actions.md](2026-02-25/next-actions.md). This section tracks completion status only.

### Phase 1: Foundation

> Goal: working baseline with rbw, clean config, updated install hook.

Reference: [next-actions.md §Phase 1](2026-02-25/next-actions.md#phase-1-clean-foundation)

- Install `rbw` via Homebrew (v1.15.0 confirmed)
- Configure `rbw` (email, lock timeout, pinentry-mac)
- Rewrite `.chezmoi.toml.tmpl` — add `[data]` prompts, remove `bw` references, clean up `[diff]`
- Rewrite `.install-password-manager.sh` for `rbw`
- Run `chezmoi init --prompt` to generate fresh config
- Verify with `chezmoi data`

### Phase 2: First Templates

> Goal: `.gitconfig` and `.ssh/config` under chezmoi management as templates.

Reference: [next-actions.md §Phase 2](2026-02-25/next-actions.md#phase-2-first-files-under-management)

- Replace `.gitconfig` Mackup symlink with real file, `chezmoi add --template`
- Templatise `.gitconfig` (email, name, delta config)
- Add `.ssh/config` as template with machine-type conditionals
- Add `.chezmoiignore` rules for machine-specific files

### Phase 3: Triage + Migrate Mackup Symlinks

> Goal: every Mackup symlink triaged and either migrated, dropped, or deferred.

Reference: [migration-status.md §Mackup symlinks](2026-02-17/migration-status.md#whats-still-symlinked-by-mackup)

**Triage table** — each file needs a user decision:


| File                                          | Decision          | Notes                      |
| --------------------------------------------- | ----------------- | -------------------------- |
| `~/.gitconfig`                                | Migrate (Phase 2) | Template with email/name   |
| `~/.gitignore_global`                         | ? — User decision | Simple file, `chezmoi add` |
| `~/.tmux.conf`                                | ? — User decision |                            |
| `~/.tool-versions`                            | ? — User decision | asdf versions              |
| `~/.npmrc`                                    | ? — User decision |                            |
| `~/.ideavimrc`                                | ? — User decision | JetBrains vim bindings     |
| `~/.ansible.cfg`                              | ? — User decision | Still used?                |
| `~/.asdfrc`                                   | ? — User decision |                            |
| `~/.pythonrc`                                 | ? — User decision | 1 byte file                |
| `~/.amethyst.yml`                             | ? — User decision | Still used?                |
| `~/.carbon-now.json`                          | ? — User decision | Still used?                |
| `~/.logseq/`                                  | ? — User decision | Directory                  |
| `~/.spacemacs.d/`                             | ? — User decision | Still used?                |
| `~/.ipython/`                                 | ? — User decision | Directory                  |
| `~/.config/cheat`                             | ? — User decision | Still used?                |
| `~/.config/linearmouse`                       | ? — User decision |                            |
| `~/.config/karabiner`                         | ? — User decision |                            |
| `~/.config/terminator/config`                 | ? — User decision | Linux only                 |
| `Library/.../Charles`                         | ? — User decision | Charles proxy              |
| `Library/.../Code/User/...`                   | ? — User decision | VS Code settings+snippets  |
| `Library/.../Code - Insiders/...`             | ? — User decision | VS Code Insiders           |
| `Library/Preferences/com.xk72.charles.config` | ? — User decision | Charles plist              |


### Phase 4: Wire Secrets into Templates

> Goal: secret files managed via `rbw` template functions, no plaintext in source.

Reference: [next-actions.md §Phase 3](2026-02-25/next-actions.md#phase-3-secrets)

- Identify files containing secrets (`.secrets.env`, `.aws/`, `.tadl-`*, etc.)
- Organise Bitwarden vault items with consistent naming for chezmoi
- Convert secret files to `.tmpl` files using `{{ (rbw "...") }}` syntax
- Verify `secrets = "error"` catches any missed plaintext

### Phase 5: Migrate Volatile Plists to `run_onchange_` Scripts

> Goal: noisy plists replaced by deterministic `defaults write` scripts.

Reference: [migration-status.md §The Plist Question](2026-02-17/migration-status.md#the-plist-question-deep-dive), [next-actions.md §Phase 4](2026-02-25/next-actions.md#phase-4-macos-preferences)

- Start with simplest app (Mos or Clocker) to learn the pattern
- Use `prefsniff` or manual `defaults read` diffing to discover keys
- Create `run_onchange_after_configure-<app>.sh.tmpl` for each app
- `chezmoi forget` the raw plist files as each script replaces them
- Apps to migrate: Moom, Raycast, Bartender, iStat Menus, Clocker, Ice

### Phase 6: Multi-Machine Testing

> Goal: `chezmoi init --apply` works from scratch on a second machine.

Reference: [next-actions.md §Phase 5](2026-02-25/next-actions.md#phase-5-multi-machine)

- Test on a second Mac (or VM)
- Test on headless Linux (exercises `is_headless`, `pinentry-tty`)
- Fix whatever breaks

### Phase 7: Post-Migration Transition

> Goal: shift from migration mode to maintenance mode. See [dedicated section below](#post-migration-transition).

- Build Claude Code assistant skill for chezmoi health checks
- Rewrite CLAUDE.md — remove migration section, add maintenance guidance
- Archive this file (move to dated session folder or mark complete)
- Clean up `~/config-in-the-cloud/*/restored_via_mackup/` stale files

---

## Post-Migration Transition

**This section describes the finish line.** When all phases above are complete, the repo shifts from transitionary mode to steady-state maintenance mode. This is not an afterthought — it's the reason the migration exists.

### What changes


| Before (now)                                  | After (post-migration)                                             |
| --------------------------------------------- | ------------------------------------------------------------------ |
| CLAUDE.md has "Migration in progress" section | Replaced with maintenance-mode operating instructions              |
| Agents guided to help with migration phases   | Agents use the assistant skill for health checks                   |
| MIGRATION.md is the primary coordination doc  | Archived — moved to `.research/2026-xx-xx/` or marked `[COMPLETE]` |
| Mixed Mackup symlinks + chezmoi files         | Everything in chezmoi, Mackup retired                              |
| Plist files tracked as binary blobs           | `defaults write` scripts, deterministic and diffable               |


### The assistant skill

A Claude Code skill replaces this migration document as the ongoing agent workflow. Rationale and full spec: [assistant-skill-rationale.md](2026-02-25/assistant-skill-rationale.md).

The skill handles:

- **Health check / triage** — run `chezmoi status` + `chezmoi diff`, classify each change as "apply", "re-add", or "conflict"
- **Target-authoritative file detection** — know which directories (e.g., `~/.claude/`) need `re-add` before `apply`
- **Safety enforcement** — always re-add target-authoritative files before apply, warn on overwrites
- **Semantic commits** — group related changes into meaningful commits
- **File flow awareness** — encoded in a manifest (`.chezmoi-workflow.yaml` or similar)

### When to build it

After Phases 1–5 are complete. The skill needs a real, fully-set-up repo to be useful — building it against a half-migrated repo would encode workarounds for incomplete config.

---

## Completed Items

Reverse-chronological log.


| Date       | What                                     | Details                                                                                                  |
| ---------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 2026-02-26 | **Phase 1 complete**                     | Config template rewritten with `[data]` prompts, install hook renamed + rewritten for `rbw`, `chezmoi init --prompt` verified. |
| 2026-02-25 | Research session: architecture decisions | Decided rbw-only, edit→apply workflow, no age for v1. Created cheatsheets, next-actions, decisions docs. |
| 2026-02-25 | Installed `rbw`                          | v1.15.0 via Homebrew. Configured: email, lock-timeout 12h, pinentry-mac.                                 |
| 2026-02-25 | Documented assistant skill rationale     | [assistant-skill-rationale.md](2026-02-25/assistant-skill-rationale.md)                                  |
| 2026-02-17 | Research session: migration assessment   | Full audit of what chezmoi manages, what's still Mackup, plist deep dive.                                |
| Pre-2026   | Initial chezmoi setup                    | Shell config, Brewfile, vim, direnv, mac app plists added to chezmoi.                                    |


---

## Unknowns / Decisions Needed

- **Triage table (Phase 3):** ~20 Mackup-symlinked files need individual migrate/drop decisions. See table above.
- **VS Code settings sync:** VS Code has built-in Settings Sync — may not need chezmoi management at all.
- **Stale tools:** Several Mackup-managed files may be for tools no longer used (Amethyst, Spacemacs, Carbon Now, Cheat, Ansible). Need user audit.
- **Ice.plist:** Re-add to chezmoi or forget? Depends on whether it moves to a `defaults write` script.
- `**.claude/` directory:** Not yet in chezmoi. Target-authoritative — will need special handling (Phase 6 polish item in next-actions.md §15).

---

## Reference Links


| Document                      | Path                                                                    | Content                                           |
| ----------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------- |
| Architecture decisions        | [decisions.md](2026-02-25/decisions.md)                                 | rbw-only, edit→apply, no age                      |
| Phased action plan            | [next-actions.md](2026-02-25/next-actions.md)                           | Detailed instructions per phase                   |
| Migration assessment (Feb 17) | [migration-status.md](2026-02-17/migration-status.md)                   | What's managed, what's symlinked, plist deep dive |
| Original CLAUDE.md            | [ORIGINAL_CLAUDE.md](2026-02-17/ORIGINAL_CLAUDE.md)                     | Pre-migration CLAUDE.md snapshot                  |
| Assistant skill spec          | [assistant-skill-rationale.md](2026-02-25/assistant-skill-rationale.md) | Why a skill, what it does, when to build          |
| Cheatsheet index              | [cheatsheets/INDEX.md](cheatsheets/INDEX.md)                            | 10 topic cheatsheets for chezmoi                  |
| Plist tutorial                | [plist-chezmoi-tutorial.html](2026-02-17/plist-chezmoi-tutorial.html)   | HTML reference on plist management                |


