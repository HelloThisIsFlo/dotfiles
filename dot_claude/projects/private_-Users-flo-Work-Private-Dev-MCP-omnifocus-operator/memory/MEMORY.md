# OmniFocus Operator — Memory Index

## Where to find things
- **Project context & key decisions**: `.planning/PROJECT.md`
- **Current milestone state**: `.planning/STATE.md`
- **GSD config**: `.planning/config.json`
- **Roadmap & milestone specs**: `.research/updated-spec/MILESTONE-v1.*.md`
- **Pending todos**: `.planning/todos/pending/`
- **Research artifacts**: `.research/` (updated-spec, deep-dives, original-spec)

## Critical Safety Rule (repeated here for visibility)
- **SAFE-01/02**: No automated test, CI pipeline, or agent execution may touch `RealBridge`. All automated testing MUST use `InMemoryBridge` or `SimulatorBridge`. RealBridge = manual UAT only.

## User
- [Career context](user_career-context.md) — between jobs, newborn, targeting team lead/staff roles. OmniFocus Operator is primary portfolio piece.

## Project artifacts
- [You-did-good document](project_you-did-good-document.md) — personal imposter syndrome document, V14 final, in `.sandbox/portfolio/you-did-good/`
- [Portfolio next iteration](project_portfolio-next-iteration.md) — queued improvements: failure story (v1.2→v1.2.1), problem-first framing, tradeoffs from research

## Memory-only decisions
- Versioning: v1.x series (v1.1→v1.5), reserve v2.0 for workflow logic

## Feedback
- [Don't close milestones autonomously](feedback_dont-close-milestones.md)
- [No redundant sentinel tests](feedback_no-redundant-sentinel-tests.md) — skip smoke/deletion guards when existing tests already cover the imports
- [Don't rush to wrap up](feedback_dont-rush-to-wrap-up.md) — verify tests catch failures before committing/updating docs
- [UNSET stays at service layer](feedback_unset-is-service-concern.md) — agent-intent logic, never pushed to repos
- [Don't decide priorities](feedback_dont-decide-priorities.md) — recommend approaches, never assign priority or say "low-priority"
- [Use git mv for todo moves](feedback_use-git-mv-for-todos.md) — always `git mv`, not plain `mv`, to preserve file history
- [Plans: contract not implementation](feedback_plans-contract-not-implementation.md) — specify behavioral contracts, let executor decide implementation
- [Split volatile vs uncomputed](feedback_split-volatile-vs-uncomputed.md) — in golden master normalization, separate truly-random from not-yet-implemented fields
- [Facts with justified praise](feedback_facts-with-justified-praise.md) — back evaluative statements with evidence; empty praise is dismissed, facts alone feel clinical, the balance is evidence + honest evaluation
- [Precise commits only](feedback_precise-commits.md) — when asked to commit specific lines, commit ONLY those — no whitespace/newline/formatting changes
- [Read todo files when cross-referencing](feedback_read-todo-files-when-cross-referencing.md) — todo files contain their own mapping/deferral decisions; read them, don't just search milestone specs
- [UAT is human-initiated only](feedback_uat-human-initiated-only.md) — never autonomously invoke UAT regression or any real-OmniFocus mutation; extends SAFE-01/02
- [Respect plan mode boundaries](feedback_respect-plan-mode.md) — don't execute changes during plan mode; write the plan, wait for approval, then implement
- [Spikes are hands-on](feedback_spikes-are-hands-on.md) — during exploration/spike work, Flo runs experiments himself; Claude provides scaffolding + guide skills
- [Prefer Pythonic test patterns](feedback_prefer-pythonic-test-patterns.md) — use pytest.raises(ToolError) not call_tool_mcp(); agent effort is not a constraint
- [Scope of delegation](feedback_scope-of-delegation.md) — "check this one" means exactly one, not all remaining items
- [No token/time optimization](feedback_no-token-time-optimization.md) — review skills prioritize comprehensiveness, not speed or cost
- [NEVER touch files you didn't change](feedback_never-touch-unowned-files.md) — no checkout/discard/commit on unowned files, even if they look wrong
- [Careful worktree merges](feedback_careful-worktree-merges.md) — don't blindly --theirs on code files; read conflicts and combine both sides
- [Thorough post-execution review](feedback_thorough-post-execution-review.md) — cross-reference summaries against codebase; auto-fixes aren't "resolved by definition"
- [Golden master snapshots are human-only](feedback_golden-master-human-only.md) — agents create test infra, never capture/refresh snapshots
