---
name: make-agents-portable
description: Make agent assets runtime-agnostic and chezmoi-managed, so skills, AGENTS.md/CLAUDE.md instructions, hooks, subagents, and MCP config work in Claude Code and Codex alike. Use when watch-dirs or chezmoi-status reports unmanaged agent files; when the user asks to onboard, port, retrofit, migrate, or audit skills, instruction files, or a repo's agent setup; when wording is runtime-specific (Codex-only tool names, `$name` handoffs, `mcp__` names); when a repo's skills or instructions are invisible to one runtime; and as the final step after creating or substantially editing any skill or AGENTS.md. Never decides ownership silently.
---

# Make Agents Portable

Turn agent assets into something both runtimes can load and follow: intentionally placed under chezmoi or in the owning repo, wired so Claude Code and Codex both see them, and worded in capabilities rather than one runtime's tool names.

The global **Capability Map** in `~/.agents/AGENTS.md` is the vocabulary. Skills and instructions name a capability ("logged-in browser", "fresh-context sub-agent"); each runtime resolves it there. That keeps one file working in Claude Code and Codex, and a tool change becomes a one-row edit instead of a sweep.

## Pick the mode

- 📦 **Onboard**: new or unmanaged files (watch-dirs list, chezmoi-status, "onboard this"). Classify, then place.
- ✍️ **Retrofit**: an existing skill or instruction file that names runtime tools or isn't wired for both runtimes. Place, then fix wording.
- 🔍 **Audit**: "which skills aren't portable?", "audit my agent setup". Report only, no edits. Fixes then run one asset at a time.
- 🚚 **Whole-repo migration**: one repo's instructions, rules, hooks, skills, commands, subagents, MCP config, and plugin-adjacent assets moved in one pass. Read `references/repo-migration.md`; it adds a clean-repo preflight and a plan Flo approves before any edit.
- A newly created skill or AGENTS.md gets Onboard + Retrofit in one pass.

## Guardrails

