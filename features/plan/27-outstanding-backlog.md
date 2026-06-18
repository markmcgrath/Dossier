# Plan 27 — Outstanding Backlog: Dossier Job-Search Skill

**Status:** Planning only. No files were created or modified in the repo during this sweep.
**Author:** Claude (subagent sweep), reviewed by Mark McGrath
**Created:** 2026-06-17

---

## 1. Summary and Method

### What was swept

| Source | Coverage |
|---|---|
| `ROADMAP.md` | All skipped-test entries and deferred-feature entries |
| `tests/SKIPPED_TESTS.md` | All 8 skip sites, with reason, exit criterion, and release-blocker disposition |
| `CHANGELOG.md` (v1.0.0 through v1.3.5 + Unreleased) | Determined what has shipped; used as the "already done" filter throughout |
| `features/plan/13-quality-audit-remediation.md` | Streams A-D; D.1-D.3 (triggered), D.4-D.5 (deferred) |
| `features/plan/22-quality-review-remediation.md` | All five streams (A-E); cross-checked against CHANGELOG to confirm ship status |
| `features/plan/06-deferred.md` | F.1-F.5 (Stream F) |
| `HARDENING.md` | SBOM/SHA-pinning deferral section |
| `skill/references/*.md` (15 files) | Confirmed which modes are fully specified vs. still documented as manual/not-yet-implemented |
| Vault entries: `2026-04-29-dossier-stream-f-deferred`, `2026-04-29-dossier-email-automation-plan`, `2026-04-29-dossier-deep-research-report`, `2026-04-29-dossier-risks`, `2026-04-29-dossier-consolidated-assessment`, `2026-04-29-dossier-stream-d-competitive`, `2026-04-29-dossier-stream-e-advanced` | Designed-but-unimplemented features; plan status vs. shipped status cross-checked |
| Grep for `TODO\|FIXME\|deferred\|not yet implemented\|stub\|placeholder\|future work` across `skill/`, `features/`, root `.md` files | Caught inline deferral markers not captured by plan docs |

### What determines "unimplemented"

A feature is listed as unimplemented if: (a) a test for it is still `pytest.skip()`-ed, (b) a plan doc marks it deferred and no CHANGELOG entry records it shipping, or (c) the skill source (`skill/references/*.md` or `skill/SKILL.md`) explicitly documents the behavior as "manual for now" or "not yet implemented."

---

## 2. Covered by Sibling Plans 23-26

The following items appeared in the research but are owned by the parallel plans being authored alongside this one. They are listed here so nothing looks dropped.

| Sibling plan | What it covers |
|---|---|
| Plan 23 | `packets/` folder convention, standardized packet creation workflow, send-ready artifact grouping |
| Plan 24 | Send-ready document contract + schema validator for outbound artifacts |
| Plan 25 | Target Radar as a standalone in-Dossier component (currently a Commonplace brief stub in Plan 21) |
| Plan 26 | Live working-folder cleanup map for Mark's active vault |

---

## 3. Backlog

### Group A: Quick Wins (Skipped Tests with Simple Exit Criteria)

These three tests have been in `pytest.skip()` since Plan 13 was scoped. All three are documentation changes, not behavior changes. The underlying behavior they assert is already present in the skill. Combined effort is under 30 minutes of focused edits plus one test-suite run.

