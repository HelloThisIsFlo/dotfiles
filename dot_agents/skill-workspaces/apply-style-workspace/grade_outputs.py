#!/usr/bin/env python3
"""Grade apply-style skill outputs against assertions."""

import json
import re
from pathlib import Path

WORKSPACE = Path("/Users/flo/.claude/skills/apply-style-workspace")
ITERATION = WORKSPACE / "iteration-1"

FILLER_PHRASES = [
    r"it.s important to note",
    r"in this document.? we will",
    r"in this section.? we will",
    r"in conclusion",
    r"it.s worth mentioning",
    r"it.s worth noting",
    r"it is important to",
    r"we will explore",
    r"we have seen that",
]


def read_file(path: Path) -> str:
    return path.read_text()


def has_filler(text: str) -> list[str]:
    """Return list of filler phrases found."""
    found = []
    for phrase in FILLER_PHRASES:
        if re.search(phrase, text, re.IGNORECASE):
            found.append(phrase)
    return found


def count_callouts(text: str) -> int:
    return len(re.findall(r">\s*\[!(important|warning|tip|note)\]", text))


def count_callout_types(text: str) -> dict[str, int]:
    types = {}
    for match in re.findall(r">\s*\[!(important|warning|tip|note)\]", text):
        types[match] = types.get(match, 0) + 1
    return types


def has_table(text: str) -> bool:
    """Check for markdown table (at least header + separator + one row)."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "|" in line and i + 1 < len(lines) and re.match(r"\s*\|[\s\-:|]+\|", lines[i + 1]):
            return True
    return False


def count_tables(text: str) -> int:
    lines = text.split("\n")
    count = 0
    for i, line in enumerate(lines):
        if "|" in line and i + 1 < len(lines) and re.match(r"\s*\|[\s\-:|]+\|", lines[i + 1]):
            count += 1
    return count


def has_emoji_identity(text: str, terms: list[str]) -> dict[str, list[str]]:
    """Check if terms have consistent emoji near them. Returns term -> emoji found."""
    result = {}
    emoji_pattern = r"[\U0001f300-\U0001f9ff\u2600-\u27bf\u2705\u274c\u26a0\ufe0f]"
    for term in terms:
        # Look for emoji within ~30 chars of the term
        matches = []
        for m in re.finditer(re.escape(term), text, re.IGNORECASE):
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            context = text[start:end]
            emojis = re.findall(emoji_pattern, context)
            matches.extend(emojis)
        result[term] = list(set(matches))
    return result


def callout_has_bullets(text: str) -> tuple[bool, list[str]]:
    """Check if callout content uses bullets. Returns (all_have_bullets, violations)."""
    violations = []
    in_callout = False
    callout_title = ""
    callout_lines = []

    for line in text.split("\n"):
        if re.match(r">\s*\[!(important|warning|tip|note)\]", line):
            if in_callout and callout_lines:
                # Check previous callout
                content_lines = [l for l in callout_lines if l.strip() and l.strip() != ">"]
                prose_lines = [l for l in content_lines if not re.match(r">\s*[-*]", l) and not re.match(r">\s*\d+\.", l) and len(l.strip()) > 20]
                # Allow 1-2 prose lines (lead-in sentence, action item)
                if len(prose_lines) > 2:
                    violations.append(f"Callout '{callout_title}' has {len(prose_lines)} prose lines")
            in_callout = True
            callout_title = line.strip()
            callout_lines = []
        elif in_callout:
            if line.startswith(">"):
                callout_lines.append(line)
            else:
                # End of callout
                content_lines = [l for l in callout_lines if l.strip() and l.strip() != ">"]
                prose_lines = [l for l in content_lines if not re.match(r">\s*[-*]", l) and not re.match(r">\s*\d+\.", l) and len(l.strip()) > 20]
                if len(prose_lines) > 2:
                    violations.append(f"Callout '{callout_title}' has {len(prose_lines)} prose lines")
                in_callout = False
                callout_lines = []

    return (len(violations) == 0, violations)


def count_bullet_lines(text: str) -> int:
    return len(re.findall(r"^\s*[-*]\s", text, re.MULTILINE))


def count_paragraph_lines(text: str) -> int:
    """Count non-heading, non-bullet, non-table, non-callout lines with substantial text."""
    count = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith("#")
            and not stripped.startswith("-")
            and not stripped.startswith("*")
            and not stripped.startswith("|")
            and not stripped.startswith(">")
            and not stripped.startswith("```")
            and not stripped.startswith("---")
            and not stripped.startswith("_")
            and len(stripped) > 40
        ):
            count += 1
    return count


def has_code_formatting(text: str) -> int:
    """Count inline code spans."""
    return len(re.findall(r"`[^`]+`", text))


def has_hierarchical_bullets(text: str) -> int:
    """Count indented bullet lines (nested bullets), including inside callouts."""
    # Bare nested bullets
    bare = len(re.findall(r"^[ \t]{2,}[-*]\s", text, re.MULTILINE))
    # Nested bullets inside callouts (>   - pattern)
    callout = len(re.findall(r"^>\s{2,}[-*]\s", text, re.MULTILINE))
    return bare + callout


def has_tier2_reference(text: str) -> bool:
    """Check for italic reference below a horizontal rule."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == "---" and i + 1 < len(lines):
            next_lines = [l.strip() for l in lines[i + 1 : i + 4] if l.strip()]
            for nl in next_lines:
                if nl.startswith("_") and nl.endswith("_"):
                    return True
    return False


