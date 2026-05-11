"""
Contract tests for the terminal archival procedure.

Ensures `skill/references/terminal-archival.md` exists, is pointed to
from every skill location that touches terminal statuses or archival,
and encodes the required design decisions (terminal statuses, versioned
folders, silent wikilink rewrite).
"""

from __future__ import annotations

from pathlib import Path

import pytest


ARCHIVAL_REL = "skill/references/terminal-archival.md"

TERMINAL_STATUSES = ["Rejected", "Passed", "Offer-Declined"]


@pytest.fixture(scope="session")
def archival_text(vault_path: Path) -> str:
    path = vault_path / ARCHIVAL_REL
    assert path.is_file(), f"terminal archival reference missing at {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Content of terminal-archival.md
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", TERMINAL_STATUSES)
def test_archival_covers_terminal_status(archival_text: str, status: str) -> None:
    assert status in archival_text, (
        f"terminal-archival.md must name {status!r} as a trigger status."
    )


def test_archival_specifies_bundle_scope(archival_text: str) -> None:
    for folder in ("evals/", "outreach/", "cover-letters/", "interview-prep/"):
        assert folder in archival_text, (
            f"terminal-archival.md must list {folder} as in-scope for the "
            f"company bundle."
        )


def test_archival_specifies_versioning_rule(archival_text: str) -> None:
    """Repeat archivals must produce versioned folders, not merged ones."""
    assert "-v2" in archival_text, (
        "terminal-archival.md must specify the versioning rule for repeat "
        "archivals (archive/[slug]-v2/, -v3/, ...)."
    )


def test_archival_specifies_wikilink_rewrite(archival_text: str) -> None:
    assert "wikilink" in archival_text.lower(), (
        "terminal-archival.md must cover silent cross-reference rewriting "
        "of path-style references to wikilink form."
    )


def test_archival_defers_cold_detection(archival_text: str) -> None:
    assert "90" in archival_text or "cold" in archival_text.lower(), (
        "terminal-archival.md must acknowledge that 90+ days cold detection "
        "is deferred (not automated)."
    )


def test_no_cold_detection_implementation_symbols(vault_path: Path) -> None:
    """Regression: the deferred cold-detection feature must not be partially
    shipped while terminal-archival.md still describes it as manual.

    If someone implements automated cold detection, the implementation will
    introduce a symbol like cold_threshold_days, days_until_cold, or a
    similar config knob. This test fails loudly when any such symbol lands
    under skill/ before the manual-fallback language is removed — preventing
    the state where the code says "automated" and the docs say "manual."
    """
    impl_markers = [
        "cold_threshold_days",
        "days_until_cold",
        "stale_application_days",
        "auto_archive_cold",
    ]

    offenders: list[str] = []
    for md_file in (vault_path / "skill").rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        for marker in impl_markers:
            if marker in text:
                offenders.append(f"{md_file.relative_to(vault_path)}: {marker}")

    assert not offenders, (
        "Cold-detection implementation symbol(s) found in skill/. If "
        "automated cold detection has shipped, remove the manual-fallback "
        "language from terminal-archival.md and status-outcome-state-machine.md "
        "and update this test list to match the new design.\n  "
        + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Cross-references from the rest of the skill
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel_path",
    [
        "skill/SKILL.md",
        "skill/references/file-conventions.md",
        "skill/references/status-outcome-state-machine.md",
        "skill/references/mode9-inbox-followup.md",
    ],
)
def test_skill_points_at_archival_reference(vault_path: Path, rel_path: str) -> None:
    text = (vault_path / rel_path).read_text(encoding="utf-8")
    assert "terminal-archival.md" in text, (
        f"{rel_path} must reference terminal-archival.md so readers find the "
        f"authoritative archival procedure."
    )


# ---------------------------------------------------------------------------
# Regression: examples should use wikilink-style cross-references
# ---------------------------------------------------------------------------


def test_example_outreach_uses_wikilink_related_eval(vault_path: Path) -> None:
    """Path-style related_eval values break on archival; examples must model
    the wikilink convention so they don't mislead."""
    text = (vault_path / "examples" / "example-outreach.md").read_text(
        encoding="utf-8"
    )
    assert 'related_eval: "examples/' not in text, (
        "examples/example-outreach.md must not use path-style related_eval — "
        "use wikilink form [[example-eval]]."
    )
    assert "[[example-eval]]" in text