- Inspect first. Do not add, move, delete, or ignore until the asset is classified.
- Never decide ownership silently. Recommend, then ask before mutation unless the user already gave an explicit exact action.
- **Placement is automatic** when classification, ownership and target path are unambiguous, nothing can be lost, and the change touches only this asset. Ask when classification, ownership, target path, generated/plugin status, divergent content, or live-data side effects are unclear.
- **Wording changes are proposed, not applied.** They change how an agent behaves, so show one proposal per file listing every swap, then edit after Flo says go.
- Preserve history with `git mv` when the asset is already tracked.
- Treat `chezmoi status`, `chezmoi diff`, and `chezmoi cat` as inspection; treat `chezmoi apply` as mutation.
- Apply only the exact live asset path(s) just onboarded or updated, with path-scoped `chezmoi --no-tty apply -- <path>` then `verify`. Never apply a parent directory, watched directory, or global target.
- Onboarding is not complete until the original live asset path still works for the tool or user that created it.
- A rename leaves the old live path behind. Remove the stale live copy after the new path verifies; the old source survives in git.
- Commit exactly one asset per commit, only when Flo asks. Stage only its source files, adapters, and required ignore/watch updates; never unrelated dirty files.
- Keep commits semantic: pure moves, content cleanup, adapters, ignore/watch updates.
- Do not onboard generated/plugin-managed assets into `.agents` just because they look skill-shaped.
- Leave third-party repos alone (remote not Flo's and no commits by Flo): their instruction files follow upstream conventions.

## Classify (Onboard)

For each candidate path, inspect enough to choose one class:

- **Shared self-authored skill**: has `SKILL.md`, written/owned by Flo, useful across agents.
- **Instruction file**: `AGENTS.md` or any casing of `CLAUDE.md`, global, repo-root, or nested.
- **Tool-specific asset**: depends on Claude-only or Codex-only config, slash commands, permissions, UI, or runtime behaviour.
- **External/plugin-managed asset**: installed by a marketplace, plugin, GSD, Herdr, npm/package manager, or another automated source.
- **Support workspace**: evals, test docs, iteration state, benchmarks, or scripts supporting a skill but not itself a skill.
- **Not an agent asset**: cache, log, generated file, local state, or unrelated file.

`watch-dirs` itself is only a terminal add/ignore/skip prompt; it never decides. This skill is where the judgement happens: a blind add would track a plugin's hook, a blind ignore would hide a skill Flo wrote.

## Place

- **Shared skill (global)**
  - canonical source: `dot_agents/skills/<name>`
  - Claude adapter: `dot_claude/skills/symlink_<name>.tmpl` containing `{{ .chezmoi.homeDir }}/.agents/skills/<name>`
  - no Codex adapter; Codex loads `~/.agents/skills` directly unless verification proves otherwise
- **Repo skill**
  - canonical source: `<repo>/.agents/skills/<name>`
  - Claude link: `<repo>/.claude/skills` is one folder symlink → `../.agents/skills`, so every repo skill shows up in Claude with no per-skill step
  - a `.claude/skills` folder holding only per-skill symlinks into `.agents/skills` converts to the folder symlink; one holding real Claude-only skills is an ask
  - commits happen in that repo, not chezmoi
- **Instruction file**: `AGENTS.md` is canonical; `CLAUDE.md` is a symlink to its sibling `AGENTS.md` (keep the original casing). Same at the root and in nested folders. The global pair is `~/.agents/AGENTS.md`, linked as `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`.
  - automatic (lossless):
    - only `AGENTS.md` → add the `CLAUDE.md` symlink
    - only a real `CLAUDE.md` → `git mv` it to `AGENTS.md`, then add the symlink
    - a `CLAUDE.md` that only points at `AGENTS.md` ("follow AGENTS.md") → replace it with the symlink
  - ask Flo:
    - both are real files with different content: one may hold recent edits made without noticing, so show the diff and ask which wins
    - `CLAUDE.md` is untracked or gitignored: it may be a deliberate personal file
    - `CLAUDE.md` links somewhere other than `AGENTS.md`
- **Tool-specific asset**: keep under `dot_claude` or `dot_codex`; document why when it isn't obvious.
- **Hooks, subagents, MCP config, commands, rules**: follow the surface policy in `references/repo-migration.md`.
- **External/plugin-managed asset**: add or confirm a `.chezmoiignore` entry; keep watch-dirs coverage so new surprises still surface.
- **Support workspace**: shared → `dot_agents/skill-workspaces/<name>`; add a tool adapter only when existing paths must keep working.
- **Shared support file** (e.g. a profile several runtimes read): `dot_agents/<area>/` plus per-runtime symlink adapters.
- **Not an asset**: ignore or skip; do not force it into `.agents`.

## Wording (Retrofit)

Scope: `SKILL.md`, `references/`, and instruction files. `agents/openai.yaml` is Codex-only UI metadata, so Codex syntax such as `$name` stays allowed there.

Look for anything that tells an agent to use what only one runtime understands, and swap it for the capability:

| Found | Becomes |
|---|---|
| `chrome:control-chrome`, "Chrome plugin", Claude in Chrome tool names | the **logged-in browser** |
| `browser:control-in-app-browser`, "built-in/in-app browser" | **interact with a public page** |
| `$name` handoffs | "invoke the `name` skill" |
| a gate on the literal `$name` text | a gate on the skill being invoked, in any runtime's syntax |
| a handoff from a global skill to a repo-local skill | a pointer naming the repo: "the `name` skill in <Repo>" |
| a manual-only gate ("run only when the user explicitly invokes `$name`") | runtime metadata: Claude frontmatter `disable-model-invocation: true` + Codex `policy.allow_implicit_invocation: false` in `agents/openai.yaml`; the text just says "manual only" |
| `mcp__…` names, Skill tool, Agent tool, `fork_turns`, WebFetch | the map's capability (tasks, email, calendar, fresh-context sub-agent, read a public page…) |
| "bundled workspace Python" or runtime-specific interpreters | `uv run --with <pkg>` |
| `/init` boilerplate: "guidance to Claude Code when working…" | "guidance to agents working…" |

Website rules, guardrails and domain knowledge stay put. Only the runtime mechanics move out.

Name the capability only. How it's done (e.g. `defuddle` before a browser) belongs to the Capability Map; copying it into a skill duplicates the map and goes stale when the map changes.

Use the map's capability names verbatim ("interact with a public page", not "public-page browser"), so a search for a capability finds every file that relies on it.

What is **not** an offender:

- the Capability Map itself, and sections explicitly labelled for one runtime (e.g. "Claude-Specific Guidance" in the global `AGENTS.md`)
- a runtime as the subject: a project about Claude, a folder named `Claude Cowork/`, a Claude Code hook the repo builds
- generated blocks marked as managed by a tool ("do not edit manually")

A runtime coupling in a repo's architecture ("operated through Codex local skills") is a design choice, not wording: flag it and ask.

### When no map row fits

- Lean toward proposing a **new Capability Map row**, even when only one skill needs it today. Ask: is this the first of many? A row keeps every future skill portable for free.
- Use a **Tier 2 runtime adapter** only for a genuine one-off mechanic of this skill: `references/runtime-claude.md` + `references/runtime-codex.md`, with `SKILL.md` pointing to "the adapter for your runtime" (the `distill-kernel` pattern).
- Always bring the choice to Flo: a new row changes global guidance in `~/.agents/AGENTS.md`.

## Audit

Every audit covers skills, instruction files, and the other agent surfaces, whatever its stated topic; "audit the skills" includes them without being asked.

- Scan:
  - global skills: `~/.agents/skills`, `~/.claude/skills` (non-symlinks = Claude-only skills), `~/.codex/skills` (outside ignored built-ins)
  - repo skills: every `<repo>/.agents/skills/<name>` under `~/Work`, listed with this command (about 2 s; quote paths, some contain spaces):
    ```bash
    find ~/Work \( -name node_modules -o -name .git -o -name .venv -o -name Library \) -prune -o -type d -path '*/.agents/skills/*' -prune -print
    ```
  - instruction files: the global pair, plus every `AGENTS.md` and `CLAUDE.md` (any casing) under `~/Work`:
    ```bash
    find ~/Work \( -name node_modules -o -name .git -o -name .venv -o -name Library -o -path '*/.claude/worktrees' \) -prune -o \( -iname 'claude.md' -o -iname 'agents.md' \) -print
    ```
  - other surfaces per repo touched by the audit: run `scripts/validate_agent_migration.py verify --root <repo>` (hooks, subagents, MCP, commands, rules, local state)
- Skip third-party repos and intentional exceptions listed in `~/.agents/AGENTS.md` (e.g. Codex-only skills).
- Resolve every handoff target against the skill lists before calling it dangling:
  - ✅ **global**: fine
  - 📁 **repo-local**: name the repo; a global skill pointing at it only works inside that repo (see the wording rule)
  - ❌ **missing**: in neither list; ask Flo whether it was renamed, folded into another skill, or should go
- Report per asset: placement gaps (missing adapter, Claude-only location, `CLAUDE.md` without `AGENTS.md` or the reverse, drifted pairs, per-skill `.claude/skills` links) and wording offenders with file:line. Group placement fixes as automatic vs needs-Flo.
- Suggest an order (smallest or most-used first). Edit nothing.

## Verification

Before reporting done:

- `git status --short`
- `git diff --cached --summary --find-renames` for staged moves
- `chezmoi status`, plus `chezmoi cat` or `chezmoi diff` for symlink adapters when relevant
- every original or new live path exists and resolves as intended after the path-scoped apply; stale renamed paths are gone
- grep the changed files for leftover offenders (`chrome:`, `browser:`, `\$[a-z]`, `mcp__`) outside `agents/openai.yaml` (this skill's own rules table is the one expected hit)
- `scripts/validate_agent_migration.py verify --root <repo>` for repo-level changes
- `codex debug prompt-input "probe"` when Codex skill discovery or instructions changed
- report whether `chezmoi apply` was run and name the exact target paths
- remind Flo about skipped candidates that are good tests for this skill
