---
name: review-wttj-recommendations
description: Review Flo's Welcome to the Jungle job recommendations in his logged-in Chrome or Vivaldi session, rank them for genuine senior AI-engineering fit, flag existing application-dashboard duplicates, and capture the review in today's Obsidian journal. Use when Flo asks to scan, review, shortlist, rank, journal, or revisit Welcome to the Jungle recommendations without onboarding them as applications.
---

# Review Welcome to the Jungle Recommendations

Turn Flo's logged-in Welcome to the Jungle recommendations into a compact, durable daily-journal shortlist. This is lightweight market triage, not application onboarding.

## Required Companion Skills

- Use `chrome:control-chrome` for the logged-in Chrome or Vivaldi session.
- Use `obsidian-cli` for vault discovery, reads, writes, and verification.
- Use `obsidian-markdown` for valid journal formatting and wikilinks.
- Follow each companion skill's setup and safety rules.

## Fixed Boundaries

- Never create or update an Application Triage candidate.
- Never inspect an application form as part of this workflow.
- Never submit, save, dismiss, follow, upload, or type personal data on Welcome to the Jungle.
- Never tailor a CV, draft application answers, or invoke application-preparation skills.
- Dashboard access is read-only and used only for duplicate detection.
- Do not commit vault changes unless Flo asks.

## Inputs and Defaults

Accept either:

- an explicit recommendation count, such as `review 20`
- no count, meaning review every recommendation currently available

For “all,” stop when the recommendation surface has no unreviewed cards or further load-more result. Report the actual count. Do not invent a batch limit.

## Start from the Recommendations Home

Every review starts in a **brand-new browser tab**. Never claim or reuse an existing Welcome to the Jungle tab, even when one is already open on a relevant job.

1. Open `https://app.welcometothejungle.com/` in the user's logged-in Chrome or Vivaldi session.
2. Wait for the personalised homepage to finish rendering before reading any counts.
3. Confirm the settled page shows the recommendation-category tiles, including `All your matches`, and read their visible counts.
4. Treat `10+ jobs` as a lower bound, not an exact total.
5. Do not infer the available recommendation count from `/jobs` or a job-detail view. That surface can show one current card while the queue contains many jobs.

The first render is provisional, even after network idle. Read the page once, allow the client-side personalised view to hydrate, then read it again. Do not trust category counts until the page shows its settled personalised state, such as `Welcome back, Flo` plus content below the category grid. If the two reads disagree, use the later settled read.

## Choose the First Category Without Blocking

An explicit category from Flo always wins. Otherwise choose the first available category in this order:

1. `Jobs added this week`
2. `Artificial Intelligence`
3. `All your matches`

Use `Jobs with salaries` first only when Flo explicitly mentions salary or compensation.

State the chosen category in a short progress update and continue. Do not ask before the first batch.

## Review in Batches of Ten

Unless Flo requests a smaller number, review 10 roles and then check in. A larger explicit count remains the overall ceiling, but does not remove the checkpoint after the first 10.

At the checkpoint:

- report the 10 completed reviews and the strongest signals
- report whether the current category is exhausted or still active
- give the visible remaining count when exact, or preserve `10+` as a lower bound
- list the most relevant available next categories
- recommend `Artificial Intelligence` next when it is available and was not the first category
- ask whether to review the next 10, switch category, or stop

This checkpoint is intentional. It happens after useful work, never before the first batch.

Track reviewed job URLs across the run. When categories overlap, do not review or journal the same role twice. If Flo continues, update the same journal entry with the additional unique roles.

## Establish the Decision Lens

Keep this pass light:

1. Locate the current `Job Search` index in `TheVault`.
2. Follow its current career-positioning link rather than relying on a remembered filename.
3. Read the most recent journal feedback about job or recommendation reviews when it materially refines the ranking.
4. Do not reconstruct the full CV evidence ledger or read the whole application queue.

Prioritize:

- movement toward a senior AI-engineering identity
- substantive AI products, agents, evaluation, reliability, and supporting platforms
- preserved Staff, Lead, Principal, or strong Senior scope
- credible transfer from production and platform engineering

Penalize:

- ordinary software engineering wearing an AI label
- downlevel scope
- primarily model research or training when it requires unsupported specialization
- unwanted management, pre-sales, location, office, travel, industry, or compensation constraints

Use judgment. Preserve uncertainty when the advert does not support a confident verdict.

## Review the Recommendations

For each recommendation:

1. Capture the exact company, advertised title, and Welcome to the Jungle job URL.
2. Inspect enough of the role page to distinguish substantive work from branding.
3. Assign it to one of three provisional interest groups:
   - `Potentially interesting`
   - `Not sure`
   - `Probably not`
