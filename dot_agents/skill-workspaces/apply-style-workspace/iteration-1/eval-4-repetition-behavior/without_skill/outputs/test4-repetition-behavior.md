# OmniFocus Repetition Behavior: Empirical Reference

> Empirically verified on OmniFocus 4.7+ (April 2026), BST (UTC+1).
> All findings tested via OmniFocus Operator MCP server against real OmniFocus behavior.
> Intended for agents working on OmniFocus Operator -- treat as ground truth.

---

## 1. The Three Schedule Types

OmniFocus offers three repetition schedule types. They differ in what date is fed into the RRULE engine at completion time.

### Regularly (No Catch-Up)

Next occurrence calculated from the **previously scheduled date**, not the completion date. If the next occurrence falls in the past, it stays there -- you must complete again to advance, one step at a time.

**Verified:** Task due Sat Mar 30 at 10 PM, completed Thu Apr 2 -- required 3 completions to reach the present. Each advanced exactly one day on the grid.

### Regularly with Catch-Up

Same fixed calendar grid as "regularly," but **skips past occurrences** that have already passed. One completion jumps to the next future occurrence. The check is **time-level** -- considers both date AND time when determining if a grid point is "in the future" (see Section 3).

**Verified:** Same task -- one completion jumped straight to Thu Apr 2 at 10 PM (next future daily slot). Original time preserved.

### From Completion

Next occurrence calculated from the **completion date**. The schedule floats based on when you actually complete it. The check is **day-level** -- the completion day itself never counts as a valid next occurrence, regardless of time-of-day (see Section 3).

**Verified:** Same task -- one completion created next occurrence on Fri Apr 3 at 10 PM. The interval (1 day) was applied from the completion date.

---

## 2. Time Preservation (Not Drift)

A deep research report claimed "from completion" causes the due *time* to drift to the completion timestamp, while "regularly + catch up" preserves it. **This is incorrect at every granularity tested.**

### Test Results

- **Weekly BYDAY** -- Tasks repeating WE+FR, due at 10 PM BST. Completed 21+ hours off from original time. All three modes preserved 10 PM.
- **Daily** -- Tasks repeating daily at 10 PM BST. Completed at various times. All three modes preserved 10 PM.
- **Hourly** -- Task repeating every 2 hours from 10 AM BST, completed at 12:36 PM. Next occurrence: 2 PM (on the original 10/12/2/4 grid, not 2:36 PM).

### Conclusion

**All three modes preserve the original RRULE time grid at every granularity tested (hourly, daily, weekly).** OmniFocus's rounding mechanism prevents time drift. The RRULE generates a fixed grid of valid times; both catch-up and from-completion find the next point on that grid -- they never shift the grid itself.

The deep research report's claim about time drift as a key differentiator is **wrong**.

---

## 3. The Fundamental Asymmetry: Day-Level vs Time-Level

The real difference between catch-up and from-completion is **what granularity each mode uses when deciding whether an occurrence is "in the past."**

### The Rule

| Mode | Granularity | Behavior |
|------|-------------|----------|
| **Catch-up** | **Time-level** | Same-day grid point counts as "future" if its exact time hasn't passed yet |
| **From-completion** | **Day-level** | Completion day NEVER counts, regardless of time-of-day |

### Proof: From-Completion Skips Today Even When Time Is Still Future

- Task due **today** (Friday) at 10 PM BST, repeating WE+FR, from-completion
- Completed at 12:36 PM BST -- over 9 hours before due time
- Next occurrence: **Wed Apr 8** at 10 PM (not today)

Even though Friday is a BYDAY match and 10 PM was 9+ hours away, from-completion skipped to next Wednesday. **Today never counts for from-completion, period.**

### Proof: Catch-Up Skips Today When Time HAS Passed

- Task overdue from Wednesday at 10 AM BST, repeating WE+FR, catch-up
- Today's grid point: Friday at 10 AM -- already passed (it's afternoon)
- Completed at 12:36 PM BST
- Next occurrence: **Wed Apr 8** at 10 AM (not today)

Catch-up skipped today because the 10 AM grid point had already passed.

### Contrast: Catch-Up Lands on Today When Time Is Still Future

- Task overdue from Wednesday at 10 PM BST, repeating WE+FR with INTERVAL=2, catch-up
- Today's grid point: Friday at 10 PM -- still future (it's ~noon)
- Next occurrence: **today** (Friday) at 10 PM

Catch-up landed on today because the 10 PM grid point was still ahead.

### Combined Truth Table

| Scenario | From-completion | Catch-up |
|----------|----------------|----------|
| Today is a match day, time still future | **Skips today** | **Lands on today** |
| Today is a match day, time already past | **Skips today** | **Skips today** |
| Today is NOT a match day | Finds next match | Finds next match |

This asymmetry is the single most important behavioral difference between the two modes for BYDAY patterns.

---

## 4. Late and Early Completion with BYDAY

### Late Completion (Overdue Task)

Tasks repeating weekly on WE+FR, due Wed Apr 1 at 10 PM (overdue). Completed Fri Apr 3 at ~1 AM.

