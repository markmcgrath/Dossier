# Implementation Plan — Dossier v2

**Status:** Ready for implementation
**Supersedes:** `../research/dossier-implementation-plan.md` (pre-vault-first draft)

---

## Overview

This plan consolidates six feature documents into a single implementation sequence. It corrects conflicts between the original documents, re-orders work by actual dependency, and flags risks the originals missed.

The plan is organized into seven streams. Streams A and B have no cross-dependencies and can run in parallel. Everything else chains off A.

## Streams

| Stream | Name | Est. Hours | Depends On | Doc |
|--------|------|-----------|------------|-----|
| A | [[01-architecture\|Architecture — Vault-First Migration]] | 5–7 | — | |
| B | [[02-governance\|Governance Docs]] | 2–3 | — | |
| C | [[03-foundation\|Foundation Features]] | 3–4 | A | |
| D | [[04-competitive\|Competitive Features]] | 6–8 | C | |
| E | [[05-advanced\|Advanced Features]] | 4–5 | C, D (partial) | |
| F | [[06-deferred\|Deferred & Speculative]] | 30+ | A–E stable | |
| — | [[07-risks\|Risks, Gaps & Open Questions]] | — | — | |

**Total estimated effort (Streams A–E):** 20–27 hours
**Stream F (email automation, batch, portal scanning):** 30+ hours, deferred

## Critical Findings from Review

These issues were discovered during the second-pass analysis. They are not in the original feature documents and must be addressed before or during implementation.

### 1. Skill File Is a ZIP Package

`dossier.skill` is a ZIP archive containing `SKILL.md` (764 lines) and `scoring-guide.md`. All edits require: extract, modify, repack. The original feature docs reference "SKILL.md" with line numbers as if it were a standalone file — those references are to the file *inside the package*, not a file on disk.

**Workflow for every skill edit:**
```bash
# Extract
unzip -o dossier.skill -d /tmp/skill-edit/

# Edit SKILL.md and/or scoring-guide.md

# Repack (from inside the extracted dir)
cd /tmp/skill-edit && zip -r /path/to/Dossier/dossier.skill SKILL.md scoring-guide.md
```

**Always back up** `dossier.skill` before editing, per CLAUDE.md rules.

### 2. Vault-First and Email Automation Conflict

The [[vault-first-architecture-spec|vault-first spec]] makes the vault the single source of truth. The [[../research/email-automation-plan|email automation plan]], written the same day, still uses Notion as the source of truth for all sequence triggers. These must be reconciled before email automation work begins. See [[06-deferred#Reconciliation Required]] for details.

### 3. Config Naming Inconsistency

`config.md` header says "Career Ops" but the skill is named "dossier." This should be corrected during Stream A.

### 4. Partial Vault-First Already Exists

The current SKILL.md (lines 22–32) already treats Notion as optional for Mode 1 logging. But Modes 9 and 10 (lines 641–738) still treat Notion as the primary data source. The migration is *completing* a half-done transition, not starting from scratch.

## Execution Principles

1. **One stream at a time, ship each stream before starting the next.** Streams A and B can overlap, but don't start C until A is verified.
2. **Backup before every skill edit.** Copy `dossier.skill` to `dossier.skill.bak-YYYY-MM-DD` before extracting.
3. **Verify after every edit.** Run a Mode 1 evaluation against a real JD after each stream ships. Run Mode 9 after Stream A specifically.
4. **Update README.md and config.md in the same commit as the skill changes.** Don't let docs drift from behavior.

## Source Documents

These feature docs informed this plan. They remain useful as reference but should not be followed directly — this plan supersedes their sequencing and resolves their conflicts.

- `../dossier-consolidated-assessment.md` — Merged analysis of deep research + gap analysis
- `../vault-first-architecture-spec.md` — Architecture spec for Notion decoupling
- `../research/deep-research-report.md` — External audit against engineering standards
- `../research/dossier-gap-analysis.md` — Competitive analysis and feature gaps
- `../research/dossier-implementation-plan.md` — Original phased implementation plan
- `../research/email-automation-plan.md` — Companion skill design for email cadence
