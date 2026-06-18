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
