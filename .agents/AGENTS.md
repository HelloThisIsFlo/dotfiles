# AGENTS.md

> **Note:** This file is the repo-specific instruction source. Claude Code loads it through `.claude/CLAUDE.md`; Codex loads it through global fallback discovery for `.agents/AGENTS.md`.

This file provides guidance to agents when working with code in this repository.

## What this repo is

A [chezmoi](https://chezmoi.io) dotfiles repository for macOS (primary) with planned Linux support. Source state lives here (`~/.local/share/chezmoi/`), target state is `~/`. Remote: `git@github.com:HelloThisIsFlo/dotfiles.git`.

## ⚠️ THIS IS A PUBLIC REPO — info-leak guardrail

The GitHub remote is **public** (intentionally — secrets are kept out of source via `rbw` templates and `secrets = "error"`). But info disclosure beyond credentials can still happen by accident. Before any of the following actions, **pause and check** whether the content might leak something the user wouldn't want public:

- **Onboarding a new file** to chezmoi management (`chezmoi add` or hand-creating a source file)
- **Writing a new cheatsheet or research doc** in `.research/`
- **Committing** — even files the user added themselves. Review the diff for leaks before `git commit`.

**What to actively flag and ask about:**
- Credentials, tokens, API keys, private keys, account IDs (these should never land here — `secrets = "error"` blocks most but won't catch everything)
- Usernames for third-party services that differ from the user's public identity (e.g. seedbox/forum/torrent accounts)
- Hostnames / identifiers not already in public DNS
- Candid opinions about named people, companies, or vendors
- Health / financial / legal info
- **Private-life context beyond names + topology.** Topology is fine ("DadHome cluster has HAOS + NAS"). Private-life narrative is not: notes describing what a family member did / said / believes, specific personal events, anecdotes that paint a portrait of the user's relationships or daily life. The test: does this read like "user's infra reference doc" or "user's personal journal that happens to be on GitHub"?

**What is fine to leave (no need to ask):**
- The user's public identity: `Flo Kempenich`, `flo@kempenich.ai`, `HelloThisIsFlo`
- Public-DNS hostnames (`kempenich.dev`, `kempenich.ai`)
- Tunnel UUIDs (identifiers, not credentials — the `.json` secret stays unmanaged)
- Tailscale tailnet name (semi-public anyway)
- Internal LAN IPs (`192.168.x.x` — non-routable)
- Cluster codenames (TheMac, TheHome, DadHome) and the public service mappings
- First-name-only references already in `.research/2026-02-25/`

**When unsure, ASK.** Cheap to confirm, expensive to scrub from public history.

## Migration in progress

> **Temporary section.** Once migration completes, this is replaced with maintenance-mode operating instructions and an assistant skill becomes the primary agent workflow. See MIGRATION.md §Post-Migration Transition.

This repo is migrating from Mackup symlinks to fully chezmoi-managed config. Current state:

- **Tracker:** `.research/MIGRATION.md` — the living migration document. Read it for full status, phase checklists, and what's broken.
- **~20 files still Mackup-symlinked** — `.gitconfig`, VS Code settings, secret env files, and others. Not yet in chezmoi.
- **Plist drift** — 5 plists show MM (modified-modified) status. Apps write runtime data into tracked files. These will be replaced by `defaults write` scripts.
- **Secrets not yet templated** — `rbw` is the decided tool but no templates use it yet.

**For agents:** When the user works on this repo, proactively check `.research/MIGRATION.md` for current phase status and suggest next migration steps if relevant to the task at hand. Be careful with `chezmoi apply` — plist drift means it can silently overwrite target changes. **After completing any migration work, update the Progress Checklist in `.research/MIGRATION.md` — check off finished items, update the Current State table, and add an entry to the Completed Items log.**

## CLI exploration (parallel track)

Separate from the migration: evaluating and adopting modern CLI tools for an upgraded terminal experience. Tracker: `.research/CLI-EXPLORATION.md`. This is an ongoing list — when the user mentions wanting to try a new tool, add it there. When a tool is configured and decided on, move it to the "Integrated" section. Don't confuse exploration work with migration work.

## Zsh → Fish migration (parallel track)

Porting the interactive shell from zsh (oh-my-zsh + antigen) to fish. Tracker: `.research/FISH-MIGRATION.md`. The bulk of aliases/functions/abbreviations are already migrated. Remaining work is mostly filling placeholders and completions. Don't confuse with the chezmoi migration (which is about *how* files are managed) or CLI exploration (which is about *which* tools to use) — this track is about translating the zsh shell config to fish equivalents.

## Active WIP tracker

Some dirty files are intentional WIP. Tracker: `.research/WIP.md`.

- If paths listed there are dirty, assume that is expected.
- Do not ask Flo to re-explain those WIP changes every session.
- At the end of repo work, briefly ask whether to keep, update, or clear the tracker if it looks stale.

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

## Secrets workflow (rbw) — conventions

> How secrets actually get created, named, stored, and consumed in this repo. The Architecture decision above is the *what*; this is the *how*.

### 🗂️ Vault layout
- **All chezmoi-managed secrets live in the rbw folder `chezmoi`.** Keeps them grouped + greppable (`rbw list --fields name,folder | grep chezmoi`).
- **Item naming:** kebab-case, service-first, purpose-suffixed. Examples: `github-pat`, `fastmail-api`, `fastmail-apppassword`, `ntfy-topic`.
- **One secret per item** (value in the `password` field) is the default. Use one item with custom fields only when several secrets are genuinely one credential set.

### ➕ Creating secrets (non-interactively)
- **Exact value → pipe to stdin** (the reliable headless method):
  ```bash
  echo "the-secret-value" | rbw add <name> --folder chezmoi
  ```
  For values with shell-hostile chars (`$`, backticks, quotes), drive it from Python so nothing hits the shell:
  ```python
  subprocess.run(['rbw','add',name,'--folder','chezmoi'], input=val+'\n', text=True)
  ```
- **`rbw add` bare needs a TTY** — in a non-interactive shell it silently skips its editor and creates an *empty* entry. Always pipe.
- **`rbw generate <len> <name> --folder chezmoi`** makes a *random* value — only for brand-new generated creds, never for reproducing an existing secret.
- **Custom fields can't be created via the CLI** — add those in the web/desktop vault. rbw can *read* them (`rbwFields`), not write them.
- After any create/change: **`rbw sync`** (pushes to server).

### 📝 Using secrets in templates
- It's the chezmoi **template function** `rbw`, distinct from the CLI `rbw get`:
  ```
  {{ (rbw "github-pat").data.password }}     # password field
  {{ (rbw "fastmail-apppassword").data.username }}   # also: .username, .notes, .uris, .totp
  {{ (rbwFields "some-item").field_name.value }}     # custom fields
  ```
- **Verify a render without applying** (prints the value — only do in a private shell):
  ```bash
  chezmoi execute-template '{{ (rbw "github-pat").data.password }}'
  ```

### 🔒 Onboarding a secret-bearing file (the only correct flow)
`secrets = "error"` runs a gitleaks scan → **`chezmoi add` on any file containing a secret is BLOCKED.** So:
1. Extract each secret value, create rbw items (folder `chezmoi`) via the stdin method above.
2. **Hand-author the `.tmpl` source** — copy the file verbatim, swap each secret value for its `{{ (rbw …) }}` call. Never `chezmoi add` it. The source therefore never holds plaintext → the guard stays `error` the whole time.
3. `chezmoi apply`, then diff rendered-vs-original to confirm byte-identical.
- ⚠️ **Before onboarding, check the file isn't mostly app *runtime state*** (recent-session lists, trusted-folder lists, device names). Those drift constantly and often carry private-life content — see the info-leak guardrail. A file mixing authored config + app state is usually a poor chezmoi candidate.

### 🩺 rbw state model + gotchas
- Three independent layers — don't conflate:
  - **`rbw unlock`** — decrypts the *local* DB. Reads (`get`/`list`) work offline after this.
  - **`rbw sync`** — talks to the *server*. Needed for writes + refresh.
  - **`rbw login`** — refreshes the *server session token*.
- **`rbw sync` failing with `missing field access_token`** = stale local auth state. Fix: **`rbw purge`** (wipes the *local* DB only — server vault untouched), then `rbw login` + `rbw sync`. Unlock alone won't fix it.
- **rbw config on macOS** lives at `~/Library/Application Support/rbw/config.json` (Apple dirs, **not** XDG `~/.config/`). It's managed here (`private_Library/Application Support/private_rbw/config.json`, plain file — email intentionally hardcoded, not templated). `device_id`, agent logs, and the `~/Library/Caches/rbw/` vault cache are **not** managed (per-machine / regenerable).

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
