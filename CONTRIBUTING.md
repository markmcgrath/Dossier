## Before you start

Read these documents in order before contributing:

- `README.md` — product model and quick start
- `CLAUDE.md` — operating contract for Claude agents working in the vault
- `DATA_CONTRACT.md` — ownership boundaries between user files and system files
- `tests/README.md` — what the test suite validates and how to run it
- `HARDENING.md` — release and security posture, known trade-offs
- `ROADMAP.md` — deferred work and exit criteria for currently-skipped tests
- `tests/semantic-review-checklist.md` — per-release human review rubric for model behavior

---

# Contributing to Dossier

Thanks for your interest in contributing. Dossier is a Claude skill for job search operations, and contributions that make it more useful for job seekers are welcome.

## How to Contribute

1. **Open an issue first.** Describe what you want to change and why. This avoids duplicate work and lets us discuss the approach before you invest time.

2. **Fork the repo** and create a feature branch from `main`.

3. **Make your changes.** If you're editing `SKILL.md`, test it by loading it into a Claude Project and running at least one Mode 1 evaluation against a real job description.

4. **Set up your dev environment.** Dossier requires Python 3.12 (declared in `pyproject.toml` and pinned in `.python-version`). From the repo root:
   ```bash
   python -m venv .venv
   # Activate: source .venv/bin/activate (POSIX) or .venv\Scripts\activate (Windows)
   pip install -r requirements.txt
   # Or, equivalently, install the dev extras from pyproject.toml:
   # pip install -e ".[dev]"
   ```
   Dependencies (full list): `pytest`, `pyyaml`, `jsonschema`, and `tomli` (Python <3.11 only — stdlib `tomllib` covers it from 3.11 onwards).

5. **Run the test suite** to verify nothing broke:
   ```bash
   DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v
   ```
   All tests should pass; a small number of skips (~3–4 depending on environment) is expected — see `tests/SKIPPED_TESTS.md`.

6. **Open a pull request** against `main`. Include:
   - What changed and why
   - How you tested it
   - Any breaking changes or migration steps

## What We're Looking For

Concrete examples of welcome contributions:

- **Bug fixes in the skill** — e.g., Mode 1 returns an invalid grade value, Mode 2 mis-formats search queries, a frontmatter field is missing from files created by a specific mode.
- **Scoring rubric refinements** — new dimensions, better weighting, calibration against real JDs, clearer anti-patterns. Include the reasoning and, ideally, example JDs showing the old vs. new behavior.
- **Documentation improvements** — clarifications, typo fixes, better examples, new troubleshooting entries, more precise language in `PRIVACY.md` / `DATA_CONTRACT.md`.
- **New example artifacts** — the `examples/` folder is meant to show "what good looks like." Additional fictional-company examples (different industries, role levels, edge cases like ghost jobs or prompt injection) are welcome.
- **Test coverage** — regression tests for fixed bugs, new fixtures that exercise edge cases, or structural checks for new modes or reference files.

## What We're NOT Looking For

- Autonomous application features (auto-submit, auto-send)
- Changes that remove the human-in-the-loop requirement
- Features that store or transmit personal vault data to external services
- Rewriting modes that are working correctly — refinements are welcome, rewrites need a strong case

## Skill Development Workflow

The Dossier skill lives in `skill/` and is packaged as a `.skill` ZIP bundle (`dossier.skill`) for distribution.

**To edit the skill:**

1. Edit files in `skill/` — `SKILL.md` is the entry point; mode details live under `skill/references/`.
2. Keep `SKILL.md` under 500 lines.
3. Verify all `references/` pointers in `SKILL.md` resolve to actual files.
4. Repack `dossier.skill` from the updated `skill/` folder using the in-repo packager:

   ```bash
   bash .github/scripts/build_skill.sh
   cp dist/dossier-*.skill dossier.skill
   ```

   The packager emits `dist/dossier-<version>.skill`; copy it over the committed `dossier.skill` so `tests/test_skill_package_parity.py` stays green. The ZIP contains `skill/SKILL.md`, `skill/manifest.json`, and `skill/references/*.md` (matching the on-disk layout). The parity test will fail in CI if the repack is stale or mis-shaped.
5. Run the test suite: `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v`

**PR checklist:**

- [ ] `SKILL.md` is under 500 lines
- [ ] Every `references/` pointer resolves to a real file
- [ ] No skill references files outside its own directory
- [ ] `CHANGELOG.md` updated
- [ ] `dossier.skill` repacked from `skill/` if either changed (`pytest tests/test_skill_package_parity.py` passes)
- [ ] PII scan clean: `python .github/scripts/pii_scan.py`

### Which checks for which changes

The full test suite is fast (~3 s) and the right default for any PR. The table below names the additional checks that matter for each change type so you can sanity-check before opening the PR.