def has_trailing_conclusion(text: str) -> bool:
    """Check if document ends with a conclusion-style paragraph."""
    lines = [l for l in text.split("\n") if l.strip()]
    last_10 = lines[-10:] if len(lines) > 10 else lines
    for line in last_10:
        if re.search(r"in conclusion|in summary|to summarize|we have seen that", line, re.IGNORECASE):
            return True
    return False


# ============================================================
# GRADING FUNCTIONS PER EVAL
# ============================================================

def grade_eval1(text: str, config: str) -> list[dict]:
    """Grade eval 1 (rate limiting)."""
    expectations = []
    evals_data = json.loads((WORKSPACE / "evals/evals.json").read_text())
    eval_expectations = evals_data["evals"][0]["expectations"]

    # 1. No filler phrases
    found = has_filler(text)
    expectations.append({
        "text": eval_expectations[0],
        "passed": len(found) == 0,
        "evidence": f"No filler phrases found" if not found else f"Found filler phrases: {found}"
    })

    # 2. At least 2 callouts
    n = count_callouts(text)
    expectations.append({
        "text": eval_expectations[1],
        "passed": n >= 2,
        "evidence": f"Found {n} callouts. Types: {count_callout_types(text)}"
    })

    # 3. Emoji identity for 3 strategies
    emoji_map = has_emoji_identity(text, ["fixed window", "sliding window", "token bucket"])
    all_have_emoji = all(len(v) > 0 for v in emoji_map.values())
    expectations.append({
        "text": eval_expectations[2],
        "passed": all_have_emoji,
        "evidence": f"Emoji found: {emoji_map}"
    })

    # 4. Comparison table
    expectations.append({
        "text": eval_expectations[3],
        "passed": has_table(text),
        "evidence": f"Found {count_tables(text)} table(s)" if has_table(text) else "No tables found"
    })

    # 5. Callout content uses bullets
    ok, violations = callout_has_bullets(text)
    expectations.append({
        "text": eval_expectations[4],
        "passed": ok,
        "evidence": "All callout content uses bullets" if ok else f"Violations: {violations}"
    })

    # 6. Bullet points extensively
    bullets = count_bullet_lines(text)
    paragraphs = count_paragraph_lines(text)
    ratio = bullets / max(bullets + paragraphs, 1)
    expectations.append({
        "text": eval_expectations[5],
        "passed": ratio > 0.5,
        "evidence": f"{bullets} bullet lines, {paragraphs} paragraph lines, ratio={ratio:.2f}"
    })

    # 7. Inline code formatting
    n_code = has_code_formatting(text)
    expectations.append({
        "text": eval_expectations[6],
        "passed": n_code >= 5,
        "evidence": f"Found {n_code} inline code spans"
    })

    # 8. Recommendation in [!important] callout
    has_important = bool(re.search(r">\s*\[!important\]", text))
    # Check if recommendation content is near the important callout
    important_sections = re.findall(r">\s*\[!important\].*?(?=\n[^>]|\Z)", text, re.DOTALL)
    has_rec = any("token bucket" in s.lower() or "public" in s.lower() or "internal" in s.lower() for s in important_sections)
    expectations.append({
        "text": eval_expectations[7],
        "passed": has_important and has_rec,
        "evidence": f"[!important] present: {has_important}, contains recommendation: {has_rec}"
    })

    return expectations


