---
name: coordinate-interview
description: "Coordinate recruiter and interview logistics when Flo asks to arrange or reschedule a conversation, review availability, prepare a booking link, or draft a logistical reply. Start from an email, task, pasted exchange, or current request; no existing task or literal skill invocation is required."
---

# Coordinate Interview

Prepare verified interview logistics and a reply that Flo can review and send.

**Recover context → prepare availability/link → Flo reviews → refine email in chat → save approved draft → hand back for sending.**

## 🎯 Invocation and scope

- A clear natural-language request such as “help me arrange this call” is sufficient. Flo need not name `$coordinate-interview`.
- Start from the available email, task, pasted exchange, calendar event, existing draft, or Flo's current request. An OmniFocus task is optional context, never an upstream requirement.
- A passing interview mention does not authorize coordination or app inspection. During an active Daily Review, stay in the review unless Flo clearly requests the detour; any reminder capture follows the review's own rules.
- Run only the parts needed for the requested logistics. A link-only request or a small revision does not require completing every step. Do not decide whether Flo wants the job, whether an exploratory call is worthwhile, or how he should prepare.
- Never send, book, RSVP, or post a LinkedIn message as part of this workflow.

Never chain automatically into `$plan-interview-prep`. Mention it only when preparation planning is a distinct next action.

## 1. 🔎 Recover context and resume

Start read-only. For new coordination, reconstruct the complete relevant source rather than relying on a snippet:

- Full Fastmail thread or pasted LinkedIn conversation, material role/brief details, booking page, and offered times.
- Existing drafts, invitations, private holds, confirmed events, and relevant calendars over the offered horizon.
- An existing OmniFocus task when available, including its note, hierarchy, dates, and Review-family tag. Do not require a task search to unlock coordination.

For resumed work, preserve settled decisions, approved wording, chosen dates, user-adjusted hours, and existing artifacts. Refresh only evidence needed for the remaining action, such as current public availability, relevant conflicts, new correspondence, or the saved draft. A small wording change does not restart the entire audit or reopen settled strategy.

Keep a compact working picture of:

- Person, company, role, stage, channel, and source links.
- Confirmed facts, working assumptions, and material unresolved choices.
- Source timezone and Flo's local timezone.
- Distinct events when the source separates a prep call, recruiter screen, panel, or exercise review. Never transfer one event's availability or deadline to another.

For longer work or a pause, save a compact local checkpoint with the latest copy, settled constraints, pending decisions, and source/artifact references. Reuse an existing working note where available; otherwise use a temporary scratch file and provide its path. Label working copy as **not a saved Fastmail draft**. Keep short exchanges in chat and avoid saving a transcript of every revision.

## 2. 🗓️ Check availability and explain the choice

Check the full relevant availability regardless of presentation. Normalize times using the offset in force on the event date, including DST transitions, and label timezones clearly. Consider hard conflicts, soft conflicts/context switching, preparation capacity, buffers, and existing holds or invitations. Do not optimize for the earliest slot.

- **Specific offered appointments:** compare every offered slot before recommending one. Show the complete matrix with conflicts, preparation window/capacity, and potential duplicates, then a preferred option and genuine fallback when available.
- **Booking link:** show daily ranges, meaningful gaps, buffers, and concerns. Do not list every interchangeable start time or turn a broad booking horizon into a slot-by-slot matrix.

### Recorded Openings configuration

`[Openings] Busy`, inspected **14 September 2026**, contains these **10 selected calendars**. Preserve account distinctions where names repeat:

| Account/group | Selected calendars |
|---|---|
| Fantastical Scheduling | Openings |
| Florian Kempenich | flori@nkempenich.com; 🍦 Flo & Mari; 🍦 Flo only (for awareness); Plan for the Day |
| Fastmail | Main (Fastmail); Time Block; flori@nkempenich.com; 🍦 Flo & Mari; 🍦 Flo only (for awareness) |

- Use this recorded membership during ordinary runs; do not inspect the calendar-set configuration each time. Continue reading live events and checking actual public availability.
- Offer a read-only configuration refresh when Flo reports a change or availability is surprising. Never modify the calendar set.
- Both Mari-only calendars are excluded. They provide awareness, not Flo's attendance. Flo & Mari and Flo's own calendars represent commitments involving Flo; do not treat every calendar visible in Fantastical as a blocking calendar.

### All-day commitments

- Do not assume an all-day commitment blocks booking. Compare commitments involving Flo with the public slots actually offered.
- If a commitment still leaves slots bookable, resolve it during Flo's existing link review before calling the link ready. Flo may confirm that the slots are intentional or approve a calendar change.
- Suggest converting the relevant all-day event to **08:00–19:00**, stating the exact event, affected date(s), and timezone. This is a proposed default, not an automatic edit.
- After approval, make the specified event change and preserve unrelated details. Re-read the event and public page; if slots remain unexpectedly open, report the unresolved mismatch.
- Preserve participant-bearing events unchanged. When one needs protection, propose an approved private timed block instead of editing the invitation.

## 3. 🔗 Prepare and review the protection mechanism

Use the authorization already given in the conversation. Do not require one blanket approval package before preparing anything reviewable.

