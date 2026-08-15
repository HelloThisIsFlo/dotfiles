---
name: coordinate-interview
description: "Coordinate recruiter and interview logistics from an existing actionable task. Use when Flo explicitly invokes $coordinate-interview to compare every offered slot, check calendar and preparation capacity, protect availability, configure a bounded Fantastical link, draft a natural recruiter reply, reschedule, or reconcile confirmed logistics. Implicit matches only remind Flo that the skill exists."
---

# Coordinate Interview

Turn an existing interview-coordination task into one verified logistical package. Stop when the action is ready for Flo to send or book. Never decide whether he wants the job and never begin interview preparation.

## Invocation boundary

First determine whether Flo explicitly named `$coordinate-interview`.

- **Explicit invocation:** run this workflow.
- **Implicit match outside a Daily Review:** only remind Flo that `$coordinate-interview` can handle it. Do not inspect apps or mutate anything.
- **Implicit match during an active Daily Review:** capture or refine `Run $coordinate-interview for …` under the live Daily Review rules, preserving source links and the intended outcome, then return immediately to the review.
- **Explicit side quest during a Daily Review:** run only when Flo clearly declares the detour.

Never chain automatically into `$plan-interview-prep`. Mention it only when preparation planning is a distinct next action.

## Preconditions and scope

An actionable coordination task must already exist. It may point to a Fastmail thread, pasted LinkedIn exchange, role page, brief, booking page, calendar event, or existing draft.

If no actionable task exists:

- Suggest the exact capture: `Run $coordinate-interview for {person/company}: {intended logistical outcome}`.
- During a Daily Review, create or refine that capture through the normal pipeline and return to the review.
- Do not start coordination from an untriaged recruiter message.

This skill does not decide:

- Whether Flo wants the job.
- Whether an exploratory call is worthwhile.
- How Flo should prepare.

## 1. Reconstruct the complete choice

Work read-only first. Read the complete source, not a snippet:

- Existing OmniFocus task, note, hierarchy, dates, and Review-family tag.
- Full Fastmail thread or pasted LinkedIn conversation.
- Role description, supplied brief, and material links.
- Booking page or every time stated in prose.
- Existing drafts, invitations, private holds, and confirmed events.
- All relevant calendars over the offered horizon.

Produce a compact fact card:

- Person, company, role, stage, and channel.
- Confirmed facts.
- Working assumptions.
- Material ambiguity that could change the action.
- Source timezone and Flo's local timezone.
- Separate events when the source distinguishes a prep call, recruiter screen, panel, or exercise review; never transfer one event's availability or deadline to another.

Enumerate **every offered slot before recommending one**. Normalize each to Flo's timezone using the offset in force on the event date, including DST transitions, and show a matrix with:

- Offered slot.
- Hard conflicts.
- Soft conflicts or costly context switching.
- Visible preparation window and realistic preparation capacity beforehand.
- Existing hold, invitation, or draft that makes a duplicate possible.

Do not optimize for the earliest slot. Do not recommend until the full matrix is visible.

## 2. Choose the protection mechanism

### Booking link

- Create no candidate holds by default.
- Duplicate the proven recruiter template; never edit Flo's general booking link.
- Keep the duplicate recruiter-specific, bounded, and unlisted.
- Specify duration, minimum notice, date range, offered windows, pre-meeting buffer, and any relevant post-meeting buffer.
- Offer one strategic private hold only when Flo wants to protect a particularly important opportunity.

### Specific availability

- Protect **every offered slot**, not only the recommendation.
- Include the preparation buffer in every protected window.
- Use private calendar events with no participants.
- Title each event `HOLD: {Company} interview`.

### Confirmed conversation

- Preserve participant-bearing invitations unchanged.
- Never duplicate an existing invitation with a hold.
- Release unused holds only with explicit approval.
- Protect preparation immediately beforehand:
  - Recruiter call: 30 minutes.
  - Panel, technical, or deeper interview: 60 minutes.
  - Adjust only when the known format clearly warrants it.

## 3. Present one approval package

Before any mutation, present one package containing:

- Complete availability matrix.
- Recommended option and a genuine fallback.
- Exact private holds to create or release.
- Exact bounded-link configuration.
- One reply draft in Flo's voice.
- At most one material question, only if its answer can change the action.
- Exact OmniFocus note replacement or append, and exact date changes.

Ask for the preference and all mutations together:

> Approve this coordination package? Preferred: X; fallback: Y; create/release these private holds; create/update this bounded link; save this draft; update TASK as shown. Nothing will be sent or booked.

A message from Flo that already approves every exact output counts as the gate. Otherwise, make no writes before this bundled approval. Host-native confirmations may still appear when unavoidable, but do not ask a second judgment question.

## 4. Apply dependency-safely and verify

Apply only the approved package, then re-read every changed artifact.

### Calendar

- Create private holds with no participants.
- Never edit participant-bearing events.
- Verify title, calendar, privacy, start/end, and absence of participants.

### Fantastical bounded link

- Check for a Fantastical connector first.
- If none exists, use the installed browser-control skill with the target Fantastical URL so an authenticated session can be reused.
- Treat authentication failure as a blocker; do not switch accounts or sources.
- Duplicate/update only the recruiter-specific link and save it.
- Open the public booking page and verify its actual visible availability.
- Never place an unverified URL in the draft.
- If creation, saving, or public verification fails, omit the URL and report the residual. Do not silently substitute manual times.

### Reply draft

- Search for an existing draft before creating one.
- Save one Fastmail reply draft when supported. Never send it.
- If safe draft updating is unavailable, preserve the existing draft and return the revised copy.
- For LinkedIn, return plain copy with the raw booking URL. Never post it.

Voice rules:

- Acknowledge delay once when relevant.
- Mention one specific role or exercise detail.
- Express measured, genuine interest.
- Give a preferred time plus a real fallback, or the bounded link.
- Ask at most one material question.
- Avoid generic enthusiasm, corporate filler, and formal LLM phrasing.

### OmniFocus

- Update the existing task under its owning project and live Daily Review rules.
- Keep the note clean, current, and navigable.
- Include destructive note replacement in the approved package whenever stale content must be removed.
- Preserve Review-family tags and flag every mutation.
- Change only dates approved in the package.
- Never complete the task before Flo actually sends or books.
- Record the next external state as `awaiting Flo to send/book` or `waiting on recruiter`.

Failures are independent where safe. If a hold fails, continue only unrelated approved actions. If a link fails, skip every dependent draft mutation. Never improvise another slot. Report exactly what applied, what was skipped, and why.

## Stop condition

Stop when:

- Flo has seen the complete choice.
- Approved mutations are verified.
- The reply is ready for Flo.
- The existing task names the next external state.
- No logistical ambiguity can change the immediate action.

State that coordination is complete, then stop before interview preparation.
