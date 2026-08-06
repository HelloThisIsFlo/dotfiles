---
name: add-flight-to-calendar
description: Find flight bookings in Fastmail and add or audit complete, buffered, timezone-verified flight itineraries in the correct calendar. Use when Flo asks to add, calendar, schedule, audit, or repair booked flights, booking references, airport-arrival plans, check-in, bag-drop, security, immigration, gate, boarding, or related travel timelines.
---

# Add Flight to Calendar

Turn an authoritative flight booking into a verified calendar itinerary. Include each flight plus the airport preparation blocks that make it realistically catchable.

## Choose the operating mode

- A direct request such as “add this flight”, “put this booking in my calendar”, or “do the same for this trip” authorizes creating or updating calendar events once calendar ownership is clear.
- An exploratory request such as “what would you add?”, “audit this booking”, or “show me the timeline” is read-only. Research and present the result without changing Fastmail or OmniFocus.
- Explicit user context outranks inference. If Flo already says who travels on each leg or names the target calendar, use that information and do not ask again.

## Workflow

1. Find the authoritative booking.
2. Extract and reconcile every leg.
3. Research realistic airport buffers.
4. Resolve the calendar separately for each leg.
5. Inspect existing calendar events.
6. Create or repair the itinerary when authorized.
7. Re-query and verify every event.
8. Reconcile one exact OmniFocus task when eligible.

Do not complete a later step when an earlier safety check is unresolved.

## 1. Find the authoritative booking

- Search Fastmail using the booking reference first, then airline, flight numbers, route, dates, and confirmation language.
- Read all plausible booking, ticket, itinerary, and schedule-change messages. Do not rely on an email preview.
- Prefer the newest authoritative schedule for each leg while retaining passenger, baggage, seat, and fare details from earlier messages when later notices omit them.
- Treat an airline-issued booking, e-ticket, or schedule-change notice as authoritative. Never infer changed times from an unrelated calendar event.
- If multiple bookings remain genuinely plausible, stop and ask which one Flo means.
- Never modify, archive, or send email as part of this workflow.

Extract per leg:

- Booking reference and manage-booking link.
- Airline and flight number.
- Origin, destination, and terminals.
- Departure and arrival local dates and times.
- Origin and destination IANA timezones.
- Absolute flight duration.
- Passengers shown for that leg or booking.
- Seats, cabin or fare, checked baggage, and cabin baggage.
- Booking-specific check-in, bag-drop, security, gate, or boarding cutoffs.

Do not put payment-card, billing, ticket-document, or other unnecessary sensitive details into calendar notes.

## 2. Research the airport timeline

Use current primary sources only:

1. The latest booking-specific instructions.
2. The airline’s official guidance.
3. The departure airport’s official guidance.

Establish:

- Recommended airport arrival time.
- Check-in and bag-drop opening and closing times.
- Passport, visa, or document-verification requirements.
- Security, customs, and exit-immigration sequence where applicable.
- Gate publication, travel-to-gate, gate-closing, and boarding rules.
- Family, infant, accessibility, terminal-transfer, satellite-gate, congestion, holiday, or seasonal factors relevant to this booking.

Booking-specific hard times override generic advice. Work backwards from departure and the strictest cutoff. Use conservative judgment when guidance provides a range. If an official detail is unavailable, preserve the uncertainty and use a reasonable buffer; never present an invented cutoff as official.

Door-to-airport travel is outside the default itinerary. Add it only when the starting point, transport method, and credible duration are known.

## 3. Resolve the calendar per leg

List Fastmail calendars before writing and resolve the exact live calendar name. The IDs below are expected anchors; do not silently use an ID if its live name differs.

- Two or more confirmed passengers on a leg:
  - Use `🍦 Flo & Mari`.
  - Expected calendar ID
    - `C0rXV`
- Exactly one passenger shown:
  - Finish the read-only booking extraction and timeline research first.
  - Before any calendar or OmniFocus mutation, ask whether that leg is genuinely Flo-only or whether Mari is travelling on a separate booking or missing from the confirmation.
  - Bundle all ambiguous legs into one question. Do not create one confirmation round trip per leg.