- An explicit request for a booking link authorizes preparing or adjusting the company-specific link using settled preferences. Ask first only about unresolved material configuration choices.
- For private holds, other calendar changes, and task notes/dates, present the exact proposed changes and obtain approval unless those changes are already authorized. Bundle related unresolved changes where useful; do not repeat an approval already given.

### Booking link

- Reuse the existing company-specific link when available; otherwise duplicate the proven recruiter template. Never edit Flo's general booking link.
- Keep the link recruiter-specific, bounded, and unlisted. Use the agreed duration, minimum notice, date range, offered windows, and pre/post-meeting buffers. Defaults are starting points; retain Flo's role-specific adjustments.
- Create no candidate holds by default. Offer a strategic private hold only when Flo wants to protect a particularly important opportunity.
- Check for a Fantastical connector first; otherwise use available browser/computer control with the existing authenticated session. Authentication failure is a blocker; do not switch accounts or sources.
- Save the link, open the recruiter-facing public page, and verify its actual visible availability. Do not place an unverified URL in the reply.
- Give Flo the **clickable public link in chat** and ask him to check and, if needed, adjust its availability for this role. Agent verification does not replace his review.
- Recheck Flo's changes before calling the link or link-dependent email ready. Reuse his completed review unless the date window, offered hours, or duration materially changes. Resolve any newly surfaced availability mismatch without restarting unrelated work.

In Flo's Fantastical setup, a booking request blocks the slot immediately, **before manual confirmation**, and it remains blocked after confirmation. This is Flo's setup knowledge, not a claim about all booking providers. Do not create test bookings to verify it.

### Specific availability and confirmed conversations

- For specific times offered to the recruiter, propose protection for **every offered slot**, not only the recommendation, including the preparation buffer. Create the approved private holds with no participants, titled `HOLD: {Company} interview`.
- Preserve participant-bearing invitations unchanged. Never duplicate an existing invitation with a hold. Release unused holds only with explicit approval.
- Protect preparation immediately beforehand with approved private time: 30 minutes for a recruiter call; 60 minutes for a panel, technical, or deeper interview. Adjust when the known format warrants it.
- Verify each changed calendar artifact's title, calendar, privacy, start/end, and absence of participants.

## 4. ✉️ Refine the reply in chat, then save

- Iterate wording in chat. Do not create or update a Fastmail draft for each revision.
- Use the relationship, existing correspondence, and approved copy to guide the voice. Preserve private strategy and compensation notes unless Flo chooses to disclose them.
- State availability confidently and naturally. Acknowledge an actual delayed reply when appropriate; do not automatically apologize for scheduling constraints or insert a repeated role/exercise detail.
- Give a preferred time and real fallback, or the reviewed bounded link. Keep questions to what materially changes the action; avoid generic enthusiasm, corporate filler, and formal LLM phrasing.

When first sharing the Fantastical link, ask the recruiter to reserve through it **before** sending their own invitation. Adapt this wording naturally:

> Once you’ve found a time that works for [name/the panel], could you please reserve it through the link before sending the interview invitation? That will block it in my calendar immediately and avoid any accidental double-booking.

Keep the causal meaning: the request through Flo's link immediately reserves the slot, even if the recruiter sends a separate invitation afterwards.

Once Flo approves the wording and any link has completed review:

- Search for an existing draft before creating one. Prefer Fastmail MCP and save one reply draft in the correct thread with the approved recipients and copy.
- Check current tool capabilities rather than assuming draft-body editing is supported. Reuse or safely update an existing draft when possible. If no safe update is available, preserve it and return the revised copy, clearly labelled as unsaved; do not create a duplicate or silently delete/recreate it.
- Re-open the saved draft and verify recipients, thread, body, URL, and unsent state. Hand it back for Flo's final review and sending.
- For LinkedIn, return plain copy with the raw booking URL. Never post it.

## 5. ✅ Optional follow-up and verified handoff

### OmniFocus, when useful

- Use an existing coordination task when available. Offer a new follow-up task when useful; create it only when Flo requests it or accepts the offer. Task creation is not a condition for proceeding or finishing.
- Prefer OmniFocus Operator MCP. Apply approved updates under the owning project and applicable Daily Review rules; put an explicitly requested inbox reminder in the inbox.
- Keep notes clean, current, and navigable. Obtain approval for destructive note replacement; preserve Review-family tags and flag every mutation.
- Change only approved dates and re-read the changed task. Never complete a task before Flo actually sends or books, and do not infer either action from a task's existence.
- Record `awaiting Flo to send/book` while the reply is unsent; use `waiting on recruiter` only when supported by the actual external state.

### Failures and stop condition

Apply only authorized changes and re-read each changed artifact. Failures are independent where safe: continue unrelated approved work, but a failed link creation/save/public verification blocks dependent draft writes. Report what applied, what was skipped, and what remains; never silently substitute manual times or another slot.

Report coordination ready for Flo when:

- Flo has seen the relevant availability summary or complete offered-slot matrix.
- Any booking link has been verified and reviewed by Flo, with material changes rechecked and availability mismatches resolved.
- Approved mutations are verified. When a reply is in scope, the approved reply is saved and ready, or the clearly identified unsaved-copy fallback is handed back with its limitation.
- No logistical ambiguity can change the immediate action. If a task was created or updated, its verified state reflects the actual next action.

State exactly what is ready and what Flo needs to do next. An OmniFocus task is never required. Stop before sending, booking, and interview preparation.
