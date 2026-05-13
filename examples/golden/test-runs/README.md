# `examples/golden/test-runs/` — Per-Release Smoke Outputs

Actual Mode 1 outputs captured during the post-release install smoke (CONTRIBUTING.md §Post-release install smoke). Each subfolder is named after the release tag (`v1.3.3/`, `v1.3.4/`, …) and contains the test-run output for each paired fixture in `examples/golden/`.

These are **not the goldens.** The goldens one level up (`examples/golden/eval-*.md`) are the regression anchors — the reference shape Mode 1 should produce. The files here are the *output the skill actually produced* in the named release, captured as proof of the smoke check rather than as a target to drift against.

## Why commit them

Two reasons.

1. **Paper trail.** When a future maintainer asks "did v1.3.3 actually produce a clean diff against the goldens at release time?", the answer is checked in alongside the release, not lost to whatever scratch folder the maintainer used.
2. **Calibration audit.** If a later release surfaces drift the maintainer accepts (golden update + CHANGELOG note), the historical test-runs let a reviewer trace when calibration shifted and by how much.

## Naming convention

- Subfolder: `vX.Y.Z/` — exact release tag, leading `v` included.
- Files: named to match the paired golden, e.g. `eval-strong-fit.md` lives next to `examples/golden/eval-strong-fit.md`. Diff with `diff examples/golden/eval-strong-fit.md examples/golden/test-runs/vX.Y.Z/eval-strong-fit.md`.

## Optional, not required

Capturing test-runs per release is optional. The smoke check itself (steps 6–7 of the CONTRIBUTING checklist) is what gates the release; committing the artifacts here just preserves the evidence. Skip for trivial patch releases that didn't touch Mode 1 or skill behavior at all.