| ID | Item | Source | Evidence it is unimplemented | Type | Effort | Value / Confidence | Recommendation |
|---|---|---|---|---|---|---|---|
| A-1 | Add `## Gate-Pass Rule` heading to `skill/SKILL.md` | `tests/SKIPPED_TESTS.md` row 1; `ROADMAP.md` "Skipped tests" §1; `tests/test_skill_structure.py:84` | `grep -c "Gate-Pass Rule" skill/SKILL.md` returns 0. Test at line 84 is hard-skipped with explicit "not present" message. Exit criterion: add the heading. | skipped-test | 10 min focused, 3 min CI | High value (test goes green, discoverability improves for contributors). Not speculative. | do-now |
| A-2 | Fix `test_bias_caveat_in_mode_1` assertion target | `tests/SKIPPED_TESTS.md` row 2; `tests/test_skill_structure.py:94` | The caveat already exists in `skill/references/mode1-offer-evaluator.md`. The skip is because the test asserts against `skill/SKILL.md` (wrong file). No content change needed, only the test assertion target. Exit criterion: rewrite assertion to check `mode1-offer-evaluator.md`, or retire the test. | skipped-test | 5 min focused, 3 min CI | High value (test goes green, zero risk). Not speculative. | do-now |
| A-3 | Document `redact_comp` and `scoring_weights` in `skill/SKILL.md` config-keys section | `tests/SKIPPED_TESTS.md` row 3; `tests/test_skill_structure.py:124`; `features/plan/13-quality-audit-remediation.md` Stream C | `grep "redact_comp" skill/SKILL.md` returns 0; `grep "scoring_weights" skill/SKILL.md` returns 0. Both keys are honored at runtime but absent from the documented config section. Exit criterion: add both keys. | skipped-test | 10 min focused, 3 min CI | High value (closes last Plan 13 documentation debt, 3 tests go green together). Not speculative. | do-now |

**Note on Plan 13 context.** D.1-D.3 from Plan 13 (competency mapping matrix, alternative interview frameworks, flexibility/location scoring split) are triggered only on "first interview scheduled" per the plan's execution table. They are not listed above because the trigger condition may not yet have fired. If a live interview has been scheduled, D.1-D.3 become immediate work (estimated 1-1.5 hours total per the plan).

---

### Group B: Designed-Not-Built Features from the Vault

These features have explicit designs in vault entries or plan docs but have not shipped. Each is verified against the repo to confirm absence.

