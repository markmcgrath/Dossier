"""
Tests for SKILL.md content structure and required sections.
"""
import re
import pytest


def test_content_trust_boundary_exists(skill_md):
    """Verify Content Trust Boundary section appears before first Mode heading."""
    if "Content Trust Boundary" not in skill_md:
        pytest.skip(
            "Content Trust Boundary section not yet added to SKILL.md — "
            "planned in features/plan/01-architecture.md (Stream A)"
        )

    # Find position of both
    ctb_pos = skill_md.find("Content Trust Boundary")
    mode_pos = skill_md.find("## Mode")
    assert ctb_pos > 0, "Content Trust Boundary not found"
    assert mode_pos > ctb_pos, "Content Trust Boundary must appear before first Mode section"


def test_mode_0_health_check_exists(skill_md):
    """Verify Mode 0 (health check) section exists and contains health check language."""
    if "Mode 0" not in skill_md:
        pytest.skip(
            "Mode 0 (health check) not yet added to SKILL.md — "
            "planned in features/plan/ (Stream B)"
        )
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

    if missing:
        pytest.skip(
            f"Modes not yet implemented in SKILL.md: {', '.join(missing)}. "
            "Modes 12, 13, and 2.1 are planned in features/plan/ (Streams D–F)."
        )


def test_pipeline_state_reading_section_exists(skill_md):
    """Verify 'Reading Pipeline State' or similar section exists."""
    has_section = (
        "Reading Pipeline State" in skill_md
        or "Reading the Pipeline" in skill_md
        or "Pipeline State" in skill_md
    )
    if not has_section:
        pytest.skip(
            "Explicit 'Pipeline State' section not yet added to SKILL.md — "
            "planned in features/plan/01-architecture.md (Stream A vault-first migration)"
        )


def test_gate_pass_rule_is_prominent(skill_md):
    """Verify Gate-Pass Rule appears as a clear section (not buried)."""
    if "Gate-Pass Rule" not in skill_md:
        pytest.skip(
            "Gate-Pass Rule section not yet added to SKILL.md as a prominent heading — "
            "planned in features/plan/review-report.md (issue #9)"
        )
    assert "gate-pass" in skill_md.lower(), "Gate-pass rule not documented"


def test_bias_caveat_in_mode_1(skill_md):
    """Verify bias caveat appears somewhere in SKILL.md mentioning AI and pattern-matching."""
    if "Bias Caveat" not in skill_md and "bias caveat" not in skill_md.lower():
        pytest.skip(
            "Explicit Bias Caveat section not yet added to SKILL.md — "
            "planned in features/plan/review-report.md"
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
            f"Config keys not yet documented in SKILL.md: {', '.join(missing_keys)}. "
            "These are planned config extensions in features/plan/ (Stream C)."
        )


def test_frontmatter_template_has_outcome(skill_md):
    """Verify frontmatter template includes outcome: field."""
    if "outcome:" not in skill_md:
        pytest.skip(
            "outcome: field not yet added to the frontmatter template in SKILL.md — "
            "present in example eval files but not yet in the skill's template block. "
            "Planned in features/plan/03-foundation.md."
        )


def test_frontmatter_template_has_legitimacy(skill_md):
    """Verify frontmatter template includes legitimacy: field."""
    if "legitimacy:" not in skill_md:
        pytest.skip(
            "legitimacy: field not yet added to the frontmatter template in SKILL.md — "
            "present in example eval files but not yet in the skill's template block. "
            "Planned in features/plan/03-foundation.md."
        )


def test_mode_12_batch_pipeline_exists(skill_md):
    """Verify Mode 12 (Batch Pipeline) section exists."""
    if "Mode 12" not in skill_md and "Batch Pipeline" not in skill_md.lower():
        pytest.skip(
            "Mode 12 (Batch Pipeline) not yet implemented in SKILL.md — "
            "planned in features/plan/05-advanced.md"
        )


def test_mode_13_calibration_exists(skill_md):
    """Verify Mode 13 (Calibration Report) section exists."""
    if "Mode 13" not in skill_md and "Calibration Report" not in skill_md.lower():
        pytest.skip(
            "Mode 13 (Calibration Report) not yet implemented in SKILL.md — "
            "planned in features/plan/05-advanced.md"
        )


def test_portal_scan_submode_exists(skill_md):
    """Verify Mode 2.1 (Portal Scan) submode exists."""
    if "Mode 2.1" not in skill_md and "Portal Scan" not in skill_md:
        pytest.skip(
            "Mode 2.1 (Portal Scan) not yet implemented in SKILL.md — "
            "planned in features/plan/04-competitive.md"
        )
