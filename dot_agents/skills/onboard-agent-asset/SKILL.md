---
name: onboard-agent-asset
description: Triage and onboard new agent assets discovered in watched Claude, Codex, or Agents folders. Use when watch-dirs reports unmanaged files, when the user asks to onboard a skill/hook/agent asset, or when migrating a Claude/Codex skill into shared `.agents` ownership without letting the agent decide ownership silently.
---

# Onboard Agent Asset

Use this skill to turn a new or unmanaged agent asset into an intentional chezmoi-managed source file, ignore rule, or follow-up decision.

## Guardrails

- Inspect first. Do not add, move, delete, or ignore until the asset is classified.
- Never decide ownership silently. Recommend, then ask before mutation unless the user already gave an explicit exact action.
- Preserve history with `git mv` when the asset is already tracked in this repo.
- Treat `chezmoi status`, `chezmoi diff`, and `chezmoi cat` as inspection commands.
- Treat `chezmoi apply` as mutation.
- Never run global `chezmoi apply` during onboarding.
- Ask Flo to apply after review, or use path-scoped `chezmoi apply` only with explicit approval.
- Onboarding is not complete until the original live asset path still works for the tool or user that created it.
- When a source file, adapter, ignore rule, or executable-mode fix changes the live target state, finish with an explicitly approved path-scoped `chezmoi apply` for only the affected target path(s).
- Keep commits semantic:
  - pure moves
  - content cleanup
  - adapters
  - ignore/watch updates
- Do not onboard generated/plugin-managed assets into `.agents` just because they look skill-shaped.

## Classify

For each candidate path, inspect enough to choose one class:

- **Shared self-authored skill**: has `SKILL.md`, appears written/owned by Flo, and is useful across agents.
- **Tool-specific asset**: depends on Claude-only or Codex-only config, slash commands, permissions, UI, or runtime behavior.
- **External/plugin-managed asset**: installed by a marketplace, plugin, GSD, npm/package manager, or another automated source.
- **Support workspace**: evals, test docs, iteration state, benchmarks, or scripts supporting a skill but not itself a skill.
- **Not an agent asset**: cache, log, generated file, local state, or unrelated file.

## Actions

Recommend exactly one action per candidate:

- **Shared skill**:
  - move canonical source to `dot_agents/skills/<name>`
  - add Claude adapter `dot_claude/skills/symlink_<name>.tmpl`
  - skip Codex adapter unless verification proves Codex cannot load `~/.agents/skills`
- **Tool-specific asset**:
  - keep under `dot_claude` or `dot_codex`
  - document why it is tool-specific if the reason is not obvious
- **External/plugin-managed asset**:
  - add or confirm `.chezmoiignore` entry
  - keep watched directory coverage so new surprises still surface
- **Support workspace**:
  - move to `dot_agents/skill-workspaces/<name>` when shared
  - add a tool adapter only when existing paths must keep working
- **Not an asset**:
  - ignore or skip; do not force it into `.agents`

## Verification

Before reporting done:

- `git status --short`
- `git diff --cached --summary --find-renames` for staged moves
- show `chezmoi status`
- `chezmoi cat` or `chezmoi diff` for symlink adapters when relevant
- verify every original live asset path still exists and resolves as intended after any path-scoped apply
- `codex debug prompt-input "probe"` when Codex skill discovery or home instructions changed
- report whether `chezmoi apply` was run
- if anything was applied, name the exact target paths
- remind Flo about any skipped candidates that are good tests for this skill
