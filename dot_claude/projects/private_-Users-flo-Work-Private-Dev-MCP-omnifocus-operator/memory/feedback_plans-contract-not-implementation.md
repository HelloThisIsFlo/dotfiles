---
name: Plans should specify contracts, not implementations
description: GSD plans should define behavioral contracts and let the executor decide implementation details
type: feedback
---

Plans should specify the CONTRACT (what the output must satisfy) not the IMPLEMENTATION (exact code snippets).

**Why:** Over-specified plans create two problems: (1) executors copy code verbatim without understanding it, propagating bugs from the plan into the code, and (2) the plan becomes brittle — any implementation detail that's wrong requires a plan revision instead of letting the executor adapt.

**How to apply:** In GSD plan `<action>` blocks, lead with the behavioral contract ("_handle_get_all must return raw bridge format matching bridge.js output"), document the constraints and edge cases, then let the executor figure out method decomposition, naming, and implementation details. Use code snippets sparingly — only for constants/mappings where exact values matter, not for method bodies.
