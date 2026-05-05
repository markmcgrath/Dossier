"""
Tests for eval frontmatter schema validation.
"""
from datetime import datetime


VALID_GRADES = {"A", "B+", "B", "B-", "C", "D", "F"}
VALID_STATUSES = {
    "Evaluating",
    "Applied",
    "Interviewing",
    "Offer",
    "Rejected",
    "Passed",
    "Offer-Declined",
    "Batch-Evaluated",
    "Superseded",
}

# Terminal bookkeeping statuses where the eval no longer represents an active
# assessment — grade, score, and outcome are exempt from schema validation
# because the eval may have been re-evaluated under a new file (same slug,
# later date) and the original assessment is preserved there.
SCHEMA_EXEMPT_STATUSES = {"Superseded"}
VALID_OUTCOMES = {
    "Pending",
    "No Response",
    "Rejected",
    "Phone Screen",
    "Interview",
    "Offer",
    "Accepted",
    "Withdrawn",
}
VALID_LEGITIMACIES = {"Verified", "Plausible", "Suspect", "Likely Ghost"}


def test_all_evals_have_required_fields(eval_files):
    """Verify all eval files have required frontmatter fields.

    Evals in a SCHEMA_EXEMPT_STATUSES state (e.g. Superseded) only need
    type, company, role, status, date — grade/score/outcome are exempt.
    """
    base_required = {"type", "company", "role", "status", "date"}
    full_required = base_required | {"grade", "score", "outcome"}
    missing = []

    for fm in eval_files:
        file_name = fm.get("__file__", "unknown")
        required = (
            base_required if fm.get("status") in SCHEMA_EXEMPT_STATUSES else full_required
        )
        for field in required:
            if field not in fm or fm[field] is None:
                missing.append((file_name, field))

    if missing:
        msg = "Evals missing required fields:\n"
        for fname, field in missing:
            msg += f"  {fname}: {field}\n"
        assert False, msg


def test_grade_values_are_valid(eval_files):
    """Verify all grade values are in valid set.

    Schema-exempt statuses skip this check.
    """
    invalid = []
    for fm in eval_files:
        if fm.get("status") in SCHEMA_EXEMPT_STATUSES:
            continue
        grade = fm.get("grade")
        file_name = fm.get("__file__", "unknown")
        if grade not in VALID_GRADES:
            invalid.append((file_name, grade))

    if invalid:
        msg = "Invalid grade values:\n"
        for fname, grade in invalid:
            msg += f"  {fname}: '{grade}' (expected one of {VALID_GRADES})\n"
        assert False, msg


def test_status_values_are_valid(eval_files):
    """Verify all status values are valid."""
    invalid = []
    for fm in eval_files:
        status = fm.get("status")
        file_name = fm.get("__file__", "unknown")
        if status not in VALID_STATUSES:
            invalid.append((file_name, status))

    if invalid:
        msg = "Invalid status values:\n"
        for fname, status in invalid:
            msg += f"  {fname}: '{status}' (expected one of {VALID_STATUSES})\n"
        assert False, msg


def test_outcome_values_are_valid(eval_files):
    """Verify all outcome values are valid.

    Schema-exempt statuses skip this check.
    """
    invalid = []
    for fm in eval_files:
        if fm.get("status") in SCHEMA_EXEMPT_STATUSES:
            continue
        outcome = fm.get("outcome")
        file_name = fm.get("__file__", "unknown")
        # outcome can be None (for old evals), but if present must be valid
        if outcome is not None and outcome not in VALID_OUTCOMES:
            invalid.append((file_name, outcome))

    if invalid:
        msg = "Invalid outcome values:\n"
        for fname, outcome in invalid:
            msg += f"  {fname}: '{outcome}' (expected one of {VALID_OUTCOMES})\n"
        assert False, msg


def test_legitimacy_values_are_valid(eval_files):
    """Verify all legitimacy values are valid (if present)."""
    invalid = []
    for fm in eval_files:
        legitimacy = fm.get("legitimacy")
        file_name = fm.get("__file__", "unknown")
        # legitimacy is optional on old evals
        if legitimacy is not None and legitimacy not in VALID_LEGITIMACIES:
            invalid.append((file_name, legitimacy))

    if invalid:
        msg = "Invalid legitimacy values:\n"
        for fname, legit in invalid:
            msg += f"  {fname}: '{legit}' (expected one of {VALID_LEGITIMACIES})\n"
        assert False, msg


def test_date_format_is_correct(eval_files):
    """Verify all date values are in YYYY-MM-DD format or are date objects."""
    invalid = []
    for fm in eval_files:
        date_val = fm.get("date")
        file_name = fm.get("__file__", "unknown")
        # Accept either string in YYYY-MM-DD format or a date object from YAML parsing
        if isinstance(date_val, datetime):
            # YAML parsed it as a date object; this is OK
            continue
        try:
            datetime.strptime(str(date_val), "%Y-%m-%d")
        except (ValueError, TypeError):
            invalid.append((file_name, date_val))

    if invalid:
        msg = "Invalid date format (expected YYYY-MM-DD or parsed date object):\n"
        for fname, date_val in invalid:
            msg += f"  {fname}: '{date_val}'\n"
        assert False, msg


def test_score_is_numeric_in_range(eval_files):
    """Verify all score values are numeric and in range 1.0–5.0.

    Schema-exempt statuses skip this check.
    """
    invalid = []
    for fm in eval_files:
        if fm.get("status") in SCHEMA_EXEMPT_STATUSES:
            continue
        score = fm.get("score")
        file_name = fm.get("__file__", "unknown")
        try:
            score_num = float(score)
            if not (1.0 <= score_num <= 5.0):
                invalid.append((file_name, score, "out of range"))
        except (ValueError, TypeError):
            invalid.append((file_name, score, "not numeric"))

    if invalid:
        msg = "Invalid score values:\n"
        for fname, score, reason in invalid:
            msg += f"  {fname}: '{score}' ({reason})\n"
        assert False, msg


def test_all_evals_have_outcome_pending_or_real(eval_files):
    """Verify all backfilled evals have outcome field (Pending or real outcome).

    Schema-exempt statuses skip this check.
    """
    missing_outcome = []
    for fm in eval_files:
        if fm.get("status") in SCHEMA_EXEMPT_STATUSES:
            continue
        if "outcome" not in fm or fm["outcome"] is None:
            missing_outcome.append(fm.get("__file__", "unknown"))

    if missing_outcome:
        msg = "Evals missing 'outcome' field (should be backfilled):\n"
        for fname in missing_outcome:
            msg += f"  {fname}\n"
        assert False, msg
