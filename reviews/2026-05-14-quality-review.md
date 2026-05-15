# Plan 22 — Project Quality Review (2026-05-14)

**Status:** Review complete
**Reviewer:** Code review agent
**Scope:** Entire tracked repository at `HEAD`, including root governance docs, skill source and packaged `dossier.skill`, schemas, tests, examples, CI/release scripts, feature plans, and changelog.
**Method:** ISO/IEC 25010-inspired product quality rubric, with OpenSSF Scorecard-style supply-chain and security checks adapted for a local-first markdown/AI-skill project.
**Scale:** 0–5 per category, converted to weighted percentage and letter grade using the table below.

---

## Executive Summary

Dossier is an unusually mature documentation-first AI skill project. It has a coherent vault-first architecture, explicit prompt-injection boundaries, a deterministic skill-packaging workflow, clear user/system/derived data ownership, machine-readable schemas, and a fast structural regression suite. The repository is ready for continued public use and iterative release work.

**Overall score: 91 / 100 — A-**

This is a high-confidence A- rather than an A/A+ because the weakest areas are not implementation polish but assurance depth: semantic LLM-output quality remains mostly manual, dependency/environment reproducibility is lighter than the rest of the release posture, and some intentionally deferred product automation (for example 90-day cold detection) still requires manual operation.

---

## Standard Grading Mechanism

### Letter Conversion

| Percent | Grade | Interpretation |
|---:|:---:|---|
| 97–100 | A+ | Exemplary; reference-quality across nearly all categories. |
| 93–96 | A | Production-ready with only minor non-blocking gaps. |
| 90–92 | A- | Strong production posture; a few material improvements remain. |
| 87–89 | B+ | Good, but several notable gaps or one significant risk. |
| 83–86 | B | Usable and maintainable; remediation recommended before scale. |
| 80–82 | B- | Functional but uneven. |
| 70–79 | C | Significant gaps; use cautiously. |
| 60–69 | D | Major deficiencies. |
| <60 | F | Not production-ready. |

### Category Rubric

Each category receives a 0–5 score:

- **5:** Excellent; well documented, tested, and enforced where appropriate.
- **4:** Strong; minor gaps or manual controls remain.
- **3:** Adequate; works but needs meaningful hardening.
- **2:** Weak; repeated gaps or unclear ownership.
- **1:** Minimal; likely fragile.
- **0:** Missing or actively harmful.

---

## Weighted Scorecard

| Category | Weight | Score (0–5) | Weighted Points | Grade | Evidence |
|---|---:|---:|---:|:---:|---|
| Functional suitability | 14 | 4.6 | 12.9 | A- | Job-search modes, vault schemas, examples, and pipeline state model are complete and internally consistent. |
| Architecture & data ownership | 12 | 4.8 | 11.5 | A | Vault-first contract is repeated across the skill, README, CLAUDE contract, DATA_CONTRACT, and tests. |
| Security, privacy & safety | 14 | 4.5 | 12.6 | A- | Content Trust Boundary, privacy threat model, PII scan, security policy, and prompt-injection fixtures are strong; no formal dynamic red-team automation. |
| Test coverage & quality gates | 13 | 4.4 | 11.4 | B+/A- | 176 passing tests plus 4 expected skips; tests cover schemas, package parity, docs consistency, state machine, and release glob behavior. Semantic quality is still a checklist/manual review area. |
| Maintainability & documentation | 13 | 4.7 | 12.2 | A | Documentation is comprehensive, cross-linked, and backed by consistency tests; plan history is unusually clear. |
| Release engineering & supply chain | 12 | 4.5 | 10.8 | A- | Deterministic packaging, manifest, SHA256 checksums, artifact verification, CI skill parity, conventional commits, changelog gates, and release workflow attestations. |
| Usability & onboarding | 9 | 4.3 | 7.7 | B+/A- | README/START_HERE/examples make the workflow approachable, but Claude Desktop/Cowork dependency and markdown-vault concepts remain a learning curve. |
| Portability & reproducibility | 7 | 3.8 | 5.3 | B | Python dependency list and portable packaging script exist, but there is no lockfile, pyproject, or version-manager file; CI is Python 3.12 while local run here used Python 3.14. |
| Roadmap clarity & risk management | 6 | 4.5 | 5.4 | A- | Deferred work, known limitations, hardening trade-offs, and plan status are explicit. |
| **Total** | **100** | — | **91.8** | **A-** | Rounded down to 91 because semantic quality remains manual and environment reproducibility is lighter than the rest of the repo. |

---

## Review Evidence

### Repository Shape

