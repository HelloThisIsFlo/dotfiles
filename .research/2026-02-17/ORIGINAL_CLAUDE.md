# Chezmoi Migration Project

## What This Project Is

Flo is migrating his Mac dotfiles management from **Mackup** to **Chezmoi**. He started 6-8 months ago but never finished, so things are in a half-migrated state. This workspace tracks the migration plan, research, and tutorials.

**Important**: Flo wants to understand before acting. Always explain what you're doing and why. Don't modify files without explicit approval.

---

## Key Locations

| What | Path |
|---|---|
| **Chezmoi source** | `~/.local/share/chezmoi/` |
| **Chezmoi source repo** | `git@github.com:HelloThisIsFlo/dotfiles.git` |
| **Chezmoi config** | `~/.config/chezmoi/chezmoi.toml` |
| **Mackup storage (public)** | `~/config-in-the-cloud/dotfiles/restored_via_mackup/` |
| **Mackup storage (secrets)** | `~/config-in-the-cloud/dotfiles-secret/restored_via_mackup/` |
| **Mackup storage (binary/plists)** | `~/config-in-the-cloud/dotfiles-binary/restored_via_mackup/` |
| **Mackup configs** | `~/config-in-the-cloud/*/mackup_config/` |
| **This workspace** | `~/Work/Private/Agent Workspaces/Claude/ChezMoi/` |

`config-in-the-cloud` is a real directory (Synology Drive synced), not a symlink.

---

## Files In This Workspace

- **`migration-status.md`** — Full status document: what's managed by chezmoi, what's still Mackup symlinks, what's broken, the plist question, and suggested next steps.
- **`plist-chezmoi-tutorial.html`** — Interactive HTML tutorial teaching how `run_onchange_` scripts work for managing macOS plists. Open in browser. Has 4 sections: The Problem, The Solution, Day-to-Day workflow, Real Examples, When Not To.

---

## Current State Summary

### Chezmoi manages (74 files, working):
- Shell: `.zshrc`, `.bashrc`, `.bash_logout`, `.zsh/` (docker completions, poetry)
- Editor: `.vimrc`
- Dev: `.Brewfile` + lockfile, `.config/direnv/direnv.toml`
- Custom: `.hierarchy`
- Mac app plists: Bartender (prefs + BMP images), iStat Menus (4 plists), Mos, Ice, Moom, Raycast, Clocker, VLC, Moom receipt
- Script: `run_onchange_after_brew-bundle.sh.tmpl` (runs `brew bundle` when Brewfile changes)

### Chezmoi config highlights:
- `autoCommit = true` (auto-commits on every add/apply)
- `autoPush` is commented out (manual push)
- `delta` as diff pager
- `plutil` textconv for plist diffs (binary → XML for `cm diff`)
- Bitwarden hook: auto-installs `bw` CLI if missing
- `secrets = "error"` — blocks accidentally adding secrets
- VS Code as merge editor

### Chezmoi aliases (from `.zshrc`):
```bash
alias cm=chezmoi
alias cmbrew="cm edit --apply ~/.Brewfile && cm apply ~/brew-bundle.sh"
```

### Still symlinked by Mackup (needs migration):

**Public dotfiles** (from `dotfiles/restored_via_mackup/`):
- `~/.gitconfig`, `~/.gitignore_global`
- `~/.tmux.conf`, `~/.tool-versions`, `~/.npmrc`, `~/.asdfrc`
- `~/.ideavimrc`, `~/.ansible.cfg`, `~/.pythonrc`
- `~/.amethyst.yml`, `~/.carbon-now.json`
- `~/.logseq/`, `~/.spacemacs.d/`, `~/.ipython/` (directories)
- `~/.config/cheat`, `~/.config/linearmouse`, `~/.config/karabiner`
- `~/.config/terminator/config` (Linux only)
- `Library/Application Support/Charles`, `Library/Application Support/Code/User/{settings.json, snippets}`, `Library/Application Support/Code - Insiders/User/{settings.json, snippets}`
- `Library/Preferences/com.xk72.charles.config`

**Secret dotfiles** (from `dotfiles-secret/restored_via_mackup/`):
- `~/.secrets.env`, `~/.tadl-pass`, `~/.tadl-minion`, `~/.cli_chat.json`
- `~/.aws/` (directory)
- `~/.config/exercism`

All symlinks are healthy (none dangling).

### Broken / needs attention:
1. **Ice.plist** (`DA` status) — deleted from chezmoi source but file exists on disk. Fix: `chezmoi add ~/Library/Preferences/com.jordanbaird.Ice.plist`
2. **Plist drift** (`MM` status) — iStat Menus status, Moom, Raycast, Bartender constantly drift due to runtime data (GPS, timestamps, window positions)
3. **Stale Mackup copies** — `dotfiles/restored_via_mackup/` has old copies of `.vimrc`, `.zshrc`, `.hierarchy`, `.zlogin`, `.zprofile`, `.profile` that chezmoi now owns

