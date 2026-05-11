"""
Light syntactic checks on dashboard.md's Dataview code blocks.

Dataview is a community Obsidian plugin; it does not surface DQL parse
errors as test-friendly exit codes. A broken query just renders as an
empty table — silently — so a typo can ship to users unnoticed.

These tests don't parse DQL. They catch the cheap kinds of brokenness:

- A `dataview` fence that's missing its closing ``` (so the rest of the
  file is treated as code).
- Unbalanced parens in WHERE clauses — usually a sign of an editor
  half-finished an edit.
- A code block tagged ```dataview that contains no FROM clause — every
  real DQL query reads from at least one folder.

If a future regression introduces a different class of breakage, add a
new assertion here rather than expanding any single one — keep each
check narrow and named so failures are easy to diagnose.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def dashboard_text(vault_path: Path) -> str:
    path = vault_path / "dashboard.md"
    assert path.is_file(), f"dashboard.md not found at {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def dataview_blocks(dashboard_text: str) -> list[str]:
    """Extract the body of every ```dataview fenced block."""
    # Match ```dataview ... ``` (non-greedy across newlines).
    pattern = re.compile(r"```dataview\s*\n(.*?)```", re.DOTALL)
    return pattern.findall(dashboard_text)


def test_dashboard_has_dataview_blocks(dataview_blocks: list[str]) -> None:
    """Sanity: the dashboard is supposed to be queries, so there should be some."""
    assert len(dataview_blocks) > 0, (
        "dashboard.md contains no ```dataview blocks. If queries were removed "
        "intentionally, also remove this whole test file."
    )


def test_every_dataview_fence_is_closed(dashboard_text: str) -> None:
    """A ```dataview fence without a closing ``` corrupts the rest of the file.

    The simplest check: the count of ```dataview openings must equal the
    count of all ``` markers minus the openings (i.e. closings).
    """
    openings = len(re.findall(r"```dataview\s*\n", dashboard_text))
    all_fences = dashboard_text.count("```")
    # Every dataview block needs both an opening and a closing fence.
    # `all_fences` may also include non-dataview fenced blocks; those
    # contribute equal opens and closes, so the parity check still holds.
    assert all_fences % 2 == 0, (
        f"dashboard.md has an odd number of ``` markers ({all_fences}); "
        f"at least one code fence is unclosed. Found {openings} ```dataview "
        f"opening fence(s)."
    )


def test_every_dataview_block_has_balanced_parens(dataview_blocks: list[str]) -> None:
    """Every ```dataview block must have balanced parentheses.

    Unbalanced parens nearly always mean an editor half-finished an edit;
    Dataview silently renders an empty table instead of erroring. All
    offenders collected into a single message for diagnose-once UX.
    """
    offenders: list[str] = []
    for idx, body in enumerate(dataview_blocks):
        opens = body.count("(")
        closes = body.count(")")
        if opens != closes:
            offenders.append(
                f"  block #{idx}: {opens} '(' vs {closes} ')'\n"
                f"    body (first 200 chars): {body[:200]!r}"
            )
    assert not offenders, "Unbalanced parens in dataview blocks:\n" + "\n".join(offenders)


def test_every_dataview_block_has_from_clause(dataview_blocks: list[str]) -> None:
    """Every ```dataview block must read FROM at least one folder.

    A query without FROM either reads the whole vault (slow) or, more
    likely, is a typo that fails silently. TASK / LIST / TABLE all accept
    FROM, so this check applies uniformly.
    """
    offenders: list[str] = []
    for idx, body in enumerate(dataview_blocks):
        upper = body.upper()
        if "FROM " not in upper and "FROM\n" not in upper:
            offenders.append(f"  block #{idx} (first 200 chars): {body[:200]!r}")
    assert not offenders, "Dataview blocks with no FROM clause:\n" + "\n".join(offenders)
