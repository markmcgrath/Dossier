---
type: plan
feature: test-suite-hardening
status: draft
created: 2026-04-22
author: claude
tags: [tests, ci, packaging, release-readiness]
related: "[[09-release-hardening-execution]], [[13-quality-audit-remediation]]"
---

# Plan 16 — Test Suite Hardening

## Problem

A review surfaced four issues in the open-source repo's test suite and CI:

1. `tests/test_package.py` calls `pytest.fail(...)` without importing `pytest`, so the BadZipFile branch raises `NameError` instead of a clean test failure.
2. `tests/test_skill_structure.py` uses `pytest.skip(...)` for many checks that should now be hard assertions, weakening CI as a release gate.
3. `tests/README.md` describes a CI command (`pytest tests/ -v --tb=short`) that does not match the actual workflow command (`python -m pytest tests/ -v`), and refers to "all three checks are required" without enumerating them.
4. The package tests prove the ZIP is valid and contains required entries, but never prove the packaged content matches the on-disk source under `skill/`. A stale or partial repack would pass CI silently.

The first three are small, low-risk corrections. The fourth is a real durability gain — currently the only thing keeping `dossier.skill` and `skill/` in sync is contributor discipline.

---

## Verification of Each Recommendation

Before adopting these recommendations as written, the current state was checked. Findings:

### Change 1 — `pytest.fail` without import (CONFIRMED)

`tests/test_package.py` line 21 calls `pytest.fail(...)` inside `except zipfile.BadZipFile`. The file's only import is `zipfile`. The branch is currently unreachable in normal runs (the ZIP is valid) but would mask the real failure with a `NameError` if it ever fires.

**Fix is one line.** No risk.

### Change 2 — Skip-to-assert conversion (PARTIALLY CONFIRMED, NEEDS NUANCE)

The recommendation treats all skips uniformly. Reality is bimodal. With the current `dossier.skill`, `pytest tests/test_skill_structure.py -v` produces:

- **10 PASS** — the section is present, the skip guard never fires. Examples: Content Trust Boundary, Mode 0, all numbered modes, Pipeline State, vault-first principles, frontmatter `outcome:` and `legitimacy:`, Mode 12, Mode 13, Mode 2.1.
- **3 SKIP** — the section is genuinely missing today:
  - `test_gate_pass_rule_is_prominent` — "Gate-Pass Rule" string not in `skill/SKILL.md`.
  - `test_bias_caveat_in_mode_1` — "Bias Caveat" not in `skill/SKILL.md`. Plan 13 (`13-quality-audit-remediation.md`) adds it to `mode1-offer-evaluator.md` (a *reference file*), not SKILL.md. The test reads SKILL.md only.
  - `test_all_config_keys_documented` — `redact_comp` and `scoring_weights` not in `skill/SKILL.md` (`gmail_allow_domains`, `gmail_deny_domains`, `target_companies` are present).

**Implication:** Removing skip guards from the 10 currently-passing tests is safe and tightens the gate. Removing them from the 3 currently-skipping tests breaks CI immediately unless the missing content is added first or the assertion is rescoped to also check reference files.

This plan splits the change accordingly.

### Change 3 — Docs/CI drift (CONFIRMED)

`tests/README.md` lines 109–114 say:

- "runs `pytest tests/ -v --tb=short` on a Python matrix" — actual workflow runs `python -m pytest tests/ -v` (no `--tb=short`).
- "All three checks are required to pass" — there are three required checks in the matrix sense (`test (3.11)`, `test (3.12)`, `pii-scan`), but the README never names them. The original recommendation says "two jobs" — that's also true (`test`, `pii-scan`) and the README is ambiguous about which framing it means. The plan resolves this by enumerating both.

**Fix is text-only.** No risk.

### Change 4 — Artifact/source parity (CONFIRMED — and current state is in parity)

A one-off byte-comparison between `dossier.skill` ZIP entries and `skill/` source files was run in advance of writing this plan. Result: zero mismatches across all 16 entries (15 references + SKILL.md). So the test would pass on the current commit. The value is forward-looking — preventing the next stale repack from shipping.

