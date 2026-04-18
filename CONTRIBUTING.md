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
4. Repack `dossier.skill` from the updated `skill/` folder.
5. Run the test suite: `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v`

**PR checklist:**

- [ ] `SKILL.md` is under 500 lines
- [ ] Every `references/` pointer resolves to a real file
- [ ] No skill references files outside its own directory
- [ ] `CHANGELOG.md` updated
- [ ] `open-source/` copy is current (no PII)
- [ ] PII scan clean: `python .github/scripts/pii_scan.py`

## Conduct

Be direct and constructive. If something is wrong, say what's wrong and propose a fix. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.