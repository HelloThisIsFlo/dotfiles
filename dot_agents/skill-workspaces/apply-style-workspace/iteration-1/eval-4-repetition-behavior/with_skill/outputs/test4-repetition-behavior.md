# OmniFocus Repetition Behavior: Empirical Reference

Empirically verified behavior for OmniFocus repetition scheduling, tested via the OmniFocus Operator MCP server. All findings validated on OmniFocus 4.7+ (April 2026) in BST (UTC+1).

- **Audience**: agents working on OmniFocus Operator
- **Trust level**: ground truth — every claim tested against real OmniFocus behavior, not inferred from docs

---

## The Three Schedule Types

OmniFocus offers three repetition schedule types. The key difference: **what date feeds into the RRULE engine on completion.**

| Type | Input to RRULE | Missed occurrences |
|------|---------------|-------------------|
| 🔄 `regularly` | Previously scheduled date | Stay in the past — must tap through one by one |
| ✅ `regularly_with_catch_up` | Previously scheduled date | Skips past them — one completion jumps to next future slot |
| ⚠️ `from_completion` | Completion date | N/A — schedule floats based on when you complete |

### 🔄 Regularly (no catch-up)

- Next occurrence calculated from the **previously scheduled date**
- If next occurrence falls in the past, it stays there — complete again to advance
- **Verified**: task due Sat Mar 30 at 10 PM, completed Thu Apr 2 => required 3 completions to reach present (one grid step per completion)

### ✅ Regularly with Catch Up

- Same fixed calendar grid as 🔄 `regularly`, but skips past occurrences
- One completion jumps to next **future** occurrence on the original schedule
- Check is **time-level** — considers both date AND time (see Part 3)
- **Verified**: same task, one completion jumped straight to Thu Apr 2 at 10 PM (next future daily slot, original time preserved)

### ⚠️ From Completion

- Next occurrence calculated from the **completion date** — schedule floats
- Check is **day-level** — the completion day itself **never** counts as valid (see Part 3)
- **Verified**: same task, one completion => Fri Apr 3 at 10 PM (interval applied from completion date)

---

## Time Preservation (Not Drift)

A deep research report claimed `from_completion` causes due *time* drift to the completion timestamp while catch-up preserves the original time. **This is wrong.**

> [!important] All three modes preserve the original RRULE time grid
>
> - **Weekly BYDAY**: tasks repeating WE+FR at 10 PM, completed 21+ hours off => all three modes preserved 10 PM
> - **Daily**: tasks repeating daily at 10 PM, completed at various times => all three modes preserved 10 PM
> - **Hourly**: task repeating every 2 hours from 10 AM, completed at 12:36 PM => next occurrence at 2 PM (on the 10/12/2/4 grid, not 2:36 PM)
>
> OmniFocus's rounding mechanism prevents drift — the RRULE generates a fixed grid of valid times, and both ✅ catch-up and ⚠️ from-completion find the next point on that grid. **They never shift the grid itself.**

The deep research report's claim about time drift as a key differentiator is ❌ **disproven**.

---

## The Fundamental Asymmetry — Day-Level vs Time-Level

The real difference between ✅ catch-up and ⚠️ from-completion is **what granularity each mode uses when deciding whether an occurrence is "in the past."**

> [!important] The rule
>
> - ✅ **Catch-up** checks at the **time-level** — a same-day grid point counts as "future" if its exact time hasn't passed yet
> - ⚠️ **From-completion** checks at the **day-level** — the completion day itself NEVER counts, regardless of time-of-day

### Proof: ⚠️ From-completion skips today even when time is still future

- Task due **today** (Friday) at 10 PM BST, repeating WE+FR, `from_completion`
- Completed at 12:36 PM BST — over 9 hours before due time
- Next occurrence: **Wed Apr 8** at 10 PM (not today)
- 🔑 Friday is a BYDAY match and 10 PM was 9+ hours away, but ⚠️ from-completion skipped to next Wednesday. **Today never counts, period.**

