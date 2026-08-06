---
name: reconstruct-my-day
description: Reconstruct Flo's selected calendar day from Codex task history, direct ChatGPT conversations in his logged-in browser, Fastmail calendar events, and scoped Git/filesystem evidence. Use when Flo invokes $reconstruct-my-day or asks what he did yesterday, today, or on a specific date; wants an ADHD-friendly activity or accomplishment recap; needs a chronology across initiatives; or wants to compare remembered work with evidence. Remain Chronicle-free and read-only, distinguish Flo's attention from autonomous agent output, label confidence, and report in conversation without changing planners or files.
---

# Reconstruct My Day

Rebuild one local calendar day as a concise, evidence-backed account of what
Flo attended to and what his agents completed. Prefer an honest incomplete
picture over a smooth invented timeline.

## Fixed contract

- Remain strictly read-only.
  - Do not send messages, edit conversations, change calendars, update
    Structured, write notes, modify repositories, or create reconstruction
    artifacts.
- Do not invoke or inspect Chronicle.
  - It is not a v1 dependency.
  - Static screen state is weak evidence of interaction.
- Default to yesterday when Flo gives no date.
- Use Flo's current timezone when available; otherwise use `Europe/London`.
- Bound the day as `[00:00, next 00:00)` in that timezone.
  - Never pull next-day activity backward across midnight.
- Treat absence of evidence as a gap, not proof that nothing happened.
- Finish with one calibration question and stop.

## Workflow

1. Resolve the target date and local-day boundary.
2. Create a source-status ledger.
3. Collect Codex, ChatGPT, and Fastmail evidence independently.
4. Derive safe project roots from Codex and collect local evidence.
5. Normalize, deduplicate, classify, and synthesize the evidence.
6. Render the conversational report.
7. Ask whether it matches Flo's memory.

Do not interrupt collection for ordinary source gaps. Continue autonomously
with the remaining sources and disclose the gaps at the end.

## Resolve the target day

- Honor an explicit date first.
- Resolve `today` and `yesterday` from the current local date, not UTC.
- State the resolved date and timezone in the report.
- Mark a reconstruction of today as still in progress.
- Honor a narrower user scope. If Flo asks only about Codex or only wants a
  short answer, do not silently expand it into the full workflow.

## Collect primary evidence

When subagents are available, run three independent collectors in parallel:

1. Codex task history
2. Direct ChatGPT history
3. Fastmail calendar

Give each collector only the target window, its source, the read-only boundary,
and the normalized record shape below. Ask for facts rather than a day
narrative. Keep synthesis in the parent agent so every source receives the
same attention and confidence rules.

If subagents are unavailable, collect the sources sequentially. Use tool
discovery for deferred connector tools rather than listing generic MCP
resources.

Track each source separately as `ok`, `partial`, or `unavailable`. One failed
source must never fail the whole reconstruction.

### Codex task history

- Prefer the connected Codex thread-list and thread-read tools.
- Discover every plausible thread overlapping the local-day window, including
  threads created earlier and resumed on the target day.
- Treat thread metadata such as `updated_at` as candidate discovery only.
- Read candidate threads deeply enough to identify:
  - same-day user turns
  - decisions, reviews, corrections, and interruptions
  - delegated or long-running work
  - concrete outputs and their completion times
  - the task's working directory when available
- Do not equate an open thread or total agent runtime with Flo's attention.
- If connected thread tools are unavailable, use local Codex sessions or
  rollout summaries only as a read-only fallback.
  - Use summaries as an index, not proof of exhaustive coverage.
  - Mark the source partial unless every session overlapping the local window
    was checked.

### Direct ChatGPT history

- Load and follow the installed `chrome:control-chrome` companion skill before
  controlling the browser.
- Use Flo's logged-in ChatGPT history in a new or safely reusable browser tab.
- Use sidebar groups, search, open tabs, or browser history to discover
  candidate conversations.
- Open each candidate and confirm target-day messages from the conversation
  itself whenever possible.
  - Preserve exact message times when exposed.
  - Otherwise use the narrowest supported precision, such as day-level.
- Include phone and voice conversations that appear in synced history.
- Treat browser visit timestamps as pointers only.
  - Never promote a visit into conversation activity without direct
    conversation evidence.
- Do not send a message or rename, archive, share, or delete a conversation.
- If lazy loading or authentication prevents a complete target-day sweep,
  mark ChatGPT partial or unavailable. Do not replace it with web search.

### Fastmail calendar

- Use Fastmail calendar search for the exact local-day window.
- Capture the event title, scheduled start/end, all-day state, and cancellation
  state when available.
- Treat a calendar event as confirmed schedule intent, not confirmed
  attendance.
- Promote attendance only when an independent source corroborates it.
- Do not create, edit, accept, decline, or delete events.

## Collect scoped local evidence

Run local collection only after Codex has supplied candidate working
directories.

- Canonicalize and deduplicate those directories.
- Prefer Git worktree roots.
- Cap the allowlist at 12 roots.
- Never broaden the scan to `/`, `/Users`, `$HOME`, `$HOME/Documents`,
  `$HOME/Work`, system directories, or cache/credential directories.
