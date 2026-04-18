# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Planned

- Phase 2: Routing ablation experiment (golden prompt test set, monolithic vs. split comparison)
- Phase 3: Five-skill split (dossier-evaluate, dossier-search, dossier-packet, dossier-prep, dossier-pipeline) — contingent on Phase 2 results
- Phase 3: dossier-researcher and dossier-qa subagents
- Phase 4: Build pipeline, open-source release prep, GitHub release v0.1.0

## [0.1.0] — 2026-04-17

### Added — Plugin Conversion (Phase 1)

- Converted Dossier from a standalone `.skill` ZIP bundle into a proper Claude Code plugin
- Plugin manifest at `.claude-plugin/plugin.json` with name, version, description, homepage
- Skill migrated to `skills/dossier/` with updated frontmatter (`allowed-tools` added for least-privilege)
- `hooks/hooks.json` — deterministic policy enforcement via Claude Code hook system:
  - `PreToolUse` hook: blocks external MCP writes (Notion, Gmail, Calendar, Apollo) pending user confirmation
  - `PostToolUse` hook: runs PII scan after any Write to vault artifact folders
- `bin/dossier-lint` — PII scanner for vault artifacts (email, phone, SSN, Notion UUIDs, custom deny-list)
- `bin/dossier-lint-hook` — PostToolUse wrapper that selectively lints vault artifact writes
- `settings.json` — Default permission policy (read vault artifacts; deny writes to cv.md, profile.md, secret files)
- `agents/dossier-researcher.md` — Read-only company/market research subagent (WebSearch, WebFetch, Read, Glob, Grep)
- `agents/dossier-qa.md` — Vault artifact QA subagent (validates frontmatter, placement, naming, PII, grade-score consistency)
- `SECURITY.md` — Security policy with scope, reporting path, and Dossier-specific threat model
- `.github/ISSUE_TEMPLATE/bug_report.md` — Bug report template with skill version, mode, model, and PII-redaction reminder
- `.github/ISSUE_TEMPLATE/feature_request.md` — Feature request template
- `.github/pull_request_template.md` — PR checklist (SKILL.md line count, reference pointers, PII check, CHANGELOG)
- `.gitignore` — Excludes config.md, secrets, backups, caches, and OS artifacts

### Changed

- Skill file structure is now the plugin canonical location (`skills/dossier/`) — `skill-update/` remains as legacy development copy during transition
- SKILL.md: 460 lines (unchanged from post-refactor state) with 11 reference files

### Inherited from v1.0.0 (2026-04-16)

- Vault-first architecture: all pipeline state owned by local markdown files
- 14 workflow modes (0–13) plus Weekly Trend Report enhancement
- Skill refactor: SKILL.md under 500 lines, 11 reference files in `references/` loaded on demand
- Open-source copy in `open-source/` with template personal files and PII-clean content