def grade_eval2(text: str, config: str) -> list[dict]:
    """Grade eval 2 (caching gotchas)."""
    evals_data = json.loads((WORKSPACE / "evals/evals.json").read_text())
    eval_expectations = evals_data["evals"][1]["expectations"]
    expectations = []

    # 1. [!important] callout about TTL contains bullets
    important_match = re.search(r">\s*\[!important\].*?\n((?:>.*\n)*)", text)
    if important_match:
        content = important_match.group(1)
        has_bullets = bool(re.search(r">\s*[-*]", content))
        expectations.append({
            "text": eval_expectations[0],
            "passed": has_bullets,
            "evidence": f"[!important] callout found, bullets inside: {has_bullets}"
        })
    else:
        expectations.append({
            "text": eval_expectations[0],
            "passed": False,
            "evidence": "No [!important] callout found"
        })

    # 2. [!warning] uses Pattern C (opening + bullets + action item)
    warning_match = re.search(r">\s*\[!warning\].*?\n((?:>.*\n)*)", text)
    if warning_match:
        content = warning_match.group(1)
        has_bullets = bool(re.search(r">\s*[-*]", content))
        has_bold_action = bool(re.search(r">\s*.*\*\*.*\*\*", content))
        expectations.append({
            "text": eval_expectations[1],
            "passed": has_bullets and has_bold_action,
            "evidence": f"Warning has bullets: {has_bullets}, has bold action item: {has_bold_action}"
        })
    else:
        expectations.append({
            "text": eval_expectations[1],
            "passed": False,
            "evidence": "No [!warning] callout found"
        })

    # 3. Edge cases have expressive emoji
    edge_terms = ["thundering herd", "race condition", "partial invalidation", "nested object"]
    emoji_map = has_emoji_identity(text, edge_terms)
    any_emoji = sum(1 for v in emoji_map.values() if len(v) > 0)
    expectations.append({
        "text": eval_expectations[2],
        "passed": any_emoji >= 2,
        "evidence": f"Emoji near edge cases: {emoji_map} ({any_emoji}/4 have emoji)"
    })

    # 4. Hierarchical bullets
    n = has_hierarchical_bullets(text)
    expectations.append({
        "text": eval_expectations[3],
        "passed": n >= 3,
        "evidence": f"Found {n} nested bullet lines"
    })

    # 5. No filler phrases
    found = has_filler(text)
    expectations.append({
        "text": eval_expectations[4],
        "passed": len(found) == 0,
        "evidence": f"No filler" if not found else f"Found: {found}"
    })

    # 6. At least 3 callouts
    n_callouts = count_callouts(text)
    expectations.append({
        "text": eval_expectations[5],
        "passed": n_callouts >= 3,
        "evidence": f"Found {n_callouts} callouts: {count_callout_types(text)}"
    })

    # 7. Three approaches in structured format (table or structured bullets, not numbered prose)
    # Check for a table or structured presentation of the 3 approaches
    has_approach_table = bool(re.search(r"eager|version tag|short ttl", text, re.IGNORECASE)) and (
        has_table(text) or has_hierarchical_bullets(text) >= 2
    )
    expectations.append({
        "text": eval_expectations[6],
        "passed": has_approach_table,
        "evidence": f"Tables: {count_tables(text)}, nested bullets: {has_hierarchical_bullets(text)}"
    })

    # 8. Tier 2 reference for benchmarks
    expectations.append({
        "text": eval_expectations[7],
        "passed": has_tier2_reference(text),
        "evidence": "Found italic reference below horizontal rule" if has_tier2_reference(text) else "No Tier 2 reference found"
    })

    return expectations


