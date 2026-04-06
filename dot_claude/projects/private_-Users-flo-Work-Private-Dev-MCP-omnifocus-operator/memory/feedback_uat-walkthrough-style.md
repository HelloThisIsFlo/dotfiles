---
name: UAT walkthrough style for foundation phases
description: For non-user-facing phases, walk through design decisions instead of mechanical import checks. Run mechanical checks automatically, present decisions for review.
type: feedback
---

For foundation/internal phases (no MCP tool or user-facing changes), UAT should focus on **design decisions**, not mechanical verification.

- Mechanical checks (imports work, values correct, tests pass): run automatically, report results briefly.
- Design decisions (naming conventions, placement, patterns chosen): walk through one at a time, ask if the user agrees.

**Why:** Flo explicitly corrected the mechanical approach — "I don't care; that's mechanical. I would like you to walk me through to make sure I agree with the decisions that were made during this phase."

**How to apply:** When building UAT test lists for foundation/refactoring phases, categorize items as "mechanical" (auto-verify) vs "decision review" (present to user). Lead with decision reviews.
