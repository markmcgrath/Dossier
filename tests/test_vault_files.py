"""
Tests for required files and folder structure in the vault.
"""
import pytest


def test_required_root_files_exist(vault_path):
    """Verify all required vault files exist.

    In the public repo, personal files are replaced by templates:
    cv.md -> cv.template.md, profile.md -> profile.template.md, etc.
    """
    required_files = [
        "dashboard.md",
        "README.md",
        "PRIVACY.md",
        "DATA_CONTRACT.md",
        "LICENSE",
    ]
    template_pairs = [
        ("cv.md", "cv.template.md"),
        ("profile.md", "profile.template.md"),
        ("config.md", "config.template.md"),
        ("stories.md", "stories.template.md"),
    ]

    missing = []
    for fname in required_files:
        if not (vault_path / fname).exists():
            missing.append(fname)

    for primary, template in template_pairs:
        if not (vault_path / primary).exists() and not (vault_path / template).exists():
            missing.append(f"{primary} (or {template})")

    if missing:
        assert False, f"Missing required files: {', '.join(missing)}"


def test_required_directories_exist(vault_path):
    """Verify all required vault directories exist."""
    required_dirs = [
        "evals",
        "outreach",
        "cover-letters",
        "interview-prep",
        "research",
        "daily",
        "weekly",
        "archive",
        "examples",
    ]
    missing = [d for d in required_dirs if not (vault_path / d).exists()]
    if missing:
        assert False, f"Missing required directories: {', '.join(missing)}"


def test_examples_directory_has_three_files(vault_path):
    """Verify examples/ directory has at least three reference files."""
    examples_dir = vault_path / "examples"
    assert examples_dir.exists(), "examples/ directory not found"

    files = list(examples_dir.glob("*.md"))
    assert len(files) >= 3, f"examples/ has {len(files)} files, expected at least 3"

    file_names = {f.name for f in files}
    expected = {"example-eval.md", "example-outreach.md", "example-prep.md"}
    for fname in expected:
        assert fname in file_names, f"examples/{fname} not found"


def test_example_eval_frontmatter(example_eval_frontmatter):
    """Verify example-eval.md has required frontmatter fields."""
    required = {"type", "grade", "legitimacy", "outcome", "model", "sources"}
    missing = required - set(example_eval_frontmatter.keys() or {})
    if missing:
        assert False, f"example-eval.md missing fields: {missing}"
    assert example_eval_frontmatter.get("type") == "eval", "example-eval.md must have type: eval"


def test_example_outreach_frontmatter(example_outreach_frontmatter):
    """Verify example-outreach.md has required frontmatter fields."""
    required = {"type", "channel", "status"}
    missing = required - set(example_outreach_frontmatter.keys() or {})
    if missing:
        assert False, f"example-outreach.md missing fields: {missing}"
    assert example_outreach_frontmatter.get("type") == "outreach", "example-outreach.md must have type: outreach"


def test_example_prep_frontmatter(example_prep_frontmatter):
    """Verify example-prep.md has required frontmatter fields."""
    required = {"type", "status"}
    missing = required - set(example_prep_frontmatter.keys() or {})
    if missing:
        assert False, f"example-prep.md missing fields: {missing}"
    assert example_prep_frontmatter.get("type") == "prep", "example-prep.md must have type: prep"


def test_config_has_notion_block(config_text):
    """Verify config has Notion configuration block."""
    assert "notion:" in config_text, "config missing 'notion:' block"
    assert "enabled:" in config_text, "config missing 'enabled:' key"


def test_config_preserves_notion_ids(config_text):
    """Verify config contains Notion data source ID and tracker URL placeholders."""
    assert "data_source_id:" in config_text, "config missing 'data_source_id:'"
    assert "tracker_url:" in config_text, "config missing 'tracker_url:'"


def test_dashboard_has_legitimacy_column(vault_path):
    """Verify dashboard.md includes legitimacy column in queries."""
    dashboard_text = (vault_path / "dashboard.md").read_text(encoding="utf-8")
    assert "legitimacy" in dashboard_text.lower(), "dashboard.md missing legitimacy field in Dataview queries"


def test_dashboard_has_offers_pending_query(vault_path):
    """Verify dashboard.md has a query filtering for Offer status."""
    dashboard_text = (vault_path / "dashboard.md").read_text(encoding="utf-8")
    assert "Offer" in dashboard_text, "dashboard.md missing Offer status filter"


def test_privacy_md_covers_seven_services(vault_path):
    """Verify PRIVACY.md mentions the seven required services."""
    privacy_text = (vault_path / "PRIVACY.md").read_text(encoding="utf-8")
    services = ["Anthropic", "Gmail", "Calendar", "Apollo", "LinkedIn", "Notion", "Indeed"]
    for service in services:
        assert service in privacy_text, f"PRIVACY.md doesn't mention {service}"


def test_data_contract_has_three_layers(vault_path):
    """Verify DATA_CONTRACT.md documents three data layers."""
    data_contract_text = (vault_path / "DATA_CONTRACT.md").read_text(encoding="utf-8")
    layers = ["User Layer", "System Layer", "Derived"]
    for layer in layers:
        assert layer in data_contract_text, f"DATA_CONTRACT.md missing '{layer}' section"


def test_license_is_mit(vault_path):
    """Verify LICENSE file contains MIT license text."""
    license_text = (vault_path / "LICENSE").read_text(encoding="utf-8")
    assert "MIT" in license_text, "LICENSE doesn't mention MIT"


def test_readme_has_governance_section(vault_path):
    """Verify README.md has Governance section."""
    readme_text = (vault_path / "README.md").read_text(encoding="utf-8")
    assert "Governance" in readme_text, "README.md missing Governance section"
    assert "PRIVACY" in readme_text or "privacy" in readme_text.lower(), "README.md Governance section missing PRIVACY reference"


def test_readme_has_retention_section(vault_path):
    """Verify README.md has Data Retention section."""
    readme_text = (vault_path / "README.md").read_text(encoding="utf-8")
    assert "Retention" in readme_text or "retention" in readme_text.lower(), "README.md missing Data Retention section"


def test_readme_references_governance_docs(vault_path):
    """Verify README.md links to the core governance documents."""
    readme_text = (vault_path / "README.md").read_text(encoding="utf-8")
    for doc in ("PRIVACY.md", "DATA_CONTRACT.md", "SECURITY.md"):
        assert doc in readme_text, f"README.md missing reference to {doc}"


def test_readme_covers_archival(vault_path):
    """Verify README.md explains the archival model."""
    readme_text = (vault_path / "README.md").read_text(encoding="utf-8").lower()
    assert "archive" in readme_text or "archival" in readme_text, "README.md missing archival/archive explanation"


def test_stories_template_has_star_format(vault_path):
    """Verify stories template includes STAR+R format guidance."""
    stories_file = vault_path / "stories.md"
    if not stories_file.exists():
        stories_file = vault_path / "stories.template.md"
    if not stories_file.exists():
        pytest.skip("Neither stories.md nor stories.template.md found")
    stories_text = stories_file.read_text(encoding="utf-8")
    star_elements = ["Situation", "Task", "Action", "Result", "Reflection"]
    for element in star_elements:
        assert element in stories_text, f"stories file missing STAR+R element: {element}"
