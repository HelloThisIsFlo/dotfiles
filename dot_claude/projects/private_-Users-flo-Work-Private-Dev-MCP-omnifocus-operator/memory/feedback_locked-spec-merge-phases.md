---
name: Locked spec → merge linearly-dependent phases
description: When a milestone spec is design-locked (multi-session interview + spikes), merge linearly-dependent phases into one rather than defaulting to the roadmapper's small-phase output.
type: feedback
originSessionId: 906fd2bb-fd4b-4233-b8f2-79e2f53658ce
---
When a milestone's design is locked (e.g. multi-session interview + completed pre-implementation spikes), prefer fewer, larger phases over many small ones — merge linearly-dependent phases into one.

**Why:** Phase boundaries in GSD carry discuss → plan → execute → verify ceremony. Those gates exist so the contract can be pressure-tested before committing to the next phase. When the spec is locked, the pressure-testing is already done during the interview/spike phase — the gates become low-value friction, not contract-alignment checkpoints. Flo confirmed this on v1.4.1 (2026-04-19) where the roadmapper produced 4 phases for 51 locked REQs; he asked to merge the first three (linear dependency chain, same deliverable). Final shape was 2 phases (31 + 20 REQs) instead of 4.

**How to apply:** After the roadmapper returns an initial draft, look for:
1. Linear dependency chains (A→B→C with no parallelization opportunity)
2. Same-deliverable grouping (all touching the same fields / same pipeline / same subsystem)
3. Spec maturity signal (design-locked, spikes complete, contract decisions all made)

When all three hold, proactively propose a merge before asking for approval — don't force the user to push back on ceremony. Keep phases separate only when they touch genuinely different subsystems (e.g. v1.4.1 kept Phase 57 "Parent Filter" separate from Phase 56 "Property Surface" — different pipeline, different subsystem).

Size tradeoff is real but manageable: a big phase gets internal structure via plan waves (e.g. "(1) foundation, (2) read, (3) write"), which preserve commit-level checkpoints without phase-boundary ceremony.
