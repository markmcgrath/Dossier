# Implementation Plan — Dossier v2

**Status:** Streams A–E shipped (April–May 2026). See "Subsequent plans" at the bottom for plans 08+ that followed this v2 baseline.
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

## Subsequent plans

After the v2 streams above shipped, follow-on work continued under individually numbered plan docs in this folder. Each plan's `Status:` header is the source of truth for whether it has shipped; the table below is a navigation index, not a status mirror.

| # | Plan | Topic |
|---|------|-------|
| 08 | [[08-review-remediation]] | Post-v2 review remediation |
| 09 | [[09-release-hardening-execution]] | Release hardening execution |
| 10 | [[10-skill-refactor]] | Skill refactor |
| 12 | [[12-readme-revision]] | README revision |
| 13 | [[13-execution-prompt]] / [[13-quality-audit-remediation]] | Execution prompt + quality audit remediation |
| 14 | [[14-lead-pulse-dedup-v2]] | Lead pulse dedup v2 |
| 15 | [[15-recruiter-inbox-pulse-broadening]] | Recruiter inbox pulse broadening |
| 16 | [[16-test-suite-hardening]] | Test suite hardening |
| 17 | [[17-eval-schema-data-hygiene]] | Eval schema data hygiene |
| 18 | [[18-version-tag-release-pipeline]] | Version-tag release pipeline |
| 19 | [[19-routing-eval-harness]] | Routing eval harness — post-hoc stub for PR #43 |
| 20 | [[20-v1-3-1-and-phase-2-foundations]] | v1.3.1 cleanup and Phase 2 foundations |
| 21 | [[21-target-radar-brief]] | Target Radar brief stub (SUPERSEDED by Plan 25, see below) |
| 22 | [[22-quality-review-remediation]] | Quality review remediation |
| 23 | [[23-packets-and-folder-structure]] | Packets + folder-structure v2 (request item 1) |
| 24 | [[24-send-ready-contract-and-validator]] | Send-ready document contract + executable validator (request item 3) |
| 25 | [[25-target-radar-component]] | Target Radar as a standalone Dossier component, Mode 15 (request item 4) |
| 26 | 26-live-vault-cleanup-plan *(completed; spec doc not tracked in this repo — it contained live-vault paths)* | Live working-folder cleanup map (request item 2). Done. |
| 27 | [[27-outstanding-backlog]] | Outstanding-feature backlog triage (request item 5) |

Plan number 11 does not have a plan doc in this folder. Plan 19's doc was backfilled post-hoc from PR #43.

## Plans 23 to 27 cohort (June 2026) — Cross-plan reconciliation

Plans 23 through 27 came out of a single planning session covering five requests: standardize packets, clean the live working folder, enforce send-ready document hygiene, build Target Radar into Dossier, and triage remaining outstanding work. They are written to be executed by Claude Code CLI. The items below are authoritative where an individual plan's local text disagrees.

**Mode numbering.** Existing modes are 0 through 13. The two new modes are: Mode 14 = Packet Assembly (Plan 23), Mode 15 = Target Radar (Plan 25). Both source agents independently proposed "Mode 14"; Target Radar was reassigned to 15. Plan 25 text reads Mode 15 throughout.

**Bundle frozen file list grows from 17 to 21.** Four files are added under `skill/references/` and therefore enter the `dossier.skill` bundle: `mode14-packet-assembly.md` (Plan 23), `mode15-target-radar.md` (Plan 25), `SEND_READY_CONTRACT.md` and `send_ready_config.json` (Plan 24). When implementing, update all of these in lockstep to 21 entries: `tests/test_package.py` `EXPECTED_BUNDLE_ENTRIES` and its "expected 17 entries" docstring, the `DATA_CONTRACT.md` "17 files under a top-level `skill/` directory" sentence, and `.github/scripts/verify_skill_artifact.py` and `.github/scripts/build_skill.sh` if either enumerates bundle contents. Per-plan lines that say the count "becomes 18" are superseded by this paragraph.

**New top-level vault folders (folder-structure v2).** `packets/[company-slug]/[role-slug]/` (Plan 23), `target-radar/` (Plan 25), and `reference/` with subfolders (Plan 26, live working folder only). OSS scaffolding adds `packets/.gitkeep` and `target-radar/.gitkeep`; `reference/` is a live-vault construct created during cleanup, not shipped scaffolding. All slugs are lowercase-hyphen, consistent with existing eval slugs.