### Proof: ✅ Catch-up skips today when time HAS passed

- Task overdue from Wednesday at 10 AM BST, repeating WE+FR, `catch_up`
- Today's grid point: Friday at 10 AM — already passed (it's afternoon)
- Completed at 12:36 PM BST
- Next occurrence: **Wed Apr 8** at 10 AM (not today)
- 🔑 Catch-up skipped today because the 10 AM grid point had already passed

### Contrast: ✅ Catch-up lands on today when time is still future

- Task overdue from Wednesday at 10 PM BST, repeating WE+FR with `INTERVAL=2`, `catch_up`
- Today's grid point: Friday at 10 PM — still future (~noon now)
- Next occurrence: **today** (Friday) at 10 PM
- 🔑 Catch-up landed on today because 10 PM was still ahead

### Combined truth table

| Scenario | ⚠️ From-completion | ✅ Catch-up |
|----------|-------------------|------------|
| Today is a match day, time still future | **Skips today** | **Lands on today** ✅ |
| Today is a match day, time already past | **Skips today** | **Skips today** |
| Today is NOT a match day | Finds next match | Finds next match |

> [!warning] This asymmetry matters
>
> This is the single most important behavioral difference between the two modes for BYDAY patterns.

---

## Late and Early Completion with BYDAY

### Late completion (overdue task)

Tasks repeating weekly on WE+FR, due Wed Apr 1 at 10 PM (overdue). Completed Fri Apr 3 at ~1 AM.

| Schedule | New due | Explanation |
|----------|---------|-------------|
| 🔄 Regularly | **Fri Apr 3** at 10 PM | Next in WE→FR sequence after Wed. Still overdue until 10 PM. |
| ✅ Catch Up | **Fri Apr 3** at 10 PM | Same grid, skipped past Wed, found Fri (still future at 1 AM). |
| ⚠️ From Completion | **Wed Apr 8** at 10 PM | `firstDateAfterDate(Friday)` → next Wed. **Skipped today entirely.** |

- ⚡ **5-day gap** — ⚠️ from-completion's day-level rounding eliminates Friday, while ✅ catch-up's time-level check saw Friday at 10 PM was still future

### Early completion (before due date)

Tasks repeating weekly on WE+FR, due Wed Apr 8 at 10 PM (in the future). Completed Fri Apr 3 (5 days early).

| Schedule | New due | Explanation |
|----------|---------|-------------|
| 🔄 Regularly | **Fri Apr 10** at 10 PM | Next in WE→FR sequence after scheduled Wed Apr 8. |
| ✅ Catch Up | **Fri Apr 10** at 10 PM | Same as above — nothing to catch up when completing early. |
| ⚠️ From Completion | **Wed Apr 8** at 10 PM | `firstDateAfterDate(Fri Apr 3)` → Wed Apr 8. **Comes back sooner.** |

- 🤔 When completing early, ⚠️ from-completion brings the task back **sooner** than 🔄 regularly
  - Regularly modes advance from the scheduled date (Wed → Fri)
  - From-completion finds the next matching BYDAY after the completion date (Fri → Wed)

> [!warning] Agent implication
>
> - If a user wants to "get ahead" on a BYDAY task by completing early, ⚠️ from-completion will bring it back sooner than they expect

---

## INTERVAL >= 2 Grid Reset — 🤯 Confirmed

The deep research report claimed ⚠️ from-completion resets the alternating week grid while ✅ catch-up preserves it. **Confirmed — the divergence is dramatic.**

### Test setup

Tasks repeating every 2 weeks on WE+FR, due Wed Apr 1 at 10 PM (overdue). Completed Fri Apr 3 at ~noon.

| Schedule | New due | Gap from completion |
|----------|---------|-------------------|
| ✅ Catch Up | **Fri Apr 3** at 10 PM | **0 days** (tonight!) |
| ⚠️ From Completion | **Fri Apr 17** at 10 PM | **14 days** |

### 🤯 14-day divergence

