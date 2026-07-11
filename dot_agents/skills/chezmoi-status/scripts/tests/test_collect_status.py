from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = next(
    path
    for path in (
        SCRIPT_DIR / "executable_collect_status.py",
        SCRIPT_DIR / "collect_status.py",
    )
    if path.is_file()
)
SPEC = importlib.util.spec_from_file_location("chezmoi_status_collector", MODULE_PATH)
assert SPEC and SPEC.loader
collector = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = collector
SPEC.loader.exec_module(collector)


def probe(
    state: str = "ok",
    *,
    stdout: str = "",
    error: str = "",
    exit_code: int | None = 0,
) -> dict:
    return {
        "state": state,
        "exit_code": exit_code,
        "duration_ms": 1,
        "stdout": stdout,
        "error": error,
    }


def managed(*, coverage: str = "full", entries: list[dict] | None = None) -> dict:
    entries = entries or []
    return {
        "coverage": coverage,
        "templates": "verified" if coverage == "full" else "unknown",
        "entry_count": len(entries),
        "counts_by_code": {},
        "target_changed": [],
        "apply_ready": [],
        "two_sided": [],
        "entries": entries,
        "truncated": False,
        "full_probe": collector.public_probe(probe()),
        "fallback_probe": None,
    }


def git_state(**overrides) -> dict:
    result = {
        "available": True,
        "dirty_count": 0,
        "dirty_paths": [],
        "ahead": 0,
        "behind": 0,
        "conflicts": [],
    }
    result.update(overrides)
    return result


def agent_state(**overrides) -> dict:
    result = {
        "coverage": "full",
        "unmanaged": [],
        "broken_claude_adapters": [],
    }
    result.update(overrides)
    return result


def document_state(state: str = "ok") -> dict[str, dict]:
    return {
        "wip": {
            "path": "/tmp/WIP.md",
            "state": state,
            "size_bytes": 1 if state == "ok" else None,
            "error": "" if state == "ok" else "unavailable",
        },
        "migration": {
            "path": "/tmp/MIGRATION.md",
            "state": state,
            "size_bytes": 1 if state == "ok" else None,
            "error": "" if state == "ok" else "unavailable",
        },
    }


class ManagedStateTests(unittest.TestCase):
    def test_full_status_verifies_templates_and_classifies_entries(self):
        with patch.object(
            collector,
            "run_command",
            return_value=probe(stdout=" M apply-me\nMM conflict\n"),
        ) as mocked:
            result = collector.collect_managed(60, 10)

        self.assertEqual(result["coverage"], "full")
        self.assertEqual(result["templates"], "verified")
        self.assertEqual(result["entry_count"], 2)
        self.assertEqual(result["apply_ready"], [{"code": " M", "path": "apply-me"}])
        self.assertEqual(result["two_sided"], [{"code": "MM", "path": "conflict"}])
        self.assertEqual(mocked.call_count, 1)

    def test_timeout_falls_back_to_non_template_coverage(self):
        with patch.object(
            collector,
            "run_command",
            side_effect=[
                probe("timeout", error="timed out", exit_code=None),
                probe(stdout=" M plain-file\n"),
            ],
        ):
            result = collector.collect_managed(60, 10)

        self.assertEqual(result["coverage"], "non_templates")
        self.assertEqual(result["templates"], "unknown")
        self.assertEqual(result["full_probe"]["state"], "timeout")
        self.assertEqual(result["fallback_probe"]["state"], "ok")


class DocumentProbeTests(unittest.TestCase):
    def test_arbitrary_markdown_is_only_probed_not_interpreted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            research = root / ".research"
            research.mkdir()
            wip = research / "WIP.md"
            migration = research / "MIGRATION.md"
            wip.write_text("No backticks, tables, or familiar headings.\n", encoding="utf-8")
            migration.write_text("# A completely different tracker format\n", encoding="utf-8")

            documents = collector.collect_documents(root)

        self.assertEqual(documents["wip"]["state"], "ok")
        self.assertEqual(documents["migration"]["state"], "ok")
        self.assertEqual(documents["wip"]["size_bytes"], 44)
        self.assertNotIn("listed_dirty", documents["wip"])
        self.assertNotIn("active_phase", documents["migration"])

    def test_missing_document_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            result = collector.probe_document(Path(directory) / "missing.md")

        self.assertEqual(result["state"], "unavailable")
        self.assertIsNone(result["size_bytes"])
        self.assertEqual(result["error"], "file not found")

    def test_open_failure_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blocked.md"
            path.write_text("content", encoding="utf-8")
            with patch.object(Path, "open", side_effect=PermissionError("denied")):
                result = collector.probe_document(path)

        self.assertEqual(result["state"], "error")
        self.assertIn("denied", result["error"])


class OverallStateTests(unittest.TestCase):
    def test_clean_attention_partial_and_failed_states(self):
        clean = collector.derive_overall(
            managed(), git_state(), agent_state(), document_state()
        )
        attention = collector.derive_overall(
            managed(), git_state(dirty_count=1), agent_state(), document_state()
        )
        partial = collector.derive_overall(
            managed(), git_state(), agent_state(), document_state("unavailable")
        )
        partial_error = collector.derive_overall(
            managed(), git_state(), agent_state(), document_state("error")
        )
        failed = collector.derive_overall(
            managed(), git_state(available=False), agent_state(), document_state()
        )

        self.assertEqual(clean, "clean")
        self.assertEqual(attention, "attention")
        self.assertEqual(partial, "partial")
        self.assertEqual(partial_error, "partial")
        self.assertEqual(failed, "failed")


class PayloadTests(unittest.TestCase):
    def test_schema_v2_contains_document_probes_not_semantic_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            research = root / ".research"
            research.mkdir()
            (research / "WIP.md").write_text("anything", encoding="utf-8")
            (research / "MIGRATION.md").write_text("anything else", encoding="utf-8")
            source = probe(stdout=str(root) + "\n")
            args = argparse.Namespace(timeout=60.0, fallback_timeout=10.0)

            with (
                patch.object(collector, "run_command", return_value=source),
                patch.object(collector, "collect_managed", return_value=managed()),
                patch.object(collector, "collect_git", return_value=git_state()),
                patch.object(collector, "collect_agents", return_value=agent_state()),
            ):
                payload = collector.collect(args)

        self.assertEqual(payload["schema_version"], 2)
        self.assertIn("documents", payload)
        self.assertNotIn("wip", payload)
        self.assertNotIn("migration", payload)
        self.assertEqual(payload["overall"], "clean")

    def test_main_emits_matching_sha256_sentinel(self):
        payload = {
            "schema_version": 2,
            "collector": "complete",
            "overall": "clean",
        }
        output = io.StringIO()
        with (
            patch.object(
                collector,
                "parse_args",
                return_value=argparse.Namespace(pretty=False),
            ),
            patch.object(collector, "collect", return_value=payload),
            contextlib.redirect_stdout(output),
        ):
            exit_code = collector.main()

        json_line, sentinel = output.getvalue().splitlines()
        expected = hashlib.sha256(json_line.encode("utf-8")).hexdigest()
        self.assertEqual(json.loads(json_line), payload)
        self.assertEqual(sentinel, f"{collector.SENTINEL} sha256={expected}")
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
