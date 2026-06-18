# Plan 23: Packets and Folder Structure v2

**Status:** Draft — ready for Claude Code CLI execution
**Implements:** User locked decision (item 1) — standardize the "packet" concept and add it to the canonical folder structure and skill.
**Depends on:** Nothing (foundational; other plans build on the folder layout defined here).
**Blocks:** Plan 24 (send-ready validator), Plan 25 (target-radar), Plan 26 (live vault cleanup), Plan 27 (backlog sweep).

---

## 1. Summary

This plan formalizes the "packet" concept already present ad-hoc in the live vault (`packets/EnvisionHealthcare/`, `packets/Healix/`, etc.) into a first-class canonical structure, integrates it into the skill as a new mode (Mode 14), and updates all relevant docs. A packet is the one-stop send-ready bundle for a single application. Plan 23 defines the structure and assembly workflow. Plan 24 (a separate plan) defines the send-ready validator that gates packet finalization.

---

## 2. Packet Definition and Rationale

A packet is the per-application, send-ready bundle that consolidates every artifact a candidate needs to submit for and follow through on one specific role. Its purpose is to eliminate context-switching during an active application: everything required to submit, answer screening questions, and follow up lives in one place.

The packet differs from the existing loose-file pattern in three ways:

- It is scoped to exactly one `[company-slug]/[role-slug]` pair. A second role at the same company gets its own packet subfolder.
- It contains tuned submission artifacts (CV, cover letter) rather than raw skill outputs. The tuning step is Mode 14 (new). The existing loose artifacts under `cover-letters/` and `cv-[slug]-[date].md` remain where they are until a separate cleanup plan migrates them.
- It carries a README that serves as both a human checklist and a machine-readable manifest, enabling future automation (the send-ready validator in Plan 24 reads this file).

The packet does NOT replace the eval (`evals/`) or the research brief (`research/`). Those artifacts stay in their existing folders and are cross-linked into the packet README. The packet is a delivery bundle, not a replacement for the analysis layer.

---

## 3. Canonical Folder Structure v2

```
Dossier/
  cv.md                        canonical, root
  profile.md                   canonical, root
  config.md                    canonical, root
  stories.md                   canonical, root
  dashboard.md                 canonical, root
  README.md                    canonical, root

  evals/                       eval-[slug]-[date].md           (Mode 1 output)
  outreach/                    outreach-[slug]-[date].md       (Mode 5 output)
  cover-letters/               cover-[slug]-[date].md          (Mode 6 output, legacy home)
  interview-prep/              prep-[slug]-[date].md           (Mode 3 output)
  research/                    target-brief-*.md, research-*.md (Mode 4 output)
  negotiation/                 negotiation-[slug]-[date].md    (Mode 7 output)
  daily/                       daily-scan-*, leads-*-am/pm, recruiter-triage-*
  weekly/                      pipeline-digest-*, week-ahead-*
  archive/                     per-company bundles once terminal

  packets/                     NEW: per-application send-ready bundles
    [company-slug]/
      [role-slug]/
        README.md              packet manifest (frontmatter + checklist)
        cv.md                  tuned CV markdown (source for export)
        cv.docx                ATS-safe export (generated from cv.md)
        cover-letter.md        tuned cover letter markdown
        cover-letter.docx      submission-ready export
        jd.md                  job description verbatim (reference, not submitted)
        prep.md                interview prep (optional; also in interview-prep/)
        outreach.md            outreach draft (optional; also in outreach/)

  target-radar/                NEW: target-company discovery artifacts (Plan 25 owns this)
  reference/                   NEW: non-artifact reference docs (Plan 25 owns this)
```

**Slug conventions:** same rule as eval slugs, lowercase-hyphen, no punctuation. `envision-healthcare`, `healix-technology-group`. The role slug mirrors the eval slug convention: `power-bi-architect`, `lead-ai-builder`. Both slugs are written in the packet README frontmatter so they are machine-readable.

**Legacy artifacts:** Existing `cv-[slug]-[date].md` files at the vault root and `cover-letters/cover-[slug]-[date].md` files are legacy. A separate cleanup plan (Plan 26) migrates them into the correct packet folders. This plan does not move them; it only notes their migration target.

---

## 4. Packet File Specifications

### 4.1 Required files (every packet must have these before `send_ready: true`)