- If no safe roots exist, skip local collection and record the gap.

Run `~/.agents/skills/reconstruct-my-day/scripts/collect_project_evidence.py`
with Python 3 and:

- `--date YYYY-MM-DD`
- `--timezone AREA/CITY`
- one `--root /trusted/project/root` per candidate

Accept output only when:

- the JSON payload has `schema_version: 1`
- the final line begins with
  `RECONSTRUCT_LOCAL_EVIDENCE_COMPLETE sha256=`

The collector:

- reads commits in the target local-day window
- lists Git tracked/untracked paths and keeps only those whose current mtime
  falls in the target window
- performs a bounded metadata-only walk for non-Git roots
- prunes generated, dependency, cache, and temporary directories
- never opens candidate work files for content; Git may read its index, ignore
  rules, and commit metadata

Interpret local evidence narrowly:

- A commit confirms an outcome existed.
- A current file mtime is tentative corroboration.
- Neither proves Flo's attention or authorship.
- Historical worktree-mtime evidence is inherently incomplete.

## Normalize the evidence

Represent collector findings with this logical shape before synthesis:

```yaml
source: codex | chatgpt | fastmail | git | filesystem
source_status: ok | partial | unavailable
observed_at: ISO-8601 timestamp or null
time_precision: exact | range | day | unknown
initiative: short project or life-area name
activity: concrete factual description
actor: user | mixed | agent | scheduled | unknown
kind: interaction | decision | meeting | outcome | ambient
evidence_strength: direct | corroborated | indirect | unknown
evidence_ref: thread, conversation, event, commit, or path identifier
```

- Preserve uncertainty instead of filling missing times.
- Cluster records that describe the same underlying event.
- Avoid false corroboration:
  - a commit and its file mtime are usually one signal
  - a Codex output and the file it generated are usually one signal
  - repeated generated files are usually one background process

## Classify attention

Apply one class to each synthesized claim:

- **Direct attention**
  - Flo asked, answered, reviewed, decided, composed, corrected, learned, or
    actively practiced.
- **Agent-assisted**
  - Flo steered or reviewed the work while an agent performed most execution.
- **Background outcome**
  - Agents, tests, renders, scans, commits, or generators ran with little or no
    nearby user interaction.
- **Scheduled**
  - The calendar shows intent but attendance is not established.
- **Ambient**
  - A tab, screen, application, or browser visit was merely present.

A three-hour Codex run with two user turns is two interaction moments plus a
background outcome. It is not three hours of direct attention.

Keep simultaneous streams when the evidence supports them. Flo may be using
ChatGPT on his phone while Codex completes work in the background.

## Assign confidence

Assign confidence to each claim, not globally to each source:

- **Confirmed**
  - A direct same-day message, explicit decision, exact calendar record, or
    concrete artifact supports the narrow claim.
- **Strongly inferred**
  - Two genuinely independent sources align.
- **Tentative**
  - One indirect signal, such as an mtime or browser visit, supports it.
- **Unknown**
  - The available evidence cannot establish the claim.

Keep the claim narrow. A commit can confirm that a change landed while leaving
who attended to it unknown. A calendar event can confirm scheduling while
leaving attendance unknown.

## Synthesize without false precision

- Build meaningful chronological blocks, not a raw telemetry dump.
- Use exact times only when supported.
- Do not smooth unknown gaps into continuous work.
- Rank only Direct and Agent-assisted attention areas qualitatively.
  - Keep Scheduled-only and Ambient items out of `Where your attention went`.
- Do not estimate percentages or exact durations unless the evidence genuinely
  supports them.
- Keep autonomous outcomes visible without crediting their runtime as Flo's
  personal effort.
- Emphasize decisions, learning, drafts, fixes, and completed artifacts.
- Use calm, accomplishment-oriented language without claiming productivity
  merely from activity volume.

For overnight work:

- Include target-day user steering that occurred before midnight.
- Include a background outcome only when it occurred inside the target day.
- Do not import a next-day completion into the selected day's timeline.

## Render the report

Use this compact order and omit empty sections:

1. `# 🧭 <weekday, date> · <timezone>`
2. Coverage line for Codex, ChatGPT, Fastmail, and local evidence
3. `## 🕒 Day at a glance`
4. `## 🎯 Where your attention went`
5. `## 🤖 Work completed in the background`
6. `## ✅ Concrete outcomes`
7. `## ⚠️ Gaps and uncertainty`

For the timeline:

- Show only meaningful blocks or interaction moments.
- Label each item `Confirmed`, `Strongly inferred`, or `Tentative`.
- Identify `Direct`, `Agent-assisted`, `Background`, or `Scheduled` when the
  distinction is not obvious.

If any primary source is partial or unavailable, call the reconstruction
incomplete near the top. Never bury a coverage failure.

End with exactly one question:

`Does this match what you remember? The least certain part is <specific block or gap>.`

Do not offer planner edits, start another investigation, or ask multiple
follow-up questions in the same response.
