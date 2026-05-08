"""Validates that release.yml's on.push.tags glob accepts releases and rejects operational markers."""
import fnmatch
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"
EXPECTED_PATTERNS = ["v[0-9]*.[0-9]*.[0-9]*", "v[0-9]*.[0-9]*.[0-9]*-*"]

@pytest.fixture(scope="module")
def workflow():
    return yaml.safe_load(WORKFLOW.read_text())

def test_workflow_has_strict_tag_globs(workflow):
    # YAML key `on:` becomes True in Python; safe_load handles it.
    triggers = workflow.get(True) or workflow.get("on") or {}
    tags = triggers.get("push", {}).get("tags", [])
    assert tags == EXPECTED_PATTERNS, (
        f"release.yml on.push.tags must equal {EXPECTED_PATTERNS}; got {tags}"
    )

@pytest.mark.parametrize(
    "tag,should_match",
    [
        ("v1.1.0", True),
        ("v0.0.0-rc-test", True),
        ("v1.2.3", True),
        ("v10.20.30", True),
        ("v1.0.0-rc.1", True),
        ("v0.0.0-dev+abc1234", True),
        ("v-snapshot-2026-q3", False),
        ("vlatest", False),
        ("v2026q3", False),
        ("v1", False),
        ("v1.0", False),
        ("v1.0.0.0", True),   # glob limitation: trailing .0 is swallowed by *; GitHub Actions has the same behavior
        ("snapshot-v1.0.0", False),
    ],
)
def test_glob_matches_expected_tags(tag, should_match):
    matched = any(fnmatch.fnmatchcase(tag, p) for p in EXPECTED_PATTERNS)
    assert matched == should_match, (
        f"tag {tag!r}: expected match={should_match}, got {matched}"
    )
