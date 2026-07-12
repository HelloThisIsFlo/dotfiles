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

If Flo identifies a specific open Welcome to the Jungle page, use it. Otherwise open the recommendations surface in his logged-in Chrome or Vivaldi session.

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
3. Assign it to one of two groups:
   - `Potentially interesting`
   - `Not interesting`
4. Write one short reason focused on the decision-driving signal.
5. Rank the interesting group by likely excitement and strategic AI alignment.
6. Keep the rejected group in reviewed order unless a later comparison clearly helps recall.

Closed or unavailable roles still count as reviewed. Put them in `Not interesting` and state that the role is unavailable.

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
  - `! **Not interesting · N**`
    - linked role
      - one-line reason
      - duplicate flag when applicable

Use standard Markdown links for job URLs and shortest-path Obsidian wikilinks for vault notes.

Before appending, search today's journal for an existing Welcome to the Jungle review containing the same role URLs. If it is the same run, update that entry instead of appending a duplicate. Never overwrite a distinct earlier review merely because it happened on the same day.

After writing, verify:

- the reviewed total equals both group counts combined
- every reviewed role appears exactly once
- job URLs are unique within the entry
- duplicate wikilinks resolve to existing candidate notes
- the rest of the journal is unchanged

## Refine from Flo's Feedback

Treat later spoken reactions as a refinement of the same journal entry unless Flo starts a new review.

- Reorder role blocks to match his excitement.
- Preserve each block's link, reason, membership, and duplicate flag unless he explicitly changes them.
- If his reaction is ambiguous, leave that role in its current position.
- Move a role between groups only when his feedback clearly changes the verdict.
- Recompute headings only when group membership changes.
- Verify the block inventory before and after the edit.

## Final Response

Keep it short:

- number reviewed and journal link
- strongest two or three roles
- confirmed and possible dashboard duplicates
- any authentication, availability, or evidence limitation

