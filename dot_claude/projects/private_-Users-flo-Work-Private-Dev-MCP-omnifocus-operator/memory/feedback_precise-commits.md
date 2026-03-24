---
name: Precise commits only
description: When asked to commit specific lines, commit ONLY those lines — no whitespace, newline, or formatting changes
type: feedback
---

When the user says "commit just those two lines" or similar, commit EXACTLY and ONLY the specified changes. Do not include any incidental whitespace, trailing newline, or formatting changes — even if they seem harmless.

**Why:** Generated files (like golden master snapshots) follow specific formatting conventions. Editor-introduced changes like trailing newline removal are noise, not intentional. The user was explicit about scope and expects precision.

**How to apply:** Before committing, always review the full `git diff --staged` output and verify every changed line matches what was requested. If there are extra changes (whitespace, newlines, formatting), exclude them or ask.
