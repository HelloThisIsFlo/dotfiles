# Workflow Reference

## 1. Find the live system

Use Obsidian vault `TheVault`.

1. Locate the current Job Search index rather than relying on remembered filenames.
2. Follow its live links to:
   - current career positioning
   - the 🎯 Applications system (`_AgentSandbox_/💼 Job Search/🎯 Applications/`)
   - the current CV location
3. Inside 🎯 Applications, read the live:
   - `INDEX.md` (system guide, statuses, shortlist contract)
   - `Jobs.base` definition
   - one or two recent candidate notes in `Jobs/` as the schema example
4. There is no global ranking. The Shortlist belongs to Flo; the skill initializes new roles as unselected and never changes an existing shortlist choice.
5. Treat dated long-form ranking notes as historical evidence, never as files to update.

If an expected entry point moved, search the vault by concept and content. Do not fail merely because a remembered path changed.

## 2. Load the decision context

Read `🎯 Applications/Decision Context.md` once. It carries the stable identity, target lanes, fit-scoring guidance, proof pillars, claim boundaries, and logistics used by both opportunity review and onboarding.

- Treat it as authoritative, read-only policy for this workflow.
- `context_refreshed` records when Flo last deliberately reviewed the policy. It is provenance, not an expiry date.
- Never reconstruct, refresh, or edit the note during onboarding.
- Age alone is never a warning and never justifies a refresh suggestion.
- If the note is missing or unusable, stop and report the blocker rather than reconstructing it implicitly.
- If Flo's current instruction materially conflicts with the note, follow the direct instruction for this run, identify the exact mismatch, leave the note unchanged, and offer a separate deliberate context review.
  - A run-specific override may change preferences, target lanes, logistics, or scoring interpretation.
  - It never relaxes fixed workflow boundaries or turns an unsupported claim into evidence. Treat a new factual claim as evidence only when Flo explicitly supplies it.

Search the vault only for **role-specific** evidence the note does not answer — a particular technology claim, an interview story, a recent correction about a comparable role.

The job advert is a relevance signal, not a claim source. Candidate Fit must be supported by the CV, the decision context, or explicit vault records. Respect every claim boundary in the note.

## 3. Resolve review-journal handoffs

When Flo refers to roles from `$review-job-opportunities`, use the journal entry as the durable handoff rather than asking him to paste every URL again.

Resolve the entry in this order:

1. Explicit journal link or date and timestamp.
2. Source-qualified reference, such as “today's Apple review” or “the latest LinkedIn batch.”
3. The review completed in the active conversation.
4. The latest unambiguous matching review entry.

Ask only when multiple entries remain plausible. Never silently combine distinct review runs.

Unless Flo names a narrower subset:

1. Read role links from `Potentially interesting` in their ranked order.
2. Then read role links from `Not sure` in their journal order.
3. Exclude `Probably not`.
4. Include roles marked `Already tracked` or `Possible duplicate`; the normal candidate duplicate rules decide whether to update or skip them.

Extract the external role link from each role block. Also carry any `Already tracked` or `Possible duplicate` candidate wikilink as duplicate-resolution evidence; it is not the external role input. Accept both the legacy WTTJ journal shape and the generic source-aware shape. A compact zero-new review contains no onboarding inputs.

Treat each extracted link exactly like a directly supplied input. Preserve a WTTJ or LinkedIn URL as `job_board_url` before following an official role or application link.

## 4. Establish official role facts

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

## 5. Inspect the role and application

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

## 6. Evaluate fit

### Candidate Fit

Answer: **How strong is the current evidence that Flo can perform and interview for this role?**

Use the live score meaning documented in the current ranking material. Preserve the existing 1–5 scale and half-point increments. Explain:

- strongest direct evidence
- transferable adjacent evidence
- meaningful gaps
- claims that must not be overstated

Open the Candidate Fit section with `### 🔢 Why This Score`. Make the score legible through a short strength-versus-gate summary, then organise the proof under semantic evidence, gap, and claim-boundary headings. The structure must make that exact score understandable rather than merely listing matching keywords.

