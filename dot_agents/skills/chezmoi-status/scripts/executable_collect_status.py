#!/usr/bin/env python3
"""Collect a compact, read-only, evidence-backed chezmoi status snapshot."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 2
SENTINEL = "CHEZMOI_STATUS_COMPLETE"
COMPLEX_LINE_THRESHOLD = 50
COMPLEX_SIZE_THRESHOLD = 50_000
MAX_PATHS = 100


def run_command(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Run a command to a real exit, killing its process group on timeout."""
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            args,
            cwd=str(cwd) if cwd else None,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
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

    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=2)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
        return {
            "state": "timeout",
            "exit_code": process.returncode,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "stdout": "",
            "error": f"timed out after {timeout:g}s",
        }

    state = "ok" if process.returncode == 0 else "error"
    return {
        "state": state,
        "exit_code": process.returncode,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "stdout": stdout,
        "error": "" if state == "ok" else summarize_error(stderr),
    }


def summarize_error(stderr: str) -> str:
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    if not lines:
        return "command failed without an error message"
    return lines[-1][:300]


def public_probe(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": result["state"],
        "exit_code": result["exit_code"],
        "duration_ms": result["duration_ms"],
        "error": result["error"],
    }


def parse_chezmoi_status(stdout: str) -> tuple[list[dict[str, str]], str | None]:
    entries: list[dict[str, str]] = []
    pattern = re.compile(r"^([ ADMR]{2}) (.+)$")
    for line in stdout.splitlines():
        if not line.strip():
            continue
        match = pattern.match(line)
        if not match:
            return [], f"unrecognized chezmoi status line: {line[:120]}"
        entries.append({"code": match.group(1), "path": match.group(2)})
    return entries, None


def summarize_managed(
    entries: list[dict[str, str]],
    *,
    coverage: str,
    full_probe: dict[str, Any],
    fallback_probe: dict[str, Any] | None,
) -> dict[str, Any]:
    counts = collections.Counter(entry["code"] for entry in entries)
    target_changed = [e for e in entries if e["code"][0] != " "]
    apply_ready = [e for e in entries if e["code"][0] == " " and e["code"][1] != " "]
    two_sided = [e for e in entries if e["code"][0] != " " and e["code"][1] != " "]
    return {
        "coverage": coverage,
        "templates": "verified" if coverage == "full" else "unknown",
        "entry_count": len(entries),
        "counts_by_code": dict(sorted(counts.items())),
        "target_changed": target_changed[:MAX_PATHS],
        "apply_ready": apply_ready[:MAX_PATHS],
        "two_sided": two_sided[:MAX_PATHS],
        "entries": entries[:MAX_PATHS],
        "truncated": len(entries) > MAX_PATHS,
        "full_probe": public_probe(full_probe),
        "fallback_probe": public_probe(fallback_probe) if fallback_probe else None,
    }


def collect_managed(timeout: float, fallback_timeout: float) -> dict[str, Any]:
    full = run_command(["chezmoi", "--no-tty", "--no-pager", "status"], timeout=timeout)
    if full["state"] == "ok":
        entries, parse_error = parse_chezmoi_status(full["stdout"])
        if parse_error is None:
            return summarize_managed(
                entries, coverage="full", full_probe=full, fallback_probe=None
            )
        full = {**full, "state": "error", "error": parse_error}

    fallback = run_command(
        [
            "chezmoi",
            "--no-tty",
            "--no-pager",
            "status",
            "--exclude=templates",
        ],
        timeout=fallback_timeout,
    )
    if fallback["state"] == "ok":
        entries, parse_error = parse_chezmoi_status(fallback["stdout"])
        if parse_error is None:
            return summarize_managed(
                entries,
                coverage="non_templates",
                full_probe=full,
                fallback_probe=fallback,
            )
        fallback = {**fallback, "state": "error", "error": parse_error}

    return {
        "coverage": "none",
        "templates": "unknown",
        "entry_count": 0,
        "counts_by_code": {},
        "target_changed": [],
        "apply_ready": [],
        "two_sided": [],
        "entries": [],
        "truncated": False,
        "full_probe": public_probe(full),
        "fallback_probe": public_probe(fallback),
    }


