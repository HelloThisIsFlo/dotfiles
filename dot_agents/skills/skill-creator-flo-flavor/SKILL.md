---
name: skill-creator-flo-flavor
description: Flo's creative direction for skills and agent guidance. Use whenever `skill-creator` is used, and whenever creating or substantially refining skills, global or repository AGENTS.md instructions, or nested agent guidance. Use automatically to shape the user experience, turn workflow feedback into durable guidance without overfitting, or decide whether guidance belongs in a skill, an instruction file, or a Capability Map row.
---

# Skill Creator · Flo's Flavor

Flo's creative-direction layer on top of the official `skill-creator`, for skills and other durable agent guidance. Route the guidance first, then apply the relevant mode.

## Choose the narrowest durable home

- Default to a dedicated skill for workflow-, domain-, or tool-specific behaviour.
- Use a nested `AGENTS.md` for stable behaviour limited to one subtree.
- Use the repository-root `AGENTS.md` for stable behaviour spanning that repository.
- Suggest the global `AGENTS.md` only for a rare preference that clearly applies across unrelated projects and ordinary agent work.
- Use a Capability Map row in the global `AGENTS.md` when the guidance is which tool each runtime uses for a capability.
- Never move guidance between layers silently. Discuss the change when its destination or blast radius is consequentially uncertain.

## When designing a skill

- Read and follow the official `skill-creator` first. Leave generic structure, resource selection, and validation mechanics to it.
- Understand how someone will invoke the skill, what the first response should accomplish, what the agent must learn, which answers can be remembered, what the user must do, where the workflow may pause, and what completion looks like.
- During creation, clarify enough intent to design the right experience. In the finished skill, discover before asking and ask only unresolved consequential questions.
- Front-load required user actions, irreversible operations, and expected pauses before a long-running workflow begins.
- Keep independent safe work moving. Never let a workflow wait silently on an undisclosed user action halfway through.
- Do not introduce fixed templates, mandatory subagents, or worktree management unless the task genuinely requires them or Flo explicitly requests them.
- Name capabilities from the Capability Map, never one runtime's tools, so the skill runs in Claude Code and Codex alike.
- Finish by invoking the `make-skill-portable` skill on the result. It places the skill under chezmoi, adds the runtime adapters, and checks the wording.

## When designing AGENTS.md guidance

- Do not load the official `skill-creator` solely for an `AGENTS.md` update.
- Read the applicable instruction hierarchy before proposing or changing guidance.
- Identify the reusable behavioural decision behind the motivating example, then check for existing, overlapping, or conflicting instructions.
- Ask when scope or behavioural impact remains consequentially ambiguous.
- Write the smallest directional rule that changes future decisions. Place it beside the closest existing guidance.
- Avoid incident transcripts, narrow procedures, duplication, and constraints on unrelated work.
- Reuse existing global mechanics instead of copying them into another instruction layer: chezmoi handling and the Capability Map live in the global `AGENTS.md`; skill placement and portability live in `make-skill-portable`.
- Check realistic triggering and non-triggering requests before finishing.

## Iterate from evidence

- When Flo asks to discuss feedback before acting, do not edit yet.
- Use real outputs, traces, and observed friction to understand the underlying decision failure.
- Distinguish reusable workflow flaws from project-specific symptoms and cosmetic preferences.
- Make the smallest general change that fixes the decision, not a transcription of one bad output.
- Add only guidance that changes decisions or the user experience.

## Review through the user's eyes

Confirm that the resulting guidance makes these clear where relevant:

- the next action
- questions that still need answers versus answers already known
- actions and pauses requiring the user
- progress during long-running work
- verified completion versus a remaining manual check

A mechanically correct workflow that is unpleasant or confusing to use still needs revision.
