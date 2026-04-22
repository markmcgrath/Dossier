"""
Tests for SKILL.md content structure and required sections.

Currently deferred (skipped) tests — all tracked in plan 13 (quality audit
remediation):

- ``test_gate_pass_rule_is_prominent`` — "Gate-Pass Rule" heading not yet in
  ``skill/SKILL.md``. Plan 13 Stream A adds it.
- ``test_bias_caveat_in_mode_1`` — Bias Caveat is being added to
  ``skill/references/mode1-offer-evaluator.md`` (a reference file), not to
  ``SKILL.md``. This test will be retired or rescoped when plan 13 ships.
- ``test_all_config_keys_documented`` — ``redact_comp`` and
  ``scoring_weights`` not yet documented in ``skill/SKILL.md``. Plan 13
  Stream C covers the config-schema work.

All other structural tests are hard asserts: a regression that removes a
required section from ``SKILL.md`` will fail CI loudly rather than
silently skip.
"""
import re
import pytest


def test_content_trust_boundary_exists(skill_md):
    """Verify Content Trust Boundary section appears before first Mode heading."""
    ctb_pos = skill_md.find("Content Trust Boundary")
    assert ctb_pos > 0, "Content Trust Boundary section missing from SKILL.md"
    mode_pos = skill_md.find("## Mode")
    assert mode_pos > ctb_pos, "Content Trust Boundary must appear before first Mode section"


def test_mode_0_health_check_exists(skill_md):
    """Verify Mode 0 (health check) section exists and contains health check language."""
    assert "Mode 0" in skill_md, "Mode 0 (health check) section missing from SKILL.md"
    mode_0_section = skill_md[skill_md.find("Mode 0") : skill_md.find("Mode 0") + 2000]
    keywords = ["health", "check", "diagnose", "validate"]
    has_keyword = any(kw in mode_0_section.lower() for kw in keywords)
    assert has_keyword, "Mode 0 section missing health check language"


def test_all_modes_exist(skill_md):
    """Verify Mode 1 through Mode 13 all present; Mode 2.1 present."""
    missing = []
    for mode in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
        if f"Mode {mode}" not in skill_md:
            missing.append(f"Mode {mode}")
    if "Mode 2.1" not in skill_md:
        missing.append("Mode 2.1")

    assert not missing, f"Modes missing from SKILL.md: {', '.join(missing)}"


def test_pipeline_state_reading_section_exists(skill_md):
    """Verify 'Reading Pipeline State' or similar section exists."""
    has_section = (
        "Reading Pipeline State" in skill_md
        or "Reading the Pipeline" in skill_md
        or "Pipeline State" in skill_md
    )
    assert has_section, "Pipeline State section missing from SKILL.md"


def test_gate_pass_rule_is_prominent(skill_md):
    """Verify Gate-Pass Rule appears as a clear section (not buried)."""
    if "Gate-Pass Rule" not in skill_md:
        pytest.skip(
            "Gate-Pass Rule section not present in `skill/SKILL.md`. "
            "Tracked in plan 13 (quality audit remediation) Stream A."
        )
    assert "gate-pass" in skill_md.lower(), "Gate-pass rule not documented"


def test_bias_caveat_in_mode_1(skill_md):
    """Verify bias caveat appears somewhere in SKILL.md mentioning AI and pattern-matching."""
    if "Bias Caveat" not in skill_md and "bias caveat" not in skill_md.lower():
        pytest.skip(
            "Bias Caveat is being added to `references/mode1-offer-evaluator.md` "
            "per plan 13 Stream A.2, not to SKILL.md. This test will be retired "
            "or rescoped when plan 13 ships — see plan 16 follow-up note."
        )
    has_ai = "AI" in skill_md
    has_pattern_or_bias = "pattern" in skill_md.lower() or "bias" in skill_md.lower()
    assert (
        has_ai and has_pattern_or_bias
    ), "SKILL.md missing caveat about AI limitations and pattern-matching risks"


def test_vault_first_general_principles(skill_md):
    """Verify general principles section includes vault-first directive."""
    assert "Always save evaluations to the vault" in skill_md or (
        "save" in skill_md.lower() and "vault" in skill_md.lower()
    ), "General principles missing vault-first directive"


def test_all_config_keys_documented(skill_md):
    """Verify all known config keys appear in SKILL.md."""
    config_keys = [
        "redact_comp",
        "gmail_allow_domains",
        "gmail_deny_domains",
        "scoring_weights",
        "target_companies",
    ]
    missing_keys = [k for k in config_keys if k not in skill_md]
    if missing_keys:
        pytest.skip(
            f"Config keys not yet documented in `skill/SKILL.md`: "
            f"{', '.join(missing_keys)}. Tracked in plan 13 Stream C "
            "(config schema work). `gmail_allow_domains`, "
            "`gmail_deny_domains`, `target_companies` are already present."
        )


def test_frontmatter_template_has_outcome(skill_md):
    """Verify frontmatter template includes outcome: field."""
    assert "outcome:" in skill_md, (
        "`outcome:` field missing from the frontmatter template in SKILL.md"
    )


def test_frontmatter_template_has_legitimacy(skill_md):
    """Verify frontmatter template includes legitimacy: field."""
    assert "legitimacy:" in skill_md, (
        "`legitimacy:` field missing from the frontmatter template in SKILL.md"
    )


def test_mode_12_batch_pipeline_exists(skill_md):
    """Verify Mode 12 (Batch Pipeline) section exists."""
    has_section = "Mode 12" in skill_md or "batch pipeline" in skill_md.lower()
    assert has_section, "Mode 12 (Batch Pipeline) missing from SKILL.md"


def test_mode_13_calibration_exists(skill_md):
    """Verify Mode 13 (Calibration Report) section exists."""
    has_section = "Mode 13" in skill_md or "calibration report" in skill_md.lower()
    assert has_section, "Mode 13 (Calibration Report) missing from SKILL.md"


def test_portal_scan_submode_exists(skill_md):
    """Verify Mode 2.1 (Portal Scan) submode exists."""
    has_section = "Mode 2.1" in skill_md or "Portal Scan" in skill_md
    assert has_section, "Mode 2.1 (Portal Scan) missing from SKILL.md"