---

## Critical Research Findings

### Mackup is broken on macOS 14+ (Sonoma)
Apple changed how `cfprefsd` handles symlinks in `~/Library/Preferences` while fixing a CVE. Apps now replace symlinks with real files when writing preferences. This is a known, unfixed issue (github.com/lra/mackup/issues/1924, 134 comments). **Going back to Mackup for plist management is not viable.**

### The plist solution: `run_onchange_` scripts
The chezmoi-native approach for volatile plists:
1. **Stop tracking the plist file** (`chezmoi forget`)
2. **Write a `run_onchange_after_configure-APPNAME.sh` script** containing `defaults write` commands for only the keys you care about
3. Chezmoi runs the script only when its contents change (hash-based)
4. App runtime noise never triggers anything — chezmoi doesn't track the plist file

This is what the chezmoi maintainer himself uses. See `plist-chezmoi-tutorial.html` for a full interactive walkthrough.

### How to discover plist keys
```bash
defaults read com.example.app > /tmp/before.txt
# (change a setting in the app's UI)
defaults read com.example.app > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt
```
Or use `prefsniff` (`brew install prefsniff`) to auto-detect.

### Chezmoi's textconv limitation
The `[[textconv]]` config with `plutil` only affects `cm diff` display. It does NOT affect what gets stored in the source repo (still binary blobs) and does NOT filter runtime keys during `add`/`re-add`. Confirmed by chezmoi maintainer in github.com/twpayne/chezmoi/discussions/4308.

---

## Migration Plan (agreed direction, not yet executed)

### Step 1: Clean up chezmoi's current state
- Re-add Ice.plist (fix `DA`)
- `cm re-add` or `cm forget` the 4 noisy plists
- Get `cm status` clean

### Step 2: Triage Mackup symlinks
- Go through each symlink and decide: **migrate to chezmoi** / **drop** / **handle separately (secrets)**
- Flo needs to decide which tools he still uses (Amethyst? Spacemacs? Carbon Now? etc.)

### Step 3: Migrate public dotfiles
For each file to migrate:
```bash
cp -L ~/.gitconfig ~/.gitconfig.real && mv ~/.gitconfig.real ~/.gitconfig
chezmoi add ~/.gitconfig    # (use --template for per-machine files like .gitconfig)
```

### Step 4: Handle secrets
Options: Bitwarden templates (hook already set up), age encryption, or keep `dotfiles-secret` as separate synced storage

### Step 5: Migrate volatile plists to `run_onchange_` scripts
One app at a time. Suggested order:
1. Mos (~4 keys, zero noise, perfect first attempt)
2. Moom (~10 keys, medium complexity)
3. iStat Menus (noisiest, big win when done)
4. Raycast (use Raycast's own export for extensions)
5. Bartender (decide how much to automate vs. manual)
6. Clocker (test if stable first — might not need a script)

### Step 6: Clean up
- Remove stale files from `config-in-the-cloud/*/restored_via_mackup/`
- Archive or delete old Mackup configs

---

## Chezmoi Quick Reference

```bash
cm status          # What's out of sync
cm diff            # Full diff of pending changes
cm apply           # Apply source state to home dir
cm add <file>      # Add a file to chezmoi management
cm add --template  # Add as template (for per-machine files)
cm edit <file>     # Edit the source version
cm managed         # List all managed files
cm forget <file>   # Stop managing (keeps target file on disk)
cm re-add <file>   # Update source from current target state
cm doctor          # Health check
cm cd              # cd into chezmoi source dir
cm data            # Dump all template variables
cmbrew             # Edit + apply Brewfile, run brew bundle
```

### Chezmoi naming conventions
- `dot_` → `.` (dot files)
- `private_` → permissions 0600/0700
- `executable_` → executable bit
- `exact_` → directory fully owned (removes unmanaged files)
- `symlink_` → create symlink
- `.tmpl` suffix → Go template
- `run_onchange_` prefix → run script when contents change
- `run_onchange_after_` → run after file updates
- `run_onchange_before_` → run before file updates

### Chezmoi config file
`~/.local/share/chezmoi/.chezmoi.toml.tmpl`:
```toml
[add]
    secrets = "error"
[git]
    autoCommit = true
[diff]
    command = "delta"
    pager = "delta"
[[textconv]]
    pattern = "**/*.plist"
    command = "plutil"
    args = ["-convert", "xml1", "-o", "-", "-"]
[hooks.read-source-state.pre]
    command = ".local/share/chezmoi/.install-password-manager.sh"
```