def grade_eval3(text: str, config: str) -> list[dict]:
    """Grade eval 3 (deploy modes)."""
    evals_data = json.loads((WORKSPACE / "evals/evals.json").read_text())
    eval_expectations = evals_data["evals"][2]["expectations"]
    expectations = []

    # 1. Emoji identity for 3 deploy modes
    emoji_map = has_emoji_identity(text, ["blue-green", "rolling", "canary"])
    all_have = all(len(v) > 0 for v in emoji_map.values())
    expectations.append({
        "text": eval_expectations[0],
        "passed": all_have,
        "evidence": f"Emoji: {emoji_map}"
    })

    # 2. Comparison table
    expectations.append({
        "text": eval_expectations[1],
        "passed": has_table(text),
        "evidence": f"Found {count_tables(text)} table(s)"
    })

    # 3. Shared state warning in [!warning]
    warning_types = count_callout_types(text)
    has_warning = warning_types.get("warning", 0) > 0
    warning_content = re.findall(r">\s*\[!warning\].*?\n((?:>.*\n)*)", text)
    warning_text = " ".join(warning_content)
    has_shared_state = bool(re.search(r"shared state|rolling|march 12|data corruption", warning_text, re.IGNORECASE))
    expectations.append({
        "text": eval_expectations[2],
        "passed": has_warning and has_shared_state,
        "evidence": f"Warning callout: {has_warning}, mentions shared state/rolling: {has_shared_state}"
    })

    # 4. No trailing conclusion
    expectations.append({
        "text": eval_expectations[3],
        "passed": not has_trailing_conclusion(text),
        "evidence": "No trailing conclusion" if not has_trailing_conclusion(text) else "Found trailing conclusion"
    })

    # 5. No filler phrases
    found = has_filler(text)
    expectations.append({
        "text": eval_expectations[4],
        "passed": len(found) == 0,
        "evidence": f"No filler" if not found else f"Found: {found}"
    })

    # 6. Recommendation in [!important] with bullets
    important_match = re.search(r">\s*\[!important\].*?\n((?:>.*\n)*)", text)
    if important_match:
        content = important_match.group(1)
        has_bullets = bool(re.search(r">\s*[-*]", content))
        expectations.append({
            "text": eval_expectations[5],
            "passed": has_bullets,
            "evidence": f"[!important] found with bullets: {has_bullets}"
        })
    else:
        expectations.append({
            "text": eval_expectations[5],
            "passed": False,
            "evidence": "No [!important] callout found"
        })

    # 7. Bullet points extensively
    bullets = count_bullet_lines(text)
    paragraphs = count_paragraph_lines(text)
    ratio = bullets / max(bullets + paragraphs, 1)
    expectations.append({
        "text": eval_expectations[6],
        "passed": ratio > 0.4,
        "evidence": f"{bullets} bullets, {paragraphs} paragraphs, ratio={ratio:.2f}"
    })

    # 8. Reference to runbook uses two-tier style
    has_tip_ref = bool(re.search(r"\[!tip\].*\n(?:>.*\n)*.*runbook", text, re.IGNORECASE))
    has_italic_ref = bool(re.search(r"_.*runbook.*_", text, re.IGNORECASE))
    expectations.append({
        "text": eval_expectations[7],
        "passed": has_tip_ref or has_italic_ref or has_tier2_reference(text),
        "evidence": f"Tip callout ref: {has_tip_ref}, italic ref: {has_italic_ref}, tier2: {has_tier2_reference(text)}"
    })

    return expectations


