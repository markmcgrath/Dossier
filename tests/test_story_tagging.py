"""
Contract tests for the interview-story-tagging procedure.

Ensures `skill/references/story-tagging.md` exists, is referenced from
SKILL.md / file-conventions / Mode 3, and encodes the required design
decisions (tag-overlap matching, top 3–4 selection, heading wikilinks,
approval-gated back-references into stories.md).
"""

from __future__ import annotations

from pathlib import Path

import pytest


STORY_TAGGING_REL = "skill/references/story-tagging.md"


@pytest.fixture(scope="session")
def story_tagging_text(vault_path: Path) -> str:
    path = vault_path / STORY_TAGGING_REL
    assert path.is_file(), f"story-tagging reference missing at {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Content of story-tagging.md
# ---------------------------------------------------------------------------


def test_story_tagging_defines_forward_link(story_tagging_text: str) -> None:
    assert "related_stories:" in story_tagging_text, (
        "story-tagging.md must name the `related_stories:` frontmatter field."
    )


def test_story_tagging_uses_heading_wikilinks(story_tagging_text: str) -> None:
    assert "[[stories#" in story_tagging_text, (
        "story-tagging.md must spec Obsidian heading wikilinks "
        "(`[[stories#Story Title]]`) since all stories live in a single file."
    )


def test_story_tagging_defines_back_reference_line(story_tagging_text: str) -> None:
    assert "**Used in:**" in story_tagging_text, (
        "story-tagging.md must name the `**Used in:**` back-reference line "
        "that is appended to matched stories in stories.md."
    )


def test_story_tagging_requires_approval_batch(story_tagging_text: str) -> None:
    lower = story_tagging_text.lower()
    assert "approval" in lower and "batch" in lower, (
        "story-tagging.md must require that back-reference writes run as a "
        "single user-approved batch, not silently."
    )


def test_story_tagging_specifies_top_matches(story_tagging_text: str) -> None:
    assert "top 3" in story_tagging_text.lower() or "3–4" in story_tagging_text, (
        "story-tagging.md must cap matches at top 3–4 per prep."
    )


def test_story_tagging_protects_user_layer(story_tagging_text: str) -> None:
    lower = story_tagging_text.lower()
    assert "user-layer" in lower or "user layer" in lower, (
        "story-tagging.md must state that stories.md is user-layer and only "
        "the `**Used in:**` line is a sanctioned mutation."
    )


def test_story_tagging_handles_zero_match(story_tagging_text: str) -> None:
    lower = story_tagging_text.lower()
    assert "no strongly matching" in lower or "zero-match" in lower, (
        "story-tagging.md must specify behavior when no stories match "
        "(warn-and-suggest-adding)."
    )


# ---------------------------------------------------------------------------
# Cross-references
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel_path",
    [
        "skill/SKILL.md",
        "skill/references/file-conventions.md",
    ],
)
def test_skill_points_at_story_tagging(vault_path: Path, rel_path: str) -> None:
    text = (vault_path / rel_path).read_text(encoding="utf-8")
    assert "story-tagging.md" in text, (
        f"{rel_path} must reference story-tagging.md so readers find the "
        f"matching and back-reference procedure."
    )


def test_file_conventions_lists_related_stories(vault_path: Path) -> None:
    text = (vault_path / "skill/references/file-conventions.md").read_text(
        encoding="utf-8"
    )
    assert "related_stories:" in text, (
        "file-conventions.md must list `related_stories:` as part of the prep "
        "frontmatter schema."
    )


# ---------------------------------------------------------------------------
# Example conformance
# ---------------------------------------------------------------------------


def test_example_prep_has_related_stories(example_prep_frontmatter: dict) -> None:
    """examples/example-prep.md must model the new related_stories convention."""
    assert "related_stories" in example_prep_frontmatter, (
        "example-prep.md frontmatter must include `related_stories:` so it "
        "models the new convention."
    )
    stories = example_prep_frontmatter["related_stories"]
    assert isinstance(stories, list) and stories, (
        "`related_stories:` must be a non-empty YAML list."
    )
    for entry in stories:
        assert isinstance(entry, str) and entry.startswith("[[stories#"), (
            f"Each related_stories entry must be an Obsidian heading wikilink, "
            f"got {entry!r}."
        )
