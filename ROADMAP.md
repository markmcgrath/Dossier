This file tracks deferred work and exit criteria for currently-skipped tests. Items here are not abandoned — they have specific, named conditions that must be true before they are considered done. Skipped tests become green when the exit criterion is met; deferred features are promoted when the listed promotion criterion is satisfied.

## Skipped tests

### `test_gate_pass_rule_is_prominent`

**Location:** `tests/test_skill_structure.py:81`

**Why skipped:** The Gate-Pass Rule (Dimensions 1 + 2 combined score of 2 or less triggers a D grade regardless of other dimensions) is documented in `skill/references/mode1-offer-evaluator.md` but does not yet appear as a visible, named section heading in `skill/SKILL.md`. The test asserts that a contributor reading the top-level skill file can locate the rule without diving into references.

**Exit criterion:** Add a `## Gate-Pass Rule` (or equivalent) section heading to `skill/SKILL.md` that names and summarizes the rule. The test unskips and passes once that heading is present.

**Tracked:** Plan 13, Stream A.

---

### `test_bias_caveat_in_mode_1`

**Location:** `tests/test_skill_structure.py:91`

**Why skipped:** The test currently asserts that a bias/recency-caveat phrase is present in `skill/SKILL.md`. The caveat lives in `skill/references/mode1-offer-evaluator.md`, not in the top-level file, so the assertion targets the wrong file.

**Exit criterion (rescope target):** Rewrite the test to assert against `skill/references/mode1-offer-evaluator.md` rather than `skill/SKILL.md`. No content change is needed — the caveat is already there. The test unskips and passes once the assertion target is corrected.

**Tracked:** Plan 13, Stream A.2; Plan 16 follow-up note.

---

### `test_all_config_keys_documented`

**Location:** `tests/test_skill_structure.py:113`

**Why skipped:** The test checks that every supported config key (`redact_comp`, `scoring_weights`, `notion_token`, `notion_db_id`, `calendar_id`) is documented in `skill/SKILL.md`. Three of the five keys (`notion_token`, `notion_db_id`, `calendar_id`) are already present. Two keys (`redact_comp` and `scoring_weights`) are not yet documented there.

**Exit criterion:** Add `redact_comp` and `scoring_weights` to the config-keys section of `skill/SKILL.md`. The test unskips and passes once both keys appear.

**Tracked:** Plan 13, Stream C.

---

## Deferred features

### 90-day cold-application detection

**Guarded by:** `tests/test_terminal_archival.py:67` — `test_no_cold_detection_implementation_symbols`

**Status:** Deliberate non-feature. This regression test fails loudly if any implementation symbol for cold detection (`cold_threshold_days`, `days_until_cold`, `stale_application_days`, `auto_archive_cold`) lands under `skill/` while the docs still describe the feature as manual. The test is not skipped; it is an active guard.

**Current behavior:** 90-day cold detection is manual. Mode 9 auto-proposes archival for explicit terminal-state transitions (rejection, offer accepted/declined). Detecting applications that have simply gone cold requires date arithmetic that no mode implements yet.

**Promotion criterion:** A mode implements date arithmetic to detect applications in `Applied` or `Interviewing` status with no activity for 90 or more days and proposes archival. When that implementation lands, the regression-guard test must be updated (or removed) as part of the same PR, and this entry moves to a `## Shipped` section.
