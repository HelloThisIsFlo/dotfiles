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
2. Group changes into thematic clusters
3. Present them as a table or list: what goes together, why, and suggested commit order
4. Flag anything that looks like WIP or doesn't clearly belong to a group
5. Wait for the user to tell you what to commit

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
