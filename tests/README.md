# Dossier Test Suite

Automated test suite for the Dossier v2 job search skill. Tests verify structural integrity, schema validation, and regression prevention.

## What Tests Cover

- **Package integrity** (`test_package.py`): ZIP file validity, required files, line counts
- **Package parity** (`test_skill_package_parity.py`): Every entry in `dossier.skill` must match the on-disk source under `skill/`. Catches stale repacks.
- **SKILL.md structure** (`test_skill_structure.py`): Required sections, modes, documentation
- **Notion optionality contracts** (`test_antipatterns.py`): Enforces vault-first architecture — no mandatory-Notion phrases, all references conditional, vault-as-source-of-truth affirmed, disabled path documented, Mode 1 saves to vault
- **Config permutations** (`test_config_contract.py`): Validates SKILL.md and config.template.md behavior across four config states: missing, Notion disabled, Notion enabled with missing IDs, Notion enabled with valid IDs
- **Doc consistency** (`test_docs_consistency.py`): Checks that README.md, CLAUDE.md, config.template.md, DATA_CONTRACT.md, and skill/SKILL.md agree on four Notion optionality rules; also flags contradictions
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
DOSSIER_VAULT="$(pwd)" python -m pytest tests/test_antipatterns.py::test_no_mandatory_notion_phrases -v
```

## Test Organization

```
tests/
├── conftest.py                       # Shared fixtures (vault_path, skill_md, eval_files, etc.)
├── test_antipatterns.py              # Notion optionality contract tests
├── test_cc_pattern_parity.py         # Conventional-Commits regex parity between hook and CI
├── test_cliff_config.py              # git-cliff config validation
├── test_commit_msg_hook.py           # Commit-msg hook accepts/rejects subjects correctly
├── test_config_contract.py           # Config-state permutation tests
├── test_dashboard.py                 # dashboard.md Dataview block syntactic checks
├── test_docs_consistency.py          # Cross-doc Notion optionality consistency
├── test_outcome_state_machine.py     # Outcome/status state-machine rules
├── test_package.py                   # ZIP integrity (17-entry frozen list)
├── test_release_workflow_glob.py     # Release workflow tag-glob matching
├── test_routing_evals_parser.py      # Routing-eval test-set parsing
├── test_routing_evals_scoring.py     # Routing-eval scoring logic
├── test_routing_golden.py            # Routing golden-snapshot tests
├── test_scoring_guide.py             # Scoring guide completeness
├── test_skill_package_parity.py      # ZIP ↔ skill/ byte-parity
├── test_skill_structure.py           # SKILL.md sections and modes
├── test_story_tagging.py             # Story-tagging cross-references
├── test_terminal_archival.py         # Terminal-archival rules + cold-detection regression
├── test_vault_files.py               # Required vault files and examples
├── test_vault_schema.py              # Eval frontmatter validation
├── test_schema_validation.py         # Validates example artifacts against schemas/eval.schema.json and schemas/outreach.schema.json (skips if jsonschema not installed)
├── run_tests.sh                      # Convenience wrapper
└── fixtures/
    ├── jd_ghost_job.md               # Ghost job (red flags)
    ├── jd_strong_fit.md              # Strong fit (verified)
    ├── jd_injection_attempt.md       # Prompt injection detection
    └── config/
        ├── config_notion_disabled.md            # Notion explicitly off
        ├── config_notion_enabled_missing_ids.md # Enabled but IDs empty
        └── config_notion_enabled_valid_sample.md # Fully configured
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

Tests run on every push and pull request to `main` via `.github/workflows/ci.yml`. The workflow defines five jobs:

