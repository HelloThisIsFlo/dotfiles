---
name: dont-rush-to-wrap-up
description: Don't rush to update docs/commit after writing tests — verify tests actually catch failures first
type: feedback
---

After writing tests, don't immediately move to committing and updating VALIDATION.md. The user wants to verify the tests are actually effective (e.g., by making them fail). Stay in the "working together" mode — wait for confirmation that the tests are good before wrapping up.

**Why:** User was annoyed when I wrote tests and immediately started committing + updating docs without verifying the tests actually catch the failures they're supposed to catch.

**How to apply:** After writing tests, run them green, then pause. Say something like "tests pass — want to verify they catch failures before I commit?" or just wait for the user's signal.
