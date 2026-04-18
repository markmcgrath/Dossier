# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Planned

- End-to-end outcome tracking — auto-populate `outcome` field on evals as pipeline state transitions (phone screen → interview → offer/rejection).
- Automatic terminal archival — move company artifacts into `archive/[company-slug]/` when status reaches a terminal state, with no prompt required.
- Interview story tagging — link `stories.md` entries to `interview-prep/` artifacts so prep surfaces the right stories per role.

## [0.1.0] — 2026-04-17

### Added — Plugin Conversion

- Converted Dossier from a standalone `.skill` ZIP bundle into a proper Claude Code plugin
- Plugin manifest at `dossier-plugin/.claude-plugin/plugin.json` with name, version, description, homepage
- Skill migrated to `dossier-plugin/skills/dossier/` with updated frontmatter (`allowed-tools` added for least-privilege tool access)
- `dossier-plugin/hooks/hooks.json` — deterministic policy enforcement via Claude Code hook system:
  - `PreToolUse` hook: blocks external MCP writes (Notion, Gmail, Calendar, Apollo) pending user confirmation
  - `PostToolUse` hook: runs PII scan after any Write to vault artifact folders
- `dossier-plugin/bin/dossier-lint` — PII scanner for vault artifacts (email, phone, SSN, Notion UUIDs, custom deny-list)
- `dossier-plugin/bin/dossier-lint-hook` — PostToolUse wrapper that selectively lints vault artifact writes
- `dossier-plugin/settings.json` — Default permission policy (read vault artifacts; deny writes to cv.md, profile.md, secret files)
- `dossier-plugin/agents/dossier-researcher.md` — Read-only company/market research subagent (WebSearch, WebFetch, Read, Glob, Grep; no Write access)
- `dossier-plugin/agents/dossier-qa.md` — Vault artifact QA subagent (validates frontmatter, placement, naming, PII, grade-score consistency)
- `dossier-plugin/SECURITY.md` — Security policy with scope, reporting path, and Dossier-specific threat model
- `.github/ISSUE_TEMPLATE/bug_report.md` — Bug report template with skill version, mode, model, and PII-redaction reminder
- `.github/ISSUE_TEMPLATE/feature_request.md` — Feature request template
- `.github/pull_request_template.md` — PR checklist (SKILL.md line count, reference pointers, PII check, CHANGELOG)
- `.gitignore` — Excludes config.md, secrets, backups, caches, and OS artifacts

### Changed — Routing Improvements (Phase 2)

Routing ablation experiment (45-prompt golden test set, monolithic vs. five-skill split) found that splitting degraded 17.8% of prompts — all compound multi-step workflows — exceeding the 10% degradation threshold. Decision: remain monolithic. The experiment identified three description gaps that are fixed regardless of split decision:

- SKILL.md description: added `"tailor my CV"` as an explicit trigger phrase (Mode 11 was only reachable via body text)
- SKILL.md description: added `"health check"` and `"calibration report"` as explicit trigger phrases (Modes 0 and 13 had no description coverage)
- SKILL.md description: added negative scope sentence — `"Only trigger when there is a clear job application, offer, interview, or outreach context."` — to reduce false-positive risk on adjacent analytics topics

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
