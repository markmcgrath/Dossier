---
type: plan
feature: eval-schema-data-hygiene
status: draft
created: 2026-05-05
author: claude
tags: [tests, schema, evals, state-machine, data-hygiene]
related: "[[13-quality-audit-remediation]], [[16-test-suite-hardening]], [[skill-update/references/status-outcome-state-machine]]"
---

# Plan 17 — Eval Schema & Data Hygiene Cleanup

## Problem

Running the full main-vault test suite after plan 16 closed surfaced a cluster of pre-existing schema/data drift. Six `test_vault_schema.py` assertions fail, and one collection error in `test_vault_files.py` is unrelated. None of these were introduced by plan 16; they accumulated from authoring drift in real evals plus an under-specified state for "this eval has been superseded by a re-evaluation."

The failures break into four categories. The decisions below are not all settled — each stream calls out where a design call is required before code can land.

---

## Verification of Each Issue

Each item below was confirmed by running `python -m pytest tests/test_vault_schema.py -v` against the current main vault on 2026-05-05, before drafting this plan.

### Issue 1 — Schema/rubric drift on `B-` (PARTIALLY MITIGATED)

Two evals from late April / early May 2026 use `grade: B-`. The schema (`tests/test_vault_schema.py:VALID_GRADES`) was widened to include `B-` as the immediate fix, but the canonical scoring rubric in `skill-update/references/scoring-guide.md` (lines 113–122) defines bands A, B+, B, C, D, F only — there is no B- band. The schema and rubric now disagree.

**Decision required:**
- **Option A** — Add a B- band to the rubric. Suggested split: `3.40 – 3.49 → B-` carved out of the current C band (`3.00 – 3.49`), or `3.50 – 3.59 → B-` carved from the bottom of B. Update `scoring-guide.md`, `SKILL.md` (line 48: `grade: A | B+ | B | C | D | F`), and `references/file-conventions.md` (line 36 same). Repack.
- **Option B** — Roll back the schema (`VALID_GRADES` minus `B-`) and re-grade the two B- evals to B or C per the canonical bands.

Until decided, the schema is permissive but the rubric is authoritative — Mode 1 will not produce B- on its own; only user-edited evals will use it.

### Issue 2 — `Superseded` status / `superseded` grade (DESIGN DECISION NEEDED)

5 evals from the 2026-05-02 / 2026-05-04 batch use `status: Superseded` (capitalized) and `grade: superseded` (lowercase). Both are non-canonical:

- `Superseded` is not in `VALID_STATUSES` (`Evaluating`, `Applied`, `Interviewing`, `Offer`, `Rejected`, `Passed`, `Offer-Declined`, `Batch-Evaluated`).
- `superseded` is not a real grade — it appears to be a marker, not a score.
- All 5 also have `score: None` and missing `outcome:` field.

This is a recognizable pattern: when a `[Company]` eval is re-evaluated (a newer eval at the same slug + later date is created), the prior eval is "superseded." The state machine does not currently model this — there is no transition for "replaced by a later eval for the same company."

**Decision required (pick one):**
- **Option A — Formalize as a real status.** Add `Superseded` to `VALID_STATUSES` and to the state machine (`status-outcome-state-machine.md`). Define the trigger ("a new eval is authored at the same `[slug]` + later date") and treat as terminal. Drop the `grade: superseded` convention; preserve the original `grade:` and `score:` from the eval that's being replaced (do not blank them).
- **Option B — Use existing terminal archival.** Move superseded evals into `archive/[slug]-v{N}/` per the `terminal-archival.md` reference, leaving only the most recent eval in `evals/`. This avoids a new status but requires a versioning convention for superseded copies.
- **Option C — Reuse `Passed` + `Withdrawn`.** Set `status: Passed`, `outcome: Withdrawn`. Fits the state machine today but loses the "replaced by re-eval" semantics — looks identical to a user-rejected role.

Option A is the cleanest if re-evaluation is a recurring pattern (it appears to be — 4 of the 5 Superseded evals have a successor in `evals/`). Option B is right if the goal is to keep `evals/` clutter-free. Option C is right only if re-evaluation is rare enough to not warrant its own concept.

### Issue 3 — `outcome: Applied` slip (CLEAR BUG)

2 evals from April 2026 have `outcome: Applied`. `Applied` is a status, not an outcome. Per the state machine, when `status: Applied` the correct `outcome:` is `Pending` (until employer responds).

