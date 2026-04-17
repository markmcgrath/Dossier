# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
- GitHub Actions CI pipeline
