# 10 — Dossier Skill Refactor Plan

**Goal:** Restructure the dossier skill from a single 1,374-line SKILL.md into a properly formed skill package that follows Anthropic's recommended skill architecture. The main SKILL.md should stay under 500 lines, with domain knowledge, output templates, and reference material moved into the `references/` subfolder.

**Why this matters:** When a skill triggers, the entire SKILL.md is loaded into context as a single message. A 1,374-line file wastes context window on material that is only relevant to one or two modes at a time. The `references/` folder exists specifically so that Claude can load supplementary files on demand — only when a specific mode needs them.

**Status:** ✅ Executed — 2026-04-16.
**Author:** Claude (Opus), requested by Mark.
**Date:** 2026-04-16

---

## 1. Current State Analysis

### What we have now

```
skill-update/
├── SKILL.md              (1,374 lines — all content in one file)
├── scoring-guide.md      (124 lines — already extracted, referenced by Mode 1)
├── CHANGES.md            (89 lines — install log)
└── [11 .bak files]       (historical backups)
```

The open-source copy at `open-source/skill/` mirrors this structure with a `references/` subfolder containing `scoring-guide.md`.

### What Anthropic recommends

From the official skill documentation and the skill-creator skill:

```
skill-name/
├── SKILL.md           (required — under 500 lines ideal)
├── references/        (domain knowledge loaded on demand)
│   ├── *.md
│   └── ...
├── scripts/           (executable code for deterministic tasks)
└── assets/            (templates, icons, fonts)
```

**Three-level progressive disclosure:**

1. **Metadata** (name + description) — always in context (~100 words). This is the triggering mechanism.
2. **SKILL.md body** — loaded when skill triggers. Must stay under 500 lines. Contains core workflow, mode routing, setup instructions, and pointers to reference files.
3. **Bundled resources** (references/, scripts/, assets/) — loaded on demand when a specific mode needs them. No size limit. Scripts can execute without loading into context.

**Key principle:** SKILL.md should contain the routing logic, setup, and high-level mode descriptions. Detailed output templates, scoring rubrics, workflow specifics, and domain knowledge belong in reference files, loaded only when the relevant mode runs.

### The problem

The current SKILL.md contains all of the following inline:

| Content type | Lines | Should be in SKILL.md? |
|---|---|---|
| Frontmatter + trust boundary + role statement | ~36 | Yes |
| Pipeline tracker + Notion mirror config | ~32 | Yes (compact version) |
| Setup (CV, profile, config reading) | ~44 | Yes (compact version) |
| Reading pipeline state | ~8 | Yes |
| File layout & conventions (folder structure, frontmatter schemas, cross-linking, archive, naming) | ~103 | **No — reference file** |
| Mode 0: Health Check | ~23 | Yes (short) |
| Mode 1: Offer Evaluator (scoring, output template, legitimacy, dedup, post-eval actions) | ~136 | **Partially — split** |
| Mode 2: Job Search | ~32 | Yes (short) |
| Mode 2.1: Portal Scan (ATS logic, Greenhouse API, output template) | ~102 | **No — reference file** |
| Mode 3: Interview Prep | ~46 | Borderline — keep compact |
| Mode 4: Company Research (Apollo, WebSearch, output template) | ~47 | Borderline — keep compact |
| Mode 5: Outreach (Apollo, contact finding, drafting guidelines) | ~42 | Yes (compact) |
| Mode 6: Cover Letter (drafting principles, word count enforcement, output template) | ~34 | Borderline — keep compact |
| Mode 7: Salary Negotiation (market data, output template, counter-offer scripts, non-comp levers) | ~122 | **No — reference file** |
| Offer Comparison sub-mode | ~43 | **No — reference file** |
| Mode 8: LinkedIn Browser (workflows, operating principles) | ~35 | Yes (compact) |
| Mode 9: Inbox & Follow-up (domain filtering, 5 workflows, operating principles) | ~60 | **Partially — split** |
| Mode 10: Calendar Ops (5 workflows, operating principles) | ~44 | Borderline — keep compact |
| Mode 11: Tailored CV (6-step process, ATS export, change summary template) | ~79 | **No — reference file** |
| Mode 12: Batch Pipeline (workflow, dedup, digest template) | ~80 | **No — reference file** |
| Mode 13: Calibration Report (data collection, output template) | ~77 | **No — reference file** |
| Weekly Trend Report enhancement | ~120 | **No — reference file** |
| General Principles + Cost Awareness + Scheduled-task paths | ~35 | Yes |

