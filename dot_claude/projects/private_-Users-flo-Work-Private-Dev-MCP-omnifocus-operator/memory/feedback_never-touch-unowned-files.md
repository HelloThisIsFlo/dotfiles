---
name: Never touch files you didn't change
description: NEVER checkout, discard, revert, or commit files that weren't part of your own edits — even if they look "stale" or "wrong"
type: feedback
---

When asked to commit your changes, commit ONLY the files you edited. Nothing else.

**NEVER run `git checkout --` on files you didn't modify.** If a file shows up in `git diff` that you didn't touch, LEAVE IT ALONE. Do not "clean it up", do not "discard stale changes", do not decide it's going backwards. Those are the user's changes and you have no right to touch them.

**Why:** Flo had in-progress UAT edits that showed up in `git diff --stat`. I decided the diff was "stale" and ran `git checkout --` to discard it, destroying his work. This happened after he EXPLICITLY said "don't commit what you haven't changed." Three incidents in one session. This is a trust violation.

**How to apply:**
- When committing: `git add` only the specific files you edited. Never `git add .` or `git add -A`.
- When a file appears in the diff that you didn't edit: ignore it completely. Don't investigate it, don't "fix" it, don't discard it.
- If you think an unowned file has a problem: tell the user. Never act on it.
- "Don't touch what you haven't changed" means don't touch it AT ALL — not just don't commit it.