**Fix:** Set `outcome: Pending` on both evals. No design decision; pure data correction.

### Issue 4 — 5 evals missing `score:` and `outcome:` (DEPENDS ON ISSUE 2)

The 5 `Superseded` evals from Issue 2 all have `score: None` (or absent) and no `outcome:` field. Resolution depends on which Option is chosen for Issue 2:

- Option A → preserve original `score:` from the eval being superseded; set `outcome:` per the new state machine row (likely `Withdrawn` or a new `Superseded`-paired outcome).
- Option B → archival removes the eval from the active set; no schema concern.
- Option C → set `score:` to the original value; `outcome: Withdrawn`.

### Issue 5 — `test_example_prep_frontmatter` collection error (NEEDS INVESTIGATION)

`tests/test_vault_files.py::test_example_prep_frontmatter` errors during collection (not failure — the test never ran). Likely a missing fixture or a bad path. Out of scope for the schema work; surface as a small follow-up under Stream D.

---

## Streams

| Stream | Name | Priority | Est. effort | Depends on |
|--------|------|----------|-------------|------------|
| A | Schema/rubric reconciliation (B-) | P1 | 30–60 min | Decision on Option A vs B |
| B | Quick fixes (`outcome: Applied`) | P0 | 10 min | None |
| C | `Superseded` design + data backfill | P1 | 90 min – 3 hr | Decision on Option A/B/C |
| D | `test_example_prep_frontmatter` triage | P2 | 30 min | None |

Stream B can ship the same day. Streams A and C each need a decision call before implementation.

---

## Stream A — Schema/Rubric Reconciliation (P1)

### A.1 — Decide rubric posture

Pick Option A (widen rubric to include B-) or Option B (roll back schema; normalize evals).

### A.2 — If Option A

- Edit `skill-update/references/scoring-guide.md` Grade Conversion table. Suggested band: `3.40 – 3.49 | B- | Marginal — selective only`. Document the cutoff rationale in a one-line note.
- Edit `skill-update/SKILL.md` line 48 (`grade: A | B+ | B | C | D | F` → `grade: A | B+ | B | B- | C | D | F`).
- Edit `skill-update/references/file-conventions.md` line 36 same.
- Repack `dossier.skill`.
- Propagate to open-source per CLAUDE.md.

### A.3 — If Option B

- Revert `VALID_GRADES` in both copies of `tests/test_vault_schema.py` (drop `B-`).
- Re-grade the 2 B- evals to B or C with a one-line annotation explaining the bump.

**Acceptance:** schema and `scoring-guide.md` agree on the grade set. `test_grade_values_are_valid` passes.

---

## Stream B — Quick Fixes (P0)

### B.1 — Fix `outcome: Applied` in two evals

For each of the 2 evals from April 2026 with `outcome: Applied`:
- Change `outcome: Applied` → `outcome: Pending`.
- Confirm `status:` is `Applied` (state-machine consistent).

**Acceptance:** `test_outcome_values_are_valid` passes. State-machine consistency holds.

---

## Stream C — `Superseded` Design + Data Backfill (P1)

### C.1 — Decide Option A / B / C

See Issue 2 for the tradeoffs.

### C.2 — If Option A (formalize)

- Add `Superseded` to `VALID_STATUSES` in both copies of `tests/test_vault_schema.py`.
- Add a row to the state machine table in `skill-update/references/status-outcome-state-machine.md`:
  - Trigger: "A newer eval at same `[company-slug]` and a later `date:` is authored."
  - status: `Superseded`
  - outcome: TBD — either reuse `Withdrawn` or add a new `Superseded` outcome.
- Mark `Superseded` as terminal alongside `Rejected`, `Passed`, `Offer-Declined`.
- Update Mode 0 health check to recognize the (Superseded, X) pair.
- Backfill the 5 affected evals: keep the original `grade:` and `score:` from the prior version (do not use `superseded` as a grade); set `status: Superseded`; set `outcome:` per the table.
- Update `skill-update/SKILL.md` if any visible mode lists statuses inline.
- Propagate to open-source. Repack.

### C.3 — If Option B (archive)

- Move the 5 evals to `archive/[slug]-v{N}/` per `terminal-archival.md`.
- Leave the most recent eval in `evals/`.
- No schema change required.
- Document the convention in `terminal-archival.md` if not already present (the "supersede via re-eval" trigger).

