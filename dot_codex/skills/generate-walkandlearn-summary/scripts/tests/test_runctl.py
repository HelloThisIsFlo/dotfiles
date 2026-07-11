from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


RUNCTL_PATH = Path(__file__).resolve().parents[1] / "runctl.py"
SPEC = importlib.util.spec_from_file_location("walkandlearn_runctl", RUNCTL_PATH)
assert SPEC and SPEC.loader
runctl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runctl)


EMOTIONAL_CHECKS = {
    "quote_fidelity",
    "attribution",
    "conversation_support",
    "taxonomy_calibration",
    "completeness",
    "structure_compliance",
}
TECHNICAL_CHECKS = {
    "quote_fidelity",
    "attribution",
    "conversation_support",
    "technical_correctness",
    "formula_validity",
    "terminology",
    "correction_transparency",
    "completeness",
    "structure_compliance",
}
FAILURE_CHECKS = {
    "fabricated_quote": "quote_fidelity",
    "reversed_attribution": "attribution",
    "unsupported_claim": "conversation_support",
    "false_independence_claim": "taxonomy_calibration",
    "truncation": "completeness",
    "placeholder_violation": "structure_compliance",
    "technical_inaccuracy": "technical_correctness",
    "unresolved_claim_not_qualified": "technical_correctness",
    "terminology_error": "terminology",
    "invalid_formula": "formula_validity",
    "missing_correction_label": "correction_transparency",
}
EXPECTED_INVENTORY = {
    "emotional_0.md",
    "emotional_1.md",
    "emotional_2.md",
    "technical_0.md",
    "technical_1.md",
    "technical_2.md",
    "evaluation.md",
    "run.json",
}


class RunControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.repo = self.root / "repo"
        self.input_dir = self.repo / "agent_files" / "walkandlearn_summary"
        self.input_dir.mkdir(parents=True)
        self.output_base = self.root / "vault" / "DebugSandbox"
        self.staging = self.root / "staging"
        self.source = self.root / "conversation.md"
        self.source.write_text(
            "## Prompt\nWhy does this work?\n\n"
            "## Response\nBecause the two ideas connect. SHA-256 has a 256-bit digest.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def args(self, **values):
        defaults = {
            "repo": self.repo,
            "output_base": self.output_base,
            "staging_root": str(self.staging),
        }
        defaults.update(values)
        return argparse.Namespace(**defaults)

    def init(self, topic: str = "unit-test") -> dict:
        return runctl.init_run(
            self.args(
                clipboard=False,
                file=str(self.source.resolve()),
                date="2026-07-10",
                topic=topic,
                reuse_canonical=False,
                max_bytes=runctl.DEFAULT_MAX_BYTES,
            )
        )

    def manifest(self, run_id: str) -> dict:
        return runctl.load_manifest(self.args(), run_id)[1]

    @staticmethod
    def emotional_body(index: int) -> str:
        return (
            f"## 💡 Moment {index}\n\n"
            "*📚 Guided Learning*\n\n"
            "> [!SUMMARY] **Summary**\n> A grounded moment.\n\n"
            "> [!SUCCESS] **Why it mattered!**\n> It clarified the idea.\n\n"
            "**I explained…**\n\nThe two ideas connect.\n\n"
            "**What you realized…**\n\nYou understood the connection.\n"
        )

    @staticmethod
    def technical_body(index: int) -> str:
        return (
            f"**Document Title:** Test Summary {index}\n\n"
            "# 📌 TL;DR / 30-Second Refresher\n\n"
            f"- Candidate {index} explains the connection.\n"
            "- SHA-256 produces a 256-bit digest.\n\n"
            "# 🧰 Quick-Reference Cheat Sheets\n\n"
            "1. Identify the two ideas.\n2. Connect them.\n\n"
            "# ⭐ Aha Moments & Discovery Journey\n"
            "[AHA_PLACEHOLDER]\n\n"
            "# 🧠 Mental Models Built\n\nThe ideas form a bridge.\n\n"
            "# 🧭 Suggested Next Adventures\n\nRevisit the connection.\n\n"
            "# 🌅 Closing Thoughts\n\nThe connection is now clearer.\n"
        )

    @staticmethod
    def source_record() -> dict:
        return {
            "title": "Secure Hash Standard (SHS)",
            "publisher": "NIST",
            "url": "https://doi.org/10.6028/NIST.FIPS.180-4",
            "support": "The standard specifies SHA-256 and its 256-bit message digest.",
            "source_type": "official",
        }

    @classmethod
    def post_session_correction(cls, statement: str) -> str:
        source = cls.source_record()
        return (
            f"{statement}\n\n"
            "> [!warning] Post-session correction\n"
            f"> Corrected after the session using [{source['title']}]({source['url']})."
        )

    def complete_family_candidates(self, run_id: str, family: str) -> None:
        for index in range(runctl.CANDIDATE_COUNT):
            current = self.manifest(run_id)["candidates"][family][index]
            if current["status"] == "valid":
                continue
            started = runctl.start_candidate(
                self.args(run_id=run_id, family=family, index=index)
            )
            body = (
                self.emotional_body(index)
                if family == "emotional"
                else self.technical_body(index)
            )
            Path(started["output_path"]).write_text(body, encoding="utf-8")
            result = runctl.validate_candidate(
                self.args(run_id=run_id, family=family, index=index)
            )
            self.assertEqual(result["status"], "valid")

    def complete_candidates(self, run_id: str) -> None:
        for family in runctl.FAMILIES:
            self.complete_family_candidates(run_id, family)

    def research_payload(self, prepared: dict, *, unresolved: bool = False) -> dict:
        bundle = Path(prepared["bundle_path"]).read_text(encoding="utf-8")
        candidate_ids = [
            line.removeprefix("## ")
            for line in bundle.splitlines()
            if line.startswith("## candidate-")
        ]
        assessment = "unresolved" if unresolved else "confirmed"
        findings = [
            {
                "finding_id": "finding-001",
                "candidate_ids": candidate_ids,
                "excerpts": [
                    {
                        "candidate_id": candidate_id,
                        "text": "SHA-256 produces a 256-bit digest.",
                    }
                    for candidate_id in candidate_ids
                ],
                "kind": "fact",
                "assessment": assessment,
                "severity": "material" if unresolved else "minor",
                "correction": (
                    "Treat this claim as unverified."
                    if unresolved
                    else "No correction required."
                ),
                "confidence": "low" if unresolved else "high",
                "sources": [] if unresolved else [self.source_record()],
            }
        ]
        bundle_sha256 = prepared.get("bundle_sha256")
        if bundle_sha256 is None:
            bundle_sha256 = runctl.sha256_file(Path(prepared["bundle_path"]))
        return {
            "schema_version": runctl.SCHEMA_VERSION,
            "bundle_sha256": bundle_sha256,
            "findings": findings,
            "coverage": {
                "candidate_ids": candidate_ids,
                "material_claims_reviewed": len(findings),
                "material_claims_unresolved": 1 if unresolved else 0,
            },
            "confidence": {
                "level": "medium" if unresolved else "high",
                "reason": "Every material candidate claim was checked.",
            },
        }

    def candidate_specific_research_payload(self, prepared: dict) -> dict:
        mapping = self.manifest(prepared["run_id"])["technical_review"]["packet"][
            "mapping"
        ]
        aliases_by_index = {index: alias for alias, index in mapping.items()}
        assessments = ("needs_correction", "needs_qualification", "confirmed")
        findings = []
        for index, assessment in enumerate(assessments):
            alias = aliases_by_index[index]
            findings.append(
                {
                    "finding_id": f"finding-{index + 1:03d}",
                    "candidate_ids": [alias],
                    "excerpts": [
                        {
                            "candidate_id": alias,
                            "text": f"Candidate {index} explains the connection.",
                        }
                    ],
                    "kind": "fact",
                    "assessment": assessment,
                    "severity": "material" if index < 2 else "minor",
                    "correction": (
                        "No correction required."
                        if assessment == "confirmed"
                        else f"Qualify candidate {index}'s claim using the source."
                    ),
                    "confidence": "high",
                    "sources": [self.source_record()],
                }
            )
        return {
            "schema_version": runctl.SCHEMA_VERSION,
            "bundle_sha256": prepared["bundle_sha256"],
            "findings": findings,
            "coverage": {
                "candidate_ids": list(mapping),
                "material_claims_reviewed": len(findings),
                "material_claims_unresolved": 0,
            },
            "confidence": {
                "level": "high",
                "reason": "Each candidate-specific claim was checked.",
            },
        }

    def complete_candidate_specific_research(self, run_id: str) -> dict:
        prepared = runctl.prepare_technical_review(self.args(run_id=run_id))
        payload = self.candidate_specific_research_payload(prepared)
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_technical_review(self.args(run_id=run_id))
        self.assertEqual(result["status"], "valid", result)
        return payload

    def complete_research(self, run_id: str, *, unresolved: bool = False) -> None:
        manifest = self.manifest(run_id)
        if manifest.get("technical_review", {}).get("status") == "valid":
            return
        prepared = runctl.prepare_technical_review(self.args(run_id=run_id))
        Path(prepared["output_path"]).write_text(
            json.dumps(self.research_payload(prepared, unresolved=unresolved)),
            encoding="utf-8",
        )
        result = runctl.record_technical_review(self.args(run_id=run_id))
        self.assertEqual(result["status"], "valid")

    def judge_payload(self, manifest: dict, family: str) -> dict:
        packet = manifest["evaluations"][family]["packet"]
        aliases = packet["order"]
        criteria = runctl.SCORE_CONTRACTS[family]
        cards = []
        for alias in aliases:
            index = packet["mapping"][alias]
            score = 5 - index
            scores = {name: score for name in criteria}
            evidence = [f"Transcript-grounded evidence for {alias}."]
            if family == "technical":
                applicable = [
                    finding
                    for finding in manifest["technical_review"]["result"]["findings"]
                    if alias in finding["candidate_ids"]
                    and finding["assessment"] != "confirmed"
                ]
                evidence.extend(
                    f"{finding['finding_id']} is reflected in the correctness score."
                    for finding in applicable
                )
                cap = 5
                for finding in applicable:
                    if finding["severity"] == "critical":
                        cap = min(cap, 1)
                    elif finding["severity"] == "material" and finding[
                        "assessment"
                    ] in {"needs_correction", "unresolved"}:
                        cap = min(cap, 2)
                    elif finding["severity"] == "material":
                        cap = min(cap, 3)
                    else:
                        cap = min(cap, 4)
                scores["technical_correctness_terminology"] = min(
                    scores["technical_correctness_terminology"], cap
                )
            cards.append(
                {
                    "candidate_id": alias,
                    "scores": scores,
                    "evidence": evidence,
                    "strengths": [f"Strength for {alias}."],
                    "omissions": [],
                    "fidelity_concerns": [],
                }
            )
        cards_by_alias = {card["candidate_id"]: card for card in cards}
        order_index = {alias: position for position, alias in enumerate(aliases)}
        ranked = sorted(
            aliases,
            key=lambda alias: (
                -sum(
                    cards_by_alias[alias]["scores"][name] * weight
                    for name, weight in criteria.items()
                ),
                order_index[alias],
            ),
        )
        return {
            "schema_version": runctl.SCHEMA_VERSION,
            "summary_type": family,
            "ranking": ranked,
            "recommendation": ranked[0],
            "ranking_reason": "Candidate indices have descending fixed scores.",
            "candidates": cards,
            "confidence": {"level": "high", "reason": "The evidence is clear."},
        }

    def complete_evaluations(self, run_id: str) -> None:
        self.complete_research(run_id)
        for family in runctl.FAMILIES:
            if self.manifest(run_id)["evaluations"][family]["status"] == "valid":
                continue
            prepared = runctl.prepare_judge(self.args(run_id=run_id, family=family))
            payload = self.judge_payload(self.manifest(run_id), family)
            Path(prepared["output_path"]).write_text(
                json.dumps(payload), encoding="utf-8"
            )
            result = runctl.record_evaluation(self.args(run_id=run_id, family=family))
            self.assertEqual(result["status"], "valid")

    def audit_payload(
        self,
        prepared: dict,
        *,
        verdict: str = "pass",
        issue_id: str = "issue-001",
        failure_code: str | None = None,
        excerpt: str | None = None,
    ) -> dict:
        family = prepared["family"]
        check_names = EMOTIONAL_CHECKS if family == "emotional" else TECHNICAL_CHECKS
        checks = {
            name: {
                "status": "pass",
                "evidence": ["The candidate satisfies this check."],
            }
            for name in check_names
        }
        if family == "technical" and prepared.get("evidence_path"):
            evidence_packet = json.loads(
                Path(prepared["evidence_path"]).read_text(encoding="utf-8")
            )
            finding_ids = [
                finding["finding_id"]
                for finding in evidence_packet["findings"]
                if finding["assessment"] != "confirmed"
            ]
            if finding_ids:
                checks["technical_correctness"]["evidence"].append(
                    "Reviewed applicable findings: " + ", ".join(finding_ids)
                )
        failures = []
        if verdict == "fail":
            failure_code = failure_code or (
                "unsupported_claim" if family == "emotional" else "technical_inaccuracy"
            )
            check = FAILURE_CHECKS[failure_code]
            checks[check] = {"status": "fail", "evidence": ["A repair is required."]}
            candidate_excerpt = excerpt or (
                "The two ideas connect."
                if family == "emotional"
                else "Candidate 0 explains the connection."
            )
            linked_finding_ids: list[str] = []
            if family == "technical" and prepared.get("evidence_path"):
                evidence_packet = json.loads(
                    Path(prepared["evidence_path"]).read_text(encoding="utf-8")
                )
                linked_finding_ids = [
                    finding["finding_id"]
                    for finding in evidence_packet["findings"]
                    if finding["assessment"] != "confirmed"
                    and any(
                        item["text"] in candidate_excerpt
                        or candidate_excerpt in item["text"]
                        for item in finding["excerpts"]
                    )
                ]
            failures = [
                {
                    "issue_id": issue_id,
                    "code": failure_code,
                    "candidate_excerpt": candidate_excerpt,
                    "evidence": "The cited passage fails the named hard gate.",
                    "required_change": "Replace only the cited passage with a supported statement.",
                    "finding_ids": linked_finding_ids,
                    "sources": [] if family == "emotional" else [self.source_record()],
                }
            ]
        return {
            "schema_version": runctl.SCHEMA_VERSION,
            "summary_type": family,
            "candidate_id": prepared["candidate_id"],
            "revision": prepared["revision"],
            "candidate_sha256": prepared["candidate_sha256"],
            "verdict": verdict,
            "hard_failures": failures,
            "checks": checks,
            "sources": [] if family == "emotional" else [self.source_record()],
            "reason": "The candidate passed."
            if verdict == "pass"
            else "The candidate needs repair.",
        }

    def record_audit(
        self,
        run_id: str,
        family: str,
        *,
        verdict: str = "pass",
        issue_id: str = "issue-001",
        failure_code: str | None = None,
        excerpt: str | None = None,
    ) -> tuple[dict, dict]:
        prepared = runctl.prepare_audit(self.args(run_id=run_id, family=family))
        payload = self.audit_payload(
            prepared,
            verdict=verdict,
            issue_id=issue_id,
            failure_code=failure_code,
            excerpt=excerpt,
        )
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_audit(self.args(run_id=run_id, family=family))
        return prepared, result

    def repair_payload(
        self,
        prepared: dict,
        *,
        issue_id: str,
        old_text: str,
        new_text: str,
        finding_ids: list[str] | None = None,
        enforce_inline_contract: bool = True,
    ) -> dict:
        finding_ids = finding_ids or []
        if (
            enforce_inline_contract
            and prepared["family"] == "technical"
            and "Post-session correction" not in new_text
            and "Verification note" not in new_text
        ):
            new_text = self.post_session_correction(new_text)
        return {
            "schema_version": runctl.SCHEMA_VERSION,
            "summary_type": prepared["family"],
            "candidate_id": prepared["candidate_id"],
            "base_revision": prepared["base_revision"],
            "base_sha256": prepared["base_sha256"],
            "replacements": [
                {
                    "resolves": [issue_id],
                    "old_text": old_text,
                    "new_text": new_text,
                    "reason": "This is the smallest complete correction.",
                    "finding_ids": finding_ids,
                }
            ],
        }

    def record_repair(
        self,
        run_id: str,
        family: str,
        *,
        issue_id: str,
        old_text: str,
        new_text: str,
    ) -> tuple[dict, dict]:
        prepared = runctl.prepare_repair(self.args(run_id=run_id, family=family))
        audit_result = json.loads(
            Path(prepared["audit_path"]).read_text(encoding="utf-8")
        )
        finding_ids = sorted(
            {
                finding_id
                for failure in audit_result["hard_failures"]
                for finding_id in failure["finding_ids"]
            }
        )
        payload = self.repair_payload(
            prepared,
            issue_id=issue_id,
            old_text=old_text,
            new_text=new_text,
            finding_ids=finding_ids,
        )
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_repair(self.args(run_id=run_id, family=family))
        return prepared, result

    def make_evaluated_run(self) -> str:
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        self.complete_evaluations(run_id)
        return run_id

    def make_ready_run(self) -> str:
        run_id = self.make_evaluated_run()
        self.record_audit(run_id, "emotional")
        _, result = self.record_audit(run_id, "technical")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(self.manifest(run_id)["status"], "ready")
        return run_id

    def make_awaiting_user_run(self) -> str:
        run_id = self.make_evaluated_run()
        self.record_audit(run_id, "emotional")
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text="Candidate 0 accurately explains the connection.",
        )
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 accurately explains the connection.",
        )
        self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text="Candidate 0 accurately explains the connection.",
            new_text="Candidate 0 accurately explains the supported connection.",
        )
        _, result = self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 accurately explains the supported connection.",
        )
        self.assertEqual(result["status"], "awaiting_user")
        return run_id

    def exhaust_current_technical_candidate(self, run_id: str, index: int) -> dict:
        original = f"Candidate {index} explains the connection."
        first = f"Candidate {index} accurately explains the connection."
        second = f"Candidate {index} accurately explains the supported connection."
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt=original,
        )
        self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text=original,
            new_text=first,
        )
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt=first,
        )
        self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text=first,
            new_text=second,
        )
        _, result = self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt=second,
        )
        self.assertEqual(result["status"], "awaiting_user")
        return result

    def assert_next_contains(self, result: dict, token: str) -> None:
        normalized = json.dumps(result["next"]).replace("_", "-")
        self.assertIn(token, normalized)

    def test_v2_contracts_are_explicit(self):
        initialized = self.init()
        manifest = self.manifest(initialized["run_id"])
        self.assertEqual(runctl.SCHEMA_VERSION, "codex-native-v2")
        self.assertEqual(manifest["schema_version"], "codex-native-v2")
        self.assertEqual(
            runctl.SCORE_CONTRACTS["technical"],
            {
                "technical_correctness_terminology": 0.35,
                "conversation_fidelity": 0.25,
                "proportional_coverage": 0.15,
                "reference_usefulness": 0.15,
                "mental_models_relationships": 0.05,
                "formatting_composition_compliance": 0.05,
            },
        )
        self.assertEqual(set(runctl.AUDIT_CHECKS["emotional"]), EMOTIONAL_CHECKS)
        self.assertEqual(set(runctl.AUDIT_CHECKS["technical"]), TECHNICAL_CHECKS)

    def test_technical_research_is_required_before_technical_judging(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        emotional = runctl.prepare_judge(self.args(run_id=run_id, family="emotional"))
        self.assertIsNone(emotional.get("evidence_path"))
        with self.assertRaisesRegex(runctl.RunError, "technical review|research"):
            runctl.prepare_judge(self.args(run_id=run_id, family="technical"))

        prepared = runctl.prepare_technical_review(self.args(run_id=run_id))
        self.assertEqual(Path(prepared["prompt_path"]).name, "technical-researcher.md")
        Path(prepared["output_path"]).write_text(
            json.dumps(self.research_payload(prepared)), encoding="utf-8"
        )
        self.assertEqual(
            runctl.record_technical_review(self.args(run_id=run_id))["status"],
            "valid",
        )
        technical = runctl.prepare_judge(self.args(run_id=run_id, family="technical"))
        self.assertTrue(Path(technical["evidence_path"]).is_file())

    def test_research_and_judging_preserve_family_independence(self):
        technical_run = self.init()["run_id"]
        self.complete_family_candidates(technical_run, "technical")
        prepared = runctl.prepare_technical_review(self.args(run_id=technical_run))
        Path(prepared["output_path"]).write_text(
            json.dumps(self.research_payload(prepared)), encoding="utf-8"
        )
        result = runctl.record_technical_review(self.args(run_id=technical_run))
        self.assertEqual(result["status"], "valid")
        self.assertTrue(
            all(
                candidate["status"] == "pending"
                for candidate in self.manifest(technical_run)["candidates"]["emotional"]
            )
        )

        emotional_run = self.init()["run_id"]
        self.complete_family_candidates(emotional_run, "emotional")
        emotional = runctl.prepare_judge(
            self.args(run_id=emotional_run, family="emotional")
        )
        self.assertIsNone(emotional["evidence_path"])
        with self.assertRaises(runctl.RunError):
            runctl.prepare_judge(self.args(run_id=emotional_run, family="technical"))

    def test_research_requires_complete_candidate_coverage_and_primary_sources(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        prepared = runctl.prepare_technical_review(self.args(run_id=run_id))
        payload = self.research_payload(prepared)
        payload["coverage"]["candidate_ids"].pop()
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_technical_review(self.args(run_id=run_id))
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(result["retry_available"])

        retry = runctl.prepare_technical_review(self.args(run_id=run_id))
        payload = self.research_payload(retry)
        payload["findings"][0]["sources"] = []
        Path(retry["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_technical_review(self.args(run_id=run_id))
        self.assertEqual(result["status"], "invalid")
        self.assertFalse(result["retry_available"])

    def test_unresolved_research_is_explicit_and_not_recast_as_nonexistence(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        prepared = runctl.prepare_technical_review(self.args(run_id=run_id))
        payload = self.research_payload(prepared, unresolved=True)
        finding = payload["findings"][0]
        self.assertEqual(finding["assessment"], "unresolved")
        self.assertNotIn("does not exist", finding["correction"].lower())
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_technical_review(self.args(run_id=run_id))
        self.assertEqual(result["status"], "valid")

    def test_research_enforces_correction_semantics_and_sequential_finding_ids(self):
        cases = {
            "confirmed_correction": (
                lambda payload: payload["findings"][0].update(
                    {"correction": "Actually rewrite this claim."}
                ),
                "No correction required",
            ),
            "categorical_unresolved": (
                lambda payload: payload["findings"][0].update(
                    {
                        "assessment": "unresolved",
                        "severity": "material",
                        "confidence": "low",
                        "sources": [],
                        "correction": "This term does not exist.",
                    }
                ),
                "uncertain|unresolved|does not exist",
            ),
            "categorical_no_such_term": (
                lambda payload: payload["findings"][0].update(
                    {
                        "assessment": "unresolved",
                        "severity": "material",
                        "confidence": "low",
                        "sources": [],
                        "correction": (
                            "This remains unresolved, but no such technique exists."
                        ),
                    }
                ),
                "uncertain|unresolved|nonexistence",
            ),
            "nonsequential_id": (
                lambda payload: payload["findings"][0].update(
                    {"finding_id": "finding-002"}
                ),
                "finding_id|sequential",
            ),
        }
        for case, (mutate, expected_reason) in cases.items():
            with self.subTest(case=case):
                run_id = self.init()["run_id"]
                self.complete_family_candidates(run_id, "technical")
                prepared = runctl.prepare_technical_review(self.args(run_id=run_id))
                payload = self.research_payload(prepared)
                mutate(payload)
                Path(prepared["output_path"]).write_text(
                    json.dumps(payload), encoding="utf-8"
                )
                result = runctl.record_technical_review(self.args(run_id=run_id))
                self.assertEqual(result["status"], "invalid")
                self.assertRegex(result["reason"], expected_reason)

    def test_research_rejects_empty_or_candidate_incomplete_ledgers(self):
        for case in ("empty", "missing_candidate"):
            with self.subTest(case=case):
                run_id = self.init()["run_id"]
                self.complete_family_candidates(run_id, "technical")
                prepared = runctl.prepare_technical_review(self.args(run_id=run_id))
                payload = self.research_payload(prepared)
                if case == "empty":
                    payload["findings"] = []
                    payload["coverage"]["material_claims_reviewed"] = 0
                else:
                    omitted = payload["findings"][0]["candidate_ids"].pop()
                    payload["findings"][0]["excerpts"] = [
                        excerpt
                        for excerpt in payload["findings"][0]["excerpts"]
                        if excerpt["candidate_id"] != omitted
                    ]
                Path(prepared["output_path"]).write_text(
                    json.dumps(payload), encoding="utf-8"
                )
                result = runctl.record_technical_review(self.args(run_id=run_id))
                self.assertEqual(result["status"], "invalid")
                self.assertIn("cover every candidate", result["reason"])

    def test_technical_judge_cannot_ignore_or_cross_apply_findings(self):
        cases = {
            "ignored": ["Transcript evidence only."],
            "cross_applied": ["finding-002 was considered."],
        }
        for case, evidence in cases.items():
            with self.subTest(case=case):
                run_id = self.init()["run_id"]
                self.complete_candidates(run_id)
                self.complete_candidate_specific_research(run_id)
                prepared = runctl.prepare_judge(
                    self.args(run_id=run_id, family="technical")
                )
                manifest = self.manifest(run_id)
                payload = self.judge_payload(manifest, "technical")
                alias = next(
                    alias
                    for alias, index in manifest["evaluations"]["technical"]["packet"][
                        "mapping"
                    ].items()
                    if index == 0
                )
                card = next(
                    card
                    for card in payload["candidates"]
                    if card["candidate_id"] == alias
                )
                card["evidence"] = evidence
                Path(prepared["output_path"]).write_text(
                    json.dumps(payload), encoding="utf-8"
                )
                result = runctl.record_evaluation(
                    self.args(run_id=run_id, family="technical")
                )
                self.assertEqual(result["status"], "invalid")
                self.assertIn("finding-001", result["reason"])

    def test_unresolved_claim_can_be_repaired_with_an_explicit_verification_note(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        self.complete_research(run_id, unresolved=True)
        self.complete_evaluations(run_id)
        audit = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        audit_payload = self.audit_payload(
            audit,
            verdict="fail",
            issue_id="issue-001",
            failure_code="unresolved_claim_not_qualified",
            excerpt="SHA-256 produces a 256-bit digest.",
        )
        audit_payload["hard_failures"][0]["sources"] = []
        Path(audit["output_path"]).write_text(
            json.dumps(audit_payload), encoding="utf-8"
        )
        result = runctl.record_audit(self.args(run_id=run_id, family="technical"))
        self.assertEqual(result["status"], "repair_pending")
        note = (
            "> [!question] Verification note\n"
            "> This claim remains uncertain pending a primary source."
        )
        _, repaired = self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text="- SHA-256 produces a 256-bit digest.",
            new_text="- The SHA-256 digest-size claim remains uncertain.\n\n" + note,
        )
        self.assertEqual(repaired["status"], "repaired")
        current = self.manifest(run_id)["candidates"]["technical"][0]["revisions"][1]
        revised = Path(current["output_path"]).read_text(encoding="utf-8")
        self.assertIn("Verification note", revised)
        self.assertIn("remains uncertain", revised)
        self.assertNotIn("http://", revised)
        self.assertNotIn("https://", revised)
        retry_audit = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        omitted = self.audit_payload(retry_audit)
        omitted["checks"]["technical_correctness"]["evidence"] = [
            "Generic correctness statement without a finding ID."
        ]
        Path(retry_audit["output_path"]).write_text(
            json.dumps(omitted), encoding="utf-8"
        )
        invalid = runctl.record_audit(self.args(run_id=run_id, family="technical"))
        self.assertEqual(invalid["status"], "invalid")
        self.assertIn("did not document review", invalid["reason"])

        _, result = self.record_audit(run_id, "technical")
        self.assertEqual(result["status"], "pending")

    def test_zero_source_unresolved_repair_rejects_missing_note_and_fabricated_link(
        self,
    ):
        cases = {
            "missing_note": (
                "This claim remains uncertain pending verification.",
                "Verification note",
            ),
            "fabricated_link": (
                "> [!question] Verification note\n"
                "> This remains uncertain; see "
                "[an invented source](https://example.org/invented).",
                "unvalidated source URL",
            ),
        }
        for case, (new_text, expected_reason) in cases.items():
            with self.subTest(case=case):
                run_id = self.init()["run_id"]
                self.complete_candidates(run_id)
                self.complete_research(run_id, unresolved=True)
                self.complete_evaluations(run_id)
                audit = runctl.prepare_audit(
                    self.args(run_id=run_id, family="technical")
                )
                audit_payload = self.audit_payload(
                    audit,
                    verdict="fail",
                    issue_id="issue-001",
                    failure_code="unresolved_claim_not_qualified",
                    excerpt="SHA-256 produces a 256-bit digest.",
                )
                audit_payload["hard_failures"][0]["sources"] = []
                Path(audit["output_path"]).write_text(
                    json.dumps(audit_payload), encoding="utf-8"
                )
                result = runctl.record_audit(
                    self.args(run_id=run_id, family="technical")
                )
                self.assertEqual(result["status"], "repair_pending")
                prepared = runctl.prepare_repair(
                    self.args(run_id=run_id, family="technical")
                )
                payload = self.repair_payload(
                    prepared,
                    issue_id="issue-001",
                    old_text="SHA-256 produces a 256-bit digest.",
                    new_text=new_text,
                    finding_ids=["finding-001"],
                    enforce_inline_contract=False,
                )
                Path(prepared["output_path"]).write_text(
                    json.dumps(payload), encoding="utf-8"
                )
                result = runctl.record_repair(
                    self.args(run_id=run_id, family="technical")
                )
                self.assertEqual(result["status"], "invalid")
                self.assertTrue(result["retry_available"])
                self.assertIn(expected_reason, result["reason"])

    def test_later_repairs_cannot_remove_a_claim_scoped_finding_proof(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        self.complete_research(run_id, unresolved=True)
        self.complete_evaluations(run_id)

        audit = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        payload = self.audit_payload(
            audit,
            verdict="fail",
            issue_id="issue-001",
            failure_code="unresolved_claim_not_qualified",
            excerpt="SHA-256 produces a 256-bit digest.",
        )
        payload["hard_failures"][0]["sources"] = []
        Path(audit["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(
            runctl.record_audit(self.args(run_id=run_id, family="technical"))["status"],
            "repair_pending",
        )

        repaired_passage = (
            "- The SHA-256 digest-size claim remains uncertain.\n\n"
            "> [!question] Verification note\n"
            "> This claim remains uncertain pending a primary source."
        )
        repair = runctl.prepare_repair(self.args(run_id=run_id, family="technical"))
        repair_payload = self.repair_payload(
            repair,
            issue_id="issue-001",
            old_text="- SHA-256 produces a 256-bit digest.",
            new_text=repaired_passage,
            finding_ids=["finding-001"],
            enforce_inline_contract=False,
        )
        Path(repair["output_path"]).write_text(
            json.dumps(repair_payload), encoding="utf-8"
        )
        self.assertEqual(
            runctl.record_repair(self.args(run_id=run_id, family="technical"))[
                "status"
            ],
            "repaired",
        )

        audit = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        payload = self.audit_payload(
            audit,
            verdict="fail",
            issue_id="issue-001",
            failure_code="unsupported_claim",
            excerpt=repaired_passage,
        )
        Path(audit["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(
            runctl.record_audit(self.args(run_id=run_id, family="technical"))["status"],
            "repair_pending",
        )

        repair = runctl.prepare_repair(self.args(run_id=run_id, family="technical"))
        replacement = self.repair_payload(
            repair,
            issue_id="issue-001",
            old_text=repaired_passage,
            new_text=self.post_session_correction(
                "The passage is replaced without its original finding lineage."
            ),
            finding_ids=[],
            enforce_inline_contract=False,
        )
        Path(repair["output_path"]).write_text(
            json.dumps(replacement), encoding="utf-8"
        )
        result = runctl.record_repair(self.args(run_id=run_id, family="technical"))
        self.assertEqual(result["status"], "invalid")
        self.assertIn("claim-scoped", result["reason"])

    def test_source_backed_technical_repair_requires_callout_and_validated_url(self):
        source_url = self.source_record()["url"]
        cases = {
            "missing_callout": (
                "Candidate 0 accurately explains the connection with "
                f"[the validated source]({source_url}).",
                "Post-session correction",
            ),
            "unvalidated_url": (
                "Candidate 0 accurately explains the connection.\n\n"
                "> [!warning] Post-session correction\n"
                "> Corrected using [an unvalidated source](https://example.org/not-validated).",
                "validated source URL",
            ),
        }
        for case, (new_text, expected_reason) in cases.items():
            with self.subTest(case=case):
                run_id = self.make_evaluated_run()
                self.record_audit(
                    run_id,
                    "technical",
                    verdict="fail",
                    issue_id="issue-001",
                    excerpt="Candidate 0 explains the connection.",
                )
                prepared = runctl.prepare_repair(
                    self.args(run_id=run_id, family="technical")
                )
                payload = self.repair_payload(
                    prepared,
                    issue_id="issue-001",
                    old_text="Candidate 0 explains the connection.",
                    new_text=new_text,
                    finding_ids=[],
                    enforce_inline_contract=False,
                )
                Path(prepared["output_path"]).write_text(
                    json.dumps(payload), encoding="utf-8"
                )
                result = runctl.record_repair(
                    self.args(run_id=run_id, family="technical")
                )
                self.assertEqual(result["status"], "invalid")
                self.assertTrue(result["retry_available"])
                self.assertIn(expected_reason, result["reason"])

    def test_repair_requires_exact_callout_and_validated_markdown_link(self):
        run_id = self.make_evaluated_run()
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        prepared = runctl.prepare_repair(self.args(run_id=run_id, family="technical"))
        source_url = self.source_record()["url"]
        malformed = self.repair_payload(
            prepared,
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text=(
                "Candidate 0 accurately explains the connection. "
                f"Post-session correction {source_url}"
            ),
            finding_ids=[],
            enforce_inline_contract=False,
        )
        Path(prepared["output_path"]).write_text(
            json.dumps(malformed), encoding="utf-8"
        )
        result = runctl.record_repair(self.args(run_id=run_id, family="technical"))
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(result["retry_available"])
        self.assertRegex(result["reason"], "callout|Markdown link")

        retry = runctl.prepare_repair(self.args(run_id=run_id, family="technical"))
        valid = self.repair_payload(
            retry,
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text=self.post_session_correction(
                "Candidate 0 accurately explains the connection."
            ),
            finding_ids=[],
            enforce_inline_contract=False,
        )
        Path(retry["output_path"]).write_text(json.dumps(valid), encoding="utf-8")
        result = runctl.record_repair(self.args(run_id=run_id, family="technical"))
        self.assertEqual(result["status"], "repaired", result)

    def test_definitive_correction_must_link_primary_or_official_source(self):
        run_id = self.make_evaluated_run()
        prepared_audit = runctl.prepare_audit(
            self.args(run_id=run_id, family="technical")
        )
        audit = self.audit_payload(
            prepared_audit,
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        secondary = {
            "title": "Secondary explanation",
            "publisher": "Example Review",
            "url": "https://example.org/secondary",
            "source_type": "secondary",
            "support": "Summarizes the official standard.",
        }
        audit["hard_failures"][0]["sources"].append(secondary)
        Path(prepared_audit["output_path"]).write_text(
            json.dumps(audit), encoding="utf-8"
        )
        recorded = runctl.record_audit(self.args(run_id=run_id, family="technical"))
        self.assertEqual(recorded["status"], "repair_pending")

        prepared = runctl.prepare_repair(self.args(run_id=run_id, family="technical"))
        new_text = (
            "Candidate 0 accurately explains the connection.\n\n"
            "> [!warning] Post-session correction\n"
            "> Corrected using [secondary evidence]"
            "(https://example.org/secondary)."
        )
        payload = self.repair_payload(
            prepared,
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text=new_text,
            finding_ids=[],
            enforce_inline_contract=False,
        )
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_repair(self.args(run_id=run_id, family="technical"))
        self.assertEqual(result["status"], "invalid")
        self.assertIn("validated URL", result["reason"])

    def test_bool_revisions_sequential_issue_ids_and_empty_replacements_are_rejected(
        self,
    ):
        cases = ("audit_bool", "repair_bool", "issue_sequence", "empty_new_text")
        for case in cases:
            with self.subTest(case=case):
                run_id = self.make_evaluated_run()
                if case in {"audit_bool", "issue_sequence"}:
                    prepared = runctl.prepare_audit(
                        self.args(run_id=run_id, family="technical")
                    )
                    payload = self.audit_payload(
                        prepared,
                        verdict="fail" if case == "issue_sequence" else "pass",
                        issue_id="issue-002",
                        excerpt="Candidate 0 explains the connection.",
                    )
                    if case == "audit_bool":
                        payload["revision"] = False
                    Path(prepared["output_path"]).write_text(
                        json.dumps(payload), encoding="utf-8"
                    )
                    result = runctl.record_audit(
                        self.args(run_id=run_id, family="technical")
                    )
                else:
                    self.record_audit(
                        run_id,
                        "technical",
                        verdict="fail",
                        issue_id="issue-001",
                        excerpt="Candidate 0 explains the connection.",
                    )
                    prepared = runctl.prepare_repair(
                        self.args(run_id=run_id, family="technical")
                    )
                    payload = self.repair_payload(
                        prepared,
                        issue_id="issue-001",
                        old_text="Candidate 0 explains the connection.",
                        new_text=(
                            ""
                            if case == "empty_new_text"
                            else self.post_session_correction(
                                "Candidate 0 accurately explains the connection."
                            )
                        ),
                        finding_ids=[],
                        enforce_inline_contract=False,
                    )
                    if case == "repair_bool":
                        payload["base_revision"] = False
                    Path(prepared["output_path"]).write_text(
                        json.dumps(payload), encoding="utf-8"
                    )
                    result = runctl.record_repair(
                        self.args(run_id=run_id, family="technical")
                    )
                self.assertEqual(result["status"], "invalid")
                if case == "issue_sequence":
                    self.assertRegex(result["reason"], "issue_id|sequential")
                elif case == "empty_new_text":
                    self.assertRegex(result["reason"], "new_text|non-empty")
                else:
                    self.assertIn("revision", result["reason"].lower())

    def test_research_tampering_blocks_later_steps(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        prepared = runctl.prepare_technical_review(self.args(run_id=run_id))
        Path(prepared["output_path"]).write_text(
            json.dumps(self.research_payload(prepared)), encoding="utf-8"
        )
        runctl.record_technical_review(self.args(run_id=run_id))
        Path(prepared["output_path"]).write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(runctl.RunError, "SHA-256 changed"):
            runctl.prepare_judge(self.args(run_id=run_id, family="technical"))

    def test_manifest_findings_and_judge_basis_tampering_are_detected(self):
        findings_run = self.init()["run_id"]
        self.complete_candidates(findings_run)
        self.complete_research(findings_run)
        manifest_path = self.staging / findings_run / "run.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["technical_review"]["result"]["findings"][0]["correction"] = (
            "Tampered guidance."
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(runctl.RunError, "findings record changed"):
            runctl.status_result(self.args(run_id=findings_run))

        basis_run = self.make_evaluated_run()
        manifest_path = self.staging / basis_run / "run.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        alias = manifest["evaluations"]["technical"]["packet"]["order"][0]
        manifest["evaluations"]["technical"]["packet"]["basis"][alias]["sha256"] = (
            "0" * 64
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(runctl.RunError, "judge basis changed"):
            runctl.status_result(self.args(run_id=basis_run))

    def test_status_tampering_cannot_hide_artifacts_or_bypass_publication(self):
        candidate_run = self.init()["run_id"]
        self.complete_candidates(candidate_run)
        manifest_path = self.staging / candidate_run / "run.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        candidate = manifest["candidates"]["emotional"][0]
        Path(candidate["output_path"]).write_text(
            self.emotional_body(0) + "tampered\n", encoding="utf-8"
        )
        candidate["status"] = "pending"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(runctl.RunError, "validated status changed"):
            runctl.status_result(self.args(run_id=candidate_run))

        publication_run = self.init()["run_id"]
        self.complete_candidates(publication_run)
        manifest_path = self.staging / publication_run / "run.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "ready"
        manifest["audit"]["status"] = "passed"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(runctl.RunError, "research|judges|accepted"):
            runctl.publish(self.args(run_id=publication_run))

    def test_family_audits_have_distinct_prompts_and_evidence(self):
        run_id = self.make_evaluated_run()
        emotional = runctl.prepare_audit(self.args(run_id=run_id, family="emotional"))
        self.assertEqual(
            Path(emotional["prompt_path"]).name, "fidelity-auditor-emotional.md"
        )
        self.assertIsNone(emotional["evidence_path"])
        Path(emotional["output_path"]).write_text(
            json.dumps(self.audit_payload(emotional)), encoding="utf-8"
        )
        runctl.record_audit(self.args(run_id=run_id, family="emotional"))

        technical = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        self.assertEqual(
            Path(technical["prompt_path"]).name, "fidelity-auditor-technical.md"
        )
        self.assertTrue(Path(technical["evidence_path"]).is_file())

    def test_technical_audit_cannot_ignore_or_cross_apply_candidate_findings(self):
        cases = ("ignored", "cross_applied")
        for case in cases:
            with self.subTest(case=case):
                run_id = self.init()["run_id"]
                self.complete_candidates(run_id)
                self.complete_candidate_specific_research(run_id)
                self.complete_evaluations(run_id)
                prepared = runctl.prepare_audit(
                    self.args(run_id=run_id, family="technical")
                )
                if case == "ignored":
                    payload = self.audit_payload(prepared, verdict="pass")
                    payload["checks"]["technical_correctness"]["evidence"] = [
                        "Generic correctness statement without a finding ID."
                    ]
                else:
                    payload = self.audit_payload(
                        prepared,
                        verdict="fail",
                        issue_id="issue-001",
                        excerpt="Candidate 0 explains the connection.",
                    )
                    payload["hard_failures"][0]["finding_ids"] = ["finding-002"]
                Path(prepared["output_path"]).write_text(
                    json.dumps(payload), encoding="utf-8"
                )
                result = runctl.record_audit(
                    self.args(run_id=run_id, family="technical")
                )
                self.assertEqual(result["status"], "invalid")
                self.assertIn("finding", result["reason"].lower())

    def test_technical_audit_requires_independent_sources_and_claim_scoped_findings(
        self,
    ):
        source_run = self.make_evaluated_run()
        prepared = runctl.prepare_audit(
            self.args(run_id=source_run, family="technical")
        )
        payload = self.audit_payload(prepared)
        payload["sources"] = []
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_audit(self.args(run_id=source_run, family="technical"))
        self.assertEqual(result["status"], "invalid")
        self.assertIn("independently checked", result["reason"])

        claim_run = self.init()["run_id"]
        self.complete_candidates(claim_run)
        self.complete_research(claim_run, unresolved=True)
        self.complete_evaluations(claim_run)
        prepared = runctl.prepare_audit(self.args(run_id=claim_run, family="technical"))
        payload = self.audit_payload(
            prepared,
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        payload["hard_failures"][0]["finding_ids"] = ["finding-001"]
        payload["hard_failures"][0]["sources"] = []
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_audit(self.args(run_id=claim_run, family="technical"))
        self.assertEqual(result["status"], "invalid")
        self.assertIn("does not match", result["reason"])

    def test_technical_audit_and_repair_receive_candidate_filtered_evidence(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        payload = self.complete_candidate_specific_research(run_id)
        self.complete_evaluations(run_id)
        mapping = self.manifest(run_id)["technical_review"]["packet"]["mapping"]
        expected_alias = next(alias for alias, index in mapping.items() if index == 0)

        prepared = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        audit_evidence = json.loads(
            Path(prepared["evidence_path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            [finding["finding_id"] for finding in audit_evidence["findings"]],
            ["finding-001"],
        )
        self.assertEqual(
            audit_evidence["findings"][0]["candidate_ids"], [expected_alias]
        )
        self.assertNotIn("finding-002", json.dumps(audit_evidence))
        self.assertIn("finding-002", json.dumps(payload))

        audit_payload = self.audit_payload(
            prepared,
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        Path(prepared["output_path"]).write_text(
            json.dumps(audit_payload), encoding="utf-8"
        )
        result = runctl.record_audit(self.args(run_id=run_id, family="technical"))
        self.assertEqual(result["status"], "repair_pending")

        repair = runctl.prepare_repair(self.args(run_id=run_id, family="technical"))
        repair_evidence = json.loads(
            Path(repair["evidence_path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            [finding["finding_id"] for finding in repair_evidence["findings"]],
            ["finding-001"],
        )
        self.assertNotIn("finding-002", json.dumps(repair_evidence))

    def test_repair_cannot_cross_apply_another_candidates_finding(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        self.complete_candidate_specific_research(run_id)
        self.complete_evaluations(run_id)
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        prepared = runctl.prepare_repair(self.args(run_id=run_id, family="technical"))
        payload = self.repair_payload(
            prepared,
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text=self.post_session_correction(
                "Candidate 0 accurately explains the connection."
            ),
            finding_ids=["finding-002"],
            enforce_inline_contract=False,
        )
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_repair(self.args(run_id=run_id, family="technical"))
        self.assertEqual(result["status"], "invalid")
        self.assertIn("finding", result["reason"].lower())

    def test_failed_audit_is_surgically_repaired_without_rejudging(self):
        run_id = self.make_evaluated_run()
        self.record_audit(run_id, "emotional")
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        before = self.manifest(run_id)
        judged = before["evaluations"]["technical"]["result"]
        original = before["candidates"]["technical"][0]["revisions"][0]
        original_path = Path(original["output_path"])
        original_bytes = original_path.read_bytes()

        prepared, result = self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text="Candidate 0 accurately explains the connection.",
        )
        self.assertEqual(result["status"], "repaired", result)
        self.assertEqual(prepared["base_revision"], 0)
        after = self.manifest(run_id)
        revisions = after["candidates"]["technical"][0]["revisions"]
        self.assertEqual([item["revision"] for item in revisions], [0, 1])
        self.assertEqual(original_path.read_bytes(), original_bytes)
        self.assertIn(
            "Candidate 0 accurately explains the connection.",
            Path(revisions[1]["output_path"]).read_text(encoding="utf-8"),
        )
        self.assertEqual(after["evaluations"]["technical"]["result"], judged)
        self.assertEqual(after["evaluations"]["technical"]["attempts"], 1)

        next_audit = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        self.assertEqual(next_audit["revision"], 1)
        self.assertEqual(next_audit["candidate_id"], "technical_0.r1")

    def test_repair_rejects_nonunique_overlapping_noop_and_unknown_issue_edits(self):
        cases = ("nonunique", "overlap", "noop", "unknown")
        expected_reasons = {
            "nonunique": "occur exactly once",
            "overlap": "overlap",
            "noop": "changed",
            "unknown": "unknown",
        }
        for case in cases:
            with self.subTest(case=case):
                run_id = self.make_evaluated_run()
                if case == "overlap":
                    audit = runctl.prepare_audit(
                        self.args(run_id=run_id, family="technical")
                    )
                    audit_payload = self.audit_payload(
                        audit,
                        verdict="fail",
                        issue_id="issue-001",
                        excerpt="Candidate 0 explains the connection.",
                    )
                    second_issue = dict(audit_payload["hard_failures"][0])
                    second_issue.update(
                        {
                            "issue_id": "issue-002",
                            "candidate_excerpt": "SHA-256 produces a 256-bit digest.",
                        }
                    )
                    audit_payload["hard_failures"].append(second_issue)
                    Path(audit["output_path"]).write_text(
                        json.dumps(audit_payload), encoding="utf-8"
                    )
                    result = runctl.record_audit(
                        self.args(run_id=run_id, family="technical")
                    )
                    self.assertEqual(result["status"], "repair_pending")
                else:
                    self.record_audit(
                        run_id,
                        "technical",
                        verdict="fail",
                        issue_id="issue-001",
                        excerpt="Candidate 0 explains the connection.",
                    )
                prepared = runctl.prepare_repair(
                    self.args(run_id=run_id, family="technical")
                )
                payload = self.repair_payload(
                    prepared,
                    issue_id="issue-001",
                    old_text="Candidate 0 explains the connection.",
                    new_text="Candidate 0 accurately explains the connection.",
                    finding_ids=[],
                )
                if case == "nonunique":
                    payload["replacements"][0]["old_text"] = "the connection."
                elif case == "overlap":
                    payload["replacements"].append(
                        {
                            "resolves": ["issue-002"],
                            "old_text": (
                                "Candidate 0 explains the connection.\n"
                                "- SHA-256 produces a 256-bit digest."
                            ),
                            "new_text": self.post_session_correction(
                                "Candidate 0 carefully explains the connection.\n"
                                "- SHA-256 produces a 256-bit digest."
                            ),
                            "reason": "A second overlapping edit.",
                            "finding_ids": [],
                        }
                    )
                elif case == "noop":
                    payload["replacements"][0]["new_text"] = payload["replacements"][0][
                        "old_text"
                    ]
                else:
                    payload["replacements"][0]["resolves"] = ["issue-999"]
                Path(prepared["output_path"]).write_text(
                    json.dumps(payload), encoding="utf-8"
                )
                result = runctl.record_repair(
                    self.args(run_id=run_id, family="technical")
                )
                self.assertEqual(result["status"], "invalid")
                self.assertTrue(result["retry_available"])
                self.assertIn(expected_reasons[case], result["reason"])
                revisions = self.manifest(run_id)["candidates"]["technical"][0][
                    "revisions"
                ]
                self.assertEqual(len(revisions), 1)

    def test_repair_rejects_a_whole_candidate_rewrite(self):
        run_id = self.make_evaluated_run()
        self.record_audit(
            run_id,
            "emotional",
            verdict="fail",
            issue_id="issue-001",
            excerpt="The two ideas connect.",
        )
        prepared = runctl.prepare_repair(self.args(run_id=run_id, family="emotional"))
        original = Path(prepared["candidate_path"]).read_text(encoding="utf-8")
        replacement = self.emotional_body(99)
        payload = self.repair_payload(
            prepared,
            issue_id="issue-001",
            old_text=original,
            new_text=replacement,
        )
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_repair(self.args(run_id=run_id, family="emotional"))
        self.assertEqual(result["status"], "invalid")
        self.assertRegex(result["reason"], "entire candidate|surgical")

        retry = runctl.prepare_repair(self.args(run_id=run_id, family="emotional"))
        expanded = self.repair_payload(
            retry,
            issue_id="issue-001",
            old_text="The two ideas connect.",
            new_text="Expanded replacement. " * 10_000,
        )
        Path(retry["output_path"]).write_text(json.dumps(expanded), encoding="utf-8")
        result = runctl.record_repair(self.args(run_id=run_id, family="emotional"))
        self.assertEqual(result["status"], "invalid")
        self.assertIn("expands too far", result["reason"])

    def test_malformed_repair_retry_does_not_consume_semantic_round(self):
        run_id = self.make_evaluated_run()
        self.record_audit(run_id, "emotional")
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        malformed = runctl.prepare_repair(self.args(run_id=run_id, family="technical"))
        Path(malformed["output_path"]).write_text("{}", encoding="utf-8")
        result = runctl.record_repair(self.args(run_id=run_id, family="technical"))
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(result["retry_available"])

        self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text="Candidate 0 accurately explains the connection.",
        )
        _, result = self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 accurately explains the connection.",
        )
        self.assertNotEqual(result["status"], "awaiting_user")
        status = runctl.status_result(self.args(run_id=run_id))
        self.assert_next_contains(status, "prepare-repair")

    def test_two_failed_semantic_repairs_pause_and_preserve_sibling_acceptance(self):
        run_id = self.make_awaiting_user_run()
        status = runctl.status_result(self.args(run_id=run_id))
        self.assertEqual(status["status"], "awaiting_user")
        self.assertEqual(status["audit"]["accepted"]["emotional"]["index"], 0)
        self.assertEqual(status["audit"]["accepted"]["emotional"]["revision"], 0)
        self.assertNotIn("technical", status["audit"]["accepted"])
        self.assert_next_contains(status, "await-user")
        self.assertEqual(
            set(status["next"]["await_user"]["actions"]),
            {"retry", "advance", "export-review", "stop"},
        )
        self.assertTrue((self.staging / run_id / "run.json").is_file())

    def test_user_can_authorize_exactly_one_extra_repair_round(self):
        run_id = self.make_awaiting_user_run()
        result = runctl.resolve_repair_limit(
            self.args(run_id=run_id, family="technical", action="retry")
        )
        self.assertIn(result["status"], {"authorized", "pending", "repair_pending"})
        self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text="Candidate 0 accurately explains the supported connection.",
            new_text="Candidate 0 explains the supported connection with evidence.",
        )
        _, result = self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the supported connection with evidence.",
        )
        self.assertEqual(result["status"], "awaiting_user")

    def test_user_can_advance_to_next_ranked_candidate(self):
        run_id = self.make_awaiting_user_run()
        result = runctl.resolve_repair_limit(
            self.args(run_id=run_id, family="technical", action="advance")
        )
        self.assertIn(result["status"], {"advanced", "pending"})
        prepared = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        self.assertEqual(prepared["candidate_id"], "technical_1.r0")
        self.assertEqual(prepared["revision"], 0)

    def test_awaiting_menu_omits_advance_when_last_ranked_candidate_fails(self):
        run_id = self.make_awaiting_user_run()
        runctl.resolve_repair_limit(
            self.args(run_id=run_id, family="technical", action="advance")
        )
        self.exhaust_current_technical_candidate(run_id, 1)
        runctl.resolve_repair_limit(
            self.args(run_id=run_id, family="technical", action="advance")
        )
        result = self.exhaust_current_technical_candidate(run_id, 2)
        actions = result["next"]["await_user"]["actions"]
        self.assertEqual(set(actions), {"retry", "export-review", "stop"})
        status = runctl.status_result(self.args(run_id=run_id))
        self.assertEqual(
            set(status["next"]["await_user"]["actions"]),
            {"retry", "export-review", "stop"},
        )

    def test_manual_export_is_marked_and_has_exact_inventory(self):
        run_id = self.make_awaiting_user_run()
        result = runctl.export_review(self.args(run_id=run_id))
        folder = Path(result["folder"])
        self.assertTrue(folder.name.endswith("-manual-review"))
        self.assertEqual({item.name for item in folder.iterdir()}, EXPECTED_INVENTORY)
        public = json.loads((folder / "run.json").read_text(encoding="utf-8"))
        self.assertNotEqual(public["status"], "published")
        self.assertTrue(public["publication"]["manual"])
        self.assertIn(
            "manual-review",
            (folder / "evaluation.md").read_text(encoding="utf-8").lower(),
        )
        self.assertTrue((self.staging / run_id / "run.json").is_file())

    def test_repaired_publish_uses_latest_revision_and_retains_private_staging(self):
        run_id = self.make_evaluated_run()
        self.record_audit(run_id, "emotional")
        self.record_audit(
            run_id,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        self.record_repair(
            run_id,
            "technical",
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text="Candidate 0 accurately explains the connection.",
        )
        _, audit = self.record_audit(run_id, "technical")
        self.assertEqual(audit["status"], "passed")
        result = runctl.publish(self.args(run_id=run_id))
        folder = Path(result["folder"])
        self.assertEqual({item.name for item in folder.iterdir()}, EXPECTED_INVENTORY)
        self.assertIn(
            "Candidate 0 accurately explains the connection.",
            (folder / "technical_0.md").read_text(encoding="utf-8"),
        )
        self.assertTrue((self.staging / run_id / "run.json").is_file())
        evaluation = (folder / "evaluation.md").read_text(encoding="utf-8")
        self.assertIn("finding-001", evaluation)
        self.assertIn("issue-001", evaluation)
        self.assertIn("revision", evaluation.lower())

    def test_unrepaired_publish_has_exact_inventory_and_frontmatter(self):
        run_id = self.make_ready_run()
        private = self.manifest(run_id)
        candidate_mapping = private["technical_review"]["packet"]["mapping"]
        result = runctl.publish(self.args(run_id=run_id))
        folder = Path(result["folder"])
        self.assertEqual({item.name for item in folder.iterdir()}, EXPECTED_INVENTORY)
        self.assertFalse(list(folder.glob("result_*.md")))
        emotional = (folder / "emotional_0.md").read_text(encoding="utf-8")
        self.assertIn("date: 2026-07-10", emotional)
        self.assertIn("review-config_template: codex-native-v2", emotional)
        self.assertIn(f"review-run_id: {run_id}", emotional)
        public = json.loads((folder / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(public["schema_version"], "codex-native-v2")
        self.assertEqual(public["publication"]["files"], 8)
        self.assertEqual(public["audit"]["status"], "passed")
        self.assertEqual(
            public["technical_review"]["candidate_mapping"], candidate_mapping
        )
        self.assertFalse((self.staging / run_id).exists())

    def test_published_candidate_metadata_distinguishes_accepted_from_unaudited(self):
        run_id = self.make_ready_run()
        result = runctl.publish(self.args(run_id=run_id))
        folder = Path(result["folder"])

        def audit_status(filename: str) -> str:
            line = next(
                line
                for line in (folder / filename).read_text(encoding="utf-8").splitlines()
                if line.startswith("review-audit_status:")
            )
            return line.split(":", 1)[1].strip().lower()

        accepted = audit_status("emotional_0.md")
        sibling = audit_status("emotional_1.md")
        self.assertNotEqual(accepted, sibling)
        self.assertRegex(accepted, "accepted|pass")
        self.assertRegex(sibling, "not.*audit|unaudited")

    def test_resume_reports_every_new_boundary(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        status = runctl.status_result(self.args(run_id=run_id), resume=True)
        self.assert_next_contains(status, "prepare-technical-review")

        research = runctl.prepare_technical_review(self.args(run_id=run_id))
        Path(research["output_path"]).write_text(
            json.dumps(self.research_payload(research)), encoding="utf-8"
        )
        status = runctl.status_result(self.args(run_id=run_id), resume=True)
        self.assert_next_contains(status, "record-technical-review")
        runctl.record_technical_review(self.args(run_id=run_id))
        self.complete_evaluations(run_id)

        audit = runctl.prepare_audit(self.args(run_id=run_id, family="emotional"))
        Path(audit["output_path"]).write_text(
            json.dumps(
                self.audit_payload(
                    audit,
                    verdict="fail",
                    issue_id="issue-001",
                    excerpt="The two ideas connect.",
                )
            ),
            encoding="utf-8",
        )
        status = runctl.status_result(self.args(run_id=run_id), resume=True)
        self.assert_next_contains(status, "record-audit")
        runctl.record_audit(self.args(run_id=run_id, family="emotional"))
        status = runctl.status_result(self.args(run_id=run_id), resume=True)
        self.assert_next_contains(status, "prepare-repair")

        repair = runctl.prepare_repair(self.args(run_id=run_id, family="emotional"))
        Path(repair["output_path"]).write_text(
            json.dumps(
                self.repair_payload(
                    repair,
                    issue_id="issue-001",
                    old_text="The two ideas connect.",
                    new_text="The two ideas connect in the discussed example.",
                )
            ),
            encoding="utf-8",
        )
        status = runctl.status_result(self.args(run_id=run_id), resume=True)
        self.assert_next_contains(status, "record-repair")

    def test_candidate_and_revision_tampering_are_detected(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        candidate = self.manifest(run_id)["candidates"]["emotional"][0]["revisions"][0]
        Path(candidate["output_path"]).write_text(
            self.emotional_body(0) + "\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(runctl.RunError, "SHA-256 changed"):
            runctl.prepare_technical_review(self.args(run_id=run_id))

        repaired_run = self.make_evaluated_run()
        self.record_audit(
            repaired_run,
            "technical",
            verdict="fail",
            issue_id="issue-001",
            excerpt="Candidate 0 explains the connection.",
        )
        self.record_repair(
            repaired_run,
            "technical",
            issue_id="issue-001",
            old_text="Candidate 0 explains the connection.",
            new_text="Candidate 0 accurately explains the connection.",
        )
        repaired = self.manifest(repaired_run)["candidates"]["technical"][0][
            "revisions"
        ][1]
        Path(repaired["output_path"]).write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(runctl.RunError, "SHA-256 changed"):
            runctl.prepare_audit(self.args(run_id=repaired_run, family="technical"))

    def test_valid_audit_and_repair_hashes_are_mandatory(self):
        audit_run = self.make_ready_run()
        manifest_path = self.staging / audit_run / "run.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["audit"]["families"]["emotional"]["rounds"][0].pop("output_sha256")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(runctl.RunError, "audit result SHA-256 changed"):
            runctl.status_result(self.args(run_id=audit_run))

        repair_run = self.make_evaluated_run()
        self.record_audit(
            repair_run,
            "emotional",
            verdict="fail",
            issue_id="issue-001",
            excerpt="The two ideas connect.",
        )
        self.record_repair(
            repair_run,
            "emotional",
            issue_id="issue-001",
            old_text="The two ideas connect.",
            new_text="The two ideas connect in the discussed example.",
        )
        manifest_path = self.staging / repair_run / "run.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["audit"]["families"]["emotional"]["repairs"][0].pop("output_sha256")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(runctl.RunError, "repair result SHA-256 changed"):
            runctl.status_result(self.args(run_id=repair_run))

    def test_publish_fails_without_visible_partial_output(self):
        run_id = self.init()["run_id"]
        with self.assertRaises(runctl.RunError):
            runctl.publish(self.args(run_id=run_id))
        self.assertFalse(self.output_base.exists())

    def test_invalid_and_duplicate_candidates_offer_one_retry(self):
        run_id = self.init()["run_id"]
        first = runctl.start_candidate(
            self.args(run_id=run_id, family="emotional", index=0)
        )
        Path(first["output_path"]).write_text("   ", encoding="utf-8")
        invalid = runctl.validate_candidate(
            self.args(run_id=run_id, family="emotional", index=0)
        )
        self.assertTrue(invalid["retry_available"])
        retry = runctl.start_candidate(
            self.args(run_id=run_id, family="emotional", index=0)
        )
        body = self.emotional_body(0)
        Path(retry["output_path"]).write_text(body, encoding="utf-8")
        self.assertEqual(
            runctl.validate_candidate(
                self.args(run_id=run_id, family="emotional", index=0)
            )["status"],
            "valid",
        )
        duplicate = runctl.start_candidate(
            self.args(run_id=run_id, family="emotional", index=1)
        )
        Path(duplicate["output_path"]).write_text(body, encoding="utf-8")
        duplicate_result = runctl.validate_candidate(
            self.args(run_id=run_id, family="emotional", index=1)
        )
        self.assertEqual(duplicate_result["status"], "invalid")
        self.assertIn("duplicate", duplicate_result["reason"])

    def test_candidate_structure_guards_remain_in_force(self):
        run_id = self.init()["run_id"]
        technical = runctl.start_candidate(
            self.args(run_id=run_id, family="technical", index=0)
        )
        Path(technical["output_path"]).write_text(
            "# ⭐ Aha Moments & Discovery Journey\nNo placeholder.\n",
            encoding="utf-8",
        )
        result = runctl.validate_candidate(
            self.args(run_id=run_id, family="technical", index=0)
        )
        self.assertEqual(result["status"], "invalid")
        self.assertIn("placeholder", result["reason"])

        emotional = runctl.start_candidate(
            self.args(run_id=run_id, family="emotional", index=0)
        )
        Path(emotional["output_path"]).write_text(
            "---\ntitle: Model frontmatter\n---\n\n" + self.emotional_body(0),
            encoding="utf-8",
        )
        result = runctl.validate_candidate(
            self.args(run_id=run_id, family="emotional", index=0)
        )
        self.assertEqual(result["status"], "invalid")
        self.assertIn("frontmatter", result["reason"])

    def test_required_candidate_structures_are_publication_gates(self):
        run_id = self.init()["run_id"]
        technical = runctl.start_candidate(
            self.args(run_id=run_id, family="technical", index=0)
        )
        Path(technical["output_path"]).write_text(
            "# ⭐ Aha Moments & Discovery Journey\n[AHA_PLACEHOLDER]\n",
            encoding="utf-8",
        )
        result = runctl.validate_candidate(
            self.args(run_id=run_id, family="technical", index=0)
        )
        self.assertEqual(result["status"], "invalid")
        self.assertRegex(result["reason"], "Title|title|section|TL;DR")

        emotional = runctl.start_candidate(
            self.args(run_id=run_id, family="emotional", index=0)
        )
        Path(emotional["output_path"]).write_text(
            "## A moment\n\n> A vague recollection without the required callouts.\n",
            encoding="utf-8",
        )
        result = runctl.validate_candidate(
            self.args(run_id=run_id, family="emotional", index=0)
        )
        self.assertEqual(result["status"], "invalid")
        self.assertRegex(result["reason"], "SUMMARY|SUCCESS|callout|structure")

    def test_audit_not_applicable_rules_are_family_specific(self):
        run_id = self.make_evaluated_run()
        emotional = runctl.prepare_audit(self.args(run_id=run_id, family="emotional"))
        payload = self.audit_payload(emotional)
        payload["checks"]["quote_fidelity"] = {
            "status": "not_applicable",
            "evidence": [],
        }
        Path(emotional["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_audit(self.args(run_id=run_id, family="emotional"))
        self.assertEqual(result["status"], "invalid")

        technical = runctl.prepare_audit(self.args(run_id=run_id, family="technical"))
        payload = self.audit_payload(technical)
        for name in ("formula_validity", "correction_transparency"):
            payload["checks"][name] = {"status": "not_applicable", "evidence": []}
        Path(technical["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_audit(self.args(run_id=run_id, family="technical"))
        self.assertIn(result["status"], {"accepted", "passed", "pending"})

    def test_malformed_audit_retries_once_and_preserves_run(self):
        run_id = self.make_evaluated_run()
        for attempt in range(1, runctl.MAX_ATTEMPTS + 1):
            prepared = runctl.prepare_audit(
                self.args(run_id=run_id, family="emotional")
            )
            self.assertEqual(prepared["attempt"], attempt)
            Path(prepared["output_path"]).write_text("{}", encoding="utf-8")
            result = runctl.record_audit(self.args(run_id=run_id, family="emotional"))
        self.assertEqual(result["status"], "invalid")
        self.assertFalse(result["retry_available"])
        self.assertTrue((self.staging / run_id / "run.json").is_file())
        self.assertFalse(self.output_base.exists())

    def test_publish_cleans_partial_directory_after_mid_publish_failure(self):
        run_id = self.make_ready_run()
        original = runctl.write_json_atomic

        def fail_visible_manifest(path, payload):
            if path.name == "run.json" and ".partial-" in path.parent.name:
                raise runctl.RunError("simulated publication failure")
            return original(path, payload)

        with patch.object(
            runctl, "write_json_atomic", side_effect=fail_visible_manifest
        ):
            with self.assertRaisesRegex(
                runctl.RunError, "simulated publication failure"
            ):
                runctl.publish(self.args(run_id=run_id))
        self.assertFalse(list(self.output_base.rglob("*.md")))
        self.assertFalse(list(self.output_base.rglob("run.json")))
        self.assertFalse(list(self.output_base.rglob("*.partial-*")))
        self.assertTrue((self.staging / run_id / "run.json").is_file())

    def test_publish_retry_recovers_after_post_rename_manifest_save_failure(self):
        run_id = self.make_ready_run()
        original = runctl.save_manifest

        def fail_published_state(path, manifest):
            if manifest["status"] == "published":
                raise runctl.RunError("simulated post-rename manifest failure")
            return original(path, manifest)

        with patch.object(runctl, "save_manifest", side_effect=fail_published_state):
            with self.assertRaisesRegex(
                runctl.RunError, "simulated post-rename manifest failure"
            ):
                runctl.publish(self.args(run_id=run_id))

        visible = [
            folder for folder in self.output_base.rglob(run_id) if folder.is_dir()
        ]
        self.assertEqual(len(visible), 1)
        self.assertEqual(
            {item.name for item in visible[0].iterdir()}, EXPECTED_INVENTORY
        )
        self.assertEqual(self.manifest(run_id)["status"], "ready")

        candidate_path = visible[0] / "technical_0.md"
        original_candidate = candidate_path.read_text(encoding="utf-8")
        candidate_path.write_text(
            original_candidate + "\nTampered after the folder move.\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(runctl.RunError, "candidate content changed"):
            runctl.publish(self.args(run_id=run_id))
        candidate_path.write_text(original_candidate, encoding="utf-8")

        result = runctl.publish(self.args(run_id=run_id))
        self.assertEqual(result["status"], "published")
        self.assertEqual(Path(result["folder"]).resolve(), visible[0].resolve())
        self.assertEqual(
            {item.name for item in visible[0].iterdir()}, EXPECTED_INVENTORY
        )
        self.assertFalse((self.staging / run_id).exists())

    def test_ranking_must_match_weighted_scores(self):
        run_id = self.init()["run_id"]
        self.complete_candidates(run_id)
        self.complete_research(run_id)
        prepared = runctl.prepare_judge(self.args(run_id=run_id, family="emotional"))
        payload = self.judge_payload(self.manifest(run_id), "emotional")
        payload["ranking"] = list(reversed(payload["ranking"]))
        payload["recommendation"] = payload["ranking"][0]
        Path(prepared["output_path"]).write_text(json.dumps(payload), encoding="utf-8")
        result = runctl.record_evaluation(self.args(run_id=run_id, family="emotional"))
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(result["retry_available"])

    def test_source_probe_copy_hash_and_collision_behaviors(self):
        probed = runctl.probe_source(
            self.args(
                clipboard=False,
                file=str(self.source.resolve()),
                max_bytes=runctl.DEFAULT_MAX_BYTES,
            )
        )
        self.assertNotIn("content", probed)
        first = self.init(topic="collision")
        second = self.init(topic="collision")
        self.assertEqual(
            Path(first["transcript_path"]).name, "input-2026-07-10-collision.md"
        )
        self.assertEqual(
            Path(second["transcript_path"]).name, "input-2026-07-10-collision-2.md"
        )
        manifest = self.manifest(first["run_id"])
        self.assertEqual(
            manifest["source"]["sha256"],
            runctl.sha256_file(Path(first["transcript_path"])),
        )

    def test_publication_parent_cannot_escape_output_base(self):
        unusual = self.input_dir / "..md"
        unusual.write_text(self.source.read_text(encoding="utf-8"), encoding="utf-8")
        initialized = runctl.init_run(
            self.args(
                clipboard=False,
                file=str(unusual.resolve()),
                date="2026-07-10",
                topic="safe-topic",
                reuse_canonical=True,
                max_bytes=runctl.DEFAULT_MAX_BYTES,
            )
        )
        manifest = self.manifest(initialized["run_id"])
        parent = runctl.publication_parent(manifest)
        self.assertTrue(parent.is_relative_to(self.output_base.resolve()))
        self.assertNotEqual(parent, self.output_base.resolve())

    def test_short_clipboard_and_oversized_files_leave_no_input(self):
        with patch.object(runctl, "command_text", return_value="short"):
            with self.assertRaises(runctl.RunError):
                runctl.init_run(
                    self.args(
                        clipboard=True,
                        file=None,
                        date="2026-07-10",
                        topic="clipboard",
                        reuse_canonical=False,
                        max_bytes=runctl.DEFAULT_MAX_BYTES,
                    )
                )
        with self.assertRaises(runctl.RunError):
            runctl.init_run(
                self.args(
                    clipboard=False,
                    file=str(self.source.resolve()),
                    date="2026-07-10",
                    topic="too-large",
                    reuse_canonical=False,
                    max_bytes=10,
                )
            )
        self.assertFalse(list(self.input_dir.glob("input-*.md")))

    def write_legacy_manifest(self, *, prompt_drift: bool) -> str:
        run_id = "20260710-120000-abcd"
        run_dir = self.staging / run_id
        for name in ("candidates", "packets", "judges", "audits"):
            (run_dir / name).mkdir(parents=True, exist_ok=True)
        prompts = {}
        legacy_names = (
            "emotional",
            "technical",
            "judge_emotional",
            "judge_technical",
            "auditor",
        )
        for name in legacy_names:
            prompt = (
                runctl.SKILL_ROOT / "references" / "fidelity-auditor.md"
                if name == "auditor"
                else runctl.PROMPTS[name]
            )
            prompts[name] = {
                "path": str(prompt),
                "sha256": (
                    "0" * 64
                    if prompt_drift and name == "auditor"
                    else runctl.sha256_file(prompt)
                ),
            }
        candidates = {
            family: [
                {
                    "index": index,
                    "status": "pending",
                    "attempts": 0,
                    "output_path": None,
                    "sha256": None,
                    "failure": None,
                    "published_file": f"{family}_{index}.md",
                }
                for index in range(3)
            ]
            for family in ("emotional", "technical")
        }
        legacy_candidate = run_dir / "candidates" / "emotional_0.attempt1.md"
        legacy_content = "\nLegacy candidate body with surrounding whitespace.\n\n"
        legacy_candidate.write_text(legacy_content, encoding="utf-8")
        candidates["emotional"][0].update(
            {
                "status": "valid",
                "attempts": 1,
                "output_path": str(legacy_candidate),
                "sha256": runctl.sha256_bytes(legacy_content.strip().encode("utf-8")),
            }
        )
        legacy = {
            "schema_version": "codex-native-v1",
            "run_id": run_id,
            "status": "failed",
            "created_at": "2026-07-10T12:00:00+01:00",
            "updated_at": "2026-07-10T12:00:00+01:00",
            "source": {
                "mode": "file",
                "session_date": "2026-07-10",
                "topic": "legacy",
                "input_file": self.source.name,
                "path": str(self.source),
                "sha256": runctl.sha256_file(self.source),
                "byte_count": self.source.stat().st_size,
            },
            "prompts": prompts,
            "candidates": candidates,
            "evaluations": {
                family: {
                    "status": "pending",
                    "attempts": 0,
                    "packet": None,
                    "output_path": None,
                    "result": None,
                    "failure": None,
                }
                for family in ("emotional", "technical")
            },
            "audit": {
                "status": "pending",
                "accepted": {},
                "rejected": {"emotional": [], "technical": []},
                "rounds": [],
            },
            "publication": {"status": "pending", "path": None},
            "config": {
                "repo": str(self.repo),
                "output_base": str(self.output_base),
                "staging_root": str(self.staging),
                "max_bytes": runctl.DEFAULT_MAX_BYTES,
            },
        }
        (run_dir / "run.json").write_text(json.dumps(legacy), encoding="utf-8")
        return run_id

    def test_v1_manifests_are_read_only_and_report_prompt_drift(self):
        run_id = self.write_legacy_manifest(prompt_drift=True)
        result = runctl.status_result(self.args(run_id=run_id), resume=True)
        self.assertTrue(result["read_only"])
        self.assertEqual(result["schema_version"], "codex-native-v1")
        self.assertTrue(result["prompt_drift"])
        self.assertTrue(result["resume_confirm_required"])
        with self.assertRaisesRegex(runctl.RunError, "read-only|legacy"):
            runctl.start_candidate(
                self.args(run_id=run_id, family="emotional", index=0)
            )
        self.assertTrue((self.staging / run_id / "run.json").is_file())

    def test_cli_exposes_every_v2_operation(self):
        parser = runctl.build_parser()
        subparsers = next(
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        )
        self.assertTrue(
            {
                "prepare-technical-review",
                "record-technical-review",
                "prepare-audit",
                "record-audit",
                "prepare-repair",
                "record-repair",
                "resolve-repair-limit",
                "export-review",
            }.issubset(subparsers.choices)
        )


if __name__ == "__main__":
    unittest.main()