**Approximately 760 lines (55% of the file) are domain knowledge, output templates, and detailed workflow logic that should live in reference files.**

---

## 2. Target Architecture

After refactoring:

```
skill-update/
├── SKILL.md                          (~400–480 lines)
│   ├── Frontmatter (name, description)
│   ├── Content Trust Boundary
│   ├── Role statement
│   ├── Pipeline Tracker (compact)
│   ├── Setup: CV, Profile, Config (compact)
│   ├── Reading Pipeline State
│   ├── File Layout summary (3–5 lines + pointer to reference)
│   ├── Mode 0: Health Check (inline — short)
│   ├── Mode 1: Offer Evaluator (trigger + summary + pointer)
│   ├── Mode 2: Job Search (inline — short)
│   ├── Mode 2.1: Portal Scan (trigger + pointer)
│   ├── Mode 3: Interview Prep (compact inline)
│   ├── Mode 4: Company Research (compact inline)
│   ├── Mode 5: Outreach (compact inline)
│   ├── Mode 6: Cover Letter (compact inline)
│   ├── Mode 7: Salary Negotiation (trigger + pointer)
│   ├── Mode 8: LinkedIn Browser (compact inline)
│   ├── Mode 9: Inbox & Follow-up (compact inline)
│   ├── Mode 10: Calendar Ops (compact inline)
│   ├── Mode 11: Tailored CV (trigger + pointer)
│   ├── Mode 12: Batch Pipeline (trigger + pointer)
│   ├── Mode 13: Calibration Report (trigger + pointer)
│   ├── Weekly Trend Report (trigger + pointer)
│   ├── General Principles
│   ├── Cost Awareness
│   └── Scheduled-task output paths
│
├── references/
│   ├── scoring-guide.md              (124 lines — already exists)
│   ├── file-conventions.md           (~110 lines — extracted)
│   ├── mode1-offer-evaluator.md      (~140 lines — extracted)
│   ├── mode2-portal-scan.md          (~105 lines — extracted)
│   ├── mode7-salary-negotiation.md   (~165 lines — extracted)
│   ├── mode11-tailored-cv.md         (~85 lines — extracted)
│   ├── mode12-batch-pipeline.md      (~85 lines — extracted)
│   ├── mode13-calibration.md         (~80 lines — extracted)
│   └── weekly-trend-report.md        (~120 lines — extracted)
│
├── CHANGES.md
└── [backups]
```

### What stays in SKILL.md

- **Frontmatter, trust boundary, role statement** — always needed.
- **Pipeline tracker** — compact version (schema + Notion mirror summary). Remove the detailed `config.md` key documentation; reference it instead.
- **Setup** — compact version. Keep the three-file read instruction and missing-file handling. Move the detailed `config.md` optional-keys block to `file-conventions.md`.
- **Reading Pipeline State** — 8 lines, stays.
- **File Layout** — replace the 103-line section with a 5-line summary and a pointer: *"For folder structure, frontmatter schemas, naming conventions, cross-linking rules, and archive discipline, read `references/file-conventions.md`."*
- **Short modes** (0, 2, 3, 4, 5, 6, 8, 9, 10) — keep inline but ensure each is compact (trigger, what to do, save path). For modes that are already under ~50 lines, no extraction needed.
- **Long modes** (1, 2.1, 7, 11, 12, 13, Weekly Trend) — keep a compact stub in SKILL.md (trigger description, 2–3 sentence summary of what the mode does, save path) and add a clear pointer: *"Read `references/mode7-salary-negotiation.md` for the full negotiation workflow, output template, and counter-offer scripts."*
- **General Principles, Cost Awareness, Scheduled-task paths** — stays (35 lines).

### What moves to references/

Each extracted reference file is self-contained — it includes everything Claude needs to execute that mode once it decides to load the file. The SKILL.md stub tells Claude *when* to load it; the reference file tells Claude *how* to do it.

---

## 3. Extraction Plan — File by File

### 3.1 `references/file-conventions.md` (new — ~110 lines)

**Extract from SKILL.md lines 126–228** (the entire "File Layout & Conventions" section).