The conftest already provides both fixtures needed for this: `skill_md` (ZIP-packed SKILL.md) and `skill_md_source` (on-disk `skill/SKILL.md`). The new test mostly needs to walk the references directory and compare each entry.

The recommendation also asks for a documented "rebuild package" command. `CONTRIBUTING.md` currently says "Repack `dossier.skill` from the updated `skill/` folder" without a one-liner. The actual repack is performed by an external skill packager (`skill-creator`). This plan adds a one-line invocation example to CONTRIBUTING.md.

---

## Gaps and Assumptions Questioned

- **The recommendation says "two jobs (`test`, `pii-scan`)" but the matrix produces three checks.** Both framings are defensible; the plan documents both explicitly so future readers don't re-litigate this.
- **The recommendation suggests a `REQUIRED_SECTIONS = True` constant pattern.** That pattern is overkill for a binary release-readiness flag. The plan instead removes guards entirely from currently-passing tests (the simpler form) and uses explicit `pytest.skip(... reason="deferred to plan N", strict=False)` for genuinely deferred work.
- **The recommendation's "skill" path naming assumes the open-source layout.** The main vault uses `skill-update/` for editing; the open-source mirror uses `skill/`. The conftest's `skill_md_source` fixture already handles both. This plan changes only the open-source repo (the recommendation's clear target).
- **The recommendation does not mention propagating to the main vault.** That's correct — these are CI/test changes targeting the public repo only. The main vault `tests/` directory has `test_package.py` (also without `import pytest`) and `test_skill_structure.py` (different content from open-source). Per CLAUDE.md propagation rules, plans propagate; runtime test files in the main vault that aren't in the propagation list don't. This plan asks Sonnet to also fix the same one-line `import pytest` bug in the main vault `tests/test_package.py` since the bug is the same and the main vault is what the user actually runs locally — but explicitly does NOT touch the main vault `test_skill_structure.py` (different shape, different content, out of scope).
- **The recommendation's expected impact ("8.2 → 9.1–9.4") is a confidence claim with no benchmark.** Drop it from the plan; it's not actionable.

---

## Plan Number

This is plan 16. Plans 14 and 15 are recently drafted (lead-pulse dedup, recruiter inbox broadening). Sequence is preserved.

---

## Streams

Three streams. P0 ships same day; P1 ships within a sprint.

| Stream | Name | Priority | Est. effort | Depends on |
|--------|------|----------|-------------|------------|
| A | Quick fixes (import + docs) | P0 | 30 min | — |
| B | Skill-structure assertion tightening | P1 | 60–90 min | A |
| C | Package parity gate + repack docs | P1 | 60–90 min | A |

Streams B and C are independent of each other. Either can run after A completes.

---

## Stream A — Quick Fixes (P0, ~30 min)

### A.1 — Fix `pytest.fail` import in `open-source/tests/test_package.py`

**File:** `open-source/tests/test_package.py`

Add `import pytest` at the top of the imports block. Result:

```python
"""
Tests for ZIP package integrity of dossier.skill.
"""
import zipfile

import pytest
```

Leave the rest of the file unchanged. The existing `pytest.fail(...)` call at line 21 will then resolve correctly.

**Acceptance:**

- `import pytest` present in `open-source/tests/test_package.py`.
- Running `python -c "import ast; ast.parse(open('open-source/tests/test_package.py').read())"` succeeds.
- Manual sanity check: temporarily replace `skill_zip.testzip()` with `raise zipfile.BadZipFile("synthetic")` in a scratch copy and confirm the test reports a clean `Failed: dossier.skill is not a valid ZIP file: synthetic`, not a `NameError`. Revert after verifying.

### A.2 — Same fix in main vault `tests/test_package.py`

**File:** `tests/test_package.py` (main vault)

Same one-line addition. The main vault test file is what the user runs locally; the bug is identical.

**Acceptance:** `import pytest` present. No other changes.

### A.3 — Reconcile `open-source/tests/README.md` CI section with actual workflow

**File:** `open-source/tests/README.md`, lines 107–114 (the "CI/CD Integration" section).

Replace the existing text with:

```markdown
## CI/CD Integration

Tests run on every push and pull request to `main` via `.github/workflows/ci.yml`. The workflow defines two jobs that produce three required status checks:

- **`test`** (matrix on Python 3.11 and 3.12) — runs `python -m pytest tests/ -v` with `DOSSIER_VAULT` set to the workspace root. The matrix produces two checks: `test (3.11)` and `test (3.12)`.
- **`pii-scan`** — runs `python .github/scripts/pii_scan.py` to block commits containing high-confidence PII or secret patterns.

All three checks (`test (3.11)`, `test (3.12)`, `pii-scan`) must pass before a PR can merge to `main`. See branch protection settings in the repo for enforcement.

> **Canonical source:** `.github/workflows/ci.yml` is authoritative. If this README and the workflow disagree, the workflow wins. Update this section in the same PR as any workflow change.
```

**Acceptance:**

- Test command in README exactly matches `.github/workflows/ci.yml` (currently `python -m pytest tests/ -v`).
- Job names and check names in README exactly match the workflow.
- The "canonical source" callout is present.
- Run `grep -c '\-\-tb=short' open-source/tests/README.md` — must return 0.

---

## Stream B — Skill-Structure Assertion Tightening (P1, ~60–90 min)

### B.1 — Remove dead skip guards from currently-passing tests

**File:** `open-source/tests/test_skill_structure.py`

For each test in this list, the section is present in the current `skill/SKILL.md` and the skip guard never fires. Remove the guard so a future regression that deletes the section fails CI loudly:

| Test | Current skip guard | Action |
|---|---|---|
| `test_content_trust_boundary_exists` | "Content Trust Boundary not yet added" | Remove guard, keep both assertions |
| `test_mode_0_health_check_exists` | "Mode 0 not yet added" | Remove guard, keep keyword assertion |
| `test_pipeline_state_reading_section_exists` | "Pipeline State not yet added" | Replace skip with `assert has_section, ...` |
| `test_frontmatter_template_has_outcome` | "outcome: not in template" | Replace skip with `assert "outcome:" in skill_md, ...` |
| `test_frontmatter_template_has_legitimacy` | "legitimacy: not in template" | Replace skip with `assert "legitimacy:" in skill_md, ...` |
| `test_mode_12_batch_pipeline_exists` | "Mode 12 not implemented" | Replace skip with `assert "Mode 12" in skill_md or "Batch Pipeline" in skill_md.lower(), ...` |
| `test_mode_13_calibration_exists` | "Mode 13 not implemented" | Replace skip with `assert "Mode 13" in skill_md or "Calibration Report" in skill_md.lower(), ...` |
| `test_portal_scan_submode_exists` | "Mode 2.1 not implemented" | Replace skip with `assert "Mode 2.1" in skill_md or "Portal Scan" in skill_md, ...` |
| `test_all_modes_exist` | Skip if any of Mode 1–13 or Mode 2.1 missing | Replace with `assert not missing, f"Modes missing from SKILL.md: {missing}"` |

**Pattern for assertion-replacing-skip:**

```python
def test_mode_12_batch_pipeline_exists(skill_md):
    """Verify Mode 12 (Batch Pipeline) section exists."""
    has_section = "Mode 12" in skill_md or "batch pipeline" in skill_md.lower()
    assert has_section, "Mode 12 (Batch Pipeline) missing from SKILL.md"
```

**Do not touch** `test_vault_first_general_principles` — it already has no skip guard.

**Acceptance:**

- After edits, all 10 listed tests still PASS (not SKIP).
- `pytest tests/test_skill_structure.py -v` shows `9 passed, 3 skipped` (the 3 active skips remain — handled in B.2).
- `grep -c "pytest.skip" open-source/tests/test_skill_structure.py` is 3, not 9.

### B.2 — Document the 3 remaining active skips

**File:** `open-source/tests/test_skill_structure.py`

These three tests genuinely skip today because the content is missing from `skill/SKILL.md`:

- `test_gate_pass_rule_is_prominent`
- `test_bias_caveat_in_mode_1`
- `test_all_config_keys_documented`

Do **not** convert these to hard asserts in this stream — that would break CI. Instead:

1. Update each skip's reason string to point to the *current* tracking plan, not the historical one. Specifically:
   - `test_gate_pass_rule_is_prominent` → "Gate-Pass Rule section not present in `skill/SKILL.md`. Tracked in plan 13 (quality audit remediation) Stream A."
   - `test_bias_caveat_in_mode_1` → "Bias Caveat is being added to `references/mode1-offer-evaluator.md` per plan 13 Stream A.2, not to SKILL.md. This test will be retired or rescoped when plan 13 ships — see plan 16 follow-up note."
   - `test_all_config_keys_documented` → "Config keys `redact_comp` and `scoring_weights` not yet documented in `skill/SKILL.md`. Tracked in plan 13 Stream C (config schema work). `gmail_allow_domains`, `gmail_deny_domains`, `target_companies` are already present."

2. Add a short module-level docstring at the top of `test_skill_structure.py` listing the three deferred items and the plan that resolves each, so a future reader does not have to grep skip reasons.

**Acceptance:**

- All three skip reasons point to plan 13 (or its successor) by name.
- Module docstring lists the three deferred items and resolution plan.
- Test count unchanged: `pytest tests/test_skill_structure.py` reports the same pass/skip ratio as before B.2.

### B.3 — Follow-up note for plan 13

**File:** `features/plan/13-quality-audit-remediation.md` and `open-source/features/plan/13-quality-audit-remediation.md` (both copies)

Add a short note at the bottom of plan 13 (under a new "## Cross-references" section if none exists):

```markdown
## Cross-references

- Plan 16 (test-suite hardening) defers conversion of `test_bias_caveat_in_mode_1`, `test_gate_pass_rule_is_prominent`, and `test_all_config_keys_documented` to hard assertions until this plan ships. When this plan completes, revisit those three tests in `open-source/tests/test_skill_structure.py` and either (a) convert the skip to an assert, or (b) rescope the assertion to read the relevant reference file rather than `SKILL.md`.
```

**Acceptance:** Section appears in both copies of plan 13.

---

## Stream C — Package Parity Gate + Repack Docs (P1, ~60–90 min)

### C.1 — Add `tests/test_skill_package_parity.py`

**File (new):** `open-source/tests/test_skill_package_parity.py`

Create a new test file that compares every entry in the `dossier.skill` ZIP against its corresponding source file in `skill/`. Use the existing `vault_path` and `skill_zip` fixtures from conftest.

```python
"""
Parity tests — every file inside dossier.skill must match the on-disk source
under skill/. Catches stale repacks where source was edited but the ZIP was
not regenerated, or vice versa.
"""
from pathlib import Path

import pytest


def _normalize(b: bytes) -> bytes:
    """Normalize line endings so CRLF vs LF differences do not flag parity."""
    return b.replace(b"\r\n", b"\n")


def test_zip_entries_match_source_files(skill_zip, vault_path):
    """Every entry in dossier.skill must exactly match the file under skill/."""
    src_root = vault_path / "skill"
    assert src_root.is_dir(), f"skill/ source directory not found at {src_root}"

    mismatches = []
    for name in skill_zip.namelist():
        if not name.startswith("skill/"):
            mismatches.append((name, "ZIP entry not under skill/ prefix"))
            continue
        rel = name[len("skill/"):]
        src_file = src_root / rel
        if not src_file.exists():
            mismatches.append((name, "no matching source file under skill/"))
            continue
        zip_bytes = skill_zip.read(name)
        src_bytes = src_file.read_bytes()
        if _normalize(zip_bytes) != _normalize(src_bytes):
            mismatches.append(
                (name, f"content differs (zip={len(zip_bytes)}B, src={len(src_bytes)}B)")
            )

    assert not mismatches, (
        "dossier.skill is out of sync with skill/ source. Repack required.\n"
        + "\n".join(f"  - {n}: {why}" for n, why in mismatches)
    )


def test_source_files_all_present_in_zip(skill_zip, vault_path):
    """Every file under skill/ must appear in dossier.skill (no orphans on disk)."""
    src_root = vault_path / "skill"
    assert src_root.is_dir(), f"skill/ source directory not found at {src_root}"

    src_entries = set()
    for f in src_root.rglob("*"):
        if f.is_file():
            rel = f.relative_to(src_root).as_posix()
            src_entries.add(f"skill/{rel}")

    zip_entries = set(skill_zip.namelist())

    missing_from_zip = src_entries - zip_entries
    extra_in_zip = zip_entries - src_entries

    assert not missing_from_zip, (
        "Source files under skill/ are missing from dossier.skill: "
        f"{sorted(missing_from_zip)}. Repack required."
    )
    assert not extra_in_zip, (
        "dossier.skill contains entries with no source file under skill/: "
        f"{sorted(extra_in_zip)}. Either delete the entry or add the source file."
    )
```

**Acceptance:**

- New file present at `open-source/tests/test_skill_package_parity.py`.
- `DOSSIER_VAULT="$(pwd)" python -m pytest tests/test_skill_package_parity.py -v` passes against the current commit (verified ahead of plan: zero mismatches in current state).
- Synthetic regression test: edit one byte in a `skill/references/*.md` file (don't commit), re-run the test, confirm it FAILS with a clear "content differs" message naming the file. Revert.
- Synthetic regression test 2: rename one file in `skill/references/`, re-run, confirm it FAILS with "Source files ... missing from dossier.skill". Revert.

### C.2 — Update `open-source/tests/README.md` test inventory

**File:** `open-source/tests/README.md`

Add a bullet to the "What Tests Cover" list (lines 6–14):

```markdown
- **Package parity** (`test_skill_package_parity.py`): Every entry in `dossier.skill` must match the on-disk source under `skill/`. Catches stale repacks.
```

Add the file to the "Test Organization" tree diagram. Increment the "Total tests" count in the "Test Statistics" section and add a "Package parity: 2 tests" line.

**Acceptance:**

- Bullet present in the cover list.
- File listed in the tree.
- Statistics section updated to reflect the additional 2 tests.

### C.3 — Add one-line repack command to `CONTRIBUTING.md`

**File:** `open-source/CONTRIBUTING.md`

In the "Skill Development Workflow" section, replace step 4 ("Repack `dossier.skill` from the updated `skill/` folder.") with:

```markdown
4. Repack `dossier.skill` from the updated `skill/` folder. The exact command depends on your packager — for the skill-creator tool included with Anthropic's Claude skill workflow:

   ```bash
   python -m scripts.package_skill /path/to/skill/ /tmp/out/ \
     && mv /tmp/out/skill.skill ./dossier.skill
   ```

   If you use a different packager, ensure the resulting ZIP contains `skill/SKILL.md` and `skill/references/*.md` (matching the on-disk layout). The new `tests/test_skill_package_parity.py` test will fail in CI if the repack is stale or mis-shaped.
```

**Acceptance:**

- A one-line repack command appears in `CONTRIBUTING.md`.
- The instruction explicitly references `tests/test_skill_package_parity.py` so future contributors find it.

### C.4 — Surface parity check in PR checklist

**File:** `open-source/CONTRIBUTING.md`, "PR checklist" block.

Add a checkbox between the existing `[ ] open-source/ copy is current (no PII)` and `[ ] PII scan clean: ...` entries:

```markdown
- [ ] `dossier.skill` repacked from `skill/` if either changed (`pytest tests/test_skill_package_parity.py` passes)
```

**Acceptance:** Checkbox added in the right position.

---

## Sequencing

```
Day 1 (~30 min):       Stream A (A.1, A.2, A.3) — ship same day, low risk
Day 2 (~60–90 min):    Stream B (B.1, B.2, B.3) — tightens existing gates
Day 2 or 3 (~60–90 min): Stream C (C.1–C.4) — adds new gate

Streams B and C are independent. Either order works after A.
```

**Total estimated effort:** 2.5–3.5 hours of focused work.

---

## Validation Checklist (post-implementation)

Each item must be true before this plan is marked done.

- [ ] `import pytest` present in `open-source/tests/test_package.py` and `tests/test_package.py` (main vault).
- [ ] `open-source/tests/README.md` CI section command matches `.github/workflows/ci.yml` exactly.
- [ ] `open-source/tests/README.md` enumerates the three required checks by name.
- [ ] No `--tb=short` references in `open-source/tests/README.md` (until/unless the workflow actually adds it).
- [ ] In `open-source/tests/test_skill_structure.py`, only 3 `pytest.skip(...)` calls remain (the active deferrals).
- [ ] All 10 currently-passing skill_structure tests still pass; none flipped to skip.
- [ ] `open-source/tests/test_skill_package_parity.py` exists and passes.
- [ ] Synthetic mismatch test (edit a source file, do not repack) causes parity test to FAIL with a useful message.
- [ ] `CONTRIBUTING.md` includes a one-line repack command and the new PR checkbox.
- [ ] Plan 13 (both copies) has the cross-reference note.
- [ ] Full suite passes locally: `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v` from `open-source/`.

---

## Risks and Open Questions

- **B.1 risk: a skip guard removal that surprises a future contributor.** Mitigation: each removed guard becomes a clearly-named `assert ..., "<descriptive message>"`. Failure mode shifts from silent skip to loud failure with a pointer to the missing section.
- **C.1 risk: line-ending differences across platforms.** Mitigated by `_normalize()` which collapses CRLF to LF before comparison. If a future packager introduces other normalization (BOM, trailing newline trimming), extend `_normalize`.
- **C.1 open question: should the parity test also enforce a sorted-and-canonical ZIP?** Out of scope for this plan. The current test is a content-equality check, not a determinism check. Determinism (reproducible builds) would be a separate, larger plan.
- **B.2 follow-up coupling:** The note added to plan 13 creates a dependency: when plan 13 ships, someone must come back to `test_skill_structure.py` and either tighten or rescope the three deferred tests. Explicit cross-reference is the mitigation; any further automation is overkill.

---

## Out of Scope

- Adding `--tb=short` or other CLI flags to the workflow. The recommendation only flagged the doc/CI mismatch; whichever side moves to align is fine, and "docs catch up to workflow" is the cheaper change.
- Changing the workflow's matrix shape, timeout, or concurrency.
- Touching the main vault `test_skill_structure.py` (different file, different scope, different test set).
- Adding a `Makefile` or formal build script. The one-line repack command in `CONTRIBUTING.md` is sufficient until contributor friction proves otherwise.
- Branch protection settings on GitHub — those live outside the repo and require admin access.

---

## Files Touched

Open-source repo (`open-source/`):

- `tests/test_package.py` (A.1)
- `tests/README.md` (A.3, C.2)
- `tests/test_skill_structure.py` (B.1, B.2)
- `tests/test_skill_package_parity.py` (C.1, new file)
- `CONTRIBUTING.md` (C.3, C.4)
- `features/plan/13-quality-audit-remediation.md` (B.3)
- `features/plan/16-test-suite-hardening.md` (this plan, propagated)

Main vault:

- `tests/test_package.py` (A.2 only)
- `features/plan/13-quality-audit-remediation.md` (B.3)
- `features/plan/16-test-suite-hardening.md` (this plan, original)

No changes to: `dossier.skill`, `skill/SKILL.md`, `skill/references/*`, any vault content under `evals/`, `outreach/`, `cv.md`, `profile.md`, or `config.md`.
