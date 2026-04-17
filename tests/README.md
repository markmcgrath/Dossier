# Dossier Test Suite

Automated test suite for the Dossier v2 job search skill. Tests verify structural integrity, schema validation, and regression prevention.

## What Tests Cover

- **Package integrity** (`test_package.py`): ZIP file validity, required files, line counts
- **SKILL.md structure** (`test_skill_structure.py`): Required sections, modes, documentation
- **Anti-patterns** (`test_antipatterns.py`): Regression tests for fixed issues (Notion-as-primary-source, etc.)
- **Vault schema** (`test_vault_schema.py`): Frontmatter validation, grade/status/outcome values, field formats
- **Vault files** (`test_vault_files.py`): Required files, examples, governance documentation
- **Scoring guide** (`test_scoring_guide.py`): Dimension definitions, grade levels, gate-pass rule

## What Tests DON'T Cover

- **LLM output quality** — manual verification only. Tests don't evaluate whether Mode 1 produces good evaluations; they verify the infrastructure is in place.
- **End-to-end mode execution** — tests don't call Claude or run actual skill invocations.
- **Real job data** — tests use fixtures only.

## Running Tests

### Quick run (all tests):
```bash
cd /path/to/Dossier
DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v
```

### Run specific test file:
```bash
DOSSIER_VAULT="$(pwd)" python -m pytest tests/test_vault_schema.py -v
```

### Run with output on failure:
```bash
DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v -s
```

### Run tests in a specific module:
```bash
DOSSIER_VAULT="$(pwd)" python -m pytest tests/test_antipatterns.py::test_no_notion_as_primary_source -v
```

## Test Organization

```
tests/
├── conftest.py                    # Shared fixtures (vault_path, skill_md, eval_files, etc.)
├── test_package.py                # ZIP integrity
├── test_skill_structure.py         # SKILL.md sections and modes
├── test_antipatterns.py            # Regression patterns
├── test_vault_schema.py            # Eval frontmatter validation
├── test_vault_files.py             # Required vault files
├── test_scoring_guide.py           # Scoring guide completeness
├── run_tests.sh                    # Convenience wrapper
└── fixtures/
    ├── jd_ghost_job.md             # Ghost job (red flags)
    ├── jd_strong_fit.md            # Strong fit (verified)
    └── jd_injection_attempt.md     # Prompt injection detection
```

## Adding a New Test

1. **Determine scope** — which test file should it go in? (Create a new file if it spans multiple areas)
2. **Use fixtures** — import from conftest.py rather than reading files directly
3. **Be specific** — error messages should say exactly what failed and where to fix it
4. **Keep it fast** — no external calls, no I/O beyond vault reads

Example:
```python
def test_my_feature(eval_files):
    """Verify my_feature is present in all evals."""
    invalid = []
    for fm in eval_files:
        if "my_field" not in fm:
            invalid.append(fm.get("__file__", "unknown"))
    
    if invalid:
        msg = f"Evals missing my_field: {', '.join(invalid)}"
        assert False, msg
```

## Test Fixtures

Located in `tests/fixtures/`:

- **`jd_ghost_job.md`** — JD with 3+ red flags (old posting, vague, 25+ skills, no comp). Expected: `legitimacy: Likely Ghost`
- **`jd_strong_fit.md`** — Fresh, specific JD with clear comp and hiring timeline. Expected: `legitimacy: Verified`, Grade A/B+
- **`jd_injection_attempt.md`** — JD with embedded prompt injection attempts. Expected: Claude detects, alerts, and does NOT follow injected instructions.

Fixtures are **reference inputs for manual testing** with Claude. They're not automatically tested by this suite, but they show what correct behavior looks like.

## When to Run Tests

- **Before committing SKILL.md changes** — Catch regressions and structural issues
- **After merging pull requests** — Verify no files were corrupted
- **During skill development** — Run after each stream to validate acceptance criteria
- **Before shipping a release** — Full regression suite as a smoke test

## CI/CD Integration

To run tests in CI/CD:
```bash
#!/bin/bash
set -e
cd Dossier
DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v --tb=short
```

If any test fails, the script exits with non-zero status.

## Interpreting Test Failures

### Example: `test_grade_values_are_valid FAILED`
```
Invalid grade values:
  eval-acme-2026-04-15.md: 'B-' (expected one of {'A', 'B+', 'B', 'C', 'D', 'F'})
```
**Fix:** Edit eval-acme-2026-04-15.md, change `grade: B-` to `grade: B`.

### Example: `test_skill_zip_contains_exactly_two_files FAILED`
```
Expected 2 files, found 3: ['SKILL.md', 'scoring-guide.md', 'extra.md']
```
**Fix:** Repack dossier.skill; ensure only SKILL.md and scoring-guide.md are at the root level of the ZIP.

### Example: `test_no_notion_as_primary_source FAILED`
```
Found FORBIDDEN_PATTERNS outside conditional context:
  Line 847: 'Pull from Notion' in: Pull from Notion for company names...
```
**Fix:** Edit SKILL.md line 847, add context like "if notion.enabled" or "optional Notion sync".

## Test Statistics

Current test suite:
- **Total tests:** 47
- **Fast execution:** < 5 seconds (no external calls)
- **Coverage areas:** 6
  - Package integrity: 5 tests
  - Skill structure: 12 tests
  - Anti-patterns: 2 tests
  - Vault schema: 8 tests
  - Vault files: 14 tests
  - Scoring guide: 4 tests

## Maintenance

Tests should be reviewed when:
1. **SKILL.md changes** — May need to adjust test_skill_structure.py or test_antipatterns.py
2. **Frontmatter schema changes** — Update test_vault_schema.py with new/removed fields
3. **New required files added** — Update test_vault_files.py
4. **Known regressions fixed** — Add anti-pattern test to prevent re-emergence

## Questions?

See `CLAUDE.md` for operating contract and principles.
