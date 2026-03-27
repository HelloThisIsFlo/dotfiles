---
name: No token/time optimization for review skills
description: Don't optimize review-panel or similar skills for token cost or speed — comprehensiveness matters, not efficiency
type: feedback
---

When building skills like review-panel, don't optimize for token cost or execution time. Flo wants maximum comprehensiveness.

**Why:** These skills are run infrequently and the value of catching a missed issue far outweighs saving a few minutes or tokens. Token/time stats are "fun to know" but should never be decision criteria or something we optimize for.

**How to apply:** In eval assertions, don't include token or time comparisons. In skill design, don't add shortcuts or limits to save resources. If there's a tradeoff between thoroughness and speed, always choose thoroughness.