### Goal Fit

Answer: **Would obtaining this role move Flo toward the professional identity and working conditions he currently wants?**

Use current vault evidence for trajectory, seniority, substantive work, logistics, compensation, and trade-offs. Do not equate comfortable skill overlap with strategic value.

Open the Goal Fit section with `### 🔢 Why This Score`. Make the strategic alignment and decisive trade-offs legible first, then organise trajectory, seniority, work shape, and logistics under semantic headings. The structure must explain why obtaining this particular role would or would not advance Flo's current direction.

### The `why` verdict

Write one decisive sentence that lets Flo judge the role from the board without opening the note — the single most decision-driving trade-off or strength. It becomes the `why` property and the opening callout of the managed block.

There is no numeric priority and no ranking against other candidates. Never promote or remove a role from the Shortlist; comparing and shortlisting are Flo's moves.

Use only role families currently defined in `INDEX.md` unless the existing system clearly cannot represent the role; ask before introducing a new family.

## 7. Create or update the record

### Duplicate detection

Search candidates in this order:

1. A journal `Already tracked` target whose stable role identity matches the incoming role.
2. Exact stable source identity in canonicalized `job_board_url`, job URL, or application URL:
   - source requisition or posting ID
   - LinkedIn numeric job ID
   - canonical public role URL when no separate ID exists
3. Exact or canonicalized `job_board_url`.
4. Exact or canonicalized job/application URL.
5. Normalized company plus normalized role title, but only when the available URLs and IDs do not prove that the openings are distinct.

Open a journal duplicate target before deciding:

- `Already tracked` is strong identity evidence, not permission to overwrite blindly. Verify that its URLs or stable source ID match the incoming role.
- `Possible duplicate` is a candidate to inspect, never proof of identity.
- Compare identities within their source. A shared official requisition or posting ID confirms the same opening; different official IDs from the same source prove distinct openings even when company, title, or canonical URL match.
- Different LinkedIn IDs prove distinct openings only when no shared official identity maps them to the same opening. A LinkedIn ID and an official requisition ID are complementary rather than conflicting.
- When official IDs are absent or non-conflicting, compare canonical URLs and substantive responsibilities and preserve uncertainty rather than collapsing two openings.

Update the existing record when one clear match exists. Ask when multiple plausible matches remain.

For a new record, use the next unused numeric prefix in the current filename convention. Do not reorder or rename older candidates.

### Frontmatter

Copy the schema from a recent candidate note in `Jobs/` rather than a schema embedded in this reference. Populate the current equivalents of:

- application route, `job_board_url`, application URL, work, and question labels
- Candidate Fit and Goal Fit
- company, role, and role family
- list-valued type membership and application status:
  ```yaml
  type:
    - "[[Job Application]]"
  application_status: deciding
  ```
- the one-sentence `why`
- semantic dates: `added_on` and `last_checked_on`
- preserve the existing `shortlist` value on updates

Never manually add or modify `created` or `modified`.
Never clear an existing `job_board_url` merely because a later run starts from an official URL or pasted advert.

Date rules (`YYYY-MM-DD`, Europe/London):

- new record from a review-journal handoff → set `added_on` to that review entry's date and `last_checked_on` to today after the live audit
- other new record → set both `added_on` and `last_checked_on` to today
- existing record → preserve `added_on` permanently
- confirmed live refresh → set `last_checked_on` to today after inspecting the official advert or application flow
- confirmed unavailable → set `last_checked_on` to today and `application_status: closed`
- interrupted rerun, duplicate lookup, scoring change, preparation edit, or managed-block rewrite without a live-page check → preserve both dates

Application-status rules (`application_status` values: `inbox`, `deciding`, `applied`, `passed`, `closed`):

- clear poor match → `passed`
- evaluated and viable → `deciding`
- new records also get `shortlist: false`
- role verifiably gone → `closed`
- preserve an existing `applied` or user-set `passed`
- never downgrade an explicit user-set `application_status` silently

### Sibling-roles block

