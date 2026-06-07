---
name: migrate-claude-to-agents
description: Explicitly invoked workflow for migrating a clean repository's Claude Code instructions, rules, hooks, skills, commands, subagents, MCP config, and plugin-adjacent assets into shared `.agents` assets plus Claude Code and Codex adapters. Use when the user asks to migrate Claude Code repo assets, reduce duplication with symlinks, preserve Git history, or make Claude/Codex agent assets consistent.
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

- Instruction files: `CLAUDE.md`, `claude.md`, any mixed-case `claude.md`, `AGENTS.md`, nested guidance files, `.claude/CLAUDE.md`, `CLAUDE.local.md`
- Claude assets: `.claude/settings.json`, `.claude/settings.local.json`, `.claude/rules`, `.claude/hooks`, `.claude/skills`, `.claude/commands`, `.claude/agents`, `.claude/agent-memory`, `.claude/agent-memory-local`
- Shared assets: `.agents`, especially `.agents/skills`, `.agents/hooks`, `.agents/plugins`
- Codex assets: `.codex/config.toml`, `.codex/hooks.json`, `.codex/rules`, `.codex/agents`, `.codex/skills`
- Tooling/package assets: `.mcp.json`, `.claude-plugin`, `.codex-plugin`
- Tracking state: `git ls-files`, `git status --short`, `git diff --name-status`

Discover instruction files case-insensitively. Do not rely only on shell globs like `*CLAUDE.md`; they miss tracked lowercase files on case-insensitive filesystems:

```bash
find . -iname 'claude.md' -o -iname 'agents.md'
git ls-files | rg -i '(^|/)claude\.md$|(^|/)agents\.md$'
```

Track original casing for every Claude instruction file. The canonical target is always `AGENTS.md`, but the compatibility adapter preserves the original filename casing (`CLAUDE.md`, `claude.md`, or mixed-case).

Compare duplicates before choosing moves or symlinks. Treat divergent existing `.agents` or `.codex` content as ambiguity.

For skills, inspect frontmatter metadata as well as files. Note trigger-heavy or unusually long `description` fields as a possible cross-agent indexing risk, but do not assume a fixed length limit. Plan to verify actual discovery after migration.

Run the bundled validator in inventory mode when available:

```bash
python3 dot_agents/skills/migrate-claude-to-agents/scripts/validate_agent_migration.py inventory
```

Use its report as a starting point, not as a substitute for reading ambiguous files.

## Surface Policy

Classify every discovered asset before planning edits:

| Surface | Preferred target | Policy |
|---|---|---|
| Shared instructions | `AGENTS.md` | Canonical cross-agent instructions. Claude compatibility is a preserved `CLAUDE.md`/`claude.md` symlink or explicit import when symlinks are unsuitable. |
| Claude rules | `.claude/rules/**/*.md` | Claude-specific. Fold into `AGENTS.md` or keep as Claude rules only when path-scoped behavior is useful and approved. |
| Skills | `.agents/skills/<name>/SKILL.md` | Shared canonical skill home. Recreate `.claude/skills` as a symlink adapter. Do not create `.codex/skills` as a fallback. |
| Slash commands | `.agents/skills` | Legacy Claude commands should usually become skills. Keep `.claude/commands` only when explicitly approved. |
| Shared hook scripts | `.agents/hooks` | Store reusable scripts here only when the same implementation works for both tools. |
| Claude hook registration | `.claude/settings.json` | Project-shareable Claude hook config. Do not put personal allow-lists in tracked settings. |
| Codex hook registration | `.codex/hooks.json` | House default for repo hook config. Use inline `.codex/config.toml` hooks only to preserve an approved existing style. |
| Subagents/custom agents | `.claude/agents/*.md` and `.codex/agents/*.toml` | Supported by both tools but formats differ. Inspect, classify, and transform only with explicit approval. |
| MCP | Claude `.mcp.json`; Codex `.codex/config.toml` `[mcp_servers.*]` | Translate deliberately. Do not assume one file can serve both tools. |
| Plugins | `.claude-plugin` or `.codex-plugin` | Separate packaging surfaces. Migrate only when the plan explicitly includes plugin distribution. |
| Rules/permissions | Claude settings; Codex `.codex/rules/*.rules` | Tool-specific. Keep deterministic policy in native rule/config surfaces. |
| Memories/local state | `CLAUDE.local.md`, `.claude/settings.local.json`, `.claude/agent-memory-local`, Codex memories | Local-only unless the user explicitly approves sharing non-private project memory. |

## Plan First

Present a clear migration plan before editing files. Include:

- Current state and ambiguities
- Migration matrix with each surface classified as shared, Claude-specific, Codex-specific, local-only, plugin-packaged, or out-of-scope
- Target structure, using Mermaid if helpful
- Commit sequence
- Files to edit, move, transform, symlink, delete, or leave untouched
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
- A Claude subagent uses tool/model/permission settings that have no obvious Codex equivalent
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
   - Add or update `.claude/settings.json` for Claude hook registrations.
   - Add or update `.codex/hooks.json` for Codex hook registrations.
   - Only use `.codex/config.toml` for hooks when preserving an explicitly approved existing inline hook style.

4. Transform tool-specific assets deliberately.
   - Convert legacy `.claude/commands/*.md` to skills when the workflow is reusable.
   - Transform Claude subagents from `.claude/agents/*.md` to Codex `.codex/agents/*.toml` only after mapping prompt, tools, model, and permissions.
   - Translate `.mcp.json` entries into Codex `[mcp_servers.*]` config only when the server command, environment, and secret handling are clear.
   - Keep plugin packaging separate unless the approved plan includes `.claude-plugin` or `.codex-plugin` distribution.

5. Keep local-only config deliberate.
   - Do not migrate personal permission allow-lists into tracked config.
   - Delete `.claude/settings.local.json` only when the approved plan says to do so.
   - Do not commit local memories or agent-memory-local content without an explicit public-repo review.

6. Leave truly unsupported or high-risk surfaces out of scope unless explicitly approved.
   - Mark unknown or undocumented compatibility as out-of-scope rather than guessing.

Split commits for readable history:

- Agent-agnostic content edits
- `git mv` canonical moves
- Symlink compatibility
- Transformed subagents, MCP, or command-to-skill changes
- Approved tool adapter config
- Optional docs

## Verify

Run the checks that match the repo:

```bash
python3 dot_agents/skills/migrate-claude-to-agents/scripts/validate_agent_migration.py verify
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

For migrated subagents, compare Claude and Codex definitions by intent rather than path:

- Confirm the Codex `.toml` agent preserves the Claude agent's role, prompt, tool intent, and safety limits.
- Mark model, permission, or tool differences explicitly in the migration report.
- Ask the user to perform a fresh-session dry test for complex agents, live-data agents, or stateful agents.

For complex skills, especially those with live-data side effects or embedded scripts, ask the user to perform the acceptance dry test in a fresh agent session. Do not invoke live-data or stateful migrated skills yourself unless the user explicitly asks you to run them.

Smoke-test hooks with synthetic payloads when hooks exist:

- Protected file payload blocks `.env` and `uv.lock`
- Python edit payload formats a temporary file
- Repo-specific test hook runs on a temporary matching path

Run the repo's normal tests when known. Finish by reporting commits, validator output, verification results, remaining dirty state, and any manual acceptance step such as invoking a migrated skill or subagent in a fresh Codex/Claude session.
