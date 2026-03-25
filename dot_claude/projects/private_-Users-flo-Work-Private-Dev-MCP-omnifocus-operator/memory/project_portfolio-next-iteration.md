---
name: Portfolio showcase — next iteration
description: Queued improvements for CODEBASE-SHOWCASE based on reviewer feedback, with Flo's context on failure stories and tradeoffs
type: project
---

Reviewers pegged at senior-not-staff. Remaining gaps to address (with Flo's input):

## 1. Failure Story (HIGH PRIORITY — Flo has content)

**The big one: v1.2 → v1.2.1 architectural cleanup**
- During v1.2, repetition rule was scope creep
- AI agents kept adding features; Flo realized he didn't fully understand parts of the codebase anymore
- Led to v1.2.1 — a full refactoring milestone to regain architectural clarity
- Learning: speed without understanding = debt. Must stay hands-on on architecture even when AI executes.
- This IS the "failure → learning → action" story both reviewers wanted
- v1.2.1 literally IS "recognizing something wasn't right and fixing it"

**Secondary stories:**
- OmniJS `removeTags(array)` was flaky — sometimes works, sometimes doesn't. Crazy debugging.
- Agents made assumptions about OmniFocus behavior that weren't true, despite instructions to not assume
- Bridge behavior had to be empirically verified (27 audit scripts came from this need)

## 2. Problem-First Framing

- Product landing page sells the product; portfolio showcase should sell the engineer
- Both should lead with the problem/constraint, not the architecture
- The tool was developed product-first with agent UX in mind — showcase should make this clearer
- Flo agrees this is important

## 3. Deep Tradeoffs

- SQLite vs bridge-only has real tradeoffs — research exists in `.research/` folder
- IPC vs AppleScript vs other approaches — pre-architecture research
- Could explore `.research/` to surface the tradeoff analysis that happened before code

## 4. "What I'd Do Differently"

- Tricky: side project with full autonomy, so things done "wrong" were actually corrected (v1.2.1)
- Reframe as: "What I DID do differently after learning" — more honest than hypothetical regrets
- The v1.2.1 story covers this naturally

## 5. Scaling — NOT APPLICABLE

- Single user, single local database, local OmniFocus — will never horizontally scale
- Pagination and field selection coming in future milestones (v1.3-v1.4)
- Showcase will be updated as features land
- Don't frame as "scaling limitation" — frame as "scope appropriate to the domain"

**How to apply:** When Flo returns to iterate on the showcase, start with the failure story (v1.2 → v1.2.1) — it's the highest-impact addition and Flo has the context. Then problem-first framing. Then tradeoffs from `.research/`.
