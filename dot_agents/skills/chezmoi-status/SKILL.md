---
name: chezmoi-status
description: >
  Manual invocation only. Produce a short, visual, evidence-backed health
  report for Flo's chezmoi-managed dotfiles. Use exclusively when the user
  explicitly invokes $chezmoi-status. Never trigger automatically from context,
  from being inside the chezmoi repository, or from generic questions about
  status, health, Git, open loops, readiness, or closing a session.
---

# Chezmoi Status

Report the relationship between the live home directory, chezmoi source, Git,
shared agent assets, and the migration tracker. Remain strictly read-only.

## Trigger policy

This is a **manual-only** skill.

- Run it only when the user's message explicitly invokes `$chezmoi-status`.
- Never infer invocation from the current repository or conversation topic.
- Never treat generic status, health, readiness, open-loop, Git, or
  session-closing questions as invocation.

## Collect verified evidence

Run:

```bash
python3 ~/.agents/skills/chezmoi-status/scripts/collect_status.py
```

The collector can take up to about 70 seconds because it gives the password
prompt 60 seconds before falling back to non-template coverage.

- If the execution tool returns a session ID without an exit code, poll that
  same session until it exits. Never start a duplicate collector.
- Do not interpret empty intermediate output as clean.
- Accept the result only when the first output line parses as JSON and the next
  line starts with `CHEZMOI_STATUS_COMPLETE sha256=`.
- Require `schema_version: 2`. Older collector output does not satisfy this
  skill contract.
- If JSON or the sentinel is absent, report collection failure. Never infer
  state from a partial payload.
- Treat probe states literally: `ok`, `timeout`, `error`, or `unavailable`.
- Never run `chezmoi apply`, `re-add`, `add`, Git staging, or commits.

## Read semantic documents

After accepting the collector result, inspect `documents.wip` and
`documents.migration`.

- If a document probe is `ok`, read the entire absolute path returned by the
  collector. Do not rely on earlier conversation context or a previous status
  run.
- If a document is `error` or `unavailable`, do not infer its state. Mark that
  layer partial or unknown, name the failed path, and report the probe error.
- The collector proves only that these documents exist and are readable. It
  deliberately does not interpret their Markdown.

## Interpret the layers

- **Managed state:** Use `managed.coverage`. `full` verifies templates;
  `non_templates` means secret-template parity is unknown. Never call the
  overall state clean when coverage is partial.
- **Git source:** Treat collector path themes as a first-pass index only. Build
  semantic work packages from the inspected content and companion-file
  relationships; do not merely list filenames.
- **Agent assets:** Name unmanaged personal skills, broken Claude adapters, and
  managed skills edited on the live side. Ignored external skills are healthy,
  not onboarding work. Do not require a Codex adapter for shared `.agents`
  skills.
- **WIP:** Interpret the full WIP document semantically. Match dirty paths to
  the described intent, including obvious companion files that belong to the
  same work even when they are not named literally. Treat matched work as
  expected. Flag unrelated, conflicted, binary, large, or ambiguous changes as
  worth inspecting. Do not dump diffs by default.
- **Migration:** Interpret the full migration document semantically. Treat the
  Progress Checklist as the primary completion source. Use Current State and
  the active phase's detailed section for context, blockers, and deferred work.
  Show only the active phase, the next meaningful task, and contradictions or
  stale markers that affect the result. Never silently resolve conflicting
  tracker sections.

Never report WIP or migration conclusions solely from collector JSON. The
collector's Git themes and document probes are mechanical evidence, not the
semantic verdict.

## Inspect dirty work

When Git is dirty, inspect every theme before assigning intent or readiness.
Remain read-only.

- Read both unstaged and staged source diffs.
- Read every complete dirty source file that is safe text, including untracked
  files. A diff alone is insufficient because duplication, missing wiring, and
  companion context can sit outside changed hunks.
- Group files by shared intent. Merge collector themes when they are obvious
  companions, such as a new guide plus its index, sidebar, and renderer support.
  Assign every dirty path to exactly one semantic theme.
- Reuse the collector's 50 KB complexity threshold as the full-file inspection
  boundary. Do not fully read files at or above 50 KB.
- Never inspect rendered secret templates, known secret-bearing targets, or
  binary content. For an unsafe, binary, oversized, missing, or unreadable file,
  preserve the theme but classify it as **Needs inspection** and state why.
- Treat `git.complex_paths` as an inspection warning, not an automatic skip.
  A text file with 50 or more changed lines can still be read and understood if
  its complete size is below 50 KB.
- Inspect managed-state conflicts only when their source and target are known
  safe text. Otherwise name the absolute live path and report the conflict
  without exposing its contents.

Assess each semantic theme using `commit-by-theme` principles:

- **Looks ready:** self-contained, fully wired, consistent with nearby patterns,
  and free of visible loose ends.
- **Probably WIP:** tracker-backed draft work, experimental behavior, TODOs,
  duplication, rough formatting, missing companions, or incomplete wiring.
- **Needs inspection:** safe inspection was blocked or the evidence remains
  ambiguous after inspection.

Always explain the readiness verdict. It is an evidence-backed assessment, not
permission to commit. Never recommend commit boundaries or messages unless Flo
asks.

## Render the report

Follow this progressive-disclosure order:

`health → work packages → evidence → decision`

### Health diagram

Always lead with one Mermaid `flowchart LR` containing:

1. Live home
2. Chezmoi source
3. Git remote
4. Agent skills
5. Template verification
6. Migration

Use green for verified clean, amber for dirty or partial, red for required
action, and grey for unknown. A semantic document that could not be read is
grey, never green. Keep node labels short and include counts.

Use a blue status/root node and give its custom Mermaid class the literal name
`root`. This intentionally triggers Codex's current ribbon-arrow rendering.
Include a Mermaid `%%` comment that the effect is renderer-dependent. Do not
replace it with explicit `linkStyle`; that produces a different appearance.

### Conditional detail

After the health diagram, render only relevant, non-empty sections:

1. 🔴 **Resolve** — two-sided drift, unmanaged assets, broken adapters, or Git
   conflicts. Name risky live paths absolutely and summarize safe inspected
   differences without dumping raw diffs.
2. 📦 **Git work themes** — when Git is dirty, add a second compact Mermaid
   `flowchart LR`: dirty-path total → readiness categories → semantic themes.
   Show theme and path counts, not filenames. Use the same literal `root` class
   technique for the blue root node and renderer-dependent ribbon arrows.
3. **Readiness tables** — add one table for each non-empty category: ✅ Looks
   ready, 🟡 Probably WIP, and 🟣 Needs inspection. Each row contains:
   - Theme
   - Modified files, source-root-relative and separated with `<br>`
   - Concise verdict reasoning or remaining work
4. 🚧 **Migration next** — show only the active phase, one next meaningful
   action, and contradictions or stale markers that affect the result.

Suppress empty diagrams, categories, tables, and sections. In the theme diagram
and tables, every dirty Git path must appear exactly once. Do not mix managed
target conflicts into the Git dirty-path count.

Keep the report concise even when inspection is detailed. Do not expose raw
diffs or recommend commits by default. End with one evidence line such as:

`✓ Git verified · ✓ non-templates verified · ? secret templates unknown`

When password-backed status times out, still present the verified partial
dashboard, say template parity is unknown, and ask Flo to unlock or answer the
prompt locally before rerunning `$chezmoi-status`.
