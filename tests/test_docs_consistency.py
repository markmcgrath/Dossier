"""
Cross-document consistency tests for Notion optionality.

All core docs must agree on four rules:
  1. Vault is the source of truth.
  2. Notion is optional.
  3. Missing/disabled Notion does not block core evaluation.
  4. When enabled, Notion is a mirror or secondary system.

Failures include the file, rule, and expected language intent so a
contributor can resolve mismatches quickly.
"""
from pathlib import Path
import pytest


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Files to check (relative to vault root).
# For paths that differ between the main vault and open-source copy,
# we list alternatives as tuples — the first one found wins.
DOC_SPEC = [
    "README.md",
    "CLAUDE.md",
    ("config.md", "config.template.md"),          # main vault vs open-source
    "DATA_CONTRACT.md",
    ("skill-update/SKILL.md", "skill/SKILL.md"),  # main vault vs open-source
]

# Canonical key used in APPLICABILITY (always the last alternative).
# This keeps rule definitions stable regardless of which path resolves.
_CANONICAL = {
    "skill-update/SKILL.md": "skill/SKILL.md",
}

# Files where the actual resolved name determines whether rules apply.
# config.md is a real user file — only config.template.md gets tested
# against optionality rules, because the real config naturally won't
# contain "optional" boilerplate.
_TEMPLATE_ONLY_KEYS = {"config.template.md"}

# START_HERE.md is excluded: it's an onboarding script for Claude, not a
# user-facing doc that describes architecture.  It shouldn't need to
# restate the optionality contract.


# ---------------------------------------------------------------------------
# Consistency rules
# ---------------------------------------------------------------------------

# Each rule is (rule_name, description, phrases).
# A doc passes the rule if at least one phrase appears (case-insensitive).
# Not every doc must pass every rule — APPLICABILITY below controls which
# docs must satisfy which rules.

RULES = {
    "vault_is_source_of_truth": {
        "description": "States that the vault is the source of truth",
        "phrases": [
            "vault is the source of truth",
            "vault is always the source of truth",
            "vault is the primary store",
            "vault owns all pipeline state",
            "single source of truth",
            "your data, your vault",
            "source of truth for",
        ],
    },
    "notion_is_optional": {
        "description": "Labels Notion as optional, not required",
        "phrases": [
            "optional",
            "not required",
            "no cloud sync required",
            "if you configure",
            "if a notion tracker is configured",
            "if you're not using notion",
        ],
    },
    "core_works_without_notion": {
        "description": "Core evaluation works without Notion",
        "phrases": [
            "vault only",
            "vault-only",
            "markdown-only",
            "markdown only",
            "without notion",
            "not using notion",
            "no notion reads or writes",
            "operate entirely from the vault",
            "falls back",
        ],
    },
    "notion_is_secondary": {
        "description": "When enabled, Notion is a mirror or secondary system",
        "phrases": [
            "mirror",
            "secondary",
            "optional mirror",
            "notion is secondary",
            "notion data is separate",
        ],
    },
}

# Which rules apply to which docs.
# SKILL.md and config.template.md must satisfy all rules.
# README, CLAUDE.md, DATA_CONTRACT need vault-sot and notion-optional at minimum.
APPLICABILITY = {
    "skill/SKILL.md":       ["vault_is_source_of_truth", "notion_is_optional", "core_works_without_notion", "notion_is_secondary"],
    "config.template.md":   ["notion_is_optional", "core_works_without_notion"],
    "README.md":            ["vault_is_source_of_truth", "notion_is_optional"],
    "CLAUDE.md":            ["vault_is_source_of_truth", "notion_is_optional"],
    "DATA_CONTRACT.md":     ["notion_is_optional"],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _resolve_doc_files(vault_path):
    """Resolve DOC_SPEC into a dict of {canonical_key: (actual_name, path)}.

    Returns both the canonical key and the actual resolved filename so
    callers can distinguish e.g. config.md (real) from config.template.md.
    """
    resolved = {}
    for entry in DOC_SPEC:
        if isinstance(entry, str):
            alternatives = (entry,)
        else:
            alternatives = entry

        found = None
        for alt in alternatives:
            full = vault_path / alt
            if full.exists():
                found = (alt, full)
                break

        assert found is not None, (
            f"None of {alternatives} found under {vault_path}"
        )

        actual_name, actual_path = found
        canonical = _CANONICAL.get(actual_name, actual_name)
        resolved[canonical] = (actual_name, actual_path)
    return resolved


@pytest.fixture(scope="session")
def doc_texts(vault_path):
    """Load all docs into a dict of {canonical_key: text}.

    Skips template-only keys when the resolved file is not the template
    (e.g. config.md in the main vault is not config.template.md).
    """
    resolved = _resolve_doc_files(vault_path)
    texts = {}
    for key, (actual_name, path) in resolved.items():
        # If this canonical key requires the template and we got the real
        # file instead, omit it — tests will skip via "not in doc_texts".
        if key in _TEMPLATE_ONLY_KEYS and actual_name != key:
            continue
        texts[key] = path.read_text(encoding="utf-8")
    return texts


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# Canonical keys used for parametrize (stable across main vault and open-source)
_CANONICAL_KEYS = list(APPLICABILITY.keys())


def _check_rule(text, rule_name):
    """Return True if the text satisfies the given rule."""
    rule = RULES[rule_name]
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in rule["phrases"])


class TestDocConsistency:
    """Each applicable doc must satisfy its required optionality rules."""

    @pytest.mark.parametrize("doc_key", _CANONICAL_KEYS)
    def test_applicable_rules(self, doc_texts, doc_key):
        """Check all applicable rules for a single document."""
        if doc_key not in doc_texts:
            pytest.skip(f"Document {doc_key} not found in this vault layout")

        text = doc_texts[doc_key]
        failures = []

        for rule_name in APPLICABILITY[doc_key]:
            if not _check_rule(text, rule_name):
                rule = RULES[rule_name]
                failures.append(
                    f"  Rule '{rule_name}': {rule['description']}\n"
                    f"    Expected one of: {', '.join(repr(p) for p in rule['phrases'][:4])}..."
                )

        if failures:
            msg = f"\n{doc_key} fails {len(failures)} optionality rule(s):\n"
            msg += "\n".join(failures)
            msg += f"\n\nFix: ensure {doc_key} contains language matching the expected phrases."
            assert False, msg


class TestNoContradictions:
    """No doc should contain language that contradicts vault-first."""

    CONTRADICTION_PHRASES = [
        "notion wins",
        "notion is the source of truth",
        "notion owns pipeline",
        "notion is required",
        "you must configure notion",
        "notion is mandatory",
    ]

    @pytest.mark.parametrize("doc_key", _CANONICAL_KEYS)
    def test_no_notion_primary_language(self, doc_texts, doc_key):
        """No doc should elevate Notion above the vault."""
        if doc_key not in doc_texts:
            pytest.skip(f"Document {doc_key} not found in this vault layout")
        text_lower = doc_texts[doc_key].lower()
        found = [p for p in self.CONTRADICTION_PHRASES if p in text_lower]
        assert not found, (
            f"{doc_key} contains language contradicting vault-first architecture: "
            + ", ".join(repr(p) for p in found)
        )
