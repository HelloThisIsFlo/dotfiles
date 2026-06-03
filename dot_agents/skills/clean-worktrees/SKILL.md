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

**a) Unmerged commit check** — First, check if the branch has any commits beyond main:
```bash
git log main..<branch> --oneline
```

If this is **not empty**, the branch has unmerged work. Proceed to step (b).

If this **is empty**, the branch has nothing that main doesn't have. But this could mean two very different things — "the work was merged" or "no work was ever done." To distinguish them, compare commit hashes:

```bash
git rev-parse <branch>
git rev-parse main
```

- **Different hashes** → the branch points to an older commit that main has moved past. Everything on this branch is already on main — but the reason matters:

  - The branch had work that was merged/fast-forwarded into main → genuinely merged, safe to delete.
  - The branch was created from an older main and never used, then main moved on → no work was done, but could still be an active session.

  Git can't distinguish these two sub-cases — in both, the branch tip is simply an ancestor of main. So use the **age check** (see below) to disambiguate:
  - **Old** (created days ago): almost certainly safe to delete — whether merged or just abandoned, the work (if any) is on main. Classify as **"Safe to delete (merged/stale)"**.
  - **Fresh** (created within the last few hours): could be an active agent session where main happened to move forward while the agent is still working. Classify as **"Needs user decision"** with a note like "branch is behind main (no unique commits), but worktree was created 2 hours ago — may be an active session."

  In both cases, check for uncommitted changes (step d) before confirming. Skip steps (b) and (c).

- **Same hash** → the branch is at the exact same commit as main HEAD. This is ambiguous: either just created (possibly an active session) or created long ago from this same commit and main never moved. Use the **age check** to disambiguate:
  - **Fresh** → likely an active session. Classify as **"Needs user decision"**.
  - **Old** → likely abandoned. Classify as **"Needs user decision"** but note the age as a signal.

  Check for uncommitted changes (step d) but skip steps (b) and (c).

**Age check** (used by both cases above):
```bash
# macOS: filesystem birth time of the worktree directory (epoch seconds)
stat -f '%B' <worktree-path>
```
Compare against the current time to get the age.
- **Fresh** (created within the last few hours): likely an active session — say something like "created 2 hours ago, you may still be working in this one"
- **Old** (created days ago): more likely abandoned — "created 3 days ago, probably stale"

Why this matters: worktrees are often used as isolated snapshots for agent sessions. An agent may be 30-60 minutes into a conversation, actively reading files and reasoning about the codebase, without having committed anything yet. From git's perspective, the worktree looks "empty" — zero commits, no changes. But from the user's perspective, there's a live session with accumulated context that took significant time to build. Deleting the worktree kills that session, and while the user can recreate the worktree and restore the agent, they lose all the conversational context and have to start over. That's the real cost — not lost code, but lost time and context.

**b) Merge check** — Only reached when step (a) found unmerged commits. `git branch --merged main` tells you if the branch's commits are reachable from main. If merged, it's safe to delete.

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
