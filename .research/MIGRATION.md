# Mackup → Chezmoi Migration Tracker

Living document. Updated as migration progresses. Any agent or returning human should read this first.

> **This repo is in transitionary mode.** The migration from Mackup symlinks to fully chezmoi-managed config is in progress. See [Post-Migration Transition](#post-migration-transition) for what changes when it's done.

### Migration Principle: Both Sides Clean

A file's migration is **not complete** until:

1. The file is managed by chezmoi (added, templatized if needed, `chezmoi apply` works)
2. The Mackup symlink in `~` is replaced with chezmoi's real file
3. The source file is **deleted** from `~/config-in-the-cloud/dotfiles/restored_via_mackup/` (or `dotfiles-secret/`)
4. Verified: no dangling symlink, no orphan in Mackup folder

Each phase checklist includes Mackup cleanup items — a phase is not done until the old side is clean too.

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
| Mackup public dotfiles                        | Still symlinked   | 14 symlinks in `~/` → `~/config-in-the-cloud/dotfiles/restored_via_mackup/`  |
| Mackup secret dotfiles                        | Still symlinked   | 5 symlinks in `~/` → `~/config-in-the-cloud/dotfiles-secret/restored_via_mackup/` |
| macOS plists                                  | Partially managed | 6 plists in chezmoi, 5 show MM (modified-modified) drift                   |
| Ice.plist                                     | Broken            | `DA` status — deleted from source but exists on disk                       |
| `.gitconfig`                                  | Not in chezmoi    | Still a Mackup symlink                                                     |
| `.ssh/config`                                 | Not in chezmoi    | Deployed by Ansible from `ansible-magic/`; Phase 2 target                  |


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

- [ ] `.gitconfig`: break symlink (cp real file over symlink)
- [ ] `.gitconfig`: `chezmoi add --template` and templatise (email, name, homeDir)
- [ ] `.gitconfig`: verify with `chezmoi cat` and `chezmoi apply`
- [ ] `.gitconfig`: delete source from `~/config-in-the-cloud/dotfiles/restored_via_mackup/.gitconfig`
- [ ] `.gitignore_global`: break symlink, `chezmoi add`, delete from Mackup
- [ ] `.ssh/config`: convert Ansible Jinja2 template to Go template, `chezmoi add --template`
- [ ] Add `.chezmoiignore` rules for machine-specific files

### Phase 3: Triage + Migrate Mackup Symlinks ⬜

- [ ] Triage ~20 Mackup-symlinked files (keep/drop/migrate decisions)
- [ ] Migrate decided files into chezmoi
- [ ] Remove resolved Mackup symlinks
- [ ] Verify `~/config-in-the-cloud/dotfiles/restored_via_mackup/` has no more symlinked files

### Phase 3.5: Non-Mackup Unmanaged Config ⬜

- [ ] `~/.config/karabiner/karabiner.json` — add to chezmoi
- [ ] `~/.config/linearmouse/linearmouse.json` — add to chezmoi
- [ ] `~/.config/cheat/` — add `conf.yml` + personal cheatsheets to chezmoi

### Phase 4: Wire Secrets into Templates ⬜

- [ ] Identify files containing secrets
- [ ] Organise Bitwarden vault items for chezmoi naming
- [ ] Convert secret files to `.tmpl` with `{{ (rbw "...") }}` syntax
- [ ] Verify `secrets = "error"` catches missed plaintext

### Phase 5: Volatile Plists → `defaults write` Scripts ⬜

- [ ] ShiftIt: `defaults write` for all `*KeyCode`/`*Modifiers` keys
- [ ] Rocket: `defaults write` for trigger char, launch-at-login, use-fuzzy-search
- [ ] Bartender: `defaults write` for `ProfileSettings.activeProfile`, `TriggerSettings`
- [ ] Keyboard Maestro: manage `Macros.plist` as binary file; serial via rbw template
- [ ] SteerMouse: manage `Device.smsetting` as binary file (not a plist)
- [ ] iTerm2: `defaults write` for `GlobalKeyMap`, `Profiles`, `TabStyle` (do last — most complex)
- [ ] Moom, Clocker, iStat Menus: already in chezmoi as plists — convert to run scripts
- [ ] `chezmoi forget` raw plist files as each script replaces them
- [ ] Pock, Spotify, Telegram, WhatsApp: document decision (noise-only plists — no user config to preserve, only window positions/update timestamps/session data)

### Phase 6: Multi-Machine Testing ⬜

- [ ] Test `chezmoi init --apply` on a second Mac (or VM)
- [ ] Test on headless Linux
- [ ] Fix whatever breaks

### Phase 6.5: Automate Dev Environment Setup ⬜

Source: `.research/2026-02-26/Dev Environment Steps (from Notion).md`

**Design pattern:** Tool lists live in `.chezmoi.toml.tmpl` as `[data.tools]` tables (pip, npm, cargo, go). Run scripts iterate over those lists with `{{ range }}`. This decouples *what* to install from *how* — same pattern as the existing Brewfile/brew-bundle workflow. When you add a tool to the data list, chezmoi detects the change hash and re-runs the script.

```toml
# In .chezmoi.toml.tmpl [data] section:
[data.tools]
    pip = ["hierarchy", "glances", "ipython", "pre-commit", "poetry", "awscli", "homeassistant-cli", "black[d]"]
    npm = ["yarn", "pragmatic-motd"]
    cargo = ["git-delta"]
    go = ["github.com/cheat/cheat/cmd/cheat@latest"]
```

- [ ] Add `[data.tools]` tables to `.chezmoi.toml.tmpl`
- [ ] `run_once_before_install-xcode-cli.sh` — `xcode-select --install` (macOS only)
- [ ] Verify asdf deps are in `dot_Brewfile` (tcl-tk, pkg-config, readline, etc.)
- [ ] `run_onchange_after_install-asdf-tools.sh.tmpl` — reads `.tool-versions`, installs plugins + versions
- [ ] `run_onchange_after_install-pip-tools.sh.tmpl` — iterates `{{ range .tools.pip }}`, hash includes list
- [ ] `run_onchange_after_install-npm-tools.sh.tmpl` — iterates `{{ range .tools.npm }}`
- [ ] `run_onchange_after_install-cargo-tools.sh.tmpl` — iterates `{{ range .tools.cargo }}`
- [ ] `run_onchange_after_install-go-tools.sh.tmpl` — iterates `{{ range .tools.go }}`
- [ ] `run_once_after_clone-repos.sh` — `hierarchy` command (clones all repos)
- [ ] `run_once_after_install-antigen.sh` — `git clone` antigen
- [ ] `run_once_after_setup-vim.sh` — trigger vim plugin install
- [ ] Review: which Notion steps are fully automated now, which remain manual

### Phase 7: Post-Migration Transition ⬜

- [ ] Clean `~/config-in-the-cloud/dotfiles/restored_via_mackup/`
- [ ] Clean `~/config-in-the-cloud/dotfiles-secret/restored_via_mackup/`
- [ ] Clean `~/config-in-the-cloud/dotfiles-binary/restored_via_mackup/`
- [ ] Audit `~/config-in-the-cloud/secrets/` — migrate live tokens to rbw, archive stale contexts
- [ ] Audit `~/config-in-the-cloud/ansible-magic/` — archive after SSH config migrated in Phase 2
- [ ] Build Claude Code assistant skill for health checks
- [ ] Rewrite CLAUDE.md — remove migration section
- [ ] Archive MIGRATION.md
- [ ] Update Notion "Dev Environment Steps" — mark automated steps, link to chezmoi repo

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

> **SSH config source:** `~/.ssh/config` is currently deployed by Ansible from `~/config-in-the-cloud/ansible-magic/ansible/roles/dev-machine/templates/base_ssh_config`. It's 116 lines with one Jinja2 conditional (`{% if ansible_os_family == "Darwin" %}` for `UseKeychain`). Convert to Go template `{{ if eq .chezmoi.os "darwin" }}` — the deployed file matches the template exactly, so no content reconciliation needed.

### Phase 3: Triage + Migrate Mackup Symlinks

> Goal: every Mackup symlink triaged and either migrated, dropped, or deferred.

Reference: [migration-status.md §Mackup symlinks](2026-02-17/migration-status.md#whats-still-symlinked-by-mackup)

**Triage table** — verified from live symlinks (`find ~ -maxdepth 1 -type l`, 2026-02-26).

Public (`~/config-in-the-cloud/dotfiles/restored_via_mackup/`):

| Symlink                  | Decision                   | Notes                                                                     |
| ------------------------ | -------------------------- | ------------------------------------------------------------------------- |
| `~/.gitconfig`           | Migrate (Phase 2)          | Template with email/name/homeDir                                          |
| `~/.gitignore_global`    | Migrate (Phase 2)          | Referenced by .gitconfig                                                  |
| `~/.tmux.conf`           | Migrate                    | Plain file, no templating needed                                          |
| `~/.tool-versions`       | Migrate                    | asdf version pins (18 tools)                                              |
| `~/.npmrc`               | Migrate (check for tokens) | May need rbw template if auth tokens present                              |
| `~/.ideavimrc`           | Migrate                    | JetBrains vim bindings, plain file                                        |
| `~/.ansible.cfg`         | Migrate                    | Sets default inventory path; low priority but real config                 |
| `~/.asdfrc`              | Migrate                    | Plain file (`java_macos_integration_enable`)                              |
| `~/.pythonrc`            | Migrate                    | 1 byte file                                                               |
| `~/.amethyst.yml`        | Migrate                    | Actively used window manager (11KB, recently updated)                     |
| `~/.carbon-now.json`     | Migrate                    | Code screenshot tool settings; low priority but real config               |
| `~/.logseq`              | Migrate config only        | See Logseq breakdown below                                                |
| `~/.spacemacs.d`         | Migrate                    | 437-line `init.el` + `layers/`. Not actively used but significant invested config |
| `~/.ipython`             | Migrate config only        | `ipython_config.py` (enables autoreload). Skip `history.sqlite` (runtime) |

**Logseq breakdown:**
- **Migrate:** `preferences.json` (theme, toolbar), `config/config.edn` (keyboard shortcuts incl. vim), `config/plugins.edn` (installed plugin list), `settings/` dir (102 per-plugin config JSONs — user preferences)
- **Skip (auto-downloadable):** `plugins/` dir (52 plugin download dirs — dist/, package.json, logos — Logseq re-downloads from plugin list)
- **Skip (mutable runtime):** `graphs/` (graph data, managed by Logseq's own sync)
- **Check:** `git/` dir (Logseq's git integration config — migrate if config, skip if state)

Secret (`~/config-in-the-cloud/dotfiles-secret/restored_via_mackup/`):

| Symlink                  | Decision          | Notes                                |
| ------------------------ | ----------------- | ------------------------------------ |
| `~/.secrets.env`         | ? — Phase 4       | Secrets — needs rbw template         |
| `~/.tadl-pass`           | ? — Phase 4       | Secrets                              |
| `~/.tadl-minion`         | ? — Phase 4       | Secrets                              |
| `~/.cli_chat.json`       | ? — Phase 4       | Secrets                              |
| `~/.aws`                 | ? — Phase 4       | Directory symlink, secrets           |

Also in Mackup folder (not currently symlinked but still stored there):

| File in Mackup folder                           | Notes                                         |
| ----------------------------------------------- | --------------------------------------------- |
| `Library/Application Support/Charles/`           | Charles proxy (certs, passwords.keystore)     |
| `Library/Application Support/Code/`              | VS Code settings — has built-in Settings Sync |
| `Library/Application Support/Code - Insiders/`   | VS Code Insiders                              |
| `Library/Application Support/Tunnelblick/`       | VPN config                                    |


### Phase 3.5: Non-Mackup Unmanaged Config

> Goal: config files discovered outside Mackup that should be in chezmoi.

These files live in `~/.config/` but were never managed by Mackup — they were found during the 2026-02-26 audit.

- `~/.config/karabiner/karabiner.json` — keyboard remapping (complex JSON, actively used)
- `~/.config/linearmouse/linearmouse.json` — mouse acceleration/scroll settings
- `~/.config/cheat/` — `conf.yml` (cheat tool config) + personal cheatsheets directory

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

### Source Audit: config-in-the-cloud/

Full audit completed 2026-02-26. Reference table for all subfolders:

| Subfolder | Contents | Status | Feeds into |
|---|---|---|---|
| `dotfiles/restored_via_mackup/` | 14 public dotfile symlinks | Active | Phase 2–3 |
| `dotfiles-secret/restored_via_mackup/` | 5 secret dotfile symlinks | Active | Phase 4 |
| `dotfiles-binary/restored_via_mackup/` | App plists + Library data (copy-not-symlink) | Active | Phase 5 |
| `dotfiles-binary/plist_human_readable/` | XML versions of binary plists | Reference | Phase 5 analysis |
| `secrets/` | TLS certs (5 contexts), SSH keys, DO tokens | Partially stale | Phase 4 + Phase 7 |
| `ansible-magic/` | Ansible playbooks; `base_ssh_config` template | Mostly stale | Phase 2 (SSH), then archive |

#### Phase 5 Reference: Plist Signal vs. Noise

**Per-app key categories** (which keys to keep in `defaults write` scripts):
- **ShiftIt:** all `*KeyCode`/`*Modifiers` keys (keyboard shortcuts)
- **Rocket:** trigger char, launch-at-login, use-fuzzy-search
- **Bartender:** `ProfileSettings.activeProfile`, `TriggerSettings`
- **Keyboard Maestro:** `Macros.plist` (binary file — entire macro library); serial number via rbw template
- **SteerMouse:** `Device.smsetting` (binary file, not a plist — custom button/scroll mappings)
- **iTerm2:** `GlobalKeyMap`, `Profiles`, `TabStyle` (most complex — do last)

**Noise pattern filters** (keys to exclude from `defaults write` scripts):
- `NSStatusItem Preferred Position *` — menu bar icon positions
- `NSWindow Frame *` — window geometry
- `SU*` — Sparkle update framework
- `NoSync*` — transient app state
- `*RunCount` — launch counters
- `trialStart*` — trial period timestamps

**Special cases:**
- **Keyboard Maestro:** `Macros.plist` is a binary plist containing the full macro library — manage as binary file, not `defaults write`. Serial number goes in separate rbw template.
- **SteerMouse:** `Device.smsetting` is a custom binary format (not a plist at all) — manage as binary file.

**Not migrating (documented reason):**
- **Pock, Spotify, Telegram, WhatsApp:** plists contain only window positions, session tokens, update timestamps — zero user-configured preferences in git history. No config to preserve.

### Phase 6: Multi-Machine Testing

> Goal: `chezmoi init --apply` works from scratch on a second machine.

Reference: [next-actions.md §Phase 5](2026-02-25/next-actions.md#phase-5-multi-machine)

- Test on a second Mac (or VM)
- Test on headless Linux (exercises `is_headless`, `pinentry-tty`)
- Fix whatever breaks

### Phase 6.5: Automate Dev Environment Setup

> Goal: automate the manual "Dev Environment Steps" from Notion into chezmoi run scripts.

Source: [Dev Environment Steps (from Notion)](2026-02-26/Dev%20Environment%20Steps%20(from%20Notion).md)

Design pattern: tool lists in `.chezmoi.toml.tmpl` `[data.tools]` tables, run scripts iterate with `{{ range }}`. Same decoupling as Brewfile workflow — *what* to install vs. *how*.

- Xcode CLI tools (`run_once_before_`)
- asdf plugins + versions from `.tool-versions` (`run_onchange_after_`)
- pip/npm/cargo/go tool lists from `[data.tools]` (`run_onchange_after_` per ecosystem)
- Repo cloning via `hierarchy` (`run_once_after_`)
- Antigen + vim plugin bootstrapping (`run_once_after_`)

### Phase 7: Post-Migration Transition

> Goal: shift from migration mode to maintenance mode. See [dedicated section below](#post-migration-transition).

- Clean all `~/config-in-the-cloud/*/restored_via_mackup/` directories
- Audit `~/config-in-the-cloud/secrets/` — migrate live tokens to rbw, archive stale contexts
- Audit `~/config-in-the-cloud/ansible-magic/` — archive after SSH config migrated in Phase 2
- Build Claude Code assistant skill for chezmoi health checks
- Rewrite CLAUDE.md — remove migration section, add maintenance guidance
- Archive MIGRATION.md
- Update Notion "Dev Environment Steps" — mark automated steps, link to chezmoi repo

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
| 2026-02-26 | Research: config-in-the-cloud full audit  | All 5 subfolders catalogued; plist git history analyzed (104 commits, signal vs noise per app); triage decisions populated; SSH config Ansible source identified; Phase 3.5 added for non-Mackup config |
| 2026-02-26 | **Phase 1 complete**                     | Config template rewritten with `[data]` prompts, install hook renamed + rewritten for `rbw`, `chezmoi init --prompt` verified. |
| 2026-02-25 | Research session: architecture decisions | Decided rbw-only, edit→apply workflow, no age for v1. Created cheatsheets, next-actions, decisions docs. |
| 2026-02-25 | Installed `rbw`                          | v1.15.0 via Homebrew. Configured: email, lock-timeout 12h, pinentry-mac.                                 |
| 2026-02-25 | Documented assistant skill rationale     | [assistant-skill-rationale.md](2026-02-25/assistant-skill-rationale.md)                                  |
| 2026-02-17 | Research session: migration assessment   | Full audit of what chezmoi manages, what's still Mackup, plist deep dive.                                |
| Pre-2026   | Initial chezmoi setup                    | Shell config, Brewfile, vim, direnv, mac app plists added to chezmoi.                                    |


---

## Unknowns / Decisions Needed

- **VS Code settings sync:** VS Code has built-in Settings Sync — may not need chezmoi management at all.
- **Ice.plist:** Re-add to chezmoi or forget? Depends on whether it moves to a `defaults write` script.
- **`.claude/` directory:** Not yet in chezmoi. Target-authoritative — will need special handling (Phase 6 polish item in next-actions.md §15).
- **`.npmrc`:** Check for auth tokens before deciding plain file vs. rbw template.
- **SteerMouse:** Still in use? Affects whether to invest in chezmoi management of `Device.smsetting`.
- **`secrets/awesometeam-*`:** Confirm stale before archiving in Phase 7.
- **`.logseq/git/`:** Check if this is config or state — migrate if config, skip if state.

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
| config-in-the-cloud/ audit   | MIGRATION.md §Source Audit                                              | Subfolder inventory                               |
| Ansible SSH config template  | `ansible-magic/.../base_ssh_config`                                     | Source for `~/.ssh/config`                        |
| Dev Environment Steps (from Notion) | [Dev Environment Steps](2026-02-26/Dev%20Environment%20Steps%20(from%20Notion).md) | Manual setup steps — feeds Phase 6.5 automation |


