# Mackup to Chezmoi Migration - Status & Next Steps

## Where Things Live Today

```
~/.local/share/chezmoi/          # Chezmoi source (git: HelloThisIsFlo/dotfiles)
~/config-in-the-cloud/
  dotfiles/restored_via_mackup/          # Mackup storage (public dotfiles)
  dotfiles-secret/restored_via_mackup/   # Mackup storage (secrets: AWS, env vars, etc.)
  dotfiles-binary/restored_via_mackup/   # Mackup storage (binary plists, Bartender BMPs)
```

---

## What Chezmoi Already Manages (working)

Real copies in your home dir. No symlinks.

| What | Source in chezmoi |
|---|---|
| `.zshrc` | `private_dot_zshrc` |
| `.bashrc`, `.bash_logout` | `dot_bashrc`, `dot_bash_logout` |
| `.vimrc` | `dot_vimrc` |
| `.Brewfile` + lockfile | `dot_Brewfile` |
| `.hierarchy` | `dot_hierarchy` |
| `.config/direnv/direnv.toml` | `dot_config/direnv/direnv.toml` |
| `.zsh/` (docker completions, poetry) | `private_dot_zsh/` |
| `brew-bundle.sh` | `run_onchange_after_brew-bundle.sh.tmpl` |
| **Mac app prefs**: Bartender, iStat Menus (x4), Mos, Ice, Moom, Raycast, Clocker, VLC, Bartender BMPs, Moom receipt | `private_Library/...` |

### Your shortcuts (from `.zshrc`)

```bash
alias cm=chezmoi
alias cmbrew="cm edit --apply ~/.Brewfile && cm apply ~/brew-bundle.sh"
```

### Config highlights (`~/.config/chezmoi/chezmoi.toml`)

- `autoCommit = true` (auto-commits on every add/apply)
- `autoPush` commented out (manual push)
- `delta` as diff pager
- `plutil` textconv for plist diffs (converts binary to XML for `cm diff`)
- Bitwarden hook (auto-installs `bw` if missing)
- `secrets = "error"` (blocks accidental secret addition)

---

## What's Still Symlinked by Mackup

### Public dotfiles (`dotfiles/restored_via_mackup/`)

| Symlink | Notes |
|---|---|
| `~/.gitconfig` | Core config |
| `~/.gitignore_global` | |
| `~/.tmux.conf` | |
| `~/.tool-versions` | asdf versions |
| `~/.npmrc` | |
| `~/.ideavimrc` | JetBrains vim bindings |
| `~/.ansible.cfg` | If still used |
| `~/.asdfrc` | |
| `~/.pythonrc` | 1 byte |
| `~/.amethyst.yml` | If still used |
| `~/.carbon-now.json` | If still used |
| `~/.logseq/` | Directory |
| `~/.spacemacs.d/` | Directory - if still used |
| `~/.ipython/` | Directory |
| `~/.config/cheat` | If still used |
| `~/.config/linearmouse` | |
| `~/.config/karabiner` | |
| `~/.config/terminator/config` | Linux only |
| `Library/Application Support/Charles` | Charles proxy |
| `Library/Application Support/Code/User/{settings.json, snippets}` | VS Code |
| `Library/Application Support/Code - Insiders/User/{settings.json, snippets}` | VS Code Insiders |
| `Library/Preferences/com.xk72.charles.config` | Charles plist |

### Secret dotfiles (`dotfiles-secret/restored_via_mackup/`)

| Symlink | What |
|---|---|
| `~/.secrets.env` | Environment secrets |
| `~/.tadl-pass`, `~/.tadl-minion` | App credentials |
| `~/.cli_chat.json` | CLI chat config |
| `~/.aws/` | AWS credentials |
| `~/.config/exercism` | Exercism API token |

All symlinks are healthy (none dangling).

---

## What's Broken or Needs Attention

### 1. Ice.plist missing from source

`chezmoi status` shows `DA` for `com.jordanbaird.Ice.plist` — deleted from chezmoi source but file exists on disk.
**Fix**: `chezmoi add ~/Library/Preferences/com.jordanbaird.Ice.plist`

### 2. Plist drift (the big question — see next section)

4 plists show `MM` (modified in both source and target): iStat Menus status, Moom, Raycast, Bartender. These apps write runtime data (GPS, timestamps, window state) into the same plist as user config.

### 3. Stale Mackup copies

`dotfiles/restored_via_mackup/` still has old copies of `.vimrc`, `.zshrc`, `.hierarchy`, `.zlogin`, `.zprofile`, `.profile` — files chezmoi now owns. Dead weight, harmless.