4. Write one short reason focused on the decision-driving signal.
5. Rank the interesting group by likely excitement and strategic AI direction.
6. Keep the other groups in reviewed order unless a later comparison clearly helps recall.

These groups predict Flo's likely interest. They do not make the deeper candidate-alignment decision owned by the application-onboarding workflow.

- **Potentially interesting**: the work itself looks exciting and deserves deeper onboarding.
- **Not sure**: the work may be interesting, but the role is a stretch or its AI substance, seniority, responsibilities, or logistics need deeper inspection.
- **Probably not**: the work itself is clearly unwanted, boring, downlevel, or incompatible. Candidate gaps alone never justify this group.

An interesting stretch belongs in `Not sure`, not `Probably not`. A role that is achievable but clearly unwanted belongs in `Probably not`.

Closed or unavailable roles still count as reviewed. Put them in `Probably not` and state that the role is unavailable.

## Verify Each Role as One Atomic Record

Treat the company, advertised title, canonical job URL, category, and one-line reason as one inseparable record.

When collecting a role:

1. Read the company, title, role evidence, and `Job` link from the same visible active card.
2. Never use an unscoped first-match query across every `/jobs/` link in the page. Welcome to the Jungle may preload adjacent cards in the DOM.
3. Keep the reason grounded only in that active card's requirements and responsibilities.

Before writing the journal, verify every record in the same reusable browser tab:

1. Open the captured canonical URL.
2. Wait for the job page's personalised client-side view to settle.
3. Confirm the resolved company and advertised title exactly match the record.
4. Re-read the role requirements and responsibilities.
5. Confirm the one-line reason accurately describes that same resolved role.

A correct URL paired with another role's reason is a failed record. Repair every mismatch before journaling. Do not write a partially verified batch.

## Detect Dashboard Duplicates

Read candidate frontmatter under the live Application Triage candidate folder. Do not modify it.

Match in this order:

1. Same canonical job or application URL, when available.
2. Same normalized company and role title.
3. Same company and a strongly overlapping title or responsibility set.

Classify matches as:

- **Confirmed duplicate** for the same role.
- **Possible duplicate** for a close but uncertain match.
- **Not a duplicate** for a different role at the same company.

Dashboard presence is positive evidence that a role or close role previously survived deeper assessment. Unless the current role is unavailable or clearly different and unwanted, a confirmed or possible dashboard match should land in `Potentially interesting` or `Not sure`, not `Probably not`.

Under the journal role's reason, add exactly one of these when applicable:

- `- = **Already tracked:** [[Candidate note]]`
- `- ? **Possible duplicate:** [[Candidate note]]`

Also summarize confirmed and possible duplicates in the final chat response.

## Write the Daily Journal Entry

Target `_Journal_/YYYY-MM-DD.md` in the user's current timezone. Preserve existing frontmatter and content.

Append one timestamped entry matching this outline:

- `= **HH:mm** Reviewed N [[Welcome to the Jungle]] recommendations`
  - a short stopping or outcome summary
  - `= **Potentially interesting · N**`
    - linked role
      - one-line reason
      - duplicate flag when applicable
  - `? **Not sure · N**`
    - linked role
      - one-line reason
      - duplicate flag when applicable
  - `! **Probably not · N**`
    - linked role
      - one-line reason
      - duplicate flag when applicable

Use standard Markdown links for job URLs and shortest-path Obsidian wikilinks for vault notes.

Before appending, search today's journal for an existing Welcome to the Jungle review containing the same role URLs. If it is the same run, update that entry instead of appending a duplicate. Never overwrite a distinct earlier review merely because it happened on the same day.

After writing, verify:

- the reviewed total equals all three group counts combined
- every reviewed role appears exactly once
- job URLs are unique within the entry
- every URL resolves to the recorded company and advertised title
- every one-line reason is supported by that resolved role's requirements or responsibilities
- duplicate wikilinks resolve to existing candidate notes
- the rest of the journal is unchanged

## Refine from Flo's Feedback

Treat later spoken reactions as a refinement of the same journal entry unless Flo starts a new review.

- Reorder role blocks to match his excitement.
- Preserve each block's link, reason, membership, and duplicate flag unless he explicitly changes them.
- If his reaction is ambiguous, leave that role in its current position.
- Move a role between groups only when his feedback clearly changes the interest category.
- Recompute headings only when group membership changes.
- Verify the block inventory before and after the edit.

## Final Response

Keep it short:

- number reviewed and journal link
- strongest two or three roles
- confirmed and possible dashboard duplicates
- any authentication, availability, or evidence limitation
