"""Validates cliff.toml structure and the CC type → CHANGELOG section mapping."""
from pathlib import Path
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # fallback for 3.10

REPO_ROOT = Path(__file__).resolve().parent.parent
CLIFF = REPO_ROOT / "cliff.toml"

def test_cliff_toml_loads():
    config = tomllib.loads(CLIFF.read_text())
    assert "git" in config

def test_filter_commits_enabled():
    config = tomllib.loads(CLIFF.read_text())
    assert config["git"]["filter_commits"] is True

def test_commit_parsers_cover_required_types():
    config = tomllib.loads(CLIFF.read_text())
    parsers = config["git"]["commit_parsers"]
    # Build a set of (regex pattern, group) pairs for verification.
    type_to_group = {}
    for parser in parsers:
        if "message" in parser and "group" in parser:
            type_to_group[parser["message"]] = parser["group"]
    # Required mappings (substring match on regex, since the parser
    # might use ^feat: or ^feat\(.+\): or similar patterns).
    required = {
        "feat": "Added",
        "fix": "Fixed",
        "perf": "Changed",
        "refactor": "Changed",
        "docs": "Documentation",
    }
    for cc_type, expected_section in required.items():
        # Find a parser whose message regex includes the CC type token.
        found = [g for m, g in type_to_group.items() if cc_type in m]
        assert found, f"no commit_parser for {cc_type!r}"
        assert expected_section in found, (
            f"{cc_type!r} must map to {expected_section!r}; got {found}"
        )
