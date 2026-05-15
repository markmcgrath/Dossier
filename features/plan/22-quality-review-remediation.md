# Plan 22 — Quality Review Remediation

**Source review:** [`reviews/2026-05-14-quality-review.md`](../../reviews/2026-05-14-quality-review.md)
**Trigger:** ISO/IEC 25010-style quality review (2026-05-14) graded the repo **A- / 91**. Remediating the named gaps targets a solid A.
**Status:** Planned
**Owner:** markmcgrath

---

## Context

The review found four targeted improvements (P1, two P2s, one P3) and one explicit no-op (P3 SBOM). None require broad rewrites. The weakest scored category is portability/reproducibility (3.8/5) — caused by missing `pyproject.toml`, no `.python-version`, and a CONTRIBUTING/README setup section that lists only 2 of 4 dependencies. Two assurance gaps follow: semantic LLM-output review is documented (`tests/semantic-review-checklist.md`) but not wired into the release ritual, and 8 conditional skips across the test suite have no single accountability surface.

This plan addresses all five P1/P2/P3 recommendations and turns the explicit no-op into a documented deferral with re-trigger criteria so it cannot become invisible debt.

---

## Streams

| Stream | Recommendation | Priority | Subagent | Effort |
|---|---|---|---|---|
| A | Environment reproducibility (`pyproject.toml` + `.python-version`) | P1 | Sonnet | ~60 min |
| B | Skipped-test exit-criteria table | P2 | Sonnet | ~45 min |
| C | Semantic review as pre-tag release ritual | P2 | inline | ~20 min |
| D | Contributor task matrix in CONTRIBUTING.md | P3 | inline | ~15 min |
| E | SBOM / action-pinning deferral note | P3 | inline | ~10 min |

User scope choice (recorded): **Stream A uses the lighter `pyproject.toml` + `.python-version` path**, leaving `requirements.txt` in place as the CI install target. No lockfile, no new tooling.

---

## Stream A — Environment Reproducibility (P1)

**Goal:** Declare project metadata, supported Python version, and a complete dependency surface so contributors can reproduce the CI environment without guessing.

### Files

| Path | Action |
|---|---|
| `pyproject.toml` | **New.** `[project]` metadata, `requires-python = ">=3.12"`, `[project.optional-dependencies] dev = [...]` mirroring `requirements.txt`. Add `[tool.pytest.ini_options]` if pytest config currently lives implicitly. |
| `.python-version` | **New.** Single line: `3.12`. |
| `requirements.txt` | **Edit.** Add a header comment pointing to `pyproject.toml` as the source of truth. Keep deps unchanged so CI is unaffected. |
| `CONTRIBUTING.md` (lines 19–30) | **Edit.** Replace the bare `pytest` invocation with venv setup + `pip install -e ".[dev]"` (or `pip install -r requirements.txt`) + the existing `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v` invocation. State Python 3.12 requirement. |
| `README.md` (lines 270–280) | **Edit.** Replace `pip install pytest pyyaml` (which omits `jsonschema` and `tomli`) with `pip install -r requirements.txt` or `pip install -e ".[dev]"`. Match CONTRIBUTING.md venv guidance. |
| `tests/README.md` | **Edit if necessary.** Confirm the documented install command matches the new flow. |

### Subagent prompt (Sonnet)

Use a `general-purpose` agent with `model: sonnet`. Brief it with:

- Current `requirements.txt` contents (pytest, pyyaml, tomli conditional, jsonschema).
- The CI Python version is 3.12 across all four workflow jobs (`ci.yml:23,49,104`, `release.yml:67`).
- The decision to keep `requirements.txt` as CI install target (do **not** rewrite `.github/workflows/ci.yml`).
- The expected `pyproject.toml` skeleton: `[project]` with `name = "dossier"`, `version = "0.0.0"` (or current CHANGELOG version), `requires-python = ">=3.12"`, `[project.optional-dependencies] dev`.
- The exact CONTRIBUTING.md and README.md lines to edit.
- Validation: after edits, run `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` and `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v` — expect 176 passed / 4 skipped.

### Acceptance criteria

- `pyproject.toml` parses cleanly with `tomllib`.
- `pip install -e ".[dev]"` installs all four dependencies in a fresh venv.
- All existing tests still pass (176 / 4 skipped) — `pyproject.toml` is metadata-only, not a breaking change.
- `CHANGELOG.md` gains an `[Unreleased]` entry under `Added`.

---

## Stream B — Skipped-Test Exit Criteria (P2)

**Goal:** Single source of truth for every skipped test, why it is skipped, what unblocks it, and whether it gates a release.

### Inputs (already audited)

8 skip sites identified:

