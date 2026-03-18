# chezmoi merge — Resolving Conflicts with a 3-Way Merge

You ran `chezmoi status`, saw `MM`, and you need parts of both sides. `apply` would nuke your disk changes. `re-add` would nuke your source changes. `chezmoi merge` is the "keep both" tool — it opens a 3-way merge editor so you can pick and choose.

But the merge UI is deceptive. Lines that are clearly different between source and disk sometimes don't show as conflicts. This is correct behavior, but only makes sense once you understand the 3-way model. This sheet explains why.

---

## When to merge (vs apply or re-add)

You're looking at `MM` in `chezmoi status`. Three options:

| I want to... | Use | What it does |
|---|---|---|
| Keep source, discard disk changes | `chezmoi apply ~/file` | Source overwrites disk |
| Keep disk, discard source changes | `chezmoi re-add ~/file` | Disk overwrites source |
| Keep parts of both | `chezmoi merge ~/file` | Opens merge editor |

Use `chezmoi diff ~/file` first if you're not sure which case you're in.

> **Never `re-add` a `.tmpl` file.** It replaces template logic with rendered output. For templates, edit the source manually or use merge. See [Templates cheat sheet](templates.md).

In practice, merge is rare if you always use `chezmoi edit` (which edits source directly). You hit it when an app mutates a config file at `~/` while you've also changed the source — or during a migration when files are being edited on both sides.

---

## The 3-way merge model

A 3-way merge compares two versions against a **common ancestor** (the "base"). This is the same concept as git merge — you're not diffing left vs right, you're diffing left vs base and right vs base independently.

```
                    base
                  (committed)
                   /      \
                  /        \
         source changed    disk changed
         (left pane)       (right pane)
```

The merge tool uses the base to figure out **who changed what**. If only one side changed a region, that change wins automatically. If both sides changed the same region, that's a real conflict — you pick.

### Our config uses git history as the base

The default chezmoi merge config copies `.Target` (what source renders) as the base. This is useless — the base is identical to one of the inputs, making it a glorified 2-way diff where everything looks like it came from one side.

Our custom config uses `git show HEAD:<file>` to extract the last committed version of the source file as the base. This gives a proper common ancestor, which is what makes auto-resolution work.

> **Caveat: uncommitted files.** If the file has never been committed to git, `git show HEAD:` fails. The config falls back to copying `.Target` as the base — degrading to a 2-way merge. Always commit your source files before making changes to get proper 3-way merges.

---

## Reading the VS Code merge UI

Our config arranges the panes like this:

```
+---------------------------+---------------------------+
|     Left pane             |     Right pane            |
|     .Target               |     .Destination          |
|     (what source renders) |     (what's on disk ~/  ) |
|     "what chezmoi wants"  |     "what you/apps did"   |
+---------------------------+---------------------------+
|     Result pane                                       |
|     .Source (the actual source file that gets saved)   |
+-------------------------------------------------------+
```

The base (last committed version from git) is invisible — VS Code uses it internally to compute which regions changed on which side.

---

## The counter-intuitive part: auto-resolution

This is the thing you'll forget. Read this section twice.

A 3-way merge doesn't show you "left vs right." It shows you "what changed relative to the base." These are different things, and the difference is why some lines look different between panes but don't show conflict markers.

### Scenario 1: each side changed a different section

You edited the Display section in source. An app updated the Plugins section on disk. Here's what the three versions look like:

```
LINE    BASE (committed)              LEFT (source)                 RIGHT (disk)
────    ────────────────              ─────────────                 ────────────

 5      # --- Display ---             # --- Display ---             # --- Display ---
 6      theme = "gruvbox"         >>  theme = "modified"            theme = "gruvbox"
 7      font_size = 14            >>  font_size = 16                font_size = 14
 8      show_sidebar = true           show_sidebar = true           show_sidebar = true
        ───── only LEFT changed ──────────────────── auto-resolved: left wins ──────

10      # --- Network ---             # --- Network ---             # --- Network ---
11      proxy = "none"                proxy = "none"                proxy = "none"
12      timeout = 30                  timeout = 30                  timeout = 30
        ───── nobody changed ───────────────────────── nothing to do ───────────────

15      # --- Plugins ---             # --- Plugins ---             # --- Plugins ---
16      plugins = ["..docker"]        plugins = ["..docker"]    <<  plugins = ["..k8s"]
17      auto_update = true            auto_update = true        <<  auto_update = false
        ───── only RIGHT changed ─────────────────── auto-resolved: right wins ─────
```

