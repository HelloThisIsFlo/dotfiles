# Technical Diagram Style

Use this reference for Mermaid diagrams that explain systems, pipelines, agents, ownership, environments, or data movement.

## Choose by relationship

- **Sequence diagram**
  - Chronological interactions
  - Handoffs
  - Data movement over time
- **Left-to-right flowchart**
  - Systems
  - Ownership
  - Environments
  - Dependencies
  - Topology
- Change direction only when horizontal width or the relationship itself makes another layout clearer.
- A long linear flowchart is usually a sequence diagram in disguise.

## Make the relationship visible

- Group elements by meaningful system, responsibility, environment, or ownership boundaries.
- Use semantic emoji in group labels and important nodes or participants.
- Keep fills transparent or controlled by Mermaid's active theme.
- Use distinct, restrained border colours to improve scanning.
- Keep equivalent groups visually consistent within the same document.
- Simplify or remove groups when they obscure the main relationship.

## Put meaning in the right place

- **Nodes** represent:
  - Actors
  - Components
  - Data
  - Durable states
- **Arrows** represent:
  - Actions
  - Transfers
  - Handoffs
- Prefer an arrow label over an action-only node when no durable component exists.
- Labels carry the meaning; colour and emoji reinforce it.

## Sequence-diagram boundaries

Mermaid's sequence `box` colour controls the fill, not an independently configurable border.

- Give each group a unique, fully transparent `rgba(...,0)` value.
- Match that exact fill value with diagram-local `themeCSS`.
- Apply the saturated version of the colour to the boundary.
- Keep the alpha at `0`; fixed fills undermine theme-safe rendering.
- If a renderer stops supporting the selector:
  - Keep the boxes transparent and accept the renderer's neutral boundary.
  - Report the limitation.
  - Do not fall back to fixed fills.

## Teaching examples

### Copy these invariants

- Relationship-driven diagram choice
- Meaningful boundaries
- Transparent fills
- Restrained border colours
- Semantic emoji
- Actions on arrows
- Overall reading direction without forcing one linear path

### Adapt these details

- Group names
- Participant count
- Colours
- Emoji choices
- Direction and layout

The colours below demonstrate the mechanism. They are not a prescribed palette.

### Grouped flowchart

The map reads left to right, but configuration bypasses the delivery path and updates the runtime independently.

```mermaid
flowchart LR
    subgraph A["📝 Authoring"]
        S["📄 Source"]
        C["⚙️ Runtime config"]
    end

    subgraph D["⚙️ Delivery"]
        W["🔁 Workflow"]
        P["📦 Package"]
    end

    subgraph R["🌐 Runtime"]
        K["🧩 Live config"] -->|configure| V["🚀 Service"]
    end

    S -->|publish| W
    W -->|build| P
    P -->|deploy| V
    C ==>|update independently| K

    style A fill:transparent,stroke:#3b82f6,stroke-width:2px
    style D fill:transparent,stroke:#f59e0b,stroke-width:2px
    style R fill:transparent,stroke:#10b981,stroke-width:2px
```

### Grouped sequence diagram

```mermaid
---
config:
  themeCSS: |
    .rect[fill="rgba(59,130,246,0)"] { stroke: rgb(59,130,246) !important; stroke-width: 2px !important; }
    .rect[fill="rgba(245,158,11,0)"] { stroke: rgb(245,158,11) !important; stroke-width: 2px !important; }
    .rect[fill="rgba(16,185,129,0)"] { stroke: rgb(16,185,129) !important; stroke-width: 2px !important; }
---
sequenceDiagram
    box rgba(59,130,246,0) 👤 Client
        participant C as 👤 Caller
    end
    box rgba(245,158,11,0) ⚙️ Processing
        participant A as 🔌 API
        participant W as ⚙️ Worker
    end
    box rgba(16,185,129,0) 💾 Storage
        participant D as 🗄️ Database
    end

    C->>A: Submit request
    A->>W: Start work
    W->>D: Store result
    D-->>W: Confirm write
    W-->>C: Return result
```

## Syntax safety

- In sequence-diagram messages and notes, avoid literal semicolons. Reword the label or escape the semicolon as `#59;`.
- After the final edit, run the shared validator below and fix syntax errors before delivery.
- If the parser cannot be run, report that syntax validation remains incomplete.
- Parsing checks syntax. Rendering remains limited to structural uncertainty.

### Shared validation command

Use the published [mermaid-lint CLI](https://github.com/jasonworden/mermaid-lint), pinned below. Requires Node.js 22+ and npm/npx. This follows the [Agent Skills guidance for existing tools](https://agentskills.io/skill-creation/using-scripts#one-off-commands).

```sh
npx --yes @mermaid-lint/cli@0.53.1 --no-semantic --format json /absolute/path/to/document.md
```

- Pass explicit file paths, including untracked drafts. The same command accepts raw `.mmd` files and multiple input paths.
- `npx` downloads into npm's cache on first use and reuses it later. No global install, skill-local `node_modules`, or separate setup step.
- `--no-semantic` disables additional diagram lint rules. Validation uses a Rust/WASM fast path with Mermaid's parser as fallback; it does not render. Do not use `--fix` for a validation pass.
- Check both the exit code and JSON results: `0` means no reported errors, `1` means validation failed, `2` means a usage/input error. A zero-diagram result does not prove validation.
- Confirm the reported diagrams cover every intended diagram. This version misses blockquoted fences and scans Mermaid examples nested inside larger code fences. For those cases, copy each intended diagram body into a temporary `.mmd` file and validate it with the same command; do not change the document's formatting to accommodate the scanner.
- If execution fails or coverage is incomplete, report the gap. The sibling `explain-visually` skill uses this same command and version.

## Render only for structural uncertainty

- **Simple diagram**
  - Review the Mermaid source against the communication goal.
  - If the intended relationship, grouping, and direction are clear, no render is needed.
- **Complex diagram**
  - Render only when Mermaid's automatic layout may change or obscure the intended reading.
  - Complexity signals:
    - Multiple branches or handoffs
    - Nested or competing groups
    - Likely crossing edges
    - Long labels or unusual width
    - Mermaid-controlled ordering that may alter the reading path
- **If rendered, inspect structure only**
  - Reading direction
  - Grouping
  - Edge crossings
  - Node order
  - Label wrapping
- Do not switch themes or assess cosmetic appearance.
- Successful parsing validates syntax; it does not create a visual-QA requirement.
