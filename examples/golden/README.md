# `examples/golden/` — Regression-Anchor Artifacts

These are **reference outputs** the dossier skill should produce when Mode 1 evaluates the paired fixture JD. They exist so that maintainers can detect substantive drift in Mode 1 behavior across releases — especially in scoring calibration, gate-pass enforcement, legitimacy classification, and prompt-injection handling.

## The set

| Golden | Paired fixture | Exercises |
|--------|----------------|-----------|
| [`eval-strong-fit.md`](eval-strong-fit.md) | [`tests/fixtures/jd_strong_fit.md`](../../tests/fixtures/jd_strong_fit.md) | Grade A path, Verified legitimacy, full 10-dimension scoring on a clean fit |
| [`eval-poor-fit-ghost-job.md`](eval-poor-fit-ghost-job.md) | [`tests/fixtures/jd_ghost_job.md`](../../tests/fixtures/jd_ghost_job.md) | Gate-pass rule (Dim 1 + Dim 2 ≤ 2 → D), Likely-Ghost legitimacy classification, integrity-rule honesty |
| [`eval-injection-response.md`](eval-injection-response.md) | [`tests/fixtures/jd_injection_attempt.md`](../../tests/fixtures/jd_injection_attempt.md) | Content Trust Boundary refusal, Prompt Injection Notice, Suspect-tier classification |

## Manual workflow (NOT a CI gate)

These goldens are **not** wired to CI. The workflow is manual and lives in maintainer judgment:

1. **When you change Mode 1** (the skill body, `references/mode1-offer-evaluator.md`, or `references/scoring-guide.md`) materially, before opening the PR:
2. **Re-run Mode 1 by hand** against each of the three paired fixtures. Use the same candidate persona that grounds [`examples/example-eval.md`](../example-eval.md) (9-year platform engineer, fintech background) so the comparison is apples-to-apples.
3. **Diff your output against the golden.** Ignore pure formatting drift (whitespace, table column padding, prose paraphrasing). Look for substantive drift: grade or score changes ≥ 0.3, dimension scores shifting by ≥ 1, gate-pass rule not firing where it should, legitimacy tier flipping, missing Prompt Injection Notice on the injection fixture, partial compliance with injected instructions.
4. **If substantive drift is detected, escalate before merging.** Either (a) update the affected golden in the same PR with a CHANGELOG note explaining the calibration change, or (b) revert the Mode 1 change. The injection golden has a higher bar — drift there is a security regression and warrants a security note in CHANGELOG.

The point of "manual, not CI" is twofold:

- **No live Claude calls in CI.** Mode 1 output isn't byte-deterministic, so a CI gate would have to wrap a similarity metric — that's its own project, deferred.
- **Human judgment is the load-bearing reviewer.** "Substantive drift" is a judgment call about whether the skill still behaves as documented. A test runner can't make that call honestly.

## Per-release test-run captures

When the post-release install smoke (CONTRIBUTING.md §Post-release install smoke, steps 6–7) is run against these goldens, the actual Mode 1 outputs can optionally be committed under [`test-runs/vX.Y.Z/`](test-runs/) for the released tag. Those are the *outputs the installed skill produced* — not the goldens themselves, and not a target to drift against. They exist as a paper trail of "did this release diff cleanly against the goldens at release time?" See [`test-runs/README.md`](test-runs/README.md) for the convention.

## How these differ from `examples/example-*.md`

The four artifacts at [`examples/example-*.md`](..) — `example-eval.md`, `example-outreach.md`, `example-prep.md`, `example-cover-letter.md` — are **showpieces**: polished demonstrations of what good output looks like for new readers. They live alongside the README on the repo's front page.

The goldens here are **regression anchors**: terse, auditable, paired one-to-one with test fixtures, and explicitly framed (in the banner at the top of each file) so a maintainer running through Mode 1 changes immediately knows the comparison is the point. They are not meant to be the first thing a new reader sees — they are meant to be the first thing a maintainer diffs.

Both sets use the same fictional candidate persona for narrative consistency. The showpieces evaluate fictional companies the candidate has researched; the goldens evaluate the test fixtures.
