---
name: commit-by-theme
description: "Help the user commit changes grouped by theme — reviewing staged/unstaged diffs, splitting unrelated changes into separate commits, and flagging work-in-progress. Use when the user asks to commit staged changes, asks what the git state looks like, wants help organizing commits, says things like 'commit what I staged', 'commit this', 'what clusters do you see', 'help me sort out these changes', 'commit by theme', or presents a messy working tree and wants guidance on how to commit it cleanly. Also trigger when the user lists specific files and asks to commit them, or wants to split a commit into multiple."
---

# Commit by Theme

You help the user commit changes in clean, thematic groups. Your job is to look at what's changed, understand the intent behind each change, and either commit directly or ask when things are ambiguous.

## Two modes

### 1. "Commit this" mode

The user has changes ready (usually staged) and wants them committed. Your job:

1. Run `git diff --cached` (and `git diff --cached --stat` for overview)
2. Assess whether everything staged belongs in one commit or should be split
3. **If cohesive** — commit with a clear message. Done.
4. **If mixed themes** — stop. Tell the user what you see and suggest how to split. Don't commit anything until they confirm.
5. **If something looks like WIP** (partial implementation, TODO comments, half-finished logic) — flag it. "This looks like it might not be ready — want me to include it or skip it?"

### 2. "What's the state?" mode

The user's working tree is messy and they want help making sense of it. Your job:

1. Run `git status` and `git diff` (both staged and unstaged)
2. Read the actual diffs — don't just list filenames
3. Group changes into thematic clusters
4. For each cluster, give a **readiness assessment** (see below)
5. Present in **two separate tables**:
   - **Looks ready** — clusters that appear complete, with a "Reason" column explaining why
   - **Probably WIP** — clusters that look unfinished, with a "Reason" column explaining what's incomplete
6. Wait for the user to tell you what to commit

## Readiness assessment

For every cluster you identify — whether in "commit this" or "what's the state?" mode — proactively give your best guess on whether it looks ready to commit or still in progress. This is critical: the user relies on this to triage quickly without re-reading every diff themselves.

**Always show your reasoning.** Don't just say "looks like WIP" — explain what you saw:

- **Looks ready:** "Self-contained change — adds the bass plugin and its ignore entry. Nothing partial."
- **Probably WIP:** "The function is half-implemented — there's a `# TODO: handle edge case` on line 42 and the error path returns `None` without handling."
- **Uncertain:** "The config change looks complete, but it references a `watch_dirs` entry that doesn't exist yet — might be waiting on another change?"

**Signals that something might be WIP:**
- TODO/FIXME/HACK comments in the diff
- Commented-out code that looks like it's being iterated on
- Partial implementations (function defined but not wired up, config added but not referenced)
- Debug/test artifacts (print statements, hardcoded paths, temporary values)
- A change that would logically need a companion change that's missing

**Signals that something looks ready:**
- Self-contained unit (config + its ignore entry, plugin + its settings)
- Clean diff with no loose ends
- Matches a pattern you've seen committed before in this repo
- Adds or removes something completely (not half-added)

**Your assessment is always a guess** — you don't know what the user intends. Frame it that way: "This looks ready to me because..." or "I'd guess this is still WIP because..." The user decides. But always give the guess — don't punt with "I don't know, you tell me." The whole point is to help them triage faster.

## Commit messages

- Short summary line in imperative mood (under ~72 chars)
- Optional 1-2 line body if the "why" isn't obvious from the summary
- Match the style of recent commits in the repo (`git log --oneline -10`)
- No conventional commit prefixes unless the repo already uses them
- Pass the message via HEREDOC to preserve formatting:
  ```bash
  git commit -m "$(cat <<'EOF'
  Summary line here

  Optional body here.
  EOF
  )"
  ```

## Splitting commits

Sometimes part of a file belongs in one commit and another part in a different commit. This requires staging specific hunks. Use `git add -p` or `git add --patch` to stage individual hunks interactively — but since interactive mode doesn't work in this environment, use an alternative approach:

- Use `git diff <file>` to show the full diff
- Create a temporary patch for just the hunks you need
- Or suggest the user stage the specific parts themselves: "Could you stage just the chezmoi-related changes in this file? The fzf-tab parts should go in a separate commit."

When the split is straightforward, handle it. When it requires judgment about which lines belong where, describe the split and let the user decide.

## What NOT to do

- Never commit unstaged or untracked files unless the user explicitly asks
- Never push, create PRs, or do anything beyond committing
- Never add files to staging that the user didn't mention
- Never amend a previous commit unless explicitly asked
- If the user says "commit X" and you see Y is also changed but unrelated — commit only X, don't mention Y unless asked about the full state
- Don't add error handling, validation, or "improvements" to the commit message — just describe what changed
