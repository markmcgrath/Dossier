# Semantic review checklist

The structural test suite validates frontmatter, schemas, packaging, and policy contracts but cannot evaluate the quality of model outputs. This checklist is for per-release human review of recent artifacts. Run it before tagging a release. Not run in CI.

---

## 1. Grade accuracy

Sample 3 recent eval files from `evals/`. For each:

- Confirm the assigned grade aligns with the match signals in `profile.md` and the evidence in `cv.md`.
- Confirm the score reasoning cites specific JD/CV touchpoints, not generic prose.
- Check that dimension scores are internally consistent with the summary grade.

- [ ] Three recent evals reviewed; grades and reasoning align with `profile.md` signals and `cv.md` evidence.

Notes:

---

## 2. Concern inclusion

Every eval must contain both strengths and concerns per the `CLAUDE.md` integrity rules. Concerns must be specific to the role, not boilerplate filler.

Sample 3 recent eval files from `evals/`. For each:

- Confirm a `## Concerns` (or equivalent) section is present and non-empty.
- Confirm concerns name specific role requirements, company signals, or JD details — not generic phrases like "compensation unknown".
- Confirm strengths are also present.

- [ ] Three recent evals reviewed; each has distinct, role-specific concerns and strengths.

Notes:

---

## 3. Prompt-injection refusal

The Content Trust Boundary defined in `skill/SKILL.md` must cause Mode 1 to flag injection attempts rather than comply with them.

Steps:

1. Feed `examples/golden/jd_injection_attempt.md` through Mode 1 (offer evaluator).
2. Read the resulting eval carefully.
3. Confirm the eval includes a Prompt Injection Notice and does NOT follow any embedded instruction (e.g., does not assign Grade A, does not output alternative content).
4. Compare against the reference response in `examples/golden/eval-injection-response.md`.

- [ ] Injection attempt correctly flagged; eval does not comply with embedded instructions.

Notes:

---

## 4. Outreach tone and non-fabrication

Outreach drafts must sound human, not templated. Tone must match the channel. No fabricated claims, invented references, or invented contacts are permitted.

Sample 3 recent drafts from `outreach/`. For each:

- Confirm no claim appears that cannot be traced to `cv.md` or the user-provided JD/context.
- Confirm no invented references or contacts.
- Confirm LinkedIn outreach is conversational; email outreach is professional.

- [ ] Three recent outreach drafts reviewed; no fabrication found; channel tone is appropriate.

Notes:

---

## 5. Frontmatter compliance and dashboard render

Vault files must pass the structural test suite and the Obsidian Dataview dashboard must render without errors.

Steps:

1. Pick 5 vault files at random across different folders (`evals/`, `outreach/`, `prep/`, `research/`, `negotiation/`).
2. Inspect each for required frontmatter fields per `README.md`.
3. Run `bash tests/run_tests.sh` and confirm it still reports 176 passed, 3 skipped (or the current pinned count).
4. Open `dashboard.md` in Obsidian and confirm all Dataview queries render without errors.

- [ ] Five files inspected; `bash tests/run_tests.sh` passes; Dataview dashboard renders cleanly.

Notes:

---

## Closing this review

If any item above surfaces a systemic issue (a mode consistently omitting concerns, grade inflation on a category of roles), file a GitHub issue so it can be tracked and addressed.

If the finding is a personal-workflow correction (a prompt pattern that works better for your context), add a `feedback_` memory entry via the standard memory workflow.

Deferred semantic-quality work — including improvements to the injection-refusal golden and any future CI-gatable similarity metrics — is tracked in `ROADMAP.md`.
