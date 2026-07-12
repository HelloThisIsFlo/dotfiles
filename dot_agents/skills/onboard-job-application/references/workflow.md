# Workflow Reference

## 1. Find the live system

Use Obsidian vault `TheVault`.

1. Locate the current Job Search index rather than relying on remembered filenames.
2. Follow its live links to:
   - current career positioning
   - current ranking context
   - the Application Triage dashboard
   - the current CV location
3. Inside Application Triage, read the live:
   - candidate template
   - triage guide
   - Base definition
   - candidate records
4. Treat the dashboard candidate properties and `triage_priority` as the live ranking.
5. Treat dated long-form ranking notes as historical evidence, never as files to update.

If an expected entry point moved, search the vault by concept and content. Do not fail merely because a remembered path changed.

## 2. Reconstruct current alignment

Build a temporary decision model for this run. Do not persist a separate profile and do not copy personal facts into the skill.

### Current CV and evidence

1. Resolve the current CV location from the live Job Search material.
2. Locate the containing `SecretAgents` CV workspace.
3. Read `resources/cv/README.md`.
4. Read the YAML named under its current section; never assume the current filename.
5. Read `MASTER_CV.yaml` only when broader reviewed evidence is needed.
6. Search the vault for role-specific evidence, claim boundaries, interview stories, and recent corrections.

The job advert is a relevance signal, not a claim source. Candidate Fit must be supported by the CV, reviewed evidence sources, or explicit vault records.

### Goals, preferences, and constraints

Read current positioning and recent job-search decisions, then search outward across the vault for:

- desired professional direction
- seniority and scope
- work that Flo wants more or less of
- location, office, travel, compensation, and family constraints
- explicit reactions to comparable roles
- honest gaps and claims Flo does not want overstated

Search recent material first, but expand when older linked context remains relevant. Prefer:

1. recent explicit statements from Flo
2. current source-of-truth notes and READMEs
3. current CV and reviewed evidence
4. recent inferred patterns across role decisions
5. older archived positioning

When sources conflict, use the newest explicit decision. Ask Flo only when recency or intent cannot resolve a material contradiction.

### Targeted saturation

Do not read the entire vault indiscriminately. Search in expanding passes:

1. current Job Search entry points
2. current CV and evidence sources
3. recent journal and decision notes
4. role/company/requirement-specific matches across the vault
5. linked or backlinked context that changes the interpretation

Stop when another pass adds no material evidence, goal, constraint, preference, or ranking distinction. Keep notes on whether each important conclusion is:

- documented fact
- expressed preference
- agent inference

## 3. Establish role truth

Use the supplied advert or URL as the starting point. Prefer the official company job page and official application form over aggregators.

Capture:

- company and exact advertised title
- what the role actually does
- seniority, ownership, and management expectations
- substantive AI content versus AI branding
- core requirements and optional requirements
- location, office cadence, travel, and work authorization
- compensation when published
- deadline, posting freshness, rolling review, and application limits
- canonical job URL and direct application URL

If a listing is stale or unavailable, find the official current page where possible and record the uncertainty.

## 4. Evaluate fit

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

### Relative ranking

Read every current candidate's scores, priority, status, and role family. Place the new role relative to the live queue using:

- Candidate Fit and Goal Fit
- strategic career value
- credible interview probability
- seniority preservation
- compensation and logistics
- application effort
- urgency or deadline
- warm path versus cold application
- how the role compounds Flo's strongest evidence

Do not mechanically add the fit scores. Assign an integer `triage_priority` from 0–100. Ties are allowed. Do not renumber existing candidates merely to create space.

Use only role families currently defined by the live triage guide unless the existing system clearly cannot represent the role; ask before introducing a new family.

## 5. Inspect the application

Use the Browser plugin for the official role and application pages. When authentication hides information, try the user's logged-in Chrome surface when it is available and appropriate.

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

If browser control is unavailable, use read-only web retrieval for role truth, mark the form audit unverified, and report the limitation.

## 6. Create or update the record

### Duplicate detection

Search candidates in this order:

1. exact or canonicalized job/application URL
2. normalized company plus normalized role title

Update the existing record when one clear match exists. Ask when multiple plausible matches remain.

For a new record, use the next unused numeric prefix in the current filename convention. Do not reorder or rename older candidates.

### Frontmatter

Copy the live template schema rather than a schema embedded in this reference. Populate the current equivalents of:

- application route, URL, work, and question labels
- Candidate Fit and Goal Fit
- company, role, and role family
- relative priority and triage status

Never manually add or modify `created` or `modified`.

Status rules:

- clear poor match → `Skip`
- viable but not prepared → blank
- demonstrably completed preparation → `Ready to Apply`
- CV-only Quick role → blank unless already explicitly marked ready
- preserve an existing `Applied`, `Ready to Apply`, or user-set `Skip`
- never downgrade an explicit user status silently

### Managed decision block

New records use one replaceable block immediately after frontmatter:

`<!-- onboard-job-application:start -->`

The block contains only useful sections:

- verdict and concise role summary
- Candidate Fit evidence and gaps
- Goal Fit alignment and trade-offs
- relative ranking rationale
- application shape and requirements
- exact questions and instructions
- blockers and unknowns
- official job and application links

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
2. Open the Base in Obsidian and force a live reload when external edits are cached.
3. Confirm:
   - the record appears
   - the derived lane matches the audited requirements
   - a CV-only role enters Apply Next
   - a Ready to Apply role enters Apply Next and leaves Needs Preparation
   - Skip and Applied records do not remain in active queues
4. Report:
   - verdict and both fit scores
   - priority and nearest comparison roles
   - application lane and remaining work
   - clickable candidate-note link
   - blockers and the exact user action needed
   - optional `$apply-to-job` handoff only when tailored CV work is worthwhile