def grade_eval4(text: str, config: str) -> list[dict]:
    """Grade eval 4 (repetition behavior - real doc)."""
    evals_data = json.loads((WORKSPACE / "evals/evals.json").read_text())
    eval_expectations = evals_data["evals"][3]["expectations"]
    expectations = []

    # 1. Emoji identity for schedule types
    emoji_map = has_emoji_identity(text, ["catch_up", "catch-up", "regularly", "from_completion", "from-completion"])
    # Need emoji near at least one variant of each schedule type
    catch_up_emoji = emoji_map.get("catch_up", []) or emoji_map.get("catch-up", [])
    regularly_emoji = emoji_map.get("regularly", [])
    from_comp_emoji = emoji_map.get("from_completion", []) or emoji_map.get("from-completion", [])
    all_have = bool(catch_up_emoji) and bool(regularly_emoji) and bool(from_comp_emoji)
    expectations.append({
        "text": eval_expectations[0],
        "passed": all_have,
        "evidence": f"Emoji: catch-up={catch_up_emoji}, regularly={regularly_emoji}, from-completion={from_comp_emoji}"
    })

    # 2. Fundamental asymmetry in [!important]
    important_sections = re.findall(r">\s*\[!important\].*?\n((?:>.*\n)*)", text)
    has_asymmetry = any("day" in s.lower() and "time" in s.lower() for s in important_sections)
    expectations.append({
        "text": eval_expectations[1],
        "passed": has_asymmetry,
        "evidence": f"Found {len(important_sections)} [!important] callouts, asymmetry rule present: {has_asymmetry}"
    })

    # 3. 14-day divergence in [!warning]
    warning_sections = re.findall(r">\s*\[!warning\].*?\n((?:>.*\n)*)", text)
    has_14day = any("14" in s for s in warning_sections)
    expectations.append({
        "text": eval_expectations[2],
        "passed": has_14day,
        "evidence": f"Found {len(warning_sections)} [!warning] callouts, 14-day mentioned: {has_14day}"
    })

    # 4. MCP Server Warning in [!warning]
    has_mcp_warning = any("mcp" in s.lower() or "warning text" in s.lower() or "incorrect" in s.lower() for s in warning_sections)
    expectations.append({
        "text": eval_expectations[3],
        "passed": has_mcp_warning or len(warning_sections) >= 2,
        "evidence": f"MCP warning in callout: {has_mcp_warning}, total warnings: {len(warning_sections)}"
    })

    # 5. Decision guide uses bullets with emoji
    # Find the decision guide section (may be a ## heading)
    decision_section = re.search(r"##\s*(?:decision|agent|guide|when to use).*?\n([\s\S]*?)(?=\n##\s[^#]|\Z)", text, re.IGNORECASE)
    if decision_section:
        section = decision_section.group(1)
        has_bullets = bool(re.search(r"^\s*[-*]", section, re.MULTILINE))
        emoji_pattern = r"[\U0001f300-\U0001f9ff\u2600-\u27bf\u2705\u274c\u26a0\ufe0f]"
        has_emoji = bool(re.search(emoji_pattern, section))
        expectations.append({
            "text": eval_expectations[4],
            "passed": has_bullets and has_emoji,
            "evidence": f"Decision guide has bullets: {has_bullets}, has emoji: {has_emoji}"
        })
    else:
        expectations.append({
            "text": eval_expectations[4],
            "passed": False,
            "evidence": "Decision guide section not found"
        })

    # 6. No multi-sentence prose where bullets would work
    paragraphs = count_paragraph_lines(text)
    bullets = count_bullet_lines(text)
    ratio = paragraphs / max(bullets + paragraphs, 1)
    expectations.append({
        "text": eval_expectations[5],
        "passed": ratio < 0.4,
        "evidence": f"{paragraphs} paragraph lines, {bullets} bullet lines, prose ratio={ratio:.2f}"
    })

    # 7. Inline code formatting
    n_code = has_code_formatting(text)
    expectations.append({
        "text": eval_expectations[6],
        "passed": n_code >= 10,
        "evidence": f"Found {n_code} inline code spans"
    })

    # 8. Methodology de-emphasized
    # Check if methodology is at the end and separated, or in a secondary position
    lines = text.split("\n")
    total_lines = len(lines)
    methodology_line = None
    for i, line in enumerate(lines):
        if re.search(r"methodology|verification scorecard", line, re.IGNORECASE):
            methodology_line = i
            break
    if methodology_line:
        position_ratio = methodology_line / total_lines
        near_end = position_ratio > 0.8
        has_separator = any(l.strip() == "---" for l in lines[max(0, methodology_line - 3):methodology_line])
        expectations.append({
            "text": eval_expectations[7],
            "passed": near_end or has_separator,
            "evidence": f"Methodology at line {methodology_line}/{total_lines} ({position_ratio:.2f}), separator: {has_separator}"
        })
    else:
        expectations.append({
            "text": eval_expectations[7],
            "passed": True,
            "evidence": "Methodology section either removed or renamed (acceptable de-emphasis)"
        })

    # 9. Tables preserved
    n_tables = count_tables(text)
    expectations.append({
        "text": eval_expectations[8],
        "passed": n_tables >= 4,
        "evidence": f"Found {n_tables} tables (original had ~7)"
    })

    # 10. Technical facts preserved
    key_facts = [
        "10 PM",
        "Apr 3",
        "14",  # 14-day gap
        "BYDAY",
        "INTERVAL",
        "completion date",
        "from scratch",
    ]
    found_facts = sum(1 for f in key_facts if f.lower() in text.lower())
    expectations.append({
        "text": eval_expectations[9],
        "passed": found_facts >= 5,
        "evidence": f"Found {found_facts}/{len(key_facts)} key facts: {[f for f in key_facts if f.lower() in text.lower()]}"
    })

    return expectations


