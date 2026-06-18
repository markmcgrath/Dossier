"""
Tests for ZIP package integrity of dossier.skill.
"""
import zipfile

import pytest


def test_skill_zip_exists(vault_path):
    """Verify dossier.skill file exists."""
    skill_path = vault_path / "dossier.skill"
    assert skill_path.exists(), "dossier.skill not found in vault root"
    assert skill_path.is_file(), "dossier.skill is not a file"


def test_skill_zip_is_valid(skill_zip):
    """Verify dossier.skill is a valid ZIP archive."""
    try:
        # Test reads to ensure ZIP is valid
        skill_zip.testzip()
        # If testzip returns None, all files are valid
    except zipfile.BadZipFile as e:
        pytest.fail(f"dossier.skill is not a valid ZIP file: {e}")


def test_skill_zip_contains_required_files(skill_zip):
    """Verify ZIP contains SKILL.md and scoring-guide.md.

    Both files may be at the archive root or nested under a `skill/` prefix,
    with scoring-guide.md additionally allowed under `references/`.
    """
    files = skill_zip.namelist()
    has_skill_md = "SKILL.md" in files or "skill/SKILL.md" in files
    assert has_skill_md, f"SKILL.md not found in ZIP (entries: {files})"
    has_scoring_guide = any(
        candidate in files
        for candidate in (
            "scoring-guide.md",
            "references/scoring-guide.md",
            "skill/references/scoring-guide.md",
        )
    )
    assert has_scoring_guide, f"scoring-guide.md not found in ZIP (entries: {files})"


def test_skill_md_line_count_is_reasonable(skill_lines):
    """Verify SKILL.md has a reasonable line count (300–2000).

    The lower bound guards against accidental truncation or a broken repack.
    The upper bound is 2000 (reference files absorb most mode detail).
    Update the bounds if the skill is intentionally expanded or contracted.
    """
    line_count = len(skill_lines)
    assert (
        300 <= line_count <= 2000
    ), f"SKILL.md has {line_count} lines; expected 300–2000"


def test_scoring_guide_is_present_and_nonempty(scoring_guide):
    """Verify scoring-guide.md exists and is not empty."""
    assert scoring_guide, "scoring-guide.md is empty"
    assert len(scoring_guide) > 100, "scoring-guide.md is suspiciously small"


def test_manifest_present(skill_zip):
    """Verify skill/manifest.json is present in dossier.skill."""
    assert "skill/manifest.json" in skill_zip.namelist(), (
        "skill/manifest.json not found in dossier.skill"
    )


def test_manifest_shape(manifest):
    """Verify manifest.json has the expected shape and field values."""
    import re

    assert manifest.get("name") == "dossier", (
        f"manifest name must be 'dossier'; got {manifest.get('name')!r}"
    )
    assert manifest.get("version"), "manifest version must be non-empty"
    built_at_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    assert re.match(built_at_pattern, manifest.get("built_at", "")), (
        f"manifest built_at {manifest.get('built_at')!r} does not match "
        f"{built_at_pattern}"
    )
    commit = manifest.get("commit", "")
    is_40_hex = bool(re.match(r"^[0-9a-f]{40}$", commit))
    is_unknown = commit == "unknown"
    assert is_40_hex or is_unknown, (
        f"manifest commit must be a 40-char hex SHA or 'unknown'; got {commit!r}"
    )


def test_zip_has_no_unexpected_top_level_entries(skill_zip):
    """Verify the ZIP contains exactly the expected 21 entries.

    Adding a new reference file requires a deliberate update to this list.
    Removing or renaming an entry also requires an update — the test is
    intentionally a frozen golden list so changes are auditable.
    """
    EXPECTED_BUNDLE_ENTRIES = [
        "skill/SKILL.md",
        "skill/manifest.json",
        "skill/references/SEND_READY_CONTRACT.md",
        "skill/references/file-conventions.md",
        "skill/references/mode1-offer-evaluator.md",
        "skill/references/mode10-calendar-ops.md",
        "skill/references/mode11-tailored-cv.md",
        "skill/references/mode12-batch-pipeline.md",
        "skill/references/mode13-calibration.md",
        "skill/references/mode14-packet-assembly.md",
        "skill/references/mode15-target-radar.md",
        "skill/references/mode2-portal-scan.md",
        "skill/references/mode5-outreach.md",
        "skill/references/mode7-salary-negotiation.md",
        "skill/references/mode9-inbox-followup.md",
        "skill/references/scoring-guide.md",
        "skill/references/send_ready_config.json",
        "skill/references/status-outcome-state-machine.md",
        "skill/references/story-tagging.md",
        "skill/references/terminal-archival.md",
        "skill/references/weekly-trend-report.md",
    ]
    actual = sorted(skill_zip.namelist())
    expected = sorted(EXPECTED_BUNDLE_ENTRIES)
    assert actual == expected, (
        f"ZIP entries do not match expected frozen list.\n"
        f"  Extra:   {sorted(set(actual) - set(expected))}\n"
        f"  Missing: {sorted(set(expected) - set(actual))}"
    )
