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
- **Test coverage** — regression tests for fixed bugs, new fixtures showing edge cases, structural tests for new skill sections.
- **Integrations** — additional job boards or tools via MCP, as long as they work within the human-in-the-loop model.
- **Template improvements** — better defaults in `cv.template.md`, `profile.template.md`, `stories.template.md`, `config.template.md`.

## What We're Not Looking For

- **Changes that weaken grading honesty.** If a change suppresses negatives or inflates grades, it's a regression — see the "Grade honestly" rule in `CLAUDE.md`.
- **Auto-send functionality.** All outreach, applications, and external actions must remain draft-only. The skill drafts; the user sends.
- **Scraping, TOS-bypass, or CAPTCHA-defeat features.** Out of scope regardless of convenience.
- **Features that require paid services beyond a Claude subscription.** Dossier must remain usable with no additional vendor costs.
- **Large refactors without a prior issue.** Open an issue to discuss scope before sinking time into a big change.

## Style

- Keep SKILL.md readable. It's a prompt, not code — clarity matters more than brevity.
- Frontmatter schemas must stay compatible with Obsidian Dataview queries.
- Follow the naming conventions in README.md.

## Maintainer setup (one-time)

If you work from a clone that may contain personal context (real evals, names, Notion IDs, etc.), activate the shared pre-commit hook so commits are scanned for PII before they leave your machine:

```bash
# Point git at the tracked hooks directory
git config core.hooksPath .githooks

# Copy the gitignored patterns file from the template, then edit it
cp .github/scripts/pii_patterns.template.txt .github/scripts/pii_patterns.txt
# Open .github/scripts/pii_patterns.txt in your editor and uncomment /
# replace the example regexes with your own identifiers.
```

The hook runs `.github/scripts/pii_scan.py --staged` on every commit and blocks anything that matches either the generic patterns (committed) or the local patterns (your machine only — `pii_patterns.txt` is gitignored). External contributors don't need this — the CI `pii-scan` job enforces the generic patterns on every PR.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be kind, be constructive.
