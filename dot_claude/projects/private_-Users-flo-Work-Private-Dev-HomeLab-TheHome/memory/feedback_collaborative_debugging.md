---
name: Collaborative debugging preference
description: For debugging/investigation sessions, Flo wants to be actively involved — no changes without explicit approval, even small ones
type: feedback
originSessionId: f3b62bc5-3491-4c0f-adf6-4286835b3ee7
---
For debugging and investigation sessions, Flo wants to be actively in the driver's seat.

**Why:** He's learning and wants to understand what's happening, not just get a fix. He's also cautious about unintended side effects on his home infrastructure (HA, k8s cluster, NAS). A past session diagnosed a root cause but didn't apply fixes precisely because he wanted to review and choose.

**How to apply:**
- Never make changes (to HA, repo, configs, services) without explicit "yes, go" approval — even one-line edits.
- Before any action: explain what, why, and the effect. Then wait.
- Share findings from read-only diagnostics (logs, state, config) as you go — summarize before moving on.
- Teach along the way: explain unfamiliar HA/integration/error concepts.
- When multiple fixes are possible, present options + tradeoffs, let Flo pick.
- This is the default mode for anything diagnosis-flavored on the homelab/HA. Normal "just do it" executor mode still applies for simple scripted tasks Flo explicitly directs.
