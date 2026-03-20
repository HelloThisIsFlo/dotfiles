---
name: no-redundant-sentinel-tests
description: Don't generate smoke/deletion-guard tests when existing unit tests already cover the imports and behavior
type: feedback
---

Don't create import smoke tests or file-deletion guards when existing tests already import and exercise those models. If 500+ tests use `CreateTaskCommand`, a standalone "can I import it?" test is redundant. Deletion guards that assert old files raise ImportError are "hardcoding the past" — they add no regression value and get in the way if the decision is revisited.

**Why:** User flagged these as weird/unnecessary during Nyquist validation of Phase 20. Existing test coverage is the real validation.

**How to apply:** During gap analysis, classify a requirement as COVERED if existing tests transitively exercise the behavior — even if no single test is a dedicated "smoke test" for it. Only generate new tests for genuinely untested behavior.
