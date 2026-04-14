# Roadmap Restructure (2026-04-12)

## Current roadmap (post-restructure)
- **v1.4** — Response Shaping & Notes Append (field selection, compact output, notes append)
- **v1.5** — UI & Perspectives (show/get perspective, open_task, live UI reads)
- **v1.6** — Production Hardening (retry, crash recovery, serial execution)
- **v1.7** — Project Writes (add_projects, edit_projects)

## Tool count progression
- v1.3.3 (current): 11 tools
- v1.4: 11 (no new tools)
- v1.5: 14 (+show_perspective, get_current_perspective, open_task)
- v1.6: 14 (hardening only)
- v1.7: 16 (+add_projects, edit_projects)

## What was dissolved
- v1.4.1 (fuzzy search) → MAYBE-IDEAS
- v1.4.2 (TaskPaper output) → MAYBE-IDEAS
- v1.4.3 (project writes) → promoted to v1.7
- Mutually exclusive tags (v1.4.3 stretch) → MAYBE-IDEAS

## What was discarded
- `delete_tasks` → DISCARDED-IDEAS (move-to-container is safer)
- `count_tasks`/`count_projects` → DISCARDED-IDEAS (redundant with list tools)

## v1.4 has a pre-planning spike
CSV output format might subsume null-stripping. Spike must run before planning.
See the spike section at top of MILESTONE-v1.4.md.

## App Nap
Between-milestones fix, not a milestone phase. Real pain point — fix when ready.
May reduce v1.6 scope significantly (bridge timeouts might just be App Nap).
