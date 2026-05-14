"""
Tests that validate example artifacts against the JSON Schemas in schemas/.

jsonschema is an optional dependency — if it's not installed, the entire
module skips cleanly so CI hosts without it don't break.
"""
import datetime
import json
from pathlib import Path

import pytest

try:
    import jsonschema
except ImportError:
    pytest.skip("jsonschema not installed", allow_module_level=True)

# conftest.py exports parse_frontmatter as a module-level function (not a fixture),
# so we can import it directly.
from conftest import parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent


def _load_schema(name: str) -> dict:
    schema_path = REPO_ROOT / "schemas" / name
    with schema_path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_frontmatter(relative_path: str) -> dict:
    path = REPO_ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    fm, _ = parse_frontmatter(text)
    assert fm is not None, f"No valid YAML frontmatter found in {relative_path}"
    # PyYAML parses unquoted ISO dates as datetime.date objects.
    # Normalise to strings so the schemas can enforce the YYYY-MM-DD pattern.
    for key, value in fm.items():
        if isinstance(value, (datetime.date, datetime.datetime)):
            fm[key] = value.strftime("%Y-%m-%d")
    return fm


def test_example_eval_matches_schema():
    """example-eval.md frontmatter validates against schemas/eval.schema.json."""
    fm = _load_frontmatter("examples/example-eval.md")
    schema = _load_schema("eval.schema.json")
    jsonschema.validate(fm, schema)


def test_example_outreach_matches_schema():
    """example-outreach.md frontmatter validates against schemas/outreach.schema.json."""
    fm = _load_frontmatter("examples/example-outreach.md")
    schema = _load_schema("outreach.schema.json")
    jsonschema.validate(fm, schema)
