#!/usr/bin/env python3
"""Validate newsletter briefs and enforce the 24-hour run guard."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo


EXPECTED_KEYS = (
    "date",
    "brief from",
    "brief until",
    "brief emails",
    "modified",
    "created",
)
LONDON = ZoneInfo("Europe/London")
REQUIRED_HEADINGS = (
    "# ⚡ The 30-second Version",
    "# 🧭 Attention Map",
    "# 🏁 Final Verdict",
    "## 🧠 Keep in Your Head",
    "## 💤 You Safely Skipped",
    "## 🧾 Everything Else",
    "## ✨ Best Line of the Batch",
)
DEFINITION_RE = re.compile(
    r"^\[\^(?P<label>[^\]]+)\]: "
    r"\[(?P<title>.+)\]\((?P<url>https://app\.fastmail\.com/mail/"
    r"search:msgid:[^)\s]+)\)\s*$"
)
REFERENCE_RE = re.compile(r"\[\^([^\]]+)\]")
FASTMAIL_URL_RE = re.compile(
    r"https://app\.fastmail\.com/mail/search:msgid:[^/\s)]+/[^)\s]+"
)


class BriefValidationError(ValueError):
    """Raised when a brief violates the format contract."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def editorial_warnings(body: str, email_count: int) -> list[str]:
    """Return non-blocking diagnostics for editorial flattening."""

    lines = body.splitlines()
    positions: dict[str, int] = {}
    for heading in REQUIRED_HEADINGS:
        matches = [index for index, line in enumerate(lines) if line == heading]
        if len(matches) != 1:
            return []
        positions[heading] = matches[0]

    ordered = [positions[heading] for heading in REQUIRED_HEADINGS]
    if ordered != sorted(ordered):
        return []

    warnings: list[str] = []
    attention = positions["# 🧭 Attention Map"]
    final = positions["# 🏁 Final Verdict"]
    thematic_indices = [
        index
        for index in range(attention + 1, final)
        if lines[index].startswith("# ")
    ]

    for offset, start in enumerate(thematic_indices):
        end = (
            thematic_indices[offset + 1]
            if offset + 1 < len(thematic_indices)
            else final
        )
        section_lines = lines[start + 1 : end]
        source_refs = set(REFERENCE_RE.findall("\n".join(section_lines)))
        has_atomic_h2 = any(line.startswith("## ") for line in section_lines)
        if len(source_refs) >= 3 and not has_atomic_h2:
            warnings.append(
                f"umbrella section '{lines[start][2:]}' cites "
                f"{len(source_refs)} sources but contains no atomic H2"
            )

    if email_count >= 10:
        thematic_refs = set(
            REFERENCE_RE.findall("\n".join(lines[attention + 1 : final]))
        )
        if len(thematic_refs) / email_count >= 0.8:
            percentage = round(len(thematic_refs) / email_count * 100)
            warnings.append(
                "thematic body references "
                f"{len(thematic_refs)} of {email_count} sources ({percentage}%); "
                "confirm that weak material was not promoted"
            )

        everything_else = positions["## 🧾 Everything Else"]
        best_line = positions["## ✨ Best Line of the Batch"]
        remainder_refs = set(
            REFERENCE_RE.findall(
                "\n".join(lines[everything_else + 1 : best_line])
            )
        )
        if not remainder_refs:
            warnings.append(
                "Everything Else contains no source references; confirm that "
                "weak, repetitive, and incidental sources were handled there"
            )

    return warnings


