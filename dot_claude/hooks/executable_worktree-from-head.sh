#!/bin/bash
# WorktreeCreate hook: branch worktrees from local HEAD instead of origin/HEAD.
#
# Without this hook, Claude Code bases worktrees on the remote tracking branch,
# so unpushed local commits aren't available to agents.
#
# Workaround for: https://github.com/anthropics/claude-code/issues/23622
#
# Input: JSON on stdin with session_id, cwd, hook_event_name
# Output: worktree path on stdout

set -euo pipefail

# Parse input
INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

if [ -z "$CWD" ]; then
  echo "ERROR: No cwd in hook input" >&2
  exit 2
fi

cd "$CWD"

# Generate unique worktree name
AGENT_ID="agent-$(openssl rand -hex 4)"
WORKTREE_PATH="$CWD/.claude/worktrees/$AGENT_ID"
BRANCH_NAME="worktree-$AGENT_ID"

# Create worktree from local HEAD
mkdir -p "$(dirname "$WORKTREE_PATH")"
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" HEAD >/dev/null 2>&1

# Return the path to Claude Code
echo "$WORKTREE_PATH"