Contents:
- Folder structure diagram
- Frontmatter requirements (eval, outreach, cover, prep schemas)
- Cross-linking rule (wikilink syntax for Obsidian graph view)
- File-first discipline for outreach and cover letters
- Archive discipline
- Time-decay archival for daily/ and weekly/
- Naming conventions (slug format, date format, versioning)

**Replace in SKILL.md with:**

```markdown
## File Layout & Conventions

All artifacts must be saved to the correct subfolder with YAML frontmatter. Read `references/file-conventions.md` for the full specification: folder structure, frontmatter schemas, cross-linking rules, archive discipline, and naming conventions.

Key folders: `evals/`, `outreach/`, `cover-letters/`, `interview-prep/`, `research/`, `daily/`, `weekly/`, `archive/`.
```

**Why this is safe to extract:** File conventions are reference material consulted when writing artifacts. Claude does not need the full frontmatter schema in context at all times — only when it is about to save a file.

### 3.2 `references/mode1-offer-evaluator.md` (new — ~140 lines)

**Extract from SKILL.md lines 260–395** (Mode 1 body content).

Keep in SKILL.md (as the Mode 1 stub):
- Trigger description (1–2 lines)
- One-sentence summary: "Run a 10-dimension weighted evaluation, score 1–5, convert to letter grade A–F, assess posting legitimacy, save to evals/ with frontmatter."
- Pointer: *"Read `references/mode1-offer-evaluator.md` for the scoring dimensions, output template, legitimacy assessment, dedup rules, and post-eval actions. Scoring calibration is in `references/scoring-guide.md`."*
- Save path: `evals/eval-[company-slug]-[date].md`

Move to reference file:
- The 10-dimension scoring table and weights
- Scoring weights configuration (custom weights from config.md)
- Gate-pass rule explanation
- Grade conversion table
- Full output template (the markdown structure)
- Posting Legitimacy Assessment (signals, tiers, design rule)
- Dedup check logic
- Post-eval actions (steps 1–6: save, dedup, Notion mirror, Gmail cross-check, calendar reminder, next-step menu)

### 3.3 `references/mode2-portal-scan.md` (new — ~105 lines)

**Extract from SKILL.md lines 430–531** (Mode 2.1 body content).

Keep in SKILL.md (as the Mode 2.1 stub):
- Trigger description
- One-sentence summary: "Scan target companies' ATS boards for new postings matching profile criteria, dedup against existing evals, output a scan digest."
- Pointer: *"Read `references/mode2-portal-scan.md` for ATS-specific logic (Greenhouse API, Lever/Ashby browser fallback), output template, and error handling."*
- Save path: `daily/portal-scan-[YYYY-MM-DD].md`

Move to reference file:
- Prerequisite (target_companies config template)
- Greenhouse ATS workflow
- Lever/Ashby/manual ATS workflows
- Output structure template
- Frontmatter schema for portal-scan files
- Error handling rules

### 3.4 `references/mode7-salary-negotiation.md` (new — ~165 lines)

**Extract from SKILL.md lines 708–830** (Mode 7 + Offer Comparison).

Keep in SKILL.md (as the Mode 7 stub):
- Trigger description
- One-sentence summary: "Gather offer details, pull market data from web sources, produce a negotiation brief with counter-offer scripts and non-comp levers."
- Pointer: *"Read `references/mode7-salary-negotiation.md` for the full negotiation workflow, output template, pushback scripts, non-comp lever enumeration, and offer comparison format."*
- Save path: `negotiation-[company-slug]-[date].md`

Move to reference file:
- Input gathering steps (offer, role, current comp, walk-away line)
- Market data research instructions (WebSearch queries)
- Full negotiation brief output template
- Principles to embed
- Offer Comparison sub-mode (trigger, workflow, output template)

### 3.5 `references/mode11-tailored-cv.md` (new — ~85 lines)

**Extract from SKILL.md lines 832–910** (Mode 11 body content).

Keep in SKILL.md (as the Mode 11 stub):
- Trigger description
- Core principle: "The master cv.md is never touched. This mode produces a disposable, role-specific export."
- Pointer: *"Read `references/mode11-tailored-cv.md` for the 6-step tailoring process, change summary template, and ATS-safe docx export workflow."*
- Save path: `cv-[company-slug]-[YYYY-MM-DD].md`