- **Tracked files:** 149
- **Markdown files:** 95 tracked files / 17,648 lines
- **Python files:** 25 tracked files / 3,914 lines
- **Shell scripts:** 5 tracked files / 589 lines
- **Test modules:** 21 `tests/test_*.py` files
- **Primary artifact:** `dossier.skill` generated from `skill/`

### Commands Run

```bash
python --version
python -m pip install -r requirements.txt
DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v
python .github/scripts/pii_scan.py
bash .github/scripts/build_skill.sh
python - <<'PY'
from pathlib import Path
import subprocess
files=subprocess.check_output(['git','ls-files'], text=True).splitlines()
by_ext={}
for f in files:
    p=Path(f)
    lines=sum(1 for _ in p.open('rb'))
    ext=p.suffix or '[none]'
    by_ext.setdefault(ext,[0,0])
    by_ext[ext][0]+=1
    by_ext[ext][1]+=lines
print('tracked files', len(files))
for ext,(cnt,lines) in sorted(by_ext.items(), key=lambda kv:(-kv[1][1], kv[0])):
    print(f'{ext:12} {cnt:4} {lines:6}')
print('test files', sum(1 for f in files if f.startswith('tests/test_') and f.endswith('.py')))
PY
```

### Results

- `python -m pip install -r requirements.txt` could not fetch `jsonschema>=4.0.0` because the package index tunnel returned HTTP 403. Existing local pytest/PyYAML were sufficient for the suite, and `jsonschema`-dependent schema-validation tests skipped as designed.
- `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v`: **176 passed, 4 skipped**.
- `python .github/scripts/pii_scan.py`: **all tracked files clean**.
- `bash .github/scripts/build_skill.sh`: **content-match passed**, with `manifest.json` excluded per documented hardening behavior.

---

## Category Findings

### 1. Functional Suitability — 4.6 / 5

**Strengths**

- The skill covers a broad, coherent job-search workflow: evaluation, outreach, prep, research, inbox follow-up, calendar operations, tailored CV, batch pipeline, calibration, and weekly trend reporting.
- Eval frontmatter has a clear schema with status, outcome, legitimacy, source, and provenance fields.
- The scoring guide is intentionally opinionated and includes a gate-pass rule, reducing the chance that a superficially attractive role receives an inflated grade.
- Example and golden artifacts provide concrete expectations for normal, poor-fit/ghost-job, and prompt-injection cases.

**Gaps**

- End-to-end LLM execution is intentionally outside automated tests.
- Some workflows remain advisory/manual rather than operationally automated, especially cold-application detection.

### 2. Architecture & Data Ownership — 4.8 / 5

**Strengths**

- Vault-first is consistently stated: the vault is the source of truth and Notion is optional/mirror-only.
- User-layer, system-layer, and derived-file ownership are explicitly separated.
- Archive-don't-delete behavior protects history and reduces accidental data loss.

**Gaps**

- The architecture is documentation-enforced more than runtime-enforced, which is appropriate for a skill/vault project but still depends on agent compliance.

### 3. Security, Privacy & Safety — 4.5 / 5

**Strengths**

- The Content Trust Boundary appears before operational instructions, explicitly treating job descriptions, email, web pages, LinkedIn profiles, and Apollo data as untrusted.
- Privacy documentation maps data types to external services and retention expectations.
- The security policy identifies prompt injection, credential exposure, unsafe untrusted-content handling, and data leakage as in-scope vulnerabilities.
- CI includes a generic PII scan, and prompt-injection fixture coverage exists.

**Gaps**

- PII scanning is necessarily generic and does not cover all contextual/private data leakage cases.
- There is no automated dynamic red-team harness for LLM behavior; semantic review remains manual.

### 4. Test Coverage & Quality Gates — 4.4 / 5

**Strengths**

- Tests cover structure, schema values, package integrity, skill/source parity, dashboard syntax, doc consistency, config permutations, state-machine contracts, conventional commit parity, release glob matching, and routing eval parser/scoring logic.
- The suite is fast enough to be run frequently.
- CI includes tests, PII scan, changelog gate, conventional commits, and skill parity.

**Gaps**

- Four tests are skipped, and at least some skipped areas represent intentional future assertions rather than irrelevant checks.
- `jsonschema` was unavailable in the local environment due to a package-index 403, so schema-validation coverage was skipped in this run.
- Manual semantic review is documented but not CI-gated.

### 5. Maintainability & Documentation — 4.7 / 5

**Strengths**

