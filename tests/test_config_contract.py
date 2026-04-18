"""
Config-state permutation tests for Notion optionality.

Validates that SKILL.md and config.template.md describe consistent,
correct behavior across four config states:

  1. config.md missing entirely
  2. Notion explicitly disabled (enabled: false)
  3. Notion enabled but IDs missing/empty
  4. Notion enabled with valid IDs

These are text-contract assertions — no network calls, no runtime connectors.
"""
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "config"


@pytest.fixture
def config_notion_disabled():
    return (FIXTURE_DIR / "config_notion_disabled.md").read_text(encoding="utf-8")


@pytest.fixture
def config_notion_enabled_missing_ids():
    return (FIXTURE_DIR / "config_notion_enabled_missing_ids.md").read_text(encoding="utf-8")


@pytest.fixture
def config_notion_enabled_valid():
    return (FIXTURE_DIR / "config_notion_enabled_valid_sample.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_yaml_blocks(text):
    """Pull fenced YAML/code blocks from markdown."""
    blocks = []
    in_block = False
    current = []
    for line in text.split("\n"):
        if line.strip().startswith("```") and not in_block:
            in_block = True
            current = []
        elif line.strip().startswith("```") and in_block:
            blocks.append("\n".join(current))
            in_block = False
        elif in_block:
            current.append(line)
    return blocks


def _has_notion_enabled(text, value):
    """Check if any YAML block contains 'enabled: <value>'."""
    for block in _extract_yaml_blocks(text):
        if f"enabled: {value}" in block:
            return True
    return False


# ---------------------------------------------------------------------------
# State 1: config.md missing entirely
# ---------------------------------------------------------------------------

class TestConfigMissing:
    """When config.md is absent, SKILL.md must describe a vault-only path."""

    def test_skill_documents_missing_config_behavior(self, skill_md):
        """SKILL.md must say what to do when config.md is missing."""
        text_lower = skill_md.lower()
        assert any(phrase in text_lower for phrase in [
            "config.md` missing",
            "config.md missing",
            "`config.md` missing",
        ]), (
            "SKILL.md does not document behavior when config.md is missing. "
            "Expected a line like '`config.md` missing or `notion.enabled: false`: ...'"
        )

    def test_missing_config_means_vault_only(self, skill_md):
        """When config is missing, the documented behavior must be vault-only."""
        # Find the line that talks about config missing
        for line in skill_md.split("\n"):
            if "config.md" in line.lower() and "missing" in line.lower():
                line_lower = line.lower()
                assert any(w in line_lower for w in [
                    "vault only", "vault-only", "markdown-only", "markdown only",
                    "proceed", "saving all evals to the vault",
                ]), (
                    f"Config-missing line does not specify vault-only path: {line.strip()}"
                )
                return
        pytest.fail("Could not find config-missing documentation line in SKILL.md")


# ---------------------------------------------------------------------------
# State 2: Notion explicitly disabled
# ---------------------------------------------------------------------------

class TestConfigNotionDisabled:
    """When notion.enabled: false, behavior must match vault-only path."""

    def test_fixture_has_enabled_false(self, config_notion_disabled):
        assert _has_notion_enabled(config_notion_disabled, "false")

    def test_skill_documents_enabled_false(self, skill_md):
        """SKILL.md must explicitly mention the enabled: false path."""
        assert "notion.enabled: false" in skill_md.lower() or \
               "`notion.enabled: false`" in skill_md, (
            "SKILL.md does not mention the notion.enabled: false config state"
        )

    def test_disabled_means_no_reads_or_writes(self, skill_md):
        """The disabled path must say 'No Notion reads or writes' or equivalent."""
        text_lower = skill_md.lower()
        assert any(phrase in text_lower for phrase in [
            "no notion reads or writes",
            "operate entirely from the vault",
            "vault only",
        ]), (
            "SKILL.md does not state that Notion-disabled means no Notion I/O"
        )


# ---------------------------------------------------------------------------
# State 3: Notion enabled but IDs missing/empty
# ---------------------------------------------------------------------------

class TestConfigNotionEnabledMissingIDs:
    """When enabled: true but IDs are empty, Mode 0 should catch this."""

    def test_fixture_has_enabled_true(self, config_notion_enabled_missing_ids):
        assert _has_notion_enabled(config_notion_enabled_missing_ids, "true")

    def test_fixture_has_empty_ids(self, config_notion_enabled_missing_ids):
        blocks = _extract_yaml_blocks(config_notion_enabled_missing_ids)
        yaml_text = "\n".join(blocks)
        assert 'data_source_id: ""' in yaml_text or "data_source_id: ''" in yaml_text

    def test_skill_validates_notion_keys(self, skill_md):
        """SKILL.md Mode 0 must validate Notion IDs when enabled: true."""
        text_lower = skill_md.lower()
        # Should mention checking that IDs are populated/well-formed
        assert any(phrase in text_lower for phrase in [
            "data_source_id",
            "parent_page_url",
            "tracker_url",
        ]), "SKILL.md does not mention validating Notion config keys"

        assert any(phrase in text_lower for phrase in [
            "malformed",
            "well-formed",
            "populated",
            "valid",
        ]), "SKILL.md does not describe validation behavior for Notion keys"


# ---------------------------------------------------------------------------
# State 4: Notion enabled with valid IDs
# ---------------------------------------------------------------------------

class TestConfigNotionEnabledValid:
    """When fully configured, Notion is a mirror — vault stays primary."""

    def test_fixture_has_enabled_true(self, config_notion_enabled_valid):
        assert _has_notion_enabled(config_notion_enabled_valid, "true")

    def test_fixture_has_real_ids(self, config_notion_enabled_valid):
        blocks = _extract_yaml_blocks(config_notion_enabled_valid)
        yaml_text = "\n".join(blocks)
        # Should have non-empty, non-placeholder IDs
        assert 'data_source_id: ""' not in yaml_text
        assert "<your-" not in yaml_text

    def test_enabled_notion_is_mirror_not_primary(self, skill_md):
        """Even with Notion enabled, the vault is primary; Notion is mirror."""
        text_lower = skill_md.lower()
        assert any(phrase in text_lower for phrase in [
            "vault is the primary store",
            "vault is the source of truth",
            "notion is secondary",
            "notion is a mirror",
            "optional mirror",
        ]), (
            "SKILL.md does not state that Notion is secondary even when enabled"
        )

    def test_enabled_notion_requires_user_confirmation(self, skill_md):
        """Notion writes should require user confirmation, not happen silently."""
        text_lower = skill_md.lower()
        assert any(phrase in text_lower for phrase in [
            "offer to push",
            "offer to mirror",
            "user confirmation",
            "after getting user confirmation",
        ]), (
            "SKILL.md does not require user confirmation before Notion writes"
        )


# ---------------------------------------------------------------------------
# Cross-state: config.template.md consistency
# ---------------------------------------------------------------------------

@pytest.fixture
def config_template_text(vault_path):
    """Raw text of config.template.md.  Skip if not present (main vault has config.md instead)."""
    template = vault_path / "config.template.md"
    if not template.exists():
        pytest.skip("config.template.md not present (main vault uses config.md)")
    return template.read_text(encoding="utf-8")


class TestConfigTemplate:
    """config.template.md must be consistent with SKILL.md's config contract.

    These tests run only in the open-source copy where config.template.md
    exists.  The main vault has a real config.md with live Notion IDs, so
    template-specific assertions (default disabled, labels optional, etc.)
    don't apply there.
    """

    def test_template_labels_notion_optional(self, config_template_text):
        """config.template.md must label Notion as optional."""
        text_lower = config_template_text.lower()
        assert "optional" in text_lower, (
            "config.template.md does not label Notion as optional"
        )

    def test_template_has_enabled_key(self, config_template_text):
        """config.template.md must include the enabled: key so users can toggle."""
        assert "enabled:" in config_template_text

    def test_template_default_is_disabled(self, config_template_text):
        """The template should default to Notion disabled (safe default)."""
        blocks = _extract_yaml_blocks(config_template_text)
        yaml_text = "\n".join(blocks)
        assert "enabled: false" in yaml_text, (
            "config.template.md should default to enabled: false for safe out-of-box behavior"
        )

    def test_template_documents_fallback(self, config_template_text):
        """Template should explain what happens when values are missing."""
        text_lower = config_template_text.lower()
        assert any(phrase in text_lower for phrase in [
            "falls back",
            "markdown-only",
            "markdown only",
            "skip",
        ]), (
            "config.template.md does not explain fallback behavior for missing values"
        )