- ✅ **Catch-up** preserved the original biweekly grid
  - Grid had Apr 1 (Wed) and Apr 3 (Fri) in the same cycle
  - Fri Apr 3 at 10 PM still future at ~noon => landed there
- ⚠️ **From-completion** reset the grid from completion date
  - `INTERVAL=2` applied 2-week minimum gap from Fri Apr 3
  - Next matching WE or FR: Fri Apr 17

> [!important] Massive practical consequence
>
> - For tasks with `INTERVAL >= 2`, the choice between ✅ catch-up and ⚠️ from-completion can shift scheduling by **14+ days**
> - Agents should flag this to users when setting up biweekly or less frequent BYDAY patterns

---

## Repeat Limits and Catch-Up

**Do skipped occurrences count against repeat limits?** No.

- Task created with `end: {occurrences: 6}`, due 5 days ago, daily, `catch_up`
- Completed once — catch-up skipped 4 past occurrences
- New `end` value: `{occurrences: 5}`
- Count decremented by **1** (from 6 to 5), not by 5
- Only the actual completion counted — the 4 skipped occurrences were free

> [!note] Confirmation level
>
> - This confirms the OmniFocus 4.7 manual's statement
> - Upgraded from "documented" to "empirically verified"

---

## Missing Anchor Date Behavior

When `basedOn` (anchor) points to a date property that is **not set** on the task, OmniFocus handles it gracefully but potentially surprisingly. 🫠

> [!warning] What happens when the anchor date field is not set?
>
> OmniFocus creates the missing anchor date from scratch on the next occurrence
>
> - Uses the **completion date** (not the creation date) for the date portion
> - Uses the **user's configured default time** for that date type (Settings → Dates & Times) for the time portion
> - Shifts any other existing dates forward proportionally
> - Dates that were never set remain unset
>
> Valid but potentially surprising => **Set the anchor date explicitly for predictable behavior**

### How we proved this

- **Experiment 1 (same-day)**: created and completed tasks within minutes
  - Ruled out that OmniFocus refuses or skips
  - Showed missing anchor date is created from scratch
  - Could not distinguish creation vs completion date (both same day)
- **Experiment 2 (cross-day)**: created tasks on April 2, completed on April 3
  - All new anchor dates landed on **April 4** (completion + 1 day), not April 3 (creation + 1 day)
  - Definitively proved **completion date fallback**, disproving creation date hypothesis
- **Experiment 3 (time verification)**: compared new anchor times against OmniFocus defaults

| Anchor type | New time (BST) | Setting | Match |
|-------------|----------------|---------|-------|
| `due_date` | 19:00 | Default time for due dates: 19:00 | ✅ |
| `defer_date` | 08:00 | Default time for defer dates: 08:00 | ✅ |
| `planned_date` | 09:00 | Default time for planned dates: 09:00 | ✅ |

### The complete algorithm

```
1. Take the COMPLETION DATE (date portion only)
2. Apply the repeat interval (e.g., +1 day for FREQ=DAILY)
3. Set the TIME to the user's configured default for that date type:
   - due_date    → Settings > "Default time for due dates"
   - defer_date  → Settings > "Default time for defer dates"  
   - planned_date → Settings > "Default time for planned dates"
4. This becomes the new anchor date on the next occurrence
5. Any other dates that WERE set shift forward by the same delta
6. Any dates that were NOT set remain unset
```

Behavior is consistent across all three schedule types.

### MCP Server Warning

The current warning text is incorrect:

> ❌ "OmniFocus will fall back to the task's creation date as the anchor."

Recommended replacement:

> ✅ "OmniFocus will create the missing {anchor_field} on the next occurrence using the completion date and the user's default time for {date_type} (configured in Settings → Dates & Times). This produces a valid but potentially surprising schedule. Set the {anchor_field} explicitly for predictable repetition behavior."

---

## Decision Guide for Agents

### ✅ Use `regularly_with_catch_up` when:

