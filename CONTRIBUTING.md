# Contributing to Dossier

Thanks for your interest in contributing. Dossier is a Claude skill for job search operations, and contributions that make it more useful for job seekers are welcome.

## How to Contribute

1. **Open an issue first.** Describe what you want to change and why. This avoids duplicate work and lets us discuss the approach before you invest time.

2. **Fork the repo** and create a feature branch from `main`.

3. **Make your changes.** If you're editing `SKILL.md`, test it by loading it into a Claude Project and running at least one Mode 1 evaluation against a real job description.

4. **Run the test suite** to verify nothing broke:
   ```bash
   DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v
   ```

5. **Open a pull request** against `main`. Include:
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
4. Repack `dossier.skill` from the updated `skill/` folder. The exact command depends on your packager — for the skill-creator tool included with Anthropic's Claude skill workflow:

   ```bash
   python -m scripts.package_skill /path/to/skill/ /tmp/out/ \
     && mv /tmp/out/skill.skill ./dossier.skill
   ```

   If you use a different packager, ensure the resulting ZIP contains `skill/SKILL.md` and `skill/references/*.md` (matching the on-disk layout). `tests/test_skill_package_parity.py` will fail in CI if the repack is stale or mis-shaped.
5. Run the test suite: `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v`

**PR checklist:**

- [ ] `SKILL.md` is under 500 lines
- [ ] Every `references/` pointer resolves to a real file
- [ ] No skill references files outside its own directory
- [ ] `CHANGELOG.md` updated
- [ ] `open-source/` copy is current (no PII)
- [ ] `dossier.skill` repacked from `skill/` if either changed (`pytest tests/test_skill_package_parity.py` passes)
- [ ] PII scan clean: `python .github/scripts/pii_scan.py`

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
git config core.hooksPath .githooks
```

This installs the hook from `.githooks/commit-msg` for your local clone. The same check runs server-side in CI on every PR via `.github/scripts/check_conventional_commits.sh`. Bypass token: add `[skip-cc]` to any commit message in the PR range to short-circuit the CI check.

**Cutover note:** Only commits from Plan 19 (Stream A) onward are expected to follow CC format. Prior history (~77% non-CC) is unaffected and will produce truncated `git cliff` suggestions for release ranges spanning the cutover — supplement with manual CHANGELOG entries in that case.

---

## Tagging a Release

The release workflow fires only on semver-shaped tags. Accepted patterns:

- `vN.N.N` — e.g. `v1.2.3`, `v10.20.30`
- `vN.N.N-<suffix>` — e.g. `v1.0.0-rc.1`, `v0.0.0-rc-test`, `v0.0.0-dev+abc1234`

Tags that do not match (e.g. `vlatest`, `v-snapshot-2026-q3`, `v1`, `v1.0`) will not trigger publication. The operational prefixes `snapshot-*`, `archive-*`, and `wip-*` are reserved for non-release purposes and must not start with `vN…`.

**Pre-tag steps (maintainer):**

1. Ensure all PRs are merged and CI is green on `main`.
2. Run `git cliff --unreleased --tag vX.Y.Z` to preview a suggested CHANGELOG section. git-cliff is a maintainer-only tool — install via `cargo install git-cliff` or `brew install git-cliff`. This step can be skipped if git-cliff is not installed; write the CHANGELOG entry manually.
3. Manually paste/edit the suggestion into `CHANGELOG.md` as a new `## [vX.Y.Z] — YYYY-MM-DD` block above `## [Unreleased]`. Re-add an empty `## [Unreleased]` above. Preserve any `### Planned` content verbatim — git-cliff does not emit it.
4. Commit: `git commit -am "chore(release): vX.Y.Z"`.
5. Tag: `git tag -a vX.Y.Z -m "Release X.Y.Z"`.
6. Push: `git push origin main vX.Y.Z`.

---

## Routing eval (optional, pre-tag)

Before tagging a release, run the eval harness locally to catch routing
regressions:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
python .github/scripts/run_routing_evals.py \
  skill/SKILL.md tests/golden_prompts/routing_test_set.md \
  --max-prompts 5     # quick dry-run
python .github/scripts/run_routing_evals.py \
  skill/SKILL.md tests/golden_prompts/routing_test_set.md
  # full run, ~30-90s
```

Required for maintainers tagging from the canonical repo (CI runs the
same gate). Optional for fork contributors — the CI step skips when
`ANTHROPIC_API_KEY` is absent.

---

## Conduct

Be direct and constructive. If something is wrong, say what's wrong and propose a fix. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.