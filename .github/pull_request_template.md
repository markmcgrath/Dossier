<!-- Thanks for contributing! Please read CONTRIBUTING.md if you haven't already.
     Open an issue first for anything non-trivial so we can align on scope. -->

## Summary

<!-- What does this PR do, and why? One or two sentences. -->

## Changes

<!-- Bulleted list of what changed. Focus on the "what", not the diff. -->

## Testing

<!-- How did you verify this works?
     - For skill edits: "Loaded skill into Claude Desktop, ran Mode 1 against [JD type]"
     - For test changes: "pytest output attached"
     - For docs: "Verified links resolve, ran PII scan" -->

## Checklist

- [ ] `SKILL.md` is under 500 lines (if modified)
- [ ] Every `references/` pointer resolves to a real file
- [ ] Tests pass: `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v`
- [ ] PII scan clean: `python .github/scripts/pii_scan.py`
- [ ] `CHANGELOG.md` updated (if user-facing change)
- [ ] No personal data in any committed file