| ID | Item | Source | Evidence it is unimplemented | Type | Effort | Value / Confidence | Recommendation |
|---|---|---|---|---|---|---|---|
| B-1 | 90-day cold-application detection (auto-archival proposal) | `ROADMAP.md` "Deferred features" §2; `CHANGELOG.md` v1.1.0 "Planned" section; `skill/references/file-conventions.md:104`; `skill/references/terminal-archival.md`; `tests/test_terminal_archival.py::test_no_cold_detection_implementation_symbols` (active regression guard) | `grep -rn "cold_threshold_days\|days_until_cold\|stale_application_days\|auto_archive_cold" skill/` returns 0 matches. `file-conventions.md:104` reads: "The >90 days cold case is currently manual." Regression guard test will fail loudly if any of those symbols land under `skill/` while docs still say manual. | designed-not-built | 45 min focused (date arithmetic logic in a new mode reference section) + 15 min to update the regression-guard test + 5 min CI | High value: fills the one remaining major pipeline-state gap; prevents applications silently aging out of view. Real, not speculative, based on convergent deep-research and gap-analysis findings. Confidence: high once the promotion criterion fires (vault has enough accumulated evals to validate the 90-day threshold). | schedule (promote when vault has 25+ evals with dates, so the detection can be validated on real data) |
| B-2 | Scoring calibration feedback loop (auto-weight adjustment based on grade-to-outcome correlation) | `CHANGELOG.md` v1.1.0 "Planned" section; `features/plan/05-advanced.md`; vault entry `2026-04-29-dossier-stream-e-advanced` | `CHANGELOG.md:169-170` explicitly marks this as "Planned, not yet implemented." `skill/references/mode13-calibration.md` is purely analytical (human reads the report); no weight adjustment logic exists anywhere in `skill/`. | designed-not-built | 60-90 min focused (new section in mode13-calibration.md + proposal output format + update to scoring-guide.md) | Moderate value; useful once 50+ evals with outcomes exist. Mode 13 already does the correlation analysis; this is the "propose new weights" output layer. Per skills convention: **value is speculative until sufficient outcome data exists.** Do not build until Mode 13 calibration report has been run 3+ times and shows systematic drift. | leave-deferred-with-trigger (trigger: Mode 13 run 3+ times showing consistent dimension-weight drift) |
| B-3 | Portal scan ATS coverage validation (Greenhouse JSON API feasibility test) | `features/plan/06-deferred.md` F.2; vault entry `2026-04-29-dossier-stream-f-deferred` | `mode2-portal-scan.md` is shipped and specced. However, `06-deferred.md` F.2 explicitly says: "Do not design or implement until the feasibility test passes." The feasibility test (whether `web_fetch` can reach `boards-api.greenhouse.io`) has never been documented as completed. The mode currently has a Lever/Ashby fallback to browser automation but the primary Greenhouse JSON path is unvalidated in production. | designed-not-built | 15 min focused (run `WebFetch` against one real Greenhouse board, document the result) | High value for the feasibility test itself (10 minutes validates or rules out the primary path). The mode is already shipped; this is just an in-use validation. Not speculative: you either can fetch the JSON or you cannot. | do-now (run a single fetch against a known Greenhouse board; document whether the JSON path works or falls back to browser; no code change required) |
| B-4 | Email automation companion skill (proactive cadence-driven outreach) | `features/plan/06-deferred.md` F.4; vault entry `2026-04-29-dossier-email-automation-plan` (`plan_status: deferred`); `features/plan/README.md` | `plan_status: deferred` in vault. Three blocking conditions documented in `06-deferred.md` F.4: (1) `gmail_send_message` availability unverified, (2) spec is still Notion-dependent and conflicts with vault-first architecture, (3) base skill must be stable first. None of these blockers have been resolved per the CHANGELOG. | designed-not-built | 25-30 hours (full companion skill, 4 phases per the email automation plan). Feasibility gating step: 30 min to test `gmail_send_message`. | Moderate value for a complete build. **Value of the full skill is speculative** until feasibility is confirmed and the Notion-dependency conflict is resolved. Level 1 (draft-only) would have high confidence value once the architectural conflict is cleared. | leave-deferred-with-trigger (trigger: (a) confirm `gmail_send_message` exists in the Gmail MCP, and (b) rewrite the email automation plan's data flow to vault-first; then build Level 1 only first) |
| B-5 | Repost fingerprinting for ghost-job detection (Plan 13, D.4) | `features/plan/13-quality-audit-remediation.md` D.4; grep confirms no fingerprinting symbols in `skill/` | Explicitly deferred in plan 13 execution table: "D.4: 60+ evals or jurisdiction match." `grep -rn "fingerprint\|repost" skill/` returns only a one-line reference to "reposted multiple times" as a legitimacy signal description, not as computed logic. | designed-not-built | 30 min focused (add normalized fingerprint instruction to mode1-offer-evaluator.md + update scoring-guide.md) | Low-to-moderate value until vault has 60+ evals. Per skills convention: **value is speculative** at current vault size. Signal is real (repost detection is a recognized ghost-job indicator) but requires a corpus to produce false-positive rate below the 5% acceptance criterion stated in D.4. | leave-deferred-with-trigger (trigger: vault reaches 60+ evals with dates) |
| B-6 | Jurisdiction-aware legitimacy warnings for Ontario/NY roles (Plan 13, D.5) | `features/plan/13-quality-audit-remediation.md` D.5 | Explicitly deferred: "until geographic scope of the job search includes these jurisdictions." No location-conditional legitimacy language exists in `skill/references/mode1-offer-evaluator.md` or `skill/references/scoring-guide.md`. | designed-not-built | 15 min focused (add two jurisdiction-conditional paragraphs to mode1-offer-evaluator.md) | Moderate value **if and only if** job search expands to Ontario or New York. Per skills convention: **value is speculative** until geographic scope is confirmed. The legislation is real and now in effect (Ontario Working for Workers Act, January 2026). | leave-deferred-with-trigger (trigger: first Ontario or New York role appears in the pipeline) |
| B-7 | Weekly trend report data-accumulation prerequisite documentation | `features/plan/06-deferred.md` F.3; `skill/references/weekly-trend-report.md` | `weekly-trend-report.md` is shipped and fully specced. However, `06-deferred.md` F.3 states it requires "4+ weeks of accumulated daily scan data." The reference file has a graceful-skip note but does not document the minimum-data prerequisite prominently for the user. This is a documentation gap, not a code gap. | docs | 10 min focused | Low value as an isolated fix; high value bundled with a first successful trend-report run. Not speculative. | schedule (bundle with first use of the weekly trend report) |

---

### Group C: Deferred-with-Explicit-Trigger (Leave as-is, triggers documented)

These items have well-formed deferral notes in the repo. No action is needed until the named trigger fires. Listed here so nothing looks forgotten.

| ID | Item | Source | Trigger to promote |
|---|---|---|---|
| C-1 | SBOM generation and third-party Action SHA pinning | `HARDENING.md` §10 "Deferred: SBOM and third-party Action SHA pinning"; `ROADMAP.md` "Deferred features" §1 | Any one of: (a) a non-first-party GitHub Action is added, (b) project publishes to a registry, (c) a runtime dependency is added to `dossier.skill`. |
| C-2 | Pipeline state machine with enforced transitions (F.5) | `features/plan/06-deferred.md` F.5 | Malformed `(status, outcome)` pairs become a recurring problem in live use despite Mode 0's spot-check. Currently the state machine is fully specified in `skill/references/status-outcome-state-machine.md`; enforcement is by convention. |
| C-3 | Scoring calibration weight auto-adjustment (B-2 above, full entry) | `CHANGELOG.md` v1.1.0 "Planned" | 3+ Mode 13 calibration runs showing systematic dimension-weight drift. |
| C-4 | 90-day cold detection (B-1 above, full entry) | `ROADMAP.md` "Deferred features" §2 | Vault reaches 25+ evals with dates, enabling real-data validation of the 90-day threshold before the regression-guard test is updated. |

---

### Group D: Hardening / Infra

These items are real gaps but the consolidated assessment and the 2026-05-14 quality review (A-/91) explicitly assessed them as low-priority at current scale. They are listed for completeness.

| ID | Item | Source | Evidence it is unimplemented | Type | Effort | Value / Confidence | Recommendation |
|---|---|---|---|---|---|---|---|
| D-1 | Automated semantic / LLM-output quality gate (CI-gated red-team harness) | `reviews/2026-05-14-quality-review.md` §Security, privacy and safety; `tests/semantic-review-checklist.md` | Semantic review is currently a manual pre-release checklist. No CI gate exists and no automated similarity-metric comparison of golden artifacts. `CONTRIBUTING.md` now flags it as a required release step, which closes the process gap. | hardening | 4-8 hours for a basic similarity-metric CI check (would require invoking Claude in CI, which has cost and nondeterminism implications) | Per the quality review: "LLM output quality is the main remaining assurance gap. It does not need to be a brittle CI gate." Per skills convention: **value of a full automated gate is speculative** given nondeterminism. The current manual checklist + golden artifacts is the right tradeoff at this scale. | leave-deferred-with-trigger (trigger: consistent routing-eval score drops below 0.95 across two consecutive releases) |
| D-2 | Dependency lockfile (pip-compile, uv lock, or similar) | `reviews/2026-05-14-quality-review.md` §Portability; `features/plan/22-quality-review-remediation.md` Stream A "Out of Scope" | `pyproject.toml` and `.python-version` shipped in v1.3.5. However, the Plan 22 remediation explicitly excluded a lockfile: "User selected the lighter pyproject-only path." No `requirements.lock` or `uv.lock` exists. | hardening | 30 min focused + Dependabot config review | Low value at current solo-maintainer scale. `requirements.txt` plus CI-pinned Python 3.12 is stable. Per skills convention: **speculative value improvement.** | leave-deferred-with-trigger (trigger: a CI failure traced to a transitive dependency version conflict) |

---

## 4. Recommended Next 3

Based on the sweep, these three items deliver the clearest near-term return per minute of work.

**Next 1 (15-25 minutes total, zero risk): Close the three Plan 13 SKILL.md doc skips (A-1, A-2, A-3).**
All three are documentation edits, none change behavior, and all three tests go green in a single PR. Closing this debt is overdue (Plan 13 was the quality audit remediation from two months ago). Combine into one commit: `docs: close plan-13 skill.md doc skips (gate-pass heading, bias-caveat test target, config-key docs)`.

**Next 2 (15 minutes, zero risk, binary outcome): Portal scan Greenhouse feasibility test (B-3).**
Run `WebFetch` against one real Greenhouse board (e.g., `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs`). This validates or rules out the primary Mode 2.1 path that has been marked "do not implement until tested" since `06-deferred.md` was written. If it works, close the deferral in `06-deferred.md`; if it is blocked, document the fallback-only posture in `mode2-portal-scan.md`. Either outcome costs 15 minutes and eliminates an open question that has lingered across multiple plans.

**Next 3 (45-60 minutes, high value): 90-day cold detection (B-1), when vault has 25+ dated evals.**
This is the single highest-value designed-not-built feature and the one the CHANGELOG explicitly flagged as "Planned." It fills the last major pipeline-state gap (Mode 9 handles terminal transitions; nothing handles silent aging). The implementation is a new section in the `terminal-archival.md` reference file plus date arithmetic instructions, paired with an update to the regression-guard test in `test_terminal_archival.py`. Schedule this immediately once the vault corpus is large enough to validate the threshold.

---

## 5. Item Counts by Group

| Group | Count | Notes |
|---|---|---|
| A: Quick wins (skipped tests) | 3 | All resolvable in one PR, under 30 minutes |
| B: Designed-not-built | 7 | Two are "do-now" (A-1 through A-3 + B-3), five are schedule-or-deferred |
| C: Deferred-with-explicit-trigger | 4 | No action until trigger fires; documented to prevent invisible debt |
| D: Hardening/infra | 2 | Assessed as premature at current scale by the quality review |
| **Total** | **16** | Excludes 4 sibling-plan items (Plans 23-26) |

---

## Appendix: Items Confirmed Shipped (Not Listed as Outstanding)

The following items appeared in early source documents as gaps or deferred work but were verified as shipped via the CHANGELOG and are excluded from the backlog.

| Item | Shipped in |
|---|---|
| Status/outcome state machine | v1.1.0 |
| Terminal archival (Mode 9 trigger) | v1.1.0 |
| Story tagging (Mode 3) | v1.1.0 |
| LinkedIn/Recruiter Inbox Pulse dedup v2 | v1.1.0 (Plan 14) |
| Recruiter Inbox Pulse broadening (Indeed, Dice, Google alerts) | v1.1.0 (Plan 15) |
| Skill parity CI gate | v1.3.0 |
| SLSA build-provenance attestations | v1.3.4 |
| Semantic review pre-tag ritual (CONTRIBUTING.md) | v1.3.5 |
| Skipped-test accountability table (`tests/SKIPPED_TESTS.md`) | v1.3.5 |
| `pyproject.toml` + `.python-version` | v1.3.5 |
| Contributor task matrix in CONTRIBUTING.md | v1.3.5 |
| SBOM deferral documented with re-trigger criteria | v1.3.5 |
| Weekly trend report (F.3) | v1.0.0 (as part of base skill) |
| Batch pipeline Mode 12 (F.1) | v1.0.0 |
| Portal scan Mode 2.1 (F.2, specced) | v1.0.0 (feasibility of Greenhouse API path still unvalidated, see B-3) |
| Golden regression artifacts (`examples/golden/`) | v1.3.2 |
