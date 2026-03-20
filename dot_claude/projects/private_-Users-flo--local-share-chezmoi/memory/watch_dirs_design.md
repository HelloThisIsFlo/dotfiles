---
name: Watch-dirs feature design
description: Design decisions for the chezmoi watch-dirs feature — auto-detect new files in tracked directories and prompt to add or ignore. Decided 2026-03-20.
type: project
---

Feature that detects new unmanaged files in watched directories and prompts the user to add them to chezmoi or ignore them.

**Config:** `.chezmoidata/watch_dirs.yaml` — flat list per OS key (no `common` key, duplication is fine):
```yaml
watch_dirs:
  macos:
    - ".config/fish"
    - ".config/kitty"
  linux:
    - ".config/fish"
```

**Reading config in hook:** `chezmoi execute-template` (not `jq`):
```bash
DIRS=$(chezmoi execute-template '{{ range index .watch_dirs .os }}{{ . }}
{{ end }}')
```

**Detection:** `chezmoi unmanaged` per watched directory.

**Recursion guard:** Lock file (`/tmp/.chezmoi-watch-lock`) — hook creates it, inner chezmoi calls see it and exit immediately.

**Triggers:** `hooks.apply.pre` and `hooks.status.pre` (not diff, not read-source-state).

**UX flow:** Batch-first with drill-down:
- Show all new files with count
- Offer: [a]dd all / [i]gnore all / [s]kip all / [p]ick one-by-one
- Per-file mode: [a]dd / [i]gnore / [s]kip per file

**Ignore mechanism:** Append to `.chezmoiignore` under header:
`# ── watch-dirs: auto-ignored (new entries appended below) ──`
No end marker. Script only appends. User can freely edit/remove lines. Removing a line makes the file show up again next time (self-healing).

**Custom OS variable:** `.os` maps `darwin` → `macos`, `linux` → `linux` (already implemented). Watch-dirs YAML keys match this.

**Why:** chezmoi is file-level, not directory-level. Apps like Fish create new files in managed directories that `chezmoi re-add` won't pick up. This hook fills the gap without requiring a full config format migration or external tools.
