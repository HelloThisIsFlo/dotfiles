from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).parents[1] / "validate_brief.py"
SPEC = importlib.util.spec_from_file_location("validate_brief", SCRIPT_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
SKILL_ROOT = Path(__file__).parents[2]


MANIFEST = [
    {
        "id": "email-one",
        "threadId": "thread-one",
        "messageId": "one@example.com",
        "subject": "First source",
        "from": "Sender One <one@example.com>",
        "receivedAt": "2026-07-24T08:00:00Z",
    },
    {
        "id": "email-two",
        "threadId": "thread-two",
        "messageId": "<two@example.com>",
        "subject": "Second source",
        "from": "Sender Two <two@example.com>",
        "receivedAt": "2026-07-24T10:00:00Z",
    },
]


def valid_note() -> str:
    first_url = VALIDATOR.expected_fastmail_url("one@example.com", "email-one")
    second_url = VALIDATOR.expected_fastmail_url(
        "<two@example.com>", "email-two"
    )
    return f"""---
date: 2026-07-24
brief from: 2026-07-24T09:00:00+01:00
brief until: 2026-07-24T11:00:00+01:00
brief emails: 2
modified: 2026-07-24T12:00:00+01:00
created: 2026-07-24T12:00:00+01:00
---

# ⚡ The 30-second Version

| Signal | Theme | What matters |
|---|---|---|
| 🔥 | Example | A useful signal |

# 🧭 Attention Map

| Priority | Newsletters | Verdict |
|---|---:|---|
| 🔥 **High signal** | 1 | Worth retaining |

# 🔥 Main Signal

> [!important] Useful idea
>
> - The first point matters.[^1]

The second source adds context.[^2]

# 🏁 Final Verdict

## 🧠 Keep in Your Head

- Remember the useful idea.

## 💤 You Safely Skipped

- Nothing important.

## 🧾 Everything Else

Everything was covered above.

## ✨ Best Line of the Batch

> Keep the signal and lose the noise.

[^1]: [**Sender One** - First source]({first_url})
[^2]: [**Sender Two** - Second source]({second_url})
"""


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.note_path = self.root / "Brief.md"
        self.manifest_path = self.root / "manifest.json"
        self.note_path.write_text(valid_note(), encoding="utf-8")
        self.manifest_path.write_text(json.dumps(MANIFEST), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate(self) -> dict:
        return VALIDATOR.validate_note(self.note_path, self.manifest_path)

    def test_valid_brief(self) -> None:
        result = self.validate()
        self.assertEqual(result["brief_emails"], 2)
        self.assertEqual(result["footnotes"], 2)
        self.assertEqual(result["warnings"], [])

    def test_missing_footnote_is_rejected(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        text = "\n".join(
            line for line in text.splitlines() if not line.startswith("[^2]:")
        )
        self.note_path.write_text(text, encoding="utf-8")
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_duplicate_source_url_is_rejected(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        first_url = VALIDATOR.expected_fastmail_url(
            "one@example.com", "email-one"
        )
        second_url = VALIDATOR.expected_fastmail_url(
            "<two@example.com>", "email-two"
        )
        self.note_path.write_text(
            text.replace(second_url, first_url),
            encoding="utf-8",
        )
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_wrong_count_is_rejected(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        self.note_path.write_text(
            text.replace("brief emails: 2", "brief emails: 3"),
            encoding="utf-8",
        )
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_wrong_timestamp_is_rejected(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        self.note_path.write_text(
            text.replace(
                "brief until: 2026-07-24T11:00:00+01:00",
                "brief until: 2026-07-24T11:01:00+01:00",
            ),
            encoding="utf-8",
        )
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_extra_frontmatter_is_rejected(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        self.note_path.write_text(
            text.replace("created: ", "title: Bad\ncreated: "),
            encoding="utf-8",
        )
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_malformed_fastmail_link_is_rejected(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        self.note_path.write_text(
            text.replace(
                "https://app.fastmail.com/mail/search:msgid:",
                "https://app.fastmail.com/mail/wrong:",
                1,
            ),
            encoding="utf-8",
        )
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_invalid_manifest_timestamp_is_rejected_cleanly(self) -> None:
        manifest = [dict(item) for item in MANIFEST]
        manifest[0]["receivedAt"] = "not-a-timestamp"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_missing_manifest_identifier_is_rejected(self) -> None:
        manifest = [dict(item) for item in MANIFEST]
        del manifest[0]["messageId"]
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_incorrect_section_order_is_rejected(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        text = text.replace(
            "## 🧠 Keep in Your Head",
            "## TEMP",
        ).replace(
            "## 💤 You Safely Skipped",
            "## 🧠 Keep in Your Head",
        ).replace(
            "## TEMP",
            "## 💤 You Safely Skipped",
        )
        self.note_path.write_text(text, encoding="utf-8")
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()

    def test_consecutive_opening_callouts_are_allowed(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        text = text.replace(
            "The second source adds context.[^2]",
            "> [!note] Second opening callout\n>\n> - More context.[^2]",
        )
        self.note_path.write_text(text, encoding="utf-8")
        self.validate()

    def test_late_callout_is_rejected(self) -> None:
        text = self.note_path.read_text(encoding="utf-8")
        text = text.replace(
            "The second source adds context.[^2]",
            "Ordinary section content.\n\n> [!note] Too late\n>\n> - More context.[^2]",
        )
        self.note_path.write_text(text, encoding="utf-8")
        with self.assertRaises(VALIDATOR.BriefValidationError):
            self.validate()


class GuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "Brief.md").write_text(valid_note(), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def status_at(self, timestamp: str) -> dict:
        now = datetime.fromisoformat(timestamp)
        return VALIDATOR.evaluate_guard(self.root, now=now)

    def test_just_under_24_hours_is_blocked(self) -> None:
        result = self.status_at("2026-07-25T11:59:59+01:00")
        self.assertEqual(result["status"], "too_soon")
        self.assertEqual(result["next_eligible"], "2026-07-25T12:00:00+01:00")

    def test_exactly_24_hours_is_allowed(self) -> None:
        self.assertEqual(
            self.status_at("2026-07-25T12:00:00+01:00")["status"],
            "ok",
        )

    def test_over_24_hours_is_allowed(self) -> None:
        self.assertEqual(
            self.status_at("2026-07-25T12:00:01+01:00")["status"],
            "ok",
        )

    def test_warnings_do_not_change_guard_eligibility(self) -> None:
        validated = {
            "created": "2026-07-24T12:00:00+01:00",
            "brief_until": "2026-07-24T11:00:00+01:00",
            "warnings": ["non-blocking editorial warning"],
        }
        with patch.object(VALIDATOR, "validate_note", return_value=validated):
            result = self.status_at("2026-07-25T12:00:00+01:00")
        self.assertEqual(result["status"], "ok")


class EditorialWarningTests(unittest.TestCase):
    @staticmethod
    def body(thematic: str, everything_else: str = "Reviewed.[^10]") -> str:
        return f"""# ⚡ The 30-second Version

# 🧭 Attention Map

{thematic}

# 🏁 Final Verdict

## 🧠 Keep in Your Head

Keep the signal.

## 💤 You Safely Skipped

Skip the noise.

## 🧾 Everything Else

{everything_else}

## ✨ Best Line of the Batch

> Keep the useful ideas.
"""

    def test_atomic_h2_structure_has_no_umbrella_warning(self) -> None:
        body = self.body(
            """# 🔥 Engineering

## 🤖 Architecture-aware Agents

One mechanism.[^1][^2][^3]"""
        )
        warnings = VALIDATOR.editorial_warnings(body, 10)
        self.assertFalse(
            any(warning.startswith("umbrella section") for warning in warnings)
        )

    def test_citation_heavy_h1_without_h2_warns(self) -> None:
        body = self.body(
            """# 🔥 Broad Engineering Theme

Three independent sources.[^1][^2][^3]"""
        )
        warnings = VALIDATOR.editorial_warnings(body, 10)
        self.assertTrue(
            any(warning.startswith("umbrella section") for warning in warnings)
        )

    def test_over_inclusive_thematic_body_warns_at_eighty_percent(self) -> None:
        references = "".join(f"[^{index}]" for index in range(1, 9))
        body = self.body(
            f"""# 🔥 Engineering

## 🤖 Atomic Idea

Eight sources.{references}""",
            everything_else="Two weak sources.[^9][^10]",
        )
        warnings = VALIDATOR.editorial_warnings(body, 10)
        self.assertTrue(
            any(
                warning.startswith("thematic body references")
                for warning in warnings
            )
        )

    def test_empty_everything_else_warns(self) -> None:
        body = self.body(
            """# 🔥 Engineering

## 🤖 Atomic Idea

One source.[^1]""",
            everything_else="Everything was covered above.",
        )
        warnings = VALIDATOR.editorial_warnings(body, 10)
        self.assertTrue(
            any(
                warning.startswith("Everything Else contains")
                for warning in warnings
            )
        )


class MetadataTests(unittest.TestCase):
    def test_skill_is_manual_only(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("explicitly invokes $generate-newsletter-brief", skill)
        self.assertIn("allow_implicit_invocation: false", metadata)

    def test_editorial_calibration_contract(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        format_reference = (
            SKILL_ROOT / "references" / "brief-format.md"
        ).read_text(encoding="utf-8")

        self.assertIn("accepted editorial", skill)
        self.assertIn("compact editorial map", skill)
        self.assertIn("Dedicated H2", skill)
        self.assertIn("flattened beneath umbrella sections", skill)
        self.assertIn("rebuild it once from the editorial map", skill)
        self.assertIn("Do not force unrelated sources", skill)
        self.assertIn("accepted editorial calibration example", format_reference)
        self.assertIn("primary unit of memorable synthesis", format_reference)
        self.assertIn("Do not give every email substantial", format_reference)
        self.assertIn("Do not copy its content", format_reference)


if __name__ == "__main__":
    unittest.main()
