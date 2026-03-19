# Chezmoi Cheatsheets

Timeless reference material for chezmoi concepts, patterns, and configuration. Each sheet is self-contained — start with whichever topic you need right now.

---

## [Templates](templates.md)

- **Conditionals** — `if`, `else`, `eq`, OS/hostname branching
- **Whitespace control** — `{{-` and `-}}` trimming
- **String functions** — `replace`, `contains`, `hasPrefix`, `join`, etc.
- **`lookPath`** — progressive enhancement (only configure tools that exist)
- **Secrets in templates** — `rbw` calls for passwords, tokens, API keys
- **Real-world examples** — `.gitconfig`, `.ssh/config`
- **Debugging** — `chezmoi execute-template`, `chezmoi cat`

## [Run Scripts](run-scripts.md)

- **Frequency prefixes** — `run_` (always), `run_once_` (first apply), `run_onchange_` (content hash)
- **Ordering** — `before_` / `after_`, alphabetical sort, numeric prefixes
- **Change detection** — the `run_onchange_` content-hash trick (embed a checksum)
- **Gotcha** — `run_once` tracks by script *name*, not content
- **Common uses** — package installs, `defaults write`, service restarts

## [Secrets](secrets.md)

- **rbw (Rust Bitwarden CLI)** — install, configure, auth model (background agent, lock timeout, pinentry)
  - Template syntax — `{{ (rbw "item").data.password }}`, `{{ (rbwFields "item").field.value }}`
  - Conditional guards — skip secrets on machines that don't need them
  - Vault organisation & troubleshooting
- **age encryption** — whole-file encryption at rest
  - Setup, key management, the bootstrap problem
- **When to use which** — rbw for field-level secrets, age for offline/unattended

## [Configuration](config.md)

- **Encryption** — age/GPG settings in `[encryption]`
- **Git integration** — `autoCommit`, `autoPush`
- **Diff/merge tools** — delta, VS Code, vimdiff
- **Edit settings** — editor, apply-after-edit
- **Interpreters** — per-extension script runners
- **`[data]`** — custom template variables

## [Data Sources](data-sources.md)

- **Built-in variables** — `.chezmoi.os`, `.chezmoi.hostname`, `.chezmoi.username`, etc.
- **Prompt functions** — `promptStringOnce`, `promptBoolOnce`, `promptChoiceOnce`
- **`.chezmoidata` files** — structured YAML/JSON/TOML for package lists, machine profiles
- **Merge priority** — how multiple data sources combine

## [macOS Preferences](macos-preferences.md)

- **Why not track plists directly** — daemon caching, binary noise, frequent churn
- **The solution** — `defaults write` in `run_onchange_after_` scripts
- **`defaults` syntax** — booleans, integers, strings, arrays, dicts
- **Discovery** — how to find the domain and key for a setting
- **App restarts** — `killall` patterns for preferences that need it

## [Naming Conventions](naming.md)

- **Prefixes** — `dot_`, `private_`, `executable_`, `readonly_`, `encrypted_`, `exact_`, `empty_`
- **Special types** — `create_`, `modify_`, `symlink_`, `remove_`
- **Stacking** — how prefixes combine (`private_dot_config/`)
- **`chezmoi add`** — auto-applies correct prefixes
- **Deployment control** — `.chezmoiignore` vs `remove_` vs `exact_`

## [Externals](externals.md)

- **`.chezmoiexternal.toml`** — declare third-party content to pull in
- **Types** — `archive` (tarballs, zips) and `git-repo`
- **Caching** — `refreshPeriod` for periodic re-fetch
- **Version pinning** — tags, commits, shallow clones
- **Examples** — zsh plugins, Nerd Fonts, Neovim plugin managers

## [Brew Management Approaches](brew-management-approaches.md)

- **Three officially blessed patterns** — `dot_Brewfile`, `.chezmoidata/` YAML, inline template lists
- **Side-by-side comparison** — pros, cons, when to use each
- **The `brew bundle --adopt` bug** — which approaches avoid it
- **Decision framework** — per-machine conditionals, Phase 6.5 readiness, brew bundle avoidance
- **Sources** — links to official docs, Tom Payne's dotfiles, relevant GitHub issues

## [Hooks](hooks.md)

- **Key difference from run scripts** — hooks run *before* template parsing
- **Use case** — bootstrap a password manager before templates need it
- **Event types** — `read-source-state`, command-specific, `git-auto-commit`, `git-auto-push`
- **When NOT to use** — prefer run scripts for most post-apply tasks

## [Merge — 3-Way Conflict Resolution](chezmoi-merge.html)

Interactive visual explainer (open in browser). Covers:
- **When to merge** — vs apply (chezmoi wins) or re-add (home wins)
- **3-way merge model** — base from git history, auto-resolution
- **The counter-intuitive part** — lines that differ between panes may not show as conflicts
- **VS Code layout** — left = chezmoi, right = home, result starts from left
- **After merge** — you MUST `chezmoi apply` afterwards

## [Status Columns](chezmoi-status.md)

- **Common misconception** — columns are NOT "source changed" vs "target changed"
- **Column 1** — last-applied state vs actual disk state (what changed since last apply)
- **Column 2** — actual disk state vs what source would render (what `chezmoi apply` would do)
- **Reading MM, M\_, \_M** — quick reference for each code

## [Tips & Escape Hatches](tips.md)

- **Diagnostics** — `chezmoi doctor`
- **Conflict resolution** — `chezmoi merge`
- **Unmanage files** — `chezmoi forget`
- **Debug templates** — `chezmoi execute-template`
- **`add` vs `re-add`** — when each is safe
- **Workflow summaries** — day-to-day use, new machine bootstrap
