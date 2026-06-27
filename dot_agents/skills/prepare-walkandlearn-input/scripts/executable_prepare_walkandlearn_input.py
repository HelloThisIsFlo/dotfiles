#!/usr/bin/env python3
"""Prepare a WalkAndLearn LangGraph input from clipboard text."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_REPO = Path("/Users/flo/Work/Private/Dev/AI/Agents")
DEFAULT_MIN_BYTES = 2000
LANGGRAPH_OK_URL = "http://127.0.0.1:2024/ok"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a WalkAndLearn input file from the macOS clipboard."
    )
    parser.add_argument("--date", required=True, help="Session date as YYYY-MM-DD.")
    parser.add_argument("--topic", required=True, help="Topic words for filename slug.")
    parser.add_argument("--repo", default=str(DEFAULT_REPO), help="Agents repo path.")
    parser.add_argument(
        "--min-bytes",
        type=int,
        default=DEFAULT_MIN_BYTES,
        help="Minimum clipboard byte count required before writing.",
    )
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Do not start LangGraph when it is not already running.",
    )
    parser.add_argument(
        "--no-browser-focus",
        action="store_true",
        help="Accepted for caller workflows; this script does not focus browsers.",
    )
    return parser.parse_args()


def run_text_command(command: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        command,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{command[0]} failed: {detail}")
    return result.stdout


def read_clipboard() -> str:
    return run_text_command(["pbpaste"])


def copy_to_clipboard(text: str) -> None:
    run_text_command(["pbcopy"], input_text=text)


def validate_date(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("--date must use YYYY-MM-DD")
    return value


def slugify(topic: str) -> str:
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if not slug:
        raise ValueError("--topic must contain at least one ASCII letter or digit")
    return slug


def next_available_path(input_dir: Path, date: str, slug: str) -> Path:
    base = f"input-{date}-{slug}"
    candidate = input_dir / f"{base}.md"
    suffix = 2
    while candidate.exists():
        candidate = input_dir / f"{base}-{suffix}.md"
        suffix += 1
    return candidate


def langgraph_status() -> str:
    try:
        with urllib.request.urlopen(LANGGRAPH_OK_URL, timeout=1) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError:
        return "down"

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return "conflict"

    return "running" if payload.get("ok") is True else "conflict"


def wait_for_langgraph(timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status = langgraph_status()
        if status == "running":
            return
        if status == "conflict":
            raise RuntimeError(f"{LANGGRAPH_OK_URL} responded but is not LangGraph")
        time.sleep(1)
    raise TimeoutError("Timed out waiting for LangGraph dev server")


def start_langgraph(repo: Path) -> None:
    log_dir = Path.home() / "Library" / "Logs" / "prepare-walkandlearn-input"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "langgraph-dev.log"
    log_handle = log_file.open("ab")
    subprocess.Popen(
        ["uv", "run", "langgraph", "dev"],
        cwd=repo,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def verify_ignored(repo: Path, generated_path: Path) -> str:
    rel_path = generated_path.relative_to(repo)
    result = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "-v", str(rel_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Generated file is not ignored by git: {rel_path}")
    return result.stdout.strip()


def main() -> int:
    args = parse_args()

    try:
        repo = Path(args.repo).expanduser().resolve()
        input_dir = repo / "agent_files" / "walkandlearn_summary"
        if not input_dir.is_dir():
            raise FileNotFoundError(f"Missing input directory: {input_dir}")

        date = validate_date(args.date)
        slug = slugify(args.topic)
        clipboard = read_clipboard()
        byte_count = len(clipboard.encode("utf-8"))
        if byte_count < args.min_bytes:
            raise ValueError(
                f"Clipboard is too short: {byte_count} bytes "
                f"(minimum {args.min_bytes})"
            )

        output_path = next_available_path(input_dir, date, slug)
        output_path.write_text(clipboard, encoding="utf-8")
        ignored_by = verify_ignored(repo, output_path)

        state = {"messages": [], "input_filename": output_path.name}
        state_json = json.dumps(state, indent=2)
        copy_to_clipboard(state_json)

        status = langgraph_status()
        if status == "conflict":
            raise RuntimeError(f"{LANGGRAPH_OK_URL} is occupied by a non-LangGraph server")
        if status == "down" and not args.no_launch:
            start_langgraph(repo)
            wait_for_langgraph()
            status = "started"
        elif status == "down":
            status = "not running"

        print(f"file: {output_path}")
        print(f"bytes: {byte_count}")
        print(f"lines: {clipboard.count(chr(10)) + 1}")
        print(f"ignored_by: {ignored_by}")
        print(f"langgraph: {status}")
        print("state:")
        print(state_json)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
