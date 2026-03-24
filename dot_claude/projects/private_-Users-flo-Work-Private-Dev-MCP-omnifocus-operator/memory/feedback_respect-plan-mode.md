---
name: Respect plan mode boundaries
description: Don't execute changes during plan mode — write the plan, wait for approval, then implement
type: feedback
---

Plan mode means plan ONLY. Write the plan file, ask questions, call ExitPlanMode. Do NOT edit source files, create new files, or make any changes until the user approves the plan.

**Why:** Flo values agency. The plan approval step exists so he can review, redirect, or reject before anything changes. Executing during plan mode bypasses his control.

**How to apply:** When plan mode is active, the only writable file is the plan file itself. Everything else is read-only until ExitPlanMode is called and the user approves.
