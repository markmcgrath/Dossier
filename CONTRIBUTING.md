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

- Bug fixes in the skill logic or scoring rubric
- Improvements to the evaluation framework (new dimensions, better calibration)
- Better templates (cv, profile, config)
- Documentation improvements
- Test coverage for untested modes
- Integrations with additional job boards or tools

## What We're Not Looking For

- Changes that weaken grading honesty (the whole point is accurate evaluation)
- Auto-send functionality (all outreach must remain draft-only)
- Features that require paid services beyond Claude Pro/Team
- Large refactors without prior discussion

## Style

- Keep SKILL.md readable. It's a prompt, not code — clarity matters more than brevity.
- Frontmatter schemas must stay compatible with Obsidian Dataview queries.
- Follow the naming conventions in README.md.

## Maintainer setup (one-time)

If you work from a clone that may contain personal context (real evals, names, Notion IDs, etc.), activate the shared pre-commit hook so commits are scanned for PII before they leave your machine:

```bash
# Point git at the tracked hooks directory
git config core.hooksPath .githooks

# Create a local, gitignored patterns file with your owner-specific regexes
cat > .github/scripts/pii_patterns.local.txt <<'EOF'
# One regex per line. Comments start with #.
# Replace the examples below with your own identifiers.
# YourSurname
# your-email-local-part
# 11111111-1111-1111-1111-111111111111
EOF
```

The hook runs `.github/scripts/pii_scan.py --staged` on every commit and blocks anything that matches either the generic patterns (committed) or the local patterns (your machine only). External contributors don't need this — the CI `pii-scan` job enforces the generic patterns on every PR.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be kind, be constructive.
