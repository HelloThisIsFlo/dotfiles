#!/usr/bin/env bash
# PostToolUse hook: auto-format Python files after Write/Edit
#
# Gated by CLAUDE_HOOK_AUTOFORMAT_PYTHON=1 (set per-project in .claude/settings.json).
# Runs ruff check --fix + ruff format on .py files.
#
# Unfixable lint issues are silently ignored — they surface
# at commit time via pre-commit hooks.
#
# To enable in a project, add to .claude/settings.json:
#
#   { "env": { "CLAUDE_HOOK_AUTOFORMAT_PYTHON": "1" } }

set -euo pipefail

if [[ "${CLAUDE_HOOK_AUTOFORMAT_PYTHON:-}" != "1" ]]; then
    exit 0
fi

file_path=$(jq -r '.tool_response.filePath // .tool_input.file_path')

if [[ "$file_path" == *.py ]]; then
    uv run ruff check --fix --quiet "$file_path" 2>/dev/null || true
    uv run ruff format --quiet "$file_path" 2>/dev/null || true
fi
