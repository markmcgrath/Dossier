"""
Tests for the send-ready contract validator.

Covers:
  - A dirty tuned CV fixture is flagged (What Changed section, placeholder bracket, html comment).
  - A clean tuned CV fixture passes.
  - A dirty cover letter fixture is flagged (NOTE: prefix, blockquote).
  - A clean cover letter fixture passes.
  - The section allowlist rejects an unknown heading in a tuned CV.
  - Frontmatter content is NOT flagged as a failure.

These tests import the validator module directly rather than calling subprocess,
matching the pattern used in test_antipatterns.py.
"""
import sys
from pathlib import Path
import importlib.util
import json
import tempfile
import textwrap

import pytest


# ---------------------------------------------------------------------------
# Helper: load the validator module by path so tests don't depend on install.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def sendready_scan(vault_path):
    script = vault_path / ".github" / "scripts" / "sendready_scan.py"
    assert script.exists(), f"sendready_scan.py not found at {script}"
    spec = importlib.util.spec_from_file_location("sendready_scan", script)
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so the dataclasses in the module can resolve their own
    # module namespace under `from __future__ import annotations` (Python 3.12+).
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def sr_config(vault_path):
    cfg_path = vault_path / "skill" / "references" / "send_ready_config.json"
    assert cfg_path.exists(), f"send_ready_config.json not found at {cfg_path}"
    return json.loads(cfg_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Fixtures: dirty and clean documents
# ---------------------------------------------------------------------------

DIRTY_CV = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    notes: "Internal note in frontmatter — should NOT be flagged."
    ---

    # Jane Smith

    Remote | jane@example.com

    ---

    ## Professional Summary

    Experienced engineer with a focus on <!-- TODO: refine this --> distributed systems.

    ---

    ## Skills

    Python, Go, [ADD YOUR SKILLS HERE]

    ---

    ## Experience

    ### Senior Engineer — Acme Corp
    2022 – Present

    - Led migration of legacy [SYSTEM NAME] to Kubernetes.

    ---

    ## What Changed (vs. master cv.md)
    *This section is for reference only — remove before submitting the CV.*

    - Summary rewritten.
""")

CLEAN_CV = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    ---

    # Jane Smith

    Remote | jane@example.com

    ---

    ## Professional Summary

    Experienced engineer with a focus on distributed systems and platform reliability.

    ---

    ## Skills

    Python, Go, Kubernetes, PostgreSQL

    ---

    ## Experience

    ### Senior Engineer — Acme Corp
    2022 – Present

    - Led migration of legacy monolith to Kubernetes, reducing deploy time by 60%.
    - Designed incident response runbooks adopted by a 12-person SRE team.

    ---

    ## Education

    **B.S. Computer Science** — State University, 2015
""")

DIRTY_COVER = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    ---

    Dear Hiring Team,

    NOTE: Insert a stronger opening here.

    > Reviewer: this paragraph needs a better hook.

    I am excited to apply for the Senior Engineer role at Acme.

    Sincerely,
    Jane Smith
""")

CLEAN_COVER = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    ---

    Dear Acme Hiring Team,

    I have spent the last five years building distributed systems at scale, most recently
    at a fintech startup where I owned the platform reliability function for a system
    processing two million transactions per day.

    I would welcome the chance to discuss how this experience maps to your Senior
    Engineer opening.

    Sincerely,
    Jane Smith
    jane@example.com
""")

DIRTY_CV_BAD_SECTION = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    ---

    # Jane Smith

    Remote | jane@example.com

    ## Professional Summary

    Experienced engineer.

    ## Hobbies and Interests

    Mountain biking, pottery.

    ## Experience

    ### Engineer — Acme
    2022 – Present

    - Built things.
""")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDirtyCV:
    def test_html_comment_flagged(self, sendready_scan, sr_config, tmp_path):
        cv_file = tmp_path / "cv-acme-2026-01-01.md"
        cv_file.write_text(DIRTY_CV, encoding="utf-8")
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "html-comment" in failure_rules_hit, "Expected html-comment failure"

    def test_placeholder_flagged(self, sendready_scan, sr_config, tmp_path):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "placeholder" in failure_rules_hit, "Expected placeholder failure"

    def test_what_changed_section_flagged(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "banned-section" in failure_rules_hit, "Expected banned-section failure for What Changed"

    def test_frontmatter_notes_not_flagged(self, sendready_scan, sr_config):
        """notes: field in frontmatter must not produce a failure."""
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV)
        # The body must not contain the frontmatter notes line
        assert 'notes: "Internal note in frontmatter' not in body


class TestCleanCV:
    def test_clean_cv_passes(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(CLEAN_CV)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failures = [f for f in findings if f.severity == "failure"]
        assert not failures, f"Expected no failures in clean CV, got: {failures}"


class TestDirtyCoverLetter:
    def test_note_prefix_flagged(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_COVER)
        findings = sendready_scan.scan_body(body, "cover_letter", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "note-prefix" in failure_rules_hit, "Expected note-prefix failure"

    def test_blockquote_flagged(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_COVER)
        findings = sendready_scan.scan_body(body, "cover_letter", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "blockquote" in failure_rules_hit, "Expected blockquote failure"


class TestCleanCoverLetter:
    def test_clean_cover_passes(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(CLEAN_COVER)
        findings = sendready_scan.scan_body(body, "cover_letter", failure_rules, warning_rules, allowed)
        failures = [f for f in findings if f.severity == "failure"]
        assert not failures, f"Expected no failures in clean cover letter, got: {failures}"


class TestSectionAllowlist:
    def test_unknown_section_flagged(self, sendready_scan, sr_config):
        """A ## heading not in the allowlist must produce an unknown-section failure."""
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV_BAD_SECTION)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "unknown-section" in failure_rules_hit, (
            "Expected unknown-section failure for 'Hobbies and Interests'"
        )

    def test_unknown_section_not_flagged_for_cover_letter(self, sendready_scan, sr_config):
        """Section allowlist does not apply to cover letters."""
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV_BAD_SECTION)
        findings = sendready_scan.scan_body(body, "cover_letter", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "unknown-section" not in failure_rules_hit
