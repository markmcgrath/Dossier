"""
Regression tests tying the routing ablation experiment
(`tests/golden_prompts/`) to live skill content.

The Phase 2 ablation identified three description gaps fixed directly in
SKILL.md — these tests fail if any of them regress. Also checks structural
integrity of the golden-prompt files themselves so drift between the test
set and the recorded results is caught.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


GOLDEN_DIR_REL = "tests/golden_prompts"

# Trigger phrases added to SKILL.md description per routing_decision.md.
# Each must appear verbatim in the description block of skill/SKILL.md.
REQUIRED_TRIGGER_PHRASES = [
    '"tailor my CV"',
    '"health check"',
    '"calibration report"',
]

# Negative-scope sentence added to reduce false-positive risk on adjacent
# analytics topics (T-032, T-037 in the baseline).
REQUIRED_NEGATIVE_SCOPE = (
    "Only trigger when there is a clear job application, offer, "
    "interview, or outreach context."
)

TEST_ID_RE = re.compile(r"T-\d{3}")


@pytest.fixture(scope="session")
def golden_dir(vault_path: Path) -> Path:
    d = vault_path / GOLDEN_DIR_REL
    assert d.is_dir(), f"golden_prompts directory not found at {d}"
    return d


@pytest.fixture(scope="session")
def routing_test_set(golden_dir: Path) -> str:
    return (golden_dir / "routing_test_set.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def baseline_results(golden_dir: Path) -> str:
    return (golden_dir / "baseline_results.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def routing_decision(golden_dir: Path) -> str:
    return (golden_dir / "routing_decision.md").read_text(encoding="utf-8")


def _ids_in_headings(text: str) -> set[str]:
    """T-IDs that appear in a level-3 heading (the test-case sections)."""
    return {
        m.group(0)
        for line in text.splitlines()
        if line.startswith("### ")
        for m in [TEST_ID_RE.search(line)]
        if m
    }


def _ids_in_result_rows(text: str) -> set[str]:
    """T-IDs that appear as the leading cell of a markdown table row."""
    ids: set[str] = set()
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) >= 2 and TEST_ID_RE.fullmatch(cells[1]):
                ids.add(cells[1])
    return ids


def _description_block(skill_md: str) -> str:
    """Return the YAML `description:` block text from SKILL.md frontmatter."""
    lines = skill_md.splitlines()
    assert lines[0].strip() == "---", "SKILL.md must start with frontmatter"
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    frontmatter = "\n".join(lines[1:end])
    marker = "description:"
    assert marker in frontmatter, "SKILL.md frontmatter missing description"
    return frontmatter[frontmatter.index(marker):]


# ---------------------------------------------------------------------------
# SKILL.md regression — description must retain Phase 2 improvements
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("phrase", REQUIRED_TRIGGER_PHRASES)
def test_description_retains_trigger_phrase(skill_md_source: str, phrase: str) -> None:
    """Description must keep each trigger phrase added by the Phase 2 ablation."""
    desc = _description_block(skill_md_source)
    assert phrase in desc, (
        f"SKILL.md description missing trigger phrase {phrase!r}. "
        f"Phase 2 routing ablation added it to address weak mode coverage; "
        f"removing it reopens a routing gap. See "
        f"tests/golden_prompts/routing_decision.md."
    )


def test_description_retains_negative_scope(skill_md_source: str) -> None:
    """Description must keep the negative-scope sentence (false-positive guard)."""
    desc = _description_block(skill_md_source)
    # Normalize whitespace since the sentence can wrap across YAML lines.
    normalized = re.sub(r"\s+", " ", desc)
    assert REQUIRED_NEGATIVE_SCOPE in normalized, (
        "SKILL.md description is missing the negative-scope sentence. "
        "Phase 2 ablation added it to reduce false positives on adjacent "
        "analytics topics (baseline T-032, T-037)."
    )


# ---------------------------------------------------------------------------
# Golden-prompts structural integrity
# ---------------------------------------------------------------------------


def test_routing_test_set_has_expected_prompt_count(routing_test_set: str) -> None:
    ids = _ids_in_headings(routing_test_set)
    assert len(ids) == 45, (
        f"routing_test_set.md has {len(ids)} prompts, expected 45. "
        f"If prompts were added/removed, update baseline_results.md and "
        f"this assertion together."
    )


def test_baseline_results_match_test_set(
    routing_test_set: str, baseline_results: str
) -> None:
    test_ids = _ids_in_headings(routing_test_set)
    result_ids = _ids_in_result_rows(baseline_results)
    missing = test_ids - result_ids
    extra = result_ids - test_ids
    assert not missing and not extra, (
        f"baseline_results.md drift: missing={sorted(missing)}, "
        f"extra={sorted(extra)}"
    )


def test_routing_decision_references_skill_md(routing_decision: str) -> None:
    """Decision doc must point at the canonical skill path, not a stale one."""
    assert "skill/SKILL.md" in routing_decision
    assert "dossier-plugin/" not in routing_decision, (
        "routing_decision.md still references the archived dossier-plugin path"
    )
