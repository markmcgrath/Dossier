# Plan 19 — Routing eval harness (stub, post-hoc)

**Status:** Shipped 2026-05-08 (PR #43, commit `b92a31d`)
**Author:** Mark McGrath (with Claude as drafting partner)
**Created:** 2026-05-12 (post-hoc stub; original work shipped without a plan doc)

This stub exists so the plan-numbering convention stays intact. The design rationale and implementation history live in PR #43's commit messages — there is no separate plan document to read.

## What shipped

`tools/run_routing_evals.py` — a maintainer-side CLI that scores routing decisions on the 45-prompt set in `tests/golden_prompts/routing_test_set.md` against the bundled `skill/SKILL.md`. The harness shells out to `claude -p` using the maintainer's existing Claude Code subscription auth and writes a markdown report; exit code is always 0 (score acceptability is the maintainer's judgment, not a CI gate).

Supporting tests: `tests/test_routing_evals_parser.py` and `tests/test_routing_evals_scoring.py`.

CONTRIBUTING.md documents the invocation under "Routing eval (optional, pre-tag)".

## Why the design changed mid-stream

The first version of PR #43 wired the harness into the release workflow as a publication gate, with `ANTHROPIC_API_KEY` in CI and a 0.95 accuracy threshold. That posture was reverted in the second commit on the same PR for three reasons captured in the commit body:

1. Threshold-gating on stochastic LLM behavior introduced flake.
2. Model drift would turn the threshold into a moving target.
3. The maintainer already has Claude Code authenticated locally — requiring a separate API key in CI was unnecessary.

The shipped design is the second commit's redesign. The first commit's gating logic is not in main.

## What this stub does not cover

- Future improvements to the prompt set, scoring rubric, or report format.
- Any decision to re-introduce a CI gate (would need its own plan).

If routing-eval coverage materially expands, replace this stub with a real plan.
