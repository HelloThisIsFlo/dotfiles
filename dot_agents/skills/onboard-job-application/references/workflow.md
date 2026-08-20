# Workflow Reference

## 1. Find the live system

Use Obsidian vault `TheVault`.

1. Locate the current Job Search index rather than relying on remembered filenames.
2. Follow its live links to:
   - current career positioning
   - the 🎯 Applications system (`_AgentSandbox_/💼 Job Search/🎯 Applications/`)
   - the current CV location
3. Inside 🎯 Applications, read the live:
   - `INDEX.md` (system guide, statuses, tier contract)
   - `Jobs.base` definition
   - one or two recent candidate notes in `Jobs/` as the schema example
4. There is no global ranking. Tiers and the Shortlist belong to Flo; the skill never writes them.
5. Treat dated long-form ranking notes as historical evidence, never as files to update.

If an expected entry point moved, search the vault by concept and content. Do not fail merely because a remembered path changed.

## 2. Load the decision context

Read `🎯 Applications/Decision Context.md` once. It carries the current identity, target lanes, fit-scoring guidance, proof pillars, claim boundaries, and logistics — pre-compressed from the canonical sources it links.

- **Fresh enough** (under a month old, no obvious contradiction with recent explicit decisions): use it as the decision model. Do not re-derive positioning from the vault.
- **Missing, stale, or contradicted**: re-derive from its listed canonical sources (positioning notes, CV `README.md` → current golden master, recent journal decisions), then update `Decision Context.md` and its `context_refreshed` date before continuing.
- Flo's direct edits to the note are current truth; never revert them during a refresh without asking.

Search the vault only for **role-specific** evidence the note does not answer — a particular technology claim, an interview story, a recent correction about a comparable role.

The job advert is a relevance signal, not a claim source. Candidate Fit must be supported by the CV, the decision context, or explicit vault records. Respect every claim boundary in the note.

## 3. Establish official role facts

Use the supplied advert or URL as the starting point. Before following its links, classify and retain the starting URL:

- If it is a third-party job-board listing such as Welcome to the Jungle or LinkedIn, sanitize it and preserve it as `job_board_url`.
- Keep `job_board_url` separate from the canonical official role URL and `application_url`.
- Leave `job_board_url` blank for an official company URL, pasted advert or browser page without a distinct job-board URL.
- On an existing record, preserve a non-empty `job_board_url` unless Flo explicitly asks to replace it.
- Allow `job_board_url` and `application_url` to match when the job board also hosts the application.

Prefer the official company job page and official application form over aggregators for role facts and application inspection.

Capture:

- company and exact advertised title
- what the role actually does
- seniority, ownership, and management expectations
- substantive AI content versus AI branding
- core requirements and optional requirements
- location, office cadence, travel, and work authorization
- compensation when published
- deadline, posting freshness, rolling review, and application limits
- original job-board URL when supplied
- canonical job URL and direct application URL

If a listing is stale or unavailable, find the official current page where possible and record the uncertainty.

Before persisting any job-board, role or application URL:

- strip URL credentials, fragments and tracking parameters
- redact query values that carry tokens, sessions, invitations, signatures, authentication, keys or authorization codes
- when redaction breaks access, store the public URL or page descriptor and record that a live session is required
- never copy the sensitive value into a candidate note or batch artifact

## 4. Inspect the role and application

Use the Browser plugin for the official role and application pages. When authentication hides information, try the user's logged-in Chrome surface when it is available and appropriate.

Perform this inspection directly — no sub-agents, no browser workers. For multiple inputs, inspect and finish each role sequentially in the same context.

Allowed browser actions:

- open and navigate
- click non-submitting controls and application steps
- inspect visible text, fields, requirements, and validation labels
- take screenshots when they help verification

Forbidden actions:

- account creation
- sign-in attempts using credentials
- typing or uploading personal information
- saving drafts externally
- accepting consequential terms
- submitting any form

Capture:

- whether CV or résumé upload is required
- cover letter and whether it is optional
- motivation or additional-information fields
- salary questions
- exact bespoke questions and their instructions
- external exercises or assessment links
- application caps or special constraints

Use short labels in `application_questions`; preserve exact wording and instructions in the note body. Optional writing still belongs in `application_work`.

If blocked:

- set `application_route` to `account-gated`
- record visible steps and exactly what remains unknown
- do not infer that unknown writing is absent
- finish the record with the evidence available
- give Flo the direct link and a precise request for what to report back

If browser control is unavailable, use read-only web retrieval for official role facts, mark the form audit unverified, and report the limitation.

## 5. Evaluate fit

### Candidate Fit

Answer: **How strong is the current evidence that Flo can perform and interview for this role?**

