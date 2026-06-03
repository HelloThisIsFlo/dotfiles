---
name: audit-ask-questions
description: Audit Claude Code sessions for the AskUserQuestion silent auto-complete bug where empty answers are hallucinated as real selections. Triggers on "audit ask questions", "empty answer bug", "check phantom answers", "session audit", "did I actually answer", "transcript audit", "check for hallucinated answers", "AskUserQuestion bug".
---

# Audit AskUserQuestion Bug

This skill detects the Claude Code bug where `AskUserQuestion` silently auto-completes with empty responses (`answers: {}`), causing Claude to hallucinate that the user chose the "(Recommended)" option and proceed with writes, commits, or agent spawns based on decisions the user never made.

## Workflow

1. **Determine scope** from the user's request:
   - Default: today's sessions
   - User may specify `--since`, `--project`, `--all`, or a specific `--date`
2. **Run the audit script** with the appropriate flags
3. **Parse JSON output** and present a formatted report
4. **For critical/high findings**, offer to check `git log` for commits that may need reverting

## Running the Audit

```bash
python3 ~/.claude/skills/audit-ask-questions/scripts/audit.py [OPTIONS]
```

### CLI Reference

| Flag | Description | Default |
|------|-------------|---------|
| `--date DATE` | Specific date (YYYY-MM-DD) | today |
| `--since DATE` | Start of date range | — |
| `--until DATE` | End of date range | today |
| `--project SUBSTR` | Filter by project dir name (repeatable) | all projects |
| `--all` | Disable date filtering | — |
| `--include-subagents` | Include subagent `.jsonl` files | main sessions only |

### Examples

```bash
# Today's sessions (default)
python3 ~/.claude/skills/audit-ask-questions/scripts/audit.py

# Last 3 days
python3 ~/.claude/skills/audit-ask-questions/scripts/audit.py --since 2026-02-28

# Only omnifocus-operator project
python3 ~/.claude/skills/audit-ask-questions/scripts/audit.py --project omnifocus-operator

# Everything, all time
python3 ~/.claude/skills/audit-ask-questions/scripts/audit.py --all
```

## Output Schema

The script outputs JSON to stdout with this structure:

```json
{
  "metadata": {
    "scan_time": "ISO timestamp",
    "date_range": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
    "sessions_scanned": 12,
    "total_ask_calls": 79,
    "total_empty": 35,
    "bug_rate_percent": 44.3
  },
  "projects": [
    {
      "project_dir": "-Users-flo-Work-Private-Dev-MCP-omnifocus-operator",
      "sessions": [
        {
          "session_id": "UUID",
          "file_path": "/full/path.jsonl",
          "git_branch": "main",
          "session_start": "ISO timestamp",
          "total_ask_calls": 15,
          "empty_count": 8,
          "empty_responses": [
            {
              "timestamp": "ISO timestamp",
              "questions_asked": [
                { "question": "...", "options": ["..."], "multi_select": false }
              ],
              "hallucinated_answer": "truncated thinking text...",
              "actions_after": [
                { "tool": "Write", "detail": "path/to/file.py" }
              ],
              "severity": "high",
              "severity_reason": "Followed by Write/Edit"
            }
          ]
        }
      ]
    }
  ],
  "summary": {
    "critical_count": 2,
    "high_count": 10,
    "medium_count": 15,
    "low_count": 8
  }
}
```

## Presenting Results

Format the report with:
- **Summary banner**: sessions scanned, bug rate %, severity breakdown
- **Per-project section**: project name, total empty/total asks
- **Per-session table**: session ID (short), branch, empty count, worst severity
- **Detail for critical/high**: show the question asked, what Claude hallucinated, and what actions followed
- For critical findings (Write/Edit + git commit), offer to run `git log --oneline` in the project to check for commits to revert

## Severity Classification

| Severity | Condition |
|----------|-----------|
| **critical** | Empty answer followed by Write/Edit AND git commit (Bash with `git commit`) |
| **high** | Empty answer followed by Write/Edit (no commit detected) |
| **medium** | Empty answer followed by Task spawn, cascading AskUserQuestion, or other tool use |
| **low** | User interrupted, or only text/thinking followed (no tool actions) |
