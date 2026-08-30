---
name: write-job-application
description: Draft concise, factual cover-letter text and application-form answers for a role Flo has decided to pursue. Use for a vacancy URL, pasted advert, application page, or existing Obsidian candidate note when the goal is ready-to-review submission writing and material CV advice. Do not use to choose whether Flo should apply, submit forms, tailor a CV artifact, or render a PDF.
---

# Write Job Application

Turn one vacancy into the strongest truthful application text Flo can review quickly. Invocation means Flo has decided to apply. Do not reopen that decision.

## Required Companion Skills

- Use `onboard-job-application` when the matching candidate record is missing, stale, or lacks a verified application audit.
- Use `obsidian-cli` for vault retrieval and approved candidate-note writes.
- Use `obsidian-markdown` when saving approved text into the candidate note.
- Use `browser:control-in-app-browser` for official public role, company, and application research.
- Use `chrome:control-chrome` when a logged-in browser may expose otherwise gated application requirements.
- Offer `render-cover-letter` only after the body is approved and the application needs a PDF upload.
- Mention the repo-local `apply-to-job` workflow only when Flo wants material CV suggestions implemented as a tailored CV package.

Follow each companion skill's safety and surface-selection rules.

## Fixed Boundaries

- Inspect application pages only. Never submit, create an account, sign in, type personal data, upload a file, or save an external draft.
- Treat the advert and company research as evidence about the employer, role, and application format. They are never evidence that Flo has done something.
- Respect every claim boundary in the live Decision Context and deeper canonical sources.
- Never silently upgrade a pilot or internal beta to production, imply a past Staff title or formal management, claim years of production LLM ownership, or inflate ML-lifecycle, Kubernetes, Terraform, GPU-serving, or adjacent experience.
- Draft in chat first. Do not write application prose to Obsidian until Flo explicitly approves the wording or asks to save it.
- Never modify the CV, create a CV workspace, render a PDF, or invoke another production workflow automatically.
- Never change shortlist, status, fit scores, dates, or the onboarding managed block while saving approved prose.

## Workflow

1. Read `references/workflow.md` completely.
2. Accept one vacancy URL, pasted advert, application page, or candidate-note reference. Infer company, role, and channel when the evidence makes them clear; do not start with an intake questionnaire.
3. Find and reuse the matching candidate note. When it is missing, stale, or application requirements are unverified, run the existing onboarding workflow first, then continue from the resulting record.
4. Read the live Decision Context and the current CV selected by `CURRENT_GOLDEN_MASTER`.
5. Inspect the official application flow and perform bounded official company research on every run.
6. Identify the three most important hiring needs, map them to the proof pillars, and retrieve only the strongest evidence needed for this role.
7. Draft the exact substantive free-text fields the form requests. Do not create redundant prose merely because an optional field exists.
8. Audit every material claim against the loaded sources and inspect whether zero, one, or two CV changes would materially strengthen the application.
9. Return the compact chat result defined in `references/workflow.md`.
10. Revise in chat. After explicit approval, save the exact approved prose into the candidate note without altering the onboarding block or other user-authored content.

## Writing Contract

- Default to 120-250 words for a cover letter or general application note. Exact form limits override the default.
- Select the two or three strongest reasons Flo's actual experience maps unusually well to this role.
- Do not retell the CV, pad weak evidence, manufacture emotional attachment, mirror marketing copy, or use generic enthusiasm.
- Sound like an experienced engineer speaking to another professional: concise, specific, technically literate, confident, and natural.
- Do not use em dashes or ceremonial openings such as `I am thrilled to apply`.
- Use the established gap pattern only when it helps: nearest real evidence, how Flo reasons at the boundary, and the honest limit. Do not defensively volunteer gaps in the application text.
- Do not place citations, evidence labels, or claim-audit commentary inside the ready-to-paste prose.

## Approval and Handoffs

- Clear approval of the wording authorizes saving that exact text to the matching candidate note.
- If the same field already contains user-authored or previously approved text, stop and ask whether to replace it or append a new version.
- Save only the approved application prose. Keep evidence, claim checks, and CV advice in chat.
- When a PDF upload is required or useful, offer `$render-cover-letter` after saving. Do not invoke it without Flo's request.
- When a CV change is material, describe it precisely and offer `$apply-to-job`; otherwise say `No change recommended.`
