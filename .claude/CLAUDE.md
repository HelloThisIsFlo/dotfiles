# CLAUDE.md

> **Note:** The `CLAUDE.md` at the repo root is managed by chezmoi and deployed to `~/CLAUDE.md`. It is NOT instructions for working in this repo. Ignore it. **This file** (`.claude/CLAUDE.md`) contains the repo-specific instructions.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A [chezmoi](https://chezmoi.io) dotfiles repository for macOS (primary) with planned Linux support. Source state lives here (`~/.local/share/chezmoi/`), target state is `~/`. Remote: `git@github.com:HelloThisIsFlo/dotfiles.git`.

## Migration in progress

> **Temporary section.** Once migration completes, this is replaced with maintenance-mode operating instructions and a Claude Code assistant skill becomes the primary agent workflow. See MIGRATION.md §Post-Migration Transition.

This repo is migrating from Mackup symlinks to fully chezmoi-managed config. Current state:

- **Tracker:** `.research/MIGRATION.md` — the living migration document. Read it for full status, phase checklists, and what's broken.
- **~20 files still Mackup-symlinked** — `.gitconfig`, VS Code settings, secret env files, and others. Not yet in chezmoi.
- **Plist drift** — 5 plists show MM (modified-modified) status. Apps write runtime data into tracked files. These will be replaced by `defaults write` scripts.
- **Secrets not yet templated** — `rbw` is the decided tool but no templates use it yet.

**For agents:** When the user works on this repo, proactively check `.research/MIGRATION.md` for current phase status and suggest next migration steps if relevant to the task at hand. Be careful with `chezmoi apply` — plist drift means it can silently overwrite target changes. **After completing any migration work, update the Progress Checklist in `.research/MIGRATION.md` — check off finished items, update the Current State table, and add an entry to the Completed Items log.**

## CLI exploration (parallel track)

Separate from the migration: evaluating and adopting modern CLI tools for an upgraded terminal experience. Tracker: `.research/CLI-EXPLORATION.md`. This is an ongoing list — when the user mentions wanting to try a new tool, add it there. When a tool is configured and decided on, move it to the "Integrated" section. Don't confuse exploration work with migration work.

## Key commands

```bash
chezmoi apply                  # render source → target (the main operation)
chezmoi edit <target-path>     # edit a managed file (resolves dot_ naming automatically)
chezmoi diff                   # preview what apply would change
chezmoi status                 # show managed files that differ from target (⚠️ see status rules below)
chezmoi data                   # dump template data (variables, OS info)
chezmoi cat <target-path>      # show what chezmoi would render (without applying)
chezmoi add <target-path>      # add a new file to management
chezmoi add --template <path>  # add as a Go template (.tmpl)
chezmoi re-add <target-path>   # sync target → source (ONLY for non-template plain files)
chezmoi doctor                 # diagnostic check
```

Git autoCommit is **disabled** (off by default — group related changes into semantic commits).

### `chezmoi status` — how to read it (agents get this wrong constantly)

Output is `XY path/to/file`. The columns are **NOT** source vs target. They are:

- **X** = last-applied state vs disk — "did something change the file since chezmoi last wrote it?"
- **Y** = disk vs source (what chezmoi would render) — "would `chezmoi apply` change this file?"

| Code | Meaning | Action |
|------|---------|--------|
| ` M` | Source is ahead, disk is untouched | `chezmoi apply` — **safe, no conflict** |
| `MM` | Disk was edited AND differs from source | **Conflict.** `chezmoi diff` first, then `apply` (keep source) or `re-add` (keep disk) or `merge` (keep both) |
| ` A` | New file in source, doesn't exist on disk | `chezmoi apply` to create |
| `M ` | Cannot happen in practice — chezmoi hides files where disk matches source |

**Key trap:** ` M` does NOT mean "target has edits source doesn't know about." It means the opposite — source has updates ready to apply. Full details: `.research/cheatsheets/chezmoi/chezmoi-status.md`.

## Architecture decisions (from .research/2026-02-25/decisions.md)

- **Secrets via rbw only** — Rust Bitwarden CLI with background agent. Template syntax: `{{ (rbw "item-name").data.password }}` or `{{ (rbwFields "item-name").field_name.value }}`. No age encryption, no GPG, no official `bw` CLI.
- **Workflow: edit → apply, not re-add** — `chezmoi re-add` destroys template logic in `.tmpl` files. Only use re-add on plain (non-template) files.
- **No age encryption for v1** — deferred until unattended apply or air-gapped servers are needed.

## Repo structure

```
.chezmoi.toml.tmpl              # chezmoi config (data prompts, secrets=error, delta diff, VS Code merge, hooks)
.chezmoiignore                  # files chezmoi should not manage
.chezmoidata/                   # template data files (watch_dirs.yaml)

.chezmoiscripts/                # run_onchange scripts (numbered for ordering)
  01-macos/                     # brew bundle (runs first — installs fish, etc.)
  02-fish/                      # Fisher plugin install + Tide config

.hooks/                         # chezmoi hook scripts (folder-based dispatcher)
  run-hooks.sh                  # dispatcher — runs all executable scripts in hook subdirs
  read-source-state.pre/        # runs before reading source (password manager check)
  status.pre/                   # runs before status (watch-dirs scan)

.research/                      # reference material (not deployed by chezmoi)
  MIGRATION.md                  # living migration tracker
  cheatsheets/                  # topic cheatsheets + INDEX.md
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
- **The `.hooks/` dispatcher runs on every chezmoi command** (configured in `.chezmoi.toml.tmpl`) — hook scripts in subdirs like `read-source-state.pre/` must be fast and idempotent.
- **`dot_Brewfile` triggers brew bundle** — the run_onchange script includes a sha256sum of the Brewfile, so any edit causes `brew bundle` to re-run on next apply.
- **To add a Fish plugin** — add the plugin line to `dot_config/private_fish/fish_plugins` and run `chezmoi apply`. Fisher picks it up automatically.
