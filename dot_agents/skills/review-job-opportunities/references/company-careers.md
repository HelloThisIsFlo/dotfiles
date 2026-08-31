# Official Company Careers Playbook

Use this playbook for bounded discovery on an official company careers site. The shared classification, review-history, dashboard duplicate, journal, and onboarding-offer rules remain in `../SKILL.md`.

## Establish a Bounded Scope

A company sweep must have:

- one named company
- a supplied or Decision Context-eligible location and work shape
- the company's official careers surface

An explicit location, remote condition, team, or craft filter from Flo wins. When logistics are implicit, use `Decision Context.md` rather than inventing a broader geography.

Record the exact settled scope, including:

- company
- location or remote eligibility
- active search text and filters
- result count or lower bound
- any visible filter leakage, such as UK-wide roles appearing in a London result

## Exhaust the Current Official Result Set

For an explicit bounded request such as all Apple roles in London, enumerate the whole current result set without a ten-role checkpoint.

1. Open the official company careers search.
2. Apply the requested scope through visible non-submitting controls.
3. Wait for client-side filters and counts to settle.
4. Traverse every result page, load-more control, or finite result collection.
5. Capture the stable identity, exact title, advertised location, and official role URL for every visible listing.
6. Stop only when the bounded result surface is exhausted or a specific access limitation prevents further enumeration.

Do not claim exhaustiveness from a search-engine result page, a partial carousel, or a count that does not match the enumerated listings. When the site's visible total disagrees with enumeration, report both and use the enumerated identities for review accounting.

## Identify Before Suppressing History

Build the complete current identity inventory before filtering previously reviewed roles.

Prefer stable identity in this order:

1. official requisition or posting ID
2. canonical sanitized official role URL

Then apply the shared journal-history suppression:

- exact prior requisition ID → previously reviewed
- different requisition IDs from the same official source → new role, even when the site reused a canonical URL
- exact canonical official role URL → previously reviewed only when requisition IDs are absent or non-conflicting
- same company and title with no stable identity agreement → possible duplicate, not a suppression match
- similar title without stable identity agreement → possible duplicate, not a suppression match

An explicitly supplied role or explicit “review again” request bypasses history.

Previously reviewed roles count toward the current source total but receive no repeated role block. Inspect them only enough to resolve their stable identity and current availability; do not repeat the full triage unless Flo requested a refresh.

## Deeply Review Every Unseen Role

For each unseen identity:

1. Open the canonical official role URL.
2. Confirm exact company, title, requisition ID when available, and location eligibility.
3. Read enough mission, responsibilities, ownership, requirements, and logistics to distinguish substantive work from branding.
4. Classify it through the shared interest model.
5. Write one decision-driving reason grounded in that exact advert.
6. Run shared dashboard duplicate detection.

Closed or unavailable roles discovered during enumeration still count as newly reviewed when their stable identity was unseen. Put them in `Probably not` and state that they are unavailable.

Never inspect application fields, start an application, create an account, save a role, subscribe to alerts, or change external state.

## Company Journal Shape

Use a source-aware lead line such as:

- `= **HH:mm** Reviewed N new London-eligible [[Company]] roles`

The outcome summary must state:

- bounded source scope
- current listings enumerated
- previously reviewed identities suppressed
- newly reviewed roles
- unavailable or unverifiable identities
- confirmed exhaustion or exact limitation

Use the shared three group headings and role blocks for newly reviewed roles only.

When the exhaustive current inventory contains no unseen identities, write a compact entry containing:

- company and exact scope
- current listing total
- previously reviewed count
- `0 new roles`
- confirmed exhaustion or access limitation

Do not repeat earlier role blocks.

## Site Limitations

- If authentication gates the listing inventory, try the user's logged-in browser only when the browser contract permits it.
- If pagination or filters are broken, report the exact verified coverage and do not claim a complete company sweep.
- If the official site exposes multiple requisitions with the same title, retain each stable requisition identity separately.
- If the same requisition advertises multiple eligible locations under one identity, review it once and record the relevant locations.
