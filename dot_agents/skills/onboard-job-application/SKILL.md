---
name: onboard-job-application
description: Onboard a job application from a role URL, pasted advert, or open browser page into Flo's Obsidian application dashboard. Use when Flo asks to evaluate, rank, inspect, triage, or add a job opportunity or application as a dashboard candidate; reconstruct current goals and evidence from the vault and current CV, inspect the application form without submitting, then create or safely update the candidate record. Do not use for a Welcome to the Jungle recommendation review whose requested output is only the daily journal; use review-wttj-recommendations instead.
---

# Onboard Job Application

Turn a job opportunity into a source-backed decision record in Flo's live Obsidian application dashboard.

The vault is the source of truth. This skill defines how to discover and apply the current truth; it must never hard-code Flo's experience, target roles, preferences, constraints, current CV filename, or ranking.

## Required Companion Skills

- Use `obsidian-cli` for vault lookup, reads, writes, and verification.
- Use `obsidian-markdown` for Obsidian-valid candidate notes.
- Use `obsidian-bases` to inspect the live schema and verify the resulting Base view.
- Use `browser:control-in-app-browser` for public role and application inspection.
- Use `chrome:control-chrome` when an existing logged-in Chrome session may expose otherwise gated information.
- Follow those browser skills' surface-selection and setup rules exactly.

## Fixed Safety Boundaries

- Inspect application pages only.
- Never submit an application.
- Never create an account.
- Never send a form, upload a CV, type personal data, or change external state.
- Never treat the job advert as evidence that Flo has a skill or experience.
- Never edit historical fit-ranking reports.
- Never invoke the repo-specific `apply-to-job` CV-tailoring skill automatically.
- Never add `created` or `modified` frontmatter; Obsidian owns those properties.

## Workflow

1. Read `references/workflow.md` completely.
2. Accept any one of:
   - a job or application URL
   - a pasted job advert
   - an explicitly identified open browser page
3. Reconstruct Flo's current decision context from the vault and current CV sources.
4. Inspect the role and application flow.
5. Score Candidate Fit and Goal Fit, then rank the role against the live queue.
6. Read the live candidate template, triage guide, and Base before writing.
7. Create a new candidate record or safely update the matching one.
8. Open the Base and verify the record, derived lane, and relevant views.
9. Report the verdict, record path, ranking position, application requirements, and any blocked information.

## Autonomy

- Write automatically when the evidence is sufficient.
- Ask only when a consequential ambiguity would materially change the record, score, ranking, or duplicate choice.
- Apply obvious states only:
  - clearly poor opportunity → `Skip`
  - demonstrably prepared application → `Ready to Apply`
  - otherwise leave `triage_status` blank
- A CV-only application does not need `Ready to Apply`; the Base routes the Quick lane into Apply Next automatically.

## Existing CV-Tailoring Skill

Keep application onboarding separate from CV production.

- If a role deserves tailored CV work, mention `$apply-to-job` as an optional next step.
- Do not create CV application workspaces, render PDFs, or tailor claims in this skill.

## Final Response

Keep it short and decision-first:

- verdict and both fit scores
- relative priority and nearby roles
- application lane and required work
- candidate-note link
- exact blocker and user action when gated
- optional `$apply-to-job` handoff only when useful
