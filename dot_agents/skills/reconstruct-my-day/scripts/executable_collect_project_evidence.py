#!/usr/bin/env python3
"""Collect bounded, read-only Git and filesystem evidence for one local day."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import selectors
import signal
import subprocess
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SCHEMA_VERSION = 1
SENTINEL = "RECONSTRUCT_LOCAL_EVIDENCE_COMPLETE"
DEFAULT_MAX_ROOTS = 12
DEFAULT_MAX_COMMITS = 100
DEFAULT_MAX_FILES = 100
DEFAULT_MAX_VISITED = 25_000
DEFAULT_MAX_DEPTH = 8
DEFAULT_TIMEOUT_SECONDS = 8.0
MAX_COMMAND_OUTPUT_BYTES = 2_000_000
MAX_GIT_PATHS_VISITED = 25_000

PRUNED_DIRECTORIES = {
    ".cache",
    ".git",
    ".gradle",
    ".idea",
    ".mypy_cache",
    ".next",
    ".npm",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "DerivedData",
    "dist",
    "logs",
    "node_modules",
    "Pods",
    "target",
    "tmp",
    "venv",
}

IGNORED_FILES = {
    ".DS_Store",
    "Thumbs.db",
}

IGNORED_SUFFIXES = {
    ".bak",
    ".log",
    ".pyc",
    ".swp",
    ".temp",
    ".tmp",
}


@dataclass(frozen=True)
class DayWindow:
    date: dt.date
    timezone: str
    start: dt.datetime
    end: dt.datetime

    def contains(self, value: dt.datetime) -> bool:
        return self.start <= value.astimezone(self.start.tzinfo) < self.end


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect bounded Git commits and metadata-only file evidence for one "
            "local calendar day."
        )
    )
    parser.add_argument("--date", required=True, help="Target date as YYYY-MM-DD")
    parser.add_argument(
        "--timezone",
        required=True,
        help="IANA timezone such as Europe/London",
    )
    parser.add_argument(
        "--root",
        action="append",
        required=True,
        help="Trusted project working directory; repeat for multiple roots",
    )
    parser.add_argument("--max-roots", type=int, default=DEFAULT_MAX_ROOTS)
    parser.add_argument("--max-commits", type=int, default=DEFAULT_MAX_COMMITS)
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument("--max-visited", type=int, default=DEFAULT_MAX_VISITED)
    parser.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH)
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    args = parser.parse_args(argv)

    for name in (
        "max_roots",
        "max_commits",
        "max_files",
        "max_visited",
        "max_depth",
    ):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")

    return args


def build_day_window(date_value: str | dt.date, timezone: str) -> DayWindow:
    if isinstance(date_value, str):
        target_date = dt.date.fromisoformat(date_value)
    else:
        target_date = date_value

    zone = ZoneInfo(timezone)
    start = dt.datetime.combine(target_date, dt.time.min, tzinfo=zone)
    end = dt.datetime.combine(
        target_date + dt.timedelta(days=1),
        dt.time.min,
        tzinfo=zone,
    )
    return DayWindow(target_date, timezone, start, end)


def public_command_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": result["state"],
        "exit_code": result["exit_code"],
        "error": result["error"],
    }


def run_command(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_output_bytes: int = MAX_COMMAND_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Run a read-only command with hard time and output bounds."""
    environment = {
        key: os.environ[key]
        for key in ("HOME", "LANG", "LC_ALL", "LC_CTYPE", "PATH", "TMPDIR")
        if key in os.environ
    }
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = "/dev/null"
    environment["GIT_ATTR_NOSYSTEM"] = "1"
    environment["GIT_TERMINAL_PROMPT"] = "0"
    environment["GIT_NO_LAZY_FETCH"] = "1"
    environment["GIT_PROTOCOL_FROM_USER"] = "0"
    environment["GCM_INTERACTIVE"] = "Never"
    environment["GIT_PAGER"] = "cat"
    environment["PAGER"] = "cat"
    started = time.monotonic()

    try:
        process = subprocess.Popen(
            args,
            cwd=str(cwd) if cwd else None,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            env=environment,
        )
    except FileNotFoundError:
        return {
            "state": "unavailable",
            "exit_code": None,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "stdout": "",
            "error": f"command not found: {args[0]}",
        }
    except OSError as exc:
        return {
            "state": "error",
            "exit_code": None,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "stdout": "",
            "error": str(exc),
        }

    assert process.stdout and process.stderr
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    deadline = started + timeout
    terminal_state: str | None = None

    while selector.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            terminal_state = "timeout"
            break
        events = selector.select(remaining)
        if not events:
            terminal_state = "timeout"
            break

        for key, _ in events:
            try:
                chunk = os.read(key.fd, 65_536)
            except OSError:
                chunk = b""
            if not chunk:
                selector.unregister(key.fileobj)
                continue
            buffers[key.data].extend(chunk)
            if sum(len(buffer) for buffer in buffers.values()) > max_output_bytes:
                terminal_state = "limit"
                break
        if terminal_state:
            break

    selector.close()
    process.stdout.close()
    process.stderr.close()

    if terminal_state:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=1)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        reason = (
            f"timed out after {timeout:g}s"
            if terminal_state == "timeout"
            else f"output limit reached ({max_output_bytes} bytes)"
        )
        return {
            "state": terminal_state,
            "exit_code": process.returncode,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "stdout": "",
            "error": reason,
        }

    try:
        process.wait(timeout=max(0.1, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        return {
            "state": "timeout",
            "exit_code": process.returncode,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "stdout": "",
            "error": f"timed out after {timeout:g}s",
        }

    stdout = bytes(buffers["stdout"]).decode("utf-8", errors="replace")
    stderr = bytes(buffers["stderr"]).decode("utf-8", errors="replace")
    state = "ok" if process.returncode == 0 else "error"
    return {
        "state": state,
        "exit_code": process.returncode,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "stdout": stdout,
        "error": stderr.strip() if process.returncode else "",
    }


def git_command(root: Path, *args: str) -> list[str]:
    """Build a Git command that cannot invoke configured hooks or fsmonitor."""
    return [
        "git",
        "--no-pager",
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "core.untrackedCache=false",
        "-C",
        str(root),
        *args,
    ]


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def unsafe_root_reason(path: Path, home: Path | None = None) -> str | None:
    """Reject broad, system, cache, and credential-bearing roots."""
    home = (home or Path.home()).resolve()
    exact_broad_roots = {
        Path("/"),
        Path("/Users"),
        Path("/Volumes"),
        home,
        home / ".agents",
        home / ".cache",
        home / ".claude",
        home / ".codex",
        home / ".config",
        home / ".local",
        home / "Documents",
        home / "Work",
    }
    if path in exact_broad_roots:
        return "root is too broad"

    blocked_subtrees = {
        Path("/Applications"),
        Path("/bin"),
        Path("/dev"),
        Path("/etc"),
        Path("/Library"),
        Path("/opt"),
        Path("/proc"),
        Path("/run"),
        Path("/sbin"),
        Path("/sys"),
        Path("/System"),
        Path("/usr"),
        Path("/private"),
        Path("/tmp"),
        Path("/var"),
        home / ".aws",
        home / ".cache",
        home / ".config",
        home / ".config" / "gcloud",
        home / ".gnupg",
        home / ".local" / "share" / "Trash",
        home / ".npm",
        home / ".ssh",
        home / ".Trash",
        home / "Library",
    }
    for blocked in blocked_subtrees:
        if path == blocked or is_within(path, blocked):
            return f"root is inside blocked subtree {blocked}"

    return None


def detect_git_root(path: Path, timeout: float) -> tuple[Path | None, dict[str, Any]]:
    probe = run_command(
        git_command(path, "rev-parse", "--show-toplevel"),
        timeout=timeout,
    )
    if probe["state"] == "ok":
        output = probe["stdout"].strip()
        if output:
            try:
                return Path(output).expanduser().resolve(strict=True), probe
            except (OSError, RuntimeError):
                return None, {
                    **probe,
                    "state": "error",
                    "error": f"Git returned an unreadable root: {output}",
                }
    return None, probe


def prepare_roots(
    requested_roots: Iterable[str],
    *,
    max_roots: int,
    timeout: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for raw_root in requested_roots:
        requested = str(Path(raw_root).expanduser())
        try:
            resolved = Path(raw_root).expanduser().resolve(strict=True)
        except (FileNotFoundError, OSError, RuntimeError) as exc:
            skipped.append(
                {
                    "requested_root": requested,
                    "status": "skipped",
                    "reason": f"unreadable or missing root: {exc}",
                }
            )
            continue

        if not resolved.is_dir():
            skipped.append(
                {
                    "requested_root": requested,
                    "resolved_root": str(resolved),
                    "status": "skipped",
                    "reason": "root is not a directory",
                }
            )
            continue

        reason = unsafe_root_reason(resolved)
        if reason:
            skipped.append(
                {
                    "requested_root": requested,
                    "resolved_root": str(resolved),
                    "status": "skipped",
                    "reason": reason,
                }
            )
            continue

        git_root, git_probe = detect_git_root(resolved, timeout)
        if git_root and resolved != git_root and not is_within(resolved, git_root):
            skipped.append(
                {
                    "requested_root": requested,
                    "resolved_root": str(resolved),
                    "status": "skipped",
                    "reason": (
                        "detected Git worktree does not contain the requested root"
                    ),
                }
            )
            continue
        kind = "git" if git_root else "filesystem"
        collection_root = git_root or resolved

        reason = unsafe_root_reason(collection_root)
        if reason:
            skipped.append(
                {
                    "requested_root": requested,
                    "resolved_root": str(collection_root),
                    "status": "skipped",
                    "reason": reason,
                }
            )
            continue

        identity = (kind, str(collection_root))
        if identity in seen:
            skipped.append(
                {
                    "requested_root": requested,
                    "resolved_root": str(collection_root),
                    "status": "skipped",
                    "reason": "duplicate canonical root",
                }
            )
            continue

        if len(accepted) >= max_roots:
            skipped.append(
                {
                    "requested_root": requested,
                    "resolved_root": str(collection_root),
                    "status": "skipped",
                    "reason": f"root limit reached ({max_roots})",
                }
            )
            continue

        seen.add(identity)
        entry = {
            "requested_root": requested,
            "resolved_root": str(collection_root),
            "kind": kind,
        }
        if kind == "filesystem" and git_probe["state"] not in {"ok", "error"}:
            entry["git_detection"] = public_command_result(git_probe)
        accepted.append(entry)

    return accepted, skipped


def parse_iso_datetime(value: str) -> dt.datetime | None:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def collect_commits(
    root: Path,
    window: DayWindow,
    *,
    max_commits: int,
    timeout: float,
) -> tuple[list[dict[str, Any]], bool, list[dict[str, Any]]]:
    result = run_command(
        git_command(
            root,
            "log",
            "--all",
            f"--since-as-filter={window.start.isoformat()}",
            f"--until={window.end.isoformat()}",
            f"--max-count={max_commits + 1}",
            "--format=%H%x1f%aI%x1f%cI%x1f%s%x1e",
            "--no-show-signature",
        ),
        timeout=timeout,
    )
    if result["state"] != "ok":
        return [], False, [public_command_result(result)]

    parsed_commits: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for raw_record in result["stdout"].split("\x1e"):
        record = raw_record.strip()
        if not record:
            continue
        fields = record.split("\x1f", 3)
        if len(fields) != 4:
            errors.append(
                {
                    "state": "error",
                    "exit_code": None,
                    "error": "could not parse one git log record",
                }
            )
            continue

        commit_hash, authored_at, committed_at, subject = fields
        committed = parse_iso_datetime(committed_at)
        if committed is None or not window.contains(committed):
            continue

        commit: dict[str, Any] = {
            "hash": commit_hash,
            "authored_at": authored_at,
            "committed_at": committed_at,
            "subject": subject,
            "evidence_scope": "confirms an outcome, not attention or authorship",
            "_committed_instant": committed.timestamp(),
        }
        parsed_commits.append(commit)

    parsed_commits.sort(key=lambda item: item["_committed_instant"])
    for commit in parsed_commits:
        commit.pop("_committed_instant", None)
    truncated = len(parsed_commits) > max_commits
    return parsed_commits[:max_commits], truncated, errors


def git_path_sets(
    root: Path,
    *,
    timeout: float,
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    commands = {
        "tracked": git_command(
            root,
            "ls-files",
            "--cached",
            "-z",
        ),
        "untracked": git_command(
            root,
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
        ),
    }
    paths: dict[str, set[str]] = {}
    errors: list[dict[str, Any]] = []
    command_timeout = max(0.05, timeout / len(commands))
    for state, command in commands.items():
        result = run_command(command, timeout=command_timeout)
        if result["state"] != "ok":
            errors.append(public_command_result(result))
            continue
        for path in result["stdout"].split("\0"):
            if path:
                paths.setdefault(path, set()).add(state)
    return paths, errors


def safe_repo_path(root: Path, relative_path: str) -> Path | None:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    candidate = root / relative
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def lstat_repo_path(root: Path, relative_path: str) -> os.stat_result | None:
    """Read metadata without following any symlinked path component."""
    candidate = safe_repo_path(root, relative_path)
    if candidate is None:
        return None

    parts = Path(relative_path).parts
    if not parts:
        return None

    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptors: list[int] = []
    try:
        descriptors.append(os.open(root, directory_flags))
        for part in parts[:-1]:
            descriptors.append(
                os.open(
                    part,
                    directory_flags,
                    dir_fd=descriptors[-1],
                )
            )
        return os.stat(
            parts[-1],
            dir_fd=descriptors[-1],
            follow_symlinks=False,
        )
    except OSError:
        return None
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def collect_dirty_files(
    root: Path,
    window: DayWindow,
    *,
    max_files: int,
    timeout: float,
) -> tuple[list[dict[str, Any]], bool, list[dict[str, Any]]]:
    started = time.monotonic()
    path_states, errors = git_path_sets(
        root,
        timeout=max(0.05, timeout * 0.4),
    )
    matches: list[dict[str, Any]] = []
    paths_visited = 0
    truncated = False

    for relative_path, states in path_states.items():
        if time.monotonic() - started >= timeout:
            errors.append(
                {
                    "state": "timeout",
                    "exit_code": None,
                    "error": f"worktree metadata timed out after {timeout:g}s",
                }
            )
            truncated = True
            break
        if paths_visited >= MAX_GIT_PATHS_VISITED:
            errors.append(
                {
                    "state": "limit",
                    "exit_code": None,
                    "error": (
                        "worktree path visit limit reached "
                        f"({MAX_GIT_PATHS_VISITED})"
                    ),
                }
            )
            truncated = True
            break
        paths_visited += 1

        stat = lstat_repo_path(root, relative_path)
        if stat is None:
            continue
        observed_at = dt.datetime.fromtimestamp(
            stat.st_mtime,
            tz=window.start.tzinfo,
        )
        if not window.contains(observed_at):
            continue
        matches.append(
            {
                "path": relative_path,
                "observed_at": observed_at.isoformat(),
                "size_bytes": stat.st_size,
                "states": sorted(states),
                "evidence_scope": "tentative current mtime corroboration only",
            }
        )
        if len(matches) >= max_files:
            truncated = True
            break

    matches.sort(key=lambda item: (item["observed_at"], item["path"]))
    return matches, truncated, errors


def collect_git_root(
    root_entry: dict[str, Any],
    window: DayWindow,
    *,
    max_commits: int,
    max_files: int,
    timeout: float,
) -> dict[str, Any]:
    root = Path(root_entry["resolved_root"])
    phase_timeout = max(0.1, timeout / 2)
    commits, commits_truncated, commit_errors = collect_commits(
        root,
        window,
        max_commits=max_commits,
        timeout=phase_timeout,
    )
    files, files_truncated, file_errors = collect_dirty_files(
        root,
        window,
        max_files=max_files,
        timeout=phase_timeout,
    )
    errors = commit_errors + file_errors
    return {
        **root_entry,
        "status": "partial" if errors or commits_truncated or files_truncated else "ok",
        "commits": commits,
        "commits_truncated": commits_truncated,
        "working_tree_files": files,
        "working_tree_files_truncated": files_truncated,
        "errors": errors,
    }


def should_ignore_file(path: Path) -> bool:
    return path.name in IGNORED_FILES or path.suffix.lower() in IGNORED_SUFFIXES


def collect_filesystem_root(
    root_entry: dict[str, Any],
    window: DayWindow,
    *,
    max_files: int,
    max_visited: int,
    max_depth: int,
    timeout: float,
) -> dict[str, Any]:
    root = Path(root_entry["resolved_root"])
    matches: list[dict[str, Any]] = []
    files_visited = 0
    directories_visited = 0
    entries_visited = 0
    stop_reason: str | None = None
    depth_limited = False
    scan_errors: list[dict[str, Any]] = []
    started = time.monotonic()

    try:
        root_device = root.stat().st_dev
    except OSError as exc:
        return {
            **root_entry,
            "status": "error",
            "files": [],
            "files_visited": 0,
            "directories_visited": 0,
            "truncated": False,
            "errors": [{"error": str(exc)}],
        }

    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        if time.monotonic() - started >= timeout:
            stop_reason = f"time limit reached ({timeout:g}s)"
            break
        if entries_visited >= max_visited:
            stop_reason = f"entry visit limit reached ({max_visited})"
            break

        current, depth = stack.pop()
        directories_visited += 1
        entries_visited += 1
        child_directories: list[Path] = []

        try:
            with os.scandir(current) as entries:
                iterator = iter(entries)
                while True:
                    if time.monotonic() - started >= timeout:
                        stop_reason = f"time limit reached ({timeout:g}s)"
                        break
                    if entries_visited >= max_visited:
                        stop_reason = (
                            f"entry visit limit reached ({max_visited})"
                        )
                        break
                    try:
                        entry = next(iterator)
                    except StopIteration:
                        break
                    entries_visited += 1

                    if entry.name in PRUNED_DIRECTORIES or entry.is_symlink():
                        continue
                    try:
                        stat = entry.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if stat.st_dev != root_device:
                        continue

                    if entry.is_dir(follow_symlinks=False):
                        if depth < max_depth:
                            child_directories.append(Path(entry.path))
                        else:
                            depth_limited = True
                        continue

                    files_visited += 1
                    path = Path(entry.path)
                    if should_ignore_file(path):
                        continue
                    observed_at = dt.datetime.fromtimestamp(
                        stat.st_mtime,
                        tz=window.start.tzinfo,
                    )
                    if not window.contains(observed_at):
                        continue
                    matches.append(
                        {
                            "path": str(path.relative_to(root)),
                            "observed_at": observed_at.isoformat(),
                            "size_bytes": stat.st_size,
                            "evidence_scope": (
                                "tentative filesystem mtime corroboration only"
                            ),
                        }
                    )
                    if len(matches) >= max_files:
                        stop_reason = f"match limit reached ({max_files})"
                        break
        except OSError as exc:
            if len(scan_errors) < 10:
                scan_errors.append(
                    {
                        "path": str(current.relative_to(root)),
                        "error": str(exc),
                    }
                )

        if stop_reason:
            break
        stack.extend(reversed(child_directories))

    matches.sort(key=lambda item: (item["observed_at"], item["path"]))
    errors: list[dict[str, Any]] = scan_errors
    if "git_detection" in root_entry:
        errors.append(root_entry["git_detection"])
    return {
        **root_entry,
        "status": "partial" if stop_reason or depth_limited or errors else "ok",
        "files": matches,
        "files_visited": files_visited,
        "directories_visited": directories_visited,
        "entries_visited": entries_visited,
        "truncated": bool(stop_reason or depth_limited),
        "stop_reason": stop_reason,
        "depth_limited": depth_limited,
        "errors": errors,
    }


def derive_source_status(
    roots: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
) -> str:
    if not roots:
        return "unavailable"

    substantive_skips = [
        entry
        for entry in skipped
        if entry.get("reason") != "duplicate canonical root"
    ]
    if substantive_skips or any(root["status"] != "ok" for root in roots):
        return "partial"
    return "ok"


def collect(args: argparse.Namespace) -> dict[str, Any]:
    window = build_day_window(args.date, args.timezone)
    accepted, skipped = prepare_roots(
        args.root,
        max_roots=args.max_roots,
        timeout=args.timeout_seconds,
    )
    collected_roots: list[dict[str, Any]] = []

    for root_entry in accepted:
        if root_entry["kind"] == "git":
            result = collect_git_root(
                root_entry,
                window,
                max_commits=args.max_commits,
                max_files=args.max_files,
                timeout=args.timeout_seconds,
            )
        else:
            result = collect_filesystem_root(
                root_entry,
                window,
                max_files=args.max_files,
                max_visited=args.max_visited,
                max_depth=args.max_depth,
                timeout=args.timeout_seconds,
            )
        collected_roots.append(result)

    commit_count = sum(len(root.get("commits", [])) for root in collected_roots)
    file_count = sum(
        len(root.get("working_tree_files", [])) + len(root.get("files", []))
        for root in collected_roots
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "source_status": derive_source_status(collected_roots, skipped),
        "window": {
            "date": window.date.isoformat(),
            "timezone": window.timezone,
            "start": window.start.isoformat(),
            "end": window.end.isoformat(),
        },
        "limits": {
            "max_roots": args.max_roots,
            "max_commits_per_root": args.max_commits,
            "max_files_per_root": args.max_files,
            "max_git_paths_visited_per_root": MAX_GIT_PATHS_VISITED,
            "max_entries_visited_per_non_git_root": args.max_visited,
            "max_depth_for_non_git_roots": args.max_depth,
            "timeout_seconds_per_operation": args.timeout_seconds,
        },
        "summary": {
            "candidate_roots": len(args.root),
            "accepted_roots": len(collected_roots),
            "skipped_roots": len(skipped),
            "commits": commit_count,
            "files": file_count,
        },
        "roots": collected_roots,
        "skipped_roots": skipped,
        "limitations": [
            "Commits confirm outcomes, not attention or authorship.",
            "Current mtimes are tentative and cannot recover later-replaced historical state.",
            (
                "Candidate work-file contents were not read; Git may read its "
                "index, ignore rules, and commit metadata."
            ),
        ],
    }


def emit(payload: dict[str, Any]) -> None:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    print(encoded.decode("utf-8"))
    print(f"{SENTINEL} sha256={hashlib.sha256(encoded).hexdigest()}")


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        payload = collect(args)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001  # pragma: no cover
        payload = {
            "schema_version": SCHEMA_VERSION,
            "source_status": "unavailable",
            "fatal_error": f"{type(exc).__name__}: {exc}",
        }
        emit(payload)
        return 1

    emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