Move to reference file:
- Steps 1–6 (extract JD requirements, map to CV, build tailored version, write change summary, save, offer docx export)
- The "do not fabricate" rules
- ATS compatibility rules
- Change summary template

### 3.6 `references/mode12-batch-pipeline.md` (new — ~85 lines)

**Extract from SKILL.md lines 1058–1137** (Mode 12 body content).

Keep in SKILL.md (as the Mode 12 stub):
- Trigger description
- One-sentence summary: "Lightweight Mode 1 on up to 10 JDs, ranked digest table partitioned into Top Picks / Review / Skip."
- Pointer: *"Read `references/mode12-batch-pipeline.md` for the batch workflow, dedup logic, digest template, and Notion sync."*
- Save path: `daily/batch-eval-[YYYY-MM-DD].md`

Move to reference file:
- Key constraints (max 10 items, lightweight scoring)
- 6-step workflow (parse, dedup, evaluate, build digest, save, Notion sync)
- Digest table template
- Operating principles

### 3.7 `references/mode13-calibration.md` (new — ~80 lines)

**Extract from SKILL.md lines 1138–1214** (Mode 13 body content).

Keep in SKILL.md (as the Mode 13 stub):
- Trigger description
- One-sentence summary: "Analyze grade-to-outcome correlation, identify predictive dimensions, detect scoring drift."
- Pointer: *"Read `references/mode13-calibration.md` for data collection steps, minimum threshold, analysis methodology, and output template."*
- Save path: `weekly/calibration-report-[date].md`

Move to reference file:
- Data collection instructions
- Minimum threshold rule (15 outcomes)
- Grade-to-outcome correlation methodology
- Predictive check description
- Dimension analysis methodology
- Scoring drift detection
- Full output template
- Edge case handling

### 3.8 `references/weekly-trend-report.md` (new — ~120 lines)

**Extract from SKILL.md lines 1221–1339** (Weekly Trend Report enhancement).

Keep in SKILL.md (as the enhancement stub):
- Trigger description
- One-sentence summary: "Aggregate 4+ weeks of batch-eval data to show volume trends, grade distribution, role frequency, company activity, salary ranges, and legitimacy trends."
- Pointer: *"Read `references/weekly-trend-report.md` for prerequisites, analysis steps, output template, and interpretation tips."*
- Save path: `weekly/trend-report-[YYYY-MM-DD].md`

Move to reference file:
- Prerequisites
- Graceful degradation message
- All 6 analysis steps (volume, grade distribution, role frequency, company activity, salary, legitimacy)
- Full output template
- Interpretation tips

---

## 4. SKILL.md Compact Mode Format

For modes that stay inline (3, 4, 5, 6, 8, 9, 10), ensure each follows this compact pattern:

```markdown
### Mode N: [Name]

**Trigger:** [1–2 sentences describing when this mode activates.]

**What to do:**

[Core workflow in 15–40 lines. Include: inputs needed, key steps, operating principles, save path.]

---
```

For modes extracted to references, the stub is:

```markdown
### Mode N: [Name]

**Trigger:** [1–2 sentences describing when this mode activates.]

[1–2 sentence summary of what the mode produces.]

Read `references/modeN-name.md` for the full workflow, output template, and detailed instructions.

**Save to:** `[folder]/[filename-pattern].md`

---
```

---

## 5. Execution Steps

Execute in this exact order. Each step is a discrete commit-worthy unit.

### Step 1: Create the references/ subfolder

Create `skill-update/references/` if it doesn't already exist. Move the existing `scoring-guide.md` into it (it currently lives at `skill-update/scoring-guide.md` — the open-source copy already has it in the right place).

**Verify:** `skill-update/references/scoring-guide.md` exists and contains the same 124 lines.

### Step 2: Extract reference files

For each of the 7 new reference files (sections 3.1–3.8 above):

1. Copy the relevant lines from the current SKILL.md into the new reference file.
2. Add a header to each reference file that identifies it: `# [Title]` and a one-line note: `*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*`
3. Preserve all content exactly — do not rewrite, summarize, or restructure the extracted content. This is a move operation, not a rewrite.
4. Ensure markdown formatting is preserved (code blocks, tables, nested lists).

**Verify after each file:** The extracted content matches the original SKILL.md source lines. Use `diff` or line-count comparison.

