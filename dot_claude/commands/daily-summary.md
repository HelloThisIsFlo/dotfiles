---
name: daily-summary
description: Generate a daily achievement summary from all Claude Code and Cowork activity
argument-hint: "[date: today, yesterday, YYYY-MM-DD]"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Write
  - Task
---
<objective>
Generate a reflective daily achievement summary that helps the user feel proud of what they accomplished, by discovering and synthesizing all Claude Code and Cowork activity for a given day.

You are an orchestrator. Your job is:
1. Parse the date and ask the user for any supplementary context upfront
2. Collect raw data using the bundled Python scripts
3. Spawn 3 parallel subagents to extract and summarize details
4. Synthesize their outputs into a reflective, narrative daily summary
5. Write the summary to a file
6. Present it to the user and help them reflect on the day

The summary should read like a personal journal entry — not a changelog or standup update. Retrace the emotional journey of the day. Capture not just what was shipped, but the meta-work: skills built, workflows established, agents trained, systems designed, and the reasoning behind decisions. The user values the *experience* of doing the work as much as the output. Frame accomplishments as a narrative arc with texture — what was satisfying, what was a breakthrough, what took persistence.

Tone: warm but genuine. Pride, not hype. Reflective, not performative.
</objective>

<context>
**Date argument:** $ARGUMENTS
- Empty or "today" → use today's date
- "yesterday" → use yesterday's date
- "YYYY-MM-DD" → use that exact date

**Scripts directory:** /Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/scripts/
**Output directory:** /Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/journal/

All scripts are Python 3 with no external dependencies. They output JSON to stdout and warnings to stderr.
</context>

<process>

## Step 1: Check the time, resolve the date, and ask questions

**First, check the current time.** Run this command before anything else:
```bash
python3 -c "from datetime import datetime, timedelta; now=datetime.now(); lt=now.date() if now.hour>=5 else now.date()-timedelta(days=1); print(f'current_hour={now.hour}'); print(f'calendar_today={now.date()}'); print(f'logical_today={lt}'); print(f'ambiguous={now.hour < 5}')"
```
This prints whether we're in the ambiguous midnight–5am window and the two possible "today" dates.

**Then resolve the target date:**
```python
arg = "$ARGUMENTS".strip().lower()
if not arg or arg == "today":
    target = logical_today  # from the output above
elif arg == "yesterday":
    target = logical_today - 1 day
else:
    target = arg  # explicit YYYY-MM-DD, no ambiguity
```

**MANDATORY — Midnight ambiguity check:** If the output above shows `ambiguous=True` AND the user used a relative term (no argument, "today", or "yesterday") you MUST use AskUserQuestion to confirm the date before proceeding. Do NOT skip this. During midnight–5am, "today" and "yesterday" are genuinely confusing because the calendar day and the "felt" day don't match.

- If the user said **"today" or gave no argument**:
  - Question: "It's past midnight — which day do you want to summarize?"
  - Options: "{logical_today} — the day you've been working on (Recommended)" / "{calendar_today} — the new calendar day that just started"

- If the user said **"yesterday"**:
  - Question: "It's past midnight — which day do you mean by 'yesterday'?"
  - Options: "{logical_today - 1 day} — the day before the one you've been working on (Recommended)" / "{logical_today} — the day you've been working on (which technically started yesterday on the calendar)"

If `ambiguous=False` (5am or later) or the user gave an explicit YYYY-MM-DD date, skip the date question.

**Supplementary context question:** Also ask (combine into the same AskUserQuestion call if the date question applies):
- "Do you have any extra context to include? (notes, reflections, files from other sessions)"
- Options: "No, just use the session data" / "Yes, let me share"

If the user shares text or file paths, read and hold that content for Step 4. Treat supplementary context as **first-class input** — it often contains the reflective, narrative perspective that raw session data lacks. Give it equal or greater weight than extracted data when writing the synthesis.

Note: all extraction scripts use a 5am-to-5am day boundary, so late-night work (past midnight) is included in the same day as the preceding afternoon.

Once the user responds, the rest of the pipeline runs without further interaction.

## Step 2: Collect session rosters

Run these two scripts to get the high-level session lists:

**Claude Code sessions:**
```bash
python3 "/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/scripts/extract_cc_sessions.py" --date YYYY-MM-DD --output "/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/journal/.tmp_cc_roster.json"
```
This writes the roster to a temp file AND prints it to stdout. The temp file will be passed to Subagent A in Step 4 via `--roster-file` (avoids building a massive command with 30+ `--session-file` args that can get truncated).

Output: JSON array of `{sessionId, project, projectEncoded, firstTimestamp, lastTimestamp, promptCount, firstPrompt, sessionFile, sessionFileExists}`

