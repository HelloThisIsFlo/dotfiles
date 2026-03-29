---
name: Thorough post-execution review
description: After phase execution, do a real audit of summaries against codebase — don't just skim summaries
type: feedback
---

Post-execution reviews must cross-reference summaries against actual codebase state, not just summarize the summaries.

**Why:** After Phase 33, surface-level scan missed: stale forward-declared exclusion sets weakening the consolidation safety net, dead imported constant, validate.py not registered as error consumer, and unplanned behavior changes in extracted helper. User had to push twice before getting a real review.

**How to apply:**
- When asked to review execution results, READ the actual files — especially test infrastructure, not just the summaries
- Auto-fixes are not "resolved by definition" — check if the fix was COMPLETE (e.g., temporary scaffolding cleaned up)
- "Tests pass" ≠ "invariants maintained" — look for weakened safety properties, not just failures
- Treat deviations and auto-fixes as the highest-priority review items, not dismissable footnotes