def parse_git_status(stdout: str) -> dict[str, Any]:
    branch = None
    upstream = None
    ahead = 0
    behind = 0
    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []
    conflicts: list[str] = []

    for line in stdout.splitlines():
        if line.startswith("# branch.head "):
            branch = line.removeprefix("# branch.head ")
        elif line.startswith("# branch.upstream "):
            upstream = line.removeprefix("# branch.upstream ")
        elif line.startswith("# branch.ab "):
            match = re.search(r"\+(\d+) -(\d+)", line)
            if match:
                ahead, behind = int(match.group(1)), int(match.group(2))
        elif line.startswith("? "):
            untracked.append(line[2:])
        elif line.startswith("u "):
            fields = line.split(" ", 10)
            if len(fields) == 11:
                conflicts.append(fields[10])
        elif line.startswith("1 "):
            fields = line.split(" ", 8)
            if len(fields) == 9:
                add_xy_path(fields[1], fields[8], staged, unstaged, conflicts)
        elif line.startswith("2 "):
            fields = line.split(" ", 9)
            if len(fields) == 10:
                path = fields[9].split("\t", 1)[0]
                add_xy_path(fields[1], path, staged, unstaged, conflicts)

    return {
        "branch": branch,
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
        "staged": sorted(set(staged)),
        "unstaged": sorted(set(unstaged)),
        "untracked": sorted(set(untracked)),
        "conflicts": sorted(set(conflicts)),
    }


def add_xy_path(
    xy: str,
    path: str,
    staged: list[str],
    unstaged: list[str],
    conflicts: list[str],
) -> None:
    if len(xy) != 2:
        return
    if "U" in xy or xy in {"AA", "DD"}:
        conflicts.append(path)
    if xy[0] != ".":
        staged.append(path)
    if xy[1] != ".":
        unstaged.append(path)


def parse_numstat(stdout: str, bucket: dict[str, dict[str, Any]]) -> None:
    for line in stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        record = bucket.setdefault(path, {"added": 0, "deleted": 0, "binary": False})
        if added == "-" or deleted == "-":
            record["binary"] = True
        else:
            record["added"] += int(added)
            record["deleted"] += int(deleted)


def theme_for_path(path: str) -> str:
    parts = Path(path).parts
    if path.startswith(".research/cheatsheets/") and len(parts) >= 3:
        return f"cheatsheets/{parts[2]}"
    if path.startswith("dot_agents/skills/") and len(parts) >= 3:
        return f"agent-skill/{parts[2]}"
    if path.startswith("dot_claude/skills/"):
        return "agent-adapters"
    if path.startswith(".research/"):
        return "research"
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0] if parts else "other"


def collect_git(source_root: Path) -> dict[str, Any]:
    status = run_command(
        [
            "git",
            "-C",
            str(source_root),
            "status",
            "--porcelain=v2",
            "--branch",
            "--untracked-files=all",
        ],
        timeout=10,
    )
    if status["state"] != "ok":
        return {"probe": public_probe(status), "available": False}

    parsed = parse_git_status(status["stdout"])
    numstats: dict[str, dict[str, Any]] = {}
    unstaged_stat = run_command(
        ["git", "-C", str(source_root), "diff", "--numstat", "--"], timeout=10
    )
    staged_stat = run_command(
        ["git", "-C", str(source_root), "diff", "--cached", "--numstat", "--"],
        timeout=10,
    )
    if unstaged_stat["state"] == "ok":
        parse_numstat(unstaged_stat["stdout"], numstats)
    if staged_stat["state"] == "ok":
        parse_numstat(staged_stat["stdout"], numstats)

    dirty_paths = sorted(
        set(parsed["staged"] + parsed["unstaged"] + parsed["untracked"])
    )
    complex_paths: list[str] = []
    for path, record in numstats.items():
        if (
            record["binary"]
            or record["added"] + record["deleted"] >= COMPLEX_LINE_THRESHOLD
        ):
            complex_paths.append(path)
    for path in parsed["untracked"]:
        try:
            if (source_root / path).stat().st_size >= COMPLEX_SIZE_THRESHOLD:
                complex_paths.append(path)
        except OSError:
            pass

    themes: dict[str, list[str]] = collections.defaultdict(list)
    for path in dirty_paths:
        themes[theme_for_path(path)].append(path)

    return {
        **parsed,
        "available": True,
        "dirty_count": len(dirty_paths),
        "dirty_paths": dirty_paths[:MAX_PATHS],
        "numstat": dict(sorted(numstats.items())),
        "complex_paths": sorted(set(complex_paths))[:MAX_PATHS],
        "themes": dict(sorted(themes.items())),
        "probe": public_probe(status),
        "numstat_probes": {
            "unstaged": public_probe(unstaged_stat),
            "staged": public_probe(staged_stat),
        },
    }