Use the live score meaning documented in the current ranking material. Preserve the existing 1–5 scale and half-point increments. Explain:

- strongest direct evidence
- transferable adjacent evidence
- meaningful gaps
- claims that must not be overstated

### Goal Fit

Answer: **Would obtaining this role move Flo toward the professional identity and working conditions he currently wants?**

Use current vault evidence for trajectory, seniority, substantive work, logistics, compensation, and trade-offs. Do not equate comfortable skill overlap with strategic value.

### The `why` verdict

Write one decisive sentence that lets Flo judge the role from the board without opening the note — the single most decision-driving trade-off or strength. It becomes the `why` property and the opening callout of the managed block.

There is no numeric priority and no ranking against other candidates. Never write `tier`; comparing and shortlisting are Flo's moves.

Use only role families currently defined in `INDEX.md` unless the existing system clearly cannot represent the role; ask before introducing a new family.

## 6. Create or update the record

### Duplicate detection

Search candidates in this order:

1. exact or canonicalized `job_board_url`
2. exact or canonicalized job/application URL
3. normalized company plus normalized role title

Update the existing record when one clear match exists. Ask when multiple plausible matches remain.

For a new record, use the next unused numeric prefix in the current filename convention. Do not reorder or rename older candidates.

### Frontmatter

Copy the schema from a recent candidate note in `Jobs/` rather than a schema embedded in this reference. Populate the current equivalents of:

- application route, `job_board_url`, application URL, work, and question labels
- Candidate Fit and Goal Fit
- company, role, and role family
- `status` and the one-sentence `why`
- semantic dates: `added_on` and `last_checked_on`
- leave `tier` untouched

Never manually add or modify `created` or `modified`.
Never clear an existing `job_board_url` merely because a later run starts from an official URL or pasted advert.

Date rules (`YYYY-MM-DD`, Europe/London):

- new record → set both `added_on` and `last_checked_on` to today
- existing record → preserve `added_on` permanently
- confirmed live refresh → set `last_checked_on` to today after inspecting the official advert or application flow
- confirmed unavailable → set `last_checked_on` to today and `status: closed`
- interrupted rerun, duplicate lookup, scoring change, preparation edit, or managed-block rewrite without a live-page check → preserve both dates

Status rules (`status` values: `inbox`, `deciding`, `applied`, `passed`, `closed`):

- clear poor match → `passed`
- evaluated and viable → `deciding`
- new records also get `shortlist: false`
- role verifiably gone → `closed`
- preserve an existing `applied` or user-set `passed`
- never downgrade an explicit user status silently

### Sibling-roles block

Every note carries one dataviewjs block between `<!-- sibling-roles:start -->` and `<!-- sibling-roles:end -->`, placed between the frontmatter and the managed decision block. It dynamically lists the company's other roles and warns when one is applied. On a new record, copy it verbatim from any existing note in `Jobs/`. On updates, leave it untouched (only ever replace it wholesale if the canonical version in the corpus has changed).

### Managed decision block

New records use one replaceable block after the sibling-roles block:

`<!-- onboard-job-application:start -->`

The block contains only useful sections:

- verdict and concise role summary
- Candidate Fit evidence and gaps
- Goal Fit alignment and trade-offs
- application shape and requirements
- exact questions and instructions
- blockers and unknowns
- job-board, official job and application links

Keep the block concise without imposing a word limit:

- state each role fact, trade-off and application requirement once
- preserve exact questions, evidence boundaries and material blockers even when they make the block longer

`<!-- onboard-job-application:end -->`

Do not repeat the filename as an H1. Use a result-first callout and `##` sections.

On later runs, replace only the managed block. Preserve everything outside it, including cover letters, drafted answers, preparation notes, and user commentary.

For a legacy record without markers:

- update safe frontmatter fields
- insert a new managed block immediately after frontmatter
- preserve the entire existing body untouched
- do not attempt a broad rewrite or deduplication

## 7. Verify and report

1. Confirm the candidate note is valid Obsidian Markdown and its frontmatter parses.
2. Open `Jobs.base` in Obsidian (or query it via the Obsidian CLI) and force a live reload when external edits are cached. For multiple roles, one check at the end of the run covers all written records.
3. Confirm:
   - the record appears in the expected view (`🤔 Deciding`, `🚫 Out`, …)
   - the derived lane emoji matches the audited requirements
   - passed and applied records do not appear in the Deciding views
4. Report:
   - verdict (`why`) and both fit scores
   - application lane and remaining work
   - clickable candidate-note link
   - blockers and the exact user action needed
   - optional `$apply-to-job` handoff only when tailored CV work is worthwhile