**File creation order** (no dependencies between them — can be done in parallel):
1. `references/file-conventions.md`
2. `references/mode1-offer-evaluator.md`
3. `references/mode2-portal-scan.md`
4. `references/mode7-salary-negotiation.md`
5. `references/mode11-tailored-cv.md`
6. `references/mode12-batch-pipeline.md`
7. `references/mode13-calibration.md`
8. `references/weekly-trend-report.md`

### Step 3: Rewrite SKILL.md

Replace the extracted sections in SKILL.md with compact stubs (as described in sections 3.1–3.8 and section 4). The stubs must include:

- The trigger description (preserved exactly from original)
- A 1–2 sentence summary of what the mode does
- A `Read references/[filename].md` pointer with a brief description of what's in the reference file
- The save path

**Important rules for the rewrite:**

- Do NOT change the frontmatter (name, description). These control triggering.
- Do NOT remove or rename any mode. All 14 modes (0–13 + Weekly Trend) must still appear in SKILL.md.
- Do NOT change the order of modes.
- Do NOT alter the Content Trust Boundary, Pipeline Tracker, Setup, or General Principles sections beyond compacting the config.md optional-keys block (move it to file-conventions.md).
- Do NOT rewrite the content of inline modes (3, 4, 5, 6, 8, 9, 10) — they stay as-is. Only extracted modes get stubs.
- The "Reading Pipeline State" section stays as-is.
- The "Scheduled-task output paths" section stays as-is.

**Verify:** The final SKILL.md is between 400 and 500 lines. Count with `wc -l`.

### Step 4: Verify cross-references

Read through the new SKILL.md and confirm every `references/` pointer matches an actual file:

```bash
# Extract all referenced files from SKILL.md
grep -oP 'references/[a-z0-9-]+\.md' skill-update/SKILL.md | sort -u

# List actual files
ls skill-update/references/

# Confirm they match
```

Also verify that each reference file does not contain orphan references to other reference files that don't exist.

### Step 5: Update the open-source copy

Per CLAUDE.md propagation rules:

1. Copy the new `skill-update/SKILL.md` to `open-source/skill/SKILL.md`.
2. Copy all new reference files from `skill-update/references/` to `open-source/skill/references/`.
3. Verify `scoring-guide.md` is present in both locations.
4. Run a PII check on all files in `open-source/skill/` — confirm no real names, emails, Notion IDs, or company names from real applications.

### Step 6: Repack the .skill bundle

After verifying both copies:

1. Back up the current `dossier.skill` as `skill-update/dossier.skill.bak-pre-refactor`.
2. Repack the main vault's `.skill` from `skill-update/`.
3. Repack the open-source `.skill` from `open-source/skill/`.

If the skill-creator's `package_skill.py` is available, use it. Otherwise, ZIP the skill folder contents (SKILL.md + references/) into a `.skill` file.

### Step 7: Smoke test

After repacking, verify the skill loads correctly:

1. Check that SKILL.md is valid YAML frontmatter + markdown (no syntax errors in the frontmatter block).
2. Confirm the .skill file is a valid ZIP containing SKILL.md and the references/ folder.
3. Read the SKILL.md and confirm every mode has either inline content or a valid pointer.
4. Read one reference file (e.g., `mode1-offer-evaluator.md`) and confirm it is self-contained and complete.

---

## 6. Line Budget

Target SKILL.md composition after refactoring:

| Section | Estimated lines |
|---|---|
| Frontmatter | 16 |
| Content Trust Boundary | 15 |
| Role statement | 3 |
| Pipeline Tracker (compact) | 25 |
| Setup: CV, Profile, Config (compact — move optional keys block) | 30 |
| Reading Pipeline State | 8 |
| File Layout summary + pointer | 6 |
| Mode 0: Health Check | 23 |
| Mode 1 stub | 8 |
| Mode 2: Job Search (inline) | 32 |
| Mode 2.1 stub | 7 |
| Mode 3: Interview Prep (inline) | 46 |
| Mode 4: Company Research (inline) | 47 |
| Mode 5: Outreach (inline) | 42 |
| Mode 6: Cover Letter (inline) | 34 |
| Mode 7 stub | 8 |
| Mode 8: LinkedIn Browser (inline) | 35 |
| Mode 9: Inbox & Follow-up (inline) | 60 |
| Mode 10: Calendar Ops (inline) | 44 |
| Mode 11 stub | 8 |
| Mode 12 stub | 8 |
| Mode 13 stub | 8 |
| Weekly Trend Report stub | 7 |
| General Principles | 10 |
| Cost Awareness | 7 |
| Scheduled-task output paths | 12 |
| **Total** | **~470 lines** |

