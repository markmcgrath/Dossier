# Release Hardening — Execution Plan

**Source:** `features/plan/Open Source Release Hardening Specification.md`
**Scope:** All 13 tasks from the hardening spec, triaged and ordered for execution
**Target:** The `open-source/` subfolder only — do not modify main vault files

---

## Triage Summary

All tasks target the `open-source/` folder. This is the public GitHub release copy. The main vault is unaffected.

| Task | Description | Status | Action |
|------|-------------|--------|--------|
| 1 | SECURITY.md | **NEEDED** | Create new file |
| 2 | GitHub Actions CI | **NEEDED** | Create `.github/workflows/ci.yml` |
| 3 | Remove dev artifacts | **NEEDED** | Delete `.pytest_cache/`, `__pycache__/`; update `.gitignore` |
| 4 | Fix START_HERE.md | **NEEDED** | Remove `/vault-template/` reference; rewrite to use existing `.template.md` files |
| 5 | Correct automation claims | **NEEDED** | One hit: README.md line 172 ("Files move into dated subfolders automatically") |
| 6 | GitHub Issue/PR templates | **NEEDED** | Create `.github/ISSUE_TEMPLATE/` and PR template |
| 7 | CHANGELOG.md | **NEEDED** | Create initial changelog |
| 8 | Support Matrix in README | **NEEDED** | Add section to README.md |
| 9 | Threat Model Summary in README | **NEEDED** | Add section to README.md |
| 10 | Secrets handling guidelines | **PARTIALLY EXISTS** | CLAUDE.md line 56 covers it; add brief note to README |
| 11 | Align Notion messaging | **NEEDED** | Fix CLAUDE.md line 19 (gives Notion authority over vault) and line 29 (says "update in place" not version) |
| 12 | LLM Safety section in README | **NEEDED** | Add section to README.md |
| 13 | Final consistency pass | **NEEDED** | Fix automation claim, verify wikilinks, check terminology |

---

## Execution Steps

All file paths are relative to `/sessions/kind-stoic-cori/mnt/Dossier/open-source/`. Execute in order.

---

### Step 1: Clean dev artifacts (Task 3)

**Delete these directories and their contents:**
- `open-source/.pytest_cache/`
- `open-source/tests/__pycache__/`

**Edit:** `open-source/.gitignore`

Add these lines after the existing `# OS files` section:

```
# Python / test artifacts
.pytest_cache/
__pycache__/
*.pyc
```

---

### Step 2: Create SECURITY.md (Task 1)

**Create file:** `open-source/SECURITY.md`

**Content:**

```markdown
# Security Policy

## Supported Versions

Only the latest release on the `main` branch is supported. There is no backport policy.

## Reporting a Vulnerability

If you discover a security issue, please report it privately:

- **GitHub:** Use [Security Advisories](../../security/advisories/new) to open a private disclosure.
- **Email:** If GitHub private disclosure is unavailable, email the repository maintainer (see profile).

**Expected response:** Acknowledgment within 72 hours. Fix targeted within 14 days for confirmed issues.

Please do not open public issues for security vulnerabilities.

## Scope

The following are considered security issues:

- Data leakage — personal data (CV content, company names, email addresses) exposed through generated artifacts or logs
- Prompt injection — external content (job descriptions, emails, pasted text) manipulating the skill into unsafe behavior
- Credential exposure — API keys, tokens, or passwords stored in or surfaced through vault files
- Unsafe handling of untrusted content — the skill executing instructions embedded in job postings or email bodies

## Out of Scope

- User misuse (e.g., intentionally pasting secrets into vault files)
- Integrations not documented in the project (third-party tools, custom MCP servers)
- AI model accuracy — the skill produces advisory output, not authoritative decisions

## Disclosure Policy

We follow coordinated disclosure:

1. Reporter submits privately.
2. Maintainer acknowledges and investigates.
3. Fix is developed and tested.
4. Fix is released before public announcement.
5. Reporter is credited (unless they prefer anonymity).
```

---

### Step 3: Create GitHub Actions CI (Task 2)

**Create directory:** `open-source/.github/workflows/`

**Create file:** `open-source/.github/workflows/ci.yml`

**Content:**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install pytest pyyaml

      - name: Run tests
        run: pytest tests/ -v
```

**Note:** The test suite imports `pytest`, `pyyaml`, `zipfile`, `pathlib`, and `os` — all stdlib except pytest and pyyaml. No `requirements.txt` exists, so dependencies are inlined in the workflow. Also create a `requirements.txt` for local use:

**Create file:** `open-source/requirements.txt`

```
pytest>=7.0
pyyaml>=6.0
```

---

### Step 4: Create GitHub Issue and PR templates (Task 6)

**Create directory:** `open-source/.github/ISSUE_TEMPLATE/`

**Create file:** `open-source/.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug Report
about: Report a problem with Dossier
labels: bug
---

