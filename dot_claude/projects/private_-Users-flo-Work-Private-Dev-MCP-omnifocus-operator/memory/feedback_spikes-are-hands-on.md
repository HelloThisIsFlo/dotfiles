---
name: Spikes and exploration are hands-on
description: During spike/exploration work, Flo runs experiments himself — Claude provides scaffolding and guide skills, not automated results
type: feedback
---

For exploratory spikes: Flo wants to run experiments himself. The fun part is the exploration.

**Why:** Running experiments and forming conclusions is the valuable learning. Having Claude run them and report back defeats the purpose.

**How to apply:** When doing spike/exploration work:
- Write experiment scripts that Flo can run with `uv run`
- Create a guide skill that walks through each experiment interactively
- Don't pre-fill findings or conclusions — let the skill help Flo build them up
- The go/no-go decision is always Flo's, not Claude's