def clean_relative_paths(stdout: str) -> set[str]:
    paths: set[str] = set()
    for line in stdout.splitlines():
        path = line.strip()
        if not path:
            continue
        if path.startswith("./"):
            path = path[2:]
        paths.add(path)
    return paths


def has_prefix(paths: Iterable[str], prefix: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for path in paths)


def collect_agents(home: Path, managed_entries: list[dict[str, str]]) -> dict[str, Any]:
    managed_probe = run_command(
        ["chezmoi", "managed", "--include=files,symlinks"], timeout=10
    )
    unmanaged_probe = run_command(
        ["chezmoi", "unmanaged", str(home / ".agents" / "skills")], timeout=10
    )
    probes = {
        "managed": public_probe(managed_probe),
        "unmanaged": public_probe(unmanaged_probe),
    }
    if managed_probe["state"] != "ok" or unmanaged_probe["state"] != "ok":
        return {
            "coverage": "none",
            "managed_count": None,
            "ignored_external_count": None,
            "unmanaged": [],
            "broken_claude_adapters": [],
            "drifted_managed_skills": [],
            "probes": probes,
        }

    managed = (
        clean_relative_paths(managed_probe["stdout"])
        if managed_probe["state"] == "ok"
        else set()
    )
    unmanaged = (
        clean_relative_paths(unmanaged_probe["stdout"])
        if unmanaged_probe["state"] == "ok"
        else set()
    )

    root = home / ".agents" / "skills"
    skill_dirs = (
        sorted(path for path in root.iterdir() if path.is_dir())
        if root.is_dir()
        else []
    )
    managed_skills: list[str] = []
    ignored_skills: list[str] = []
    unmanaged_skills: list[str] = []
    broken_adapters: list[str] = []

    for skill_dir in skill_dirs:
        name = skill_dir.name
        prefix = f".agents/skills/{name}"
        if has_prefix(managed, prefix):
            managed_skills.append(name)
            adapter = home / ".claude" / "skills" / name
            adapter_prefix = f".claude/skills/{name}"
            live_ok = adapter.is_symlink() and adapter.resolve(
                strict=False
            ) == skill_dir.resolve(strict=False)
            source_ok = has_prefix(managed, adapter_prefix)
            if not live_ok or not source_ok:
                broken_adapters.append(name)
        elif has_prefix(unmanaged, prefix):
            unmanaged_skills.append(name)
        else:
            # Present but neither managed nor reported as unmanaged means an
            # ignore rule intentionally owns this external/plugin asset.
            ignored_skills.append(name)

    drift_skills = sorted(
        {
            entry["path"].split("/")[2]
            for entry in managed_entries
            if entry["path"].startswith(".agents/skills/")
            and len(entry["path"].split("/")) >= 3
        }
    )
    return {
        "coverage": "full",
        "managed_count": len(managed_skills),
        "ignored_external_count": len(ignored_skills),
        "unmanaged": unmanaged_skills[:MAX_PATHS],
        "broken_claude_adapters": broken_adapters[:MAX_PATHS],
        "drifted_managed_skills": drift_skills[:MAX_PATHS],
        "probes": probes,
    }


