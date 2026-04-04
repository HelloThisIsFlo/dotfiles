# Flo's Documentation Style Reference

> This document captures Flo's markdown documentation style as observed and refined through iterative editing sessions. It is intended to be consumed by an agent that will create a reusable skill/template for producing documents in this style. The agent reading this has NO access to the original conversation — everything needed must be here.

---

## 1. Core Philosophy

- **Scanability above all else.** If someone looks at a doc and thinks "I don't want to read this," it's too verbose.
- **Outline density.** The document should read like a tight outline that happens to be the final document — not like a Wikipedia article or a blog post.
- **Lead with decisions and results**, not the story of how we got there.
- **Bullet points over prose.** This applies everywhere: body text, callouts, explanations. Prose paragraphs are acceptable only for brief introductions or one-liner context setters (1-2 sentences max before switching to structured content).
- **Hierarchical bullets are encouraged** when sub-points are needed — don't flatten everything into a single level.

---

## 2. Obsidian-Style Callouts

Flo uses GitHub/Obsidian-compatible callouts (`> [!type]`) extensively. They are a primary structural element, not decoration.

### 2.1 Callout Types and When to Use Them

| Type | Purpose | Example title |
|------|---------|---------------|
| `[!important]` | Core rules, key takeaways, the "one thing to remember" | "The rule" |
| `[!warning]` | Gotchas, surprising behavior, things that can go wrong | "What happens when X?" |
| `[!tip]` | Invitations to go deeper, links to detailed guides | "Check out the X deep dive" |
| `[!note]` | Supplementary context, clarifications, side notes | "What about X?" |

### 2.2 Content Inside Callouts: ALWAYS Bullets

This is a hard rule. **Never write prose paragraphs inside callouts.** Bullets are far easier to scan.

Acceptable structures inside a callout:

**Pattern A — Pure bullets (for rules/mappings):**
```markdown
> [!important] The rule
>
> - **Due dates** → deadlines
> - **Defer dates** → constraints
> - **Planned dates** → intentions
> - Unsure which to use? It's probably a planned date.
```

**Pattern B — Lead-in sentence + bullets (for explanations):**
```markdown
> [!important] The rule
> Choose the date that the recurrence is "about":
>
> - Due every Friday → anchor on `due_date`
> - Becomes available every Monday → anchor on `defer_date`
> - Plan it for the same day each week → anchor on `planned_date`
```

**Pattern C — Structured warning (for gotchas with action items):**
```markdown
> [!warning] What happens when the anchor date field is not set?
>
> OmniFocus creates the missing anchor date from scratch on the next occurrence
>
> - Uses the **completion date** (not the creation date) for the date portion
> - Uses the user's **default time** for that date type (Settings → Dates & Times) for the time portion
>
> Valid but potentially surprising => **Set the anchor date explicitly for predictable behavior**
>
> _See [reference-doc.md](path), Part 7 for the full empirical verification_
```

Structure of Pattern C:
1. **Opening statement** (not bulleted) — what happens, in one line
2. **Detail bullets** — the specifics
3. **Conclusion / action item** — bolded, tells the reader what to do
4. **Reference link** — italic, understated, at the bottom

**Pattern D — Invitation to another document:**
```markdown
> [!tip] Check out the BYDAY deep dive
>
> The [BYDAY Edge Cases](byday-edge-cases.md) guide walks through each scenario with:
>
> - Diagrams
> - Concrete examples
> - A mode selection cheatsheet
```

Structure: link + what the reader will find there, as bullets. No fluff, no "you should definitely..." — just the content.

### 2.3 Callout Formatting Details

- Always leave a blank `>` line between the title and the content (i.e., `> [!type] Title` then `>` then content)
- Blank `>` lines between logical groups within the callout (e.g., between bullets and a conclusion)
- The title should be a short hook, not a full sentence
  - Good: "The rule", "What happens when X?", "Check out the BYDAY deep dive"
  - Bad: "Important information about how the anchor date field behaves when not set"

---

## 3. Emoji Usage

Emoji are used **deliberately and consistently**, never decoratively. They serve as visual shorthand.