| File:Line | Skip Type | Reason | Exit Criteria |
|---|---|---|---|
| `test_config_contract.py:219` | fixture | `config.template.md` not in vault layout | Vault contains `config.template.md` (always true for open-source vault) |
| `test_schema_validation.py:16` | module | `jsonschema` not installed | `jsonschema` installed (declared in `requirements.txt`); skip is environment-conditional |
| `test_docs_consistency.py:194` | parametrized | doc not in vault layout | Per-doc; conditional on vault contents |
| `test_docs_consistency.py:230` | parametrized | doc not in vault layout | Per-doc; conditional on vault contents |
| `test_vault_files.py:199` | fixture | no stories file present | Vault contains `stories.md` or `stories.template.md` |
| `test_skill_structure.py:84–87` | hard | Gate-Pass Rule placement (plan 13 Stream A) | Plan 13 Stream A completes Gate-Pass Rule wording in `skill/SKILL.md` |
| `test_skill_structure.py:94–98` | hard | Bias Caveat moved to mode-1 reference doc (plan 13 Stream A.2 / plan 16 follow-up) | Test retired or rescoped after plan 13 ships |
| `test_skill_structure.py:124–129` | hard | Config keys not yet documented (plan 13 Stream C) | Plan 13 Stream C documents the 5 named config keys in `skill/SKILL.md` |

### Files

| Path | Action |
|---|---|
| `tests/SKIPPED_TESTS.md` | **New.** Table with columns: `Test`, `File:Line`, `Skip Type`, `Reason`, `Exit Criteria`, `Release Blocker?`. One row per skip site. Brief intro paragraph explaining when to update the table. |
| `tests/README.md` | **Edit.** Add a sentence under "Skips" linking to `SKIPPED_TESTS.md` as the canonical accountability surface. |
| `ROADMAP.md` | **Edit.** Replace any inline skipped-test discussion with a link to `tests/SKIPPED_TESTS.md`. |
| `features/plan/13-quality-audit-remediation.md` | **Edit (if low-touch).** Add a "Related: tests/SKIPPED_TESTS.md tracks blocked tests for this plan" note. Otherwise leave untouched. |

### Subagent prompt (Sonnet)

Use a `general-purpose` agent with `model: sonnet`. Brief it with:

- The 8 skip sites listed above (verbatim file:line and reason strings).
- Open `tests/test_skill_structure.py:84–129` directly; that file contains the most load-bearing skips (plan 13 dependencies) — paraphrase the in-file skip messages into the `Reason` and `Exit Criteria` columns.
- For each row, judge `Release Blocker?` as **No** by default unless the skip masks a regression in a release-critical guarantee. Mark the three plan-13 skips as **No** (the underlying behavior is verified by other tests; the skip is on the assertion form, not the behavior).
- Output is a single new file: `tests/SKIPPED_TESTS.md`.

### Acceptance criteria

- Every skip surfaced by `pytest -v -rs` appears in the table.
- Adding a new skip without updating the table fails a future doc-consistency test (note this as a follow-up; do not implement the test in this stream).

---

## Stream C — Semantic Review as Release Ritual (P2)

**Goal:** Make the manual semantic review unavoidable before tagging, without turning it into a brittle CI gate.

### Files

| Path | Action |
|---|---|
| `CONTRIBUTING.md` (lines 139–148, "Tagging a Release") | **Edit.** Insert a new step between the routing-evals optional step and the `git cliff` preview: **"Run semantic review: walk `tests/semantic-review-checklist.md` end-to-end against the three golden artifacts in `examples/golden/`. All five sections must pass. Record completion in the release PR description."** Mark this as required, not optional. |
| `HARDENING.md` (§7 Test surface, lines 145–156) | **Edit.** Add a sentence: "Semantic review is required for tagged releases — see CONTRIBUTING.md release section. The semantic-review-checklist.md run is the binding gate, not a CI check." |
| `tests/semantic-review-checklist.md` | **Edit (optional).** Add a sign-off footer line: `_Last run: vX.Y.Z by <maintainer> on YYYY-MM-DD_`. Cosmetic but useful. |

### Acceptance criteria

- CONTRIBUTING.md release section names semantic-review as a required step.
- HARDENING.md no longer reads as if semantic review is purely advisory.

---

## Stream D — Contributor Task Matrix (P3)

**Goal:** Make it obvious which subset of checks each change type triggers.

### Files

| Path | Action |
|---|---|
| `CONTRIBUTING.md` (after the PR checklist, before the conventional-commits section ~line 80) | **Edit.** Insert the review's task matrix as a new subsection titled "Which checks for which changes". |

### Content to insert (verbatim from the review's P3 table, lightly expanded for accuracy)