def probe_document(path: Path) -> dict[str, Any]:
    """Verify that a semantic source document exists and can be opened."""
    resolved = path.expanduser().resolve(strict=False)
    try:
        stat = resolved.stat()
        if not resolved.is_file():
            return {
                "path": str(resolved),
                "state": "unavailable",
                "size_bytes": None,
                "error": "path is not a regular file",
            }
        with resolved.open("rb") as handle:
            handle.read(1)
    except FileNotFoundError:
        return {
            "path": str(resolved),
            "state": "unavailable",
            "size_bytes": None,
            "error": "file not found",
        }
    except OSError as exc:
        return {
            "path": str(resolved),
            "state": "error",
            "size_bytes": None,
            "error": str(exc)[:300],
        }
    return {
        "path": str(resolved),
        "state": "ok",
        "size_bytes": stat.st_size,
        "error": "",
    }


def collect_documents(source_root: Path | None) -> dict[str, dict[str, Any]]:
    relative_paths = {
        "wip": Path(".research/WIP.md"),
        "migration": Path(".research/MIGRATION.md"),
    }
    if source_root is None:
        return {
            name: {
                "path": None,
                "state": "unavailable",
                "size_bytes": None,
                "error": "chezmoi source root is unavailable",
            }
            for name in relative_paths
        }
    return {
        name: probe_document(source_root / relative_path)
        for name, relative_path in relative_paths.items()
    }


def derive_overall(
    managed: dict[str, Any],
    git: dict[str, Any],
    agents: dict[str, Any],
    documents: dict[str, dict[str, Any]],
) -> str:
    if managed["coverage"] == "none" or not git.get("available"):
        return "failed"
    if (
        managed["coverage"] != "full"
        or agents.get("coverage") != "full"
        or any(document["state"] != "ok" for document in documents.values())
    ):
        return "partial"
    needs_action = bool(
        managed["entry_count"]
        or git["dirty_count"]
        or git["ahead"]
        or git["behind"]
        or agents["unmanaged"]
        or agents["broken_claude_adapters"]
    )
    return "attention" if needs_action else "clean"


def collect(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    source_probe = run_command(["chezmoi", "source-path"], timeout=10)
    source_root: Path | None = None
    if source_probe["state"] == "ok" and source_probe["stdout"].strip():
        source_root = Path(source_probe["stdout"].strip()).expanduser().resolve()

    managed = collect_managed(args.timeout, args.fallback_timeout)
    if source_root and source_root.is_dir():
        git = collect_git(source_root)
    else:
        git = {"available": False, "probe": public_probe(source_probe)}

    agents = collect_agents(Path.home(), managed["entries"])
    documents = collect_documents(source_root)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "collector": "complete",
        "source_root": str(source_root) if source_root else None,
        "overall": "failed",
        "managed": managed,
        "git": git,
        "agents": agents,
        "documents": documents,
        "evidence": {"source_path": public_probe(source_probe)},
        "duration_ms": 0,
    }
    payload["overall"] = derive_overall(managed, git, agents, documents)
    payload["duration_ms"] = round((time.monotonic() - started) * 1000)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="seconds to allow the full password-backed status probe",
    )
    parser.add_argument(
        "--fallback-timeout",
        type=float,
        default=10.0,
        help="seconds to allow the non-template fallback",
    )
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = collect(args)
    except Exception as exc:  # Fail closed and preserve a machine-readable result.
        payload = {
            "schema_version": SCHEMA_VERSION,
            "collector": "failed",
            "overall": "failed",
            "error": f"{type(exc).__name__}: {exc}",
        }
    encoded = json.dumps(
        payload,
        indent=2 if args.pretty else None,
        sort_keys=True,
        separators=None if args.pretty else (",", ":"),
    )
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    print(encoded)
    print(f"{SENTINEL} sha256={digest}")
    return 0 if payload.get("collector") == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
