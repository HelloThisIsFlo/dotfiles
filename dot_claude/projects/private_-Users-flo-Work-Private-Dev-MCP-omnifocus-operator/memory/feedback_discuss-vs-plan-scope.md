---
name: Discuss-phase stays out of plan decomposition
description: discuss-phase captures design decisions only. Don't surface plan-wave / task breakdown gray areas — that's plan-phase's job.
type: feedback
originSessionId: d6808e00-4849-4f1a-b1cd-19dac93dd606
---
During `/gsd-discuss-phase`, don't ask about plan decomposition (how many plans, what each plan covers, which tasks come in what wave). That's explicitly the job of `/gsd-plan-phase`, which runs next.

**Why:** The GSD workflow has a clean separation of concerns:
- **discuss-phase** — captures design decisions, contracts, architectural choices.
- **plan-phase** — takes the CONTEXT.md and decomposes the work into executable plans.
Mixing them in discuss-phase pollutes CONTEXT.md with task-breakdown decisions that the planner should own, and creates friction when the user runs plan-phase next ("we already decided this" vs "that was a sketch").

**How to apply:**
- Phase-57-style gray areas: surface contract shapes, naming, architectural patterns, warning placement, semantics — the WHAT and the HOW-AT-A-DESIGN-LEVEL.
- Do NOT surface: wave count, plan split, task ordering, which REQs get bundled together — any of the question "how do we break this into deliverable chunks."
- If the user asks about plan breakdown during discuss-phase, note it but defer to plan-phase.
