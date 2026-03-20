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

## Memory-only decisions
- Versioning: v1.x series (v1.1→v1.5), reserve v2.0 for workflow logic

## Feedback
- [Don't close milestones autonomously](feedback_dont-close-milestones.md)
- [No redundant sentinel tests](feedback_no-redundant-sentinel-tests.md) — skip smoke/deletion guards when existing tests already cover the imports
- [Don't rush to wrap up](feedback_dont-rush-to-wrap-up.md) — verify tests catch failures before committing/updating docs
- [UNSET stays at service layer](feedback_unset-is-service-concern.md) — agent-intent logic, never pushed to repos
- [Don't decide priorities](feedback_dont-decide-priorities.md) — recommend approaches, never assign priority or say "low-priority"
- [Use git mv for todo moves](feedback_use-git-mv-for-todos.md) — always `git mv`, not plain `mv`, to preserve file history
