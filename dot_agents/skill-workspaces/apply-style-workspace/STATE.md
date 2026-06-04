# Apply Style Skill — Iteration State

## Current status: Iteration 1 complete, user reviewing

## What exists

- **Skill**: `~/.agents/skills/apply-style/` (SKILL.md + references/style-reference.md)
- **Style reference source**: `~/Work/Private/Dev/MCP/omnifocus-operator/STYLE-REFERENCE.md`
- **Test docs**: `~/.agents/skill-workspaces/apply-style-workspace/test-docs/` (4 files)
- **Iteration 1 results**: `~/.agents/skill-workspaces/apply-style-workspace/iteration-1/` (8 runs graded)
- **Grading script**: `~/.agents/skill-workspaces/apply-style-workspace/grade_outputs.py`
- **Evals**: `~/.agents/skill-workspaces/apply-style-workspace/evals/evals.json` (4 test cases, 34 assertions total)
- **Benchmark**: `~/.agents/skill-workspaces/apply-style-workspace/iteration-1/benchmark.json`

## Iteration 1 results

| Eval | With Skill | Without Skill |
|------|-----------|---------------|
| 1 - Rate Limiting (full prose) | **100%** (8/8) | 50% (4/8) |
| 2 - Caching Gotchas (partial style) | **88%** (7/8) | 50% (4/8) |
| 3 - Deploy Modes (restructure) | **100%** (8/8) | 38% (3/8) |
| 4 - Repetition Behavior (real doc) | **100%** (10/10) | 40% (4/10) |
| **Average** | **97%** | **44%** |

## User feedback (verbal, iteration 1)

- "Ridiculously good" — rate limiting, caching, deploy modes all very strong
- "Repetition behaviour is still a bit hard to read" — room for improvement on real doc
- "The deployment mode reference is crazy; yeah, that's insanely good"
- Overall: massive improvement, wants to iterate further

## Next steps

- Iterate on the skill based on feedback (especially eval 4 — repetition behavior readability)
- User will compact context window first, then continue
- Consider: what makes eval 4 "hard to read" — likely the density of empirical data with proofs
- Could add guidance to SKILL.md about handling dense empirical/proof-heavy docs
- After iteration: description optimization, then package
