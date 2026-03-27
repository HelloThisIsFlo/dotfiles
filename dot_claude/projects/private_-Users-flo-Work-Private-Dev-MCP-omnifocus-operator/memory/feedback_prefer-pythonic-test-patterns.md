---
name: Prefer Pythonic test patterns over churn minimization
description: Use pytest.raises(ToolError) not call_tool_mcp() — agent effort is not a constraint, prefer idiomatic patterns
type: feedback
---

Use idiomatic Python test patterns (e.g., `pytest.raises(ToolError)`) instead of compatibility shims (e.g., `call_tool_mcp()`) that minimize assertion churn.

**Why:** Agents do the implementation work, so minimizing lines changed is not a valid trade-off. The codebase should use the cleanest, most Pythonic patterns available. "Less churn" is not a goal when it comes at the cost of code quality.

**How to apply:** When migrating test infrastructure, always prefer the idiomatic new pattern over backward-compatible shims. Rewrite assertions fully rather than using compatibility layers.
