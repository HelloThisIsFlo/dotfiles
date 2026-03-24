---
name: Read todo files when cross-referencing
description: When mapping todos to milestones, read the todo files themselves — they may contain mapping/deferral decisions
type: feedback
---

When cross-referencing todos against milestones, read the todo files themselves, not just milestone specs.

**Why:** Todo files can contain their own milestone mapping status (e.g., "Intentionally Unmapped" with rationale). Searching only milestone specs for mentions misses decisions documented at the source. This caused an unnecessary deep-dive search when the answer was in the todo file all along.

**How to apply:** During any todo review or cross-reference workflow, read each todo file's content (at least the frontmatter/status) before reporting mapping status. The todo is the primary source of truth about its own disposition.
