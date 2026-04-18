# Vault Template

This folder is a starter skeleton for a new Dossier vault. Copy it to the location where you want to keep your job-search artifacts, then follow `START_HERE.md` at the repo root for guided setup.

## What you get

Eight empty folders that match Dossier's artifact conventions:

- `evals/` — role evaluations (Mode 1 output): `eval-[company-slug]-[date].md`
- `outreach/` — LinkedIn / email outreach drafts (Mode 5): `outreach-[company-slug]-[date].md`
- `cover-letters/` — cover-letter drafts (Mode 6): `cover-[company-slug]-[date].md`
- `interview-prep/` — interview prep sheets (Mode 3): `prep-[company-slug]-[date].md`
- `research/` — company research briefs (Mode 4): `target-brief-[company-slug]-[date].md`
- `daily/` — daily scans, lead pulses, recruiter triage
- `weekly/` — weekly pipeline digests and week-aheads
- `archive/` — terminal applications are auto-moved here per company slug

Each folder carries a `.gitkeep` sentinel so git tracks the empty directory. You can delete `.gitkeep` once you add real artifacts.

## Also copy into your vault (from the repo root)

- `dashboard.md` — live Obsidian Dataview dashboard queries for the pipeline.
- `cv.template.md` → rename to `cv.md` and fill in your work history. This is the source of truth for capability fit.
- `profile.template.md` → rename to `profile.md` and fill in your target roles, match signals, and roles to avoid.
- `stories.template.md` → rename to `stories.md` (optional; most people build this as interviews happen rather than up front).
- `config.template.md` → rename to `config.md` (optional; only needed if you want Notion / Gmail / Calendar / Apollo integrations).

## Frontmatter conventions

Every artifact file uses YAML frontmatter. See `skill/references/file-conventions.md` for the full schema per file type. `examples/` at the repo root contains reference artifacts (example-eval, example-outreach, example-prep) with correct frontmatter you can copy.

## What not to put here

- `cv.md`, `profile.md`, `stories.md`, `config.md` — these live at your vault root, not in a subfolder.
- Credentials, API keys, or secrets of any kind. See `SECURITY.md` at the repo root.
