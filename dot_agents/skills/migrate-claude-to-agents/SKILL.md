---
name: migrate-claude-to-agents
description: Explicitly invoked workflow for migrating a clean repository's Claude Code instructions, hooks, and skills into shared `.agents` assets with Claude Code and Codex adapters. Use when the user asks to migrate Claude Code repo assets, reduce duplication with symlinks, preserve Git history, or make Claude hooks/skills agent-agnostic.
---

# Migrate Claude To Agents

## Guardrails

Never mutate before approval. This skill is executor-capable, but always plans first and waits for the user to explicitly approve the migration plan.

Stop immediately if the repo is dirty:

```bash
git rev-parse --show-toplevel
git status --short
```

If `git status --short` prints anything, do not inspect or migrate further. Tell the user to commit, push, stash, or otherwise clean the repo first. Dirty means dirty even when changes look unrelated.

## Inspect

After a clean preflight, inspect the repo shape:

- Instruction files: `CLAUDE.md`, `claude.md`, any mixed-case `claude.md`, `AGENTS.md`, nested guidance files
- Claude assets: `.claude/settings.json`, `.claude/settings.local.json`, `.claude/hooks`, `.claude/skills`, `.claude/agents`
- Existing shared/Codex assets: `.agents`, `.codex`
- Tracking state: `git ls-files`, `git status --short`, `git diff --name-status`

Discover instruction files case-insensitively. Do not rely only on shell globs like `*CLAUDE.md`; they miss tracked lowercase files on case-insensitive filesystems:

```bash
find . -iname 'claude.md' -o -iname 'agents.md'
git ls-files | rg -i '(^|/)claude\.md$|(^|/)agents\.md$'
```

Track original casing for every Claude instruction file. The canonical target is always `AGENTS.md`, but the compatibility adapter preserves the original filename casing (`CLAUDE.md`, `claude.md`, or mixed-case).

Compare duplicates before choosing moves or symlinks. Treat divergent existing `.agents` or `.codex` content as ambiguity.

## Plan First

Present a clear migration plan before editing files. Include:

- Current state and ambiguities
- Target structure, using Mermaid if helpful
- Commit sequence
- Files to edit, move, symlink, delete, or leave untouched
- Any project folders with no instruction file, listed separately from unmigrated instruction files
- Verification commands

Ask for explicit approval. Do not continue from vague encouragement; wait for a clear approval such as "implement this plan", "approved", or "go ahead".

Ask targeted questions before planning or executing when:

- `.claude/settings.local.json` contains non-permission behavior
- Untracked duplicates do not match tracked originals
- Existing `.agents` or `.codex` files differ from Claude assets
- Hooks contain repo-specific commands, secrets, or unclear payload parsing
- Claude subagents, slash commands, MCP servers, or unsupported assets are present
- The repo is not in Git

## Execute After Approval

Use this default sequence unless the approved plan says otherwise:

1. Make tracked Claude assets agent-agnostic before moving them.
   - Replace tool-specific wording like "Claude" with "agent" when behavior is shared.
   - Keep product-specific config names where they are actual adapter surfaces.
   - Make hook failures explicit with nonzero exits where possible.

2. Preserve history with `git mv`.
   - Move any case variant of `claude.md` to `AGENTS.md`.
   - Preserve the original adapter casing when recreating the symlink (`CLAUDE.md -> AGENTS.md` or `claude.md -> AGENTS.md`).
   - Move canonical hooks and skills into `.agents/hooks` and `.agents/skills`.
   - Keep pure moves in their own commit.

3. Add compatibility adapters.
   - Recreate `.claude` hook/skill paths as symlinks to `.agents`.
   - Add `.codex/hooks` symlinks when useful for readability.
   - Add or update `.claude/settings.json` and `.codex/hooks.json` to call the adapter paths.

4. Keep local-only config deliberate.
   - Do not migrate personal permission allow-lists into tracked config.
   - Delete `.claude/settings.local.json` only when the approved plan says to do so.

5. Leave unsupported surfaces out of scope unless explicitly approved.
   - Claude subagents, slash commands, MCP config, plugins, and custom Codex agents are separate migrations.

Split commits for readable history:

- Agent-agnostic content edits
- `git mv` canonical moves
- Symlink compatibility
- Tool adapter config
- Optional docs

## Verify

Run the checks that match the repo:

```bash
git show --summary --oneline HEAD
git ls-files -s .agents .claude .codex
git ls-files | rg -i '(^|/)claude\.md$|(^|/)agents\.md$'
find . -iname 'claude.md' -type f
codex debug prompt-input "probe"
```

After instruction migration, there should be no tracked regular file matching `claude.md` case-insensitively. Every tracked Claude instruction adapter should be a symlink to `AGENTS.md`, preserving its original casing. Every canonical instruction file should be a regular tracked `AGENTS.md`.

Smoke-test hooks with synthetic payloads when hooks exist:

- Protected file payload blocks `.env` and `uv.lock`
- Python edit payload formats a temporary file
- Repo-specific test hook runs on a temporary matching path

Run the repo's normal tests when known. Finish by reporting commits, verification results, remaining dirty state, and any manual acceptance step such as invoking a migrated skill in Codex.
