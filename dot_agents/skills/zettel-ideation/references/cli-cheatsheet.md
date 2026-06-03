# Obsidian CLI Cheatsheet (for zettel-ideation)

Quick reference for talking to Flo's vault programmatically. Used internally by Pass A of graph traversal.

## Preconditions

- **Obsidian app must be running** — the CLI talks to the live app via local IPC. If it's closed, calls fail.
- `obsidian` must be in PATH (`/opt/homebrew/bin/obsidian` on Flo's machine).
- Always pass `vault=TheVault` to disambiguate.

## Primitives

### Outgoing links from a file

```bash
obsidian vault=TheVault links file="Note Title"
```

Returns one path per line. Includes unresolved `[[Concept]]` placeholders (marked `(unresolved)`).

### Backlinks (incoming references) to a file

```bash
obsidian vault=TheVault backlinks file="Note Title"
```

Returns paths. Use `format=json` for structured output, `counts` to include link counts.

### Arbitrary JS via `eval`

```bash
obsidian vault=TheVault eval code='JSON.stringify(...)'
```

Full access to Obsidian's runtime: `app.vault`, `app.metadataCache`, `app.workspace`. Output is prefixed with `=> ` on the first line — strip it if you want clean JSON.

Useful APIs:
- `app.vault.getMarkdownFiles()` — all `.md` TFile objects (path, basename, etc.)
- `app.metadataCache.resolvedLinks` — graph as `{src: {tgt: count}}` (forward edges only — build the reverse map yourself if you need it)
- `app.metadataCache.getFileCache(file)` — tags, frontmatter, links, headings for a single file

## Bundled wrapper: `scripts/neighborhood.py`

BFS the live graph from seed zettels. One call returns the full multi-layer neighborhood.

```bash
~/.claude/skills/zettel-ideation/scripts/neighborhood.py [--depth N] [--vault NAME] SEED [SEED ...]
```

- `SEED` — vault path (`_ZK_/Zettel/Foo.md`) or basename (`Foo`, `Having a system we can trust`). Resolved by basename match.
- `--depth` — number of BFS layers (default: 2). Use 3 for richer first-pass coverage.
- `--vault` — vault name (default: `TheVault`).

**Output** (JSON to stdout):

```json
{
  "seeds": ["_ZK_/Zettel/...", ...],
  "unresolvedSeeds": ["names that didn't match"],
  "totalNeighborhood": 28,
  "layers": [
    {"depth": 1, "count": 12, "paths": [...]},
    {"depth": 2, "count": 16, "paths": [...]}
  ]
}
```

**Filters**: only includes notes under `_ZK_/Zettel/`, `_ZK_/Evergreen/`, `_ZK_/Distill/Fragment/`. Skips concept-stub notes like `[[Flow]]` and `[[MIDI]]`.

**On unresolvable seeds**: lists them under `unresolvedSeeds` and proceeds with whatever resolved. If nothing resolves, returns `{"error": "No seeds resolved", "requested": [...]}`.

## Other useful commands (rarely needed)

- `obsidian vault=TheVault unresolved` — list all unresolved `[[wikilinks]]` in the vault (useful if Flo wonders what concepts he's referenced but never written).
- `obsidian vault=TheVault tags counts` — tag inventory with counts.
- `obsidian vault=TheVault tag name=zk/zettel verbose` — list all files with a given tag.
