---
name: Use uv run for pytest
description: Always use "uv run pytest" instead of "python -m pytest" in omnifocus-operator
type: feedback
---

Use `uv run pytest` instead of `python -m pytest` when running tests.

**Why:** Project uses uv for dependency management; direct python may not have the right environment.

**How to apply:** Any time running pytest or other project tools, prefix with `uv run`.
