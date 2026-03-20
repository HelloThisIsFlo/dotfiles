---
name: Don't close milestones autonomously
description: Never mark a milestone as shipped/complete — the user has a formal audit+complete process for that
type: feedback
---

Don't mark milestones as shipped or complete. The user has a formal process (`/gsd:audit-milestone` + `/gsd:complete-milestone`) for closing milestones. When asked to clean up a roadmap or remove phases, only do what was asked — don't infer that the milestone should be closed.

**Why:** Milestone completion involves auditing against original intent, which is a separate deliberate step the user runs themselves.

**How to apply:** When editing ROADMAP.md or STATE.md, leave milestone status markers (shipped/in-progress, frontmatter status) unchanged unless the user explicitly asks to close the milestone.