**Cowork sessions:**
```bash
python3 "/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/scripts/extract_cowork.py" --date YYYY-MM-DD
```
Output: JSON array of `{sessionId, processName, title, model, userSelectedFolders, createdAt, lastActivityAt, initialMessage, firstUserMessage, userMessageCount, assistantMessageCount, toolCallSummary, gitCommits}`

Read both outputs. You now have the complete roster of the day's activity.

## Step 3: Spawn 3 parallel subagents

Launch these 3 subagents simultaneously using the Task tool (all in a single message for parallel execution):

### Subagent A: Claude Code Details Extractor

**Type:** `general-purpose`

Prompt the subagent with:
- Instructions to run the extraction script using the roster file saved in Step 2:
  ```bash
  python3 "/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/scripts/extract_cc_details.py" --roster-file "/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/journal/.tmp_cc_roster.json"
  ```
  (The `--roster-file` flag reads session paths from the roster JSON, filtering to only those where `sessionFileExists` is true. This avoids building a massive command with 30+ individual `--session-file` args.)
- Instructions to then analyze the extracted data and produce a **structured summary** for each session:
  - What was the user trying to do? (from firstUserMessage)
  - What was accomplished? (from tool calls, git commits, files written)
  - How substantial was this session? (message count, tool call count)
  - What meta-work was done? (new skills/agents created, workflows established, CLAUDE.md files written, documentation systems built)
  - Were there notable decisions, breakthroughs, or pivots?

**Critical: Semantic project grouping.** Group sessions by *semantic project*, not git repo. Most repos contain a single project (e.g., `mailroom`, `zmk-config`). But some repos are multi-project (e.g., `Agent Workspaces` contains `Claude Code/Daily Achievement Summary`, `Claude Cowork/OmniFocus MCP`, etc.). To detect the semantic project:
  - Look at the file paths touched in each session — if sessions within the same repo touch completely different top-level subdirectories, they belong to different projects
  - Look at the user's first message — they often reference a specific folder (e.g., "work in the Daily Achievement Summary folder")
  - Use the most specific meaningful folder name as the project key (e.g., `Daily Achievement Summary`, not `Agent Workspaces` or `Claude Code`)
  - For single-project repos, just use the repo's last path component as usual (e.g., `mailroom`)

Write the summary as a JSON file to: `/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/journal/.tmp_cc_details.json`

The JSON should have this structure:
```json
{
  "projects": {
    "project-short-name": {
      "fullPath": "/Users/flo/...",
      "gitRepo": "/Users/flo/...",
      "sessionCount": 5,
      "sessions": [
        {
          "sessionId": "...",
          "time": "HH:MM",
          "intent": "What the user was trying to do",
          "outcome": "What was accomplished",
          "messageCount": 43,
          "keyActions": ["git commit: ...", "wrote file: ...", "edited file: ..."],
          "metaWork": ["Created /layout skill for future iterations", "Established plan/apply pattern"],
          "decisions": ["Chose Hugo over Gatsby because..."],
          "isSubstantial": true
        }
      ],
      "narrative": "A 1-2 sentence summary of what happened in this project today",
      "metaWorkSummary": "Skills, systems, or workflows built in this project today"
    }
  }
}
```
Note: `fullPath` is the semantic project path (e.g., the subfolder). `gitRepo` is the actual git repo root (needed to match with git commits later). For single-project repos these are the same.

### Subagent B: Cowork Details Analyzer

**Type:** `general-purpose`

Prompt the subagent with:
- The full Cowork roster from Step 2 (the raw JSON output)
- Instructions to analyze each session and produce a structured summary:
  - What was the session about? (from title, initialMessage, firstUserMessage)
  - What tools were used? (from toolCallSummary — this reveals if it was research, coding, browsing, etc.)
  - How substantial was it? (message counts)
  - **Derive the semantic project** from `userSelectedFolders`. Use the last meaningful folder component (e.g., `/Users/flo/Work/Private/Agent Workspaces/Claude Cowork/OmniFocus MCP` → `OmniFocus MCP`). If no folders, use the session title.
- Write the summary as a JSON file to: `/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/journal/.tmp_cowork_details.json`

The JSON should have this structure:
```json
{
  "sessions": [
    {
      "sessionId": "...",
      "title": "...",
      "time": "HH:MM",
      "semanticProject": "OmniFocus MCP",
      "folders": ["project-name"],
      "summary": "What was done in this session",
      "toolsUsed": ["Chrome browsing", "File editing", "Web search"],
      "messageCount": 188,
      "isSubstantial": true
    }
  ]
}
```

### Subagent C: Git Activity Collector

