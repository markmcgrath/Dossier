## What Changed and Why

<!-- Describe the change and the motivation. Reference the relevant plan doc or issue. -->

## Modes Affected

<!-- Which modes does this change touch? List all. -->

## Checklist

- [ ] `skills/dossier/SKILL.md` is under 500 lines (`wc -l skills/dossier/SKILL.md`)
- [ ] Every `references/` pointer in SKILL.md resolves to a real file
- [ ] No skill references files outside its own directory
- [ ] `CHANGELOG.md` updated with a summary of the change
- [ ] If SKILL.md or any reference file was modified: open-source copy updated (`open-source/skill/`)
- [ ] PII check passed on open-source copy (no real names, emails, Notion IDs, company names from real applications)
- [ ] If hooks.json was modified: hook schema verified against current Claude Code docs
- [ ] If bin/ scripts were modified: scripts tested with PII and clean fixtures

## Testing Done

<!-- How did you verify this works? Describe the test prompt or scenario used. -->
