---
name: RRULE serialization boundary decision
description: Decision to move RRULE serialization into repository layer (Option C) for symmetric read/write handling
type: project
---

RRULE serialization/deserialization should live in the repository layer, both directions.

**Why:** The repository already parses RRULE on reads (hybrid.py, adapter.py). Write-side RRULE building was in the service layer (repetition_rule.py), creating an asymmetry where the same concept lived in different layers depending on direction. This was accidental, not a design choice.

**How to apply:**
- Reshape `RepetitionRuleRepoPayload` to carry core types (Frequency, Schedule, BasedOn, EndCondition) instead of pre-serialized bridge data (rule_string, schedule_type, etc.)
- Repository write path calls `build_rrule()`, `schedule_to_bridge()`, `based_on_to_bridge()` before handing to bridge
- Delete `service/repetition_rule.py` — service never touches RRULE concepts
- The `rrule` package becomes consumed only by repository/bridge layer
- This was chosen over full repo-level read types (TaskRepoRow etc.) as the pragmatic fix that achieves symmetry without adding types

**Status:** Decided 2026-04-02, not yet implemented