- **`test`** (matrix on Python 3.12) — runs `python -m pytest tests/ -v` with `DOSSIER_VAULT` set to the workspace root. The matrix produces one check: `test (3.12)`. The matrix shape is preserved so additional Python versions can be re-added without renaming the check.
- **`pii-scan`** — runs `python .github/scripts/pii_scan.py` to block commits containing high-confidence PII or secret patterns.
- **`changelog-check`** (PR only) — runs `.github/scripts/changelog_check.sh` to enforce that touching `skill/`, `tests/`, or `dossier.skill` is accompanied by an `[Unreleased]` CHANGELOG entry. Bypass token: `[skip-changelog]`.
- **`conventional-commits`** (PR only) — runs `.github/scripts/check_conventional_commits.sh` to validate that every commit subject in the PR range follows Conventional Commits format. Bypass token: `[skip-cc]`.
- **`skill-parity`** — runs `.github/scripts/build_skill.sh` and exits non-zero if the freshly-built bundle's content drifts from the committed `dossier.skill` (manifest.json excluded).

All five jobs must pass before a PR can merge to `main`. See branch protection settings in the repo for enforcement.

> **Canonical source:** `.github/workflows/ci.yml` is authoritative. If this README and the workflow disagree, the workflow wins. Update this section in the same PR as any workflow change.

## Interpreting Test Failures

### Example: `test_grade_values_are_valid FAILED`
```
Invalid grade values:
  eval-acme-2026-04-15.md: 'B-' (expected one of {'A', 'B+', 'B', 'C', 'D', 'F'})
```
**Fix:** Edit eval-acme-2026-04-15.md, change `grade: B-` to `grade: B`.

### Example: `test_zip_has_no_unexpected_top_level_entries FAILED`
```
ZIP entries do not match expected frozen list.
  Extra:   ['skill/references/extra.md']
  Missing: []
```
**Fix:** Either remove the extra file from `skill/references/` and repack via `bash .github/scripts/build_skill.sh`, or — if the addition is intentional — update `EXPECTED_BUNDLE_ENTRIES` in `tests/test_package.py` to include the new entry. The frozen-list design forces a deliberate, auditable update on every reference-file change.

### Example: `test_no_mandatory_notion_phrases FAILED`
```
Found phrases that imply Notion is mandatory (vault-first violation):
  Line 847: found "pull from notion" in: Pull from Notion for company names...
```
**Fix:** Edit SKILL.md line 847 — either remove the phrase or rewrite as conditional (e.g., "If Notion is configured, pull from Notion for...").

## Test Statistics

- **Total tests:** ~180 (run `python -m pytest tests/ --collect-only -q | tail -1` for the current count; this number is not updated on every PR).
- **Fast execution:** under 2 seconds (no external calls).
- **Coverage areas** (named, not counted, so the list survives PRs that add/remove tests within an area):
  - Notion optionality contracts and config-state permutations
  - Conventional Commits regex parity (hook vs CI script)
  - git-cliff config validation
  - Commit-msg hook accept/reject behavior
  - Dashboard Dataview block syntactic checks
  - Cross-doc consistency (README ↔ SKILL.md ↔ DATA_CONTRACT.md ↔ CLAUDE.md)
  - Outcome/status state-machine rules
  - ZIP package integrity (17-entry frozen list)
  - Release-workflow tag-glob matching
  - Routing-eval test-set parsing and scoring
  - Routing golden-snapshot tests
  - Scoring guide completeness
  - ZIP ↔ skill/ byte-parity
  - SKILL.md structural sections (modes, Content Trust Boundary, Integrity Rules)
  - Story tagging cross-references
  - Terminal archival rules + cold-detection regression
  - Vault files (required directories, example artifacts)
  - Vault frontmatter schema

## Skipped tests

Every `pytest.skip()` site in this suite is tracked in [`SKIPPED_TESTS.md`](SKIPPED_TESTS.md) with file:line, reason, exit criterion, and release-blocker disposition. PRs adding a new skip must add a corresponding row in the same commit. PRs resolving a skip should delete the row. Reconcile by running `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -rs` and matching the "short test summary info" against the table.

## Maintenance

Tests should be reviewed when:
1. **SKILL.md changes**
