---
name: Use git mv for todo moves
description: Always use git mv (not plain mv) when moving todo files between pending/done directories
type: feedback
---

Use `git mv` instead of plain `mv` when moving todo files between `.planning/todos/pending/` and `.planning/todos/done/`.

**Why:** Flo wants git to track the move as a rename, preserving file history. Plain `mv` shows as delete + add.

**How to apply:** Any time a todo is moved to done (or any file relocation in the planning directory), use `git mv` as the first choice.
