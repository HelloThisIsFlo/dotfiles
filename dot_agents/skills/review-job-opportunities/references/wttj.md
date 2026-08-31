# Welcome to the Jungle Playbook

Use this playbook only for Welcome to the Jungle recommendations. The shared classification, dashboard duplicate, journal, and onboarding-offer rules remain in `../SKILL.md`.

## Browser Surface

- Use `chrome:control-chrome` in Flo's logged-in Chrome or Vivaldi session.
- Start every review in a **brand-new tab**.
- Never claim or reuse an existing WTTJ tab, even when it already shows a relevant job.
- Open `https://app.welcometothejungle.com/`.

## Wait for the Personalised Home

The first render is provisional, even after network idle.

1. Read the page once.
2. Allow the client-side personalised view to hydrate.
3. Read it again.
4. Trust category counts only after the page shows its settled personalised state, such as `Welcome back, Flo` plus content below the category grid.
5. If the reads disagree, use the later settled read.

Confirm the settled page shows recommendation-category tiles, including `All your matches`, and read their visible counts.

- Treat `10+ jobs` as a lower bound, never an exact total.
- Never infer the recommendation count from `/jobs` or a job-detail page. That surface may show one active card while the queue contains many jobs.

## Inputs and Category Choice

Accept either:

- an explicit recommendation count
- no count, meaning all recommendations currently available

For “all,” keep the ten-role checkpoint but impose no overall ceiling. Stop only when the active recommendation surface has no unseen cards or further load-more result, then report the actual reviewed count.

An explicit category from Flo always wins. Otherwise choose the first available category in this order:

1. `Jobs added this week`
2. `Artificial Intelligence`
3. `All your matches`

Use `Jobs with salaries` first only when Flo explicitly mentions salary or compensation.

State the chosen category in a short progress update and continue. Do not ask before the first batch.

## Review in Batches of Ten

Unless Flo requests fewer, review 10 unique roles and then check in. A larger requested count remains the overall ceiling but does not remove the first checkpoint.

At the checkpoint, report:

- ten completed reviews and the strongest signals
- whether the current category is exhausted or active
- the exact visible remaining count, or `10+` as a lower bound
- the most relevant next categories
- `Artificial Intelligence` as the recommended next category when available and not already used
- WTTJ Save totals:
  - saved
  - already saved
  - failed or ambiguous
- current `Potentially interesting` and `Not sure` counts

Offer the available next actions:

- review the next ten
- switch category
- stop

The checkpoint happens after useful work, never before the first batch.

Track reviewed WTTJ URLs across the active run. When categories overlap, never review or journal the same role twice. WTTJ's queue supplies unseen cards, so do not suppress a card merely because the URL appears in an older journal entry.

If Flo continues, update the same journal entry with only the additional unique roles and cumulative counts.

## Collect and Verify One Atomic Role

Treat company, advertised title, WTTJ URL, classification, and reason as one inseparable record.

When collecting a card:

1. Read company, title, role evidence, and the `Job` link from the same visible active card.
2. Never use an unscoped first-match query across every `/jobs/` link. WTTJ may preload adjacent cards in the DOM.
3. Ground the reason only in that active card's requirements and responsibilities.
4. Open the captured WTTJ URL in the reusable verification tab.
5. Wait for the personalised job page to settle.
6. Confirm the resolved company and advertised title exactly match the record.
7. Re-read the role requirements and responsibilities.
8. Confirm the reason accurately describes that same resolved role.
9. Run the shared dashboard duplicate check.
10. Finalise classification using the role evidence and any duplicate evidence.
11. Perform the Save decision below before advancing away from the verified role.

A correct URL paired with another role's reason is a failed record. Repair every mismatch before journaling. Never write a partially verified batch.

## Save Interest Signals

Flo has given standing authorization for one WTTJ mutation: save roles classified as `Potentially interesting` or `Not sure` so the platform receives an explicit interest signal.

For each verified role:

- **Potentially interesting** → save
- **Not sure** → save
- **Probably not** → do not save

Apply these safeguards:

1. Use only the visible role-specific control whose accessible label or adjacent text unambiguously means Save or Saved.
2. Never infer the action from an unlabeled icon alone.
3. If the role already shows a saved state, record `already saved` and do not click it.
4. Otherwise click Save once.
5. Wait for the role-specific control to settle.
6. Verify a visible saved state, such as `Saved` or an equivalent remove-from-saved label.
7. If the target or resulting state is ambiguous, do not retry blindly; record the Save as failed or ambiguous.

Never:

- unsave a role
- save a `Probably not` role
- dismiss, follow, apply, upload, submit, or type personal data
- reinterpret another bookmark, follow, or application control as Save
- retroactively revisit older journal entries merely to save their roles

A Save failure does not invalidate an otherwise verified role. Journal it normally and report the failure in the checkpoint and final response.

## Dashboard Duplicates

Use the shared dashboard matching rules. Preserve the exact journal annotations:

- `- = **Already tracked:** [[Candidate note]]`
- `- ? **Possible duplicate:** [[Candidate note]]`

Dashboard presence remains positive assessment evidence. It does not suppress the WTTJ card from the review.

## WTTJ Journal Shape

Use the established lead line:

- `= **HH:mm** Reviewed N [[Welcome to the Jungle]] recommendations`

Below it, preserve the shared outcome summary, exact group headings, role links, reasons, and duplicate annotations.

Before appending, search today's journal for an active WTTJ review containing the same run's role URLs. Update that entry on continuation rather than appending a duplicate. Never overwrite a distinct earlier review merely because it occurred on the same day.

In the outcome summary, include cumulative reviewed and group counts. Mention aggregate Save failures when any occurred; do not add noisy per-role Save markers to successful role blocks.

After writing, apply every shared journal verification, including URL uniqueness, supported reasons, resolved duplicate wikilinks, and preservation of the rest of the journal.

## Authentication or Platform Change

- If authentication expires, stop and ask Flo to sign in. Do not switch to an unauthenticated cache, another browser, or inferred listings.
- If WTTJ changes its recommendation layout, locate the current personalised recommendation entry point through visible semantics.
- Preserve the hydration, atomic-role, batch, Save, exhaustion, and journal invariants.
- If the new UI makes the active role or Save target ambiguous, stop and report the exact ambiguity rather than guessing.

## Final Response

When the requested review ends, apply the shared final-response and conditional onboarding-offer contract.

Also report cumulative WTTJ Save totals:

- saved
- already saved
- failed or ambiguous

Do not offer onboarding at an intermediate ten-role checkpoint. Offer it when Flo ends the review and at least one role is `Potentially interesting` or `Not sure`.