- Confirmed Flo-only leg:
  - Use `Main (Fastmail)`.
  - Expected calendar ID
    - `CC-`
- Mari travelling despite not appearing on Flo’s confirmation:
  - Use `🍦 Flo & Mari`.
- Any other unclear ownership:
  - Ask for the calendar rather than guessing.

Apply the decision separately to every leg. A solo outbound and shared return use different calendars. Put each leg’s preparation blocks on the same calendar as its flight event.

## 4. Inspect existing events

Before creating anything, search the travel window across all calendars using:

- Booking reference.
- Flight number.
- Route and travel date.

Classify each intended event.

- Exact and correct
  - Reuse it.
- One unambiguous incomplete or incorrect match
  - Update it when the request authorizes writes.
- Missing
  - Create it when authorized.
- Multiple plausible matches or conflicting duplicates
  - Stop before changing them, preserve everything, and ask.

Never blindly create a second itinerary. Never delete duplicate or conflicting events automatically.

## 5. Build each leg

Create one event for the flight and the applicable preparation sequence. Adapt the wording to the actual airport process; omit irrelevant steps.

Typical titles

- `🧳 Arrive + check in / bag drop`
- `🛂 Security + departure controls`
- `☕ Airside reset + monitor gate`
- `🚪 At gate + boarding`
- `✈️ {FLIGHT} · {ORIGIN} → {DESTINATION}`

Event rules

- Use the departure airport’s local timezone for the preparation blocks and flight start.
- Make preparation blocks contiguous, non-overlapping, and ending exactly at flight departure.
- Give the flight its true absolute duration, including overnight and date-line crossings.
- Put the local arrival time and destination timezone in the flight description.
- Include useful operational context: booking reference, terminals, passengers, seats, cabin, baggage, manage-booking link, hard cutoffs, and official source links.
- Use concise locations such as the airport and terminal.
- Do not add invitees or send invitations.

## 6. Verify timezones and persistence

Never trust the write response alone. Re-query every created or updated event by ID, booking reference, or flight number.

For every event

1. Calculate the expected UTC instant from the intended local date/time and the departure airport’s IANA timezone for that travel date. Use a timezone-aware calculation such as Python’s standard `zoneinfo` when useful.
2. Compare the read-back start, timezone, duration, calendar, title, description, and location with the intended value.
3. For flights, also calculate arrival from the destination timezone and confirm the absolute duration.
4. Check that the leg contains no gaps, overlaps, or duplicate events.

Fastmail may incorrectly apply the current seasonal offset to a future event. If the stored instant differs:

- Measure the exact observed delta for that individual event.
- Correct using that delta and re-query.
- Never hard-code a one-hour correction or reuse one event’s correction across other dates or timezones.
- If two careful repair attempts do not produce the exact expected instant, stop, report the mismatch, and do not reconcile OmniFocus.

Success requires correct absolute instants and correct local display, not merely a returned `timeZone` label. A different returned label is diagnostic rather than an automatic failure only when both the exact instant and the intended local display are independently proven correct.

## 7. Reconcile OmniFocus

Run this only for an authorized write request after every intended calendar event has passed verification. Skip it when Flo asks for calendar-only work or a read-only audit.

Search using the booking reference, flight number, route, dates, and wording such as “add flights to calendar”. Complete and flag a task only when exactly one match is:

- Explicitly about adding this booking or these flights to the calendar.
- A remaining leaf task with no children.
- Filed inside a real project rather than loose in the inbox.
- Non-recurring.

Complete and flag that task without changing its notes, dates, project, or unrelated tags. If the match is missing, ambiguous, recurring, an inbox item, or a parent task, leave OmniFocus unchanged and report why.

## Report the outcome

Keep the final response concise and organize it per leg:

- Calendar used.
- Flight and preparation timeline in the departure timezone.
- Buffer rationale and any important hard cutoffs.
- Verification result, including timezone and duplicate checks.
- OmniFocus reconciliation result.
- Any intentionally omitted door-to-airport travel or unresolved uncertainty.
