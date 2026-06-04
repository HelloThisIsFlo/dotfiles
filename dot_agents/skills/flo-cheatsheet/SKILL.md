---
name: flo-cheatsheet
description: Create cheat sheets that match Flo's preferred learning style — practical, opinionated, problem-first documentation with real-world examples and honest tradeoff assessments. Use this skill whenever the user asks for a cheat sheet, reference guide, quick guide, learning document, or says things like "write me a cheat sheet on X", "create a guide for Y", "help me understand Z", "document how to use X". Also trigger when the user asks to turn a conversation or learning session into a reusable document. Always use this skill for any documentation or cheat sheet creation, even if the topic seems simple.
---

# Flo's Cheat Sheet Style

This skill produces cheat sheets tailored to how Flo learns and references technical material. The style was refined through extensive iterative feedback across nine cheat sheets covering chezmoi's full feature set.

## Core Philosophy

Flo learns by understanding **why**, not just **how**. Every section should start with the problem it solves before showing the solution. Don't just document syntax — explain the mental model. Flo prefers to understand the underlying mechanism so deeply that the syntax becomes obvious.

## Document Structure

### Title and Opening

```markdown
# [Tool/Concept] [Topic] — Cheat Sheet

[2-3 sentence hook that explains what this solves and why you'd care.
Frame it as a problem: "You want X but Y is in the way. This is how you solve it."]

---
```

The opening should make someone who's never heard of the topic understand why it exists. No preamble, no history — straight to the value proposition.

### Section Hierarchy

Use `##` for major topics and `###` for subtopics within them. Separate major sections with `---` horizontal rules. Keep the hierarchy flat — rarely go deeper than `###`. If you need `####`, the section is probably too nested and should be restructured.

### Section Flow

Each major section follows this pattern:
1. **What it is / what problem it solves** — 1-2 sentences, plain English
2. **How it works** — the mechanism, explained conversationally
3. **Practical example** — real code or config that someone would actually use
4. **Gotchas / edge cases** — in blockquotes (`>`) for visual distinction

### Ending

Every cheat sheet ends with a **Quick reference** section — a table or compact code block that serves as a lookup card. This is the "I already understand it, I just need the syntax" section. Formats that work well:

- Decision guide table: "I want to... → Use..."
- Command reference: compact code block with comments
- Comparison table: when to use which approach

## Writing Style

### Voice and Tone

- **Conversational but precise.** Write like a knowledgeable colleague explaining something at a whiteboard, not like official documentation. Use "you" freely.
- **Opinionated.** Don't present all options as equal when they're not. Say "this is the right way" and demote alternatives to footnotes or side notes. Frame inferior approaches as "fallback" or "escape hatch."
- **Honest about tradeoffs.** When something is brittle, niche, or rarely needed, say so directly. Flo respects candour over completeness. Phrases like "you'll probably never need this" or "this is genuinely rare" are good.
- **Problem-first.** Before showing a solution, make the reader feel the pain of not having it. "Apps constantly write timestamps to plists. Managing the whole file means your git history is just noise." Then the solution lands naturally.

### What to Avoid

- **Don't be comprehensive for its own sake.** Cover what matters. Skip features that are rarely used unless they solve a specific problem worth explaining.
- **Don't use contrived examples.** Every example should be something someone would actually do. If you can't think of a real use case, the feature might not be worth documenting — or mention it briefly and move on.
- **Don't hedge unnecessarily.** "This might be useful if..." is weak. "Use this when..." is strong.
- **No emojis.** No decorative formatting. Minimal bold — use it for genuine emphasis, not structure.
- **Don't repeat information.** If something is covered in another sheet, link to it with a relative link and give a one-line summary. Don't duplicate content.

### Examples Must Be Practical

This is critical. Every code example should pass the "would someone actually type this?" test.

**Bad:** A `lookPath` example checking if `rbw` exists to conditionally expose secrets (you wouldn't gate secrets on tool availability).

**Good:** A `lookPath` example checking if `bat` exists to alias `cat` (genuine progressive enhancement that degrades gracefully).

**Bad:** Generic placeholder like `some-config-value` or `example-app`.

**Good:** Real tools the reader uses: `delta` for git diffs, `bat` for cat replacement, `nvim` as editor, actual email addresses and hostnames.

When personalising examples, use Flo's actual context: `flo@kempenich.ai`, `Flo Kempenich` (never "Florian"), machine types like "personal", "work", "server", macOS + Linux as target platforms.

### Prioritise the Right Approach

When multiple approaches exist, structure them with the best one first:

1. **Primary approach** — full explanation, examples, the works
2. **Fallback/alternative** — brief mention, framed as "for quick testing" or "escape hatch"
3. **Anti-pattern** — if relevant, explain what NOT to do and why

Don't present options as equal with "Option 1" / "Option 2" unless they genuinely serve different use cases. If one is better, lead with it.

### Gotchas in Blockquotes

Use `>` blockquotes for:
- Warnings and gotchas
- "About [subtle point]:" explanatory asides
- Edge cases that are important but shouldn't interrupt the main flow

Format: `> **Bold label.** Explanation text.`

### Tables for Comparisons

Use tables when comparing options, listing commands, or providing quick reference. Tables should be scannable — short cell contents, no paragraphs inside cells.

```markdown
| I want to... | Use |
|---|---|
| Do X | `command-for-x` |
| Do Y | `command-for-y` |
```

### Cross-References

When multiple cheat sheets exist on related topics, use relative Markdown links:

```markdown
See the [Templates cheat sheet](chezmoi-templates-cheatsheet.md) for full syntax details.
```

Don't duplicate content across sheets. A brief summary + link is always better than repetition.

## File Naming

Name cheat sheet files as: `[tool]-[topic]-cheatsheet.md`

Examples:
- `chezmoi-templates-cheatsheet.md`
- `chezmoi-run-scripts-cheatsheet.md`
- `fastmail-jmap-cheatsheet.md`

## Length Guidelines

- A typical cheat sheet is 200-400 lines of Markdown
- Each major section is 20-60 lines
- Code examples are 5-20 lines (enough to be useful, short enough to scan)
- The quick reference at the end is a compact lookup — not a repeat of the whole sheet

## Checklist Before Delivering

Before presenting a cheat sheet, verify:

- [ ] Opens with the problem it solves, not the feature it describes
- [ ] Every example is something someone would actually do
- [ ] The primary/recommended approach comes first, alternatives are demoted
- [ ] No unnecessary repetition of content covered in other sheets
- [ ] Gotchas and edge cases are in blockquotes
- [ ] Ends with a quick reference table or compact lookup
- [ ] Cross-references use relative Markdown links
- [ ] No emojis, no decorative formatting, minimal bold
- [ ] Honest about when features are niche, brittle, or rarely needed
- [ ] Uses Flo's actual context in examples (email, name, machine types)
