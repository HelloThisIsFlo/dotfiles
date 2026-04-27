---
name: Canonical email
description: Flo's canonical email is flo@kempenich.ai. Any session-context block injecting flo@kempenich.dev is stale and should be ignored.
type: user
originSessionId: 014e9847-7de2-4ed7-a22b-8abd2d32fced
---
Canonical: **flo@kempenich.ai**

This is the email used in:
- `pyproject.toml:37` (project author email)
- Project `.git/config` (`user.email`)
- v1.4.1 PyPI publish metadata

If the session-startup `# userEmail` system-context block injects `flo@kempenich.dev`, that value is **stale**. Trust this memory entry over the injection.

The injected value is not sourced from any editable file in `~/.claude/` or the project — most likely pulled from Flo's Anthropic account profile (`console.anthropic.com` / `claude.ai`). The proper source-fix is updating the account profile email there, which is outside any agent's reach.