### C.4 — If Option C (Passed + Withdrawn)

- For each of the 5 evals: set `status: Passed`, `outcome: Withdrawn`. Restore `grade:` and `score:` from the original (do not blank).
- Add a one-line comment to each: "Superseded by re-eval YYYY-MM-DD" so the relationship is visible to a reader.
- No schema change required.

**Acceptance (any option):** all schema tests pass. The 5 evals are no longer flagged as invalid.

---

## Stream D — `test_example_prep_frontmatter` Triage (P2)

### D.1 — Investigate collection error

Run `python -m pytest tests/test_vault_files.py::test_example_prep_frontmatter -v --tb=long` against the main vault. Likely causes:

- `examples/example-prep.md` missing or renamed.
- Fixture `example_prep_frontmatter` not defined or broken.
- Frontmatter parse error in the example file.

Fix or document why the test is permanently skipped.

**Acceptance:** error becomes a pass or an explicit `pytest.skip(...)` with a reason and a tracking pointer.

---

## Plan 16 Cross-Reference Carry-Over

Plan 16 left three deferred skills-structure tests in the open-source repo (`test_bias_caveat_in_mode_1`, `test_gate_pass_rule_is_prominent`, `test_all_config_keys_documented`) waiting on plan 13 to fully ship. Those are tracked in plan 13's "Cross-references" section and are not duplicated here. When this plan + plan 13 D.4–D.5 both close, revisit the three deferred tests.

---

## Out of Scope

- Touching `evals/` files for any reason other than the four specific data corrections above. The schema work is the contract; the eval data is the user's pipeline.
- Rewriting `test_vault_files.py` beyond the one-test triage in D.1.
- Changing the state machine for any status other than `Superseded`.
- Backporting Stream A's rubric change retroactively across pre-existing evals.

---

## Files Touched

Main vault (and open-source mirror per CLAUDE.md propagation rules):

- `tests/test_vault_schema.py` — schema constants (Streams A, C if Option A)
- `skill-update/SKILL.md` — grade list (Stream A.2 if Option A)
- `skill-update/references/scoring-guide.md` — band table (Stream A.2 if Option A)
- `skill-update/references/file-conventions.md` — grade list (Stream A.2 if Option A)
- `skill-update/references/status-outcome-state-machine.md` — Superseded row (Stream C.2 if Option A)
- `skill-update/references/terminal-archival.md` — supersede trigger (Stream C.3 if Option B)
- `dossier.skill` — repacked (any rubric/state-machine change)
- `features/plan/17-eval-schema-data-hygiene.md` — this plan

Main vault only (not propagated):

- `evals/*.md` — the 7 affected evals (2 outcome fixes + 5 superseded backfills)

---

## Validation Checklist

- [ ] `python -m pytest tests/test_vault_schema.py -v` passes (all 9 schema tests green).
- [ ] `scoring-guide.md`, `SKILL.md`, `file-conventions.md`, and `tests/test_vault_schema.py` all agree on the grade set.
- [ ] If Option A on Stream C: state machine table includes a Superseded row; Mode 0 recognizes the pair; terminal-status list includes `Superseded`.
- [ ] If Option B on Stream C: 5 evals moved to archive; `evals/` directory does not contain Superseded artifacts.
- [ ] `test_example_prep_frontmatter` no longer errors at collection.
- [ ] `dossier.skill` repacked in both main vault and open-source if any skill content changed.
- [ ] `tests/test_skill_package_parity.py` still passes (open-source).

---

## Risks and Open Questions

- **Risk: choosing Option B on Stream C and finding re-evaluation is more frequent than expected.** Mitigation: B is reversible — formalizing later is a strict superset of archival.
- **Open question: should `Superseded` be terminal?** Probably yes — once superseded, the eval is replaced and no further state writes apply. But it is not a "user decision" terminal like Passed; it is a "system bookkeeping" terminal. Worth documenting that distinction if Option A is chosen.
- **Open question: should the rubric also add a B- band, or stay coarse?** Argument for adding: B- is the natural human grade for a 3.40–3.49 weighted score. Argument for keeping coarse: the rubric is meant to force binary apply/don't-apply decisions, not differentiate within a band that should already mean "selective only." Recommend adding B- only if it changes a real user behavior.
