# config-in-the-cloud Audit Notes — 2026-02-26

Session journal from the full audit of `~/config-in-the-cloud/`. Conclusions are in MIGRATION.md; this file preserves context for future reference.

## What we explored

### 1. Subfolder inventory

Ran `ls ~/config-in-the-cloud/` — 5 subfolders:
- `dotfiles/restored_via_mackup/` — 14 public dotfile symlinks (verified with `find ~ -maxdepth 1 -type l`)
- `dotfiles-secret/restored_via_mackup/` — 5 secret dotfile symlinks
- `dotfiles-binary/restored_via_mackup/` — app plists + Library data (Mackup copies, not symlinks)
- `dotfiles-binary/plist_human_readable/` — XML versions of binary plists (reference for Phase 5)
- `secrets/` — TLS certs, SSH keys, DigitalOcean tokens (partially stale)
- `ansible-magic/` — Ansible playbooks; SSH config template is the only live asset

### 2. Plist git history analysis

Ran `git log --oneline --all -- '*.plist'` in `~/config-in-the-cloud/` — 104 commits total.

**Key finding:** most plist commits are noise (macOS apps writing runtime data). The signal-to-noise ratio varies dramatically per app. We categorized each app's commits to determine which apps have real user config worth preserving vs. apps whose plists contain only transient data.

**To reproduce:** run the git log command above, then for each app grep for its bundle ID or app name. Compare with `defaults read <bundle-id>` output and the noise patterns documented in MIGRATION.md §Phase 5 Reference.

### 3. SSH config source

Found that `~/.ssh/config` is deployed by Ansible, not manually created:
- Template: `~/config-in-the-cloud/ansible-magic/ansible/roles/dev-machine/templates/base_ssh_config`
- 116 lines, one Jinja2 conditional (`{% if ansible_os_family == "Darwin" %}` for `UseKeychain`)
- The deployed file on disk matches the template output exactly — no manual edits to reconcile

### 4. Triage decisions

Applied the principle: **everything migrates unless there's a documented technical reason not to.** "Not actively used" is not a valid reason to skip — only "no real config to preserve" or "mutable runtime data only."

Notable decisions:
- `.spacemacs.d` — not actively used but 437 lines of invested config → migrate
- `.logseq` — complex directory, needed per-subdirectory analysis. Config files migrate, plugins dir skips (auto-downloadable), graphs skip (runtime). `git/` dir still TBD.
- `.ipython` — config file migrates, `history.sqlite` skips (runtime data)

### 5. Non-Mackup config discovered

Found 3 config files in `~/.config/` that were never managed by Mackup:
- `karabiner/karabiner.json` — keyboard remapping
- `linearmouse/linearmouse.json` — mouse settings
- `cheat/` — conf.yml + personal cheatsheets

These became Phase 3.5.

### 6. Notion "Dev Environment Steps"

Exported the manual setup guide from Notion. This documents the full from-scratch setup process (xcode CLI tools → brew → asdf → language installs → pip/npm/cargo/go tools → chezmoi → ansible → repos → antigen → vim plugins).

The goal (Phase 6.5) is to automate most of these steps as chezmoi run scripts using a `[data.tools]` pattern in `.chezmoi.toml.tmpl`.