---

## The Plist Question (Deep Dive)

This is the hardest part. You mentioned wanting **one tool** and that chezmoi feels less good than your old `plutil -p` human-readable workflow. Here's what I found:

### What chezmoi actually supports for plists

- **`textconv`** (what you have now): makes `cm diff` readable by converting binary plists to XML. But it **only affects diff display** — the source repo still stores binary blobs. Confirmed by the chezmoi maintainer ([discussion #4308](https://github.com/twpayne/chezmoi/discussions/4308)).
- **No smudge/clean filters**: chezmoi cannot strip runtime keys during `add`/`re-add`. There's no equivalent of git's clean filter for plists.
- **`modify_` scripts**: can surgically manage specific keys using `PlistBuddy` or `defaults write`. The file itself isn't tracked — only the keys you specify. Eliminates noise but requires per-app reverse-engineering.
- **`run_onchange_` scripts with `defaults write`**: this is what the chezmoi maintainer himself uses for macOS settings. No plist file tracked at all — just a script of `defaults write` commands that reruns when you change it.

### What the community actually does

The consensus is: **don't track volatile plists as files**. Instead:
1. Use `run_onchange_` scripts with `defaults write` for the settings you care about
2. Leave the rest unmanaged (apps recreate their own defaults)
3. A tool called [prefsniff](https://github.com/zcutlip/prefsniff) can watch a plist and auto-generate the `defaults write` commands for changes you make in the app's UI

### Important: going back to Mackup is not viable

**Mackup's symlink approach is broken on macOS 14+ (Sonoma).** Apple changed how `cfprefsd` handles symlinks in `~/Library/Preferences` while fixing a CVE. Apps now replace symlinks with real files when writing preferences. This is a [known, unfixed issue](https://github.com/lra/mackup/issues/1924) with 134 comments. Your existing `dotfiles-binary/backup.sh` works around this by using Mackup's restore (copy) + `killall cfprefsd`, but the live-sync model is dead.

### Recommended approach: `run_onchange_` scripts

This keeps everything in chezmoi (one tool) and eliminates plist noise:

```bash
# Example: run_onchange_after_configure-moom.sh
#!/bin/bash
# Moom settings I care about
defaults write com.manytricks.Moom "Allow For Drawers" -bool true
defaults write com.manytricks.Moom "Grid Spacing: Gap" -int 2
# ... etc

# Restart the app to pick up changes
killall Moom 2>/dev/null; open -a Moom
```

**How to discover the right keys**: Change a setting in the app's UI, then diff before/after:
```bash
defaults read com.manytricks.Moom > /tmp/before.plist
# (change setting in app)
defaults read com.manytricks.Moom > /tmp/after.plist
diff /tmp/before.plist /tmp/after.plist
```
Or use `prefsniff` to auto-detect changes.

**Trade-off**: upfront work to identify keys, but once done, it's clean, one-tool, and no noise. You don't need to do all apps at once — migrate one at a time.

---

## Suggested Next Steps

### Step 1: Clean up chezmoi's current state
1. Re-add Ice.plist (fix `DA`)
2. For the 4 noisy plists: either `cm re-add` to sync them, or `cm forget` them (your call — can decide per-app)
3. Get `cm status` clean

### Step 2: Triage Mackup symlinks
Go through the symlink tables and mark each: **migrate** / **drop** / **handle separately** (secrets)

### Step 3: Migrate public dotfiles to chezmoi
For each file:
```bash
cp -L ~/.gitconfig ~/.gitconfig.real && mv ~/.gitconfig.real ~/.gitconfig
chezmoi add ~/.gitconfig    # (consider --template for per-machine files)
```

### Step 4: Handle secrets
Options: Bitwarden templates (hook already set up), age encryption, or keep `dotfiles-secret` separate

### Step 5: Migrate plists to `run_onchange_` scripts
One app at a time. Start with the simplest one (Mos or Clocker), get comfortable with the pattern, then tackle Moom/Raycast/etc.

### Step 6: Clean up
Remove stale files from `config-in-the-cloud/*/restored_via_mackup/`

---

## Quick Reference

```bash
cm status          # What's out of sync
cm diff            # Full diff of pending changes
cm apply           # Apply source to home dir
cm add <file>      # Add file to chezmoi
cm add --template  # Add as template (for per-machine files)
cm edit <file>     # Edit source version
cm managed         # List managed files
cm forget <file>   # Stop managing (keeps target)
cm re-add <file>   # Update source from current target
cm doctor          # Health check
cmbrew             # Edit + apply Brewfile, run brew bundle
```
