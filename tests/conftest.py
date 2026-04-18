"""
Shared pytest fixtures for Dossier test suite.
"""
import os
from pathlib import Path
import zipfile
import yaml
import pytest


@pytest.fixture(scope="session")
def vault_path():
    """Path to the Dossier vault root."""
    vault = os.environ.get("DOSSIER_VAULT")
    if vault:
        return Path(vault)
    # Default to the vault location
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def skill_zip(vault_path):
    """Opened ZipFile for dossier.skill."""
    skill_path = vault_path / "dossier.skill"
    assert skill_path.exists(), f"dossier.skill not found at {skill_path}"
    return zipfile.ZipFile(skill_path, "r")


@pytest.fixture(scope="session")
def skill_md(skill_zip):
    """Full text of SKILL.md as a string (root, skill/, or skill-update/ subfolder)."""
    names = skill_zip.namelist()
    for candidate in ("SKILL.md", "skill/SKILL.md", "skill-update/SKILL.md"):
        if candidate in names:
            return skill_zip.read(candidate).decode("utf-8")
    raise FileNotFoundError(
        f"SKILL.md not found in dossier.skill ZIP. Contents: {names}"
    )


@pytest.fixture(scope="session")
def skill_lines(skill_md):
    """SKILL.md as a list of lines."""
    return skill_md.split("\n")


@pytest.fixture(scope="session")
def scoring_guide(skill_zip):
    """Full text of scoring-guide.md (root, references/, or skill/references/ subfolder)."""
    names = skill_zip.namelist()
    for candidate in (
        "scoring-guide.md",
        "references/scoring-guide.md",
        "skill/references/scoring-guide.md",
        "skill-update/references/scoring-guide.md",
    ):
        if candidate in names:
            return skill_zip.read(candidate).decode("utf-8")
    raise FileNotFoundError(
        f"scoring-guide.md not found in dossier.skill ZIP. Contents: {names}"
    )


def parse_frontmatter(text):
    """
    Extract YAML frontmatter from markdown.
    Returns (frontmatter_dict, body_text) or (None, text) if no frontmatter.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text

    # Find closing ---
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            yaml_text = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :])
            try:
                fm = yaml.safe_load(yaml_text)
                return fm if isinstance(fm, dict) else None, body
            except yaml.YAMLError:
                return None, text
    return None, text


@pytest.fixture(scope="session")
def skill_md_source(vault_path):
    """Raw text of SKILL.md from the filesystem (not the ZIP).

    Some tests (routing golden, outcome state machine) need the on-disk
    version rather than the ZIP-packed copy so they can verify the
    description block and filesystem references independently.
    """
    skill_file = vault_path / "skill" / "SKILL.md"
    if not skill_file.exists():
        # Fall back to skill-update/ (private vault layout)
        skill_file = vault_path / "skill-update" / "SKILL.md"
    assert skill_file.exists(), (
        f"SKILL.md not found at {vault_path / 'skill' / 'SKILL.md'}"
    )
    return skill_file.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def example_prep_frontmatter(example_prep_text):
    """Parsed frontmatter of example-prep.md."""
    fm, _ = parse_frontmatter(example_prep_text)
    return fm


@pytest.fixture(scope="session")
def eval_files(vault_path):
    """List of parsed frontmatter dicts for all .md files in evals/."""
    evals_dir = vault_path / "evals"
    assert evals_dir.exists(), f"evals/ directory not found at {evals_dir}"

    files = []
    for md_file in sorted(evals_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        if fm:
            fm["__file__"] = md_file.name
            files.append(fm)
    return files


@pytest.fixture(scope="session")
def config_text(vault_path):
    """Raw text of config.md (or config.template.md in the public repo)."""
    config_file = vault_path / "config.md"
    if not config_file.exists():
        # Public repo ships config.template.md instead of a real config.md
        config_file = vault_path / "config.template.md"
    assert config_file.exists(), (
        f"Neither config.md nor config.template.md found at {vault_path}"
    )
    return config_file.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def example_eval_text(vault_path):
    """Raw text of examples/example-eval.md."""
    example_file = vault_path / "examples" / "example-eval.md"
    assert example_file.exists(), f"example-eval.md not found"
    return example_file.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def example_eval_frontmatter(example_eval_text):
    """Parsed frontmatter of example-eval.md."""
    fm, _ = parse_frontmatter(example_eval_text)
    return fm


@pytest.fixture(scope="session")
def example_outreach_text(vault_path):
    """Raw text of examples/example-outreach.md."""
    example_file = vault_path / "examples" / "example-outreach.md"
    assert example_file.exists(), f"example-outreach.md not found"
    return example_file.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def example_outreach_frontmatter(example_outreach_text):
    """Parsed frontmatter of example-outreach.md."""
    fm, _ = parse_frontmatter(example_outreach_text)
    return fm


@pytest.fixture(scope="session")
def example_prep_text(vault_path):
    """Raw text of examples/example-prep.md."""
    example_file = vault_path / "examples" / "example-prep.md"
    assert example_file.exists(), f"example-prep.md not found"
    return example_file.read_text(encoding="utf-8")
