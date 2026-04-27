---
name: Maintainability over micro-performance
description: Prefer single code paths and minimal divergence over small perf wins. Milliseconds don't matter; implementation forks do.
type: feedback
originSessionId: d6808e00-4849-4f1a-b1cd-19dac93dd606
---
Don't optimize for milliseconds when the cost is implementation divergence. Single code paths that handle all cases uniformly are preferred over specialized paths that save small amounts of time.

**Why:** The SQLite cache already makes reads crazy-fast compared to bridge (~46ms full snapshot). Multiple `get_all()` calls inside a pipeline are "suboptimal" but cheap enough that they don't matter. The real pain is functions that diverge — implementation-specific branches ("fast path" / "slow path", "mostly this, except for X") create a maintenance burden and are a source of subtle bugs. When parallel code paths accumulate, each feature change has to be verified across all of them.

**How to apply:**
- When weighing options, rank **pattern consistency / single code path** above **100ms-level perf**.
- Don't propose specialized fast paths or divergent repo implementations to shave milliseconds off.
- If perf is in the seconds range (e.g., 3s+ per request for common operations), that IS relevant — raise it. Otherwise, default to the uniform implementation.
- "You can always optimize later" — the presumption is that cleanliness-first leaves optimization reachable, while optimization-first locks in divergence that's hard to undo.
- This reinforces the "Structure Over Discipline" principle in `docs/architecture.md` — paved paths, self-documenting module boundaries, prefer duplication only when paths will GENUINELY diverge (not for micro-perf).
