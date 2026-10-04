# Whole-Repo Migration

Read this when one repo needs every agent surface moved at once: instructions, rules, hooks, skills, commands, subagents, MCP config, and plugin-adjacent assets. Smaller fixes (one symlink, one skill) follow `SKILL.md` directly.

Skill placement, the instruction-file pair, and wording rules live in `SKILL.md`. This file adds the surfaces and the sequence a full migration needs.

## Preflight

A whole-repo migration moves many tracked files at once, so it needs a clean starting point to keep history readable and reversible.

```bash
git rev-parse --show-toplevel
git status --short
```

If `git status --short` prints anything, stop. Ask Flo to commit, stash, or otherwise clean the repo first, even when the changes look unrelated.

## Inspect

Run the bundled validator first. Resolve its path relative to this skill, not the repo being migrated:

```bash
SKILL_DIR=/path/to/make-agents-portable
python3 "$SKILL_DIR/scripts/validate_agent_migration.py" inventory --root <repo>
```

Use its report as a starting point, then read every ambiguous file:

- Instruction files: any casing of `claude.md`, `AGENTS.md`, nested guidance, `.claude/CLAUDE.md`, `CLAUDE.local.md`. Discover them case-insensitively (`find . -iname 'claude.md' -o -iname 'agents.md'` plus `git ls-files | rg -i '(^|/)(claude|agents)\.md$'`); shell globs miss lowercase files on case-insensitive filesystems.
- Claude assets: `.claude/settings.json`, `.claude/settings.local.json`, `.claude/rules`, `.claude/hooks`, `.claude/skills`, `.claude/commands`, `.claude/agents`, `.claude/agent-memory`, `.claude/agent-memory-local`
- Shared assets: `.agents/skills`, `.agents/hooks`, `.agents/plugins`
- Codex assets: `.codex/config.toml`, `.codex/hooks.json`, `.codex/rules`, `.codex/agents`, `.codex/skills`
- Packaging: `.mcp.json`, `.claude-plugin`, `.codex-plugin`

Compare duplicates before choosing moves or symlinks. Divergent existing `.agents` or `.codex` content is an ambiguity to raise.

## Surface policy

| Surface | Target | Policy |
|---|---|---|
| Shared instructions | `AGENTS.md` | Canonical. Claude reads it through a `CLAUDE.md` symlink that keeps the original filename casing. |
| Claude rules | `.claude/rules/**/*.md` | Fold into `AGENTS.md`, or keep as Claude rules only when path-scoped behaviour is useful and approved. |
| Skills | `.agents/skills/<name>` | Per `SKILL.md`: `.claude/skills` is one folder symlink. No `.codex/skills` fallback. |
| Slash commands | `.agents/skills` | Legacy Claude commands usually become skills. Keep `.claude/commands` only when approved. |
| Shared hook scripts | `.agents/hooks` | Only when the same implementation works for both runtimes. |
| Claude hook registration | `.claude/settings.json` | Project-shareable config. No personal allow-lists in tracked settings. |
| Codex hook registration | `.codex/hooks.json` | House default. Inline `.codex/config.toml` hooks only to preserve an approved existing style. |
| Subagents | `.claude/agents/*.md` and `.codex/agents/*.toml` | Formats differ. Transform only after mapping prompt, tools, model, and permissions, with approval. |
| MCP | Claude `.mcp.json`; Codex `.codex/config.toml` `[mcp_servers.*]` | Translate deliberately; one file can't serve both. |
| Plugins | `.claude-plugin` / `.codex-plugin` | Separate packaging. Migrate only when the plan includes distribution. |
| Permissions | Claude settings; Codex `.codex/rules/*.rules` | Runtime-specific. Keep in native config. |
| Local state | `CLAUDE.local.md`, `.claude/settings.local.json`, `.claude/agent-memory-local`, Codex memories | Local-only unless Flo approves sharing non-private project memory. |

## Plan, then wait

Present the plan before editing:

- current state and ambiguities
- every surface classified as shared, Claude-specific, Codex-specific, local-only, plugin-packaged, or out of scope
- target structure (Mermaid if it helps)
- files to move, transform, symlink, delete, or leave alone
- commit sequence and verification commands
- whether repo-specific, live-data, or multi-step maintenance skills should be manual-only (recommend manual-only unless Flo wants automatic selection)

Wait for a clear approval ("approved", "go ahead"), not vague encouragement. Ask targeted questions first when:

- `.claude/settings.local.json` holds more than permissions
- untracked duplicates differ from tracked originals
- existing `.agents` or `.codex` files differ from the Claude assets
- hooks contain repo-specific commands, secrets, or unclear payload parsing
- subagents, slash commands, MCP servers, or unsupported assets are present
- a subagent's tool, model, or permission settings have no obvious Codex equivalent
- the repo is not in Git

## Execute after approval

1. Make tracked Claude assets runtime-neutral before moving them (the wording rules in `SKILL.md`). Keep real adapter config names. Make hook failures exit nonzero where possible.
2. Move with `git mv` to preserve history; pure moves get their own commit.
3. Add adapters: the `CLAUDE.md` symlink, the `.claude/skills` folder symlink, `.claude/settings.json` and `.codex/hooks.json` hook registrations. If Codex doesn't discover `.agents/skills`, diagnose metadata, indexing, version, or config; never add a `.codex/skills` fallback.
4. Transform runtime-specific assets deliberately: commands → skills, `.claude/agents/*.md` → `.codex/agents/*.toml`, `.mcp.json` → `[mcp_servers.*]` only when command, environment, and secret handling are clear.
5. Keep local-only config local. Delete `.claude/settings.local.json` only when the plan says so; never commit local memories without a public-repo review.
6. Leave unknown or high-risk surfaces out of scope rather than guessing.

Commits, in this order: runtime-neutral content edits → canonical moves → symlink adapters → transformed subagents / MCP / commands → runtime adapter config → docs.

## Verify

```bash
python3 "$SKILL_DIR/scripts/validate_agent_migration.py" verify --root <repo>
git ls-files -s .agents .claude .codex
find . -iname 'claude.md' -type f
codex debug prompt-input "probe"
```

- No tracked regular `claude.md` file remains in any casing; each is a symlink to its sibling `AGENTS.md`.
- Every `.agents/skills/*/SKILL.md` appears in Codex's prompt input. When one is missing, check metadata first (malformed YAML, oversized trigger-heavy descriptions, unsupported fields).
- Subagents: compare Claude and Codex definitions by intent; report model, permission, or tool differences.
- Hooks: smoke-test with synthetic payloads.
- Run the repo's normal tests when known.
- Complex, live-data, or stateful skills and subagents: ask Flo for a fresh-session dry run instead of invoking them yourself.

Report commits, validator output, verification results, remaining dirty state, and any manual acceptance step.
