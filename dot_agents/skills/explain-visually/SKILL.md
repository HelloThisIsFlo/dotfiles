---
name: explain-visually
description: Create or revise a temporary Mermaid-first Markdown explanation when Flo wants a visual mental model or is confused about how concepts, components, layers, or products relate. Use for visual explanation requests and focused questions about how one thing fits with another. Do not use for durable operational references, restyling an existing document, broad multi-perspective research, or Agent Sandbox notes.
---

# Explain Visually

Create a visual working model that meets Flo at his current understanding and makes the relationship causing confusion click. This is a disposable thinking artifact, not a comprehensive reference.

## Teach Through the Diagrams

Design backward from the distinction or relationship that should become obvious. Choose the narrative shape that fits the topic and Flo's apparent understanding.

- Let headings and Mermaid diagrams carry the core explanation.
- Use prose only where the diagrams cannot safely carry precision, caveats, mathematics, commands, or exact rules.
- Make every diagram advance the mental model rather than illustrate a point the prose already explained.
- Avoid presenting an unexplained final architecture as the explanation.
- Preserve continuity across diagrams by reusing actors, names, boundaries, emoji, and visual roles.
- Let later diagrams extend or refine the model instead of restarting it from scratch.
- Use no fixed sequence, diagram count, or topic template.

Read `../apply-style/references/technical-diagrams.md` before creating or revising Mermaid. It is the canonical visual grammar; do not reproduce it here.

## Keep One Working Artifact

- Always create or update one standalone Markdown file.
- Use a path supplied by the user. Otherwise create `<topic>-visual-explanation.md` in the current working folder.
- Revise that same file during follow-ups. Do not create numbered versions.
- Keep it uncommitted and disposable unless the user explicitly asks to preserve it.
- Keep chat for collaboration. Report the file path and what changed without reproducing the artifact.

Treat follow-up confusion as evidence that the model needs revision. Strengthen the relevant diagram or teaching arc instead of appending an explanatory essay.

## Check the Mental Model

Ignore the supporting prose for a moment and read only the headings and diagrams.

- The central relationship should still be reconstructable.
- Each diagram should contribute a new connection or useful refinement.
- Equivalent things should retain a stable visual identity.
- The reader should not have to decode a large unexplained structure.

If that test fails, improve the diagrams rather than compensating with more prose.

## Route Durable Work Elsewhere

- Use `flo-cheatsheet` for durable operational references, command guides, and reusable cheat sheets.
- Use `apply-style` when the content already exists and only its Markdown presentation should change.
- Use `sandbox-explain` when the explanation should be preserved in `_AgentSandbox_/` for future Flo or other agents.
- Use `explore-and-present` for broad multi-perspective research and polished comprehensive deliverables.
- Use the existing `visual-explainer` when available and the user explicitly wants its polished standalone HTML experience.
