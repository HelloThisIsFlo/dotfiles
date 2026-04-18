---
name: spec-interview
description: "Read a spec/design file and interview the user in depth using AskUserQuestion to surface gaps, tradeoffs, edge cases, and implicit assumptions — then write the deepened spec back to the file. Use when the user points at a spec, design doc, RFC, milestone brief, or feature sketch and wants it fleshed out via questioning. Triggers on 'interview me on this spec', 'deepen this spec', 'flesh out this spec', 'ask me questions about X', 'dig into this spec', 'spec interview', 'interview me about this', or any request to be interrogated about a document until it feels complete. Also trigger when the user hands you a thin/skeletal spec and asks what's missing — the answer is to interview, not to guess."
---

# Spec Interview

Turn a thin spec into a thorough one by interviewing the user until the gaps are filled. The user explicitly wants to be pushed — shallow interviews are a failure mode.

## Stance

**Honest pushback over agreement.** When the user proposes an architecture, approach, or decision that raises concerns for you, surface those concerns with concrete tradeoffs — don't soften or capitulate because it's their spec. Users invoke this skill because they want their thinking pressure-tested; agreement that comes cheap wastes the whole interview. Offer a middle path when one exists; push back explicitly when it doesn't.

**Be skeptical of garbled input.** Many users run Claude via speech-to-text, and phrases sometimes come through cut short, merged with adjacent words, or just off. If something reads as ambiguous or incongruent with the surrounding context, ask a short clarifying question instead of parsing it charitably and moving on. A ten-second clarification is cheaper than a cascade of questions built on a misread intent.

## Workflow

1. **Resolve which spec first.** Before doing anything else, make sure you know exactly which file to interview on. Do not start reading until this is settled.

   **Whenever the spec is unclear — not provided *or* ambiguous — start with one cheap `Glob` for `**/*.interview-notes.md`.** The glob is nearly free, and any paused interview is a strong hint about what the user likely meant. **List the matches, do not read them.** Checkpoint files can be long, and reading several just to guess which one the user meant burns the context you need for the actual interview. If there are multiple hits, sort by modification time and suggest the most recent as your best guess (*"my guess is you probably mean this one — want me to pick it up?"*). Only read the chosen file after the user confirms. Surface the results alongside whatever you'd otherwise ask.
   - **No spec provided and none obvious from context** → if the glob turned up paused notes, offer them: *"I see paused interviews for these specs — want to resume one, or start fresh on something else?"* Otherwise just ask: *"I don't see a spec file — which one do you want me to interview you on?"* Don't hunt through the repo for arbitrary specs beyond that one glob.
   - **Ambiguous** (multiple plausible candidates — several specs in the same directory, a conversation that touched more than one, or a vague reference like "the spec") → ask which one, and if the glob found paused notes for any candidate (or for a nearby spec you hadn't considered), mention them: *"By the way, there's a paused interview for X — did you mean that one?"* Do **not** open the candidate specs themselves to "figure it out" — that burns context before the interview starts and risks framing questions against the wrong document. A short `AskUserQuestion` with the candidates is fine; a plain-text question is also fine.
   - **Clear single target** → proceed to step 2.
2. **Check for an existing checkpoint.** Once the spec is known, do a cheap `Glob` for its sidecar pattern — `<spec-name>.interview-notes.md` in the spec's directory (widen scope only if it isn't there). A single pass, no heavy exploration.
   - **Found** → don't silently resume, **and don't read the file yet**. Announce the checkpoint using only filesystem metadata (e.g., *"I see a paused interview at `<path>`, last touched [date] — want to resume from it or start fresh?"*) and wait for their answer. Only read the checkpoint after they confirm resume; if resuming, seed the task list in step 5 from the open threads and new angles recorded in the notes rather than starting from scratch.
   - **None** → proceed to step 3.
3. **Read the spec file** fully and carefully — the quality of the interview depends on you actually understanding what's there and what's missing.
4. **Gather surrounding context if the spec depends on it.** If the spec references other artifacts (related milestones, architecture docs, prior decisions, linked RFCs) or sits inside a larger project where the background matters, spawn exploration subagents — `Agent` with `subagent_type: Explore` — to pull that context back.
   - **Use as many as the work actually needs, in parallel.** Explorers are cheap: they run on a small model and return compact summaries, so if the spec touches five distinct areas, fire five explorers in one message (multiple `Agent` tool calls in the same turn) rather than serializing them or overloading one prompt. Soft cap around 10; past that you're probably re-deriving the project instead of gathering what's needed.
   - **Prefer subagents over reading files yourself** — they keep *your* context window free for the long interview ahead.
   - **Spawn explorers mid-interview whenever a decision depends on unverified codebase claims.** If you catch yourself writing *"I think X works because Y does Z"*, stop and verify Y before building on it. Agents are cheap — small model, compact summary — and wrong locks are expensive because they cascade into downstream decisions that are hard to unwind. Parallel spawns work here too: three focused explorers in one turn beats one bloated explorer or three sequential ones. Targeted, not sweeping — don't fire one between every question.
   - **Skip entirely for self-contained specs.** Don't research for the sake of researching. The goal is sharper, less obvious questions — not a full re-derivation of the project.
