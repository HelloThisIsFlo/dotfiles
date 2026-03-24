---
name: UAT regression is human-initiated only
description: The UAT regression skill touches the real OmniFocus database — agents must never autonomously invoke it
type: feedback
---

Never autonomously run the UAT regression skill or any operation that touches the real OmniFocus database. The skill must only run when the user explicitly requests it.

**Why:** The UAT skill creates, edits, moves, completes, and drops real tasks in the user's live OmniFocus database. An agent deciding on its own to "verify changes" by running UAT could create dozens of test tasks without the user's knowledge. This extends SAFE-01/02 beyond just `RealBridge` in code — the principle applies to any path that mutates real OmniFocus data.

**How to apply:** Never suggest or initiate `/uat-regression` as part of a verification step, post-implementation check, or CI-like flow. If verification against real OmniFocus is needed, tell the user to run it themselves. This also applies to one-off MCP tool calls against the real database during non-UAT work.