def grade_run(eval_id: int, eval_name: str, config: str):
    """Grade a single run."""
    output_dir = ITERATION / eval_name / config / "outputs"
    output_files = list(output_dir.glob("*.md"))
    if not output_files:
        print(f"  SKIP {eval_name}/{config}: no output files")
        return

    text = read_file(output_files[0])
    timing_path = ITERATION / eval_name / config / "timing.json"
    timing = json.loads(timing_path.read_text()) if timing_path.exists() else {}

    graders = {1: grade_eval1, 2: grade_eval2, 3: grade_eval3, 4: grade_eval4}
    expectations = graders[eval_id](text, config)

    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)

    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total > 0 else 0,
        },
        "timing": {
            "total_duration_seconds": timing.get("total_duration_seconds", 0),
        },
    }

    grading_path = ITERATION / eval_name / config / "grading.json"
    grading_path.write_text(json.dumps(grading, indent=2))
    print(f"  {eval_name}/{config}: {passed}/{total} passed ({grading['summary']['pass_rate']:.0%})")


def main():
    evals = [
        (1, "eval-1-rate-limiting"),
        (2, "eval-2-caching-gotchas"),
        (3, "eval-3-deploy-modes"),
        (4, "eval-4-repetition-behavior"),
    ]

    for eval_id, eval_name in evals:
        print(f"\n=== {eval_name} ===")
        for config in ["with_skill", "without_skill"]:
            grade_run(eval_id, eval_name, config)


if __name__ == "__main__":
    main()
