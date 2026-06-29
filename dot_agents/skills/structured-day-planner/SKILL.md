---
name: structured-day-planner
description: Update Flo's Structured daily planner from natural language. Use when the user asks to update, reorganize, clean up, reschedule, color-code, icon-code, split, log, or reconcile tasks/events/time blocks in Structured, especially today's plan, including messy voice-transcribed updates, quarter-hour scheduling, overlap handling, recurring task instances, travel/appointment splitting, and Structured built-in icons/colors.
---

# Structured Day Planner

Update the user's Structured day plan with careful time hygiene, visual categorization, and explicit conflict handling.

## Workflow

1. Read the current Structured plan first.
   - Use today's plan for relative requests like "today" or "my plan of the day".
   - Use the user's current timezone when available.
   - Preserve existing tasks unless the user clearly changes, replaces, completes, or removes them.

2. Parse the user's update into proposed changes.
   - Treat voice-transcription quirks generously.
   - If the user gives conflicting corrections in one message, the latest correction wins.
   - Split compound events into useful blocks: travel there, appointment, travel back, follow-up activity.
   - For recurring tasks, change only today's occurrence by default. Do not edit the whole series unless requested.

3. Apply every unambiguous change.
   - Do not wait on unrelated ambiguities before making clear updates.
   - Mark completed past/logged blocks complete when the user says they already happened.
   - Remove accidental/log-only blocks only when the user says they are not needed.

4. Stop and ask about ambiguous or conflicting changes.
   - Ask before deleting, moving, or replacing an existing task that might still be intended.
   - Ask before resolving overlaps.
   - Summarize what was already changed, then list the unresolved choices.

5. Verify by reading the plan back.
   - Confirm no unintended overlaps remain.
   - Confirm task titles, times, colors, and `symbol` values persisted.
   - Report concise final schedule changes and assumptions.

## Time Rules

- Start and end every timed block on a quarter-hour boundary: `:00`, `:15`, `:30`, or `:45`.
- Durations may be any length that preserves quarter-hour start/end boundaries.
- If the user gives a precise non-quarter time, ask before rounding unless the intended rounding is obvious and low-risk.
- Do not create overlapping blocks unless the user explicitly confirms the overlap is intentional.
- If a duration is missing but the context makes one natural, infer minimally and state the assumption.

## Overlaps and Ambiguity

When overlap or duplicate intent appears, apply unrelated clear edits first, then ask.

Offer concrete options when useful:

- Move one block.
- Shorten one block.
- Delete/cancel one block.
- Split one block around the other.
- Split parallel time between tasks.
- Keep the overlap only if the user confirms it is intentional.

Common patterns:

- Parallel work:
  - If the user says two tasks happened in parallel, suggest dividing the shared time between them.
  - Example: "X and Y both happened 10:00-11:00" -> offer 10:00-10:30 X and 10:30-11:00 Y.
  - Never choose the split without confirmation.

- Interrupted work:
  - If a task started, was interrupted, and finished later, suggest splitting it into "Start <task>" and "Finish <task>" around the interruption.
  - Example: Start daily review -> call -> Finish daily review.
  - Ask if order or timing is unclear.

- Duplicate or superseded task:
  - If an existing task says "Daily review" in the morning and the user says "I'll do daily review at 2 p.m.", ask whether to move/delete the morning task or create another review.
  - Do not silently duplicate or remove the old block.

## Visual Categorization

- Use Structured's built-in `symbol` field for icons. Do not use emoji prefixes in task titles unless the user asks.
- Read `references/structured-icons.md` when choosing icons.
- Use colors to make categories visually distinct, but do not hard-code a permanent category-to-color palette.
- Prefer continuity with the user's existing color habits on that day.
- If the day has no obvious pattern, choose distinct colors from the available palette: `day`, `dawn`, `sunshine`, `nature`, `forest`, `twilight`, `night`, `midnight`, `classic`.
- After setting a `symbol`, read the task back. Structured accepts only a curated subset of icon names; readback is the verification step.

## Response Style

- Keep updates concise.
- If asking after partial updates, use this shape:
  - "I updated X and Y."
  - "I am unsure about Z because it overlaps/duplicates A."
  - "Options: move A, shorten B, split the time, or keep both overlapping."
- Final response should list the resulting schedule and any unresolved questions.