Every note carries one dataviewjs block between `<!-- sibling-roles:start -->` and `<!-- sibling-roles:end -->`, placed between the frontmatter and the managed decision block. The block delegates to the shared view:

```dataviewjs
await dv.view("__meta__/_Dataview_/jobSiblingRoles");
```

On a new record, insert this canonical call. On updates, leave the markers and call intact. Never copy the shared implementation into a role note.

### Managed decision block

New records use one replaceable block after the sibling-roles block:

`<!-- onboard-job-application:start -->`

Use `apply-style` inside this block. Its structure, hierarchy, and semantic-emoji guidance controls presentation; this workflow's evidence, frontmatter, marker, and preservation rules remain authoritative.

The opening callout is a compact decision map:

- Use the verdict-appropriate callout type (`success`, `warning`, `question`, or `failure`) and a short hook.
- Leave a blank `>` line after the title.
- Keep the body bullet-only.
- Show:
  - `🧩 **Candidate Fit** → **X/5**`
  - `🎯 **Goal Fit** → **X/5**`
  - `✅ **Why it works**`
  - `⚠️ **What holds it back**`
  - `🔑 **Bottom line**`
- Preserve the decision encoded by the frontmatter `why`, but split its pull and gate into scannable bullets rather than repeating one long sentence.
- Do not use the callout as a substitute for the role summary or score rationales.

After the callout, use this hierarchy:

1. `## 🧭 Role Summary`
   - `### 🎯 Mission`
   - `### 🛠️ What You'd Own`
   - `### 🤝 How You'd Work`
   - Describe the team or product mission, actual responsibilities, ownership or seniority, and substantive technology or AI content.
   - Keep this source-backed and role-focused. Do not mix in evidence that Flo can perform it.
2. `## ✨ Why It Might Be Interesting`
   - Use role-specific semantic `###` headings for the genuinely attractive dimensions.
   - Connect the actual work to Flo's direction or working preferences, including when the role ultimately scores poorly.
3. `## 🧩 Candidate Fit · X/5`
   - `### 🔢 Why This Score`
   - `### ✅ Direct Evidence`
   - `### 🔄 Transferable Evidence` when applicable
   - `### ⚠️ Material Gaps`
   - `### 🧱 Claim Boundary`
   - Use selective `####` headings only when a dense evidence section contains genuinely distinct stories, skills, or proof groups.
4. `## 🎯 Goal Fit · X/5`
   - `### 🔢 Why This Score`
   - `### 🚀 Professional Direction`
   - `### 🧭 Seniority & Scope`
   - `### ⚖️ Work Shape`
   - `### 📍 Logistics`
   - `### 🚦 Application Constraint` when relevant
5. `## 📝 Application Shape`
   - `### ✍️ Lane`
   - `### 📦 Required`
   - `### ➕ Optional` when applicable
   - `### 🚫 Not Required` when known
   - `### ❓ Exact Questions` when available; preserve one question per quote block
   - `### 📝 Supporting Instructions` when available; preserve exact wording in quote blocks
   - Record material blockers and unknowns under a clearly named semantic heading when needed.
6. `## 🔗 Sources`
   - Preserve job-board, official-role, and application links as applicable.

Omit inapplicable groups rather than emitting empty headings. Use semantic emoji consistently, keep leaf bullets mostly undecorated, and make the document's map legible from its headings alone.

Scannability comes from hierarchy, not factual compression:

- preserve every substantive role fact, rationale, trade-off, application requirement, exact question, evidence boundary, and material blocker
- state each fact once when restructuring makes duplication unnecessary
- impose no word limit

`<!-- onboard-job-application:end -->`

Do not repeat the filename as an H1. Use a result-first callout and `##` sections.

On later runs, replace only the managed block. Preserve everything outside it, including cover letters, drafted answers, preparation notes, and user commentary.

For a legacy record without markers:

- update safe frontmatter fields
- insert a new managed block immediately after frontmatter
- preserve the entire existing body untouched
- do not attempt a broad rewrite or deduplication

## 8. Verify and report

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