| Schedule | New Due | Explanation |
|----------|---------|-------------|
| Regularly (no catch-up) | **Fri Apr 3** at 10 PM | Next in WE->FR sequence after Wed. Still overdue until 10 PM. |
| Regularly + Catch Up | **Fri Apr 3** at 10 PM | Same grid, skipped past Wed, found Fri (still future at 1 AM). |
| From Completion | **Wed Apr 8** at 10 PM | `firstDateAfterDate(Friday)` -> next Wed. **Skipped today entirely.** |

From-completion created a **5-day gap** compared to catch-up. This is because from-completion's day-level rounding eliminates Friday, while catch-up's time-level check saw that Friday at 10 PM was still in the future.

### Early Completion (Before Due Date)

Tasks repeating weekly on WE+FR, due Wed Apr 8 at 10 PM (in the future). Completed Fri Apr 3 (5 days early).

| Schedule | New Due | Explanation |
|----------|---------|-------------|
| Regularly (no catch-up) | **Fri Apr 10** at 10 PM | Next in WE->FR sequence after the scheduled Wed Apr 8. |
| Regularly + Catch Up | **Fri Apr 10** at 10 PM | Same as above -- nothing to catch up when completing early. |
| From Completion | **Wed Apr 8** at 10 PM | `firstDateAfterDate(Fri Apr 3)` -> Wed Apr 8. **Comes back sooner.** |

When completing early, from-completion brings the task back **sooner** than regularly. The regularly modes advance from the scheduled date (Wed -> Fri), while from-completion finds the next matching BYDAY after the completion date (Fri -> Wed).

**Agent implication:** If a user wants to "get ahead" on a BYDAY task by completing it early, from-completion will bring it back sooner than they might expect.

---

## 5. INTERVAL >= 2 Grid Reset

The deep research report claimed from-completion resets the alternating week grid while catch-up preserves it. **Confirmed -- the divergence is dramatic.**

### Test Setup

Tasks repeating every 2 weeks on WE+FR, due Wed Apr 1 at 10 PM (overdue). Completed Fri Apr 3 at ~noon.

| Schedule | New Due | Gap from Completion |
|----------|---------|---------------------|
| Regularly + Catch Up | **Fri Apr 3** at 10 PM | **0 days** (tonight!) |
| From Completion | **Fri Apr 17** at 10 PM | **14 days** |

### Why This Happens

- **Catch-up** preserved the original biweekly grid. Apr 1 (Wed) and Apr 3 (Fri) were in the same cycle. Since Fri Apr 3 at 10 PM was still future at ~noon, it landed there.
- **From-completion** reset the grid from the completion date. With INTERVAL=2, it applied a 2-week minimum gap from Fri Apr 3, finding Fri Apr 17.

**14-day difference between the two modes.** For tasks with INTERVAL >= 2, the choice between catch-up and from-completion has massive practical consequences. Agents should flag this when setting up biweekly or less frequent BYDAY patterns.

---

## 6. Repeat Limits and Catch-Up

### Do Skipped Occurrences Count Against Repeat Limits?

**No.** Empirically verified.

- Task created with `end: {occurrences: 6}`, due 5 days ago, daily, catch-up
- Completed once -- catch-up skipped 4 past occurrences
- New `end` value: `{occurrences: 5}`

Count decremented by **1** (from 6 to 5), not by 5. Only the actual completion counted. The 4 skipped occurrences were free.

Confirms the OmniFocus 4.7 manual's statement -- upgraded from "documented" to "empirically verified."

---

## 7. Missing Anchor Date Behavior

When `basedOn` (anchor) points to a date property that is **not set**, OmniFocus handles it gracefully but potentially surprisingly.

### What OmniFocus Does NOT Do

- Does NOT refuse to repeat
- Does NOT silently skip the repetition
- Does NOT fall back to the task's creation date

### What Actually Happens

1. **Creates the missing anchor date from scratch** on the next occurrence
2. Uses the **completion date** for the date portion (not the creation date)
3. Uses the **user's configured default time** for that date type (from OmniFocus Settings -> Dates & Times) for the time portion
4. Shifts any other existing dates forward proportionally
5. Dates that were never set remain unset

### How We Proved This

- **Experiment 1 (same-day):** Created and completed tasks within minutes. Ruled out refusal/skip. Showed missing anchor is created from scratch. Could not distinguish creation vs completion date (both same day).
- **Experiment 2 (cross-day):** Created tasks Apr 2, completed Apr 3. All new anchors landed on **Apr 4** (completion + 1 day), not Apr 3 (creation + 1 day). Definitively proved **completion date fallback**.
- **Experiment 3 (time verification):** Compared new anchor times against OmniFocus defaults:

| Anchor Type | New Time (BST) | Setting |
|-------------|----------------|---------|
| due_date | 19:00 | Default time for due dates: **19:00** |
| defer_date | 08:00 | Default time for defer dates: **08:00** |
| planned_date | 09:00 | Default time for planned dates: **09:00** |