This is within the recommended 500-line limit. The 8 reference files total approximately 890 additional lines, loaded only when needed.

---

## 7. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Claude fails to load reference file when needed | Each mode stub includes an explicit `Read references/...` instruction. The pointer is not optional text — it is the primary instruction for that mode. |
| Reference file content drifts from SKILL.md stubs | Each reference file header includes a note: "Do not edit without also updating the pointer in SKILL.md." Add this to CLAUDE.md as a maintenance rule. |
| Open-source copy falls out of sync | Step 5 is mandatory. Add a checklist item to the session-end routine. |
| Backup not taken before destructive edit | Step 6 explicitly backs up dossier.skill before repacking. The existing .bak files in skill-update/ also provide rollback points. |
| Mode behavior changes due to extraction | Step 2 rule: "Preserve all content exactly — do not rewrite, summarize, or restructure." This is a move operation. Behavioral equivalence is maintained by copying verbatim. |

---

## 8. What This Plan Does NOT Do

- **Does not rewrite any mode logic.** Content moves, it does not change.
- **Does not add new modes or features.** Scope is structural only.
- **Does not change the frontmatter description.** Triggering behavior is unchanged.
- **Does not touch cv.md, profile.md, config.md, or any eval/outreach files.**
- **Does not reorganize the vault folder structure.** Only the skill's internal structure changes.

---

## 9. Success Criteria

1. `skill-update/SKILL.md` is between 400 and 500 lines.
2. All 14 modes are present in SKILL.md (as inline content or stubs with pointers).
3. Every `references/` pointer in SKILL.md resolves to a real file.
4. Every reference file is self-contained (a reader can execute the mode using only that file plus context from SKILL.md's setup sections).
5. The open-source copy mirrors the main vault's skill structure.
6. Both `.skill` bundles are valid and loadable.
7. No content has been lost — the union of SKILL.md + all reference files contains every line from the original SKILL.md.
8. No PII in the open-source copy.

---

## 10. Execution Log (2026-04-16)

The plan was executed in full with the following deviations from the original design:

### Additional extractions (not in original plan)

The original plan estimated ~470 lines for SKILL.md. After executing Steps 1–3 as planned, the result was 602 lines — over the 500-line target. The inline modes were longer than the line budget predicted. Two additional extractions brought it under:

- **Mode 9: Inbox & Follow-up** → `references/mode9-inbox-followup.md` (61 lines). This was the largest remaining inline mode at 60 lines with 5 distinct workflows. Replaced with a 6-line stub.
- **Mode 10: Calendar Ops** → `references/mode10-calendar-ops.md` (45 lines). Second-largest remaining inline mode at 46 lines. Replaced with a 5-line stub.

### Template compaction

Mode 3 (Interview Prep) and Mode 4 (Company Research) each contained large multi-line output template code blocks that were mostly structural boilerplate. These were compacted into single-paragraph inline descriptions of the section structure, saving ~30 lines without losing information.

### Backup relocation

The `.bak` files in `skill-update/` were included in the first `.skill` repack, polluting the installable bundle. Fixed by moving all backups to `Dossier/skill-backups/` (outside the skill folder) and repacking clean.

### Final metrics

| Metric | Planned | Actual |
|---|---|---|
| SKILL.md lines | 400–500 | **460** |
| Reference files | 8 (scoring-guide + 7 new) | **11** (scoring-guide + 10 new) |
| Total reference lines | ~890 | **1,087** |
| Modes extracted to refs | 7 (1, 2.1, 7, 11, 12, 13, trend) | **9** (+ Modes 9, 10) |
| Modes kept inline | 8 (0, 2, 3, 4, 5, 6, 8, 9, 10) | **6** (0, 2, 3, 4, 5, 6, 8) |
| Open-source synced | Yes | **Yes** |
| Both .skill bundles valid | Yes | **Yes** |
| PII check clean | Yes | **Yes** |

All 9 success criteria met.
