# Chezmoi Research & Reference

Everything learned while setting up chezmoi for dotfile management across macOS and Linux machines, with rbw (Rust Bitwarden CLI) for secrets.

---

## Quick start

New to this repo? Read in this order:

1. [DECISIONS.md](cheatsheets/DECISIONS.md) — the architectural choices and why
2. [Next Actions](cheatsheets/chezmoi-next-actions.md) — what to do, in what order
3. Whichever cheat sheet covers what you're working on right now

---

## Cheat sheets

Core workflow — the ones you'll reference constantly:

| Sheet | What it covers |
|---|---|
| [Templates](cheatsheets/chezmoi-templates-cheatsheet.md) | `{{ }}` syntax, conditionals, functions, real-world examples |
| [Run Scripts](cheatsheets/chezmoi-run-scripts-cheatsheet.md) | `run_once_before_`, `run_onchange_after_`, execution order |
| [Secrets](cheatsheets/chezmoi-secrets-cheatsheet.md) | rbw setup, template syntax for secrets, age as escape hatch |
| [Configuration](cheatsheets/chezmoi-config-cheatsheet.md) | `chezmoi.toml` — git, diff, merge, encryption settings |
| [Data Sources](cheatsheets/chezmoi-data-sources-cheatsheet.md) | `.chezmoi.toml.tmpl`, `.chezmoidata`, prompts, data merging |

Specialised topics — reach for these when you need them:

| Sheet | What it covers |
|---|---|
| [macOS Preferences](cheatsheets/chezmoi-macos-preferences-cheatsheet.md) | `defaults write` in run scripts instead of managing plists |
| [Naming Conventions](cheatsheets/chezmoi-naming-cheatsheet.md) | `dot_`, `private_`, `encrypted_`, `modify_` — the full prefix/suffix system |
| [Externals](cheatsheets/chezmoi-external-cheatsheet.md) | `.chezmoiexternal.toml` for third-party repos and archives |
| [Hooks](cheatsheets/chezmoi-hooks-cheatsheet.md) | `read-source-state.pre` for password manager bootstrap, git hooks |
| [Tips & Escape Hatches](cheatsheets/chezmoi-tips-cheatsheet.md) | `chezmoi doctor`, `forget`, `merge`, debugging, recovery |

## Planning

| Document | What it covers |
|---|---|
| [Architecture Decisions](cheatsheets/DECISIONS.md) | rbw-only secrets, edit→apply workflow, no age for v1, Touch ID backlog |
| [Next Actions](cheatsheets/chezmoi-next-actions.md) | Phased plan from clean foundation through multi-machine setup |
| [Secrets Conversation Summary](cheatsheets/chezmoi-secrets-conversation-summary.md) | Context behind the rbw decision, options considered |

---

## Research & experiments

Space for trying things out before committing to the main repo.

| Directory | What's in it |
|---|---|
| *(none yet)* | |

<!--
Example entries for future experiments:

| `experiment-rbw-pinentry` | Testing custom Swift pinentry for Touch ID |
| `experiment-age-hybrid` | Trialling age encryption alongside rbw for server use |
| `experiment-chezmoi-skill` | Claude Code skill for chezmoi repo management |
-->
