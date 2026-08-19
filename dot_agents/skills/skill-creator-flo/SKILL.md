---
name: skill-creator-flo
description: Companion to the official skill-creator that applies Flo's preferences when creating or substantially refining skills. Use automatically alongside skill-creator for Flo's shared or repository skills, especially when shaping the user experience, resolving creation-time uncertainty, incorporating feedback without overfitting, and front-loading user actions or expected pauses.
---

# Skill Creator Flo

Read and follow the official `skill-creator` first. Use it for generic skill design and mechanics. This companion adds only Flo-specific workflow and user-experience preferences.

## Design from the user's experience

- Before writing or substantially revising a skill, understand how someone will invoke it, what the first response should accomplish, what the agent must learn, which answers can be remembered, what the user must do, where the workflow may pause, and what completion looks like.
- Ask when uncertainty would materially change usability, safety, scope, or the interaction model. Do not optimize only the agent instructions while leaving the human-facing flow confusing.
- Treat a skill as successful when its user can easily tell what happens next, what is expected from them, and whether the workflow is running, waiting, blocked, or complete.

## Preserve agency without creating friction

- During creation, clarify enough intent to design the right experience.
- In the finished skill, discover before asking and ask only unresolved consequential questions. Never repeat answers already stored in a durable source.
- Front-load required user actions, irreversible operations, and expected pauses before a long-running workflow begins.
- Keep independent safe work moving. Never let a workflow wait silently on an undisclosed user action halfway through.
- When a pause is unavoidable, make its timing, reason, and exact user action obvious in advance.

## Iterate from evidence

- When Flo asks to discuss feedback before acting, do not edit yet.
- Use real outputs, traces, and observed friction to understand the underlying decision failure.
- Distinguish reusable workflow flaws from project-specific symptoms and cosmetic preferences.
- Make the smallest general change that fixes the decision, not a transcription of one bad output.
- Default improvements to the target skill. Suggest `AGENTS.md` only for the rare rule that clearly applies across unrelated skills and ordinary agent work; never move guidance there silently.

## Keep the addition focused

- Add only guidance that changes decisions or the user experience.
- Reuse existing global instructions and shared skills instead of copying them into the target skill.
- Leave generic skill structure, resource selection, and validation mechanics to the official `skill-creator`.
- Do not introduce fixed templates, mandatory subagents, or worktree management unless the task genuinely requires them or Flo explicitly requests them.

## Review through the user's eyes

Before finishing, confirm that the intended behavior makes these clear:

- the next action
- questions that still need answers versus answers already known
- actions and pauses requiring the user
- progress during long-running work
- verified completion versus a remaining manual check

Use the official `skill-creator` for technical validation. Use this review to catch a skill that is mechanically correct but unpleasant or confusing to use.
