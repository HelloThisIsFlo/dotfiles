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

For skills, inspect frontmatter metadata as well as files. Note trigger-heavy or unusually long `description` fields as a possible cross-agent indexing risk, but do not assume a fixed length limit. Plan to verify actual discovery after migration.

## Plan First

Present a clear migration plan before editing files. Include:

- Current state and ambiguities
- Target structure, using Mermaid if helpful
- Commit sequence
- Files to edit, move, symlink, delete, or leave untouched
- Any project folders with no instruction file, listed separately from unmigrated instruction files
- Verification commands
- Whether migrated repo skills should be auto-discoverable or manual-only. For repo-specific workflows, live-data workflows, and multi-step maintenance/audit skills, recommend manual-only descriptions unless the user explicitly wants automatic selection.

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
   - Do not add `.codex/skills` as a fallback. Repo-local `.agents/skills` is the intended Codex surface.
   - If Codex does not discover `.agents` skills, treat that as a verification failure to diagnose, not as a reason to recreate old `.codex` adapters. Check metadata, indexing, Codex version/config, and unsupported fields first.
   - Only touch existing `.codex` assets when the approved plan explicitly says to preserve, migrate, or remove them.
   - Add or update `.claude/settings.json` to call the adapter paths.

4. Keep local-only config deliberate.
   - Do not migrate personal permission allow-lists into tracked config.
   - Delete `.claude/settings.local.json` only when the approved plan says to do so.

5. Leave unsupported surfaces out of scope unless explicitly approved.
   - Claude subagents, slash commands, MCP config, plugins, and custom Codex agents are separate migrations.

Split commits for readable history:

- Agent-agnostic content edits
- `git mv` canonical moves
- Symlink compatibility
- Approved tool adapter config
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

For migrated skills, compare the skills on disk with the skills Codex exposes in `codex debug prompt-input "probe"`:

- Find skill files with `find .agents/skills -maxdepth 2 -name SKILL.md -print`.
- Parse Codex's prompt input and confirm every expected repo skill appears from the repo `.agents/skills` root.
- If a skill is missing, investigate metadata before adding adapters. Possible causes include malformed YAML, trigger-heavy or oversized frontmatter descriptions, unsupported fields, or discovery/indexing limits.
- Prefer concise frontmatter descriptions. Put detailed trigger matrices, suite lists, and workflow instructions in the body, where they load only after explicit selection.

For complex skills, especially those with live-data side effects or embedded scripts, ask the user to perform the acceptance dry test in a fresh agent session. Do not invoke live-data or stateful migrated skills yourself unless the user explicitly asks you to run them.

Smoke-test hooks with synthetic payloads when hooks exist:

- Protected file payload blocks `.env` and `uv.lock`
- Python edit payload formats a temporary file
- Repo-specific test hook runs on a temporary matching path

Run the repo's normal tests when known. Finish by reporting commits, verification results, remaining dirty state, and any manual acceptance step such as invoking a migrated skill in Codex.
