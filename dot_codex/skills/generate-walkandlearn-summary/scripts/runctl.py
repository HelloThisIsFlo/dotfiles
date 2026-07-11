#!/usr/bin/env python3
"""Deterministic state and file controller for Codex-native WalkAndLearn runs."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = "codex-native-v2"
LEGACY_SCHEMA_VERSION = "codex-native-v1"
DEFAULT_REPO = Path("/Users/flo/Work/Private/Dev/AI/Agents")
DEFAULT_OUTPUT_BASE = Path(
    "/Users/flo/Work/Private/PKM/Obsidian/TheVault/WalkAndLearn/DebugSandbox"
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_BYTES = 750_000
CLIPBOARD_MIN_BYTES = 2_000
FAMILIES = ("emotional", "technical")
CANDIDATE_COUNT = 3
MAX_ATTEMPTS = 2
AUTO_REPAIR_LIMIT = 2

PROMPTS = {
    "emotional": SKILL_ROOT / "references" / "summary-emotional.md",
    "technical": SKILL_ROOT / "references" / "summary-technical.md",
    "judge_emotional": SKILL_ROOT / "references" / "judge-emotional.md",
    "judge_technical": SKILL_ROOT / "references" / "judge-technical.md",
    "technical_researcher": SKILL_ROOT / "references" / "technical-researcher.md",
    "auditor_emotional": SKILL_ROOT / "references" / "fidelity-auditor-emotional.md",
    "auditor_technical": SKILL_ROOT / "references" / "fidelity-auditor-technical.md",
    "repair": SKILL_ROOT / "references" / "exact-replacement-repair.md",
}

SCORE_CONTRACTS = {
    "emotional": {
        "quote_attribution_fidelity": 0.40,
        "genuine_moment_coverage": 0.20,
        "taxonomy_calibration": 0.20,
        "recall_value": 0.10,
        "emotional_authenticity": 0.10,
    },
    "technical": {
        "technical_correctness_terminology": 0.35,
        "conversation_fidelity": 0.25,
        "proportional_coverage": 0.15,
        "reference_usefulness": 0.15,
        "mental_models_relationships": 0.05,
        "formatting_composition_compliance": 0.05,
    },
}

AUDIT_CHECKS = {
    "emotional": {
        "quote_fidelity",
        "attribution",
        "conversation_support",
        "taxonomy_calibration",
        "completeness",
        "structure_compliance",
    },
    "technical": {
        "quote_fidelity",
        "attribution",
        "conversation_support",
        "technical_correctness",
        "formula_validity",
        "terminology",
        "correction_transparency",
        "completeness",
        "structure_compliance",
    },
}
FAILURE_TO_CHECK = {
    "emotional": {
        "fabricated_quote": "quote_fidelity",
        "reversed_attribution": "attribution",
        "unsupported_claim": "conversation_support",
        "false_independence_claim": "taxonomy_calibration",
        "truncation": "completeness",
        "placeholder_violation": "structure_compliance",
    },
    "technical": {
        "fabricated_quote": "quote_fidelity",
        "reversed_attribution": "attribution",
        "unsupported_claim": "conversation_support",
        "technical_inaccuracy": "technical_correctness",
        "unresolved_claim_not_qualified": "technical_correctness",
        "terminology_error": "terminology",
        "invalid_formula": "formula_validity",
        "missing_correction_label": "correction_transparency",
        "truncation": "completeness",
        "placeholder_violation": "structure_compliance",
    },
}

RESEARCH_KINDS = {"fact", "terminology", "formula", "scope", "version"}
RESEARCH_ASSESSMENTS = {
    "confirmed",
    "needs_correction",
    "needs_qualification",
    "unresolved",
}
RESEARCH_SEVERITIES = {"critical", "material", "minor"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}
SOURCE_TYPES = {"primary", "official", "secondary"}


class RunError(RuntimeError):
    """Expected controller failure rendered as JSON by the CLI."""


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise RunError("topic must contain at least one ASCII letter or digit")
    return slug


def validate_date(value: str) -> str:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise RunError("date must use YYYY-MM-DD") from exc
    if parsed.strftime("%Y-%m-%d") != value:
        raise RunError("date must use YYYY-MM-DD")
    return value


def run_id_now() -> str:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{secrets.token_hex(2)}"


def ensure_run_id(value: str) -> str:
    if not re.fullmatch(r"[0-9]{8}-[0-9]{6}-[a-f0-9]{4}", value):
        raise RunError(f"invalid run ID: {value}")
    return value


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{secrets.token_hex(4)}.tmp")
    temp.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    os.replace(temp, path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RunError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RunError(f"expected a JSON object in {path}")
    return value


def command_text(command: list[str]) -> str:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RunError(f"{command[0]} failed: {detail}")
    return result.stdout


def next_available_input(input_dir: Path, date: str, topic: str) -> Path:
    base = f"input-{date}-{topic}"
    candidate = input_dir / f"{base}.md"
    suffix = 2
    while candidate.exists():
        candidate = input_dir / f"{base}-{suffix}.md"
        suffix += 1
    return candidate


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def verify_ignored(repo: Path, path: Path) -> None:
    if not (repo / ".git").exists():
        return
    relative = path.relative_to(repo)
    result = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "-q", str(relative)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RunError(f"canonical input is not ignored by git: {relative}")


def staging_root(args: argparse.Namespace) -> Path:
    if args.staging_root:
        return Path(args.staging_root).expanduser().resolve()
    return args.repo / "agent_files" / "walkandlearn_summary" / ".codex-runs"


def manifest_path(args: argparse.Namespace, run_id: str) -> Path:
    ensure_run_id(run_id)
    return staging_root(args) / run_id / "run.json"


def load_manifest(
    args: argparse.Namespace, run_id: str, *, mutable: bool = True
) -> tuple[Path, dict[str, Any]]:
    path = manifest_path(args, run_id)
    if not path.is_file():
        raise RunError(f"run not found: {run_id}")
    manifest = read_json(path)
    version = manifest.get("schema_version")
    if (
        version not in {SCHEMA_VERSION, LEGACY_SCHEMA_VERSION}
        or manifest.get("run_id") != run_id
    ):
        raise RunError(f"manifest identity mismatch for {run_id}")
    if mutable and version != SCHEMA_VERSION:
        raise RunError(
            f"legacy {version} run is read-only; start a fresh {SCHEMA_VERSION} run"
        )
    failures = integrity_check(manifest, verify_prompts=version == SCHEMA_VERSION)
    if failures:
        raise RunError("; ".join(failures))
    return path, manifest


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = now_iso()
    write_json_atomic(path, manifest)


def prompt_record(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise RunError(f"missing prompt: {path}")
    return {"path": str(path), "sha256": sha256_file(path)}


def probe_source(args: argparse.Namespace) -> dict[str, Any]:
    if args.clipboard:
        data = command_text(["pbpaste"]).encode("utf-8")
        return {
            "status": "probed",
            "source": "clipboard",
            "byte_count": len(data),
            "plausible": CLIPBOARD_MIN_BYTES <= len(data) <= args.max_bytes,
            "minimum_bytes": CLIPBOARD_MIN_BYTES,
            "maximum_bytes": args.max_bytes,
        }
    source = Path(args.file).expanduser()
    if not source.is_absolute():
        raise RunError("conversation file must be an absolute path")
    source = source.resolve()
    if not source.is_file():
        raise RunError(f"conversation file not found: {source}")
    data = source.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RunError("conversation must be valid UTF-8") from exc
    return {
        "status": "probed",
        "source": "file",
        "path": str(source),
        "input_file": source.name,
        "byte_count": len(data),
        "plausible": bool(data) and len(data) <= args.max_bytes,
        "maximum_bytes": args.max_bytes,
    }


def candidate_entry(run_dir: Path, family: str, index: int) -> dict[str, Any]:
    return {
        "index": index,
        "family": family,
        "status": "pending",
        "attempts": 0,
        "output_path": None,
        "sha256": None,
        "failure": None,
        "published_file": f"{family}_{index}.md",
        "current_revision": None,
        "accepted_revision": None,
        "revisions": [],
    }


def audit_family_entry() -> dict[str, Any]:
    return {
        "status": "pending",
        "current_index": None,
        "pending_issues": [],
        "rounds": [],
        "repairs": [],
        "extra_repairs": {},
        "pause_reason": None,
    }


def init_run(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo
    input_dir = repo / "agent_files" / "walkandlearn_summary"
    if not input_dir.is_dir():
        raise RunError(f"missing canonical input directory: {input_dir}")
    date = validate_date(args.date)
    topic = slugify(args.topic)

    if args.clipboard:
        source_mode = "clipboard"
        data = command_text(["pbpaste"]).encode("utf-8")
        if len(data) < CLIPBOARD_MIN_BYTES:
            raise RunError(
                f"clipboard is too short: {len(data)} bytes; minimum is {CLIPBOARD_MIN_BYTES}"
            )
        canonical = next_available_input(input_dir, date, topic)
        canonical.write_bytes(data)
        try:
            verify_ignored(repo, canonical)
        except Exception:
            canonical.unlink(missing_ok=True)
            raise
    else:
        source_mode = "file"
        source = Path(args.file).expanduser()
        if not source.is_absolute():
            raise RunError("conversation file must be an absolute path")
        source = source.resolve()
        if not source.is_file():
            raise RunError(f"conversation file not found: {source}")
        data = source.read_bytes()
        if args.reuse_canonical:
            if not is_within(source, input_dir.resolve()):
                raise RunError(
                    "--reuse-canonical requires a file in the canonical input directory"
                )
            canonical = source
            verify_ignored(repo, canonical)
        else:
            canonical = next_available_input(input_dir, date, topic)
            canonical.write_bytes(data)
            try:
                verify_ignored(repo, canonical)
            except Exception:
                canonical.unlink(missing_ok=True)
                raise

    byte_count = len(data)
    if byte_count == 0:
        if not args.reuse_canonical:
            canonical.unlink(missing_ok=True)
        raise RunError("conversation file is empty")
    if byte_count > args.max_bytes:
        if not args.reuse_canonical:
            canonical.unlink(missing_ok=True)
        raise RunError(
            f"conversation is too large: {byte_count} bytes; maximum is {args.max_bytes}. "
            "Split the source instead of silently chunking it."
        )
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        if not args.reuse_canonical:
            canonical.unlink(missing_ok=True)
        raise RunError("conversation must be valid UTF-8") from exc

    run_id = run_id_now()
    root = staging_root(args)
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    for relative in (
        "candidates",
        "packets",
        "judges",
        "audits",
        "research",
        "repairs",
        "prompts",
    ):
        (run_dir / relative).mkdir()

    prompt_records: dict[str, dict[str, str]] = {}
    for name, source_prompt in PROMPTS.items():
        if not source_prompt.is_file():
            raise RunError(f"missing prompt: {source_prompt}")
        snapshot = run_dir / "prompts" / source_prompt.name
        snapshot.write_bytes(source_prompt.read_bytes())
        prompt_records[name] = prompt_record(snapshot)

    created_at = now_iso()
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "status": "generating",
        "created_at": created_at,
        "updated_at": created_at,
        "source": {
            "mode": source_mode,
            "session_date": date,
            "topic": topic,
            "input_file": canonical.name,
            "path": str(canonical),
            "sha256": sha256_bytes(data),
            "byte_count": byte_count,
        },
        "prompts": prompt_records,
        "candidates": {
            family: [
                candidate_entry(run_dir, family, index)
                for index in range(CANDIDATE_COUNT)
            ]
            for family in FAMILIES
        },
        "technical_review": {
            "status": "pending",
            "attempts": 0,
            "packet": None,
            "output_path": None,
            "sha256": None,
            "result": None,
            "failure": None,
        },
        "evaluations": {
            family: {
                "status": "pending",
                "attempts": 0,
                "packet": None,
                "output_path": None,
                "sha256": None,
                "result": None,
                "failure": None,
                "basis": None,
            }
            for family in FAMILIES
        },
        "audit": {
            "status": "pending",
            "accepted": {},
            "rejected": {family: [] for family in FAMILIES},
            "families": {family: audit_family_entry() for family in FAMILIES},
        },
        "publication": {"status": "pending", "path": None, "manual_exports": []},
        "config": {
            "repo": str(repo),
            "output_base": str(args.output_base),
            "staging_root": str(root),
            "max_bytes": args.max_bytes,
        },
    }
    path = run_dir / "run.json"
    write_json_atomic(path, manifest)
    return {
        "status": "initialized",
        "run_id": run_id,
        "manifest_path": str(path),
        "transcript_path": str(canonical),
        "session_date": date,
        "topic": topic,
        "next": "start emotional candidates 0, 1, and 2",
    }


def get_candidate(manifest: dict[str, Any], family: str, index: int) -> dict[str, Any]:
    if family not in FAMILIES:
        raise RunError(f"invalid family: {family}")
    if index not in range(CANDIDATE_COUNT):
        raise RunError(f"candidate index must be 0 through {CANDIDATE_COUNT - 1}")
    return manifest["candidates"][family][index]


def get_revision(entry: dict[str, Any], revision: int | None = None) -> dict[str, Any]:
    target = entry.get("current_revision") if revision is None else revision
    if target is None:
        raise RunError(f"{entry['family']}_{entry['index']} has no validated revision")
    for item in entry.get("revisions", []):
        if item["revision"] == target:
            return item
    raise RunError(f"missing revision {target} for {entry['family']}_{entry['index']}")


def candidate_id(family: str, index: int, revision: int) -> str:
    return f"{family}_{index}.r{revision}"


def start_candidate(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    entry = get_candidate(manifest, args.family, args.index)
    if entry["status"] == "valid":
        raise RunError(f"{args.family}_{args.index} is already valid")
    if entry["attempts"] >= MAX_ATTEMPTS:
        raise RunError(f"retry limit exhausted for {args.family}_{args.index}")
    entry["attempts"] += 1
    output = (
        path.parent
        / "candidates"
        / (f"{args.family}_{args.index}.attempt{entry['attempts']}.partial.md")
    )
    output.unlink(missing_ok=True)
    entry.update(
        {
            "status": "started",
            "output_path": str(output),
            "sha256": None,
            "failure": None,
        }
    )
    save_manifest(path, manifest)
    prompt_key = args.family
    return {
        "status": "started",
        "run_id": args.run_id,
        "family": args.family,
        "index": args.index,
        "attempt": entry["attempts"],
        "transcript_path": manifest["source"]["path"],
        "prompt_path": manifest["prompts"][prompt_key]["path"],
        "output_path": str(output),
    }


def obvious_truncation(content: str) -> str | None:
    lower = content.lower()
    markers = (
        "summary generation returned no visible text",
        "summary generation stopped because max_tokens",
        "[generation failed]",
        "[error generating",
    )
    for marker in markers:
        if marker in lower:
            return f"generation failure marker found: {marker}"
    if content.count("```") % 2:
        return "unclosed fenced code block"
    if len(re.findall(r"(?m)^\s*\$\$\s*$", content)) % 2:
        return "unclosed block-math fence"
    return None


def validate_candidate_content(
    manifest: dict[str, Any], family: str, index: int, content: str
) -> str | None:
    if not content.strip():
        return "candidate is empty"
    first_line = content.lstrip("\ufeff \t\r\n").splitlines()[0].strip()
    if first_line == "---":
        return "candidate must not contain model-supplied frontmatter"
    truncation = obvious_truncation(content)
    if truncation:
        return truncation
    placeholder_count = content.count("[AHA_PLACEHOLDER]")
    aha_h1_count = len(
        re.findall(r"(?mi)^#\s+[^\n]*Aha Moments\s*&\s*Discovery Journey\s*$", content)
    )
    if family == "emotional":
        if placeholder_count:
            return "emotional candidate contains [AHA_PLACEHOLDER]"
        if aha_h1_count:
            return "emotional candidate contains the outer Aha H1"
        required_markers = {
            "an H2 moment heading": r"(?m)^##\s+\S",
            "the Summary callout": r"(?m)^> \[!SUMMARY\] \*\*Summary\*\*\s*$",
            "the Why it mattered callout": (
                r"(?m)^> \[!SUCCESS\] \*\*Why it mattered!\*\*\s*$"
            ),
            "the model-contribution boundary": r"(?m)^\*\*I (?:explained|introduced|started by presenting)",
            "the user-contribution boundary": r"(?m)^\*\*(?:What you|Your insight)",
        }
        for label, pattern in required_markers.items():
            if not re.search(pattern, content):
                return f"emotional candidate is missing {label}"
    else:
        if placeholder_count != 1:
            return f"technical candidate has {placeholder_count} AHA placeholders; expected 1"
        exact_heading = "# ⭐ Aha Moments & Discovery Journey"
        if content.count(exact_heading) != 1 or aha_h1_count != 1:
            return "technical candidate must contain exactly one exact Aha H1"
        if not re.search(
            r"(?m)^# ⭐ Aha Moments & Discovery Journey\r?\n\[AHA_PLACEHOLDER\]\s*$",
            content,
        ):
            return "technical candidate must keep the exact Aha heading and placeholder adjacent"
        if not content.lstrip().startswith("**Document Title:** "):
            return "technical candidate must begin with the document title field"
        h1_lines = re.findall(r"(?m)^#\s+(.+?)\s*$", content)
        required_sections = (
            "TL;DR / 30-Second Refresher",
            "Quick-Reference Cheat Sheets",
            "Aha Moments & Discovery Journey",
            "Mental Models Built",
            "Suggested Next Adventures",
            "Closing Thoughts",
        )
        for section in required_sections:
            if sum(section in heading for heading in h1_lines) != 1:
                return f"technical candidate must contain one H1 section for {section}"
    canonical_digest = sha256_bytes(content.strip().encode("utf-8"))
    for other in manifest["candidates"][family]:
        if other["index"] != index and other["status"] == "valid":
            other_content = Path(other["output_path"]).read_text(encoding="utf-8")
            if sha256_bytes(other_content.strip().encode("utf-8")) == canonical_digest:
                return f"exact duplicate of {family}_{other['index']}"
    return None


def validate_candidate(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    entry = get_candidate(manifest, args.family, args.index)
    if entry["status"] != "started" or not entry["output_path"]:
        raise RunError(f"{args.family}_{args.index} has no started candidate attempt")
    output = Path(entry["output_path"])
    try:
        content = output.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failure = f"candidate output is unreadable UTF-8: {exc}"
    else:
        failure = validate_candidate_content(manifest, args.family, args.index, content)
    if failure:
        entry.update({"status": "invalid", "failure": failure, "sha256": None})
        retry = entry["attempts"] < MAX_ATTEMPTS
        if not retry:
            manifest["status"] = "failed"
        save_manifest(path, manifest)
        return {
            "status": "invalid",
            "run_id": args.run_id,
            "family": args.family,
            "index": args.index,
            "reason": failure,
            "retry_available": retry,
        }
    digest = sha256_bytes(content.encode("utf-8"))
    revision = {
        "revision": 0,
        "kind": "generated",
        "parent_revision": None,
        "output_path": str(output),
        "sha256": digest,
        "created_at": now_iso(),
        "resolved_issues": [],
        "finding_ids": [],
        "finding_proofs": {},
        "repair_record": None,
        "audit_status": "pending",
    }
    entry.update(
        {
            "status": "valid",
            "failure": None,
            "sha256": digest,
            "output_path": str(output),
            "current_revision": 0,
            "revisions": [revision],
        }
    )
    if manifest["status"] == "generating" and all(
        item["status"] == "valid"
        for family in FAMILIES
        for item in manifest["candidates"][family]
    ):
        manifest["status"] = "researching"
    save_manifest(path, manifest)
    return {
        "status": "valid",
        "run_id": args.run_id,
        "family": args.family,
        "index": args.index,
        "sha256": digest,
    }


def all_candidates_valid(manifest: dict[str, Any], family: str | None = None) -> bool:
    families = (family,) if family else FAMILIES
    return all(
        entry["status"] == "valid"
        for name in families
        for entry in manifest["candidates"][name]
    )


def parse_source(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise RunError(f"{label} must be an object")
    require_keys(value, {"title", "publisher", "url", "support", "source_type"}, label)
    for key in ("title", "publisher", "url", "support"):
        if not isinstance(value[key], str) or not value[key].strip():
            raise RunError(f"{label}.{key} must be a non-empty string")
    if value["source_type"] not in SOURCE_TYPES:
        raise RunError(f"{label}.source_type is invalid")
    parsed = urlparse(value["url"])
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RunError(f"{label}.url must be an absolute HTTP(S) URL")
    host = (parsed.hostname or "").casefold()
    search_result = (
        (host.endswith("google.com") and parsed.path in {"/search", "/scholar"})
        or (host.endswith("bing.com") and parsed.path.startswith("/search"))
        or (host.endswith("duckduckgo.com") and bool(parsed.query))
        or (host == "search.brave.com" and parsed.path.startswith("/search"))
    )
    if search_result:
        raise RunError(f"{label}.url must be a canonical source, not a search page")
    return copy.deepcopy(value)


def has_authoritative_source(sources: list[dict[str, str]]) -> bool:
    return any(source["source_type"] in {"primary", "official"} for source in sources)


def is_uncertainty_worded(value: str) -> bool:
    lower = value.casefold()
    markers = (
        "uncertain",
        "unresolved",
        "unverified",
        "not established",
        "cannot confirm",
        "could not confirm",
        "insufficient evidence",
    )
    return any(marker in lower for marker in markers)


def categorically_denies_existence(value: str) -> bool:
    lower = value.casefold()
    if any(
        phrase in lower
        for phrase in (
            "does not exist",
            "doesn't exist",
            "doesn’t exist",
            "nonexistent",
            "not a real",
        )
    ):
        return True
    patterns = (
        r"\bno such\b.{0,120}\bexists?\b",
        r"\bthere (?:is|are) no such\b",
        r"\b(?:is|are|was|were) not real\b",
        r"\b(?:isn't|aren't|wasn't|weren't) real\b",
        r"\b(?:cannot|can't|could not|couldn't) exist\b",
    )
    return any(re.search(pattern, lower, flags=re.DOTALL) for pattern in patterns)


def prepare_technical_review(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    if not all_candidates_valid(manifest, "technical"):
        raise RunError("all three technical candidates must be valid before research")
    review = manifest["technical_review"]
    if review["status"] == "valid":
        raise RunError("technical review is already valid")
    if review["attempts"] >= MAX_ATTEMPTS:
        raise RunError("retry limit exhausted for technical research")
    if manifest["evaluations"]["technical"]["status"] != "pending":
        raise RunError("technical research must finish before technical judging")

    review["attempts"] += 1
    if review["status"] == "invalid" and review["packet"]:
        packet = review["packet"]
        bundle = Path(packet["path"])
        if not bundle.is_file() or sha256_file(bundle) != packet["sha256"]:
            raise RunError("preserved technical research bundle changed")
    else:
        indices = list(range(CANDIDATE_COUNT))
        secrets.SystemRandom().shuffle(indices)
        aliases = [f"candidate-{secrets.token_hex(3)}" for _ in indices]
        mapping = dict(zip(aliases, indices, strict=True))
        order = list(aliases)
        bundle = path.parent / "packets" / "technical-research.md"
        parts = ["# Anonymized Technical Candidates"]
        for alias in order:
            index = mapping[alias]
            entry = manifest["candidates"]["technical"][index]
            revision = get_revision(entry, 0)
            body = Path(revision["output_path"]).read_text(encoding="utf-8").strip()
            parts.extend(["", f"## {alias}", "", body])
        bundle.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
        packet = {
            "path": str(bundle),
            "sha256": sha256_file(bundle),
            "mapping": mapping,
            "order": order,
        }
    output = path.parent / "research" / f"technical.attempt{review['attempts']}.json"
    output.unlink(missing_ok=True)
    review.update(
        {
            "status": "started",
            "packet": packet,
            "output_path": str(output),
            "sha256": None,
            "result": None,
            "failure": None,
        }
    )
    save_manifest(path, manifest)
    return {
        "status": "started",
        "run_id": args.run_id,
        "attempt": review["attempts"],
        "transcript_path": manifest["source"]["path"],
        "prompt_path": manifest["prompts"]["technical_researcher"]["path"],
        "bundle_path": packet["path"],
        "bundle_sha256": packet["sha256"],
        "output_path": str(output),
    }


def parse_technical_review(
    raw: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    require_keys(
        raw,
        {"schema_version", "bundle_sha256", "findings", "coverage", "confidence"},
        "technical review",
    )
    if raw["schema_version"] != SCHEMA_VERSION:
        raise RunError("technical review schema_version mismatch")
    review = manifest["technical_review"]
    packet = review["packet"]
    if raw["bundle_sha256"] != packet["sha256"]:
        raise RunError("technical review bundle SHA-256 mismatch")
    aliases = set(packet["mapping"])
    findings = raw["findings"]
    if not isinstance(findings, list):
        raise RunError("technical review findings must be an array")
    parsed_findings: list[dict[str, Any]] = []
    finding_ids: set[str] = set()
    aliases_with_findings: set[str] = set()
    unresolved_material = 0
    for position, finding in enumerate(findings):
        label = f"finding[{position}]"
        if not isinstance(finding, dict):
            raise RunError(f"{label} must be an object")
        require_keys(
            finding,
            {
                "finding_id",
                "candidate_ids",
                "excerpts",
                "kind",
                "assessment",
                "severity",
                "correction",
                "confidence",
                "sources",
            },
            label,
        )
        finding_id = finding["finding_id"]
        if finding_id != f"finding-{position + 1:03d}" or finding_id in finding_ids:
            raise RunError(
                f"{label}.finding_id must be sequential from finding-001 and unique"
            )
        finding_ids.add(finding_id)
        candidate_ids = string_list(
            finding["candidate_ids"], f"{label}.candidate_ids", nonempty=True
        )
        if (
            len(candidate_ids) != len(set(candidate_ids))
            or not set(candidate_ids) <= aliases
        ):
            raise RunError(f"{label}.candidate_ids must be unique packet IDs")
        aliases_with_findings.update(candidate_ids)
        if finding["kind"] not in RESEARCH_KINDS:
            raise RunError(f"{label}.kind is invalid")
        if finding["assessment"] not in RESEARCH_ASSESSMENTS:
            raise RunError(f"{label}.assessment is invalid")
        if finding["severity"] not in RESEARCH_SEVERITIES:
            raise RunError(f"{label}.severity is invalid")
        if finding["confidence"] not in CONFIDENCE_LEVELS:
            raise RunError(f"{label}.confidence is invalid")
        if (
            not isinstance(finding["correction"], str)
            or not finding["correction"].strip()
        ):
            raise RunError(f"{label}.correction must be non-empty")
        correction = finding["correction"].strip()
        assessment = finding["assessment"]
        if assessment == "confirmed" and correction != "No correction required.":
            raise RunError(
                f"{label}.correction must be exactly 'No correction required.' when confirmed"
            )
        if assessment != "confirmed" and correction == "No correction required.":
            raise RunError(f"{label}.correction contradicts its assessment")
        if assessment == "unresolved":
            if categorically_denies_existence(correction):
                raise RunError(
                    f"{label}.correction cannot claim nonexistence from an unresolved search"
                )
            if not is_uncertainty_worded(correction):
                raise RunError(
                    f"{label}.correction must state uncertainty explicitly when unresolved"
                )
        excerpts = finding["excerpts"]
        if not isinstance(excerpts, list) or not excerpts:
            raise RunError(f"{label}.excerpts must be a non-empty array")
        excerpt_candidates: set[str] = set()
        for excerpt_position, excerpt in enumerate(excerpts):
            excerpt_label = f"{label}.excerpts[{excerpt_position}]"
            if not isinstance(excerpt, dict):
                raise RunError(f"{excerpt_label} must be an object")
            require_keys(excerpt, {"candidate_id", "text"}, excerpt_label)
            alias = excerpt["candidate_id"]
            text = excerpt["text"]
            if alias not in candidate_ids or not isinstance(text, str) or not text:
                raise RunError(f"{excerpt_label} identity or text is invalid")
            index = packet["mapping"][alias]
            body = Path(
                get_revision(manifest["candidates"]["technical"][index], 0)[
                    "output_path"
                ]
            ).read_text(encoding="utf-8")
            if body.count(text) != 1:
                raise RunError(f"{excerpt_label}.text must occur exactly once")
            if alias in excerpt_candidates:
                raise RunError(f"{label}.excerpts contains duplicate candidate IDs")
            excerpt_candidates.add(alias)
        if excerpt_candidates != set(candidate_ids) or len(excerpts) != len(
            candidate_ids
        ):
            raise RunError(
                f"{label}.excerpts must contain exactly one excerpt per candidate_id"
            )
        sources = finding["sources"]
        if not isinstance(sources, list):
            raise RunError(f"{label}.sources must be an array")
        parsed_sources = [
            parse_source(source, f"{label}.sources[{source_position}]")
            for source_position, source in enumerate(sources)
        ]
        if finding["assessment"] in {
            "confirmed",
            "needs_correction",
        } and not has_authoritative_source(parsed_sources):
            raise RunError(
                f"{label} definitive assessment requires a primary or official source"
            )
        if finding["assessment"] == "needs_qualification" and not parsed_sources:
            raise RunError(f"{label} qualification requires supporting evidence")
        if finding["assessment"] == "unresolved" and finding["severity"] in {
            "critical",
            "material",
        }:
            unresolved_material += 1
        enriched = copy.deepcopy(finding)
        enriched["sources"] = parsed_sources
        parsed_findings.append(enriched)

    if aliases_with_findings != aliases:
        missing_aliases = sorted(aliases - aliases_with_findings)
        raise RunError(
            "technical review findings must cover every candidate: "
            + ", ".join(missing_aliases)
        )

    coverage = raw["coverage"]
    if not isinstance(coverage, dict):
        raise RunError("technical review coverage must be an object")
    require_keys(
        coverage,
        {"candidate_ids", "material_claims_reviewed", "material_claims_unresolved"},
        "technical review coverage",
    )
    covered_ids = string_list(coverage["candidate_ids"], "coverage.candidate_ids")
    if len(covered_ids) != len(set(covered_ids)) or set(covered_ids) != aliases:
        raise RunError(
            "coverage.candidate_ids must contain every packet ID exactly once"
        )
    for key in ("material_claims_reviewed", "material_claims_unresolved"):
        if type(coverage[key]) is not int or coverage[key] < 0:
            raise RunError(f"coverage.{key} must be a non-negative integer")
    if coverage["material_claims_reviewed"] != len(parsed_findings):
        raise RunError("coverage.material_claims_reviewed must equal findings")
    if coverage["material_claims_unresolved"] != unresolved_material:
        raise RunError("coverage.material_claims_unresolved does not match findings")
    confidence = raw["confidence"]
    if not isinstance(confidence, dict):
        raise RunError("technical review confidence must be an object")
    require_keys(confidence, {"level", "reason"}, "technical review confidence")
    if confidence["level"] not in CONFIDENCE_LEVELS:
        raise RunError("technical review confidence.level is invalid")
    if not isinstance(confidence["reason"], str) or not confidence["reason"].strip():
        raise RunError("technical review confidence.reason must be non-empty")
    return {
        "bundle_sha256": raw["bundle_sha256"],
        "findings": parsed_findings,
        "coverage": copy.deepcopy(coverage),
        "confidence": copy.deepcopy(confidence),
    }


def record_technical_review(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    review = manifest["technical_review"]
    if review["status"] != "started" or not review["output_path"]:
        raise RunError("technical research has not been started")
    output = Path(review["output_path"])
    try:
        raw = read_json(output)
        result = parse_technical_review(raw, manifest)
    except RunError as exc:
        review.update(
            {"status": "invalid", "failure": str(exc), "result": None, "sha256": None}
        )
        retry = review["attempts"] < MAX_ATTEMPTS
        if not retry:
            manifest["status"] = "failed"
        save_manifest(path, manifest)
        return {
            "status": "invalid",
            "run_id": args.run_id,
            "reason": str(exc),
            "retry_available": retry,
        }
    review.update(
        {
            "status": "valid",
            "failure": None,
            "result": result,
            "sha256": sha256_file(output),
        }
    )
    manifest["status"] = "judging"
    save_manifest(path, manifest)
    return {
        "status": "valid",
        "run_id": args.run_id,
        "findings": len(result["findings"]),
        "sha256": review["sha256"],
        "next": "prepare emotional and technical judges",
    }


def technical_candidate_alias(manifest: dict[str, Any], index: int) -> str:
    packet = manifest["technical_review"].get("packet")
    if not packet:
        raise RunError("technical research packet is unavailable")
    matches = [
        alias
        for alias, candidate_index in packet["mapping"].items()
        if candidate_index == index
    ]
    if len(matches) != 1:
        raise RunError(f"technical research mapping is invalid for candidate {index}")
    return matches[0]


def applicable_technical_findings(
    manifest: dict[str, Any], index: int
) -> dict[str, dict[str, Any]]:
    review = manifest["technical_review"]
    if review["status"] != "valid" or not review["result"]:
        raise RunError("validated technical findings are unavailable")
    alias = technical_candidate_alias(manifest, index)
    return {
        finding["finding_id"]: finding
        for finding in review["result"]["findings"]
        if alias in finding["candidate_ids"]
    }


def write_candidate_evidence_packet(
    destination: Path,
    manifest: dict[str, Any],
    index: int,
    candidate_identity: str,
) -> dict[str, str]:
    """Write a candidate-scoped view that cannot expose sibling excerpts."""
    alias = technical_candidate_alias(manifest, index)
    findings: list[dict[str, Any]] = []
    for finding in applicable_technical_findings(manifest, index).values():
        scoped = copy.deepcopy(finding)
        scoped["candidate_ids"] = [alias]
        scoped["excerpts"] = [
            excerpt
            for excerpt in scoped["excerpts"]
            if excerpt["candidate_id"] == alias
        ]
        findings.append(scoped)
    write_json_atomic(
        destination,
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_id": candidate_identity,
            "candidate_alias": alias,
            "research_sha256": manifest["technical_review"]["sha256"],
            "findings": findings,
        },
    )
    return {"path": str(destination), "sha256": sha256_file(destination)}


def prepare_judge(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    if not all_candidates_valid(manifest, args.family):
        raise RunError(
            f"all three {args.family} candidates must be valid before judging"
        )
    evaluation = manifest["evaluations"][args.family]
    if evaluation["status"] == "valid":
        raise RunError(f"{args.family} evaluation is already valid")
    if evaluation["attempts"] >= MAX_ATTEMPTS:
        raise RunError(f"retry limit exhausted for {args.family} judge")
    if args.family == "technical" and manifest["technical_review"]["status"] != "valid":
        raise RunError("technical research must be valid before technical judging")

    evaluation["attempts"] += 1
    if evaluation["status"] == "invalid" and evaluation["packet"]:
        packet_path = Path(evaluation["packet"]["path"])
        if not packet_path.is_file():
            raise RunError(f"missing preserved judge packet: {packet_path}")
        mapping = evaluation["packet"]["mapping"]
        packet_order = evaluation["packet"]["order"]
    elif args.family == "technical":
        research_packet = manifest["technical_review"]["packet"]
        packet_path = Path(research_packet["path"])
        if (
            not packet_path.is_file()
            or sha256_file(packet_path) != research_packet["sha256"]
        ):
            raise RunError("technical research bundle changed before judging")
        mapping = copy.deepcopy(research_packet["mapping"])
        packet_order = list(research_packet["order"])
    else:
        indices = list(range(CANDIDATE_COUNT))
        secrets.SystemRandom().shuffle(indices)
        aliases = [f"candidate-{secrets.token_hex(3)}" for _ in indices]
        mapping = dict(zip(aliases, indices, strict=True))
        packet_order = list(aliases)
        packet_path = path.parent / "packets" / f"judge-{args.family}.md"
        parts = [f"# Anonymized {args.family.capitalize()} Candidates"]
        for alias, index in mapping.items():
            candidate = manifest["candidates"][args.family][index]
            body = (
                Path(get_revision(candidate, 0)["output_path"])
                .read_text(encoding="utf-8")
                .strip()
            )
            parts.extend(["", f"## {alias}", "", body])
        packet_path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    basis = {
        alias: {
            "index": index,
            "revision": 0,
            "sha256": get_revision(manifest["candidates"][args.family][index], 0)[
                "sha256"
            ],
        }
        for alias, index in mapping.items()
    }
    output_path = (
        path.parent / "judges" / (f"{args.family}.attempt{evaluation['attempts']}.json")
    )
    output_path.unlink(missing_ok=True)
    evaluation.update(
        {
            "status": "started",
            "packet": {
                "path": str(packet_path),
                "mapping": mapping,
                "order": packet_order,
                "sha256": sha256_file(packet_path),
                "basis": basis,
            },
            "output_path": str(output_path),
            "sha256": None,
            "result": None,
            "failure": None,
            "basis": basis,
        }
    )
    save_manifest(path, manifest)
    return {
        "status": "started",
        "run_id": args.run_id,
        "family": args.family,
        "attempt": evaluation["attempts"],
        "transcript_path": manifest["source"]["path"],
        "prompt_path": manifest["prompts"][f"judge_{args.family}"]["path"],
        "bundle_path": str(packet_path),
        "evidence_path": (
            manifest["technical_review"]["output_path"]
            if args.family == "technical"
            else None
        ),
        "output_path": str(output_path),
    }


def require_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise RunError(f"{label} keys mismatch; missing={missing}, extra={extra}")


def string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise RunError(f"{label} must be an array of strings")
    if nonempty and not value:
        raise RunError(f"{label} must not be empty")
    return value


def parse_evaluation(
    raw: dict[str, Any], family: str, packet: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    require_keys(
        raw,
        {
            "schema_version",
            "summary_type",
            "ranking",
            "recommendation",
            "ranking_reason",
            "candidates",
            "confidence",
        },
        "evaluation",
    )
    if raw["schema_version"] != SCHEMA_VERSION or raw["summary_type"] != family:
        raise RunError("evaluation schema_version or summary_type mismatch")
    aliases = set(packet["mapping"])
    ranking = string_list(raw["ranking"], "ranking")
    if len(ranking) != CANDIDATE_COUNT or set(ranking) != aliases:
        raise RunError("ranking must contain each anonymous candidate exactly once")
    if raw["recommendation"] != ranking[0]:
        raise RunError("recommendation must equal ranking[0]")
    if not isinstance(raw["ranking_reason"], str) or not raw["ranking_reason"].strip():
        raise RunError("ranking_reason must be a non-empty string")
    candidates = raw["candidates"]
    if not isinstance(candidates, list) or len(candidates) != CANDIDATE_COUNT:
        raise RunError("candidates must contain three scorecards")
    criteria = SCORE_CONTRACTS[family]
    scorecards: dict[str, dict[str, Any]] = {}
    for card in candidates:
        if not isinstance(card, dict):
            raise RunError("candidate scorecards must be objects")
        require_keys(
            card,
            {
                "candidate_id",
                "scores",
                "evidence",
                "strengths",
                "omissions",
                "fidelity_concerns",
            },
            "candidate scorecard",
        )
        alias = card["candidate_id"]
        if alias not in aliases or alias in scorecards:
            raise RunError("candidate scorecard IDs must be unique anonymous IDs")
        scores = card["scores"]
        if not isinstance(scores, dict) or set(scores) != set(criteria):
            raise RunError(f"{alias} scores do not match the {family} criteria")
        for key, score in scores.items():
            if type(score) is not int or not 1 <= score <= 5:
                raise RunError(f"{alias}.{key} must be an integer from 1 to 5")
        for field in ("evidence", "strengths", "omissions", "fidelity_concerns"):
            string_list(
                card[field],
                f"{alias}.{field}",
                nonempty=field in {"evidence", "strengths"},
            )
        if family == "technical":
            applicable = [
                finding
                for finding in manifest["technical_review"]["result"]["findings"]
                if alias in finding["candidate_ids"]
                and finding["assessment"] != "confirmed"
            ]
            evidence_text = "\n".join(card["evidence"])
            omitted_findings = [
                finding["finding_id"]
                for finding in applicable
                if finding["finding_id"] not in evidence_text
            ]
            if omitted_findings:
                raise RunError(
                    f"{alias}.evidence omits applicable findings: "
                    + ", ".join(sorted(omitted_findings))
                )
            correctness_score = scores["technical_correctness_terminology"]
            score_cap = 5
            for finding in applicable:
                if finding["severity"] == "critical":
                    score_cap = min(score_cap, 1)
                elif finding["severity"] == "material" and finding["assessment"] in {
                    "needs_correction",
                    "unresolved",
                }:
                    score_cap = min(score_cap, 2)
                elif finding["severity"] == "material":
                    score_cap = min(score_cap, 3)
                else:
                    score_cap = min(score_cap, 4)
            if correctness_score > score_cap:
                raise RunError(
                    f"{alias}.technical_correctness_terminology exceeds finding-based cap {score_cap}"
                )
        total = round(sum(scores[key] * weight for key, weight in criteria.items()), 3)
        enriched = copy.deepcopy(card)
        enriched["weighted_score"] = total
        enriched["candidate_index"] = packet["mapping"][alias]
        basis = packet.get("basis", {}).get(alias)
        if basis:
            enriched["candidate_revision"] = basis["revision"]
            enriched["candidate_sha256"] = basis["sha256"]
        scorecards[alias] = enriched
    if set(scorecards) != aliases:
        raise RunError("scorecards must cover every anonymous candidate")
    order_index = {alias: pos for pos, alias in enumerate(packet["order"])}
    expected_ranking = sorted(
        aliases,
        key=lambda alias: (-scorecards[alias]["weighted_score"], order_index[alias]),
    )
    if ranking != expected_ranking:
        raise RunError("ranking does not match weighted scores and packet tie order")
    confidence = raw["confidence"]
    if not isinstance(confidence, dict):
        raise RunError("confidence must be an object")
    require_keys(confidence, {"level", "reason"}, "confidence")
    if confidence["level"] not in {"low", "medium", "high"}:
        raise RunError("confidence.level must be low, medium, or high")
    if not isinstance(confidence["reason"], str) or not confidence["reason"].strip():
        raise RunError("confidence.reason must be non-empty")
    return {
        "ranking": [packet["mapping"][alias] for alias in ranking],
        "recommendation": packet["mapping"][ranking[0]],
        "ranking_reason": raw["ranking_reason"],
        "confidence": confidence,
        "scorecards": [scorecards[alias] for alias in ranking],
        "anonymous_ranking": ranking,
    }


def record_evaluation(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    evaluation = manifest["evaluations"][args.family]
    if evaluation["status"] != "started" or not evaluation["output_path"]:
        raise RunError(f"{args.family} judge has not been started")
    try:
        raw = read_json(Path(evaluation["output_path"]))
        result = parse_evaluation(raw, args.family, evaluation["packet"], manifest)
    except RunError as exc:
        evaluation.update(
            {"status": "invalid", "failure": str(exc), "result": None, "sha256": None}
        )
        retry = evaluation["attempts"] < MAX_ATTEMPTS
        if not retry:
            manifest["status"] = "failed"
        save_manifest(path, manifest)
        return {
            "status": "invalid",
            "run_id": args.run_id,
            "family": args.family,
            "reason": str(exc),
            "retry_available": retry,
        }
    evaluation.update(
        {
            "status": "valid",
            "failure": None,
            "result": result,
            "sha256": sha256_file(Path(evaluation["output_path"])),
        }
    )
    if all(manifest["evaluations"][family]["status"] == "valid" for family in FAMILIES):
        manifest["status"] = "auditing"
    save_manifest(path, manifest)
    return {
        "status": "valid",
        "run_id": args.run_id,
        "family": args.family,
        "ranking": result["ranking"],
        "recommendation": result["recommendation"],
    }


def next_audit_candidate(manifest: dict[str, Any], family: str) -> int:
    state = manifest["audit"]["families"][family]
    if state["current_index"] is not None:
        return state["current_index"]
    evaluation = manifest["evaluations"][family]
    if evaluation["status"] != "valid":
        raise RunError(f"{family} evaluation must be valid before auditing")
    rejected = set(manifest["audit"]["rejected"][family])
    for index in evaluation["result"]["ranking"]:
        if index not in rejected:
            state["current_index"] = index
            return index
    raise RunError(f"no eligible {family} candidate remains")


def prepare_audit(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    family = args.family
    state = manifest["audit"]["families"][family]
    if state["status"] == "accepted":
        raise RunError(f"{family} audit has already passed")
    if state["status"] == "awaiting_user":
        raise RunError(f"{family} is awaiting user direction")
    if state["status"] in {"repair_pending", "repair_started"}:
        raise RunError(f"{family} repair must finish before re-audit")
    rounds = state["rounds"]
    if rounds and rounds[-1]["status"] == "started":
        raise RunError(f"{family} audit attempt must be recorded first")
    if rounds and rounds[-1]["status"] == "invalid":
        current = rounds[-1]
        if current["attempts"] >= MAX_ATTEMPTS:
            raise RunError(f"retry limit exhausted for {family} audit")
        current["attempts"] += 1
        index = current["candidate_index"]
        revision_number = current["revision"]
    else:
        index = next_audit_candidate(manifest, family)
        entry = get_candidate(manifest, family, index)
        revision_number = entry["current_revision"]
        current = {
            "round": len(rounds) + 1,
            "candidate_index": index,
            "revision": revision_number,
            "candidate_sha256": get_revision(entry, revision_number)["sha256"],
            "attempts": 1,
            "status": "pending",
            "bundle_path": None,
            "bundle_sha256": None,
            "evidence_path": None,
            "evidence_sha256": None,
            "output_path": None,
            "result": None,
            "failure": None,
        }
        rounds.append(current)
    entry = get_candidate(manifest, family, index)
    revision = get_revision(entry, revision_number)
    cid = candidate_id(family, index, revision_number)
    bundle = (
        path.parent
        / "packets"
        / (f"audit-{family}-round{current['round']}.attempt{current['attempts']}.md")
    )
    body = Path(revision["output_path"]).read_text(encoding="utf-8").strip()
    bundle.write_text(
        "\n".join(
            [
                f"# Proposed {family.capitalize()} Winner",
                "",
                f"- Candidate ID: `{cid}`",
                f"- Revision: `{revision_number}`",
                f"- SHA-256: `{revision['sha256']}`",
                "",
                f"## {cid}",
                "",
                body,
            ]
        ).rstrip()
        + "\n",
        encoding="utf-8",
    )
    evidence: dict[str, str] | None = None
    if family == "technical":
        evidence = write_candidate_evidence_packet(
            path.parent
            / "packets"
            / (
                f"audit-technical-{index}-round{current['round']}."
                f"attempt{current['attempts']}.evidence.json"
            ),
            manifest,
            index,
            cid,
        )
    output = (
        path.parent
        / "audits"
        / (f"{family}.round{current['round']}.attempt{current['attempts']}.json")
    )
    output.unlink(missing_ok=True)
    current.update(
        {
            "status": "started",
            "bundle_path": str(bundle),
            "bundle_sha256": sha256_file(bundle),
            "evidence_path": evidence["path"] if evidence else None,
            "evidence_sha256": evidence["sha256"] if evidence else None,
            "output_path": str(output),
            "candidate_id": cid,
            "result": None,
            "failure": None,
        }
    )
    state["status"] = "started"
    manifest["audit"]["status"] = "started"
    manifest["status"] = "auditing"
    save_manifest(path, manifest)
    return {
        "status": "started",
        "run_id": args.run_id,
        "family": family,
        "round": current["round"],
        "attempt": current["attempts"],
        "candidate_id": cid,
        "revision": revision_number,
        "candidate_sha256": revision["sha256"],
        "transcript_path": manifest["source"]["path"],
        "prompt_path": manifest["prompts"][f"auditor_{family}"]["path"],
        "bundle_path": str(bundle),
        "bundle_sha256": current["bundle_sha256"],
        "evidence_path": current["evidence_path"],
        "evidence_sha256": current["evidence_sha256"],
        "output_path": str(output),
    }


def parse_audit(
    raw: dict[str, Any],
    manifest: dict[str, Any],
    family: str,
    round_record: dict[str, Any],
) -> dict[str, Any]:
    require_keys(
        raw,
        {
            "schema_version",
            "summary_type",
            "candidate_id",
            "revision",
            "candidate_sha256",
            "verdict",
            "hard_failures",
            "checks",
            "sources",
            "reason",
        },
        "audit result",
    )
    if raw["schema_version"] != SCHEMA_VERSION or raw["summary_type"] != family:
        raise RunError("audit schema_version or summary_type mismatch")
    if raw["candidate_id"] != round_record["candidate_id"]:
        raise RunError("audit candidate identity mismatch")
    if (
        type(raw["revision"]) is not int
        or raw["revision"] < 0
        or raw["revision"] != round_record["revision"]
    ):
        raise RunError("audit candidate revision mismatch")
    if raw["candidate_sha256"] != round_record["candidate_sha256"]:
        raise RunError("audit candidate SHA-256 mismatch")
    if raw["verdict"] not in {"pass", "fail"}:
        raise RunError("audit verdict must be pass or fail")
    if not isinstance(raw["reason"], str) or not raw["reason"].strip():
        raise RunError("audit reason must be non-empty")
    raw_sources = raw["sources"]
    if not isinstance(raw_sources, list):
        raise RunError("audit sources must be an array")
    audit_sources = [
        parse_source(source, f"audit sources[{position}]")
        for position, source in enumerate(raw_sources)
    ]
    if family == "emotional" and audit_sources:
        raise RunError("emotional audit must remain transcript-only")
    if family == "technical" and not has_authoritative_source(audit_sources):
        raise RunError(
            "technical audit requires an independently checked primary or official source"
        )
    checks = raw["checks"]
    expected_checks = AUDIT_CHECKS[family]
    if not isinstance(checks, dict) or set(checks) != expected_checks:
        raise RunError(f"audit checks do not match the {family} check set")
    failing_checks: set[str] = set()
    for name, check in checks.items():
        if not isinstance(check, dict):
            raise RunError(f"audit check {name} must be an object")
        require_keys(check, {"status", "evidence"}, f"audit check {name}")
        allowed = {"pass", "fail"}
        if family == "technical" and name in {
            "formula_validity",
            "correction_transparency",
        }:
            allowed.add("not_applicable")
        if check["status"] not in allowed:
            raise RunError(f"invalid status for audit check {name}")
        evidence = string_list(check["evidence"], f"audit check {name} evidence")
        if check["status"] == "not_applicable" and evidence:
            raise RunError(f"not_applicable check {name} must have empty evidence")
        if check["status"] in {"pass", "fail"} and not evidence:
            raise RunError(f"{check['status']} check {name} must include evidence")
        if check["status"] == "fail":
            failing_checks.add(name)
    entry = get_candidate(manifest, family, round_record["candidate_index"])
    audited_revision = get_revision(entry, round_record["revision"])
    body = Path(audited_revision["output_path"]).read_text(encoding="utf-8")
    applicable_findings = (
        applicable_technical_findings(manifest, round_record["candidate_index"])
        if family == "technical"
        else {}
    )
    known_findings = set(applicable_findings)
    failures = raw["hard_failures"]
    if not isinstance(failures, list):
        raise RunError("hard_failures must be an array")
    parsed_failures: list[dict[str, Any]] = []
    issue_ids: set[str] = set()
    issue_signatures: set[tuple[str, str]] = set()
    mapped_checks: set[str] = set()
    referenced_findings: set[str] = set()
    for position, failure in enumerate(failures):
        label = f"hard_failures[{position}]"
        if not isinstance(failure, dict):
            raise RunError(f"{label} must be an object")
        require_keys(
            failure,
            {
                "issue_id",
                "code",
                "candidate_excerpt",
                "evidence",
                "required_change",
                "finding_ids",
                "sources",
            },
            label,
        )
        issue_id = failure["issue_id"]
        if issue_id != f"issue-{position + 1:03d}" or issue_id in issue_ids:
            raise RunError(
                f"{label}.issue_id must be sequential from issue-001 and unique"
            )
        issue_ids.add(issue_id)
        code = failure["code"]
        if code not in FAILURE_TO_CHECK[family]:
            raise RunError(f"invalid {family} hard-failure code: {code}")
        excerpt = failure["candidate_excerpt"]
        if not isinstance(excerpt, str) or not excerpt or body.count(excerpt) != 1:
            raise RunError(f"{label}.candidate_excerpt must occur exactly once")
        signature = (code, excerpt)
        if signature in issue_signatures:
            raise RunError(f"{label} duplicates an earlier defect")
        issue_signatures.add(signature)
        for key in ("evidence", "required_change"):
            if not isinstance(failure[key], str) or not failure[key].strip():
                raise RunError(f"{label}.{key} must be non-empty")
        finding_ids = string_list(failure["finding_ids"], f"{label}.finding_ids")
        if (
            len(finding_ids) != len(set(finding_ids))
            or not set(finding_ids) <= known_findings
        ):
            raise RunError(f"{label}.finding_ids contains unknown or duplicate IDs")
        if family == "technical":
            alias = technical_candidate_alias(manifest, round_record["candidate_index"])
            for finding_id in finding_ids:
                finding = applicable_findings[finding_id]
                if finding["assessment"] == "confirmed":
                    raise RunError(
                        f"{label}.finding_ids cannot use a confirmed finding as failure evidence"
                    )
                finding_excerpts = [
                    item["text"]
                    for item in finding["excerpts"]
                    if item["candidate_id"] == alias
                ]
                if not any(
                    finding_excerpt in excerpt or excerpt in finding_excerpt
                    for finding_excerpt in finding_excerpts
                ):
                    raise RunError(
                        f"{label}.{finding_id} does not match the audited passage"
                    )
        sources = failure["sources"]
        if not isinstance(sources, list):
            raise RunError(f"{label}.sources must be an array")
        parsed_sources = [
            parse_source(source, f"{label}.sources[{source_position}]")
            for source_position, source in enumerate(sources)
        ]
        if family == "emotional" and (finding_ids or parsed_sources):
            raise RunError("emotional audit failures cannot use external evidence")
        if (
            family == "technical"
            and code
            in {
                "technical_inaccuracy",
                "terminology_error",
                "invalid_formula",
                "unresolved_claim_not_qualified",
                "missing_correction_label",
            }
            and not (finding_ids or parsed_sources)
        ):
            raise RunError(f"{label} requires technical evidence")
        if family == "technical":
            linked_findings = [applicable_findings[item] for item in finding_ids]
            authoritative_sources = list(parsed_sources)
            authoritative_sources.extend(
                source for finding in linked_findings for source in finding["sources"]
            )
            definitive = code in {
                "technical_inaccuracy",
                "terminology_error",
                "invalid_formula",
            } or (
                code == "missing_correction_label"
                and (
                    not linked_findings
                    or any(
                        finding["assessment"] in {"confirmed", "needs_correction"}
                        for finding in linked_findings
                    )
                )
            )
            if definitive and not has_authoritative_source(authoritative_sources):
                raise RunError(
                    f"{label} definitive correction requires primary or official evidence"
                )
        mapped_checks.add(FAILURE_TO_CHECK[family][code])
        referenced_findings.update(finding_ids)
        enriched = copy.deepcopy(failure)
        enriched["sources"] = parsed_sources
        parsed_failures.append(enriched)
    if mapped_checks != failing_checks:
        raise RunError("hard failures and failing checks must map exactly")
    if raw["verdict"] == "pass" and (parsed_failures or failing_checks):
        raise RunError("passing audit cannot contain hard failures")
    if raw["verdict"] == "fail" and (not parsed_failures or not failing_checks):
        raise RunError("failing audit requires hard failures and failing checks")
    if family == "technical":
        required_findings = {
            finding_id
            for finding_id, finding in applicable_findings.items()
            if finding["assessment"] != "confirmed"
        }
        check_evidence_text = "\n".join(
            evidence for check in checks.values() for evidence in check["evidence"]
        )
        reviewed_findings = referenced_findings | {
            finding_id
            for finding_id in required_findings
            if finding_id in check_evidence_text
        }
        unreviewed = required_findings - reviewed_findings
        if unreviewed:
            raise RunError(
                "technical audit did not document review of applicable findings: "
                + ", ".join(sorted(unreviewed))
            )
        outstanding = required_findings - set(audited_revision["finding_ids"])
        omitted = outstanding - referenced_findings
        if omitted:
            raise RunError(
                "technical audit omitted applicable findings: "
                + ", ".join(sorted(omitted))
            )
    result = copy.deepcopy(raw)
    result["hard_failures"] = parsed_failures
    result["sources"] = audit_sources
    return result


def repair_count(entry: dict[str, Any]) -> int:
    return sum(
        1 for revision in entry.get("revisions", []) if revision["kind"] == "repair"
    )


def repair_limit_actions(manifest: dict[str, Any], family: str) -> list[str]:
    actions = ["retry"]
    state = manifest["audit"]["families"][family]
    current = state["current_index"]
    ranking = manifest["evaluations"][family]["result"]["ranking"]
    unavailable = set(manifest["audit"]["rejected"][family])
    if current is not None:
        unavailable.add(current)
    if any(index not in unavailable for index in ranking):
        actions.append("advance")
    actions.extend(["export-review", "stop"])
    return actions


def refresh_global_audit_status(manifest: dict[str, Any]) -> None:
    states = manifest["audit"]["families"]
    if all(states[family]["status"] == "accepted" for family in FAMILIES):
        manifest["audit"]["status"] = "passed"
        manifest["status"] = "ready"
    elif any(states[family]["status"] == "awaiting_user" for family in FAMILIES):
        manifest["audit"]["status"] = "awaiting_user"
        manifest["status"] = "awaiting_user"
    elif any(states[family]["status"].startswith("repair") for family in FAMILIES):
        manifest["audit"]["status"] = "repairing"
        manifest["status"] = "repairing"
    else:
        manifest["audit"]["status"] = "pending"
        manifest["status"] = "auditing"


def record_audit(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    family = args.family
    state = manifest["audit"]["families"][family]
    if not state["rounds"] or state["rounds"][-1]["status"] != "started":
        raise RunError(f"no {family} audit is awaiting a result")
    current = state["rounds"][-1]
    try:
        raw = read_json(Path(current["output_path"]))
        result = parse_audit(raw, manifest, family, current)
    except RunError as exc:
        current.update({"status": "invalid", "failure": str(exc), "result": None})
        retry = current["attempts"] < MAX_ATTEMPTS
        state["status"] = "pending" if retry else "failed"
        if not retry:
            manifest["audit"]["status"] = "failed"
            manifest["status"] = "failed"
        save_manifest(path, manifest)
        return {
            "status": "invalid",
            "run_id": args.run_id,
            "family": family,
            "reason": str(exc),
            "retry_available": retry,
        }
    current.update(
        {
            "status": "valid",
            "failure": None,
            "result": result,
            "output_sha256": sha256_file(Path(current["output_path"])),
        }
    )
    entry = get_candidate(manifest, family, current["candidate_index"])
    revision = get_revision(entry, current["revision"])
    revision["audit_status"] = result["verdict"]
    if result["verdict"] == "pass":
        accepted = {
            "index": current["candidate_index"],
            "revision": current["revision"],
            "sha256": current["candidate_sha256"],
        }
        manifest["audit"]["accepted"][family] = accepted
        entry["accepted_revision"] = current["revision"]
        state.update(
            {
                "status": "accepted",
                "pending_issues": [],
                "pause_reason": None,
            }
        )
        next_action: Any = (
            "publish"
            if len(manifest["audit"]["accepted"]) == len(FAMILIES)
            else "prepare remaining family audit"
        )
    else:
        state["pending_issues"] = copy.deepcopy(result["hard_failures"])
        index_key = str(current["candidate_index"])
        allowed = AUTO_REPAIR_LIMIT + state["extra_repairs"].get(index_key, 0)
        if repair_count(entry) < allowed:
            state["status"] = "repair_pending"
            state["pause_reason"] = None
            next_action = {"prepare_repair": family}
        else:
            state["status"] = "awaiting_user"
            state["pause_reason"] = "repair_limit_reached"
            next_action = {
                "await_user": {
                    "family": family,
                    "actions": repair_limit_actions(manifest, family),
                }
            }
    refresh_global_audit_status(manifest)
    save_manifest(path, manifest)
    response_status = (
        manifest["audit"]["status"] if result["verdict"] == "pass" else state["status"]
    )
    return {
        "status": response_status,
        "run_id": args.run_id,
        "family": family,
        "accepted": manifest["audit"]["accepted"],
        "rejected": manifest["audit"]["rejected"],
        "next": next_action,
    }


def prepare_repair(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    family = args.family
    state = manifest["audit"]["families"][family]
    repairs = state["repairs"]
    if state["status"] == "awaiting_user":
        raise RunError(f"{family} repair limit requires user direction")
    if repairs and repairs[-1]["status"] == "started":
        raise RunError(f"{family} repair attempt must be recorded first")
    if (
        repairs
        and repairs[-1]["status"] == "invalid"
        and repairs[-1]["attempts"] < MAX_ATTEMPTS
    ):
        repair = repairs[-1]
        repair["attempts"] += 1
    else:
        if state["status"] != "repair_pending" or not state["pending_issues"]:
            raise RunError(f"{family} has no pending repair")
        index = state["current_index"]
        entry = get_candidate(manifest, family, index)
        base = get_revision(entry)
        repair = {
            "semantic_round": repair_count(entry) + 1,
            "candidate_index": index,
            "base_revision": base["revision"],
            "base_sha256": base["sha256"],
            "issues": copy.deepcopy(state["pending_issues"]),
            "attempts": 1,
            "status": "pending",
            "packet_path": None,
            "packet_sha256": None,
            "evidence_path": None,
            "evidence_sha256": None,
            "output_path": None,
            "result": None,
            "failure": None,
            "revision": None,
        }
        repairs.append(repair)
    index = repair["candidate_index"]
    entry = get_candidate(manifest, family, index)
    base = get_revision(entry, repair["base_revision"])
    cid = candidate_id(family, index, base["revision"])
    bundle = (
        path.parent
        / "packets"
        / (
            f"repair-{family}-{index}-round{repair['semantic_round']}.attempt{repair['attempts']}.md"
        )
    )
    body = Path(base["output_path"]).read_text(encoding="utf-8").strip()
    issues_json = json.dumps(repair["issues"], indent=2, ensure_ascii=False)
    bundle.write_text(
        "\n".join(
            [
                f"# Repair {cid}",
                "",
                f"- Base revision: `{base['revision']}`",
                f"- Base SHA-256: `{base['sha256']}`",
                "",
                "## Validated audit issues",
                "",
                "```json",
                issues_json,
                "```",
                "",
                "## Candidate body",
                "",
                body,
            ]
        ).rstrip()
        + "\n",
        encoding="utf-8",
    )
    evidence: dict[str, str] | None = None
    if family == "technical":
        evidence = write_candidate_evidence_packet(
            path.parent
            / "packets"
            / (
                f"repair-technical-{index}-round{repair['semantic_round']}."
                f"attempt{repair['attempts']}.evidence.json"
            ),
            manifest,
            index,
            cid,
        )
    output = (
        path.parent
        / "repairs"
        / (
            f"{family}_{index}.round{repair['semantic_round']}.attempt{repair['attempts']}.json"
        )
    )
    output.unlink(missing_ok=True)
    repair.update(
        {
            "status": "started",
            "packet_path": str(bundle),
            "packet_sha256": sha256_file(bundle),
            "evidence_path": evidence["path"] if evidence else None,
            "evidence_sha256": evidence["sha256"] if evidence else None,
            "output_path": str(output),
            "result": None,
            "failure": None,
        }
    )
    state["status"] = "repair_started"
    refresh_global_audit_status(manifest)
    save_manifest(path, manifest)
    return {
        "status": "started",
        "run_id": args.run_id,
        "family": family,
        "candidate_id": cid,
        "base_revision": base["revision"],
        "base_sha256": base["sha256"],
        "transcript_path": manifest["source"]["path"],
        "prompt_path": manifest["prompts"]["repair"]["path"],
        "audit_path": state["rounds"][-1]["output_path"],
        "evidence_path": repair["evidence_path"],
        "evidence_sha256": repair["evidence_sha256"],
        "bundle_path": str(bundle),
        "bundle_sha256": repair["packet_sha256"],
        "candidate_path": base["output_path"],
        "output_path": str(output),
    }


def exact_callout_blocks(content: str, header: str) -> list[tuple[str, set[str]]]:
    """Return body text and Markdown-link URLs for exact Obsidian callouts."""
    lines = content.splitlines()
    expected = f"> {header}"
    blocks: list[tuple[str, set[str]]] = []
    for position, line in enumerate(lines):
        if line != expected:
            continue
        body: list[str] = []
        cursor = position + 1
        while cursor < len(lines) and lines[cursor].startswith(">"):
            body.append(lines[cursor])
            cursor += 1
        if not body:
            continue
        body_text = "\n".join(body)
        blocks.append(
            (
                body_text,
                set(re.findall(r"\[[^\]\n]+\]\((https?://[^)\s]+)\)", body_text)),
            )
        )
    return blocks


def callout_links(blocks: list[tuple[str, set[str]]]) -> set[str]:
    return set().union(*(links for _, links in blocks)) if blocks else set()


def validate_recorded_finding_callouts(
    content: str,
    finding_map: dict[str, dict[str, Any]],
    finding_ids: set[str],
) -> None:
    correction_blocks = exact_callout_blocks(
        content, "[!warning] Post-session correction"
    )
    verification_blocks = exact_callout_blocks(content, "[!question] Verification note")
    for finding_id in finding_ids:
        finding = finding_map[finding_id]
        assessment = finding["assessment"]
        if assessment == "confirmed":
            continue
        sources = finding["sources"]
        requires_verification = assessment == "unresolved" or (
            assessment == "needs_qualification"
            and not has_authoritative_source(sources)
        )
        blocks = verification_blocks if requires_verification else correction_blocks
        if not blocks:
            label = (
                "Verification note"
                if requires_verification
                else "Post-session correction"
            )
            raise RunError(f"repaired candidate lost the {label} for {finding_id}")
        if requires_verification and not any(
            is_uncertainty_worded(body) and not categorically_denies_existence(body)
            for body, _ in blocks
        ):
            raise RunError(
                f"repaired candidate must state explicit uncertainty for {finding_id}"
            )
        required_urls = {
            source["url"]
            for source in sources
            if source["source_type"] in {"primary", "official"}
        }
        if required_urls and not callout_links(blocks).intersection(required_urls):
            raise RunError(
                f"repaired candidate must retain a validated callout link for {finding_id}"
            )


def parse_repair(
    raw: dict[str, Any], manifest: dict[str, Any], family: str, repair: dict[str, Any]
) -> tuple[dict[str, Any], str]:
    require_keys(
        raw,
        {
            "schema_version",
            "summary_type",
            "candidate_id",
            "base_revision",
            "base_sha256",
            "replacements",
        },
        "repair result",
    )
    expected_id = candidate_id(
        family, repair["candidate_index"], repair["base_revision"]
    )
    if raw["schema_version"] != SCHEMA_VERSION or raw["summary_type"] != family:
        raise RunError("repair schema_version or summary_type mismatch")
    if raw["candidate_id"] != expected_id:
        raise RunError("repair candidate identity mismatch")
    if (
        type(raw["base_revision"]) is not int
        or raw["base_revision"] < 0
        or raw["base_revision"] != repair["base_revision"]
        or raw["base_sha256"] != repair["base_sha256"]
    ):
        raise RunError("repair base revision or SHA-256 mismatch")
    replacements = raw["replacements"]
    if not isinstance(replacements, list) or not replacements:
        raise RunError("repair replacements must be a non-empty array")
    issues = {issue["issue_id"]: issue for issue in repair["issues"]}
    finding_map = (
        applicable_technical_findings(manifest, repair["candidate_index"])
        if family == "technical"
        else {}
    )
    known_findings = set(finding_map)
    entry = get_candidate(manifest, family, repair["candidate_index"])
    base = get_revision(entry, repair["base_revision"])
    body = Path(base["output_path"]).read_text(encoding="utf-8")
    operations: list[tuple[int, int, str, dict[str, Any]]] = []
    resolved: set[str] = set()
    repaired_findings: set[str] = set()
    replacement_proofs: dict[str, str] = {}
    parsed_replacements: list[dict[str, Any]] = []
    for position, replacement in enumerate(replacements):
        label = f"replacements[{position}]"
        if not isinstance(replacement, dict):
            raise RunError(f"{label} must be an object")
        require_keys(
            replacement,
            {"resolves", "old_text", "new_text", "reason", "finding_ids"},
            label,
        )
        resolves = string_list(
            replacement["resolves"], f"{label}.resolves", nonempty=True
        )
        if len(resolves) != len(set(resolves)) or not set(resolves) <= set(issues):
            raise RunError(f"{label}.resolves contains unknown or duplicate issues")
        if set(resolves) & resolved:
            raise RunError(f"{label}.resolves repeats an issue resolved earlier")
        old = replacement["old_text"]
        new = replacement["new_text"]
        if (
            not isinstance(old, str)
            or not old
            or not isinstance(new, str)
            or not new.strip()
            or old == new
        ):
            raise RunError(
                f"{label}.old_text and {label}.new_text must contain non-empty changed text"
            )
        if body.count(old) != 1:
            raise RunError(f"{label}.old_text must occur exactly once")
        if old.strip() == body.strip():
            raise RunError(
                f"{label}.old_text cannot replace the entire candidate; repairs must be surgical"
            )
        old_bytes = len(old.encode("utf-8"))
        new_bytes = len(new.encode("utf-8"))
        if new_bytes > max(old_bytes * 4, old_bytes + 2_000):
            raise RunError(
                f"{label}.new_text expands too far beyond the audited passage"
            )
        if (
            not isinstance(replacement["reason"], str)
            or not replacement["reason"].strip()
        ):
            raise RunError(f"{label}.reason must be non-empty")
        finding_ids = string_list(replacement["finding_ids"], f"{label}.finding_ids")
        if (
            len(finding_ids) != len(set(finding_ids))
            or not set(finding_ids) <= known_findings
        ):
            raise RunError(f"{label}.finding_ids contains unknown or duplicate IDs")
        if repaired_findings.intersection(finding_ids):
            raise RunError(
                f"{label}.finding_ids repeats a finding from another replacement"
            )
        required_findings = {
            finding_id
            for issue_id in resolves
            for finding_id in issues[issue_id]["finding_ids"]
        }
        if set(finding_ids) != required_findings:
            raise RunError(
                f"{label}.finding_ids must exactly match the resolved audit findings"
            )
        if len(finding_ids) > 1:
            alias = technical_candidate_alias(manifest, repair["candidate_index"])
            finding_excerpts = {
                finding_id: next(
                    item["text"]
                    for item in finding_map[finding_id]["excerpts"]
                    if item["candidate_id"] == alias
                )
                for finding_id in finding_ids
            }
            for left_position, left_id in enumerate(finding_ids):
                for right_id in finding_ids[left_position + 1 :]:
                    left = finding_excerpts[left_id]
                    right = finding_excerpts[right_id]
                    if left not in right and right not in left:
                        raise RunError(
                            f"{label} cannot merge findings from distinct passages"
                        )
        for issue_id in resolves:
            if issues[issue_id]["candidate_excerpt"] not in old:
                raise RunError(
                    f"{label}.old_text must contain the excerpt for {issue_id}"
                )
        start = body.index(old)
        if family == "technical":
            codes = {issues[issue_id]["code"] for issue_id in resolves}
            assessments = {
                finding_map[finding_id]["assessment"]
                for finding_id in finding_ids
                if finding_id in finding_map
            }
            requires_verification_note = (
                "unresolved_claim_not_qualified" in codes
                or "unresolved" in assessments
                or any(
                    finding_map[finding_id]["assessment"] == "needs_qualification"
                    and not has_authoritative_source(finding_map[finding_id]["sources"])
                    for finding_id in finding_ids
                )
            )
            definitive_codes = {
                "technical_inaccuracy",
                "terminology_error",
                "invalid_formula",
            }
            requires_correction = bool(codes & definitive_codes) or (
                "missing_correction_label" in codes and not requires_verification_note
            )
            verification_blocks = exact_callout_blocks(
                new, "[!question] Verification note"
            )
            correction_blocks = exact_callout_blocks(
                new, "[!warning] Post-session correction"
            )
            if requires_verification_note and not verification_blocks:
                raise RunError(f"{label} must add an exact Verification note callout")
            if requires_correction and not correction_blocks:
                raise RunError(
                    f"{label} must add an exact Post-session correction callout"
                )
            if requires_verification_note and not any(
                is_uncertainty_worded(body) and not categorically_denies_existence(body)
                for body, _ in verification_blocks
            ):
                raise RunError(
                    f"{label} Verification note must state uncertainty without claiming nonexistence"
                )
            source_urls = {
                source["url"]
                for issue_id in resolves
                for source in issues[issue_id]["sources"]
            }
            source_urls.update(
                source["url"]
                for finding_id in finding_ids
                for source in finding_map[finding_id]["sources"]
            )
            emitted_urls = set(re.findall(r"https?://[^)\s]+", new))
            if not emitted_urls <= source_urls:
                raise RunError(f"{label} contains an unvalidated source URL")
            required_blocks = (
                verification_blocks if requires_verification_note else correction_blocks
            )
            linked_urls = callout_links(required_blocks)
            if emitted_urls and not emitted_urls <= linked_urls:
                raise RunError(
                    f"{label} source URLs must be Markdown links inside the required callout"
                )
            required_urls = {
                source["url"]
                for issue_id in resolves
                for source in issues[issue_id]["sources"]
                if source["source_type"] in {"primary", "official"}
            } | {
                source["url"]
                for finding_id in finding_ids
                for source in finding_map[finding_id]["sources"]
                if source["source_type"] in {"primary", "official"}
            }
            if required_urls and not linked_urls.intersection(required_urls):
                raise RunError(
                    f"{label} must link an exact validated URL inside the required callout"
                )
            if (
                (requires_verification_note or requires_correction)
                and new.startswith("> ")
                and start > 0
                and body[start - 1] != "\n"
            ):
                raise RunError(
                    f"{label}.old_text must start at a line boundary when the replacement begins with a callout"
                )
            validate_recorded_finding_callouts(new, finding_map, set(finding_ids))
        operations.append((start, start + len(old), new, copy.deepcopy(replacement)))
        resolved.update(resolves)
        repaired_findings.update(finding_ids)
        replacement_proofs.update({finding_id: new for finding_id in finding_ids})
        parsed_replacements.append(copy.deepcopy(replacement))
    if resolved != set(issues):
        raise RunError("repair replacements must resolve every pending issue")
    starts = [operation[0] for operation in operations]
    if starts != sorted(starts):
        raise RunError("repair replacements must follow candidate order")
    previous_end = -1
    for start, end, _, _ in operations:
        if start < previous_end:
            raise RunError("repair replacements overlap")
        previous_end = end
    replaced_bytes = sum(end - start for start, end, _, _ in operations)
    if replaced_bytes >= len(body) * 0.8:
        raise RunError(
            "repair replacements cover too much of the candidate to be surgical"
        )
    revised = body
    for start, end, new, _ in reversed(operations):
        revised = revised[:start] + new + revised[end:]
    if len(revised.encode("utf-8")) > len(body.encode("utf-8")) + max(
        4_000, len(body.encode("utf-8")) // 2
    ):
        raise RunError("repaired candidate grows too much to remain a surgical patch")
    if family == "technical":
        base_proofs = base.get("finding_proofs", {})
        for finding_id, proof in base_proofs.items():
            proof_text = proof.get("text")
            if not isinstance(proof_text, str) or body.count(proof_text) != 1:
                raise RunError(
                    f"base revision lost the protected passage for {finding_id}"
                )
            expected_text = replacement_proofs.get(finding_id, proof_text)
            if revised.count(expected_text) != 1:
                raise RunError(
                    f"repair must preserve one claim-scoped corrected passage for {finding_id}"
                )
        for finding_id, proof_text in replacement_proofs.items():
            if finding_id not in base_proofs and revised.count(proof_text) != 1:
                raise RunError(
                    f"repair must create one claim-scoped corrected passage for {finding_id}"
                )
    failure = validate_candidate_content(
        manifest, family, repair["candidate_index"], revised
    )
    if failure:
        raise RunError(f"repaired candidate is invalid: {failure}")
    result = copy.deepcopy(raw)
    result["replacements"] = parsed_replacements
    return result, revised


def record_repair(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    family = args.family
    state = manifest["audit"]["families"][family]
    if not state["repairs"] or state["repairs"][-1]["status"] != "started":
        raise RunError(f"no {family} repair is awaiting a result")
    repair = state["repairs"][-1]
    try:
        raw = read_json(Path(repair["output_path"]))
        result, revised = parse_repair(raw, manifest, family, repair)
    except RunError as exc:
        repair.update({"status": "invalid", "failure": str(exc), "result": None})
        retry = repair["attempts"] < MAX_ATTEMPTS
        state["status"] = "repair_pending" if retry else "failed"
        if not retry:
            manifest["audit"]["status"] = "failed"
            manifest["status"] = "failed"
        else:
            refresh_global_audit_status(manifest)
        save_manifest(path, manifest)
        return {
            "status": "invalid",
            "run_id": args.run_id,
            "family": family,
            "reason": str(exc),
            "retry_available": retry,
        }
    entry = get_candidate(manifest, family, repair["candidate_index"])
    revision_number = max(item["revision"] for item in entry["revisions"]) + 1
    output = (
        path.parent
        / "candidates"
        / (f"{family}_{repair['candidate_index']}.revision{revision_number}.md")
    )
    temp = output.with_name(f".{output.name}.{secrets.token_hex(4)}.tmp")
    temp.write_text(revised, encoding="utf-8")
    os.replace(temp, output)
    digest = sha256_bytes(revised.encode("utf-8"))
    base_revision = get_revision(entry, repair["base_revision"])
    finding_ids = sorted(
        set(base_revision["finding_ids"])
        | {
            finding_id
            for replacement in result["replacements"]
            for finding_id in replacement["finding_ids"]
        }
    )
    finding_proofs = copy.deepcopy(base_revision.get("finding_proofs", {}))
    for replacement in result["replacements"]:
        for finding_id in replacement["finding_ids"]:
            new_text = replacement["new_text"]
            finding_proofs[finding_id] = {
                "text": new_text,
                "sha256": sha256_bytes(new_text.encode("utf-8")),
                "callout": (
                    "verification"
                    if "[!question] Verification note" in new_text
                    else "correction"
                ),
            }
    resolved_issues = sorted(
        {
            issue_id
            for replacement in result["replacements"]
            for issue_id in replacement["resolves"]
        }
    )
    revision = {
        "revision": revision_number,
        "kind": "repair",
        "parent_revision": repair["base_revision"],
        "output_path": str(output),
        "sha256": digest,
        "created_at": now_iso(),
        "resolved_issues": resolved_issues,
        "finding_ids": finding_ids,
        "finding_proofs": finding_proofs,
        "repair_record": len(state["repairs"]) - 1,
        "audit_status": "pending",
    }
    entry["revisions"].append(revision)
    entry.update(
        {
            "current_revision": revision_number,
            "output_path": str(output),
            "sha256": digest,
        }
    )
    repair.update(
        {
            "status": "valid",
            "failure": None,
            "result": result,
            "revision": revision_number,
            "sha256": digest,
            "output_sha256": sha256_file(Path(repair["output_path"])),
        }
    )
    state.update(
        {
            "status": "pending",
            "pending_issues": [],
            "pause_reason": None,
        }
    )
    refresh_global_audit_status(manifest)
    save_manifest(path, manifest)
    return {
        "status": "repaired",
        "run_id": args.run_id,
        "family": family,
        "candidate_index": repair["candidate_index"],
        "revision": revision_number,
        "sha256": digest,
        "next": {"prepare_audit": family},
    }


def resolve_repair_limit(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    family = args.family
    state = manifest["audit"]["families"][family]
    if state["status"] != "awaiting_user" or state["current_index"] is None:
        raise RunError(f"{family} is not awaiting repair-limit direction")
    index = state["current_index"]
    if args.action == "retry":
        key = str(index)
        state["extra_repairs"][key] = state["extra_repairs"].get(key, 0) + 1
        state["status"] = "repair_pending"
        state["pause_reason"] = None
        next_action: Any = {"prepare_repair": family}
    elif args.action == "advance":
        ranking = manifest["evaluations"][family]["result"]["ranking"]
        rejected = set(manifest["audit"]["rejected"][family]) | {index}
        if not any(candidate not in rejected for candidate in ranking):
            raise RunError(f"no next-ranked {family} candidate remains")
        manifest["audit"]["rejected"][family].append(index)
        state.update(
            {
                "status": "pending",
                "current_index": None,
                "pending_issues": [],
                "pause_reason": None,
            }
        )
        next_action = {"prepare_audit": family}
    else:
        raise RunError(f"invalid repair-limit action: {args.action}")
    refresh_global_audit_status(manifest)
    save_manifest(path, manifest)
    return {
        "status": state["status"],
        "run_id": args.run_id,
        "family": family,
        "action": args.action,
        "next": next_action,
    }


def integrity_check(
    manifest: dict[str, Any], *, verify_prompts: bool = True
) -> list[str]:
    failures: list[str] = []
    source = Path(manifest["source"]["path"])
    if not source.is_file():
        failures.append("source file is missing")
    elif sha256_file(source) != manifest["source"]["sha256"]:
        failures.append("source SHA-256 changed")
    if verify_prompts:
        for name, record in manifest["prompts"].items():
            prompt = Path(record["path"])
            if not prompt.is_file():
                failures.append(f"prompt {name} is missing")
            elif sha256_file(prompt) != record["sha256"]:
                failures.append(f"prompt {name} SHA-256 changed")
    for family in FAMILIES:
        for entry in manifest["candidates"][family]:
            revisions = entry.get("revisions") or []
            if manifest.get("schema_version") == SCHEMA_VERSION:
                if revisions and entry.get("status") != "valid":
                    failures.append(
                        f"candidate {family}_{entry['index']} validated status changed"
                    )
                if entry.get("status") == "valid" and not revisions:
                    failures.append(
                        f"candidate {family}_{entry['index']} lost its revision chain"
                    )
                if not revisions:
                    continue
            elif entry.get("status") != "valid":
                continue
            elif not revisions:
                revisions = [
                    {
                        "revision": 0,
                        "output_path": entry.get("output_path"),
                        "sha256": entry.get("sha256"),
                    }
                ]
            if manifest.get("schema_version") == SCHEMA_VERSION:
                numbers = [revision.get("revision") for revision in revisions]
                expected_numbers = list(range(len(revisions)))
                if numbers != expected_numbers:
                    failures.append(
                        f"candidate {family}_{entry['index']} revision chain is not contiguous"
                    )
                if (
                    entry.get("current_revision") != numbers[-1]
                    or entry.get("output_path") != revisions[-1].get("output_path")
                    or entry.get("sha256") != revisions[-1].get("sha256")
                ):
                    failures.append(
                        f"candidate {family}_{entry['index']} current revision pointer changed"
                    )
                for position, revision in enumerate(revisions):
                    if position == 0:
                        if (
                            revision.get("kind") != "generated"
                            or revision.get("parent_revision") is not None
                        ):
                            failures.append(
                                f"candidate {family}_{entry['index']} generated revision lineage changed"
                            )
                    elif (
                        revision.get("kind") != "repair"
                        or type(revision.get("parent_revision")) is not int
                        or not 0 <= revision["parent_revision"] < position
                    ):
                        failures.append(
                            f"candidate {family}_{entry['index']} repair revision lineage changed"
                        )
                    else:
                        repair_index = revision.get("repair_record")
                        repairs = manifest["audit"]["families"][family]["repairs"]
                        if type(repair_index) is not int or not 0 <= repair_index < len(
                            repairs
                        ):
                            failures.append(
                                f"candidate {family}_{entry['index']} repair record pointer changed"
                            )
                            continue
                        repair = repairs[repair_index]
                        if (
                            repair.get("status") != "valid"
                            or repair.get("candidate_index") != entry["index"]
                            or repair.get("base_revision")
                            != revision["parent_revision"]
                            or repair.get("revision") != revision["revision"]
                            or repair.get("sha256") != revision.get("sha256")
                        ):
                            failures.append(
                                f"candidate {family}_{entry['index']} repair record lineage changed"
                            )
            for revision in revisions:
                output_value = revision.get("output_path")
                if not output_value:
                    failures.append(
                        f"validated candidate {family}_{entry['index']} revision {revision['revision']} has no path"
                    )
                    continue
                output = Path(output_value)
                try:
                    content = output.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    failures.append(
                        f"validated candidate {family}_{entry['index']} revision {revision['revision']} is unreadable"
                    )
                    continue
                digest_source = (
                    content.strip()
                    if manifest.get("schema_version") == LEGACY_SCHEMA_VERSION
                    else content
                )
                digest = sha256_bytes(digest_source.encode("utf-8"))
                if digest != revision.get("sha256"):
                    failures.append(
                        f"validated candidate {family}_{entry['index']} revision {revision['revision']} SHA-256 changed"
                    )
                if manifest.get("schema_version") == SCHEMA_VERSION:
                    proofs = revision.get("finding_proofs", {})
                    if set(proofs) != set(revision.get("finding_ids", [])):
                        failures.append(
                            f"candidate {family}_{entry['index']} revision {revision['revision']} finding proof lineage changed"
                        )
                    for finding_id, proof in proofs.items():
                        proof_text = proof.get("text")
                        if (
                            not isinstance(proof_text, str)
                            or content.count(proof_text) != 1
                            or proof.get("sha256")
                            != sha256_bytes(proof_text.encode("utf-8"))
                            or proof.get("callout")
                            not in {"correction", "verification"}
                        ):
                            failures.append(
                                f"candidate {family}_{entry['index']} revision {revision['revision']} proof for {finding_id} changed"
                            )
    if manifest.get("schema_version") == SCHEMA_VERSION:
        for family, accepted in manifest.get("audit", {}).get("accepted", {}).items():
            try:
                entry = manifest["candidates"][family][accepted["index"]]
                revision = get_revision(entry, accepted["revision"])
            except (KeyError, IndexError, TypeError, RunError):
                failures.append(f"accepted {family} revision identity changed")
                continue
            if (
                entry.get("accepted_revision") != accepted["revision"]
                or revision["sha256"] != accepted.get("sha256")
                or revision.get("audit_status") != "pass"
            ):
                failures.append(f"accepted {family} revision record changed")
        review = manifest.get("technical_review", {})
        if (
            review.get("result") is not None or review.get("sha256") is not None
        ) and review.get("status") != "valid":
            failures.append("technical research validated status changed")
        if review.get("packet"):
            packet = review["packet"]
            mapping = packet.get("mapping", {})
            order = packet.get("order", [])
            if (
                set(mapping.values()) != set(range(CANDIDATE_COUNT))
                or len(mapping) != CANDIDATE_COUNT
                or order != list(mapping)
            ):
                failures.append("technical research candidate mapping changed")
            packet_path = Path(packet["path"])
            if (
                not packet.get("sha256")
                or not packet_path.is_file()
                or sha256_file(packet_path) != packet["sha256"]
            ):
                failures.append("technical research bundle SHA-256 changed")
        if review.get("status") == "valid":
            output = Path(review["output_path"])
            if (
                not review.get("sha256")
                or not output.is_file()
                or sha256_file(output) != review["sha256"]
            ):
                failures.append("technical research result SHA-256 changed")
            else:
                try:
                    reparsed_review = parse_technical_review(
                        read_json(output), manifest
                    )
                except RunError as exc:
                    failures.append(f"technical research result is invalid: {exc}")
                else:
                    if reparsed_review != review.get("result"):
                        failures.append("technical research findings record changed")
        for family in FAMILIES:
            evaluation = manifest["evaluations"][family]
            if (
                evaluation.get("result") is not None
                or evaluation.get("sha256") is not None
            ) and evaluation.get("status") != "valid":
                failures.append(f"{family} judge validated status changed")
            if evaluation.get("packet"):
                judge_packet = evaluation["packet"]
                mapping = judge_packet.get("mapping", {})
                basis = judge_packet.get("basis", {})
                if (
                    set(mapping.values()) != set(range(CANDIDATE_COUNT))
                    or len(mapping) != CANDIDATE_COUNT
                    or set(basis) != set(mapping)
                    or judge_packet.get("order") != list(mapping)
                ):
                    failures.append(f"{family} judge candidate mapping changed")
                else:
                    for alias, index in mapping.items():
                        revision = get_revision(
                            manifest["candidates"][family][index], 0
                        )
                        if basis[alias] != {
                            "index": index,
                            "revision": 0,
                            "sha256": revision["sha256"],
                        }:
                            failures.append(f"{family} judge basis changed")
                            break
                packet_path = Path(judge_packet["path"])
                if (
                    not judge_packet.get("sha256")
                    or not packet_path.is_file()
                    or sha256_file(packet_path) != judge_packet["sha256"]
                ):
                    failures.append(f"{family} judge packet SHA-256 changed")
            if evaluation.get("status") == "valid":
                output = Path(evaluation["output_path"])
                if (
                    not output.is_file()
                    or not evaluation.get("sha256")
                    or sha256_file(output) != evaluation["sha256"]
                ):
                    failures.append(f"{family} judge result SHA-256 changed")
                else:
                    try:
                        reparsed_evaluation = parse_evaluation(
                            read_json(output), family, evaluation["packet"], manifest
                        )
                    except RunError as exc:
                        failures.append(f"{family} judge result is invalid: {exc}")
                    else:
                        if reparsed_evaluation != evaluation.get("result"):
                            failures.append(f"{family} judge result record changed")
            state = manifest["audit"]["families"][family]
            for round_record in state["rounds"]:
                if (
                    round_record.get("result") is not None
                    or round_record.get("output_sha256") is not None
                ) and round_record.get("status") != "valid":
                    failures.append(f"{family} audit validated status changed")
                if round_record.get("bundle_path"):
                    bundle = Path(round_record["bundle_path"])
                    if (
                        not round_record.get("bundle_sha256")
                        or not bundle.is_file()
                        or sha256_file(bundle) != round_record["bundle_sha256"]
                    ):
                        failures.append(f"{family} audit packet SHA-256 changed")
                if round_record.get("evidence_path"):
                    evidence = Path(round_record["evidence_path"])
                    if (
                        not round_record.get("evidence_sha256")
                        or not evidence.is_file()
                        or sha256_file(evidence) != round_record["evidence_sha256"]
                    ):
                        failures.append(f"{family} audit evidence SHA-256 changed")
                if round_record.get("status") == "valid":
                    output = Path(round_record["output_path"])
                    if (
                        not round_record.get("output_sha256")
                        or not output.is_file()
                        or sha256_file(output) != round_record["output_sha256"]
                    ):
                        failures.append(f"{family} audit result SHA-256 changed")
                    else:
                        try:
                            reparsed_audit = parse_audit(
                                read_json(output), manifest, family, round_record
                            )
                        except RunError as exc:
                            failures.append(f"{family} audit result is invalid: {exc}")
                        else:
                            if reparsed_audit != round_record.get("result"):
                                failures.append(f"{family} audit result record changed")
            for repair in state["repairs"]:
                if (
                    repair.get("result") is not None
                    or repair.get("output_sha256") is not None
                ) and repair.get("status") != "valid":
                    failures.append(f"{family} repair validated status changed")
                if repair.get("packet_path"):
                    packet = Path(repair["packet_path"])
                    if (
                        not repair.get("packet_sha256")
                        or not packet.is_file()
                        or sha256_file(packet) != repair["packet_sha256"]
                    ):
                        failures.append(f"{family} repair packet SHA-256 changed")
                if repair.get("evidence_path"):
                    evidence = Path(repair["evidence_path"])
                    if (
                        not repair.get("evidence_sha256")
                        or not evidence.is_file()
                        or sha256_file(evidence) != repair["evidence_sha256"]
                    ):
                        failures.append(f"{family} repair evidence SHA-256 changed")
                if repair.get("status") == "valid":
                    output = Path(repair["output_path"])
                    if (
                        not repair.get("output_sha256")
                        or not output.is_file()
                        or sha256_file(output) != repair["output_sha256"]
                    ):
                        failures.append(f"{family} repair result SHA-256 changed")
                    else:
                        try:
                            reparsed_repair, revised = parse_repair(
                                read_json(output), manifest, family, repair
                            )
                        except RunError as exc:
                            failures.append(f"{family} repair result is invalid: {exc}")
                        else:
                            if reparsed_repair != repair.get("result"):
                                failures.append(
                                    f"{family} repair result record changed"
                                )
                            revision = get_revision(
                                manifest["candidates"][family][
                                    repair["candidate_index"]
                                ],
                                repair["revision"],
                            )
                            digest = sha256_bytes(revised.encode("utf-8"))
                            if digest != revision["sha256"]:
                                failures.append(
                                    f"{family} repaired revision content record changed"
                                )
    return failures


def next_action(manifest: dict[str, Any]) -> Any:
    for family in FAMILIES:
        for entry in manifest["candidates"][family]:
            if entry["status"] == "valid":
                continue
            target = {"family": family, "index": entry["index"]}
            if entry["status"] == "started":
                return {"validate_candidate": target}
            if entry["attempts"] < MAX_ATTEMPTS:
                return {"start_candidate": target}
            return f"retry limit exhausted for {family}_{entry['index']}"
    review = manifest["technical_review"]
    if review["status"] != "valid":
        if review["status"] == "started":
            return "record-technical-review"
        if review["attempts"] < MAX_ATTEMPTS:
            return "prepare-technical-review"
        return "retry limit exhausted for technical research"
    for family in FAMILIES:
        evaluation = manifest["evaluations"][family]
        if evaluation["status"] == "valid":
            continue
        if evaluation["status"] == "started":
            return {"record_evaluation": family}
        if evaluation["attempts"] < MAX_ATTEMPTS:
            return {"prepare_judge": family}
        return f"retry limit exhausted for {family} judge"
    if manifest["audit"]["status"] != "passed":
        for family in FAMILIES:
            state = manifest["audit"]["families"][family]
            if state["status"] == "started":
                return {"record_audit": family}
            if state["status"] == "repair_started":
                return {"record_repair": family}
            if state["status"] == "repair_pending":
                return {"prepare_repair": family}
            if state["status"] == "awaiting_user":
                return {
                    "await_user": {
                        "family": family,
                        "actions": repair_limit_actions(manifest, family),
                    }
                }
        for family in FAMILIES:
            state = manifest["audit"]["families"][family]
            if state["status"] == "accepted":
                continue
            if state["status"] == "failed":
                return f"retry limit exhausted for {family} workflow"
            return {"prepare_audit": family}
    if manifest["publication"]["status"] != "published":
        return "publish"
    return "complete"


def status_result(args: argparse.Namespace, *, resume: bool = False) -> dict[str, Any]:
    _, manifest = load_manifest(args, args.run_id, mutable=False)
    if manifest["schema_version"] == LEGACY_SCHEMA_VERSION:
        prompt_drift = []
        for name, record in manifest.get("prompts", {}).items():
            prompt = Path(record["path"])
            if not prompt.is_file() or sha256_file(prompt) != record["sha256"]:
                prompt_drift.append(name)
        result = {
            "status": manifest["status"],
            "run_id": manifest["run_id"],
            "schema_version": LEGACY_SCHEMA_VERSION,
            "read_only": True,
            "prompt_drift": prompt_drift,
            "source": {
                "input_file": manifest["source"]["input_file"],
                "session_date": manifest["source"]["session_date"],
                "topic": manifest["source"]["topic"],
                "sha256": manifest["source"]["sha256"],
            },
            "next": f"start a fresh {SCHEMA_VERSION} run",
        }
        if resume:
            result["resume_confirm_required"] = True
        return result
    result = {
        "status": manifest["status"],
        "run_id": manifest["run_id"],
        "schema_version": manifest["schema_version"],
        "read_only": False,
        "source": {
            "input_file": manifest["source"]["input_file"],
            "session_date": manifest["source"]["session_date"],
            "topic": manifest["source"]["topic"],
            "sha256": manifest["source"]["sha256"],
        },
        "candidates": {
            family: [
                {
                    "index": item["index"],
                    "status": item["status"],
                    "attempts": item["attempts"],
                    "current_revision": item["current_revision"],
                    "accepted_revision": item["accepted_revision"],
                }
                for item in manifest["candidates"][family]
            ]
            for family in FAMILIES
        },
        "evaluations": {
            family: {
                "status": manifest["evaluations"][family]["status"],
                "attempts": manifest["evaluations"][family]["attempts"],
            }
            for family in FAMILIES
        },
        "technical_review": {
            "status": manifest["technical_review"]["status"],
            "attempts": manifest["technical_review"]["attempts"],
            "findings": len(
                (manifest["technical_review"].get("result") or {}).get("findings", [])
            ),
        },
        "audit": {
            "status": manifest["audit"]["status"],
            "accepted": manifest["audit"]["accepted"],
            "rejected": manifest["audit"]["rejected"],
            "families": {
                family: {
                    "status": manifest["audit"]["families"][family]["status"],
                    "current_index": manifest["audit"]["families"][family][
                        "current_index"
                    ],
                    "repairs": len(manifest["audit"]["families"][family]["repairs"]),
                    "pause_reason": manifest["audit"]["families"][family][
                        "pause_reason"
                    ],
                }
                for family in FAMILIES
            },
        },
        "next": next_action(manifest),
    }
    if resume:
        result["resume_confirm_required"] = True
    return result


def frontmatter(
    manifest: dict[str, Any],
    summary_type: str,
    index: int | None = None,
    *,
    revision: int | None = None,
    publication_status: str = "published",
    audit_status: str | None = None,
    accepted: bool | None = None,
) -> str:
    source = manifest["source"]
    lines = [
        "---",
        f"date: {source['session_date']}",
        f"generated_at: {manifest['created_at']}",
        "WL Type: Walk & Learn",
        f"review-config_template: {SCHEMA_VERSION}",
        f"review-input_file: {source['input_file']}",
        f"review-input_sha256: {source['sha256']}",
        f"review-run_id: {manifest['run_id']}",
        f"review-summary_type: {summary_type}",
        f"review-publication_status: {publication_status}",
        f"review-audit_status: {audit_status or manifest['audit']['status']}",
    ]
    if index is not None:
        lines.append(f"review-candidate_index: {index}")
    if revision is not None:
        lines.append(f"review-candidate_revision: {revision}")
    if accepted is not None:
        lines.append(f"review-accepted: {'true' if accepted else 'false'}")
    lines.extend(["---", "", ""])
    return "\n".join(lines)


def render_evaluation(manifest: dict[str, Any], *, manual: bool = False) -> str:
    audit = manifest["audit"]
    parts = ["# ⚖️ WalkAndLearn Candidate Evaluation", ""]
    if manual:
        parts.extend(
            [
                "> [!WARNING] **Manual review export**",
                "> This run has not passed every audit gate and is not an accepted publication.",
                "",
            ]
        )
    for family in FAMILIES:
        accepted = audit["accepted"].get(family)
        if accepted:
            parts.append(
                f"- **Accepted {family} candidate:** `{family}_{accepted['index']}.md` revision `{accepted['revision']}`"
            )
        else:
            parts.append(f"- **Accepted {family} candidate:** none")
    parts.append(f"- **Audit status:** `{audit['status']}`")

    review = manifest.get("technical_review", {})
    if review.get("status") == "valid":
        result = review["result"]
        parts.extend(
            [
                "",
                "## 🔎 Technical correctness research",
                "",
                f"- **Findings:** {len(result['findings'])}",
                f"- **Confidence:** `{result['confidence']['level']}`",
                f"- {result['confidence']['reason']}",
            ]
        )
        for finding in result["findings"]:
            parts.extend(
                [
                    "",
                    f"### `{finding['finding_id']}`",
                    "",
                    f"- **Assessment:** `{finding['assessment']}`",
                    f"- **Kind:** `{finding['kind']}`",
                    f"- **Severity:** `{finding['severity']}`",
                    f"- **Guidance:** {finding['correction']}",
                ]
            )
            if finding["sources"]:
                parts.append("- **Sources:**")
                for source in finding["sources"]:
                    parts.append(
                        f"  - [{source['title']}]({source['url']}) · {source['publisher']}"
                    )

    for family in FAMILIES:
        evaluation = manifest["evaluations"][family]
        if evaluation["status"] != "valid":
            continue
        result = evaluation["result"]
        parts.extend(
            [
                "",
                f"## {'💡' if family == 'emotional' else '🛠️'} {family.capitalize()} ranking",
                "",
                f"**Confidence:** {result['confidence']['level']}  ",
                result["confidence"]["reason"],
                "",
                result["ranking_reason"],
            ]
        )
        for position, card in enumerate(result["scorecards"], start=1):
            index = card["candidate_index"]
            parts.extend(
                [
                    "",
                    f"### {position}. `{family}_{index}.md`",
                    "",
                    f"- **Judge basis:** revision `{card.get('candidate_revision', 0)}` · `{card.get('candidate_sha256', '')}`",
                    f"- **Weighted score:** {card['weighted_score']:.3f} / 5",
                    "",
                    "**Criterion scores**",
                    "",
                ]
            )
            for criterion, score in card["scores"].items():
                parts.append(f"- `{criterion}`: {score}/5")
            for label, key in (
                ("Evidence", "evidence"),
                ("Strengths", "strengths"),
                ("Omissions", "omissions"),
                ("Fidelity concerns", "fidelity_concerns"),
            ):
                parts.extend(["", f"**{label}**", ""])
                values = card[key]
                parts.extend(
                    f"- {value}" for value in values
                ) if values else parts.append("- None")

    parts.extend(["", "## 🔒 Audit and repair lineage", ""])
    for family in FAMILIES:
        state = audit["families"][family]
        parts.extend([f"### {family.capitalize()}", ""])
        for round_record in state["rounds"]:
            if round_record["status"] != "valid":
                continue
            result = round_record["result"]
            parts.append(
                f"- **Round {round_record['round']} · revision {round_record['revision']}:** `{result['verdict']}`"
            )
            parts.append(f"  - {result['reason']}")
            for source in result.get("sources", []):
                parts.append(
                    f"  - Source: [{source['title']}]({source['url']}) · {source['publisher']}"
                )
            for failure in result["hard_failures"]:
                parts.append(
                    f"  - `{failure['issue_id']}` · `{failure['code']}`: {failure['evidence']}"
                )
        for repair in state["repairs"]:
            if repair["status"] != "valid":
                continue
            parts.append(
                f"- **Repair {repair['semantic_round']}:** revision `{repair['base_revision']}` → `{repair['revision']}`"
            )
            for replacement in repair["result"]["replacements"]:
                parts.append(
                    f"  - Resolved {', '.join(f'`{item}`' for item in replacement['resolves'])}: {replacement['reason']}"
                )
        if not state["rounds"] and not state["repairs"]:
            parts.append("- No audit activity recorded.")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def revision_record_public(revision: dict[str, Any]) -> dict[str, Any]:
    return {
        "revision": revision["revision"],
        "kind": revision["kind"],
        "parent_revision": revision["parent_revision"],
        "sha256": revision["sha256"],
        "created_at": revision["created_at"],
        "resolved_issues": copy.deepcopy(revision["resolved_issues"]),
        "finding_ids": copy.deepcopy(revision["finding_ids"]),
        "finding_proofs": {
            finding_id: {
                "sha256": proof["sha256"],
                "callout": proof["callout"],
            }
            for finding_id, proof in revision.get("finding_proofs", {}).items()
        },
        "audit_status": revision["audit_status"],
    }


def selected_revision(entry: dict[str, Any], *, manual: bool) -> dict[str, Any]:
    if manual:
        target = entry["current_revision"]
    elif entry["accepted_revision"] is not None:
        target = entry["accepted_revision"]
    else:
        target = 0
    return get_revision(entry, target)


def candidate_is_accepted(
    manifest: dict[str, Any], family: str, index: int, revision: int
) -> bool:
    accepted = manifest["audit"]["accepted"].get(family)
    return bool(
        accepted and accepted["index"] == index and accepted["revision"] == revision
    )


def published_audit_status(revision: dict[str, Any]) -> str:
    return {"pass": "passed", "fail": "failed", "pending": "not-audited"}.get(
        revision["audit_status"], revision["audit_status"]
    )


def public_manifest(
    manifest: dict[str, Any],
    destination: Path,
    published_at: str,
    *,
    manual: bool = False,
) -> dict[str, Any]:
    source = copy.deepcopy(manifest["source"])
    source.pop("path", None)
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "status": "manual-review" if manual else "published",
        "created_at": manifest["created_at"],
        "published_at": published_at,
        "source": source,
        "prompts": {
            name: {"sha256": record["sha256"]}
            for name, record in manifest["prompts"].items()
        },
        "candidates": {
            family: [
                {
                    "index": item["index"],
                    "file": item["published_file"],
                    "revision": selected_revision(item, manual=manual)["revision"],
                    "sha256": selected_revision(item, manual=manual)["sha256"],
                    "audit_status": published_audit_status(
                        selected_revision(item, manual=manual)
                    ),
                    "accepted": candidate_is_accepted(
                        manifest,
                        family,
                        item["index"],
                        selected_revision(item, manual=manual)["revision"],
                    ),
                    "attempts": item["attempts"],
                    "accepted_revision": item["accepted_revision"],
                    "revisions": [
                        revision_record_public(revision)
                        for revision in item["revisions"]
                    ],
                }
                for item in manifest["candidates"][family]
            ]
            for family in FAMILIES
        },
        "technical_review": {
            "status": manifest["technical_review"]["status"],
            "sha256": manifest["technical_review"]["sha256"],
            "candidate_mapping": copy.deepcopy(
                (manifest["technical_review"].get("packet") or {}).get("mapping", {})
            ),
            "result": copy.deepcopy(manifest["technical_review"]["result"]),
        },
        "evaluations": {
            family: copy.deepcopy(manifest["evaluations"][family]["result"])
            for family in FAMILIES
        },
        "audit": {
            "status": manifest["audit"]["status"],
            "accepted": copy.deepcopy(manifest["audit"]["accepted"]),
            "rejected": copy.deepcopy(manifest["audit"]["rejected"]),
            "families": {
                family: {
                    "status": state["status"],
                    "current_index": state["current_index"],
                    "pause_reason": state["pause_reason"],
                    "rounds": [
                        {
                            "round": item["round"],
                            "candidate_index": item["candidate_index"],
                            "revision": item["revision"],
                            "candidate_sha256": item["candidate_sha256"],
                            "attempts": item["attempts"],
                            "status": item["status"],
                            "result": copy.deepcopy(item["result"]),
                        }
                        for item in state["rounds"]
                    ],
                    "repairs": [
                        {
                            "semantic_round": item["semantic_round"],
                            "candidate_index": item["candidate_index"],
                            "base_revision": item["base_revision"],
                            "base_sha256": item["base_sha256"],
                            "attempts": item["attempts"],
                            "status": item["status"],
                            "revision": item.get("revision"),
                            "sha256": item.get("sha256"),
                            "result": copy.deepcopy(item["result"]),
                        }
                        for item in state["repairs"]
                    ],
                }
                for family, state in manifest["audit"]["families"].items()
            },
        },
        "publication": {
            "status": "manual-review" if manual else "published",
            "path": str(destination),
            "files": 8,
            "manual": manual,
        },
    }


def publication_inventory() -> list[str]:
    return sorted(
        [
            f"{family}_{index}.md"
            for family in FAMILIES
            for index in range(CANDIDATE_COUNT)
        ]
        + ["evaluation.md", "run.json"]
    )


def publication_parent(manifest: dict[str, Any]) -> Path:
    output_base = Path(manifest["config"]["output_base"]).resolve()
    input_stem = Path(manifest["source"]["input_file"]).stem
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", input_stem):
        input_stem = (
            f"input-{manifest['source']['session_date']}-"
            f"{slugify(manifest['source']['topic'])}"
        )
    parent = (output_base / input_stem).resolve()
    if parent == output_base or not is_within(parent, output_base):
        raise RunError("publication parent escapes the configured output base")
    return parent


def run_has_repairs(manifest: dict[str, Any]) -> bool:
    return any(
        any(revision["kind"] == "repair" for revision in entry["revisions"])
        for family in FAMILIES
        for entry in manifest["candidates"][family]
    )


def validate_existing_publication(
    destination: Path, manifest: dict[str, Any]
) -> dict[str, Any]:
    files = sorted(item.name for item in destination.iterdir())
    expected = publication_inventory()
    if files != expected:
        raise RunError(
            f"existing publication has an unexpected inventory: {destination}"
        )
    visible = read_json(destination / "run.json")
    published_at = visible.get("published_at")
    if (
        visible.get("schema_version") != SCHEMA_VERSION
        or visible.get("run_id") != manifest["run_id"]
        or visible.get("status") != "published"
        or visible.get("source", {}).get("sha256") != manifest["source"]["sha256"]
        or visible.get("audit", {}).get("accepted") != manifest["audit"]["accepted"]
        or visible.get("publication", {}).get("path") != str(destination)
        or not isinstance(published_at, str)
        or not published_at
    ):
        raise RunError(
            f"publication destination belongs to a different run: {destination}"
        )
    expected_manifest = public_manifest(manifest, destination, published_at)
    if visible != expected_manifest:
        raise RunError("existing publication manifest content changed")
    for family in FAMILIES:
        visible_candidates = visible.get("candidates", {}).get(family)
        if not isinstance(visible_candidates, list) or len(visible_candidates) != 3:
            raise RunError("existing publication candidate inventory is invalid")
        for entry, public_entry in zip(
            manifest["candidates"][family], visible_candidates, strict=True
        ):
            revision = selected_revision(entry, manual=False)
            if (
                public_entry.get("index") != entry["index"]
                or public_entry.get("revision") != revision["revision"]
                or public_entry.get("sha256") != revision["sha256"]
            ):
                raise RunError("existing publication candidate identity mismatch")
            body = Path(revision["output_path"]).read_text(encoding="utf-8").strip()
            expected_content = (
                frontmatter(
                    manifest,
                    family,
                    entry["index"],
                    revision=revision["revision"],
                    audit_status=published_audit_status(revision),
                    accepted=candidate_is_accepted(
                        manifest,
                        family,
                        entry["index"],
                        revision["revision"],
                    ),
                )
                + body
                + "\n"
            )
            try:
                actual_content = (destination / entry["published_file"]).read_text(
                    encoding="utf-8"
                )
            except (OSError, UnicodeError) as exc:
                raise RunError("existing publication candidate is unreadable") from exc
            if actual_content != expected_content:
                raise RunError(
                    f"existing publication candidate content changed: {entry['published_file']}"
                )
    expected_evaluation = frontmatter(manifest, "evaluation") + render_evaluation(
        manifest
    )
    try:
        actual_evaluation = (destination / "evaluation.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RunError("existing publication evaluation is unreadable") from exc
    if actual_evaluation != expected_evaluation:
        raise RunError("existing publication evaluation content changed")
    return visible


def finish_publication_state(
    path: Path,
    manifest: dict[str, Any],
    destination: Path,
    published_at: str,
) -> bool:
    manual_exports = manifest["publication"].get("manual_exports", [])
    manifest["publication"] = {
        "status": "published",
        "path": str(destination),
        "published_at": published_at,
        "manual_exports": manual_exports,
    }
    manifest["status"] = "published"
    save_manifest(path, manifest)
    has_repairs = run_has_repairs(manifest)
    if not has_repairs:
        shutil.rmtree(path.parent)
    return has_repairs


def require_publication_ready(manifest: dict[str, Any]) -> None:
    if manifest["audit"]["status"] != "passed":
        raise RunError("run is not ready for publication")
    if not all_candidates_valid(manifest):
        raise RunError("all six candidates must be valid before publication")
    if manifest["technical_review"].get("status") != "valid" or any(
        manifest["evaluations"][family].get("status") != "valid" for family in FAMILIES
    ):
        raise RunError(
            "validated research and both judges are required for publication"
        )
    accepted = manifest["audit"].get("accepted", {})
    if set(accepted) != set(FAMILIES):
        raise RunError("accepted emotional and technical revisions are required")
    for family in FAMILIES:
        state = manifest["audit"]["families"][family]
        accepted_record = accepted[family]
        if state.get("status") != "accepted":
            raise RunError(f"{family} family acceptance state is inconsistent")
        matching_rounds = [
            round_record
            for round_record in state["rounds"]
            if round_record.get("status") == "valid"
            and (round_record.get("result") or {}).get("verdict") == "pass"
            and round_record.get("candidate_index") == accepted_record["index"]
            and round_record.get("revision") == accepted_record["revision"]
            and round_record.get("candidate_sha256") == accepted_record["sha256"]
        ]
        if len(matching_rounds) != 1:
            raise RunError(
                f"{family} accepted revision lacks one matching passed audit"
            )


def publish(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    require_publication_ready(manifest)
    parent = publication_parent(manifest)
    parent.mkdir(parents=True, exist_ok=True)
    destination = parent / manifest["run_id"]
    if destination.exists():
        if manifest["status"] not in {"ready", "published"}:
            raise RunError(f"publication destination already exists: {destination}")
        visible_manifest = validate_existing_publication(destination, manifest)
        has_repairs = finish_publication_state(
            path,
            manifest,
            destination,
            visible_manifest["published_at"],
        )
        return {
            "status": "published",
            "run_id": args.run_id,
            "folder": str(destination),
            "accepted": visible_manifest["audit"]["accepted"],
            "files": publication_inventory(),
            "staging_retained": has_repairs,
            "recovered": True,
        }
    if manifest["status"] != "ready":
        raise RunError("run is not ready for publication")
    temp = parent / f".{manifest['run_id']}.partial-{secrets.token_hex(3)}"
    temp.mkdir(parents=False, exist_ok=False)
    published_at = now_iso()
    try:
        for family in FAMILIES:
            for entry in manifest["candidates"][family]:
                revision = selected_revision(entry, manual=False)
                body = Path(revision["output_path"]).read_text(encoding="utf-8").strip()
                content = (
                    frontmatter(
                        manifest,
                        family,
                        entry["index"],
                        revision=revision["revision"],
                        audit_status=published_audit_status(revision),
                        accepted=candidate_is_accepted(
                            manifest,
                            family,
                            entry["index"],
                            revision["revision"],
                        ),
                    )
                    + body
                    + "\n"
                )
                (temp / entry["published_file"]).write_text(content, encoding="utf-8")
        evaluation = frontmatter(manifest, "evaluation") + render_evaluation(manifest)
        (temp / "evaluation.md").write_text(evaluation, encoding="utf-8")
        visible_manifest = public_manifest(manifest, destination, published_at)
        write_json_atomic(temp / "run.json", visible_manifest)
        files = sorted(item.name for item in temp.iterdir())
        expected = publication_inventory()
        if files != expected or any(name.startswith("result_") for name in files):
            raise RunError(f"publication inventory mismatch: {files}")
        os.replace(temp, destination)
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    has_repairs = finish_publication_state(path, manifest, destination, published_at)
    return {
        "status": "published",
        "run_id": args.run_id,
        "folder": str(destination),
        "accepted": visible_manifest["audit"]["accepted"],
        "files": expected,
        "staging_retained": has_repairs,
        "recovered": False,
    }


def next_manual_destination(parent: Path, run_id: str) -> Path:
    destination = parent / f"{run_id}-manual-review"
    suffix = 2
    while destination.exists():
        destination = parent / f"{run_id}-{suffix}-manual-review"
        suffix += 1
    return destination


def export_review(args: argparse.Namespace) -> dict[str, Any]:
    path, manifest = load_manifest(args, args.run_id)
    if manifest["status"] not in {"awaiting_user", "failed"}:
        raise RunError("manual review export requires an awaiting_user or failed run")
    if not all_candidates_valid(manifest):
        raise RunError("all six candidates must be valid before manual export")
    parent = publication_parent(manifest)
    parent.mkdir(parents=True, exist_ok=True)
    destination = next_manual_destination(parent, manifest["run_id"])
    temp = parent / f".{destination.name}.partial-{secrets.token_hex(3)}"
    temp.mkdir(parents=False, exist_ok=False)
    exported_at = now_iso()
    expected = sorted(
        [
            f"{family}_{index}.md"
            for family in FAMILIES
            for index in range(CANDIDATE_COUNT)
        ]
        + ["evaluation.md", "run.json"]
    )
    try:
        for family in FAMILIES:
            for entry in manifest["candidates"][family]:
                revision = selected_revision(entry, manual=True)
                body = Path(revision["output_path"]).read_text(encoding="utf-8").strip()
                content = (
                    frontmatter(
                        manifest,
                        family,
                        entry["index"],
                        revision=revision["revision"],
                        publication_status="manual-review",
                        audit_status=published_audit_status(revision),
                        accepted=candidate_is_accepted(
                            manifest,
                            family,
                            entry["index"],
                            revision["revision"],
                        ),
                    )
                    + body
                    + "\n"
                )
                (temp / entry["published_file"]).write_text(content, encoding="utf-8")
        evaluation = frontmatter(
            manifest,
            "evaluation",
            publication_status="manual-review",
        ) + render_evaluation(manifest, manual=True)
        (temp / "evaluation.md").write_text(evaluation, encoding="utf-8")
        visible_manifest = public_manifest(
            manifest, destination, exported_at, manual=True
        )
        write_json_atomic(temp / "run.json", visible_manifest)
        files = sorted(item.name for item in temp.iterdir())
        if files != expected or any(name.startswith("result_") for name in files):
            raise RunError(f"manual export inventory mismatch: {files}")
        os.replace(temp, destination)
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    manifest["publication"].setdefault("manual_exports", []).append(
        {"path": str(destination), "exported_at": exported_at}
    )
    save_manifest(path, manifest)
    return {
        "status": "manual-review",
        "run_id": args.run_id,
        "folder": str(destination),
        "files": expected,
        "run_status": manifest["status"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=lambda value: Path(value).expanduser().resolve(),
        default=Path(os.environ.get("WALKANDLEARN_REPO", DEFAULT_REPO)).resolve(),
    )
    parser.add_argument(
        "--output-base",
        type=lambda value: Path(value).expanduser().resolve(),
        default=Path(
            os.environ.get("WALKANDLEARN_OUTPUT_BASE", DEFAULT_OUTPUT_BASE)
        ).resolve(),
    )
    parser.add_argument(
        "--staging-root",
        default=os.environ.get("WALKANDLEARN_STAGING_ROOT"),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe")
    probe_source_group = probe.add_mutually_exclusive_group(required=True)
    probe_source_group.add_argument("--clipboard", action="store_true")
    probe_source_group.add_argument("--file")
    probe.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)

    init = sub.add_parser("init")
    source = init.add_mutually_exclusive_group(required=True)
    source.add_argument("--clipboard", action="store_true")
    source.add_argument("--file")
    init.add_argument("--date", required=True)
    init.add_argument("--topic", required=True)
    init.add_argument("--reuse-canonical", action="store_true")
    init.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)

    for name in (
        "status",
        "resume",
        "prepare-technical-review",
        "record-technical-review",
        "publish",
        "export-review",
    ):
        command = sub.add_parser(name)
        command.add_argument("run_id")

    for name in ("prepare-audit", "record-audit", "prepare-repair", "record-repair"):
        command = sub.add_parser(name)
        command.add_argument("run_id")
        command.add_argument("--family", choices=FAMILIES, required=True)

    resolve = sub.add_parser("resolve-repair-limit")
    resolve.add_argument("run_id")
    resolve.add_argument("--family", choices=FAMILIES, required=True)
    resolve.add_argument("--action", choices=("retry", "advance"), required=True)

    candidate = sub.add_parser("start-candidate")
    candidate.add_argument("run_id")
    candidate.add_argument("--family", choices=FAMILIES, required=True)
    candidate.add_argument("--index", type=int, required=True)

    validation = sub.add_parser("validate-candidate")
    validation.add_argument("run_id")
    validation.add_argument("--family", choices=FAMILIES, required=True)
    validation.add_argument("--index", type=int, required=True)

    judge = sub.add_parser("prepare-judge")
    judge.add_argument("run_id")
    judge.add_argument("--family", choices=FAMILIES, required=True)

    evaluation = sub.add_parser("record-evaluation")
    evaluation.add_argument("run_id")
    evaluation.add_argument("--family", choices=FAMILIES, required=True)
    return parser


def dispatch(args: argparse.Namespace) -> dict[str, Any]:
    handlers = {
        "probe": probe_source,
        "init": init_run,
        "start-candidate": start_candidate,
        "validate-candidate": validate_candidate,
        "prepare-technical-review": prepare_technical_review,
        "record-technical-review": record_technical_review,
        "prepare-judge": prepare_judge,
        "record-evaluation": record_evaluation,
        "prepare-audit": prepare_audit,
        "record-audit": record_audit,
        "prepare-repair": prepare_repair,
        "record-repair": record_repair,
        "resolve-repair-limit": resolve_repair_limit,
        "status": status_result,
        "resume": lambda value: status_result(value, resume=True),
        "publish": publish,
        "export-review": export_review,
    }
    return handlers[args.command](args)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = dispatch(args)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
