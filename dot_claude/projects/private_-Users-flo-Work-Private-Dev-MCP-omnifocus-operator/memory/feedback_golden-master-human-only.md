---
name: Golden master snapshot refresh is human-only
description: Agents create test infrastructure but never capture/refresh golden master snapshots — only the user does that
type: feedback
---

Agents can create golden master test cases (the test code/infrastructure) but must NEVER capture or refresh golden master snapshots themselves. Only the human user runs the snapshot capture step.

**Why:** Golden master snapshots are captured from real OmniFocus data via the bridge. Refreshing them is a mutation-adjacent operation that extends SAFE-01/02. The user needs to verify the captured output is correct before it becomes the reference.

**How to apply:** When planning golden master work, split into: (1) agent creates test cases/infrastructure, (2) plan includes an explicit "user runs snapshot capture" step at the end. Never include `--update-snapshots` or equivalent in agent-executable plans.
