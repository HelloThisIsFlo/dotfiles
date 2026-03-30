#!/usr/bin/env python3
"""Audit Claude Code sessions for the AskUserQuestion silent auto-complete bug.

Detects cases where AskUserQuestion returned empty answers ({}) and Claude
hallucinated the user's selection, potentially taking actions based on
decisions the user never made.
"""

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Subagent files typically have a parent session UUID embedded
SUBAGENT_PATTERN = re.compile(r"^[0-9a-f]{8}-.*_[0-9a-f]{8}-")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Audit Claude Code sessions for AskUserQuestion empty-answer bug"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Specific date to scan (YYYY-MM-DD). Default: today",
    )
    parser.add_argument(
        "--since", type=str, help="Start of date range (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--until", type=str, help="End of date range (YYYY-MM-DD). Default: today"
    )
    parser.add_argument(
        "--project",
        type=str,
        action="append",
        dest="projects",
        help="Filter by project directory name substring (repeatable)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Disable date filtering (scan everything)"
    )
    parser.add_argument(
        "--include-subagents",
        action="store_true",
        help="Include subagent .jsonl files (default: main sessions only)",
    )
    return parser.parse_args()


def resolve_date_range(args):
    """Return (start_date, end_date) or (None, None) if --all."""
    if args.all:
        return None, None

    if args.since:
        start = date.fromisoformat(args.since)
        end = date.fromisoformat(args.until) if args.until else date.today()
        return start, end

    if args.date:
        d = date.fromisoformat(args.date)
        return d, d

    # Default: today
    today = date.today()
    return today, today


def is_subagent_file(filepath: Path) -> bool:
    """Heuristic: subagent files contain underscores in the UUID-like name."""
    name = filepath.stem
    return "_" in name or SUBAGENT_PATTERN.match(name) is not None


