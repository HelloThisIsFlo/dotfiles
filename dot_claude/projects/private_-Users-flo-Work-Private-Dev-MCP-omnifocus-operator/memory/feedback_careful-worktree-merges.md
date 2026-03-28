---
name: Careful worktree merges
description: When merging parallel worktree branches, don't blindly take --theirs on code files — inspect conflicts properly
type: feedback
---

After parallel executor agents complete in worktrees, merging their branches can produce conflicts in shared files (especially test files). Don't resolve code file conflicts with blanket `git checkout --theirs` — actually read the conflict markers and combine both sides correctly.

**Why:** During 32.1 gap closure, plans 02 and 03 both modified test files. I resolved conflicts by taking --theirs for test_models.py and test_output_schema.py without properly combining changes. Flo had to fix the merge manually.

**How to apply:**
- For planning docs (STATE.md, ROADMAP.md): taking one side is usually fine since they'll be updated by gsd-tools anyway
- For code/test files: read the actual conflict, understand what each side added, and combine both contributions correctly
- If unsure about a merge resolution, show the conflict to the user instead of guessing