| File | Notes |
|---|---|
| `README.md` | Packet manifest. Frontmatter schema defined in section 4.2. Body: submission guidance, application Q&A, source file table, notes. |
| `cv.md` | Tuned CV markdown. Same structure as master `cv.md` plus `## What Changed` section at bottom. Strip `## What Changed` before exporting to docx. |
| `cv.docx` | ATS-safe Word export. Single-column, Arial, name/contact in body. Generated from `cv.md` with the `## What Changed` block stripped. |
| `cover-letter.md` | Tuned cover letter markdown with `type: cover` frontmatter. Under 400 words per Mode 6 rules. |
| `cover-letter.docx` | Submission-ready Word export generated from `cover-letter.md`. |

### 4.2 Optional files

| File | When to include |
|---|---|
| `jd.md` | Always include for recruiter-inbound roles where the JD was forwarded as text rather than available at a stable URL. Verbatim capture, not for submission. |
| `prep.md` | Include when interview prep has been drafted. May duplicate `interview-prep/prep-[slug]-[date].md` — the packet copy is the send-ready, role-specific version. |
| `outreach.md` | Include when an outreach draft is also stored in `outreach/`. Packet copy is the final text; `outreach/` copy is the durable record (do not move the outreach/ copy). |

### 4.3 Packet README frontmatter schema

```yaml
---
type: packet
company: "Company Name"
role: "Role Title"
company_slug: company-slug
role_slug: role-slug
status: Assembling | Ready | Submitted | Archived
send_ready: false
related_eval: "[[eval-company-slug-YYYY-MM-DD]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
contents:
  cv_md: false
  cv_docx: false
  cover_letter_md: false
  cover_letter_docx: false
  jd_md: false
  prep_md: false
  outreach_md: false
---
```

**Field rules:**

- `type: packet` is the Dataview discriminator. Do not omit it.
- `status` mirrors the application's pipeline state from the related eval's `status` field. Update it when the eval status changes. Valid values: `Assembling` (packet being built), `Ready` (all required files present, docx exports done, pending send-ready sign-off), `Submitted` (application sent), `Archived` (terminal state, packet moved to `archive/[company-slug]/[role-slug]/`).
- `send_ready: false` is the default. The send-ready validator (Plan 24) sets this to `true` when all required files are present and pass validation. Do not set it manually except when no validator is available.
- `related_eval` uses Obsidian wikilink syntax, matching the eval file basename without extension.
- `contents` is a checklist of which files are present. Set each to `true` when the corresponding file exists and has been reviewed. The send-ready validator in Plan 24 reads this checklist.

### 4.4 Packet README body structure

The body of the packet README follows the pattern established by the live vault packets. Required sections:

1. H1 heading: `# [Company] Submission Packet`
2. Metadata block (role, source, packet date, eval summary, comp band, location, legitimacy).
3. `## Files in this packet` with subsections `### Required` and `### Supplemental` (if any).
4. `## Submission guidance` covering how to send, application Q&A, questions to ask them.
5. `## Source files` table mapping file type to vault path (for traceability).
6. `## Notes` for standing rules, gaps to hold for screen, engagement-mode posture.
7. `## Related` (at bottom, for Obsidian graph wikilinks back to eval, research, outreach).

The `## Related` section uses the same cross-linking convention as eval files:

```
## Related

- Eval: [[eval-company-slug-YYYY-MM-DD]]
- Research: [[research-company-slug-YYYY-MM-DD]]
- Outreach: [[outreach-company-slug-YYYY-MM-DD]]
```

---

## 5. Mode 14: Packet Assembly

### 5.1 Decision: new mode, not an extension of Modes 6 or 11

Mode 14 is a new mode rather than an extension of Modes 6 or 11 for three reasons:

- It orchestrates multiple existing modes in sequence (Mode 11 for CV, Mode 6 for cover letter) plus additional steps (README generation, docx export coordination, cross-linking). Extending either parent mode would create a hidden multi-step workflow inside a single mode that is already documented inline.
- It writes to a different output location (`packets/` rather than `cover-letters/` or vault root) and requires a different frontmatter type (`type: packet`).
- It is the entry point for send-ready validation (Plan 24), which needs a well-defined handoff boundary. A clean mode boundary makes Plan 24's scope unambiguous.

Modes 6 and 11 continue to work independently. Mode 14 calls their logic; it does not replace them.

### 5.2 Trigger

User asks "assemble a packet for [company/role]", "build the packet", "create my submission bundle for [company]", or follows up after a Mode 1 evaluation with a B or higher grade and "let's assemble the packet."

### 5.3 Step sequence

**Step 0: Pre-flight.**
Read `cv.md`, `profile.md`, and `stories.md`. Locate the most recent eval for this company/role in `evals/`. If no eval exists, run Mode 1 first and use its output. If grade is C or lower, warn: "Packet assembly for a C or lower grade is allowed but non-standard. Confirm to proceed." Require explicit confirmation.

