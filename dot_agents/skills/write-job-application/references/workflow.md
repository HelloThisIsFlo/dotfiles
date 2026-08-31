# Workflow Reference

## 1. Resolve the Vacancy and Candidate Record

Use Obsidian vault `TheVault`.

Accept one of:

- an existing candidate-note link or path
- an official role or application URL
- a third-party job-board URL
- a pasted advert
- an explicitly identified browser page

Search the live Applications system rather than relying on remembered paths. Match an existing candidate in this order:

1. canonicalized `job_board_url`
2. canonicalized official role or application URL
3. normalized company plus normalized advertised title

Reuse the candidate note when its role analysis and application audit are current. Treat it as stale when:

- `last_checked_on` is 14 or more days old
- the advert or form is unavailable or materially changed
- `application_route` is unknown
- prose fields or their exact instructions are not verified
- the supplied advert contradicts the record

Before invoking onboarding, load and validate Decision Context under section 2. If it is missing or unusable, stop without changing the candidate record.

When no clear current record exists, use `$onboard-job-application` to create or refresh it. That role audit may write automatically under its own contract. It must not write application prose or maintain Decision Context. Resume this workflow after onboarding instead of repeating its role analysis.

Invocation means Flo has decided to apply. Existing fit scores, gaps, and `why` inform evidence selection and claim safety; they are not a reason to debate, refuse, or reopen the application decision. Never change the candidate's shortlist or status merely because this skill was invoked.

If the input is a pasted advert without a URL, search for the exact official role and application page. If no exact live page can be verified, continue from the supplied advert, mark the application format as unverified, and state the smallest fact Flo must confirm.

## 2. Load Shared Career Context

Read the materialized application Decision Context once. Treat it as the stable, read-only policy for this workflow.

It supplies:

- identity and target lanes
- proof pillars
- current fit and positioning language
- claim boundaries
- logistics
- links to canonical career sources
- the current CV root

`context_refreshed` records when Flo last deliberately reviewed the policy. It is provenance, not an expiry date.

- Never reconstruct, refresh, or edit Decision Context during application writing.
- Never ask onboarding to refresh it; onboarding may refresh only the candidate's role and application audit.
- Age alone is never a warning and never justifies a refresh suggestion.
- If Decision Context is missing or unusable, stop before drafting and report the blocker.
- If Flo's current instruction materially conflicts with it, follow the direct instruction for this run, identify the exact mismatch, leave the note unchanged, and offer a separate deliberate context review.
  - A run-specific override may change preferences, target lanes, logistics, or positioning emphasis.
  - It never relaxes fixed workflow boundaries or turns an unsupported claim into evidence. Treat a new factual claim as evidence only when Flo explicitly supplies it.

Do not recursively re-derive Flo's career.

Resolve the CV from the live CV root:

1. read `README.md` for the repository contract
2. read `CURRENT_GOLDEN_MASTER` as the machine-readable pointer
3. read the pointed YAML
4. read `MASTER_CV.yaml` only when the current CV appears to omit a material, supportable signal

The current CV and `MASTER_CV.yaml` are approved CV claim sources. The vault's canonical Project Stories and Interview Stories may support application prose, but a claim that would be added to the CV still follows the CV workflow's provenance contract.

## 3. Inspect the Application and Research the Company

Use the official vacancy and application form as primary sources. Inspect directly in the Browser plugin, using logged-in Chrome only when appropriate and already available.

Capture the exact writing surface:

- cover-letter upload, pasted text, or both
- required versus optional status
- motivation, additional-information, and bespoke questions
- word or character limits
- supporting instructions
- whether multiple prose fields would duplicate one another

Do not infer that writing is absent behind an account gate. If the form remains gated, draft only what is justified by the visible requirements and label the unknown clearly outside the application prose.

Research the company on every run, but keep it bounded. Prefer:

1. the official product or company page that explains what is actually being built
2. one official technical, research, engineering, or current-direction source relevant to the role
3. a second high-value official source only when it materially improves the motivation

Use current public sources. Distinguish facts from hypotheses while researching. Company research may support a specific motivation, but never invent longstanding interest, emotional attachment, product use, or admiration Flo has not expressed.

## 4. Identify the Application Case

Reduce the vacancy to at most three hiring needs that are both important and useful for selection. Prefer needs such as:

- the actual product or workflow outcome
- architecture and ownership expectations
- reliability, evaluation, or operational constraints
- senior influence and ambiguity management
- a genuinely distinctive domain or company problem

Map each need to the compressed proof pillars. Then retrieve only the evidence needed to make the strongest case.

### Progressive evidence retrieval

1. Start with Decision Context and the current CV.
2. Query the Interview Stories system and inspect frontmatter signals:
   - `interview_angles`
   - `cue`
   - `company`
   - `answer_mode`
   - `project_story`
3. Read one to three of the strongest matching story bodies.
4. Follow a linked Project Story when the claim needs fuller provenance, attribution, or boundary detail.
5. Search other canonical vault notes only when the selected sources do not answer a role-specific question.
6. Stop when two or three defensible evidence hooks cover the important needs.

