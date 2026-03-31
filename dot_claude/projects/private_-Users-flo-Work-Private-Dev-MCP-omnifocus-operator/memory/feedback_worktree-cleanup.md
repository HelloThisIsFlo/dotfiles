---
name: Check worktrees before deleting
description: Always verify worktree branches are merged into main before removing them
type: feedback
---

Before deleting stale worktrees, check if their branches are merged into main.
- **Merged**: safe to delete (worktree + branch).
- **Unmerged**: do NOT delete. Report back to Flo with details so he can decide.

**Why:** Worktrees may contain unmerged work. Deleting without checking risks losing changes.

**How to apply:** Any time Flo asks to clean up worktrees, run `git branch --merged main` or equivalent check before removing.
