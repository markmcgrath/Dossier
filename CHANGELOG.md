# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Status/outcome state machine — `skill/references/status-outcome-state-machine.md` defines a transition table binding every `status` value to an `outcome` value. Mode 1 sets the initial `(Evaluating, Pending)` pair; Mode 9's Application Status Sync proposes `(status, outcome)` updates together from email signals; Mode 0 health check flags any eval whose pair is not a row in the table. Last-event-wins — a rejection email applied to an `outcome: Interview` eval moves it to `(Rejected, Rejected)` without preserving the prior outcome. 90+ days cold detection is deferred (requires date arithmetic not yet implemented).
- Automatic terminal archival — `skill/references/terminal-archival.md` defines the archival procedure. When Mode 9's Application Status Sync proposes a terminal status (`Rejected`, `Passed`, `Offer-Declined`), the same batch approval also moves the company bundle (eval + outreach + cover-letter + interview-prep) into `archive/[slug]/`, preserving original folder nesting. Repeat archivals of the same company are versioned (`archive/[slug]-v2/`, `-v3/`, …) rather than merged. Path-style cross-references to artifacts being moved are silently rewritten to wikilink form so they survive the relocation. 90+ days cold detection remains manual.

### Changed

Routing ablation experiment (45-prompt golden test set, monolithic vs. five-skill split) found that splitting degraded 17.8% of prompts — all compound multi-step workflows — exceeding the 10% degradation threshold. Decision: remain monolithic. The experiment identified three description gaps that are fixed regardless of split decision:

- SKILL.md description: added `"tailor my CV"` as an explicit trigger phrase (Mode 11 was only reachable via body text)
- SKILL.md description: added `"health check"` and `"calibration report"` as explicit trigger phrases (Modes 0 and 13 had no description coverage)
- SKILL.md description: added negative scope sentence — `"Only trigger when there is a clear job application, offer, interview, or outreach context."` — to reduce false-positive risk on adjacent analytics topics

### Planned

- End-to-end outcome tracking — auto-populate `outcome` field on evals as pipeline state transitions (phone screen → interview → offer/rejection).
- Automatic terminal archival — move company artifacts into `archive/[company-slug]/` when status reaches a terminal state, with no prompt required.
- Interview story tagging — link `stories.md` entries to `interview-prep/` artifacts so prep surfaces the right stories per role.

## [1.0.0] — 2026-04-16

### Added

- Vault-first architecture: all pipeline state owned by local markdown files
- 14 workflow modes: Evaluate (Mode 1), Search (Mode 2), Portal Scan (Mode 2.1), Interview Prep (Mode 3), Company Research (Mode 4), Outreach (Mode 5), Cover Letter (Mode 6), Salary Negotiation (Mode 7), LinkedIn Browser (Mode 8), Gmail Inbox (Mode 9), Calendar Ops (Mode 10), Tailored CV with ATS export (Mode 11), Batch Pipeline (Mode 12), Calibration Report (Mode 13)
- Mode 0 health check with 6 validation checks
- 10-dimension scoring system with gate-pass override and configurable weights
- Notion optionality — Notion tracker is an optional mirror, not a requirement; vault-first workflow works without any Notion configuration
- Skill refactor: SKILL.md restructured to under 500 lines with 11 reference files in `references/` directory, loaded on demand to stay within token budget
- Open-source release: `open-source/` subfolder with PII-clean content, template personal files (`cv.template.md`, `profile.template.md`, `stories.template.md`, `config.template.md`), and public README
- `examples/` directory with fictional-company reference artifacts showing correct frontmatter, naming, and content structure
