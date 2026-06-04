---
name: apply-style
description: Rewrite markdown documents to match Flo's documentation style — scannable, outline-dense, callout-rich, emoji-semantic. Use this whenever the user says "apply my style", "style this", "make it look like mine", "format this doc in my style", or wants a markdown document reformatted to their personal conventions. Also trigger when the user references their "style guide" or "style reference" in the context of reformatting a document. Even if the user just says "now make it pretty" or "clean up the formatting" after drafting content, this is likely the right skill.
---

# Apply Flo's Documentation Style

You're restyling a markdown document to match Flo's writing conventions. The content has already been drafted for accuracy — your job is purely **form**: structure, formatting, tone, and flow.

## Before you start

1. Read the target document in full
2. Read `references/style-reference.md` — the complete style guide. Internalize it before making any changes.
3. If the user points to a specific section, restyle only that section (leave the rest untouched). Otherwise, restyle the entire document.

## What to change

Everything about *how* the content is presented:

- **Structure** — Reorganize sections if they'd flow better. Lead with decisions and results, not narrative buildup.
- **Prose to bullets** — Convert paragraphs into bullet points. Prose is only acceptable for 1-2 sentence intros before switching to structured content.
- **Callouts** — Identify key rules (`[!important]`), gotchas (`[!warning]`), cross-references (`[!tip]`), and side notes (`[!note]`). Content inside callouts is ALWAYS bullets — never prose paragraphs.
- **Emoji** — Assign semantic emoji to modes/variants and use them consistently throughout. Use expressive emoji for edge cases/gotchas (severity should be instantly clear). Never decorative.
- **Tone** — Direct, conversational, confident. No hedging, no filler, no trailing summaries.
- **Inline formatting** — `code` for API values/field names/enum names, **bold** for key terms/concepts, `→` for mappings, `—` for inline explanations, `=>` for implications/conclusions.
- **Hierarchy** — Use nested bullets when sub-points exist. Don't flatten everything to one level.
- **Reference links** — Two tiers only: `[!tip]` callouts for "definitely read this", italic footnotes below a `---` for "available if you need it".

## What NOT to change

- **Meaning** — Every fact, finding, and conclusion must survive the restyle
- **Technical accuracy** — Don't reword in ways that shift technical meaning
- **Scope** — Don't add new content, remove findings, or editorialize beyond what the source says

## Be bold

The user stages their file before applying this skill, so they get a clean diff. Don't hold back — if a section needs restructuring, restructure it. If headings need renaming, rename them. If the order should change to lead with results instead of narrative, change it. The user expects a thorough transformation, not cosmetic tweaks.

## Common transformations

| Before | After |
|--------|-------|
| Multi-sentence explanation paragraph | 1-line intro + bullet list |
| Inline "note: ..." or "important: ..." | `> [!note]` or `> [!important]` callout |
| Repeated mode/variant references | Assign emoji identity, use consistently |
| "In this section we will discuss..." | Delete — just start |
| "In conclusion, we have seen that..." | Delete — the structure IS the summary |
| Flat bullet list with mixed concerns | Hierarchical bullets grouped by concern |
| Prose inside a callout | Bullets inside a callout (always) |
| Wall of text explaining an edge case | Pattern C callout: statement → detail bullets → bold action item |
| Scattered "see also" links | Two-tier references: tip callout OR italic footnote |

## Section rhythm

A well-styled section typically follows this flow (not every section needs all four):

1. **Brief intro** — 1-2 sentences of context, no more
2. **Concrete examples** — `**Example:**` / `**Not a X:**` prefixes
3. **Summary table** — for comparisons or multi-variant overviews
4. **Callout with the key rule** — `[!important]` with the takeaway

## After restyling

Write the restyled document back to the same file. Don't create a new file or add a suffix — the user is relying on `git diff` to review your changes.
