# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
- Ghost job detection with 4-tier legitimacy assessment
- Obsidian-compatible dashboard with Dataview queries
- Gmail domain filtering (allow-list / deny-list)
- STAR+R story bank template for behavioral interview prep
- Governance documentation: PRIVACY.md, DATA_CONTRACT.md, SECURITY.md
- Example artifacts: eval, outreach, and interview prep templates
- Test suite with pytest (vault schema, skill structure, antipattern detection)
- GitHub Actions CI pipeline with Python 3.11/3.12 matrix and automated PII scan gate

### Known Limitations

- **Model output is advisory, not authoritative.** Grades, scores, and recommendations reflect pattern matching between the JD and your profile — they're not expert assessments. Every eval ships with a bias caveat for this reason.
- **Notion sync is one-way and optional.** When enabled, the vault is the source of truth and Notion mirrors it; conflicts always resolve in favor of the vault. There's no reverse sync from Notion edits back to the vault.
- **End-to-end mode execution isn't automatically tested.** The test suite verifies structure (ZIP integrity, frontmatter schemas, SKILL.md sections, anti-patterns) but doesn't call Claude or exercise the modes against live JDs. LLM output quality is verified manually.
- **LinkedIn, Gmail, Calendar, and Apollo integrations require separate MCP connectors** and are out of scope for the core skill.
- **Ghost-job detection relies on heuristics** (posting age, specificity, comp transparency, recruiter patterns) and will both miss some real ghost jobs and false-flag some real roles. Treat the `legitimacy` field as directional, not definitive.
