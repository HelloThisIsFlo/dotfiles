---
name: No context window warnings
description: Context warnings disabled — they caused agents to make autonomous triage/wrap-up decisions
type: feedback
---

Context window warnings are disabled in GSD config. Don't re-enable them or suggest enabling them.

**Why:** The warnings prompted the agent to start making wrap-up decisions autonomously (prioritizing, cutting scope, rushing to commit) — violating Flo's agency principle. Flo is aware of context limits himself and manages them.

**How to apply:** Never suggest re-enabling context warnings. If approaching context limits, don't preemptively triage or wrap up — Flo will decide when to `/clear` or pause. This reinforces the broader rule: don't make decisions on the user's behalf under resource pressure.