- Task is tied to specific calendar days (standup every MWF, rent on the 1st)
- User wants to skip over missed occurrences without tapping through them
- User might complete early and wants today's occurrence to still count (if time hasn't passed)
- **This is the recommended default for most recurring tasks**

### 🔄 Use `regularly` (no catch-up) when:

- User explicitly needs to process every missed occurrence (e.g., logging daily entries)
- Missing an occurrence has real consequences that can't be skipped

### ⚠️ Use `from_completion` when:

- Minimum time gap between occurrences matters more than the specific day
- **Examples**: "water plants every 10 days," "replace filter every 3 months"

> [!warning] Caution with BYDAY patterns
>
> - The completion day **never** counts — even if the due time is hours away
> - Late completion skips the current day entirely (landed on next Wednesday instead of today's Friday)
> - Early completion brings the task back **sooner** than expected
> - `INTERVAL >= 2` resets the week grid, potentially shifting by 14+ days vs catch-up

### Always set the anchor date explicitly

- If `basedOn` points to an unset date field, OmniFocus creates it using completion date + default time
- This works but is rarely intentional — produces user-specific results (depends on their Settings)
- Warn the user; don't silently allow it

---

## Untested Areas

> [!note] Not yet empirically verified — do not treat as ground truth
>
> - **Monthly patterns**: `onDates: [1, 15]` and `on: {last: "friday"}` with `from_completion` — expected same algorithm but monthly edge cases (month boundaries, varying lengths) could surprise
> - **Minutely frequency**: hourly showed no time drift, but minutely rounding may differ
> - **Time drift at very fine granularity with large offsets**: all hourly tests completed within a few hours of due time — completing a 2-hourly task 18 hours late might reveal drift

---

## Methodology

- All experiments used `omnifocus-operator-2:add_tasks` to create tasks and `omnifocus-operator-2:get_task` to query results after completion
- Task IDs persist across repetition completions — same ID returns the new occurrence
- Times verified against user's OmniFocus Settings → Dates & Times (screenshot confirmed: due=19:00, defer=08:00, planned=09:00 BST)
- Experiments conducted April 2-3, 2026, OmniFocus 4.7+, BST (UTC+1)

### Verification scorecard

| Claim | Status | Source | Notes |
|-------|--------|--------|-------|
| Time drift for `from_completion` | ❌ **DISPROVEN** | Deep research report | Time preserved at hourly, daily, and weekly granularity |
| From-completion: today never counts | ✅ **CONFIRMED** | Experiment Q1 | Day-level rounding — skips today even with 9+ hours remaining |
| Catch-up: checks exact time, not just day | ✅ **CONFIRMED** | Experiments Q2 + IV1 | Lands on today if time is future; skips if time has passed |
| Early completion date difference | ✅ **CONFIRMED** | Experiment EC1-3 | From-completion finds next BYDAY after completion; can return sooner |
| Late completion date difference | ✅ **CONFIRMED** | Part 3 BYDAY test | From-completion skips current day; catch-up lands on nearest future grid point |
| `INTERVAL >= 2` grid reset | ✅ **CONFIRMED** | Experiment IV1-2 | 14-day divergence observed; from-completion resets the alternation grid |
| Skipped occs don't count against limits | ✅ **CONFIRMED** | Experiment Q4 | `end.occurrences` decremented by 1, not by number of skipped days |
| Catch-up preserves original time | ✅ **CONFIRMED** | Multiple experiments | But so does from-completion — not a differentiator |
| No time drift at hourly granularity | ✅ **CONFIRMED** | Experiment Q5 | Landed on original 2-hour grid, not completion_time + interval |
| Missing anchor uses creation date | ❌ **DISPROVEN** | Experiment 2 (cross-day) | Uses completion date + user's default time settings |
| Missing anchor creates the date | ✅ **CONFIRMED** | Experiment 1 | OmniFocus creates the anchor date from scratch; doesn't refuse or skip |
| Monthly from-completion behavior | ⬜ **UNTESTED** | — | Expected same algorithm but unverified |
