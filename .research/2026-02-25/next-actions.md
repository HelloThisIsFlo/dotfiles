# Chezmoi Repo — Next Actions

Based on decisions from sessions on 2026-02-24 and 2026-02-25. Reference material: 10 cheat sheets, decisions.md.

---

## Phase 1: Clean foundation

These get you from "existing repo with stale config" to "working baseline with the right tools."

### 1. Install rbw and configure it

You're moving from `bw` (official Bitwarden CLI) to `rbw`. This needs to happen before anything else because templates will depend on it.

```bash
brew install rbw
rbw config set email flo@kempenich.ai
rbw register        # one-time device registration
rbw unlock          # type master password, starts the agent
```

Set lock timeout to 12 hours so you type the password once per morning:

```bash
rbw config set lock-timeout 43200
```

On Mac, configure `pinentry-mac` for the GUI dialog:

```bash
brew install pinentry-mac
rbw config set pinentry pinentry-mac
```

### 2. Rewrite `.chezmoi.toml.tmpl`

Your current config template has outdated sections. Start fresh with this structure:

- Add `[data]` section with `promptChoiceOnce` for `machine_type` (personal/work/server), `promptBoolOnce` for `is_headless`, `promptStringOnce` for `email`
- Keep `[add] secrets = "error"` — safety net against committing plaintext secrets
- Keep `[git] autoCommit = true`, `autoPush = false`
- Keep `[diff] command = "delta"` — remove the `pager` line (delta is already a pager)
- Remove the `[[textconv]]` plist section — you're using `defaults write`, not managing plist files
- Keep `[merge]` VS Code setup — rarely used but harmless
- Update `[hooks.read-source-state.pre]` to point to the rewritten install script (step 3)
- Skip `[age]` and `encryption` for now (Decision #4: no age for v1)

### 3. Rewrite `.install-password-manager.sh`

The current script installs `bw`. Rewrite it for `rbw`:

- Check for `rbw` with `command -v rbw`, exit 0 if found
- macOS: `brew install rbw`
- Linux: decide on install method (cargo, package manager, or pre-built binary)
- Keep it fast and idempotent — this runs on every chezmoi command

### 4. Run `chezmoi init` on your current machine

This re-renders the config template, asks the prompt questions for the first time, and generates a fresh `chezmoi.toml`.

```bash
chezmoi init --prompt
```

Verify with `chezmoi data` that your variables are set correctly.

---

## Phase 2: First files under management

Start small. Get the workflow (`chezmoi edit` → `chezmoi apply`) into muscle memory before adding complexity.

### 5. Add `.gitconfig` as a template

This is the obvious first file — it has your name and email, which vary per machine.

```bash
chezmoi add --template ~/.gitconfig
chezmoi edit ~/.gitconfig
```

Replace hardcoded values with template variables: `{{ .email }}`, `"Flo Kempenich"`, delta as diff tool. See the real-world `.gitconfig.tmpl` example in the templates cheat sheet.

### 6. Add `.ssh/config` as a template

Another natural fit — different hosts, keys, and `IdentityFile` paths per machine type. Use `.chezmoiignore` to skip the entire `.ssh/` directory on machines that shouldn't have certain keys.

### 7. Add shell config (`.zshrc` or equivalent)

Start with the parts that are the same everywhere. Templatise anything that varies by machine (PATH additions, tool-specific config that only exists on certain machines). Use `lookPath` checks for progressive enhancement:

```
{{ if lookPath "bat" }}alias cat="bat"{{ end }}
```

---

## Phase 3: Secrets

Once the basic workflow is solid and `rbw` is working, start wiring secrets into templates.

### 8. Templatise files that contain secrets

Identify files with API tokens, credentials, or passwords. Convert them to templates using `rbw`:

```
{{ (rbw "item-name").data.password }}
{{ (rbwFields "item-name").field_name.value }}
```

Good first candidates: git credential helpers, API tokens in shell env, app-specific config files with auth tokens.

### 9. Organise secrets in Bitwarden

Create a consistent naming scheme in your Bitwarden vault for items that chezmoi will reference. The name you pass to `rbw "..."` is the item name in your vault. If you have duplicates, use folder scoping: `rbw "item-name" --folder "chezmoi"`.

---

## Phase 4: macOS preferences

### 10. Create a `defaults write` run script

Build a `run_onchange_after_macos-defaults.sh.tmpl` script for your macOS preferences. Start with the settings you always configure on a new Mac (Dock, keyboard, Finder, screenshots, etc.). Use the macOS preferences cheat sheet as a guide.

Guard it with a macOS check at the top:

```bash
{{ if ne .chezmoi.os "darwin" }}
exit 0
{{ end }}
```

### 11. Add app-specific preferences scripts

Separate scripts for apps you care about (Terminal/iTerm, VS Code settings that aren't synced, etc.). Each one as a `run_onchange_after_` so it only re-runs when you change the settings.

---

## Phase 5: Multi-machine

### 12. Test on a second machine

Clone your repo on another machine (or a VM/container) and run:

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply <your-github-username>
```

This is the real test. The hook should install `rbw`, the prompts should ask machine type, and everything should apply cleanly. Fix whatever breaks.

### 13. Add a headless Linux machine

This exercises the `is_headless` and OS-specific paths. Configure `rbw` with `pinentry-tty` instead of `pinentry-mac`. Verify `.chezmoiignore` correctly skips GUI-only files.

---

## Phase 6: Polish (when you feel like it)

### 14. Add `.chezmoidata/packages.yaml`

List your Homebrew packages and casks. Create a `run_onchange_after_brew-bundle.sh.tmpl` that installs them. This makes "set up a new Mac" a single command.

### 15. Add `~/.claude/` directory as plain files

Add your Claude config, skills, and `claude.md` as plain (non-template) files. These are target-authoritative — external tools and your own edits modify the destination, not the source.

- `chezmoi add ~/.claude/` to get everything into the repo
- Use `.chezmoiignore` to skip on machines that don't need it: `{{ if eq .machine_type "server" }}.claude/**{{ end }}`
- After editing skills or after the Claude CLI updates config, run `chezmoi re-add ~/.claude/` to sync back to source
- Never apply without diffing first — `chezmoi apply` would silently overwrite un-re-added target changes

### 16. Set up externals for tool plugins

If you use shell plugins, editor configs, or other things pulled from git repos, use `.chezmoiexternal.toml` instead of managing them as files. See the externals cheat sheet.

### 17. Build a chezmoi assistant skill for Claude Code

A skill that understands your repo and helps you keep it tidy. Encode:

- **File flow direction** — which directories are source-authoritative (most config) vs target-authoritative (`.claude/`), possibly via a manifest file in the repo
- **Triage workflow** — run `chezmoi status`/`chezmoi diff`, classify each change as "apply", "re-add", or "conflict", present a summary (the health check)
- **Safety checks** — always re-add target-authoritative files before apply, warn if apply would overwrite local changes
- **Semantic commits** — group related changes and commit with meaningful messages instead of one big "update dotfiles"

Start as a Claude Code skill. If you ever want it in a chat UI, the skill becomes the spec for an MCP server — but there's a 99% chance the skill is enough.

### 18. Revisit age encryption (if needed)

Only add age if you hit one of the triggers from Decision #4: unattended `chezmoi apply` on a server, air-gapped machines, or CI/CD pipelines. Until then, rbw-only is simpler.

---

## Not now (backlog)

- **Touch ID for rbw** — custom Swift pinentry that stores the master password in macOS Keychain behind Touch ID. 3-5 days of work, 6-12 months out. Current "type password once per morning" is fine.
- **Chezmoi MCP server** — only if you find yourself wanting the assistant skill's capabilities outside Claude Code. The skill is the spec; building the MCP is mechanical wrapping of shell commands.
- **Age encryption** — deferred until a concrete need arises.
- **Ansible/cloud-init integration** — only if server fleet grows beyond a handful.

---

## Reference material

All in the `../cheatsheets/` directory:

| Sheet | File |
|---|---|
| Templates | `templates.md` |
| Run Scripts | `run-scripts.md` |
| Secrets (rbw + age) | `secrets.md` |
| Configuration | `config.md` |
| Data Sources | `data-sources.md` |
| macOS Preferences | `macos-preferences.md` |
| Naming Conventions | `naming.md` |
| Externals | `externals.md` |
| Tips & Escape Hatches | `tips.md` |
| Hooks | `hooks.md` |
| Architecture Decisions | `decisions.md` |
