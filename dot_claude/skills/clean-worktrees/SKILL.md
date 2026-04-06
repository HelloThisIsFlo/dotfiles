---
name: clean-worktrees
description: "Clean up stale git worktrees and their associated branches. Checks merge status, detects rebased work on main, flags uncommitted changes, and only deletes what's safe. Use this skill whenever the user mentions worktrees, stale branches, cleaning up branches, or worktree cleanup. Trigger on: 'clean worktrees', 'delete worktrees', 'stale worktrees', 'worktree cleanup', 'clean up branches', 'remove worktrees'."
---

# Clean Worktrees

Safely remove stale git worktrees and their branches. The goal is to never lose work — verify everything is on main before deleting.

## Workflow

### 1. List worktrees

Run `git worktree list` to see all active worktrees. The main worktree is never touched.

### 2. Check each worktree branch

For every non-main worktree, determine its status:

**a) Zero-commit check** — First, check if the branch has any commits beyond main:
```bash
git log main..<branch> --oneline
```
If this is empty, the worktree was created but no work was committed yet. This is ambiguous — it could be freshly started (actively in use right now) or abandoned before any work began. There's no way to tell from git alone.

Here's why this matters: worktrees are often used as isolated snapshots for agent sessions. An agent may be 30-60 minutes into a conversation, actively reading files and reasoning about the codebase, without having committed anything yet. From git's perspective, the worktree looks "empty" — zero commits, no changes. But from the user's perspective, there's a live session with accumulated context that took significant time to build. Deleting the worktree kills that session, and while the user can recreate the worktree and restore the agent, they lose all the conversational context and have to start over. That's the real cost — not lost code, but lost time and context.

A zero-commit branch is also technically "merged" into main (it points at a commit main already has), so step (b) below will say "safe to delete." That's a trap — the merge check is answering a meaningless question for this case.

So for zero-commit worktrees: skip steps (b)-(d) entirely and move to the next worktree. Only the user can tell you whether it's abandoned or active — but you can help them by checking when the worktree was created:

```bash
# macOS: filesystem birth time of the worktree directory (epoch seconds)
stat -f '%B' <worktree-path>
```

Compare against the current time to get the age. Use this to give the user a helpful nudge in your report:
- **Fresh** (created within the last few hours): likely an active session — say something like "created 2 hours ago, you may still be working in this one"
- **Old** (created days ago): more likely abandoned — "created 3 days ago, probably stale"

This is guidance, not a verdict. Always classify as "Needs user decision" regardless of age — but the freshness signal helps the user quickly triage without having to remember which worktree is which.

**b) Merge check** — Only reached when step (a) found commits. `git branch --merged main` tells you if the branch's commits are reachable from main. If merged, it's safe to delete.

**c) Rebased work check** — If not merged, the work may still be on main under different SHAs (from rebasing or cherry-picking). This is a two-level check:

**Level 1 — commit message scan** (quick signal, not proof):
```bash
git log --oneline main | grep -F "<first 40 chars of commit subject>"
```
If all unmerged commits have message matches on main, it's *likely* stale — but commit messages alone don't guarantee identical content. Someone could have amended the commit on main.

**Level 2 — content verification** (when Level 1 matches):
Compare the actual tree content between the worktree branch and main. For each unmerged commit, verify the changes it introduced are present on main:
```bash
# Compare the final state of changed files
git diff main..<branch> -- <file>
```
If the diff is empty, the work is truly on main. If there are any differences — code, planning docs, anything — report them. Don't dismiss differences just because they're "only docs" or "only planning files." The user decides what matters.

Only classify as "safe to delete" when content is verified identical, or the branch is truly merged (`git branch --merged`). If commit messages match but you can't confirm content, report it as "likely stale — commit messages match but content not verified" and let the user decide.

**d) Uncommitted changes** — Run `git -C <worktree-path> status --porcelain` to catch untracked or modified files. If present, check whether those files already exist on main with identical content. Always report uncommitted files to the user — even planning docs, debug notes, or files that seem trivial. Don't classify anything as "safe to discard" on the user's behalf.

### 3. Report findings

Present a clear summary before deleting anything. Group worktrees into:

- **Safe to delete** — merged, or rebased onto main, no uncommitted changes
- **Safe to delete (with note)** — merged/rebased but has uncommitted files that are already on main or are disposable (e.g., `test-file.txt`)
- **Needs user decision** — unmerged work not found on main, or uncommitted changes with unique content

For worktrees needing user decision, show the unmerged commits and/or uncommitted files so the user can make an informed call.

### 4. Delete confirmed worktrees

Handle nested worktrees (worktree-inside-worktree) by deleting inside-out — deepest first, then parent.

```bash
git worktree remove --force <path>
git branch -D <branch-name>
```

Note: a worktree may use a non-standard branch name (e.g., `phase-37.1-clean` instead of `worktree-agent-xyz`). In that case, there may be two branches to clean — the checked-out branch AND the auto-created `worktree-agent-*` branch. Check for both.

### 5. Check for orphaned branches

After removing worktrees, run `git branch | grep worktree` to find branches that no longer have an associated worktree directory. Apply the same merge/rebase check and clean up.

### 6. Prune remote tracking refs

If any remote worktree branches were deleted, run `git remote prune origin` to clean up stale remote refs.

## Key Principles

- **Never delete without verifying.** Even if the user says "delete everything", check merge status first and report anything that's not on main.
- **Rebased ≠ lost.** Many worktree branches are rebased onto main, so `git branch --merged` misses them. Always do the commit-message search as a second check.
- **Report, don't decide.** For anything ambiguous, show the user what's there and let them choose. Don't silently discard uncommitted work.