Resolve slugs: `company_slug` from the eval filename, `role_slug` by lowercasing and hyphenating the role title. If the role title is long (> 4 words), abbreviate sensibly and confirm with the user. Example: "Principal Solution and Database Architect" -> `principal-solution-architect`.

Create the directory `packets/[company-slug]/[role-slug]/` if it does not exist.

**Step 1: Read and summarize all input sources.**
Read in parallel (these are all reads, no writes at this step):
- The eval at `evals/eval-[company-slug]-[date].md` (full body, not just frontmatter).
- The research brief at `research/research-[company-slug]-[date].md` if present.
- The JD (from the eval body's JD section, or from the user if not embedded).
- `stories.md` (full content for story selection).

Produce an internal summary of: top 3 JD requirements by weight, the 2-3 strongest stories from `stories.md` that match those requirements (by tag overlap per `references/story-tagging.md`), the gaps called out in the eval, and the eval's submission guidance and notes.

Do not output this summary to the user. Use it as the working context for Steps 2-4.

**Step 2: Produce the tuned CV.**
Apply Mode 11 logic to produce a tuned CV, writing to `packets/[company-slug]/[role-slug]/cv.md`.

Key differences from a standalone Mode 11 run:
- Output path is `packets/[company-slug]/[role-slug]/cv.md`, not `Dossier/cv-[slug]-[date].md`.
- The `## What Changed` section is appended to the packet `cv.md` exactly as Mode 11 specifies. It is stripped at docx export time (Step 5), not at write time.
- No separate "save to Mode 11 root path" step; the packet is the canonical output.

Story selection: for the professional summary and any narrative framing, prefer the 2-3 strongest story matches identified in Step 1. Do not fabricate bullets; apply Mode 11's fabrication rules without exception.

**Step 3: Produce the tuned cover letter.**
Apply Mode 6 logic to produce the cover letter, writing to `packets/[company-slug]/[role-slug]/cover-letter.md` with `type: cover` frontmatter and `related_eval` wikilink.

Use the tuned `cv.md` from Step 2 as the CV input rather than the master `cv.md`. This ensures cover letter proof points reference the already-selected and reordered bullets rather than the master document order.

Select the strongest two proof points from the Step 1 story summary. Apply Mode 6 word-count enforcement (400-word hard cap) before writing the file.

**Step 4: Capture the JD.**
If the JD is not available at a stable URL, write it verbatim to `packets/[company-slug]/[role-slug]/jd.md`. Plain markdown, no frontmatter. Note at the top: `<!-- Reference only — not for submission -->`.

If the JD is at a stable public URL (a Greenhouse/Lever/Ashby posting), record the URL in the packet README instead; do not create a `jd.md` file.

**Step 5: Generate docx exports.**
Offer to generate both `cv.docx` and `cover-letter.docx` using the docx skill. Apply Mode 11's ATS-safety rules for `cv.docx` (single-column, Arial, name/contact in body, strip `## What Changed`). Apply standard docx export for `cover-letter.docx`.

If the user declines, set `contents.cv_docx: false` and `contents.cover_letter_docx: false` in the manifest. The packet is not `send_ready: true` until both docx files exist and are confirmed.

**Step 6: Write the packet README (manifest).**
Write `packets/[company-slug]/[role-slug]/README.md` with:
- YAML frontmatter per the schema in section 4.3, with `contents` fields set based on which files were produced.
- Body following the section structure in section 4.4.
- `## Related` section at the bottom with wikilinks to the eval, research brief, and outreach (if any).

Set `status: Ready` if all required files are present (cv.md, cv.docx, cover-letter.md, cover-letter.docx). Set `status: Assembling` if any required file is missing. Set `send_ready: false` always (Plan 24's validator sets it to `true`).

**Step 7: Update the eval's `## Related` section.**
Append (or update) the `## Related` section of the linked eval file to include a wikilink to the packet README:

```
- Packet: [[packets/company-slug/role-slug/README]]
```

Use the wikilink path form (not just the basename) because packet READMEs are not uniquely named across the vault.

**Step 8: Confirm to user.**
Report:
- Files written (with paths).
- Contents checklist state.
- Whether `send_ready` is eligible (all required files present) or what is missing.
- Reminder: "The `## What Changed` section in `cv.md` is for reference only. It has been stripped from `cv.docx`. Do not submit `cv.md` directly."
- Offer to run Mode 3 (interview prep) and save the result to the packet as `prep.md`.

---

## 6. Exact Edit List

### 6.1 `skill/SKILL.md`

**Edit 1: Update folder layout reference in "File Layout & Conventions" section.**

Find the line:
```
Key folders: `evals/`, `outreach/`, `cover-letters/`, `interview-prep/`, `research/`, `negotiation/`, `daily/`, `weekly/`, `archive/`.
```

Replace with:
```
Key folders: `evals/`, `outreach/`, `cover-letters/`, `interview-prep/`, `research/`, `negotiation/`, `daily/`, `weekly/`, `archive/`, `packets/` (per-application send-ready bundles).
```

**Edit 2: Add Mode 14 section after Mode 13.**

Insert the following block immediately after the Mode 13 section (before `## Enhancement: Weekly Trend Report`):

```markdown
### Mode 14: Packet Assembly

**Trigger:** User asks to "assemble a packet", "build the packet", "create my submission bundle for [company]", or follows up after a Mode 1 evaluation with B or higher grade and "let's assemble the packet."

A packet is the per-application, send-ready bundle containing a tuned CV and cover letter (plus optional JD capture, prep doc, and outreach draft), assembled into `packets/[company-slug]/[role-slug]/`. The master `cv.md` is never touched.

Read `references/mode14-packet-assembly.md` for the 8-step assembly workflow, packet README frontmatter schema, story-selection rules, cross-linking steps, and docx export discipline.

**Writes to:** `packets/[company-slug]/[role-slug]/` (README.md, cv.md, cv.docx, cover-letter.md, cover-letter.docx, and optionally jd.md, prep.md, outreach.md).
```

**Edit 3: Update `test_all_modes_exist` reference in any inline comment.**

SKILL.md does not contain an inline test list, so no additional edit is needed here. The test file edit in section 6.6 covers this.

---

### 6.2 `skill/references/file-conventions.md`

**Edit 1: Replace the "Folder structure" code block.**

Find the fenced code block starting with:
```
Dossier/
├── cv.md                   ← canonical, root
```

Replace the entire fenced block with:
```
```
Dossier/
├── cv.md                    canonical, root
├── profile.md               canonical, root
├── config.md                canonical, root
├── stories.md               canonical, root
├── dashboard.md             canonical, root
├── README.md                canonical, root
│
├── evals/                   eval-[slug]-[date].md             (Mode 1 output)
├── outreach/                outreach-[slug]-[date].md         (Mode 5 output)
├── cover-letters/           cover-[slug]-[date].md            (Mode 6 output, legacy home)
├── interview-prep/          prep-[slug]-[date].md             (Mode 3 output)
├── research/                target-brief-*.md, research-*.md  (Mode 4 output)
├── negotiation/             negotiation-[slug]-[date].md      (Mode 7 output)
├── daily/                   daily-scan-*, leads-*-am/pm, recruiter-triage-*
├── weekly/                  pipeline-digest-*, week-ahead-*
├── archive/                 per-company bundles once terminal
│
├── packets/                 NEW: per-application send-ready bundles
│   └── [company-slug]/
│       └── [role-slug]/
│           ├── README.md         packet manifest (frontmatter + checklist)
│           ├── cv.md             tuned CV markdown
│           ├── cv.docx           ATS-safe export
│           ├── cover-letter.md   tuned cover letter markdown
│           ├── cover-letter.docx submission-ready export
│           ├── jd.md             job description verbatim (optional, not submitted)
│           ├── prep.md           interview prep (optional)
│           └── outreach.md       outreach draft (optional)
│
├── target-radar/            target-company discovery artifacts (Plan 25)
└── reference/               non-artifact reference docs (Plan 25)
```
```

**Edit 2: Add a "Packets" subsection after the "Archive discipline" subsection.**

Insert the following after the archive discipline subsection and before the "Time-decay archival" subsection:

```markdown
### Packets

A packet (`packets/[company-slug]/[role-slug]/`) is the send-ready bundle for one application. It is created by Mode 14 (Packet Assembly) and contains tuned submission artifacts derived from the master CV and the role's eval, research, and stories.

**Packet README frontmatter** (`type: packet`):
```yaml
---
type: packet
company: "Company Name"
role: "Role Title"
company_slug: company-slug
role_slug: role-slug
status: Assembling | Ready | Submitted | Archived
send_ready: false
related_eval: "[[eval-company-slug-YYYY-MM-DD]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
contents:
  cv_md: false
  cv_docx: false
  cover_letter_md: false
  cover_letter_docx: false
  jd_md: false
  prep_md: false
  outreach_md: false
---
```

**Required files in every packet:** `README.md`, `cv.md`, `cv.docx`, `cover-letter.md`, `cover-letter.docx`. A packet is not `send_ready: true` until all five are present and confirmed.

**Cross-linking:** The packet README's `## Related` section links back to the eval, research brief, and outreach draft using Obsidian wikilink syntax. The eval's own `## Related` section gets a `- Packet: [[packets/company-slug/role-slug/README]]` entry added by Mode 14.

**Naming:** company and role slugs follow the same lowercase-hyphen convention as eval slugs. Two roles at the same company each get their own `[role-slug]/` subfolder under the shared `[company-slug]/` directory.

**Legacy artifacts:** `cv-[slug]-[date].md` files at the vault root and `cover-letters/cover-[slug]-[date].md` files are from before packets were standardized. Their migration target is `packets/[company-slug]/[role-slug]/cv.md` and `cover-letter.md` respectively. Migration is handled by Plan 26 (live vault cleanup) and is not performed by this mode.

**Archive behavior:** When a company reaches a terminal pipeline state, the entire `packets/[company-slug]/` directory is moved to `archive/[company-slug]/packets/` alongside the other company artifacts. Packet `status` is set to `Archived` before the move.
```

---

### 6.3 `skill/references/mode14-packet-assembly.md` (new file)

Create `skill/references/mode14-packet-assembly.md` with the full Mode 14 step sequence from section 5.3, the packet README frontmatter schema from section 4.3, the packet README body structure from section 4.4, and the file specifications from sections 4.1 and 4.2. This is the on-demand reference file loaded when Mode 14 runs.

File path: `skill/references/mode14-packet-assembly.md`

Full content:

```markdown
# Mode 14: Packet Assembly — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User asks to "assemble a packet", "build the packet", "create my submission bundle for [company]", or follows up after a Mode 1 evaluation graded B or higher with "let's assemble the packet."

**Core principle:** A packet is the per-application, send-ready bundle for one `[company-slug]/[role-slug]` pair. It contains tuned submission artifacts (not raw Mode 6/11 outputs) produced by reading the eval, research brief, JD, and stories in combination. The master `cv.md` is never touched.

---

## Packet file set

### Required (every packet must have all five before `send_ready: true`)

| File | Description |
|---|---|
| `README.md` | Packet manifest. Frontmatter schema below. Body: submission guidance, application Q&A, source file table, notes, Related section. |
| `cv.md` | Tuned CV markdown. Same structure as master `cv.md` plus `## What Changed` at bottom. Strip before docx export. |
| `cv.docx` | ATS-safe Word export. Single-column, Arial, name/contact in body. `## What Changed` stripped. |
| `cover-letter.md` | Tuned cover letter markdown with `type: cover` frontmatter. 400-word hard cap (Mode 6 rule). |
| `cover-letter.docx` | Submission-ready Word export from `cover-letter.md`. |

### Optional

| File | When |
|---|---|
| `jd.md` | When the JD was forwarded as text and is not at a stable public URL. Verbatim. Not submitted. |
| `prep.md` | When interview prep has been drafted for this role. |
| `outreach.md` | When an outreach draft exists. The `outreach/` file remains the durable record; this is the packet copy. |

---

## Packet README frontmatter schema

```yaml
---
type: packet
company: "Company Name"
role: "Role Title"
company_slug: company-slug
role_slug: role-slug
status: Assembling | Ready | Submitted | Archived
send_ready: false
related_eval: "[[eval-company-slug-YYYY-MM-DD]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
contents:
  cv_md: false
  cv_docx: false
  cover_letter_md: false
  cover_letter_docx: false
  jd_md: false
  prep_md: false
  outreach_md: false
---
```

Field rules:
- `type: packet` is the Dataview discriminator. Never omit it.
- `send_ready: false` is the default. The send-ready validator (Plan 24) sets it to `true`. Do not set manually except when no validator is available.
- `related_eval` uses Obsidian wikilink syntax (file basename, no extension, no path prefix).
- `status: Ready` when all five required files are present; `Assembling` otherwise.
- `contents` checklist: set each boolean to `true` when the corresponding file exists and has been reviewed.

---

## Packet README body structure

1. `# [Company] Submission Packet` (H1)
2. Metadata block: role, source, packet date, eval grade/score summary, comp band, location, legitimacy.
3. `## Files in this packet` with `### Required` and `### Supplemental` subsections.
4. `## Submission guidance`: how to send, application Q&A (anticipated screening questions with honest answers), questions to ask them.
5. `## Source files` table: maps file type to vault path for traceability.
6. `## Notes`: standing rules (no em-dashes), gaps to hold for screen, engagement-mode posture.
7. `## Related` (bottom): Obsidian wikilinks back to eval, research brief, outreach. Example:
   ```
   ## Related
   - Eval: [[eval-company-slug-YYYY-MM-DD]]
   - Research: [[research-company-slug-YYYY-MM-DD]]
   - Outreach: [[outreach-company-slug-YYYY-MM-DD]]
   ```

---

## Step sequence

### Step 0: Pre-flight

Read `cv.md`, `profile.md`, and `stories.md`. Locate the most recent eval for this company/role in `evals/`. If no eval exists, run Mode 1 first. If grade is C or lower, warn and require explicit confirmation before proceeding.

Resolve slugs: `company_slug` from the eval filename. `role_slug` by lowercasing the role title and replacing spaces and special characters with hyphens. If the title is more than 4 words, abbreviate to the most distinguishing terms and confirm with the user.

Create `packets/[company-slug]/[role-slug]/` if it does not exist.

### Step 1: Gather and summarize inputs

Read in parallel (no writes at this step):
- Full eval body at `evals/eval-[company-slug]-[date].md`.
- Research brief at `research/research-[company-slug]-[date].md` (if present).
- JD (from eval body or user-provided).
- `stories.md` (full content).

Produce an internal working summary of: top 3 JD requirements by weight; the 2-3 best-matching stories from `stories.md` by tag overlap (per `references/story-tagging.md`); the gaps the eval flagged; the eval's submission guidance and notes. Do not output this summary to the user.

### Step 2: Tuned CV

Apply Mode 11 logic. Write output to `packets/[company-slug]/[role-slug]/cv.md`.

Differences from a standalone Mode 11 run:
- Output path is the packet directory, not `Dossier/cv-[slug]-[date].md`.
- `## What Changed` section is appended (as per Mode 11); stripped at docx export time in Step 5, not now.
- Use the 2-3 story matches from Step 1 to inform which bullets and skills to foreground.
- Apply Mode 11's fabrication rules without exception.

### Step 3: Tuned cover letter

Apply Mode 6 logic. Write output to `packets/[company-slug]/[role-slug]/cover-letter.md` with `type: cover` frontmatter and `related_eval` wikilink.

Use `packets/[company-slug]/[role-slug]/cv.md` (the Step 2 output) as the CV input, not the master `cv.md`. Select the strongest two proof points from the Step 1 story summary. Apply the 400-word hard cap before writing.

### Step 4: JD capture (conditional)

If the JD is not at a stable public URL: write it verbatim to `packets/[company-slug]/[role-slug]/jd.md`. Add `<!-- Reference only — not for submission -->` at the top. If it is at a stable URL: record the URL in the packet README; do not create `jd.md`.

### Step 5: docx exports

Offer to generate `cv.docx` and `cover-letter.docx` using the docx skill.

For `cv.docx`: apply Mode 11's ATS-safety rules (single-column, Arial 11-12pt body, 14pt headers, name/contact in body, no tables/text boxes, plain bullets, standard date format). Strip the `## What Changed` section before passing content to the docx generator.

If the user declines: set `contents.cv_docx: false` and `contents.cover_letter_docx: false`. The packet will not be `send_ready: true` until both files exist.

### Step 6: Write packet README

Write `packets/[company-slug]/[role-slug]/README.md` with:
- YAML frontmatter per the schema above, with `contents` booleans set based on what was produced.
- Body following the section structure above.
- `status: Ready` if all five required files are present; `Assembling` otherwise.
- `send_ready: false` always at this stage.

### Step 7: Cross-link into the eval

Append or update the `## Related` section of `evals/eval-[company-slug]-[date].md` to include:
```
- Packet: [[packets/company-slug/role-slug/README]]
```

Use the path-form wikilink (not just the basename) because packet READMEs are not uniquely named.

### Step 8: Report to user

Tell the user:
- All files written, with their paths relative to the vault root.
- Which `contents` fields are `true` and which are missing.
- Whether `status: Ready` was set or what is still needed.
- Reminder: "`## What Changed` in `cv.md` is reference only; it has been stripped from `cv.docx`. Do not submit `cv.md` directly."
- Offer: "Want me to run Mode 3 (interview prep) and save the result to this packet as `prep.md`?"

---

## Fabrication rules (inherited from Mode 11, non-negotiable)

- Every bullet in the tuned `cv.md` must be traceable to a line in master `cv.md`. If a bullet cannot be traced, it does not go in.
- Do not add sections that do not exist in master `cv.md`.
- Do not write accomplishment bullets with metrics not present in master `cv.md`.
- Do not swap in JD terminology for something the CV cannot support.
- Gaps go in the `## What Changed` section and inform the cover letter. They do not get papered over.
```

---

### 6.4 `DATA_CONTRACT.md`

**Edit: Add `packets/` to the User Layer table and the Derived Files section.**

In the "User Layer" fenced code block, add after the `archive/` line:
```
├── packets/                   # All your per-application submission bundles. Sacred.
```

In the "Derived Files" section, update the description paragraph and the fenced code block:

Find:
```
├── cv-[slug]-[date].md             # Tailored CV (e.g., cv-acme-corp-2026-01-15.md). Updatable only on your request.
├── cv-[slug]-[date].docx           # ATS-formatted export. Updatable only on your request.
├── negotiation/negotiation-*.md    # Mode 7 negotiation briefs.
└── [other custom outputs]          # Other derived artifacts. Updatable only on your request.
```

Replace with:
```
├── cv-[slug]-[date].md             # Tailored CV (legacy root location). Updatable only on your request.
├── cv-[slug]-[date].docx           # ATS-formatted export (legacy root location). Updatable only on your request.
├── negotiation/negotiation-*.md    # Mode 7 negotiation briefs.
├── packets/[company-slug]/[role-slug]/cv.md             # Tuned CV in packet (Mode 14 output).
├── packets/[company-slug]/[role-slug]/cv.docx           # ATS export in packet (Mode 14 output).
├── packets/[company-slug]/[role-slug]/cover-letter.md   # Tuned cover letter in packet (Mode 14 output).
├── packets/[company-slug]/[role-slug]/cover-letter.docx # Cover letter export (Mode 14 output).
└── [other custom outputs]          # Other derived artifacts. Updatable only on your request.
```

Also update the Summary Table row for Derived Files to include `packets/`:

Find:
```
| **Derived Files** | cv-[slug]-[date].md, cv-[slug]-[date].docx, etc. | Only on explicit request | Review before use, edit as needed, version as you see fit |
```

Replace with:
```
| **Derived Files** | cv-[slug]-[date].md, cv-[slug]-[date].docx, packets/[company-slug]/[role-slug]/cv.md, cover-letter.md, cover-letter.docx, etc. | Only on explicit request | Review before use, edit as needed, version as you see fit |
```

---

### 6.5 `README.md`

**Edit 1: Update "Project structure" code block to include `packets/`.**

In the fenced block under "Project structure", add after the `archive/` line:
```
└── packets/                # Per-application submission bundles (cv, cover letter, manifest)
```

Remove the existing trailing comment on `archive/` if it wraps awkwardly; the block is visual and correctness matters more than formatting parity.

**Edit 2: Update the "Governance" section.**

Find:
```
**User layer (never overwritten by updates):** `cv.md`, `profile.md`, `stories.md`, `config.md`, `dashboard.md`, and all working folders (`evals/`, `outreach/`, `cover-letters/`, `interview-prep/`, `research/`, `daily/`, `weekly/`, `archive/`).
```

Replace with:
```
**User layer (never overwritten by updates):** `cv.md`, `profile.md`, `stories.md`, `config.md`, `dashboard.md`, and all working folders (`evals/`, `outreach/`, `cover-letters/`, `interview-prep/`, `research/`, `daily/`, `weekly/`, `archive/`, `packets/`).
```

---

### 6.6 OSS scaffolding: `.gitkeep` files

Add one `.gitkeep` to the `packets/` directory so Git tracks the folder in the open-source repo. The `target-radar/` and `reference/` `.gitkeep` files are owned by Plan 25 and are not created here.

File to create: `packets/.gitkeep` (empty file, no content).

---

### 6.7 `test_package.py`: update frozen entry list

The frozen list currently has 17 entries. Adding `mode14-packet-assembly.md` is one of four bundle additions across Plans 23 to 25; the final frozen list is 21 entries. See the Cross-plan reconciliation in features/plan/README.md. Update `EXPECTED_BUNDLE_ENTRIES` in `tests/test_package.py`:

Add to the list:
```python
"skill/references/mode14-packet-assembly.md",
```

The list is sorted alphabetically; insert it between `"skill/references/mode13-calibration.md"` and `"skill/references/mode2-portal-scan.md"`.

Also update the docstring comment near `test_zip_has_no_unexpected_top_level_entries` from "expected 17 entries" to "expected 21 entries" (final count after Plans 23 to 25).

---

## 7. Tests to Add

### 7.1 `tests/test_skill_structure.py` — add one test

Add to the existing file, after `test_mode_13_calibration_exists`:

```python
def test_mode_14_packet_assembly_exists(skill_md):
    """Verify Mode 14 (Packet Assembly) section exists."""
    has_section = "Mode 14" in skill_md or "packet assembly" in skill_md.lower()
    assert has_section, "Mode 14 (Packet Assembly) missing from SKILL.md"
```

Also update `test_all_modes_exist` to include 14:

Find:
```python
    for mode in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
```

Replace with:
```python
    for mode in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
```

### 7.2 `tests/test_vault_files.py` — add packet scaffold check

The existing `test_vault_files.py` verifies required directories exist. Add a test that `packets/` is present (or a `.gitkeep` in it, so the test works against the open-source repo before any real packets are created):

```python
def test_packets_directory_exists(vault_path):
    """Verify packets/ directory (or its .gitkeep) is present in vault root."""
    packets_dir = vault_path / "packets"
    assert packets_dir.exists(), (
        "packets/ directory missing from vault root. "
        "Create it with a .gitkeep per plan 23."
    )
```

### 7.3 `tests/test_docs_consistency.py` — no change required

The four Notion-optionality rules tested here are not affected by packets. No edit needed.

### 7.4 `tests/test_schema_validation.py` — add packet schema (future, not this plan)

A JSON schema for packet frontmatter (`schemas/packet.schema.json`) and a corresponding example (`examples/example-packet.md`) are appropriate follow-up additions, but are not part of this plan. Adding them requires creating example content, which is a separate authoring task. Note this as a follow-up in `tests/SKIPPED_TESTS.md` when the test is added.

---

## 8. Acceptance Criteria

- [ ] `packets/` directory exists at the vault root with a `.gitkeep`.
- [ ] `packets/[company-slug]/[role-slug]/` path structure is documented in both `SKILL.md` and `skill/references/file-conventions.md`.
- [ ] `skill/references/mode14-packet-assembly.md` exists with the full step sequence, frontmatter schema, file set, and fabrication rules.
- [ ] SKILL.md Mode 14 section exists with trigger, summary, reference pointer, and output path.
- [ ] `file-conventions.md` folder structure block matches the canonical structure in section 3 of this spec.
- [ ] `file-conventions.md` includes a "Packets" subsection with frontmatter schema, required-file list, cross-linking rule, naming rule, legacy migration note, and archive behavior.
- [ ] `DATA_CONTRACT.md` User Layer table includes `packets/`.
- [ ] `DATA_CONTRACT.md` Derived Files section includes `packets/[company-slug]/[role-slug]/cv.md`, `cv.docx`, `cover-letter.md`, `cover-letter.docx`.
- [ ] `README.md` project structure block includes `packets/`.
- [ ] `README.md` Governance section includes `packets/` in the user-layer list.
- [ ] `test_package.py` frozen list updated to 21 entries (Plans 23 to 25 combined): adds mode14-packet-assembly.md, mode15-target-radar.md, SEND_READY_CONTRACT.md, send_ready_config.json.
- [ ] `test_skill_structure.py` `test_all_modes_exist` includes Mode 14; `test_mode_14_packet_assembly_exists` added.
- [ ] `test_vault_files.py` `test_packets_directory_exists` added and passes.
- [ ] All existing tests pass (no regressions).
- [ ] CI `skill-parity` job passes (bundle rebuilt, byte-match guard satisfied).

---

## 9. Out of Scope / Owned by Other Plans

- **Send-ready validation** (`send_ready: true` logic, validator that reads the `contents` checklist and confirms docx files are present): Plan 24.
- **`target-radar/` and `reference/` folder scaffolding** (including their `.gitkeep` files): Plan 25.
- **Live vault cleanup** (migrating existing `cv-[slug]-[date].md` root files and `cover-letters/cover-[slug]-[date].md` files into `packets/` directories, migrating existing ad-hoc packet folders from PascalCase to lowercase-hyphen slugs, renaming `Mark-McGrath-CV.docx` to `cv.docx` inside each packet): Plan 26.
- **Packet Dataview queries** (adding a `packets` table to `dashboard.md` showing `send_ready` status, `status`, and `related_eval` per packet): a dashboard update not scoped here.
- **`schemas/packet.schema.json` and `examples/example-packet.md`**: schema authoring task, not scoped here.
- **Archive integration for packets** (auto-proposing `packets/[slug]/` move to `archive/[slug]/packets/` in Mode 9 terminal-archival flow): a Mode 9 update not scoped here, deferred to Plan 27.
