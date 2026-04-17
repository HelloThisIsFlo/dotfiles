---
name: Don't hand-wave bugs with threshold/knob tweaks
description: Never propose "bump the threshold / raise the timeout / add a retry" as a fix for a bug with unknown root cause. Mitigation ≠ fix. Prioritization is Flo's call, not Claude's.
type: feedback
originSessionId: c39eb5cb-f872-4d48-a02f-fb7b8faa837c
---
Never propose "raise the threshold", "bump the timeout", "add a retry", or similar magic-number tweaks as a **fix** for a bug whose root cause hasn't been verified. That's mitigation dressed up as solution — and it's explicitly against what this project stands for.

**Why:** During v1.4 audit UAT (2026-04-17), I hit an MCP progress-notification disconnect (a known issue with an existing empirical mitigation via `PROGRESS_NOTIFICATION_MIN_BATCH_SIZE = 3`). Without understanding the root cause, I proposed bumping the threshold to 20. Flo's response (verbatim): *"If you send 21 items, are we okay with having a bug at 21 items? It's ridiculous."* The whole project is framed around reliability — see README "Reliable, simple, debuggable access" and PROJECT.md "executive function infrastructure that works at 7:30am". Duct-tape fixes are antithetical to that.

**How to apply:**
- When a bug surfaces, **separate** "what's the root cause" from "what do we do about it now." Don't conflate them.
- If root cause is unknown: say so explicitly. Propose an **investigation plan**, not a knob-tweak. Evidence first, fix second.
- If Flo decides to prioritize shipping over fixing, **he decides**. Claude's job is to frame options honestly: "this is a real bug with no verified fix; we can either investigate root cause now, or defer with a todo — your call." Never preemptively offer the defer path as a solution.
- When a mitigation already exists in the codebase with a comment admitting uncertainty (like "precise mechanism NOT verified"), **treat that comment as a red flag**, not permission to stack more mitigation on top. The next audit will be harder, not easier.
- Relevant todos capturing root-cause investigations (rather than code fixes) are legitimate — the investigation IS the work.