def parse_datetime(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a UTC offset")
    return parsed


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise BriefValidationError(["missing opening frontmatter delimiter"])
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise BriefValidationError(["missing closing frontmatter delimiter"]) from exc

    properties: dict[str, Any] = {}
    errors: list[str] = []
    for raw_line in lines[1:end]:
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            errors.append(f"invalid frontmatter line: {raw_line}")
            continue
        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if key in properties:
            errors.append(f"duplicate frontmatter property: {key}")
            continue
        if key == "brief emails":
            try:
                properties[key] = int(value)
            except ValueError:
                properties[key] = value
        else:
            properties[key] = value
    if errors:
        raise BriefValidationError(errors)
    return properties, "\n".join(lines[end + 1 :])


def expected_fastmail_url(message_id: str, email_id: str) -> str:
    normalized = message_id.strip()
    if normalized.startswith("<") and normalized.endswith(">"):
        normalized = normalized[1:-1]
    return (
        "https://app.fastmail.com/mail/search:msgid:"
        f"{quote(normalized, safe='')}/{quote(email_id, safe='')}"
    )


def validate_properties(
    properties: dict[str, Any],
    expected_count: int | None = None,
    expected_from: str | None = None,
    expected_until: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    if tuple(properties) != EXPECTED_KEYS:
        missing = [key for key in EXPECTED_KEYS if key not in properties]
        extra = [key for key in properties if key not in EXPECTED_KEYS]
        if missing:
            errors.append(f"missing frontmatter properties: {', '.join(missing)}")
        if extra:
            errors.append(f"unexpected frontmatter properties: {', '.join(extra)}")
        if not missing and not extra:
            errors.append("frontmatter properties are in the wrong order")

    email_count = properties.get("brief emails")
    if isinstance(email_count, bool) or not isinstance(email_count, int):
        errors.append("brief emails must be an integer")
    elif email_count < 1:
        errors.append("brief emails must be at least 1")
    elif expected_count is not None and email_count != expected_count:
        errors.append(
            f"brief emails is {email_count}, expected {expected_count}"
        )

    parsed: dict[str, datetime] = {}
    for field in ("brief from", "brief until", "modified", "created"):
        if field not in properties:
            continue
        try:
            parsed[field] = parse_datetime(properties[field], field)
        except ValueError as exc:
            errors.append(str(exc))

    for field, value in parsed.items():
        london_value = value.astimezone(LONDON)
        if value.utcoffset() != london_value.utcoffset():
            errors.append(f"{field} does not use the Europe/London UTC offset")

    if "brief from" in parsed and "brief until" in parsed:
        if parsed["brief from"] > parsed["brief until"]:
            errors.append("brief from must not be later than brief until")

    if "created" in parsed and "modified" in parsed:
        if parsed["modified"] < parsed["created"]:
            errors.append("modified must not be earlier than created")

    raw_date = properties.get("date")
    try:
        parsed_date = date.fromisoformat(raw_date) if isinstance(raw_date, str) else None
    except ValueError:
        parsed_date = None
    if parsed_date is None:
        errors.append("date must use YYYY-MM-DD")
    elif "created" in parsed:
        if parsed_date != parsed["created"].astimezone(LONDON).date():
            errors.append("date must equal the London creation date")

    comparisons = (
        ("brief from", expected_from),
        ("brief until", expected_until),
    )
    for field, expected_value in comparisons:
        if expected_value is None or field not in parsed:
            continue
        try:
            expected_dt = parse_datetime(expected_value, f"expected {field}")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if parsed[field].astimezone(timezone.utc) != expected_dt.astimezone(timezone.utc):
            errors.append(f"{field} does not match the expected timestamp")

    if errors:
        raise BriefValidationError(errors)
    return {**properties, **parsed}


def validate_structure(body: str, email_count: int) -> dict[str, Any]:
    errors: list[str] = []
    warnings = editorial_warnings(body, email_count)
    lines = body.splitlines()
    heading_positions: dict[str, int] = {}
    for heading in REQUIRED_HEADINGS:
        positions = [index for index, line in enumerate(lines) if line == heading]
        if len(positions) != 1:
            errors.append(f"required heading must appear exactly once: {heading}")
        else:
            heading_positions[heading] = positions[0]

    if len(heading_positions) == len(REQUIRED_HEADINGS):
        ordered = [heading_positions[heading] for heading in REQUIRED_HEADINGS]
        if ordered != sorted(ordered):
            errors.append("required headings are in the wrong order")
        attention = heading_positions["# 🧭 Attention Map"]
        final = heading_positions["# 🏁 Final Verdict"]
        thematic = [
            line
            for line in lines[attention + 1 : final]
            if line.startswith("# ") and not line.startswith("## ")
        ]
        if not thematic:
            errors.append("at least one thematic level-one section is required")

    for index, line in enumerate(lines):
        if not line.startswith("> [!"):
            continue
        heading = index - 1
        while heading >= 0 and not lines[heading].startswith("#"):
            heading -= 1
        intervening = [
            candidate
            for candidate in lines[heading + 1 : index]
            if candidate.strip()
        ]
        if heading < 0 or any(
            not candidate.startswith(">") for candidate in intervening
        ):
            errors.append(
                f"callout on body line {index + 1} is not in the opening callout group"
            )

    definitions: dict[str, str] = {}
    definition_urls: list[str] = []
    body_without_definitions: list[str] = []
    for line in lines:
        if not line.startswith("[^"):
            body_without_definitions.append(line)
            continue
        match = DEFINITION_RE.match(line)
        if not match:
            errors.append(f"malformed footnote definition: {line}")
            continue
        label = match.group("label")
        title = match.group("title")
        url = match.group("url")
        if label in definitions:
            errors.append(f"duplicate footnote definition: {label}")
        definitions[label] = url
        definition_urls.append(url)
        if not re.match(r"^\[\*\*.+\*\* - .+\]$", f"[{title}]"):
            errors.append(f"footnote {label} must use **Sender** - Subject")

    expected_labels = {str(index) for index in range(1, email_count + 1)}
    actual_labels = set(definitions)
    if actual_labels != expected_labels:
        missing = sorted(expected_labels - actual_labels, key=int)
        extra = sorted(actual_labels - expected_labels)
        if missing:
            errors.append(f"missing footnote definitions: {', '.join(missing)}")
        if extra:
            errors.append(f"unexpected footnote definitions: {', '.join(extra)}")

    references = Counter(
        REFERENCE_RE.findall("\n".join(body_without_definitions))
    )
    unused = sorted(
        (label for label in actual_labels if references[label] == 0),
        key=lambda item: int(item) if item.isdigit() else item,
    )
    if unused:
        errors.append(f"unused footnote definitions: {', '.join(unused)}")
    unknown = sorted(set(references) - actual_labels)
    if unknown:
        errors.append(f"references without definitions: {', '.join(unknown)}")

    duplicate_urls = [
        url for url, count in Counter(definition_urls).items() if count > 1
    ]
    if duplicate_urls:
        errors.append("duplicate Fastmail source URLs are not allowed")

    all_fastmail_urls = FASTMAIL_URL_RE.findall(body)
    if Counter(all_fastmail_urls) != Counter(definition_urls):
        errors.append("Fastmail links must appear exactly once in footnote definitions")

    if errors:
        raise BriefValidationError(errors)
    return {
        "footnotes": definitions,
        "references": references,
        "urls": definition_urls,
        "warnings": warnings,
    }


def load_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BriefValidationError([f"cannot read manifest: {exc}"]) from exc
    if not isinstance(payload, list) or not payload:
        raise BriefValidationError(["manifest must be a non-empty JSON array"])
    required = {"id", "threadId", "messageId", "subject", "from", "receivedAt"}
    required_strings = {"id", "threadId", "messageId", "subject", "receivedAt"}
    errors: list[str] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            errors.append(f"manifest item {index} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(
                f"manifest item {index} is missing: {', '.join(missing)}"
            )
            continue
        invalid_strings = sorted(
            field
            for field in required_strings
            if not isinstance(item[field], str) or not item[field].strip()
        )
        if invalid_strings:
            errors.append(
                f"manifest item {index} has invalid strings: "
                f"{', '.join(invalid_strings)}"
            )
        if item["from"] is None or item["from"] == "":
            errors.append(f"manifest item {index} has an empty from value")
    ids = [item.get("id") for item in payload if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append("manifest email IDs must be unique")
    if errors:
        raise BriefValidationError(errors)
    return payload


def validate_note(
    note_path: Path,
    manifest_path: Path | None = None,
    expected_count: int | None = None,
    expected_from: str | None = None,
    expected_until: str | None = None,
) -> dict[str, Any]:
    try:
        text = note_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BriefValidationError([f"cannot read note: {exc}"]) from exc

    properties, body = parse_frontmatter(text)
    manifest: list[dict[str, Any]] | None = None
    if manifest_path is not None:
        manifest = load_manifest(manifest_path)
        expected_count = len(manifest)
        try:
            received = [
                parse_datetime(item["receivedAt"], "manifest receivedAt")
                for item in manifest
            ]
        except ValueError as exc:
            raise BriefValidationError([str(exc)]) from exc
        expected_from = min(received).astimezone(LONDON).isoformat(timespec="seconds")
        expected_until = max(received).astimezone(LONDON).isoformat(timespec="seconds")

    validated_properties = validate_properties(
        properties,
        expected_count=expected_count,
        expected_from=expected_from,
        expected_until=expected_until,
    )
    structure = validate_structure(body, validated_properties["brief emails"])

    if manifest is not None:
        expected_urls = {
            expected_fastmail_url(item["messageId"], item["id"])
            for item in manifest
        }
        actual_urls = set(structure["urls"])
        missing = sorted(expected_urls - actual_urls)
        extra = sorted(actual_urls - expected_urls)
        errors: list[str] = []
        if missing:
            errors.append(f"missing manifest source URLs: {', '.join(missing)}")
        if extra:
            errors.append(f"unexpected source URLs: {', '.join(extra)}")
        if errors:
            raise BriefValidationError(errors)

    return {
        "note": str(note_path),
        "brief_emails": validated_properties["brief emails"],
        "brief_from": validated_properties["brief from"].isoformat(),
        "brief_until": validated_properties["brief until"].isoformat(),
        "created": validated_properties["created"].isoformat(),
        "footnotes": len(structure["footnotes"]),
        "warnings": structure["warnings"],
    }


def evaluate_guard(brief_dir: Path, now: datetime | None = None) -> dict[str, Any]:
    if not brief_dir.is_dir():
        return {
            "status": "no_checkpoint",
            "brief_dir": str(brief_dir),
            "reason": "brief directory does not exist",
        }

    valid: list[tuple[Path, dict[str, Any]]] = []
    invalid: list[dict[str, Any]] = []
    for path in sorted(brief_dir.glob("*.md")):
        try:
            result = validate_note(path)
        except BriefValidationError as exc:
            invalid.append({"path": str(path), "errors": exc.errors})
        else:
            valid.append((path, result))

    if invalid:
        return {
            "status": "invalid",
            "brief_dir": str(brief_dir),
            "invalid_briefs": invalid,
        }
    if not valid:
        return {
            "status": "no_checkpoint",
            "brief_dir": str(brief_dir),
            "reason": "no valid briefs found",
        }

    created_entry = max(
        valid,
        key=lambda entry: parse_datetime(entry[1]["created"], "created"),
    )
    checkpoint_entry = max(
        valid,
        key=lambda entry: parse_datetime(entry[1]["brief_until"], "brief until"),
    )
    latest_created = parse_datetime(created_entry[1]["created"], "created")
    checkpoint = parse_datetime(
        checkpoint_entry[1]["brief_until"], "brief until"
    )
    next_eligible = (
        latest_created.astimezone(timezone.utc) + timedelta(hours=24)
    ).astimezone(LONDON)
    current = now or datetime.now(LONDON)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must include a UTC offset")

    status = (
        "too_soon"
        if current.astimezone(timezone.utc) < next_eligible.astimezone(timezone.utc)
        else "ok"
    )
    return {
        "status": status,
        "latest_created": latest_created.astimezone(LONDON).isoformat(
            timespec="seconds"
        ),
        "latest_created_file": str(created_entry[0]),
        "next_eligible": next_eligible.isoformat(timespec="seconds"),
        "checkpoint": checkpoint.astimezone(LONDON).isoformat(timespec="seconds"),
        "checkpoint_file": str(checkpoint_entry[0]),
        "now": current.astimezone(LONDON).isoformat(timespec="seconds"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--note", type=Path, required=True)
    validate_parser.add_argument("--manifest", type=Path)
    validate_parser.add_argument("--expected-count", type=int)
    validate_parser.add_argument("--expected-from")
    validate_parser.add_argument("--expected-until")

    guard_parser = subparsers.add_parser("guard")
    guard_parser.add_argument("--brief-dir", type=Path, required=True)
    guard_parser.add_argument(
        "--now",
        help="Testing override as an offset-aware ISO timestamp",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "validate":
        try:
            result = validate_note(
                args.note,
                manifest_path=args.manifest,
                expected_count=args.expected_count,
                expected_from=args.expected_from,
                expected_until=args.expected_until,
            )
        except BriefValidationError as exc:
            print(json.dumps({"status": "invalid", "errors": exc.errors}, indent=2))
            return 2
        print(json.dumps({"status": "ok", **result}, indent=2))
        return 0

    now = parse_datetime(args.now, "now") if args.now else None
    result = evaluate_guard(args.brief_dir, now=now)
    print(json.dumps(result, indent=2))
    return {
        "ok": 0,
        "too_soon": 3,
        "no_checkpoint": 4,
        "invalid": 5,
    }[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
