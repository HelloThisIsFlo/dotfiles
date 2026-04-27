---
name: Shipped means passed — don't gate on audit frontmatter
description: For changelog/release work, if a milestone is shipped and STATE.md marks it complete, treat it as passed regardless of audit frontmatter status field
type: feedback
originSessionId: 537336fd-c829-475a-9c93-46184e2506e0
---
If a milestone is shipped and `STATE.md` marks it complete, treat it as passed for downstream work (changelog, release notes, etc.) — regardless of whether the audit frontmatter `status` field reads `passed`, `tech_debt`, or anything else.

**Why:** Flo closes milestones pragmatically. Audit frontmatter is sometimes left in an intermediate state (e.g., `tech_debt`) even after the in-audit decisions resolve everything and the milestone ships. The act of shipping IS the pass. Gating on the frontmatter field creates false blockers.

**How to apply:** For `/update-changelog` and any skill that checks audit status, trust `STATE.md` (`status: complete`) + presence of archive/close commits over the audit frontmatter `status:` value. Don't ask Flo to flip cosmetic fields before proceeding — just proceed.
