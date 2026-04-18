"""
Tests for required files and folder structure in the vault.
"""

import pytest


VAULT_TEMPLATE_FOLDERS = [
    "evals",
    "outreach",
    "cover-letters",
    "interview-prep",
    "research",
    "daily",
    "weekly",
    "archive",
]


def test_vault_template_has_readme(vault_path):
    """vault-template/ must carry a README documenting how to use the skeleton."""
    readme = vault_path / "vault-template" / "README.md"
    assert readme.is_file(), (
        "vault-template/README.md missing — START_HERE.md points at "
        "vault-template/ as the starter skeleton."
    )


@pytest.mark.parametrize("folder", VAULT_TEMPLATE_FOLDERS)
def test_vault_template_has_folder(vault_path, folder):
    """Each expected artifact folder must exist in the skeleton."""
    d = vault_path / "vault-template" / folder
    assert d.is_dir(), f"vault-template/{folder}/ missing from starter skeleton."


def test_required_files_exist(vault_path):
    """Verify all required vault files exist.

    In the public repo, personal files (cv.md, profile.md, stories.md) are not
    shipped — only templates are. config.md is also excluded; config.template.md
    ships instead. These are checked separately below.
    """
    # Files that must be present in both private vault and public repo
    required_files = [
        "dashboard.md",
        "README.md",
        "PRIVACY.md",
        "DATA_CONTRACT.md",
        "LICENSE",
    ]
    missing = []
    for fname in required_files:
        fpath = vault_path / fname
        if not fpath.exists():
            missing.append(fname)

    if missing:
        msg = f"Missing required files: {', '.join(missing)}"
        assert False, msg

    # In the public repo, personal files ship as templates
    template_pairs = [
        ("cv.md", "cv.template.md"),
        ("profile.md", "profile.template.md"),
        ("config.md", "config.template.md"),
        ("stories.md", "stories.template.md"),
    ]
    for real_file, template_file in template_pairs:
        real_exists = (vault_path / real_file).exists()
        template_exists = (vault_path / template_file).exists()
        assert real_exists or template_exists, (
            f"Neither {real_file} nor {template_file} found — at least one must exist"
        )


def test_examples_directory_has_three_files(vault_path):
    """Verify examples/ directory has exactly three reference files."""
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
        msg = f"example-eval.md missing fields: {missing}"
        assert False, msg

    # Verify type is "eval"
    assert (
        example_eval_frontmatter.get("type") == "eval"
    ), "example-eval.md must have type: eval"


def test_example_outreach_frontmatter(example_outreach_frontmatter):
    """Verify example-outreach.md has required frontmatter fields."""
    required = {"type", "channel", "status"}
    missing = required - set(example_outreach_frontmatter.keys() or {})

    if missing:
        msg = f"example-outreach.md missing fields: {missing}"
        assert False, msg

    # Verify type is "outreach"
    assert (
        example_outreach_frontmatter.get("type") == "outreach"
    ), "example-outreach.md must have type: outreach"


def test_example_prep_frontmatter(example_prep_frontmatter):
    """Verify example-prep.md has required frontmatter fields."""
    required = {"type", "status"}
    missing = required - set(example_prep_frontmatter.keys() or {})

    if missing:
        msg = f"example-prep.md missing fields: {missing}"
        assert False, msg

    # Verify type is "prep"
    assert (
        example_prep_frontmatter.get("type") == "prep"
    ), "example-prep.md must have type: prep"


def test_config_has_notion_block(config_text):
    """Verify config.md has Notion configuration block."""
    assert "notion:" in config_text, "config.md missing 'notion:' block"
    assert "enabled:" in config_text, "config.md missing 'enabled:' key"


def test_config_preserves_notion_ids(config_text):
    """Verify config.md contains Notion data source ID and tracker URL."""
    assert "data_source_id:" in config_text, "config.md missing 'data_source_id:'"
    assert "tracker_url:" in config_text, "config.md missing 'tracker_url:'"


def test_dashboard_has_legitimacy_column(vault_path):
    """Verify dashboard.md includes legitimacy column in queries."""
    dashboard_text = (vault_path / "dashboard.md").read_text(encoding="utf-8")
    assert "legitimacy" in dashboard_text.lower(), (
        "dashboard.md missing legitimacy field in Dataview queries"
    )


def test_dashboard_has_offers_pending_query(vault_path):
    """Verify dashboard.md has a query filtering for Offer status."""
    dashboard_text = (vault_path / "dashboard.md").read_text(encoding="utf-8")
    assert "Offer" in dashboard_text, "dashboard.md missing Offer status filter"


def test_privacy_md_covers_seven_services(vault_path):
    """Verify PRIVACY.md mentions the seven required services."""
    privacy_text = (vault_path / "PRIVACY.md").read_text(encoding="utf-8")
    services = [
        "Anthropic",
        "Gmail",
        "Calendar",
        "Apollo",
        "LinkedIn",
        "Notion",
        "Indeed",
    ]
    for service in services:
        assert service in privacy_text, f"PRIVACY.md doesn't mention {service}"


def test_data_contract_has_three_layers(vault_path):
    """Verify DATA_CONTRACT.md documents three data layers."""
    data_contract_text = (vault_path / "DATA_CONTRACT.md").read_text(encoding="utf-8")
    layers = ["User Layer", "System Layer", "Derived"]
    for layer in layers:
        assert layer in data_contract_text, (
            f"DATA_CONTRACT.md missing '{layer}' section"
        )


def test_license_is_mit(vault_path):
    """Verify LICENSE file contains MIT license text."""
    license_text = (vault_path / "LICENSE").read_text(encoding="utf-8")
    assert "MIT" in license_text, "LICENSE doesn't mention MIT"


def test_readme_references_governance_docs(vault_path):
    """Verify README.md links to the core governance documents.

    Guards against accidental removal of references to PRIVACY, DATA_CONTRACT,
    and SECURITY. Checks for content, not a specific section title.
    """
    readme_text = (vault_path / "README.md").read_text(encoding="utf-8")
    for doc in ("PRIVACY.md", "DATA_CONTRACT.md", "SECURITY.md"):
        assert doc in readme_text, f"README.md missing reference to {doc}"


def test_readme_covers_archival(vault_path):
    """Verify README.md explains the archival / retention model.

    The word 'archive' or 'archival' must appear; specific section titles
    may evolve (e.g., "Vault discipline" vs "Data retention"), but losing
    the concept entirely would be a regression.
    """
    readme_text = (vault_path / "README.md").read_text(encoding="utf-8").lower()
    assert "archive" in readme_text or "archival" in readme_text, (
        "README.md missing archive/archival content"
    )


def test_stories_md_has_star_template(vault_path):
    """Verify stories.md (or stories.template.md) includes STAR+R format guidance."""
    stories_file = vault_path / "stories.md"
    if not stories_file.exists():
        # Public repo ships stories.template.md instead of a real stories.md
        stories_file = vault_path / "stories.template.md"
    assert stories_file.exists(), "Neither stories.md nor stories.template.md found"
    stories_text = stories_file.read_text(encoding="utf-8")
    star_elements = ["Situation", "Task", "Action", "Result", "Reflection"]
    for element in star_elements:
        assert element in stories_text, (
            f"{stories_file.name} missing STAR+R element: {element}"
        )
