---
name: sandbox-explain
description: Create or update explanatory Obsidian notes in Flo's agent sandbox. Use when the user asks to create a sandbox file, agent handbook note, explanation note, visual explainer, or communication artifact in the agent sandbox; when they mention the Agent Sandbox, sandbox folder, INDEX.md, or helping agents understand a project/concept.
---

# Sandbox Explain

Create clear explanatory notes in Flo's Obsidian agent sandbox.

## Fixed Target

- Use Obsidian vault `TheVault`.
- Use sandbox root `_AgentSandbox_/`.
- Do not use other vaults for this workflow.
- Create shared personal skill outputs under the vault, not inside a project repo.

## Required Companion Skills

- Use `obsidian-cli` for vault lookup, reads, and writes when Obsidian interaction is needed.
- Use `obsidian-markdown` for Obsidian-valid Markdown, frontmatter, wikilinks, callouts, embeds, and Mermaid.
- Use `apply-style` for Flo's documentation style.
- Do not duplicate Flo's full style rules in this skill; defer to `apply-style` and the base agent instructions.

## Workflow

1. Identify the topic or project the note should explain.
2. Inspect `_AgentSandbox_/` first-level folders.
3. Choose the folder:
   - Reuse an existing emoji-prefixed folder when it clearly matches the topic.
   - Create a new emoji-prefixed folder only when no good candidate exists.
   - Use a semantic emoji that helps scanning.
4. Ensure the folder has `INDEX.md`.
   - Create it if missing.
   - Update it if the new note should be listed.
   - Keep it short: purpose, key notes, and current status.
5. Create one focused explanation note unless the user asks for more.
6. Apply Flo's style through `apply-style`.
7. Verify Obsidian can read the created or updated note.

## Default Output Shape

Use this default unless the user asks otherwise:

- Folder:
  - `_AgentSandbox_/{emoji} {Topic}/`
- Index:
  - `_AgentSandbox_/{emoji} {Topic}/INDEX.md`
- Topic note:
  - `_AgentSandbox_/{emoji} {Topic}/{short-title}.md`

## INDEX.md Contents

Keep `INDEX.md` as a lightweight entrypoint:

- What this folder is for
- Important notes in the folder
- Current status or next useful read
- Links using Obsidian wikilinks

Do not turn `INDEX.md` into the full explanation unless the user explicitly wants a single-file folder.

## Explanation Note Guidance

Default to a note that helps another agent or future Flo understand the work quickly:

- Start with the result or mental model.
- Include a Mermaid diagram when it materially improves understanding.
- Use concrete examples from the current project or artifact.
- Clearly separate:
  - what exists now
  - how it works
  - what is not built yet
  - what to check next
- Use code fences only for real code, commands, config, or data shapes.

## Folder Reuse Heuristic

Prefer reuse when:

- Folder name contains the project/topic name.
- Folder contents already cover the same system or investigation.
- The user says "this sandbox" or "the existing folder".

Create a new folder when:

- Existing folders are unrelated.
- Reuse would mix unrelated projects.
- The user asks for a new sandbox area.

## Safety

- Do not delete or rename existing sandbox notes unless explicitly asked.
- Do not move notes between folders without asking.
- Do not create Codex-local skill adapters under `~/.codex/skills`.
- If creating or updating this skill itself, use `/Users/flo/.agents/skills`.