Prefer `answer_mode: direct`. A `bridge` story is useful when the transfer is explicit. Do not use a `missing-detail` story as strong evidence unless a deeper canonical source resolves the missing fact.

Do not create a new evidence bank. The typed Interview Stories, Project Stories, Decision Context, current CV, and targeted search are the retrieval index.

## 5. Choose What to Draft

Draft every substantive application-specific prose field that is verified and useful.

- Required motivation question:
  - answer the exact question
  - follow its stated limit or guidance
- General Additional Information field:
  - use it as a concise application note when no stronger required prose field already carries the case
- Optional cover letter alongside a required motivation answer:
  - draft it only when it adds distinct evidence or context
  - otherwise say that no additional letter is recommended
- Cover-letter upload:
  - draft the body in chat
  - offer PDF rendering only after approval
- No prose field:
  - report that no written application text is required
  - still perform the CV materiality check
- Multiple bespoke questions:
  - answer each under its exact wording
  - avoid repeating the same story unless the questions genuinely require it

Do not draft routine identity, demographic, or consent fields. For logistics questions, retrieve the existing canonical answer when available rather than improvising.

## 6. Write the Text

Default full-letter or general-note length: 120-250 words. Use a longer response only when the form explicitly asks for it, such as a 200-400-word motivation answer.

A strong default structure is:

1. Open on the specific overlap between the role's real need and Flo's experience.
2. Develop two or three evidence-backed connections.
3. Close on the contribution or problem Flo wants to continue solving.

The structure is a guide, not a template. Preserve strong natural phrasing from approved career sources where it fits.

Avoid:

- CV chronology
- generic company praise
- unsupported claims of passion or product usage
- job-description keyword mirroring
- inflated ownership
- adjective-heavy claims without evidence
- clichés and ceremonial cover-letter language
- em dashes

Do not volunteer a gap merely to appear balanced. When the employer explicitly asks about missing experience and the gap cannot be omitted honestly, use:

1. what Flo has not owned
2. the nearest real evidence
3. how he reasons at that boundary
4. the precise limit

## 7. Claim Audit

Before presenting the draft, trace every material experience claim to one loaded source. Check specifically for:

- pilot or internal beta described as production
- projected impact described as realized impact
- Staff scope described as a past formal title
- coaching or leadership described as formal management
- team ownership described as solo authorship
- adjacent ML, infrastructure, or customer experience described as direct depth
- company motivation presented as Flo's personal history without evidence

When evidence is ambiguous, retrieve the source instead of weakening the wording with a guess.

## 8. CV Materiality Check

Compare the vacancy's top needs with the current golden master.

Recommend no change when the relevant evidence is already prominent enough. Otherwise recommend at most two material changes, favouring:

- promoting or reordering an existing approved bullet
- surfacing a more relevant approved `MASTER_CV.yaml` bullet
- accurately adopting the vacancy's terminology for work Flo has genuinely done
- moving the most relevant project or evidence earlier

Do not rewrite every bullet, keyword-stuff, alter titles or dates, apply a proposed summary, or implement the changes. Name the exact evidence to promote and why it changes the application. Offer `$apply-to-job` only if Flo wants an actual tailored artifact.

## 9. Default Chat Output

Keep the normal result compact and easy to review:

```markdown
## ✍️ Ready to Paste

### <Exact field or question>

<application text>

## 🧾 Evidence Used

- <two or three concise evidence hooks>

## 🛡️ Claim Check

- <only relevant boundaries or intentionally omitted claims>

## 📄 CV Changes

No change recommended.
```

For multiple prose fields, repeat only the `### <Exact field or question>` sections. For the no-prose path, replace `Ready to Paste` with a one-line `Application Shape` result.

Keep supporting analysis to roughly twelve bullets or fewer. The application text may exceed the normal total only when the form requires it.

Do not include research citations in the application text. In default mode, name vault evidence succinctly rather than dumping source paths. If Flo requests verbose or debug mode, add:

- the hiring-needs-to-evidence map
- exact vault source paths
- official research sources
- rejected or deliberately unused claims
- CV-change rationale

## 10. Approval, Persistence, and Rendering

Draft and revise in chat without touching the candidate note.

Treat clear approval of the wording or an explicit save request as authorization to persist the exact approved prose. If approval is ambiguous, ask one short question before writing.

When saving:

- re-read the candidate note immediately before editing
- preserve frontmatter, sibling-role block, onboarding markers, managed block, and all user-authored content
- append semantic sections outside the onboarding block:
  - `# ✉️ Cover Letter`
  - `# ❓ <Exact Question>`
- save only the approved prose, not evidence notes, claim checks, CV suggestions, or research citations
- never add `created` or `modified`
- verify the saved text is byte-for-byte identical to the approved prose

If the same section already has text, do not overwrite it. Ask whether Flo wants replacement or a new version, then perform exactly that choice.

After saving:

- offer `$render-cover-letter` only when the form supports or requires a cover-letter PDF
- pass company, role, and the exact approved body to the renderer
- do not render or overwrite a PDF without Flo's request
- do not suggest rendering for ordinary free-text fields