- README, START_HERE, CONTRIBUTING, DATA_CONTRACT, PRIVACY, HARDENING, SECURITY, ROADMAP, schemas, tests README, and feature plans are unusually comprehensive.
- Changelog discipline is strong and follows a recognizable Keep a Changelog structure.
- The feature-plan archive preserves architectural reasoning and implementation history.

**Gaps**

- The amount of documentation is a strength but also creates drift risk; existing doc-consistency tests mitigate this but cannot validate every narrative claim.

### 6. Release Engineering & Supply Chain — 4.5 / 5

**Strengths**

- `dossier.skill` is built from source with deterministic ordering and pinned ZIP timestamps.
- The build script writes a manifest, emits checksums, and verifies content-match against the committed artifact while excluding volatile manifest content.
- Release workflow includes artifact verification and provenance attestation.
- Conventional-commit and changelog gates create release-note discipline.

**Gaps**

- GitHub Actions are first-party but not SHA-pinned; HARDENING documents this as an accepted trade-off.
- There is no SBOM, which is reasonable for this project size but still a supply-chain completeness gap.

### 7. Usability & Onboarding — 4.3 / 5

**Strengths**

- The README communicates value proposition, setup, limitations, and upgrade paths clearly.
- START_HERE and examples lower the barrier for a first successful run.
- The dashboard and Dataview queries make the vault operational rather than merely archival.

**Gaps**

- The product depends on Claude Desktop/Cowork and skill installation, which is inherently less approachable than a hosted app.
- Users unfamiliar with Obsidian/Dataview/YAML frontmatter may need guidance beyond the quick start.

### 8. Portability & Reproducibility — 3.8 / 5

**Strengths**

- The dependency list is short.
- Tests are pure local reads with no external-service calls.
- The packaging script uses Python stdlib zipfile instead of relying on system `zip`, improving cross-platform behavior.

**Gaps**

- There is no lockfile, `pyproject.toml`, or explicit local Python-version file.
- CI targets Python 3.12 only; the local environment here was Python 3.14.4, which is useful signal but not a declared support target.
- The failed dependency install shows that offline or restricted-network development depends on already-cached packages unless contributors prepare an environment in advance.

### 9. Roadmap Clarity & Risk Management — 4.5 / 5

**Strengths**

- Known limitations are stated directly rather than hidden.
- Deferred features are separated from shipped behavior.
- HARDENING documents trade-offs and post-public security enablement.
- ROADMAP and feature plans give maintainers a reliable next-work queue.

**Gaps**

- Some roadmap items are intentionally outside this repo or depend on external workflows, so execution state must be kept synchronized across contexts.

---

## Priority Recommendations

### P1 — Improve Environment Reproducibility

Add one of the following:

- `pyproject.toml` with project metadata and test dependencies; or
- a constraints/lock file for CI and local development; and
- an explicit Python version declaration such as `.python-version` or an equivalent documented standard.

**Why:** The project’s release engineering is stronger than its local environment reproducibility. Closing this gap would make contributor setup and offline validation more predictable.

### P2 — Turn Semantic Review Into a Scheduled Release Ritual

Keep semantic review manual, but make it operationally unavoidable before tags by adding a release-checklist item that references `tests/semantic-review-checklist.md` and the golden examples.

**Why:** LLM output quality is the main remaining assurance gap. It does not need to be a brittle CI gate, but it should be a required human release step.

### P2 — Document Skipped-Test Exit Criteria in One Place

Create or update a short table that maps each skipped test to:

- why it is skipped,
- what must change before enabling it,
- whether enabling it is a release blocker.

**Why:** Skips are currently acceptable, but skipped assertions should never become invisible debt.

### P3 — Add a Lightweight Contributor Task Matrix

Add a small table in CONTRIBUTING or README that tells contributors which commands to run for common change types:

| Change type | Required checks |
|---|---|
| Skill source | tests + build skill parity + semantic checklist |
| Schemas/examples | tests + schema validation |
| Docs only | tests relevant to docs consistency + changelog |
| Release workflow | tests + release artifact verifier review |

**Why:** The repo has excellent checks; this would make choosing the right subset easier.

### P3 — Revisit SBOM / Action Pinning Only If Dependency Surface Grows

No immediate action needed. If the project adds non-first-party GitHub Actions, publishes to registries, or adds runtime dependencies, revisit SHA pinning and SBOM generation.

---

## Final Verdict

**Grade: A- / 91**

Dossier is production-ready as a local-first job-search operations vault and AI skill. Its strongest attributes are architectural clarity, safety posture, release discipline, and documentation quality. The main improvements needed to reach a solid A are not broad rewrites: they are targeted assurance upgrades around local environment reproducibility, skipped-test accountability, and making semantic LLM-output review a formal pre-release habit.