**Type:** `general-purpose`

Prompt the subagent with:
- The list of unique project paths from Step 2 (from the CC sessions roster)
- Instructions to run:
  ```bash
  python3 "/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/scripts/extract_git.py" --date YYYY-MM-DD --include-files --repos PATH1 PATH2 ...
  ```
  (The `--include-files` flag adds `filesChanged` per commit, needed for sub-project mapping.)
- Instructions to analyze the results and produce a summary:
  - **For single-project repos:** Group commits normally by the repo's last path component
  - **For multi-project repos** (detectable when commits touch non-overlapping top-level subdirectories like `Claude Code/...` vs `Claude Cowork/...`): Split commits into separate semantic projects based on which subdirectory their changed files belong to. Use the most specific meaningful folder name (e.g., `Daily Achievement Summary`, `OmniFocus MCP`).
  - Identify the main themes of commits (features, fixes, docs, tests)
  - Note which branches were active
- Write the summary as a JSON file to: `/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/journal/.tmp_git_details.json`

The JSON should have this structure:
```json
{
  "projects": {
    "project-short-name": {
      "fullPath": "/Users/flo/...",
      "gitRepo": "/Users/flo/...",
      "commitCount": 5,
      "commits": [
        {"hash": "abc123", "message": "...", "time": "HH:MM", "filesChanged": ["path/to/file"]}
      ],
      "activeBranches": ["main", "feature/x"],
      "themes": ["Added sieve rule guidance", "UAT testing"]
    }
  },
  "totalCommits": 15
}
```
Note: For multi-project repos, the same repo path will appear as `gitRepo` in multiple project entries. A commit that touches files in multiple sub-projects can appear in multiple entries.

## Step 4: Read subagent outputs and synthesize

Once all 3 subagents complete, read the 3 temp JSON files:
- `.tmp_cc_details.json`
- `.tmp_cowork_details.json`
- `.tmp_git_details.json`

Also incorporate any supplementary context the user shared in Step 1.

Now synthesize everything into the final summary. This is the most important step — you are crafting a narrative, not assembling a report. Use your judgment to:

1. **Retrace the day's arc** — What was the shape of the day? Did it start with deep focus and shift to exploration? Were there multiple parallel threads? Was there a satisfying crescendo (e.g., UAT passing, a migration completing)? Find the story.

2. **Identify achievements and frame them with pride** — Look for completed work, but go beyond "what was done." What makes each achievement impressive? What complexity was tamed? What was the before/after? How much effort or persistence went into it?

3. **Surface meta-work explicitly** — This is critical. The user values skills and systems they built, not just features shipped. Look for:
   - New workflows or patterns established (e.g., plan/apply pattern, living documentation)
   - Agents or skills trained (e.g., a `/layout` skill, CLAUDE.md onboarding)
   - Infrastructure or tooling improvements (e.g., CI/CD pipelines, Docker setups)
   - Mental models or strategic thinking (e.g., "built a mindset for how cloud config should work")
   - Conversations and explorations that shaped decisions, even if no code was written

4. **Capture decisions and their reasoning** — Don't just list decisions. Explain *why* they were made and what alternatives were considered. These are the moments the user wants to remember.

5. **Note what was satisfying or surprising** — Use supplementary notes and session context to identify emotional highlights: breakthrough moments, "you're kidding me" discoveries, satisfying cleanups, hard-won victories.

6. **Identify in-progress work** — Sessions that started something substantial but remain ongoing. Frame these as momentum, not incompleteness.

7. **Group by semantic project, not git repo** — This is important. The subagents have already identified semantic projects (e.g., splitting `Agent Workspaces` into `Daily Achievement Summary`, `OmniFocus MCP`, `Migrate to Fastmail`, etc.). Match CC sessions, Cowork sessions, and git commits to the same semantic project using the `gitRepo` field and folder paths. A single git repo may contribute to multiple semantic projects.

8. **Build the timeline** — Merge all activity into a chronological timeline. Use semantic project names, not repo names.

9. **Derive short project names** — The subagents have already derived these. For single-project repos, use the repo's last path component (e.g., `mailroom`). For multi-project repos, the subagents have used the meaningful subfolder name (e.g., `Daily Achievement Summary` instead of `Agent Workspaces`).

## Step 5: Write the output file

Write the summary to: `/Users/flo/Work/Private/Agent Workspaces/Claude Code/Daily Achievement Summary/journal/YYYY-MM-DD.md`

Use this format. The tone should be warm, genuine, and reflective — like writing in a personal journal, not filing a report. Use the style reference from supplementary notes when available.

