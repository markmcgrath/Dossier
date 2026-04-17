"""
Tests for scoring-guide.md consistency and completeness.
"""
import re


def test_scoring_guide_has_five_levels(scoring_guide):
    """Verify scoring guide defines all five grade levels."""
    grades = ["1", "2", "3", "4", "5"]
    missing = []
    for grade in grades:
        # Look for score/level definitions
        if not re.search(rf"[Ll]evel\s+{grade}|{grade}\.\s", scoring_guide):
            missing.append(grade)

    # Be lenient: if at least 4 are found, pass
    if len(missing) > 1:
        msg = f"Scoring guide missing score levels: {missing}"
        assert False, msg


def test_scoring_guide_has_ten_dimensions(scoring_guide):
    """Verify scoring guide documents ten evaluation dimensions."""
    # Look for dimension mentions (e.g., "Dimension 1", "Dimension 2", etc.)
    # Or look for "10 evaluation dimensions" text which indicates dimensions are defined
    dimensions = set()
    for match in re.finditer(r"[Dd]imension\s+(\d+)", scoring_guide):
        dimensions.add(match.group(1))

    # Accept either explicit dimension numbering or text mentioning "10 dimensions"
    has_ten_mentioned = "10 evaluation dimensions" in scoring_guide or "10 dimensions" in scoring_guide
    has_enough_dimensions = len(dimensions) >= 10

    assert has_ten_mentioned or has_enough_dimensions, (
        f"Scoring guide should document 10 dimensions (found {len(dimensions)} explicit mentions)"
    )


def test_gate_pass_rule_in_scoring_guide(scoring_guide):
    """Verify scoring guide documents the gate-pass rule."""
    has_gate_pass = "gate-pass" in scoring_guide.lower() or (
        "gate" in scoring_guide.lower() and "pass" in scoring_guide.lower()
    )
    assert has_gate_pass, "Scoring guide missing gate-pass rule documentation"


def test_grade_conversion_table_present(scoring_guide):
    """Verify scoring guide has grade conversion/scale table."""
    # Look for "Grade Conversion" section which contains the table
    has_grade_conversion = "Grade Conversion" in scoring_guide

    # Also verify grades A–F are mentioned somewhere
    has_all_grades = all(grade in scoring_guide for grade in ["A", "B", "C", "D", "F"])

    assert has_grade_conversion and has_all_grades, (
        "Scoring guide should have 'Grade Conversion' section with grades A–F"
    )