| Change type | Required checks |
|---|---|
| `skill/` source (SKILL.md, references/, manifest) | full test suite + `bash .github/scripts/build_skill.sh` (parity) + semantic-review checklist before the next release |
| `schemas/` or `examples/` | full test suite — `test_schema_validation.py` runs when `jsonschema` is installed; `test_vault_schema.py` runs always |
| Docs only (`README.md`, `CONTRIBUTING.md`, `HARDENING.md`, etc.) | full test suite (covers `test_docs_consistency.py`) + `CHANGELOG.md` entry under `## [Unreleased]` |
| `.github/workflows/` or release scripts | full test suite + manual review of `verify_skill_artifact.py` output on a draft / `-rc` release before tagging the stable version |
| `tests/` only | full test suite + update [`tests/SKIPPED_TESTS.md`](tests/SKIPPED_TESTS.md) if the skip surface changes |
| `pyproject.toml`, `requirements.txt`, `.python-version` | full test suite + fresh-venv install (`python -m venv .venv && pip install -r requirements.txt && pytest`) to confirm no transitive breakage |

CI enforces five required status checks regardless of change type (`pii-scan`, `test (3.12)`, `changelog-check`, `conventional-commits`, `skill-parity`). See [HARDENING.md §7](HARDENING.md#7-ci-and-test-coverage) for the canonical list.

## Conventional Commits

All new commits should follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>)?(!)?:  <description>
```

**Valid types** and their CHANGELOG sections:

| Type | CHANGELOG section |
|---|---|
| `feat` | Added |
| `fix` | Fixed |
| `perf` | Changed |
| `refactor` | Changed |
| `docs` | Documentation |
| `revert` | Changed |
| `chore` | (dropped — not shown in CHANGELOG) |
| `build` | (dropped) |
| `ci` | (dropped) |
| `style` | (dropped) |
| `test` | (dropped) |

**Breaking changes** — add `!` after the type/scope (e.g. `feat!: ...` or `feat(scope)!: ...`) or include `BREAKING CHANGE:` in the commit footer. Breaking commits appear with a `[BREAKING]` callout in the generated output regardless of type.

**Scope** is optional. Use a lowercase noun describing the affected area (e.g. `feat(ci):`).

**Auto-generated messages** (`Merge ...`, `Revert "..."`) are allowed without format validation.

**Opt-in to the local commit-msg hook:**

```bash
bash tools/setup-hooks.sh
```

That runs `git config core.hooksPath .githooks` and confirms the hook is wired up. The shell one-liner works too if you prefer:

```bash
git config core.hooksPath .githooks
```

Either way installs the hook from `.githooks/commit-msg` for your local clone. The same check runs server-side in CI on every PR via `.github/scripts/check_conventional_commits.sh`. Bypass token: add `[skip-cc]` to any commit message in the PR range to short-circuit the CI check.

**Cutover note:** Only commits from Plan 19 (Stream A) onward are expected to follow CC format. Prior history (~77% non-CC) is unaffected and will produce truncated `git cliff` suggestions for release ranges spanning the cutover — supplement with manual CHANGELOG entries in that case.

---

## Tagging a Release

The release workflow fires only on semver-shaped tags. Accepted patterns:

- `vN.N.N` — e.g. `v1.2.3`, `v10.20.30`
- `vN.N.N-<suffix>` — e.g. `v1.0.0-rc.1`, `v0.0.0-rc-test`, `v0.0.0-dev+abc1234`

Tags that do not match (e.g. `vlatest`, `v-snapshot-2026-q3`, `v1`, `v1.0`) will not trigger publication. The operational prefixes `snapshot-*`, `archive-*`, and `wip-*` are reserved for non-release purposes and must not start with `vN…`.

**Pre-tag steps (maintainer):**

1. Ensure all PRs are merged and CI is green on `main`.
2. **Run semantic review (required).** Walk [`tests/semantic-review-checklist.md`](tests/semantic-review-checklist.md) end-to-end against the three golden artifacts in `examples/golden/`. All five sections (grade accuracy, concern inclusion, prompt-injection refusal, outreach tone, frontmatter + dashboard) must pass. This is the human-review gate for LLM output quality that CI cannot enforce — record completion (date + checklist version) in the release PR description or the release notes draft. If any section fails, fix the underlying skill behaviour before tagging.
3. *(Optional)* Run the routing evals harness — see [§Routing eval (optional, pre-tag)](#routing-eval-optional-pre-tag) below. Catches holistic routing regressions before they ship in a release.
4. Run `git cliff --unreleased --tag vX.Y.Z` to preview a suggested CHANGELOG section. git-cliff is a maintainer-only tool — install via `cargo install git-cliff` or `brew install git-cliff`. This step can be skipped if git-cliff is not installed; write the CHANGELOG entry manually.
5. Manually paste/edit the suggestion into `CHANGELOG.md` as a new `## [vX.Y.Z] — YYYY-MM-DD` block above `## [Unreleased]`. Re-add an empty `## [Unreleased]` above. Preserve any `### Planned` content verbatim — git-cliff does not emit it.
6. Commit: `git commit -am "chore(release): vX.Y.Z"`.
7. Tag: `git tag -a vX.Y.Z -m "Release X.Y.Z"`.
8. Push: `git push origin main vX.Y.Z`.
9. After the release workflow finishes, run the post-release install smoke — see [§Post-release install smoke (manual)](#post-release-install-smoke-manual).

---

## Post-release install smoke (manual)

The release workflow's structural smoke (`verify_skill_artifact.py`) confirms the bundle is a valid ZIP with the right entries. It does not exercise the user-facing install path — download the asset, verify the checksum, load it into a fresh Claude project, and run a mode. This manual checklist closes that gap. Roughly ten minutes; catches release workflow silent failures, bad checksums, version-string drift, and skill-body regressions that prevent the bundle from loading.

Run after `release.yml` reports green on the tag:

1. **Confirm the Release page** at `https://github.com/markmcgrath/Dossier/releases/tag/vX.Y.Z` exists with both assets attached:
   - `dossier-vX.Y.Z.skill`
   - `dossier-vX.Y.Z.skill.sha256`
2. **Confirm the release notes** match the `## [vX.Y.Z] —` section of `CHANGELOG.md`. The workflow's awk extractor falls back to `[Unreleased]` or a placeholder when the per-tag section is missing — if you see "no CHANGELOG section found" or notes you don't recognize, fix the CHANGELOG and edit the Release body.
3. **Download and verify checksum** in a scratch directory (the user-facing path from `README.md` §Upgrading):
   ```bash
   curl -LO https://github.com/markmcgrath/Dossier/releases/download/vX.Y.Z/dossier-vX.Y.Z.skill
   curl -LO https://github.com/markmcgrath/Dossier/releases/download/vX.Y.Z/dossier-vX.Y.Z.skill.sha256
   sha256sum -c dossier-vX.Y.Z.skill.sha256
   ```
   Expected: `dossier-vX.Y.Z.skill: OK`. A failure here means the uploaded asset is corrupted or the `.sha256` was generated from a different build — investigate before advertising the release.
4. **Verify the bundle's manifest** (no Claude required):
   ```bash
   unzip -t dossier-vX.Y.Z.skill
   unzip -p dossier-vX.Y.Z.skill skill/manifest.json | python -m json.tool
   ```
   The manifest's `version` field should equal the tag verbatim, with the leading `v` (e.g. `"version": "v1.3.2"`). The `commit` field should match the SHA the tag points at — verify with `git rev-parse vX.Y.Z^{commit}` (the `^{commit}` peeling matters: on an annotated tag, plain `git rev-parse vX.Y.Z` returns the *tag object's* SHA, not the commit SHA the tag points at).
