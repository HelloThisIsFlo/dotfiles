# chezmoi status — Reading the Output

You run `chezmoi status`, see `MM` next to a file, and think "both source and target changed." That's wrong — and the real meaning isn't obvious from the help text either. This sheet explains what the two columns actually mean so you stop guessing.

---

## The mental model

`chezmoi status` prints two characters per file. It's tempting to read them as "source | target" (like git's "staging | working tree"). They're not.

Chezmoi tracks three states for every managed file:

1. **Last-applied state** — what chezmoi wrote to `~/` the last time you ran `apply` (or `add`)
2. **Actual state** — what's currently sitting at `~/filename` right now
3. **Target state** — what chezmoi *would* render from the source repo if you ran `apply`

The two columns compare adjacent pairs:

```
Column 1                    Column 2
last-applied → actual       actual → target
"what changed on disk"      "what apply would do"
```

Column 1 is informational: "did something touch this file since chezmoi last wrote it?" (you, an app, an OS update).

Column 2 is actionable: "will `chezmoi apply` change this file?"

---

## Reading real output

We tested this by creating four files, all starting with "original", then making targeted edits:

```
 M test-modify-source         # edited only in source repo
MM test-modify-both           # edited in both places (different content)
MM test-modify-target         # edited only at ~/
                              # test-hack — MISSING (see below)
```

**` M` on `test-modify-source`** — Disk still has "original" (matches what chezmoi last wrote, so column 1 = space). Source now says "edited in source" (differs from disk, so column 2 = M). Running `chezmoi apply` would update the file. This is the safe, no-conflict case.

**`MM` on `test-modify-target`** — Disk was changed to "edited in target" (column 1 = M, changed since last apply). Source still says "original" (differs from disk, so column 2 = M). This is a conflict — `chezmoi apply` would overwrite your target edit.

**`MM` on `test-modify-both`** — Disk says "edited in target (both)", source says "edited in source (both)". Both diverged from "original". Column 1 = M (disk changed), column 2 = M (disk differs from source). Same conflict status as target-only — chezmoi can't tell the difference.

> **The trap.** `MM` doesn't mean "source changed AND target changed." It means "target changed since last apply AND target differs from source." Both columns reference the target — they just compare it against different baselines. Notice that `test-modify-target` (only target edited) and `test-modify-both` (both edited) show the same `MM` code.

---

## The `M ` mystery — can it even happen?

We tried to force it with `test-hack`: edit both source and target to the **same** new content, so disk diverges from last-applied (column 1 = M) but matches source (column 2 = space).

Result: **the file disappeared from status entirely.** Chezmoi doesn't show files where disk matches source, period. `M ` is technically what the help text describes, but in practice chezmoi skips the file instead of displaying it.

This tells you something important: chezmoi status is really just answering **"does disk match what source wants?"** If yes, the file is clean — regardless of history.

---

## What you'll actually see

| Code | What happened | What to do |
|---|---|---|
| ` M` | Source has updates, disk is untouched | `chezmoi apply` — safe |
| `MM` | Disk was edited AND differs from source | Conflict. `chezmoi diff` to inspect, then `re-add` (keep disk) or `apply` (keep source) |
| ` A` | New file in source, doesn't exist on disk | `chezmoi apply` to create |
| `A ` | File deleted from disk, source still has it | `chezmoi apply` to recreate, or `chezmoi forget` to stop managing |

> **`M ` is not a thing.** If disk matches source, the file just doesn't appear — even if both sides independently changed to the same content.

---

## Resolving `MM` — apply, re-add, or merge?

| I want to... | Use |
|---|---|
| Keep source, discard disk | `chezmoi apply ~/file` |
| Keep disk, discard source | `chezmoi re-add ~/file` |
| Keep parts of both | `chezmoi merge ~/file` then `chezmoi apply ~/file` |
| See what's different first | `chezmoi diff ~/file` |

> **Never `re-add` a `.tmpl` file.** It replaces template logic with rendered output. For templates, use `chezmoi merge` or manually edit the source. See [Templates cheat sheet](templates.md).

For the full story on how 3-way merge works (especially the counter-intuitive auto-resolution behavior), see the [Merge visual explainer](chezmoi-merge.html) or try the [Interactive merge simulator](chezmoi-merge-interactive.html) (open in browser).

---

## Quick reference

```
chezmoi status output:  XY  path/to/file

X = last-applied vs disk    "did the disk change?"
Y = disk vs source          "would apply change it?"

 M = source ahead, safe to apply
MM = conflict — diff, then re-add or apply
 A = new in source, apply to create
A  = deleted from disk, apply to recreate
M  = theoretically "in sync" but chezmoi just hides the file instead
```
