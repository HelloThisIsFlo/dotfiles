---
name: Split volatile vs uncomputed fields in test normalization
description: When excluding fields from golden master comparison, separate truly-random from not-yet-implemented
type: feedback
---

When golden master / contract tests exclude fields from comparison, split them into two categories:
- **VOLATILE**: Different every run, will never match (id, url, timestamps)
- **UNCOMPUTED**: Deterministic but the test double doesn't compute them yet

**Why:** When InMemoryBridge learns a new computation (e.g., effectiveDueDate = dueDate for simple cases), you just remove it from UNCOMPUTED and the contract test automatically starts verifying it. With a single DYNAMIC set, you'd have to remember which fields are skippable vs which are genuinely untestable.

**How to apply:** Use `DYNAMIC_X_FIELDS = VOLATILE_X_FIELDS | UNCOMPUTED_X_FIELDS` so existing code using DYNAMIC still works, but the split is visible and maintainable.
