# Chezmoi Cheatsheets

Timeless reference material for chezmoi concepts, patterns, and configuration. Each sheet is self-contained — start with whichever topic you need right now.

---

## [Templates](templates.md)

Go's `text/template` engine powers chezmoi's dynamic file generation. This sheet covers conditionals, whitespace control, string functions, `lookPath` for progressive enhancement, and secrets retrieval via `rbw`. Includes real-world examples for `.gitconfig` and `.ssh/config`, plus a debugging guide for when templates don't render as expected.

Start here if you're adding a new managed file that needs to vary by machine.

## [Run Scripts](run-scripts.md)

Scripts that execute during `chezmoi apply` instead of being copied to your home directory. Covers the full naming convention: frequency prefixes (`run_`, `run_once_`, `run_onchange_`), ordering prefixes (`before_`, `after_`), and every valid combination. Explains how ordering works (alphabetical sort, numeric prefixes for control), the `run_onchange_` content-hash trick for change detection, and the gotcha that `run_once` tracks by script name.

Reach for this when you need to install packages, set defaults, or run any side-effect during apply.

## [Secrets](secrets.md)

The most comprehensive sheet. Covers two approaches: `rbw` (Rust Bitwarden CLI) for pulling individual secrets into templates, and `age` encryption for whole-file encryption at rest. Details rbw installation, configuration, authentication model (background agent, lock timeout, pinentry), template syntax, conditional guards, vault organisation, and troubleshooting. The age section covers setup, key management, and the bootstrap problem.

Read this before adding any credential, token, or password to a managed file.

## [Configuration](config.md)

Everything in `chezmoi.toml`: encryption settings, git integration (`autoCommit`, `autoPush`), diff/merge tool configuration, edit settings, interpreters, and the `[data]` section that feeds template variables.

A focused reference — use it when you need to change how chezmoi itself behaves rather than what it manages.

## [Data Sources](data-sources.md)

Where template variables come from and how they merge. Covers built-in variables (`.chezmoi.os`, `.chezmoi.hostname`, etc.), the `.chezmoi.toml.tmpl` prompt functions (`promptStringOnce`, `promptBoolOnce`, `promptChoiceOnce`), `.chezmoidata` files for structured data like package lists, and merge priority rules.

Essential reading when you're designing the data model for multi-machine support.

## [macOS Preferences](macos-preferences.md)

Why you can't track plist files directly (daemon caching, binary noise) and the solution: `defaults write` commands in `run_onchange_after_` scripts. Covers the `defaults` command syntax for every type (boolean, integer, string, array), common preference domains, how to discover settings you want to manage, and handling apps that need a restart.

macOS-specific — skip on Linux.

## [Naming Conventions](naming.md)

The Rosetta Stone between the source directory and your filesystem. Every prefix (`dot_`, `private_`, `executable_`, `readonly_`, `encrypted_`, `exact_`, `empty_`) and special file type (`create_`, `modify_`, `symlink_`, `remove_`), how they stack, how `chezmoi add` applies them automatically, and the differences between `.chezmoiignore`, `remove_`, and `exact_` for controlling what gets deployed.

Reference this when filenames in the source directory look confusing.

## [Externals](externals.md)

`.chezmoiexternal.toml` for pulling third-party content (git repos, tarballs, zip archives) into your home directory without committing them to the dotfiles repo. Covers both `archive` and `git-repo` types, `refreshPeriod` caching, version pinning (tags, commits, shallow clones), and practical examples for zsh plugins, Nerd Fonts, and Neovim plugin managers.

Use this instead of git submodules or manual downloads.

## [Hooks](hooks.md)

Lifecycle hooks configured in `chezmoi.toml` (not run scripts). Explains the key difference: hooks run before template parsing, so they can bootstrap dependencies like a password manager. Covers the four event types (`read-source-state`, command-specific, `git-auto-commit`, `git-auto-push`), the canonical use case (installing rbw before templates that reference it are parsed), and when NOT to use hooks (prefer run scripts for most tasks).

## [Tips & Escape Hatches](tips.md)

The grab bag: `chezmoi doctor` for diagnostics, `chezmoi merge` for conflict resolution, `chezmoi forget` to unmanage files, `chezmoi execute-template` for debugging, `add` vs `re-add` guidance, and complete workflow summaries for day-to-day use and new machine setup.

Reach for this when something goes wrong or you need a command you don't use often.