**Shared files edited by more than one plan.** `skill/SKILL.md`, `skill/references/file-conventions.md`, `DATA_CONTRACT.md`, and `README.md` are each touched by Plans 23, 24, and 25. Apply every plan's edits; in `SKILL.md` the new mode sections go in order (Mode 14 then Mode 15) after the Mode 13 block; in `file-conventions.md` the folder diagram must end up showing `packets/`, `target-radar/` (and the live cleanup adds `reference/`). Edits target the `skill/` source directory; rebuild the bundle with `.github/scripts/build_skill.sh`, never a hand-run `zip`.

**Recommended execution order.** 23 (folder structure and packets) first, then 24 (the validator gates packet finalization via `send_ready: true`), then 25 (Target Radar), then 26 (live cleanup, which relies on the packet convention from 23). 27 is independent and can land any time. Plan 26 operated on the live `Dossier` working folder, not this repo; it moved user data and has since been completed. Its spec doc is not tracked here because it contained live-vault paths.

**Vault supersede.** Plan 25 changes a prior canonical decision: Target Radar was designed as an upstream Commonplace brief (vault entries `2026-05-11-target-radar-brief-design` and `2026-05-27-dossier-plan21-target-radar-brief`). Building it into Dossier supersedes those. The user runs the `commonplace supersede` operation separately; Plan 25 only records the intent, and Plan 21's stub is annotated.

## Implementation guardrails (read before executing Plans 23 to 25)

A pre-execution review found defects that only bite when these plans run in sequence (Edit old-string targets and the bundle count shift after an earlier plan has already changed the file). Apply these corrections; they override any conflicting local instruction in the individual plans.

**Verify-before-edit.** Several plans give an old-string Edit target without quoting the live file (for example `tests/test_skill_structure.py` `test_all_modes_exist`'s mode list, and `SKILL.md`'s `description:` field tail). Before each Edit, read the actual file and match the exact current string including whitespace and trailing commas. Do not trust a paraphrased target.

**Bundle file count: increment per plan, never preemptively.** The frozen `EXPECTED_BUNDLE_ENTRIES` in `tests/test_package.py` and its "expected 17 entries" docstring must equal the bundle's real contents after each plan lands, so CI stays green between plans. Update the running total inside the same plan that adds each file: after Plan 23 = 18 (`mode14-packet-assembly.md`), after Plan 24 = 20 (`SEND_READY_CONTRACT.md` and `send_ready_config.json`), after Plan 25 = 21 (`mode15-target-radar.md`). Do not jump straight to 21 in Plan 23.

**Non-`.md` bundle members.** `send_ready_config.json` is a JSON file under `skill/references/`. Confirm `.github/scripts/build_skill.sh` packs all of `skill/references/*` (not only `*.md`); if it filters by extension, add `.json`. Add the literal `skill/references/send_ready_config.json` to `EXPECTED_BUNDLE_ENTRIES` and verify with `unzip -l dossier.skill`. Without this the validator hits config-not-found when run from an installed bundle.

**SKILL.md insertion order.** Mode sections are appended after the Mode 13 block in numeric order: Plan 23 inserts Mode 14, then Plan 25 inserts Mode 15 after the Mode 14 section (not after Mode 13). The `Key folders` line ends, in final state, with `... archive/ packets/ target-radar/` (Plan 23 appends `packets/`, Plan 25 appends `target-radar/` to the post-23 line, not to a line ending in `archive/`).

**Plan 26 command block is authoritative over its prose table.** Where Section 3's prose table and Section 5's command block disagree, run the command block. Specifically: (a) resolve the per-packet docx collision as `cv.docx` (the freshly exported tuned CV from the markdown source) versus `cv-legacy.docx` (the existing PascalCase `Mark-McGrath-CV.docx` submission copy), one consistent rule for every packet, not `cv-submission.docx` in one place and `cv.docx` in another. (b) `cover-letters/cover-openai-2026-05-07.md` stays REVIEW REQUIRED (three same-date OpenAI evals, role ambiguous), not an unflagged move. (c) The `daily-scan` root-versus-`daily/` `-vN` suffixes in the command block are placeholders: run `ls daily/daily-scan-YYYY-MM-DD*.md` first and pick the next free `-vN`; do not trust the hardcoded number.

**Plan 24 validator sketch.** `parse_frontmatter` returns the body string only: annotate it `-> str` (not `-> tuple[str]`), and drop the `conftest.py` snippet that implies a two-value return. Use one document-class detection approach (the `path.parents` form in the sketch); delete the divergent pseudocode above it.

**Plan 27 note.** Item B-7 (weekly-trend-report prerequisite docs) is a documentation item grouped under B for convenience; the "Group B = 7" count includes it.