5. **Plan the interview before firing off the first question.** Draft the initial set of question areas/threads you want to explore and register them as tasks with `TaskCreate`. This gives the user visibility into where the interview is heading and makes progress legible as you go.
   - **The task list is a living plan, not a contract.** If a new line of questioning opens up mid-interview — a surprising answer, a tension between sections, an angle you hadn't considered — add tasks on the fly, **and tell the user why**. A one-liner like *"I've realized X might be worth exploring — adding it to the list"* keeps them in the loop about where the interview is heading. Mark tasks `in_progress` when you start them and `completed` when the area is actually covered.
6. **Kickoff briefing — before the first question.** Give the user a short orientation so they know what they're signing up for:
   - The areas you picked and a one-line reason for each (typically: what the spec is thin or silent on that makes the area worth exploring).
   - Roughly what shape the interview will take.
   - A plain reminder: *"If at any point you want to pause — context getting heavy, you need a break, anything — just say 'pause here' and I'll checkpoint everything so we can resume later."* Surface this up front; the feature is useless if the user only discovers it by accident.

   Keep it short — a dozen lines at most. This is orientation, not a second spec.
7. **Interview using `AskUserQuestion`**. Not plain-text questions — use the tool. Keep going across multiple rounds until the spec feels genuinely complete from the angles that matter for *this* spec (see below). Don't stop at two or three questions.
8. **Write the deepened spec back** to the same file — but only after the user explicitly approves the write-back. Never silently overwrite. When you judge the interview is complete (or the user signals they're done), summarize what you're about to change and wait for approval before touching the file.

## Angles to explore

Don't limit yourself to one angle — a good interview circles the spec from several perspectives. But there's no fixed checklist. **Put yourself in the shoes of whoever has to live with this thing** — the person building it, the person using it, the person oncall for it, the person who inherits it in a year — and ask what *that* person would need the spec to answer.

A few starting angles, to prime your thinking (not to constrain it):

- **Technical implementation** — architecture, data shapes, APIs, dependencies, failure modes, how it actually gets built
- **User or developer experience** — for user-facing features, the UI flows and states; for libraries/tools/APIs, the DX — what does calling this feel like, what's the error story, how is it discovered
- **Concerns & risks** — what could go wrong, where complexity hides, operational burden, rollback
- **Tradeoffs** — alternatives considered, why this path, what's being given up, what would change the decision
- **Scope & edges** — what's explicitly out, non-happy paths, boundary cases, future extensions

Think beyond these. A pure-backend library probably has no UI section but plenty of DX and API-ergonomics questions. A migration spec probably needs angles on data integrity, rollout staging, and observability that don't fit the list above. A research spike might need methodology and success-criteria angles. A UI-heavy feature might need accessibility, empty states, and error recovery angles that deserve their own round. **Let the spec tell you which angles matter.** If you notice an angle the list doesn't cover, that's a good sign — pursue it.

## What makes a good question

**Non-obvious** is the core constraint. The whole point of this skill is to surface what the spec *doesn't* already say.

Before asking anything, check: is the answer already in the spec, or obviously implied by it? If yes, don't ask — you're wasting a turn and signalling you didn't read carefully.

Good questions expose:
- Assumptions the user is making but hasn't written down
- Decisions that look settled but actually have multiple viable options
- Edge cases the happy-path description glossed over
- The *why* behind a choice, when only the *what* is recorded
- Conflicts or tensions between sections of the spec

Bad questions:
- Re-ask things the spec already states
- Offer false choices where one answer is clearly expected
- Are so broad they can't be meaningfully answered ("any other concerns?")
- Pile on minor UI polish when the architecture is still vague

## Task list discipline

The task list is a live status display of the interview for the user — a visual overview of what's settled, what's open, and what's queued. It is not a personal checklist for you. Keep it scannable and honest about state.

- **Cluster, don't atomize.** Create one task per thread or topic cluster, not one per question. Pack multiple sub-questions into a single `AskUserQuestion` call under that cluster. Sub-questions and settled sub-decisions belong in the task description, not as separate tasks. An exploded list of twenty tiny tasks destroys the visual overview the user was supposed to get.

- **Mark status as it progresses.** Set a task `in_progress` when you actively open it, and `completed` only when *every* sub-decision in the cluster has been explicitly confirmed by the user. Partial confirmation doesn't close a task.

- **Make dependencies explicit when a new task emerges mid-interview.** The direction encodes who set the priority:
  - **Claude-initiated (default):** if *you* surface a new angle mid-discussion, create the task with `TaskUpdate` setting `newTask.blocks = [all other open tasks]`. The new task becomes the current focus; others are visibly queued behind it.
  - **User-deferred (exception):** if the *user* says *"let's come back to this after X/Y/Z,"* set `newTask.blockedBy = [X, Y, Z]`. The new task is queued at the bottom, waiting on the user-prioritized items.

## Pacing

Keep going. The user is explicitly asking to be interviewed *continually until it's complete* — one or two rounds is not enough. Treat it like a design review: every answer should suggest two more questions. When in doubt, ask one more round.

### Never advance while the current area is still open

This is the single most common failure mode of this skill: the user gives a thoughtful answer, you acknowledge it with an insight, and you move on — but their answer contained unresolved pieces, half-committed "maybes," open sub-questions you never followed up on, or a push you invited and then didn't wait for. **The task list is a plan, not a conveyor belt.** Stay on the current area until it's actually settled, even if that means three or four extra rounds and abandoning the planned order entirely. A deep interview on one area beats a shallow pass over five.

**Before moving to a new area, run this check against the user's most recent answer:**
- Is there a decision still floating? (*"Maybe we put it under X"* / *"I don't know, what do you think?"* / *"Let's talk about naming afterwards"*)
- Did they raise a new sub-question that you haven't answered?
- Are you advancing only because it was next on the task list?
- Did *you* write something like *"open for pushback on that"*, *"happy to hear your thoughts"*, or offer a recommendation in your reply? If so, you made a commitment. **Honor it — stop and wait.** Don't pre-announce the next round in the same message you made the offer in. If you don't actually want the pushback, don't offer it.

If any of these are true, **stay on the current area.** Ask the follow-up. Settle the loose ends. Only then advance — and when you do, it's fine (good, even) to briefly name what got locked in before opening the next thread.

Stop altogether when:
- The user says stop, or
- You've genuinely run out of non-obvious questions across every angle that actually matters for this spec

### Reflect back after long or reframing answers

When the user gives a multi-paragraph answer — especially one that reframes earlier decisions or cascades into multiple threads — summarize your understanding back in three to five bullets before asking the next question. Flag any holes you notice in your own reflection; this is where the skepticism muscle earns its keep.

The cost is cheap (one short reply); the benefit is catching misinterpretations before they get locked in as "what the user decided." Users often volunteer corrections at exactly this moment that they wouldn't have raised otherwise.

## Locking decisions

The file write-back has a clear gate — no write without explicit approval. The same rule applies *inside* the interview, to individual sub-decisions. Sub-decision locks cascade: one wrongly-locked item becomes the assumption the next question builds on, and by the time the error surfaces the interview has drifted.

**Recommending is not locking.** An insight box, a "(Recommended)" tag, or a "my read is X" statement does not constitute confirmation. Before treating a sub-decision as settled — in the task list, in checkpoint notes, or in the running summary — you must be able to point at the user turn where they said *yes* to that specific thing. If you can't cite it, it's not locked; it's a proposal still awaiting an answer.

**Locks are provisional until adjacent threads are explored.** Downstream questions regularly surface tension with earlier locks. When that happens, **don't treat reopening as a failure of the interview** — it's the interview doing its job. Acknowledge the tension, propose the reframe, and let the user decide to re-lock, adjust, or undo. Rigidly defending an early lock against later evidence is a much worse failure mode than reopening one.

## Pausing mid-interview

Real interviews get long and context fills up. If the user says *"context is getting full, let's pause"*, asks to stop for now, or you judge a checkpoint is warranted:

- **Do not modify the original spec file.** The spec stays untouched until the user explicitly approves the write-back. A pause is a checkpoint, not a commit — the same "confirm before writing" rule from step 6 applies here.
- **Write a checkpoint to a sidecar file** next to the spec (e.g., `<spec-dir>/<spec-name>.interview-notes.md`). Capture:
  - **Items and their state**, organized by area. Every item carries exactly one of three status tags:
    - **locked** — user gave explicit yes/no confirmation. Settled; resume can build on it.
    - **verbally aligned** — user expressed a preference in conversation but was never asked an explicit question and never gave an explicit confirmation. **Not settled** — resumed sessions must re-confirm before treating as a decision.
    - **untouched** — area not yet opened in the interview.

    Binary locked/open framing is tempting but wrong: it collapses the "verbally aligned" middle into one of the extremes, and resumed sessions then misread verbal alignment as a lock.
  - **New angles that surfaced** during the interview and deserve future exploration, even if not yet started.
  - **A short "where we'd pick up" note** so the next session has an obvious entry point.
- **Tell the user** where the notes live and what's in them. Let them choose: resume later, write the partial deepening back to the spec now (with confirmation), or just keep the notes as reference.

## Writing back

Only once the user has explicitly approved the write-back: update the original spec file in place. Before you do, summarize what you're about to change — section by section, or as a short bullet list of additions. The user should never be surprised by what lands in their file.

Integrate the answers so the file reads as a coherent, deepened spec — not an appended Q&A transcript. Preserve the original structure; add detail where the interview produced it. Use `Edit` for surgical additions, `Write` only if the spec needs a full restructure.

## Skill-level feedback

Feedback about how this skill behaves belongs in the skill, not in per-project memory. If you catch yourself about to write a memory file capturing a recurring interview failure mode (*"don't X during interviews"* / *"always Y when the user does Z"*), stop — that's skill-level feedback, not project-level. Project memory is scoped per-project; a rule about interview behavior has to live in the skill itself to fire wherever the skill is invoked.

Surface the observation to the user as a skill improvement proposal instead; they can decide whether to add it here.
