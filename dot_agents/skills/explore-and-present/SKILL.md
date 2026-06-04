---
name: explore-and-present
description: >
  **Multi-Agent Exploration & Visualization Pipeline**: Spawns multiple brainstorming agents with different perspectives, synthesizes their findings into a comprehensive Markdown reference doc, then builds a stunning interactive HTML showcase. Optionally writes utility code and updates project instructions.
  - MANDATORY TRIGGERS: explore and present, deep dive, brainstorm, research and visualize, multi-perspective analysis, explore all angles, comprehensive analysis, "what can we do with", research this thoroughly
  - Also use when the user asks to analyze a dataset/codebase/system from multiple angles, wants to understand all possibilities before making a decision, or says things like "I want to really understand X", "explore everything about Y", "give me the full picture on Z"
  - Use this skill even for requests like "think about this from different angles" or "I want creative ideas about X" — any time multiple perspectives would add value and the user wants a polished deliverable, not just a chat response.
---

# Explore and Present — Multi-Agent Brainstorm Pipeline

You are running a multi-agent research pipeline. The goal is to explore a topic from multiple independent perspectives, synthesize everything into a reference document, and then build a visually stunning HTML showcase that makes the findings easy to navigate and genuinely impressive to look at.

## Why this approach works

A single agent exploring a topic tends to go deep on one angle and miss others. By spawning 3-4 agents with distinct perspectives, you get broader coverage, surprising connections, and ideas that wouldn't emerge from a single line of thinking. The synthesis step then weaves these into a coherent whole, and the HTML showcase makes it tangible and shareable.

## The Pipeline

### Phase 1: Clarify the Mission

Before spawning anything, make sure you understand:

1. **What's being researched?** — The topic, dataset, system, or question.
2. **What data sources exist?** — Are there databases, files, APIs, or codebases to ground the research in? If so, make sure every agent knows how to access them (exact file paths, query methods, schemas).
3. **Who's the audience?** — Just the user? Their team? This affects tone and depth.
4. **What decisions will this inform?** — Understanding the downstream use helps agents focus on actionable insights rather than academic observations.

If anything is ambiguous, ask the user — but don't over-interview. Two questions max, then start.

### Phase 2: Spawn Brainstorming Agents

Launch 3-4 agents **in parallel** (this is critical for speed). Each agent gets:

- A **distinct perspective** (see below for how to choose these)
- Full access to any **data sources** (database paths, file locations, API docs)
- A clear instruction to **ground findings in real data** — run actual queries, cite real numbers, show real examples
- Instructions to structure output as: use case name, why it matters, method/query, real example output, practical application

**How to choose perspectives:** Pick angles that have minimal overlap but collectively cover the full space. Good patterns:

- **By stakeholder**: User perspective, developer perspective, business perspective, security perspective
- **By time horizon**: Immediate wins, medium-term projects, long-term vision, maintenance/hygiene
- **By activity type**: Search & retrieval, analytics & insights, automation & rules, cleanup & optimization
- **By approach**: Data-driven/quantitative, workflow/process, creative/exploratory, practical/implementation

Each agent should independently explore 5-15 use cases within their perspective. Encourage them to run real queries and include real output — not hypothetical examples.

