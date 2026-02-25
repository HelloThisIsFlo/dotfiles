# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A [chezmoi](https://chezmoi.io) dotfiles repository for macOS (primary) with planned Linux support. Source state lives here (`~/.local/share/chezmoi/`), target state is `~/`. Remote: `git@github.com:HelloThisIsFlo/dotfiles.git`.

## Migration in progress

> **Temporary section.** Once migration completes, this is replaced with maintenance-mode operating instructions and a Claude Code assistant skill becomes the primary agent workflow. See MIGRATION.md §Post-Migration Transition.

This repo is migrating from Mackup symlinks to fully chezmoi-managed config. Current state:

- **Tracker:** `.research/MIGRATION.md` — the living migration document. Read it for full status, phase checklists, and what's broken.
- **~20 files still Mackup-symlinked** — `.gitconfig`, VS Code settings, secret env files, and others. Not yet in chezmoi.
- **Plist drift** — 5 plists show MM (modified-modified) status. Apps write runtime data into tracked files. These will be replaced by `defaults write` scripts.
- **Config is stale** — `.chezmoi.toml.tmpl` and `.install-password-manager.sh` still reference `bw` (old Bitwarden CLI). `rbw` is installed but not wired in.
- **Secrets not yet templated** — `rbw` is the decided tool but no templates use it yet.

**For agents:** When the user works on this repo, proactively check `.research/MIGRATION.md` for current phase status and suggest next migration steps if relevant to the task at hand. Be careful with `chezmoi apply` — plist drift means it can silently overwrite target changes.

## Key commands

```bash
chezmoi apply                  # render source → target (the main operation)
chezmoi edit <target-path>     # edit a managed file (resolves dot_ naming automatically)
chezmoi diff                   # preview what apply would change
chezmoi status                 # show managed files that differ from target
chezmoi data                   # dump template data (variables, OS info)
chezmoi cat <target-path>      # show what chezmoi would render (without applying)
chezmoi add <target-path>      # add a new file to management
chezmoi add --template <path>  # add as a Go template (.tmpl)
chezmoi re-add <target-path>   # sync target → source (ONLY for non-template plain files)
chezmoi doctor                 # diagnostic check
```

Git autoCommit is enabled — every `chezmoi add`/`chezmoi apply` creates a git commit automatically. autoPush is disabled.

## Architecture decisions (from .research/2026-02-25/decisions.md)

- **Secrets via rbw only** — Rust Bitwarden CLI with background agent. Template syntax: `{{ (rbw "item-name").data.password }}` or `{{ (rbwFields "item-name").field_name.value }}`. No age encryption, no GPG, no official `bw` CLI.
- **Workflow: edit → apply, not re-add** — `chezmoi re-add` destroys template logic in `.tmpl` files. Only use re-add on plain (non-template) files.
- **No age encryption for v1** — deferred until unattended apply or air-gapped servers are needed.

## Repo structure

```
.chezmoi.toml.tmpl              # chezmoi config template (secrets=error, autoCommit, delta diff, VS Code merge, rbw hook)
.install-password-manager.sh    # pre-hook: installs bw (being migrated to rbw) if missing
run_onchange_after_brew-bundle.sh.tmpl  # re-runs `brew bundle` when dot_Brewfile changes (darwin only)

dot_Brewfile                    # Homebrew bundle (taps, brews, casks)
dot_bashrc                      # bash → zsh trampoline
dot_vimrc                       # vim config
private_dot_zshrc               # main shell config (zsh, large, uses vim foldmarkers)
private_dot_zsh/                # zsh completions (docker, poetry)
dot_config/direnv/              # direnv config (load_dotenv = true)
dot_hierarchy                   # repo manifest (yaml, lists git repos and paths)

private_Library/                # macOS app preferences (Bartender, iStat Menus, Moom, Raycast, Clocker, etc.)
  Preferences/                  # plist files for app settings
  Application Support/          # Bartender menu bar image configs

.research/                      # reference material (not deployed by chezmoi)
  MIGRATION.md                  # living migration tracker — start here for current status
  README.md                     # master index with quick links
  cheatsheets/                  # 10 topic cheatsheets + INDEX.md
  2026-02-17/                   # session notes: migration assessment, original CLAUDE.md, plist tutorial
  2026-02-25/                   # session notes: decisions, next-actions, assistant-skill-rationale
```

## Chezmoi naming conventions (critical for this repo)

| Prefix/suffix | Meaning |
|---|---|
| `dot_` | becomes `.` in target path |
| `private_` | target gets `0600` permissions |
| `symlink_` | creates a symlink |
| `.tmpl` | Go template, rendered before placement |
| `run_onchange_after_` | script that re-runs when its content hash changes |
| `run_once_before_` | script that runs once during init |

## Editing guidelines

- **Never use `chezmoi re-add` on `.tmpl` files** — it replaces template logic with rendered output.
- **Plist files use textconv** — the config converts plists to XML via `plutil` for readable diffs. When editing plists, prefer `defaults write` in run scripts over directly managing plist files.
- **The `.research/` directory is reference material** — not deployed to target. Start with `MIGRATION.md` for current migration status. Contains cheatsheets (`cheatsheets/`) and session notes (`2026-02-17/`, `2026-02-25/`). Consult `2026-02-25/decisions.md` before changing secrets strategy or adding encryption.
- **The `.install-password-manager.sh` hook runs on every chezmoi command** — keep it fast and idempotent.
- **`dot_Brewfile` triggers brew bundle** — the run_onchange script includes a sha256sum of the Brewfile, so any edit causes `brew bundle` to re-run on next apply.