5. **Install into a fresh Claude project** (Cowork → Customize → Skills → upload `dossier-vX.Y.Z.skill`) and confirm the skill description loads — Claude should list Dossier and its modes when asked "what skills do you have?".
6. **Run one Mode 1 evaluation** against a known fixture, e.g. `tests/fixtures/jd_strong_fit.md`. Compare the output shape against `examples/golden/eval-strong-fit.md` — frontmatter shape, scoring dimensions, grade. Substantive drift from the golden is a "investigate or rollback" signal, not a release-go signal.
7. **(Security-relevant, optional)** Run Mode 1 against `tests/fixtures/jd_injection_attempt.md` and confirm the response surfaces a Prompt Injection Notice without acting on the injected instructions. Compare against `examples/golden/eval-injection-response.md`. Drift here is a security regression and warrants a follow-up patch even if every other check passed.

If any step fails, do not advertise the release publicly. The standard recovery is a follow-up patch tag (`vX.Y.Z+1`), not deletion — a deleted tag forces anyone who already pulled to re-fetch and produces an audit-log gap. Mark the release as a pre-release while investigating with `gh release edit vX.Y.Z --prerelease` if you want to discourage downloads in the meantime.

---

## Routing eval (optional, pre-tag)

`tools/run_routing_evals.py` is a maintainer-side aid that runs the 45
golden prompts (`tests/golden_prompts/routing_test_set.md`) through the
local `claude` CLI with `skill/SKILL.md` as system context, scores
routing decisions against expected outcomes, and writes a markdown
report. It does NOT use the Anthropic SDK or `ANTHROPIC_API_KEY` —
invocations draw from your existing Claude Code subscription.

Run before tagging a release to catch holistic routing regressions that
the structural test (`tests/test_routing_golden.py`) wouldn't catch:

```bash
# Quick dry-run on 5 prompts
python tools/run_routing_evals.py --max-prompts 5

# Full run (~45 prompts)
python tools/run_routing_evals.py
```

Requires `claude` (Claude Code CLI) on PATH and authenticated. The
harness exits 0 on completion regardless of accuracy — score acceptability
is your judgment call. The report (default `routing-evals-report.md`)
captures per-prompt detail and any failures with the model's rationale.

This step is optional and not enforced in CI. Routing regressions are
also caught in normal Claude Code use within hours of breaking SKILL.md.

---

## Conduct

Be direct and constructive. If something is wrong, say what's wrong and propose a fix. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.