"""
tests/test_routing_evals_scoring.py — Pure scoring tests with synthetic inputs.

No API calls are made. Tests import the score() function from the harness and
verify credit computation for all credit levels (0.0, 0.5, 1.0).

Authority: ~/.claude/plans/lucky-pondering-dragon.md (Plan 19 Stream B)
"""

import sys
from pathlib import Path

# Add .github/scripts to sys.path so we can import the harness.
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

from run_routing_evals import score  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _expected(trigger, mode=None):
    return {"would_trigger": trigger, "mode": mode}


def _got(trigger, mode=None):
    return {"would_trigger_dossier": trigger, "mode": mode}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_full_match_trigger_and_mode():
    """Trigger agrees and primary mode agrees → 1.0 credit."""
    assert score(
        _expected(True, "Mode 1"),
        _got(True, "Mode 1"),
    ) == 1.0


def test_trigger_match_mode_mismatch():
    """Trigger agrees but mode disagrees → 0.5 credit."""
    assert score(
        _expected(True, "Mode 1"),
        _got(True, "Mode 5"),
    ) == 0.5


def test_trigger_disagrees_got_false():
    """Expected trigger=True, got trigger=False → 0.0 credit."""
    assert score(
        _expected(True, "Mode 1"),
        _got(False, None),
    ) == 0.0


def test_negative_full_match():
    """Both expected and got trigger=False → 1.0 credit."""
    assert score(
        _expected(False, None),
        _got(False, None),
    ) == 1.0


def test_negative_trigger_disagrees():
    """Expected trigger=False, got trigger=True → 0.0 credit."""
    assert score(
        _expected(False, None),
        _got(True, "Mode 1"),
    ) == 0.0


def test_trigger_only_required_any_mode_accepted():
    """
    T-038 case: expected mode=None with trigger=True.
    Any mode (or null mode) from the model counts as full credit when
    expected mode is None, because only trigger agreement is required.
    """
    assert score(
        _expected(True, None),   # trigger-only required (no specific mode)
        _got(True, "Mode 5"),
    ) == 1.0


def test_trigger_only_required_null_mode_accepted():
    """T-038 variant: model returns trigger=True, mode=null → still 1.0."""
    assert score(
        _expected(True, None),
        _got(True, None),
    ) == 1.0


def test_mode_normalization_whitespace():
    """Mode strings with extra whitespace still match."""
    # score uses _normalize_mode internally
    assert score(
        _expected(True, "Mode 1"),
        _got(True, "mode  1"),
    ) == 1.0


def test_mode_case_insensitive():
    """Mode comparison is case-insensitive via title-case normalization."""
    assert score(
        _expected(True, "Mode 2"),
        _got(True, "MODE 2"),
    ) == 1.0