**Agent prompt template:**

    You are a [PERSPECTIVE] brainstorming agent. [CONTEXT about what's being researched].

    [DATA ACCESS INSTRUCTIONS — exact paths, schemas, query methods]

    Your job: brainstorm how [the thing] can be used from a [PERSPECTIVE] angle. Think about:
    - [Specific prompts relevant to this perspective]
    - [More prompts]

    Run actual queries/analysis to ground your ideas in real data. Show real examples.

    For each use case, provide:
    1. Name and what it does
    2. Why it's useful (be specific — who benefits and how)
    3. The method (SQL query, code pattern, API call, etc.)
    4. Real example output from actual data
    5. Practical application or next step

    Return your findings as a structured document.

### Phase 3: Synthesize into Markdown

Once all agents return, read through all their findings and write a single comprehensive Markdown document. This is THE reference doc — it should be thorough enough that someone reading it understands the full landscape of what's possible.

**Structure:**

    # [Topic] — Comprehensive Analysis

    ## Overview
    Quick summary: what was analyzed, key numbers, high-level findings.

    ## Category 1: [Theme]
    ### 1. [Use Case Name]
    **What it does** — one sentence
    **Why it matters** — who benefits, what it enables
    **Method** — the query/code/approach
    **Example** — real output
    **Application** — what to do with this

    ### 2. [Next Use Case]
    ...

    ## Category 2: [Theme]
    ...

    ## What's Next
    Future possibilities, things to explore further.

**Key principles:**

- Deduplicate across agents — if three agents found the same thing, consolidate it (but note it's significant that multiple perspectives converged here)
- Organize by theme, not by agent — the reader shouldn't know or care how many agents contributed
- Keep all the real data and examples — these are what make the doc valuable
- Be comprehensive rather than brief — this is a reference document, not a summary

### Phase 4: Build the HTML Showcase

Read the Markdown synthesis, then create a single-file HTML page that presents the findings beautifully. This page should make the user go "wow."

**Design principles:**

- **Dark theme** with vibrant accent colors (modern dashboard aesthetic)
- **Scroll animations** — elements fade/slide in as you scroll (use Intersection Observer)
- **Animated counters** — key numbers count up when they enter the viewport
- **Interactive cards** — categories as expandable/clickable sections
- **Data visualizations** — bar charts, timelines, or grids built with pure CSS/JS
- **Single file** — all HTML, CSS, and JS in one file, no external dependencies
- **Mobile responsive**

**Recommended sections:**

1. **Hero** — the big headline stat with an animated counter, plus a compelling subtitle
2. **Stats dashboard** — grid of 4-6 key metrics that count up on scroll
3. **Category cards** — one per theme, expandable to show use cases within
4. **Spotlight section** — 2-4 of the most compelling use cases shown in rich detail (scenario-style: "User asks X, System responds Y")
5. **Visualizations** — charts/bars for any quantitative data
6. **Footer** — methodology note, what data was used

**No external dependencies.** Pure HTML/CSS/JS. Use CSS animations (@keyframes), CSS Grid/Flexbox for layout, and vanilla JS for scroll triggers and counters.

### Phase 5: Build Utilities (if applicable)

If the research involved querying a database, API, or data source, write a utility library that makes those queries easy to reuse. This is what turns one-off research into lasting infrastructure.

**Utility design principles:**

- Methods should be named intuitively — `search("query")`, `top_senders()`, `recent(days=7)`
- All methods return lists of dicts (universal, easy to work with)
- Include a CLI mode so the utility works both as a library and a standalone tool
- Add docstrings with usage examples
- Handle edge cases gracefully (missing data, empty results)

### Phase 6: Update Project Instructions

If the project has a `claude.md` or similar instruction file, update it to document:

- What was created (the Markdown, HTML, utilities)
- How to use the utilities (with code examples)
- Where to find the research for context

This ensures future agents can build on the work instead of starting from scratch.

## Cleanup

The brainstorm agents may create intermediate files. After synthesis, move agent raw output into a subdirectory (e.g., `Agent Raw Output/`) to keep the workspace clean. The user should see the polished deliverables, not the sausage-making.

## Adapting to Context

This pipeline is flexible. Not every run needs all phases:

- **No data source?** — Agents can brainstorm from knowledge alone, but push them to be specific and give concrete examples rather than vague generalities.
- **No need for utilities?** — Skip Phase 5. The Markdown + HTML are the deliverables.
- **User wants speed over polish?** — Skip the HTML showcase and deliver just the Markdown synthesis.
- **Small topic?** — Use 2 agents instead of 4. The principle (multiple perspectives) still applies even at smaller scale.

The core of the skill is always: **multiple independent perspectives → synthesis → polished presentation**.
