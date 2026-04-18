"""
Contract tests for Notion optionality in SKILL.md.

These enforce the vault-first architecture: the vault is always the source of
truth, and Notion is strictly optional.  Every Notion reference in SKILL.md
must appear in a clearly conditional context — never as a mandatory step.

Replaces the earlier pattern-scan approach that relied on unconditional skips
and informational-only assertions.
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Markers that make a Notion reference "conditional" (i.e. clearly gated on
# config or labeled optional/mirror).
CONDITIONAL_MARKERS = [
    "notion.enabled",
    "if notion",
    "if `notion",
    "optional",
    "mirror",
    "notion:",          # YAML key definition
    "Notion Mirror",
    "(optional)",
    "configured",
    "when enabled",
]

# Section headings whose *entire scope* is inherently conditional/setup.
# A Notion mention inside one of these is fine without a per-line marker.
SAFE_SECTION_HEADINGS = [
    "Pipeline Tracker",
    "Setup",
    "Content Trust Boundary",
    "Health Check",         # Mode 0 validates config, mentions are diagnostic
    "Configuration source",
]

# Phrases that, if they appear as a Notion reference, are *always* violations
# regardless of surrounding context — they imply Notion is required.
MANDATORY_PHRASES = [
    "log the result to notion",
    "always log evaluations to notion",
    "logged to notion",
    "notion tracker goes stale",
    "pull from notion",
    "query notion for rows",
    "company names from notion",
    "points to the notion tracker",
    "cross-reference against notion",
    "notion wins",
    "notion is the source of truth",
    "notion owns",
]


def _current_section(lines, line_idx):
    """Walk backwards from line_idx to find the nearest markdown heading."""
    for i in range(line_idx, -1, -1):
        if lines[i].startswith("#"):
            return lines[i].lstrip("#").strip()
    return ""


def _line_is_conditional(line, section_heading):
    """True if the line (or its section) makes the Notion reference clearly conditional."""
    line_lower = line.lower()

    # Per-line conditional markers
    if any(m.lower() in line_lower for m in CONDITIONAL_MARKERS):
        return True

    # Inside a safe section
    if any(h.lower() in section_heading.lower() for h in SAFE_SECTION_HEADINGS):
        return True

    return False


# ---------------------------------------------------------------------------
# Contract 1: No mandatory-Notion phrases anywhere
# ---------------------------------------------------------------------------

def test_no_mandatory_notion_phrases(skill_md):
    """
    SKILL.md must never contain language that implies Notion is required.
    These phrases are unconditional violations — no surrounding context
    can make them acceptable in a vault-first architecture.
    """
    lines = skill_md.split("\n")
    violations = []

    for i, line in enumerate(lines):
        line_lower = line.lower()
        for phrase in MANDATORY_PHRASES:
            if phrase in line_lower:
                violations.append(
                    f"  Line {i+1}: found \"{phrase}\" in: {line.strip()[:100]}"
                )

    assert not violations, (
        "Found phrases that imply Notion is mandatory (vault-first violation):\n"
        + "\n".join(violations)
    )


# ---------------------------------------------------------------------------
# Contract 2: Every Notion reference is conditional or in a safe context
# ---------------------------------------------------------------------------

def test_notion_references_are_conditional(skill_md):
    """
    Every line mentioning 'Notion' (case-insensitive, as a word boundary)
    must either:
      a) contain a conditional marker (optional, mirror, configured, etc.), OR
      b) be inside a section that is inherently about setup/configuration.

    Violations mean a Notion reference looks unconditional to a reader,
    which contradicts the vault-first contract.
    """
    lines = skill_md.split("\n")
    violations = []

    for i, line in enumerate(lines):
        if "notion" not in line.lower():
            continue

        # Skip headings themselves (they name sections, not prescribe behavior)
        if line.strip().startswith("#"):
            continue

        section = _current_section(lines, i)

        if _line_is_conditional(line, section):
            continue

        violations.append({
            "line": i + 1,
            "section": section,
            "text": line.strip()[:120],
        })

    # Known borderline cases — Notion is mentioned but in a context that
    # actually reinforces vault-first (e.g. contrasting vault with Notion)
    # or is a reference-file content listing.  Each entry is a substring
    # that, if present in the violation text, makes it acceptable.
    # When adding to this list, include a reason.
    KNOWN_BORDERLINE = [
        # "vault-native alternative to Notion queries" — affirms vault approach
        "vault-native alternative to notion",
        # Reference-file pointer listing what mode12 reference contains
        "digest table template, notion sync",
    ]

    unexpected = []
    for v in violations:
        text_lower = v["text"].lower()
        if not any(b in text_lower for b in KNOWN_BORDERLINE):
            unexpected.append(v)

    if unexpected:
        msg = (
            f"Found {len(unexpected)} Notion reference(s) without conditional context:\n"
        )
        for v in unexpected:
            msg += f"  Line {v['line']} [{v['section']}]: {v['text']}\n"
        msg += (
            "\nIf this reference is benign, add a substring match to "
            "KNOWN_BORDERLINE in this test with a reason."
        )
        assert False, msg


# ---------------------------------------------------------------------------
# Contract 3: Vault is explicitly the source of truth
# ---------------------------------------------------------------------------

def test_vault_is_source_of_truth(skill_md):
    """
    SKILL.md must contain at least one explicit statement that the vault
    is the source of truth.  This is the affirmative side of the contract.
    """
    markers = [
        "vault is the source of truth",
        "vault is the primary store",
        "source of truth",
        "vault owns all pipeline state",
        "single source of truth",
    ]
    text_lower = skill_md.lower()
    found = [m for m in markers if m in text_lower]
    assert found, (
        "SKILL.md does not contain any explicit vault-as-source-of-truth statement. "
        "Expected at least one of: " + ", ".join(f'"{m}"' for m in markers)
    )


# ---------------------------------------------------------------------------
# Contract 4: Notion-disabled path is explicitly documented
# ---------------------------------------------------------------------------

def test_notion_disabled_path_exists(skill_md):
    """
    SKILL.md must document what happens when Notion is disabled or missing.
    This ensures a user without Notion sees a clear, intentional path —
    not silence or an error.
    """
    indicators = [
        "notion.enabled: false",
        "notion: block is missing",
        "notion is not configured",
        "vault only",
        "vault-only",
        "markdown-only",
        "markdown only",
        "saving all evals to the vault only",
    ]
    text_lower = skill_md.lower()
    found = [ind for ind in indicators if ind in text_lower]
    assert found, (
        "SKILL.md does not document the Notion-disabled path. "
        "Expected at least one of: " + ", ".join(f'"{ind}"' for ind in indicators)
    )


# ---------------------------------------------------------------------------
# Contract 5: No Notion requirement for core evaluation workflow
# ---------------------------------------------------------------------------

def test_mode1_eval_saves_to_vault(skill_md):
    """
    The evaluation output section must mandate saving to the vault.
    This ensures Mode 1 never depends on Notion for its primary operation.
    """
    text_lower = skill_md.lower()
    assert "always save evaluations to the vault" in text_lower or \
           "saved to `evals/" in skill_md or \
           "save as a markdown file in `evals/`" in text_lower, (
        "SKILL.md Mode 1 does not clearly mandate saving evals to the vault filesystem."
    )
