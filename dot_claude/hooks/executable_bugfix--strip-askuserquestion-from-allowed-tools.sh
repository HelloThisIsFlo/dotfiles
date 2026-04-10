#!/usr/bin/env bash
# When AskUserQuestion is listed in a skill's allowed-tools, the permission
# evaluator's alwaysAllowRules path auto-approves it with an empty response
# before the UI renders. Claude proceeds as if the user answered, making
# unilateral decisions.
#
# Tracked in:
#   - anthropics/claude-code#29547 (root cause, closed, fix identified)
#   - anthropics/claude-code#29733 (duplicate, open)
#   - gsd-build/get-shit-done#803 (GSD-side report)
#
# Fix: requiresUserInteraction() guard on alwaysAllowRules early return
# Shipped in: v2.1.69
#
# REMOVE THIS HOOK when upgrading past 2.1.63.


shopt -s nullglob
files=(~/.claude/skills/*/SKILL.md)
[[ ${#files[@]} -eq 0 ]] && exit 0

matches=$(grep -rl '  - AskUserQuestion' "${files[@]}" 2>/dev/null)
[[ -z "$matches" ]] && exit 0

echo "$matches" | while read -r f; do
    sed -i '' '/^  - AskUserQuestion$/d' "$f"
done