### 3.1 Semantic Emoji Identity

When a concept has multiple variants/modes, assign each one a consistent emoji that carries across the entire document (and across related documents):

```
✅ regularly_with_catch_up  (recommended / correct / expected)
🔄 regularly                (neutral / mechanical)
⚠️ from_completion          (caution / proceed carefully)
```

These emojis appear in:
- Mode tables
- "Choosing a mode" bullet lists
- Inline references

### 3.2 Expressive Emoji for Edge Cases / Scenarios

Edge cases and gotchas get expressive, emotional emoji that make the severity instantly clear:

```
⚡ Same-day eligibility     (surprising gap)
🤯 Grid reset               (mind-blowing divergence)
😤 Early completion dismissal (frustrating outcome)
🫠 General "this is weird"   (casual, in intros)
```

### 3.3 Structural Emoji (within explanations)

```
✅ Expected/correct result
❌ Surprising/wrong/counterintuitive result
🔑 Key takeaway
🤔 "This might seem surprising, but..."
```

### 3.4 Emoji Placement

- **In tables:** At the start of the first column (e.g., `| ✅ **Catch Up** | ...`)
- **In bullet lists:** At the start of the line (e.g., `- ⚡ **Same-day eligibility** — ...`)
- **In section headings:** After the "Why" label (e.g., `### Why — ⚡ 5 day gap`)
- **In prose:** Sparingly, usually at end of an intro sentence (e.g., "...behaves counterintuitively. 🫠")

---

## 4. Document Structure

### 4.1 Section Pattern

A typical section follows this flow:

1. **Brief intro** — 1-2 sentences of context, no more
2. **Concrete examples** — using `**Example:**` / `**Not a X:**` prefixes
3. **Summary table** — for comparisons or multi-variant overviews
4. **Callout with the key rule** — `[!important]` with the takeaway

Not every section needs all four. Small sections might just be intro + callout.

### 4.2 Reference Links — Two Tiers of Emphasis

When linking to other documents, Flo uses two distinct visual tiers to signal "definitely read this" vs. "available if you need it":

**Tier 1 — Primary reference (read this!):**
Use a `[!tip]` callout. This pops visually and says "you should go here."

```markdown
> [!tip] Check out the BYDAY deep dive
>
> The [BYDAY Edge Cases](byday-edge-cases.md) guide walks through each scenario with:
>
> - Diagrams
> - Concrete examples
> - A mode selection cheatsheet
```

**Tier 2 — Secondary reference (if you need it):**
Italic text below a horizontal rule. Quiet, out of the way.

```markdown
---

_For raw empirical data and experiment methodology, see [omnifocus-repetition-behavior.md](path)._
```

The visual contrast between the two is the point — the callout draws the eye, the italic footnote doesn't.

### 4.3 Document Layering

When a topic has multiple documents at different depths:

- **Concepts doc** — high-level "what to know", brief, scannable. Links down to the guide.
- **Practical guide** — edge cases, scenarios, diagrams. The "where things get surprising" doc. Links down to raw data.
- **Raw reference** — empirical data, experiment methodology. Stays in a research directory, not in docs.

Each layer summarizes just enough to be useful on its own, then points to the next layer for readers who want more.

---

## 5. Formatting Conventions

### 5.1 Inline Formatting

| Element | Format | Example |
|---------|--------|---------|
| API values, enum names, field names | `` `code` `` | `due_date`, `from_completion` |
| Key terms, concepts | `**bold**` | **completion date**, **anchor date** |
| Mappings / transformations | `→` arrow | `due_date` → deadlines |
| Inline explanations | em dash `—` | `from_completion` skips today entirely — no matter how many hours remain |
| Implications / conclusions | `=>` | Valid but potentially surprising => **Set the anchor date explicitly** |
| De-emphasized references | `_italic_` | _See [doc.md](path) for details_ |
| Parenthetical contrasts | `(not X)` | Uses the **completion date** (not the creation date) |

### 5.2 Tables

