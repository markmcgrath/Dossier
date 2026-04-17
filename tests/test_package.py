"""
Tests for ZIP package integrity of dossier.skill.
"""
import zipfile


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

    scoring-guide.md may be at root or in references/ subfolder.
    """
    files = skill_zip.namelist()
    assert "SKILL.md" in files, "SKILL.md not found in ZIP"
    has_scoring_guide = (
        "scoring-guide.md" in files
        or "references/scoring-guide.md" in files
    )
    assert has_scoring_guide, f"scoring-guide.md not found in ZIP (entries: {files})"


def test_skill_md_line_count_is_reasonable(skill_lines):
    """Verify SKILL.md has a reasonable line count (500–2000).

    The lower bound is 500 (current v1 release is ~765 lines).
    The upper bound is 2000 (planned Mode 12/13 additions will grow it).
    Update the bounds if the skill is intentionally expanded or contracted.
    """
    line_count = len(skill_lines)
    assert (
        500 <= line_count <= 2000
    ), f"SKILL.md has {line_count} lines; expected 500–2000"


def test_scoring_guide_is_present_and_nonempty(scoring_guide):
    """Verify scoring-guide.md exists and is not empty."""
    assert scoring_guide, "scoring-guide.md is empty"
    assert len(scoring_guide) > 100, "scoring-guide.md is suspiciously small"
