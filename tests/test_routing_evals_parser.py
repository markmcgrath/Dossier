"""
tests/test_routing_evals_parser.py — Pure parsing tests for run_routing_evals.py.

No API calls are made. Tests import parse_test_set and parse_expected from the
harness and verify that the golden test set is parsed correctly.

Authority: ~/.claude/plans/lucky-pondering-dragon.md (Plan 19 Stream B)
"""

import sys
from pathlib import Path

# Add .github/scripts to sys.path so we can import the harness.
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

from run_routing_evals import parse_test_set, parse_expected  # noqa: E402

# Path to the real golden test set
TEST_SET_PATH = str(
    Path(__file__).parent / "golden_prompts" / "routing_test_set.md"
)


def _get_tuples():
    """Return the parsed tuples (cached once per test session via helper)."""
    return parse_test_set(TEST_SET_PATH)


# ---------------------------------------------------------------------------
# Test 1 — count
# ---------------------------------------------------------------------------

def test_parser_returns_45_tuples():
    """parse_test_set must return exactly 45 (test_id, prompt, expected) tuples."""
    tuples = _get_tuples()
    assert len(tuples) == 45, (
        f"Expected 45 tuples, got {len(tuples)}. "
        f"IDs found: {[t[0] for t in tuples]}"
    )


# ---------------------------------------------------------------------------
# Test 2 — T-001 prompt text
# ---------------------------------------------------------------------------

def test_t001_prompt_extracted():
    """T-001 prompt should contain text about Databricks / analytics engineer."""
    tuples = _get_tuples()
    t001 = next((t for t in tuples if t[0] == "T-001"), None)
    assert t001 is not None, "T-001 not found in parsed tuples"
    prompt_text = t001[1]
    # T-001 prompt contains "Evaluate this job description" and "Databricks"
    assert "Databricks" in prompt_text, (
        f"T-001 prompt does not contain 'Databricks'. Got: {prompt_text!r}"
    )
    assert "Evaluate" in prompt_text or "evaluate" in prompt_text, (
        f"T-001 prompt does not contain 'Evaluate'. Got: {prompt_text!r}"
    )


# ---------------------------------------------------------------------------
# Test 3 — T-031 expected is NONE
# ---------------------------------------------------------------------------

def test_t031_expected_is_none():
    """T-031 (generic coding task) must parse to would_trigger=False."""
    tuples = _get_tuples()
    t031 = next((t for t in tuples if t[0] == "T-031"), None)
    assert t031 is not None, "T-031 not found in parsed tuples"
    expected = parse_expected("T-031", t031[2])
    assert expected["would_trigger"] is False, (
        f"T-031 should parse to would_trigger=False. "
        f"expected_text={t031[2]!r}, parsed={expected}"
    )
    assert expected["mode"] is None, (
        f"T-031 should have mode=None. Got: {expected['mode']!r}"
    )


# ---------------------------------------------------------------------------
# Test 4 — T-038 expected is trigger=True (prompt injection)
# ---------------------------------------------------------------------------

def test_t038_expected_is_trigger_true():
    """T-038 (prompt injection) must parse to would_trigger=True per special case."""
    tuples = _get_tuples()
    t038 = next((t for t in tuples if t[0] == "T-038"), None)
    assert t038 is not None, "T-038 not found in parsed tuples"
    expected = parse_expected("T-038", t038[2])
    assert expected["would_trigger"] is True, (
        f"T-038 should parse to would_trigger=True (prompt injection special case). "
        f"expected_text={t038[2]!r}, parsed={expected}"
    )


# ---------------------------------------------------------------------------
# Test 5 — T-039 expected primary mode is Mode 1
# ---------------------------------------------------------------------------

def test_t039_expected_primary_mode():
    """T-039 (JD + outreach compound) expected primary mode must be Mode 1."""
    tuples = _get_tuples()
    t039 = next((t for t in tuples if t[0] == "T-039"), None)
    assert t039 is not None, "T-039 not found in parsed tuples"
    expected = parse_expected("T-039", t039[2])
    assert expected["would_trigger"] is True, (
        f"T-039 should trigger dossier. parsed={expected}"
    )
    # T-039 expected: "dossier → Mode 1 (eval) then Mode 5 (outreach draft)"
    # Primary mode is Mode 1 (first occurrence)
    assert expected["mode"] == "Mode 1", (
        f"T-039 primary mode should be 'Mode 1'. Got: {expected['mode']!r}. "
        f"expected_text={t039[2]!r}"
    )