### The Complete Algorithm

```
1. Take the COMPLETION DATE (date portion only)
2. Apply the repeat interval (e.g., +1 day for FREQ=DAILY)
3. Set the TIME to the user's configured default for that date type:
   - due_date     -> Settings > "Default time for due dates"
   - defer_date   -> Settings > "Default time for defer dates"
   - planned_date -> Settings > "Default time for planned dates"
4. This becomes the new anchor date on the next occurrence
5. Any other dates that WERE set shift forward by the same delta
6. Any dates that were NOT set remain unset
```

Behavior is consistent across all three schedule types.

### MCP Server Warning

Current warning text is **incorrect**:

> "OmniFocus will fall back to the task's creation date as the anchor."

Recommended replacement:

> "OmniFocus will create the missing {anchor_field} on the next occurrence using the completion date and the user's default time for {date_type} (configured in Settings -> Dates & Times). This produces a valid but potentially surprising schedule. Set the {anchor_field} explicitly for predictable repetition behavior."

---

## 8. Decision Guide for Agents

### `regularly_with_catch_up` (Recommended Default)

Use when:
- Task is tied to specific calendar days (standup every MWF, rent on the 1st)
- User wants to skip over missed occurrences without tapping through them
- User might complete early and wants today's occurrence to still count (if time hasn't passed)

### `regularly` (No Catch-Up)

Use when:
- User explicitly needs to process every missed occurrence (e.g., logging daily entries)
- Missing an occurrence has real consequences that can't be skipped

### `from_completion`

Use when:
- Minimum time gap between occurrences matters more than the specific day
- Examples: "water plants every 10 days," "replace filter every 3 months"

**Caution with BYDAY patterns** -- from-completion can produce surprising results:
- Completion day never counts, even if due time is hours away
- Late completion skips current day entirely (landed on next Wednesday instead of today's Friday)
- Early completion brings the task back sooner than expected
- INTERVAL >= 2 resets the week grid, potentially shifting by 14+ days vs catch-up

### Always Set the Anchor Date Explicitly

- If `basedOn` points to an unset date field, OmniFocus creates it using completion date + default time
- This works but is rarely intentional and produces user-specific results (depends on their Settings)
- Warn the user; don't silently allow it

---

## 9. Untested Areas

The following have **not** been empirically verified -- do not treat as ground truth:

- **Monthly patterns** -- `onDates: [1, 15]` and `on: {last: "friday"}` with from-completion. Expected to follow the same algorithm, but monthly edge cases (month boundaries, varying lengths) could surprise.
- **Minutely frequency** -- Hourly showed no time drift, but minutely rounding may behave differently.
- **Time drift at very fine granularity with large offsets** -- All hourly tests completed within a few hours of due time. Completing a 2-hourly task 18 hours late might reveal drift not visible in our tests.

---

## Methodology

- All experiments used `omnifocus-operator-2:add_tasks` to create tasks and `omnifocus-operator-2:get_task` to query results after completion
- Task IDs persist across repetition completions -- same ID returns the new occurrence
- Times verified against user's OmniFocus Settings -> Dates & Times (screenshot confirmed: due=19:00, defer=08:00, planned=09:00 BST)
- Experiments conducted April 2-3, 2026, OmniFocus 4.7+, BST (UTC+1)

### Verification Scorecard

| Claim | Status | Source | Notes |
|-------|--------|--------|-------|
| Time drift for from_completion | **DISPROVEN** | Deep research report | Time preserved at hourly, daily, and weekly granularity |
| From-completion: today never counts | **CONFIRMED** | Experiment Q1 | Day-level rounding -- skips today even with 9+ hours remaining |
| Catch-up: checks exact time, not just day | **CONFIRMED** | Experiments Q2 + IV1 | Lands on today if time is future; skips if time has passed |
| Early completion date difference | **CONFIRMED** | Experiment EC1-3 | From-completion finds next BYDAY after completion; can return sooner |
| Late completion date difference | **CONFIRMED** | Part 3 BYDAY test | From-completion skips current day; catch-up lands on nearest future grid point |
| INTERVAL >= 2 grid reset | **CONFIRMED** | Experiment IV1-2 | 14-day divergence observed; from-completion resets alternation grid |
| Skipped occs don't count against limits | **CONFIRMED** | Experiment Q4 | `end.occurrences` decremented by 1, not by number of skipped days |
| Catch-up preserves original time | **CONFIRMED** | Multiple experiments | But so does from-completion -- not a differentiator |
| No time drift at hourly granularity | **CONFIRMED** | Experiment Q5 | Landed on original 2-hour grid, not completion_time + interval |
| Missing anchor uses creation date | **DISPROVEN** | Experiment 2 (cross-day) | Uses completion date + user's default time settings |
| Missing anchor creates the date | **CONFIRMED** | Experiment 1 | OmniFocus creates anchor date from scratch; doesn't refuse or skip |
| Monthly from-completion behavior | **UNTESTED** | -- | Expected same algorithm but unverified |