## Description

What happened?

## Steps to Reproduce

1.
2.
3.

## Expected Behavior

What should have happened?

## Actual Behavior

What happened instead?

## Environment

- OS:
- Python version:
- Obsidian version (if applicable):
- Claude model:
```

**Create file:** `open-source/.github/ISSUE_TEMPLATE/feature_request.md`

```markdown
---
name: Feature Request
about: Suggest an improvement to Dossier
labels: enhancement
---

## Problem

What problem does this solve?

## Proposed Solution

How should it work?

## Alternatives Considered

What other approaches did you consider?
```

**Create file:** `open-source/.github/pull_request_template.md`

```markdown
## Summary

What does this PR do?

## Changes

-

## Test Coverage

- [ ] Existing tests pass (`pytest tests/ -v`)
- [ ] New tests added (if applicable)

## Checklist

- [ ] Documentation updated (if behavior changed)
- [ ] No breaking changes (or documented in summary)
- [ ] No PII or credentials included
```

---

### Step 5: Create CHANGELOG.md (Task 7)

**Create file:** `open-source/CHANGELOG.md`

```markdown
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
```

---

### Step 6: Fix START_HERE.md (Task 4)

**Edit:** `open-source/START_HERE.md`

**Replace lines 49–65 (the "Set up the vault" section):**

Current text:
```
### 3. Set up the vault

Explain the vault structure:

- evals/
- outreach/
- cover-letters/
- interview-prep/
- research/
- daily/
- weekly/
- archive/
- dashboard.md

Then:
- Ask the user where they want to store their vault (local folder or Obsidian)
- Help them copy or recreate the structure from `/vault-template/`
```

Replace with:
```
### 3. Set up the vault

Explain the vault structure (see `README.md` for full layout).

The repository IS the vault — there is no separate template to copy. The user should:

1. Clone this repository
2. Rename `cv.template.md` → `cv.md` and fill in their work history
3. Rename `profile.template.md` → `profile.md` and fill in their targeting preferences
4. Rename `stories.template.md` → `stories.md` (optional, for behavioral interview prep)
5. Rename `config.template.md` → `config.md` and add their Notion tracker IDs (optional)
6. Open the folder in Obsidian as a vault, or work with it via Claude directly

The subfolder structure (`evals/`, `outreach/`, `cover-letters/`, etc.) is already in place.
```

---

### Step 7: Fix automation claim (Task 5)

**Edit:** `open-source/README.md` line 172

**Current:** `Files move into dated subfolders automatically.`

**Replace with:** `When Claude detects these thresholds, it moves older files into dated subfolders.`

---

### Step 8: Fix Notion messaging in CLAUDE.md (Task 11)

**Edit:** `open-source/CLAUDE.md` line 19

**Current:**
```
If you configure a Notion tracker, it owns pipeline state (grade, status, score). The vault owns narrative content. If they disagree: Notion wins for status, markdown wins for content. If Notion is not configured, the vault is the sole source of truth.
```

**Replace with:**
```
The vault owns all pipeline state and narrative content. If a Notion tracker is configured, it serves as an optional mirror — the vault is always the source of truth.
```

**Edit:** `open-source/CLAUDE.md` line 29

**Current:** `5. If a file already exists for the same company + date, update in place.`

**Replace with:** `5. If a file already exists for the same company + date, version with `-v#` suffix (see SKILL.md dedup rules).`

---

### Step 9: Add sections to README.md (Tasks 8, 9, 10, 12)

**Edit:** `open-source/README.md`

**Insert the following four sections after the "Governance" section (after line 239: `- LICENSE → MIT`) and before the "Source-of-truth model" section.**

```markdown

---

## Support Matrix

**Supported:**

- Vault-first workflow with local markdown files and Obsidian
- Claude-assisted artifact generation via the Dossier skill
- Obsidian v1.11.7+ with Dataview plugin for dashboard queries
- Python 3.11+ for running the test suite

**Optional:**

- Notion tracker mirroring (vault remains source of truth)
- Gmail, Google Calendar, and Apollo integrations (require MCP connectors)
- LinkedIn browser automation via Claude in Chrome

**Not supported:**

- Autonomous job applications or unsupervised outbound messaging
- Scraping, automation against platform TOS, or CAPTCHA bypassing
- Use without human review of all generated artifacts

---

## Security Model

Dossier is an assistive system, not an autonomous one. These principles are enforced throughout the skill:

1. **Human-in-the-loop.** All external actions (sending emails, submitting applications, posting messages) require explicit user approval. The skill drafts; the user sends.
2. **External content is untrusted.** Job descriptions, recruiter emails, and pasted text may contain prompt injection attempts or misleading claims. The skill's Content Trust Boundary (see SKILL.md) prevents external content from overriding grading criteria or user preferences.
3. **No automatic execution.** The skill never executes instructions found in job postings, emails, or other external content, regardless of how they are phrased.
4. **No credential storage.** API keys, tokens, and passwords must never be stored in vault markdown files. Use environment variables or platform secret stores. The `.gitignore` excludes `config.md` (which may contain Notion IDs) from version control.
5. **User responsibility.** The user owns all data in the vault and all decisions made based on skill output. Model output is advisory, not authoritative.

For the full threat model and data flow documentation, see [PRIVACY.md](PRIVACY.md) and [DATA_CONTRACT.md](DATA_CONTRACT.md).

---

## LLM Safety

Dossier generates evaluations, outreach drafts, and interview prep using Claude. Keep in mind:

- Model output is advisory. Grades, scores, and recommendations reflect pattern-matching against the JD and your CV — they are not authoritative assessments.
- External content (job postings, emails, company descriptions) may contain manipulative or inaccurate claims. The skill flags suspicious signals (see ghost job detection) but cannot guarantee accuracy.
- Always review generated artifacts before acting on them. This applies especially to outreach messages, cover letters, and salary negotiation scripts.
- The skill includes a bias caveat on every evaluation for this reason.

---

## Secrets Handling

Never store API keys, tokens, passwords, or credentials in vault markdown files. This includes `config.md`, eval files, and outreach drafts.

If you need to configure integrations (Notion, Gmail, Calendar), use environment variables or your platform's secret management. The `.gitignore` excludes `config.md` from version control to prevent accidental commits, but the file itself should not contain raw secrets — only identifiers like Notion page IDs.

See [PRIVACY.md](PRIVACY.md) for the full data handling policy.
```

---

### Step 10: Final consistency pass (Task 13)

After completing all previous steps, verify:

1. **Broken references:** Search all `.md` files in `open-source/` for references to `/vault-template/`. There should be zero hits after Step 6.
2. **Automation claims:** Search for "automatically" in all `.md` files. The only remaining hit should be in `README.md` line 193 ("All new evals created via Mode 1 include the full field set automatically") — this is accurate and refers to Mode 1 behavior, not autonomous file operations.
3. **Terminology consistency:** Confirm these terms are used consistently:
   - "vault" (not "workspace" or "project folder") for the Dossier directory
   - "eval" (not "evaluation file" or "assessment") for `evals/` artifacts
   - "artifact" (not "document" or "output") for generated files
4. **No TODOs or placeholders:** Search for `TODO`, `FIXME`, `TBD`, `PLACEHOLDER`, `XXX` in non-planning `.md` files. Should be zero hits.
5. **New files exist:** Confirm these files were created:
   - `open-source/SECURITY.md`
   - `open-source/CHANGELOG.md`
   - `open-source/requirements.txt`
   - `open-source/.github/workflows/ci.yml`
   - `open-source/.github/ISSUE_TEMPLATE/bug_report.md`
   - `open-source/.github/ISSUE_TEMPLATE/feature_request.md`
   - `open-source/.github/pull_request_template.md`
6. **Dev artifacts removed:** Confirm `.pytest_cache/` and `tests/__pycache__/` are deleted.
7. **Tests pass:** Run `cd open-source && pytest tests/ -v` and confirm all tests pass. If any tests fail due to changes made in this plan, fix them.
8. **PII check:** Run a grep across `open-source/` for personal identifiers — your name (full and variants), your email local-part, any Notion workspace IDs (UUIDs and 32-char hex), real employer names, and local user paths. Any hits in non-`.gitignore`-excluded files must be false positives (e.g., "markdown") — true hits must be redacted.

---

## Files Summary

### New files (8):
- `SECURITY.md`
- `CHANGELOG.md`
- `requirements.txt`
- `.github/workflows/ci.yml`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/pull_request_template.md`

### Modified files (4):
- `.gitignore` — add Python/test artifact patterns
- `START_HERE.md` — remove `/vault-template/` reference, rewrite setup instructions
- `CLAUDE.md` — fix Notion authority claim (line 19), fix versioning instruction (line 29)
- `README.md` — fix automation claim (line 172), add Support Matrix / Security Model / LLM Safety / Secrets Handling sections

### Deleted (2 directories):
- `.pytest_cache/`
- `tests/__pycache__/`
