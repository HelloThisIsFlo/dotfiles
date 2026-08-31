# LinkedIn Playbook

Use this playbook only for LinkedIn searches or postings. The shared classification, review-history, dashboard duplicate, journal, and onboarding-offer rules remain in `../SKILL.md`.

## Browser Surface and Scope

- Use `chrome:control-chrome` in Flo's logged-in Chrome session.
- Start an active search in a new tab rather than claiming an unrelated LinkedIn tab.
- An explicit query, company, location, remote filter, or supplied search URL wins.
- When Flo leaves logistics implicit, use the eligible locations and work shape in `Decision Context.md`.
- Record the settled search phrase, location, filters, sorting when visible, and result count or lower bound.

Wait for LinkedIn's client-side search and selected job panel to settle before reading result cards. If authentication expires or the page becomes an interstitial, stop and report the exact action Flo must take.

## Bounded Batch

One LinkedIn batch has two independent ceilings:

- scan at most **50 unique result cards**
- deeply review at most **10 previously unseen roles**

Stop earlier when the current search is exhausted.

Count every unique result card toward the 50-card scan ceiling, including:

- previously reviewed roles
- unavailable roles
- roles selected for deep review

Uniqueness is by LinkedIn numeric job ID. A repeated rendering of the same job ID is one card for the ceiling and is never counted or reviewed twice.

At the checkpoint, report:

- visible result total or lower bound
- cards scanned
- roles suppressed as previously reviewed
- unseen roles deeply reviewed
- whether the search is exhausted
- strongest signals and both selected-group counts

Offer another batch and the shared onboarding handoff. Persist the last scanned job ID and the set of IDs already counted using the exact hidden marker defined under **LinkedIn Journal Shape**. A continuation of the same active search updates that entry and resumes after the last scanned identity; if LinkedIn reordered the cards, rescan as needed but do not count an already-recorded ID again.

## Stable LinkedIn Identity

Capture the numeric LinkedIn job ID from stable posting shapes such as:

- `/jobs/view/<id>`
- a title slug ending in the numeric job ID
- `currentJobId=<id>`

Canonicalize the journal link to a public LinkedIn posting URL carrying that job ID. Remove search-state, tracking, session, and recommendation parameters.

Within the active run:

- never scan or review one LinkedIn job ID twice
- never use the selected panel's first generic `/jobs/` link when multiple cards are preloaded
- bind company, title, evidence, and ID to the same visible result card

Apply the shared historical review suppression before deep inspection. Exact prior LinkedIn job ID or canonical posting URL suppresses the bulk-search result indefinitely. Company and title alone never suppress it.

An explicitly supplied posting or explicit “review again” request bypasses suppression.

## Verify Each Selected Role

For each unseen role selected for review:

1. Open the stable LinkedIn posting URL.
2. Wait for the selected posting to settle.
3. Confirm exact company, advertised title, and numeric job ID.
4. Read enough responsibilities and requirements to distinguish substantive work from branding.
5. When a trustworthy official company advert is directly available, open it in a separate tab and use it to verify role facts.
6. Retain the LinkedIn posting as the originating journal link.
7. Do not inspect application-form fields or proceed through an application flow.
8. Classify and write the one-line reason using only evidence from the matched role.

If LinkedIn and the official advert disagree materially, preserve the uncertainty, state the mismatch, and do not silently merge the records.

## External-State Boundary

LinkedIn review is read-only.

Never:

- save a role
- follow a company or person
- connect or message
- start or submit Easy Apply
- upload a file
- type personal data
- change search alerts or profile settings

If a control's effect is ambiguous, do not click it.

## LinkedIn Journal Shape

Use a source-aware lead line such as:

- `= **HH:mm** Reviewed N new [[LinkedIn]] roles · <search scope>`

The outcome summary must include cards scanned, exact prior-review suppression count, new-review count, and exhaustion state.

Use the shared three group headings and role-block shape. The role link is the canonical LinkedIn posting URL; duplicate annotations remain candidate-note wikilinks.

When the active search is not exhausted, place exactly one continuation marker inside the same journal entry, after its visible content:

`<!-- review-job-opportunities:linkedin-scan last_job_id=123 counted_job_ids=123,456 -->`

- `last_job_id` is the final unique LinkedIn job ID counted in the latest batch.
- `counted_job_ids` contains every unique numeric job ID counted for this active search, comma-separated without spaces and in first-seen order.
- Update this marker in place after each incomplete batch. Never append a second marker for the same entry.
- On continuation, skip every ID already in `counted_job_ids`, even when LinkedIn reordered the cards.
- When the search is exhausted, remove the marker and retain the visible exhaustion summary.

The marker is hidden continuation state inside the journal, not review history, frontmatter, or a separate schema.

When all scanned roles were previously reviewed and the search is exhausted or the 50-card ceiling is reached, write the shared compact zero-new entry without repeated role blocks.