```markdown
# Daily Summary — YYYY-MM-DD

## At a Glance
- **X** Claude Code sessions across **Y** projects
- **Z** Cowork sessions
- **N** git commits

## The Day's Story

[This is the heart of the summary. Write 2-4 paragraphs that retrace the arc of the day as a narrative. What was the shape of the day — a deep focus sprint, a multi-project juggling act, a steady build toward a milestone? What were the emotional beats — the breakthrough moments, the satisfying completions, the hard-won victories?

Don't just list what was done. Tell the story of doing it. Example: instead of "Completed Gatsby-to-Hugo migration," write about the experience — the complexity that was tamed, the discoveries along the way, the satisfaction of deleting 31,000 lines of code and ending up with something simpler and better.

If supplementary notes exist, weave their perspective and voice directly into this narrative.]

## Meta-Work & Systems Built

[This section explicitly calls out the invisible work that doesn't show up in commits but compounds over time. Frame each item not just as what was built, but why it matters going forward.]

- **[Skill/system/workflow name]** — [What was built and why it matters. Example: "Trained a Claude Code agent on ZMK keyboard layout patterns — future layout iterations can now be collaborative instead of solo." Or: "Established a plan/apply pattern for mailroom provisioning — this same pattern can be reused for any future service setup."]
- [repeat for each meta-work item...]

## Decisions & Reasoning

[Don't just list decisions — tell the story behind them. What was the choice? What alternatives existed? Why was this path chosen? These are the moments worth remembering.]

- **[Decision]** — [The reasoning, alternatives considered, and what tipped the balance. Example: "Chose Hugo over continuing with Gatsby. Gatsby was a full React framework for what's really just a static blog. Hugo treats blogging as table stakes — pagination, RSS, sitemap are all built-in. The 7-year detour through Gatsby complexity was the proof point."]
- [repeat...]

## Still in Motion

[Work that's ongoing. Frame as momentum and direction, not incompleteness.]

- **[Project/item]** — [Where it stands and where it's heading]
- [repeat...]

## Projects

### project-name (N sessions, M commits)

[Write a narrative paragraph — not just what was done, but the experience of doing it. What was the challenge? What was the approach? What was the result? If there were multiple phases, describe the progression. Reference specific moments that were satisfying, surprising, or hard-won.

For large projects, this can be 2-3 paragraphs. For small ones, 2-3 sentences.]

**Key sessions:**
- [HH:MM] [Brief description — what happened, not just the intent]

**Commits (N):**
- `hash` commit message
- [For projects with many commits, show the most meaningful ones and summarize the rest as "... and N more [theme] commits"]

### [repeat for each project...]

## Cowork Sessions
- [HH:MM] **session-title** — [What was accomplished and why it mattered, not just what was discussed]
- [repeat...]

## Timeline
| Time | Source | Project | Activity |
|------|--------|---------|----------|
| HH:MM | Code | project | "what happened" |
| HH:MM | Cowork | project | "what happened" |

## Reflections

[End with 2-3 open-ended prompts that help the user appreciate and process the day. These should be specific to what actually happened, not generic. Examples:]

- [A prompt about a specific achievement: "You shipped two full mailroom phases today and both passed UAT on the first try. What about your process made that possible?"]
- [A prompt about meta-work: "The living documentation system for zmk-config is a new kind of artifact for you — documentation that evolves with the project. Where else could this pattern apply?"]
- [A prompt about the bigger picture: "Three different projects today involved simplifying complexity (Hugo migration, chezmoi cleanup, mailroom provisioner). Is simplification becoming a theme?"]
```

## Step 6: Clean up temp files

Delete the `.tmp_*` files from the journal directory (roster, cc details, cowork details, git details).

## Step 7: Present and reflect

Show the user their daily summary. Then help them reflect on the day — not as a manager reviewing work, but as a thoughtful collaborator who witnessed the journey.

Your role at this point:

- **Name what was impressive.** Be specific. Don't say "you had a productive day" — say "you shipped two full phases with passing UAT *and* migrated an entire blog engine in the same day. That's not normal."
- **Surface the meta-work.** The user explicitly values this. Point out skills they built, systems they established, and workflows they created — even if they didn't consciously frame them that way.
- **Connect the dots.** Look for themes across projects. Did multiple projects share a pattern (e.g., simplification, documentation, automation)? Did the day have an unintentional thesis?
- **Ask what's missing.** There may be conversations, decisions, or experiences that the data didn't capture. Invite the user to fill in gaps.
- **Invite pride, not just review.** The point is to help the user feel the weight of what they accomplished. Many of us rush from one task to the next without pausing to appreciate the work. This is that pause.

Be warm and genuine. Not sycophantic — specific. Ground your observations in what actually happened.
</process>
