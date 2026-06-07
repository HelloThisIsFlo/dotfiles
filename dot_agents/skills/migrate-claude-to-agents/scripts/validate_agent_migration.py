#!/usr/bin/env python3
"""Inventory and verify Claude/Codex agent migration surfaces.

This script is intentionally read-only. It reports likely migration surfaces and
post-migration invariants, but never edits, moves, deletes, symlinks, formats, or
trusts any files.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".direnv",
    "node_modules",
}


@dataclass(frozen=True)
class Surface:
    name: str
    path: str
    state: str
    classification: str


@dataclass(frozen=True)
class Check:
    status: str
    check: str
    detail: str


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def find_root(start: Path) -> tuple[Path, bool]:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve(), True
    return start.resolve(), False


def git_ls_files(root: Path) -> set[str]:
    result = run_git(root, ["ls-files", "-z"])
    if result.returncode != 0:
        return set()
    return {item for item in result.stdout.split("\0") if item}


def git_status(root: Path) -> list[str]:
    result = run_git(root, ["status", "--short"])
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def iter_repo_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        base = Path(current_root)
        for filename in filenames:
            paths.append(base / filename)
    return paths


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def path_state(root: Path, path_text: str, tracked: set[str]) -> str:
    path = root / path_text
    pieces: list[str] = []
    if path.is_symlink():
        pieces.append("symlink")
    elif path.is_dir():
        pieces.append("dir")
    elif path.is_file():
        pieces.append("file")
    elif path.exists() or path.is_symlink():
        pieces.append("other")
    else:
        pieces.append("missing")
    if path_text in tracked:
        pieces.append("tracked")
    elif path.exists() or path.is_symlink():
        pieces.append("untracked")
    return ", ".join(pieces)


def add_if_exists(
    root: Path,
    tracked: set[str],
    surfaces: list[Surface],
    name: str,
    path_text: str,
    classification: str,
) -> None:
    path = root / path_text
    if path.exists() or path.is_symlink() or path_text in tracked:
        surfaces.append(
            Surface(name, path_text, path_state(root, path_text, tracked), classification)
        )


def discover_surfaces(root: Path, tracked: set[str]) -> list[Surface]:
    surfaces: list[Surface] = []

    for path in iter_repo_files(root):
        path_text = rel(root, path)
        basename = path.name.lower()
        if basename in {"agents.md", "claude.md", "claude.local.md"}:
            classification = "shared" if basename == "agents.md" else "claude/local"
            surfaces.append(
                Surface("Instruction file", path_text, path_state(root, path_text, tracked), classification)
            )

    known_paths = [
        ("Claude project settings", ".claude/settings.json", "claude-specific"),
        ("Claude local settings", ".claude/settings.local.json", "local-only"),
        ("Claude rules", ".claude/rules", "claude-specific"),
        ("Claude hooks", ".claude/hooks", "claude adapter/scripts"),
        ("Claude skills", ".claude/skills", "claude adapter"),
        ("Claude commands", ".claude/commands", "claude legacy"),
        ("Claude agents", ".claude/agents", "claude-specific"),
        ("Claude project agent memory", ".claude/agent-memory", "shared-or-local-review"),
        ("Claude local agent memory", ".claude/agent-memory-local", "local-only"),
        ("Shared skills", ".agents/skills", "shared"),
        ("Shared hooks", ".agents/hooks", "shared"),
        ("Shared plugin marketplace", ".agents/plugins", "shared/plugin"),
        ("Codex config", ".codex/config.toml", "codex-specific"),
        ("Codex hooks", ".codex/hooks.json", "codex-specific"),
        ("Codex rules", ".codex/rules", "codex-specific"),
        ("Codex agents", ".codex/agents", "codex-specific"),
        ("Codex skills fallback", ".codex/skills", "discouraged"),
        ("Claude MCP", ".mcp.json", "claude-specific"),
        ("Claude plugin package", ".claude-plugin", "plugin-packaged"),
        ("Codex plugin package", ".codex-plugin", "plugin-packaged"),
    ]
    for name, path_text, classification in known_paths:
        add_if_exists(root, tracked, surfaces, name, path_text, classification)

    deduped: dict[tuple[str, str], Surface] = {}
    for surface in surfaces:
        deduped.setdefault((surface.name, surface.path), surface)
    return list(deduped.values())


def is_regular_file(path: Path) -> bool:
    return path.exists() and path.is_file() and not path.is_symlink()


def verify(root: Path, tracked: set[str], is_git_repo: bool) -> list[Check]:
    checks: list[Check] = []
    status_lines = git_status(root)

    checks.append(
        Check(
            "PASS" if is_git_repo else "FAIL",
            "Git repository",
            f"root: {root}" if is_git_repo else "not inside a git repository",
        )
    )

    checks.append(
        Check(
            "PASS" if not status_lines else "WARN",
            "Working tree clean",
            "clean" if not status_lines else f"{len(status_lines)} status entries",
        )
    )

    agents_md = root / "AGENTS.md"
    claude_instruction_paths = sorted(
        path for path in tracked if Path(path).name.lower() == "claude.md"
    )
    regular_claude_files = [
        path for path in claude_instruction_paths if is_regular_file(root / path)
    ]
    missing_tracked_claude_files = [
        path for path in claude_instruction_paths if not (root / path).exists() and not (root / path).is_symlink()
    ]
    if agents_md.exists() and not regular_claude_files and not missing_tracked_claude_files:
        detail = "AGENTS.md exists; no tracked regular CLAUDE.md adapters found"
        checks.append(Check("PASS", "Instruction adapters", detail))
    elif regular_claude_files:
        checks.append(
            Check(
                "FAIL",
                "Instruction adapters",
                "tracked regular Claude instruction files: " + ", ".join(regular_claude_files),
            )
        )
    elif missing_tracked_claude_files:
        checks.append(
            Check(
                "WARN",
                "Instruction adapters",
                "tracked Claude instruction files missing on disk: "
                + ", ".join(missing_tracked_claude_files),
            )
        )
    else:
        checks.append(Check("INFO", "Instruction adapters", "no tracked Claude instruction adapters detected"))

    codex_skills = root / ".codex" / "skills"
    checks.append(
        Check(
            "WARN" if codex_skills.exists() else "PASS",
            "Codex skills fallback",
            ".codex/skills exists; prefer .agents/skills" if codex_skills.exists() else "no .codex/skills fallback",
        )
    )

    shared_skills = root / ".agents" / "skills"
    claude_skills = root / ".claude" / "skills"
    if shared_skills.exists() and claude_skills.exists():
        checks.append(
            Check(
                "PASS" if claude_skills.is_symlink() else "WARN",
                "Claude skills adapter",
                ".claude/skills is a symlink" if claude_skills.is_symlink() else ".claude/skills exists but is not a symlink",
            )
        )
    elif shared_skills.exists():
        checks.append(Check("INFO", "Claude skills adapter", ".agents/skills exists; .claude/skills is absent"))
    else:
        checks.append(Check("INFO", "Shared skills", ".agents/skills not present"))

    codex_hooks_json = root / ".codex" / "hooks.json"
    codex_config = root / ".codex" / "config.toml"
    inline_hooks = False
    if codex_config.is_file():
        inline_hooks = "[hooks" in codex_config.read_text(encoding="utf-8", errors="replace")
    if codex_hooks_json.exists() and inline_hooks:
        checks.append(Check("WARN", "Codex hook representation", "both .codex/hooks.json and inline hooks in .codex/config.toml"))
    elif codex_hooks_json.exists():
        checks.append(Check("PASS", "Codex hook representation", ".codex/hooks.json"))
    elif inline_hooks:
        checks.append(Check("WARN", "Codex hook representation", "inline hooks in .codex/config.toml; house default is .codex/hooks.json"))
    else:
        checks.append(Check("INFO", "Codex hook representation", "no Codex hook registration detected"))

    shared_hooks = root / ".agents" / "hooks"
    claude_settings = root / ".claude" / "settings.json"
    if shared_hooks.exists() and not claude_settings.exists() and not codex_hooks_json.exists() and not inline_hooks:
        checks.append(Check("WARN", "Shared hook registration", ".agents/hooks exists without Claude or Codex hook registration"))
    elif shared_hooks.exists():
        checks.append(Check("INFO", "Shared hook registration", ".agents/hooks present"))

    claude_agents = root / ".claude" / "agents"
    codex_agents = root / ".codex" / "agents"
    if claude_agents.exists() and not codex_agents.exists():
        checks.append(Check("WARN", "Subagent migration", ".claude/agents exists without .codex/agents"))
    elif claude_agents.exists() and codex_agents.exists():
        checks.append(Check("INFO", "Subagent migration", "both Claude and Codex agent surfaces exist; compare definitions by intent"))
    else:
        checks.append(Check("INFO", "Subagent migration", "no Claude subagents detected"))

    local_paths = [
        ".claude/settings.local.json",
        ".claude/agent-memory-local",
        "CLAUDE.local.md",
    ]
    present_local = [path for path in local_paths if (root / path).exists() or (root / path).is_symlink()]
    checks.append(
        Check(
            "WARN" if present_local else "PASS",
            "Local-only assets",
            ", ".join(present_local) if present_local else "no known local-only Claude assets detected",
        )
    )

    return checks


def print_inventory(root: Path, surfaces: list[Surface], status_lines: list[str]) -> None:
    print("# Agent Migration Inventory")
    print()
    print(f"- Repo: `{root}`")
    print(f"- Git status entries: `{len(status_lines)}`")
    print()
    print("## Detected Surfaces")
    print()
    print("| Surface | Path | State | Classification |")
    print("|---|---|---|---|")
    if surfaces:
        for surface in sorted(surfaces, key=lambda item: (item.classification, item.path, item.name)):
            print(f"| {surface.name} | `{surface.path}` | {surface.state} | {surface.classification} |")
    else:
        print("| None | - | - | - |")


def print_verify(root: Path, checks: list[Check], surfaces: list[Surface]) -> None:
    print("# Agent Migration Verification")
    print()
    print(f"- Repo: `{root}`")
    print()
    print("## Checks")
    print()
    print("| Status | Check | Detail |")
    print("|---|---|---|")
    for check in checks:
        print(f"| {check.status} | {check.check} | {check.detail} |")
    print()
    print("## Surface Count")
    print()
    counts: dict[str, int] = {}
    for surface in surfaces:
        counts[surface.classification] = counts.get(surface.classification, 0) + 1
    if counts:
        for classification, count in sorted(counts.items()):
            print(f"- `{classification}`: {count}")
    else:
        print("- No migration surfaces detected")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=["inventory", "verify"],
        nargs="?",
        default="inventory",
        help="report detected surfaces or verify post-migration invariants",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="repository root or any path inside it",
    )
    args = parser.parse_args()

    root, is_git_repo = find_root(Path(args.root))
    tracked = git_ls_files(root) if is_git_repo else set()
    status_lines = git_status(root) if is_git_repo else []
    surfaces = discover_surfaces(root, tracked)

    if args.mode == "inventory":
        print_inventory(root, surfaces, status_lines)
        return 0

    checks = verify(root, tracked, is_git_repo)
    print_verify(root, checks, surfaces)
    return 1 if any(check.status == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