You open `chezmoi merge` and look at VS Code:

- **Lines 6-7:** Left says `"modified"` / `16`. Right says `"gruvbox"` / `14`. They're clearly different. But **no conflict markers. No "Accept" buttons.** Your brain screams "that's a conflict!" — it's not. The base also says `"gruvbox"` / `14`, matching the right side. Only the left changed. Auto-resolved.
- **Lines 16-17:** Same logic, other direction. Only the right changed. Auto-resolved.
- **Result pane:** Already has both changes merged. You might not need to click anything.

### Scenario 2: both sides changed the same lines

Now imagine both sides edited the Display section with different values:

```
LINE    BASE (committed)              LEFT (source)                 RIGHT (disk)
────    ────────────────              ─────────────                 ────────────

 6      theme = "gruvbox"         >>  theme = "catppuccin"     <<  theme = "tokyo-night"
        ───── BOTH changed ────────────────────── CONFLICT: you choose ─────────────
```

Both sides diverged from the base on the same line. VS Code highlights this region on **both** panes with "Accept" buttons. You pick one, accept a combination, or edit the result manually.

### The rule

```
                          Did LEFT change     Did RIGHT change
                          (vs base)?          (vs base)?
                          ───────────         ────────────
Only left changed?        Yes                 No           →  auto-resolved: left wins
Only right changed?       No                  Yes          →  auto-resolved: right wins
Both changed same lines?  Yes                 Yes          →  CONFLICT — you choose
Neither changed?          No                  No           →  nothing to do
```

"Changed" means "differs from the base (last committed version)" — NOT "differs from the other pane."

> **Why this matters.** This is the whole point of 3-way merge. If you edited Display in source and an app edited Plugins on disk, those aren't in conflict — the merge tool combines them automatically. The 2-way fallback (default chezmoi config) can't do this because there's no real base to compare against, so everything looks like a conflict.

---

## After the merge

`chezmoi merge` only modifies the **source file**. Your disk (`~/`) is untouched. You must apply afterwards:

```bash
chezmoi merge ~/file      # resolve conflicts → saves to source
chezmoi apply ~/file      # push merged source → disk
chezmoi status ~/file     # should be clean now
```

This is consistent with chezmoi's philosophy: source is the single source of truth. Even merge doesn't write to `~/` directly — it fixes the source, then `apply` does the rest.

---

## The merge config

The config lives in `.chezmoi.toml.tmpl`. It mixes two template evaluation times:

- **Init-time** (Go template at `chezmoi init`): `{{ .chezmoi.sourceDir }}` resolves to the actual path
- **Merge-time** (at `chezmoi merge`): `{{ "{{ .Source }}" }}` passes through as literal `{{ .Source }}`

The base extraction: `git show HEAD:<relative-path>` gets the last committed version. If it fails (file never committed), falls back to copying `.Target` (2-way degradation).

To debug the merge args, temporarily replace the command in the generated config (`~/.config/chezmoi/chezmoi.toml`, NOT the template) with:

```
'echo "Left:   {{ .Target }}" && echo "Right:  {{ .Destination }}" && echo "Base:   $BASE" && echo "Result: {{ .Source }}"',
```

Then `chezmoi init` to reset back to the real config.

---

## Quick reference

```
chezmoi merge ~/file      # open 3-way merge in VS Code
chezmoi apply ~/file      # push merged result to disk (REQUIRED after merge)
chezmoi diff ~/file       # preview what apply would change (use before deciding)

VS Code panes:
  Left   = source (what chezmoi wants)
  Right  = disk   (what's at ~/)
  Base   = last committed version (invisible, used for auto-resolution)
  Result = source file (what gets saved)

Auto-resolution:
  One side changed   → auto-accepted, no conflict shown
  Both sides changed → conflict, you pick
  "Changed" = differs from base (committed version), NOT from the other pane

After merge:
  merge only edits source → you MUST `chezmoi apply` to push to disk
```

| I want to... | Command |
|---|---|
| Discard disk, keep source | `chezmoi apply ~/file` |
| Discard source, keep disk | `chezmoi re-add ~/file` |
| Keep parts of both | `chezmoi merge ~/file` then `chezmoi apply ~/file` |
| See what's different first | `chezmoi diff ~/file` |
| Debug merge tool args | Edit generated `~/.config/chezmoi/chezmoi.toml`, then `chezmoi init` to reset |