```markdown
### Which checks for which changes

| Change type | Required checks |
|---|---|
| `skill/` source | full test suite + `bash .github/scripts/build_skill.sh` (parity) + semantic-review checklist before release |
| `schemas/` or `examples/` | full test suite (includes `test_schema_validation.py` when `jsonschema` is installed) |
| Docs only (`README.md`, `CONTRIBUTING.md`, etc.) | `test_docs_consistency.py` + CHANGELOG entry |
| `.github/workflows/` or release scripts | full test suite + manual review of `verify_skill_artifact.py` output on a draft release |
| `tests/` only | full test suite + update `tests/SKIPPED_TESTS.md` if skip surface changes |
```

### Acceptance criteria

- New subsection present, scannable, and consistent with existing CI required-checks list in HARDENING.md §1.

---

## Stream E — SBOM / Action-Pinning Deferral (P3)

**Goal:** Convert the review's "no immediate action" into a documented deferral with explicit re-trigger criteria.

### Files

| Path | Action |
|---|---|
| `HARDENING.md` (Operational Patterns section, ~line 195) | **Edit.** Append a short subsection: "Deferred: SBOM and third-party action SHA pinning". State the current first-party-only posture, and the three triggers from the review (non-first-party action added; registry publication; runtime dependencies added). |
| `ROADMAP.md` | **Edit.** Add a "Deferred (criteria-gated)" entry pointing to the HARDENING.md subsection. |

### Acceptance criteria

- A future contributor proposing a non-first-party Action sees the deferral note and the triggers before merging.

---

## Execution Order

1. **Stream A** — Sonnet subagent. Stream A is the most invasive (new metadata file, README/CONTRIBUTING edits). Land first so subsequent docs reference the new install flow.
2. **Stream B** — Sonnet subagent. Independent of A.
3. **Streams C, D, E** — inline edits, no subagent. Land as a single commit each, or bundle into one PR labeled `docs: review remediation`.

Streams A and B can run in parallel via two Sonnet subagents on **separate worktrees** — they edit different files and do not collide. (Per memory: avoid two agents sharing a working tree.) If executing sequentially in one tree, finish A first, then B.

---

## Verification

End-to-end checks after all streams land:

1. **Test suite** — `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v` reports **176 passed, 4 skipped** (same baseline as the review).
2. **Build parity** — `bash .github/scripts/build_skill.sh` passes content-match.
3. **PII scan** — `python .github/scripts/pii_scan.py` reports clean.
4. **`pyproject.toml` parses** — `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`.
5. **Fresh-venv install** — in a clean venv: `pip install -e ".[dev]"` then `python -m pytest tests/ -v`. Should succeed with the same 176/4 result.
6. **Skipped-test table coverage** — `pytest --collect-only -q | grep -c 'skip'` (rough count) matches the row count in `tests/SKIPPED_TESTS.md`.
7. **Doc cross-links** — manually verify CONTRIBUTING → semantic-review-checklist, HARDENING → SKIPPED_TESTS.md, ROADMAP → HARDENING deferral.
8. **CHANGELOG** — `[Unreleased]` entries cover all five streams under `Added` / `Changed` / `Docs`.

---

## Out of Scope (Explicit)

- **Lockfile / pip-tools / uv.** User selected the lighter pyproject-only path. Revisit if dependency drift causes a CI/local divergence.
- **Multi-version CI matrix.** Review did not ask for it. Adding 3.13 to the matrix is a separate, additive change.
- **SBOM generation, third-party Action SHA pinning.** Documented as deferred in Stream E with explicit re-trigger criteria.
- **Automated dynamic red-team harness for LLM behavior.** Review acknowledges this is the right call to keep manual; Stream C makes the manual ritual binding.
- **Plan 13 completion.** Three skipped tests are gated on plan 13; Stream B documents this without unblocking the underlying plan.

---

## Critical Files Referenced

- `requirements.txt:1–6` — current dep declaration
- `.github/workflows/ci.yml:23,49,104` — Python version pin sites
- `.github/workflows/release.yml:67` — release Python pin
- `CONTRIBUTING.md:19–30` — setup section
- `CONTRIBUTING.md:54–80` — implicit PR matrix
- `CONTRIBUTING.md:130–210` — release workflow
- `README.md:267–280` — running-tests section
- `HARDENING.md:145–156` — §7 test surface
- `HARDENING.md:195–202` — operational patterns
- `tests/README.md` — test taxonomy
- `tests/semantic-review-checklist.md` — manual review rubric (existing)
- `tests/test_skill_structure.py:84–129` — three plan-13 skips
- `tests/test_schema_validation.py:16` — jsonschema module skip
- `examples/golden/` — three regression-anchor artifacts referenced by semantic checklist