def discover_jsonl_files(date_start, date_end, project_filters, include_subagents):
    """Walk project dirs and collect JSONL files matching filters."""
    if not CLAUDE_PROJECTS_DIR.exists():
        return []

    files = []
    for project_dir in sorted(CLAUDE_PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        # Project name filter
        if project_filters:
            dir_name = project_dir.name.lower()
            if not any(p.lower() in dir_name for p in project_filters):
                continue

        for jsonl_file in sorted(project_dir.glob("*.jsonl")):
            if not include_subagents and is_subagent_file(jsonl_file):
                continue
            files.append((project_dir.name, jsonl_file))

    if date_start is None:
        # --all: no date filtering
        return files

    # Filter by session start date (read first entry's timestamp)
    filtered = []
    for project_name, jsonl_file in files:
        try:
            with open(jsonl_file, "r") as f:
                first_line = f.readline().strip()
                if not first_line:
                    continue
                first_entry = json.loads(first_line)
                ts_str = first_entry.get("timestamp")
                if not ts_str:
                    continue
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                session_date = ts.date()
                if date_start <= session_date <= date_end:
                    filtered.append((project_name, jsonl_file))
        except (json.JSONDecodeError, OSError):
            continue

    return filtered


def extract_session_metadata(entries):
    """Extract session metadata from early entries."""
    meta = {
        "session_id": None,
        "cwd": None,
        "version": None,
        "git_branch": None,
        "timestamp": None,
    }
    for entry in entries[:10]:
        if meta["session_id"] is None and entry.get("sessionId"):
            meta["session_id"] = entry["sessionId"]
        if meta["cwd"] is None and entry.get("cwd"):
            meta["cwd"] = entry["cwd"]
        if meta["version"] is None and entry.get("version"):
            meta["version"] = entry["version"]
        if meta["git_branch"] is None and entry.get("gitBranch"):
            meta["git_branch"] = entry["gitBranch"]
        if meta["timestamp"] is None and entry.get("timestamp"):
            meta["timestamp"] = entry["timestamp"]
        if all(v is not None for v in meta.values()):
            break
    return meta


def extract_tool_actions(content_blocks):
    """Extract tool_use actions from assistant message content blocks."""
    actions = []
    for block in content_blocks:
        if block.get("type") != "tool_use":
            continue
        tool_name = block.get("name", "")
        inp = block.get("input", {})
        detail = ""

        if tool_name == "Write":
            detail = inp.get("file_path", "")
        elif tool_name == "Edit":
            detail = inp.get("file_path", "")
        elif tool_name == "Bash":
            cmd = inp.get("command", "")
            detail = cmd[:200]
        elif tool_name == "Task":
            detail = inp.get("description", "") or inp.get("prompt", "")[:100]
        elif tool_name == "AskUserQuestion":
            qs = inp.get("questions", [])
            detail = qs[0].get("question", "") if qs else ""
        elif tool_name == "Skill":
            detail = inp.get("skill", "")
        else:
            detail = str(inp)[:150]

        actions.append({"tool": tool_name, "detail": detail})
    return actions


def extract_thinking(content_blocks, max_len=500):
    """Extract thinking text from assistant message content blocks."""
    for block in content_blocks:
        if block.get("type") == "thinking":
            text = block.get("thinking", "")
            if len(text) > max_len:
                return text[:max_len] + "..."
            return text
    return ""


def classify_severity(actions_after):
    """Classify severity based on actions taken after empty answer."""
    if not actions_after:
        return "low", "No tool actions followed"

    tool_names = [a["tool"] for a in actions_after]
    has_write_edit = any(t in ("Write", "Edit") for t in tool_names)
    has_git_commit = any(
        t == "Bash" and "git commit" in a.get("detail", "")
        for t, a in zip(tool_names, actions_after)
    )
    has_task = any(t == "Task" for t in tool_names)
    has_cascading_ask = any(t == "AskUserQuestion" for t in tool_names)

    if has_write_edit and has_git_commit:
        return "critical", "Followed by Write/Edit + git commit"
    if has_write_edit:
        return "high", "Followed by Write/Edit"
    if has_task or has_cascading_ask:
        return "medium", "Followed by Task spawn or cascading AskUserQuestion"
    return "medium", "Followed by other tool use"


def find_next_assistant_message(entries, start_idx):
    """Find the next assistant message after the given index."""
    for i in range(start_idx + 1, min(start_idx + 20, len(entries))):
        entry = entries[i]
        if entry.get("type") == "assistant" and entry.get("message", {}).get("role") == "assistant":
            return entry, i
    return None, -1


def is_user_interruption(entries, empty_idx):
    """Check if user interrupted before Claude could act on the empty answer.

    Looks for a regular user message (not a tool_result) shortly after the empty response.
    """
    for i in range(empty_idx + 1, min(empty_idx + 5, len(entries))):
        entry = entries[i]
        if entry.get("type") == "user":
            msg = entry.get("message", {})
            content = msg.get("content", [])
            if isinstance(content, str):
                return True
            if isinstance(content, list):
                # tool_result = automated response, text = user interruption
                has_text = any(
                    b.get("type") == "text" for b in content if isinstance(b, dict)
                )
                has_only_tool_results = all(
                    b.get("type") == "tool_result" for b in content if isinstance(b, dict)
                )
                if has_text and not has_only_tool_results:
                    return True
        if entry.get("type") == "assistant":
            return False
    return False


def audit_session(entries):
    """Audit a single session's entries for AskUserQuestion empty-answer bug."""
    ask_calls = []
    empty_responses = []

    for idx, entry in enumerate(entries):
        # Find toolUseResult entries that are AskUserQuestion responses
        tur = entry.get("toolUseResult")
        if tur is None or not isinstance(tur, dict):
            continue
        if "questions" not in tur or "answers" not in tur:
            continue

        questions_raw = tur["questions"]
        answers = tur["answers"]
        timestamp = entry.get("timestamp", "")

        # Format questions for output
        questions_asked = []
        for q in questions_raw:
            options = [opt.get("label", "") for opt in q.get("options", [])]
            questions_asked.append({
                "question": q.get("question", ""),
                "options": options,
                "multi_select": q.get("multiSelect", False),
            })

        ask_calls.append({
            "timestamp": timestamp,
            "questions": questions_asked,
            "answers": answers,
            "empty": not answers,  # {} is falsy
        })

        if not answers:
            # Empty answer detected — find what Claude did next
            hallucinated = ""
            actions_after = []

            next_msg, next_idx = find_next_assistant_message(entries, idx)
            if next_msg:
                content_blocks = next_msg.get("message", {}).get("content", [])
                hallucinated = extract_thinking(content_blocks)
                actions_after = extract_tool_actions(content_blocks)

                # Also check subsequent assistant messages for multi-step responses
                # (Claude sometimes splits thinking and tool_use across messages)
                if not actions_after and next_idx > 0:
                    second_msg, _ = find_next_assistant_message(entries, next_idx)
                    if second_msg:
                        more_blocks = second_msg.get("message", {}).get("content", [])
                        actions_after = extract_tool_actions(more_blocks)

            # Check for user interruption
            if is_user_interruption(entries, idx):
                severity = "low"
                severity_reason = "User interrupted before actions taken"
            elif not actions_after:
                severity = "low"
                severity_reason = "No tool actions followed"
            else:
                severity, severity_reason = classify_severity(actions_after)

            empty_responses.append({
                "timestamp": timestamp,
                "questions_asked": questions_asked,
                "hallucinated_answer": hallucinated,
                "actions_after": actions_after,
                "severity": severity,
                "severity_reason": severity_reason,
            })

    return ask_calls, empty_responses


def main():
    args = parse_args()
    date_start, date_end = resolve_date_range(args)

    files = discover_jsonl_files(
        date_start, date_end, args.projects, args.include_subagents
    )

    if not files:
        date_desc = "all time" if args.all else f"{date_start} to {date_end}"
        result = {
            "metadata": {
                "scan_time": datetime.now(timezone.utc).isoformat(),
                "date_range": {"start": str(date_start), "end": str(date_end)},
                "sessions_scanned": 0,
                "total_ask_calls": 0,
                "total_empty": 0,
                "bug_rate_percent": 0,
            },
            "projects": [],
            "summary": {
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
            },
        }
        json.dump(result, sys.stdout, indent=2)
        return

    # Group files by project
    project_files = {}
    for project_name, jsonl_file in files:
        project_files.setdefault(project_name, []).append(jsonl_file)

    total_sessions = 0
    total_ask_calls = 0
    total_empty = 0
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    projects_output = []

    for project_name in sorted(project_files.keys()):
        sessions_output = []

        for jsonl_file in sorted(project_files[project_name]):
            # Parse all entries
            entries = []
            try:
                with open(jsonl_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                entries.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            except OSError:
                continue

            if not entries:
                continue

            meta = extract_session_metadata(entries)
            ask_calls, empty_responses = audit_session(entries)

            if not ask_calls:
                continue  # No AskUserQuestion calls in this session

            total_sessions += 1
            total_ask_calls += len(ask_calls)
            total_empty += len(empty_responses)

            for er in empty_responses:
                severity_counts[er["severity"]] += 1

            sessions_output.append({
                "session_id": meta["session_id"],
                "file_path": str(jsonl_file),
                "git_branch": meta["git_branch"],
                "session_start": meta["timestamp"],
                "total_ask_calls": len(ask_calls),
                "empty_count": len(empty_responses),
                "empty_responses": empty_responses,
            })

        if sessions_output:
            projects_output.append({
                "project_dir": project_name,
                "sessions": sessions_output,
            })

    bug_rate = (total_empty / total_ask_calls * 100) if total_ask_calls > 0 else 0

    result = {
        "metadata": {
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "date_range": {
                "start": str(date_start) if date_start else "all",
                "end": str(date_end) if date_end else "all",
            },
            "sessions_scanned": total_sessions,
            "total_ask_calls": total_ask_calls,
            "total_empty": total_empty,
            "bug_rate_percent": round(bug_rate, 1),
        },
        "projects": projects_output,
        "summary": {
            "critical_count": severity_counts["critical"],
            "high_count": severity_counts["high"],
            "medium_count": severity_counts["medium"],
            "low_count": severity_counts["low"],
        },
    }

    json.dump(result, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
