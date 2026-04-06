---
name: UAT client shadows validators
description: Claude Desktop pre-validates against JSON Schema, hiding custom Pydantic error messages — test in Claude Code CLI to verify validators work
type: feedback
---

Claude Desktop co-work mode pre-validates tool input against JSON Schema before sending it to the MCP server. This means custom `field_validator` error messages (e.g., "parent cannot be null") may not appear — the client shows a generic schema error instead.

**Why:** Both Claude Desktop (regular) and Claude Code CLI pass input directly to the server, where Pydantic validators fire normally. The shadowing is specific to co-work mode, not the MCP framework.

**How to apply:** Be reactive, not proactive. Don't preemptively warn about this during UAT. If Flo flags a missing custom error message as unexpected, explain the client-side validation behavior and suggest trying via Claude Code CLI. Don't volunteer it unprompted. See `docs/model-taxonomy.md` and `CLAUDE.md` UAT section for the documented convention.
