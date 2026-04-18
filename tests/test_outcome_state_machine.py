"""
Contract tests for the status/outcome state machine.

Ensures the transition table at
`skill/references/status-outcome-state-machine.md` is well-formed and
that the places in the skill that write (status, outcome) all reference
it. Also asserts every example eval's (status, outcome) pair appears as
a valid row in the table.
"""

from __future__ import annotations

from pathlib import Path

import pytest


STATE_MACHINE_REL = "skill/references/status-outcome-state-machine.md"

# Pairs that must appear in the transition table. If any of these is
# missing, the state machine no longer covers a required pipeline event
# — the skill would be under-specified and the Mode 0 health check
# would not know how to validate it.
REQUIRED_PAIRS = {
    ("Evaluating", "Pending"),
    ("Applied", "Pending"),
    ("Interviewing", "Phone Screen"),
    ("Interviewing", "Interview"),
    ("Rejected", "Rejected"),
    ("Offer", "Offer"),
    ("Offer", "Accepted"),
    ("Passed", "Withdrawn"),
}


@pytest.fixture(scope="session")
def state_machine_text(vault_path: Path) -> str:
    path = vault_path / STATE_MACHINE_REL
    assert path.is_file(), f"state machine reference missing at {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def transition_pairs(state_machine_text: str) -> set[tuple[str, str]]:
    """Parse the markdown table and return the set of (status, outcome) pairs."""
    pairs: set[tuple[str, str]] = set()
    in_table = False
    for line in state_machine_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Trigger "):
            in_table = True
            continue
        if in_table:
            if not stripped.startswith("|"):
                break
            if set(stripped) <= set("|-: "):
                continue  # separator row
            cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]
            if len(cells) >= 3:
                pairs.add((cells[1], cells[2]))
    return pairs


@pytest.fixture(scope="session")
def example_eval_status_outcome(example_eval_frontmatter: dict) -> tuple[str, str]:
    return (example_eval_frontmatter["status"], example_eval_frontmatter["outcome"])


# ---------------------------------------------------------------------------
# Table shape
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("pair", sorted(REQUIRED_PAIRS))
def test_transition_table_covers_required_pair(
    transition_pairs: set[tuple[str, str]], pair: tuple[str, str]
) -> None:
    assert pair in transition_pairs, (
        f"state-machine transition table missing required pair {pair}. "
        f"Every row in SKILL.md's status/outcome value lists must have a "
        f"corresponding trigger in the table."
    )


def test_transition_table_is_nonempty(transition_pairs: set[tuple[str, str]]) -> None:
    assert len(transition_pairs) >= len(REQUIRED_PAIRS), (
        f"transition table parsed only {len(transition_pairs)} pairs; "
        f"expected at least {len(REQUIRED_PAIRS)}."
    )


# ---------------------------------------------------------------------------
# Skill references the state machine in the right places
# ---------------------------------------------------------------------------


def test_skill_md_references_state_machine(skill_md_source: str) -> None:
    assert "references/status-outcome-state-machine.md" in skill_md_source, (
        "SKILL.md must point at references/status-outcome-state-machine.md "
        "so readers know where transition rules live."
    )


def test_mode1_references_state_machine(vault_path: Path) -> None:
    text = (vault_path / "skill/references/mode1-offer-evaluator.md").read_text(
        encoding="utf-8"
    )
    assert "status-outcome-state-machine.md" in text, (
        "mode1-offer-evaluator.md must reference the state machine since "
        "Mode 1 sets the initial (status, outcome) pair."
    )


def test_mode9_references_state_machine(vault_path: Path) -> None:
    text = (vault_path / "skill/references/mode9-inbox-followup.md").read_text(
        encoding="utf-8"
    )
    assert "status-outcome-state-machine.md" in text, (
        "mode9-inbox-followup.md must reference the state machine since "
        "Application Status Sync drives most transitions."
    )


def test_mode0_health_check_validates_state_machine(skill_md_source: str) -> None:
    assert "Status/outcome consistency" in skill_md_source, (
        "Mode 0 health check must include a 'Status/outcome consistency' "
        "step that validates eval frontmatter against the state machine."
    )


# ---------------------------------------------------------------------------
# Example eval matches the machine
# ---------------------------------------------------------------------------


def test_example_eval_is_valid_transition(
    example_eval_status_outcome: tuple[str, str],
    transition_pairs: set[tuple[str, str]],
) -> None:
    assert example_eval_status_outcome in transition_pairs, (
        f"examples/example-eval.md has {example_eval_status_outcome} which "
        f"is not a row in the state machine. Either fix the example or add "
        f"a row to the transition table."
    )