- Use tables for comparisons, mode overviews, and summaries
- Emoji at the start of rows when modes have emoji identities
- Keep tables compact — one line per row, no multi-line cells
- Tables summarize; bullets/callouts explain

### 5.3 Horizontal Rules

Used sparingly, for:
- Separating importance tiers (main content from footnote-style references)
- Separating major scenarios in a guide

NOT used between every section — that's what headings are for.

---

## 6. Guide / Edge Case Document Style

For practical guides that walk through scenarios (like the BYDAY edge cases doc), each scenario follows a rigid structure:

```markdown
## Scenario N: [Name]

![](images/diagram.png)

### Setup

- Task: repeat [pattern], due **[date]** (context)
- Completed: **[date]** (context)

### Results

| Mode | Next due |
|------|----------|
| ✅ **Catch Up** | **[date]** |
| ❌ **From Completion** | **[date]** |

### Why — [emoji] [gap description]

- **Catch Up** checks at the **[level]**
  - *"Inner monologue quote showing the logic"*
  - ✅ [outcome]
- **From Completion** checks at the **[level]**
  - *"Inner monologue quote showing the logic"*
  - ❌ [outcome]
- 🔑 [Key takeaway]
```

Key features of this pattern:
- **Setup** is always bullet points with bold dates
- **Results** is always a table with ✅/❌ emoji
- **Why** heading includes the emoji and the gap description (e.g., "⚡ 5 day gap")
- **Inner monologue quotes** in italic — showing what the algorithm "thinks"
- Hierarchical bullets: mode → logic → outcome
- Ends with a summary section ("When to use which mode") using the same emoji from the mode table

---

## 7. Tone

- **Technical but not dry.** Personality shows through emoji and phrasing.
- **Not afraid of casual/emotional markers** — 😤 "effort dismissed", 🫠 "this is weird", 🤯 for dramatic divergence. These make the doc more human and the gotchas more memorable.
- **Direct.** No hedging ("it might be worth considering..."), no filler ("it's important to note that..."). Just say the thing.
- **Conversational confidence.** Reads like a senior engineer explaining to a peer, not a textbook.

---

## 8. Anti-Patterns (What NOT to Do)

- **No prose paragraphs inside callouts.** Bullets only.
- **No wall-of-text explanations.** If it's longer than 2-3 sentences, restructure as bullets.
- **No decorative emoji.** Every emoji earns its place through consistent semantic meaning.
- **No "In this section, we will discuss..."** preamble. Just start.
- **No trailing summaries** ("In conclusion, we have seen that..."). The structure IS the summary.
- **No redundant emphasis.** Don't bold AND callout AND emoji the same point. Pick the right tool.
- **Don't flatten hierarchy.** If sub-points exist, use nested bullets — don't cram everything into one level.
- **Don't over-link.** Two tiers of references max. Don't sprinkle "see also" links throughout the text.

---

## 9. Complete Example

Here's a full section written in Flo's style, combining multiple patterns:

```markdown
## Widget Configuration

Widgets accept three configuration modes. They look similar but behave very differently when the user overrides defaults.

| Mode | Behavior |
|------|----------|
| ✅ `managed` | Widget respects global theme; overrides merge cleanly |
| 🔄 `standalone` | Widget ignores global theme; fully self-contained |
| ⚠️ `hybrid` | Widget starts managed, detaches on first override |

> [!important] The rule
>
> - User-facing widgets → `managed` (recommended default)
> - Embedded third-party widgets → `standalone`
> - Unsure? → `managed`

### Override edge cases

When `hybrid` widgets receive their first override, the detachment is permanent and can produce surprising results:

- ⚡ **Theme switch after override** — the widget keeps the OLD theme. It detached on override and never re-attaches.
- 🤯 **Nested hybrid widgets** — parent detachment does NOT cascade. Children stay managed until THEY get an override.

> [!tip] Check out the widget override deep dive
>
> The [Override Edge Cases](override-edge-cases.md) guide covers:
>
> - Detachment lifecycle diagrams
> - Re-attachment workarounds
> - Migration path from hybrid to managed

---

_For the original design discussion and trade-off analysis, see [widget-design-notes.md](path)._
```
