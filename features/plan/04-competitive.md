# Stream D — Competitive Features

**Estimated effort:** 6–8 hours
**Depends on:** [[03-foundation|Stream C]] (outcome tracking, config extensions)
**Blocks:** [[05-advanced|Stream E]] (partially — calibration needs outcomes populated)
**Reference:** [[../research/dossier-implementation-plan|Implementation Plan]] §2.1–2.4; [[../research/dossier-gap-analysis|Gap Analysis]] §2

---

## Why These Features

These close the most visible gaps relative to Career-Ops and commercial tools. Ghost job detection, STAR stories, ATS export, and offer comparison are table-stakes features that job search tools in this space offer. Without them, Dossier is strong on workflow but weak on output quality.

---

## D.1 — Ghost Job Detection

**What:** Add a "Posting Legitimacy" check to Mode 1 output, independent of the 1–5 score.

**Where:** SKILL.md Mode 1, after the main evaluation output and before the dedup check.

**Signals to assess:**
1. **Posting age** — listings open 60+ days without refresh are suspect
2. **Requirement realism** — 15+ required skills or 10+ years for mid-level title = inflated
3. **Specificity** — does the JD name a team, manager, project, or business unit?
4. **Company hiring signals** — cross-reference Mode 4 data if available (recent layoffs + aggressive posting = yellow flag)
5. **Duplicate detection** — identical JD text on 5+ boards with no attribution suggests staffing agency or ghost listing

**Classification tiers:**
- **Verified** — named team, specific responsibilities, company actively hiring, fresh posting
- **Plausible** — no red flags but limited specificity signals
- **Suspect** — 2+ yellow flags
- **Likely Ghost** — 3+ red flags or classic ghost job pattern

**Output format:** Single header line: `**Grade: [X] | Score: [X.X]/5 | Legitimacy: [TIER]**`

If Suspect or Likely Ghost, add a "Legitimacy Warning" section after Red Flags with specific signals.

**Frontmatter addition:**
```yaml
legitimacy: Verified | Plausible | Suspect | Likely Ghost
```

**Design decision:** Legitimacy does NOT affect the numeric score or letter grade. A role can score A on fit but flag as Suspect on legitimacy. These are independent dimensions — fit quality and posting authenticity are different questions.

**Acceptance:**
- Every Mode 1 output includes a legitimacy tier
- `legitimacy` field in eval frontmatter
- Dashboard query can filter by legitimacy
- Score and grade are unaffected by legitimacy rating

---

## D.2 — STAR Story Bank

**What:** A persistent file that accumulates behavioral interview stories across evaluations and prep sessions.

**Where:** `Dossier/stories.md` (new file, user layer) + SKILL.md changes to Modes 1, 3, and 6.

**Template structure:**
```markdown
# Story Bank

Stories in STAR+R format (Situation, Task, Action, Result, Reflection).
Tagged by competency theme.

---

## Stories

### [Story Title]
**Tags:** leadership, stakeholder-management, data-modeling
**Source:** [Which CV bullet or project this comes from]

**Situation:** [Context]
**Task:** [Your specific responsibility]
**Action:** [What YOU did — specific, not vague]
**Result:** [Quantified outcome]
**Reflection:** [What you learned or would do differently]
```

**Mode integrations:**

- **Mode 1** — after CV Match section: if a strong proof point maps directly to a top JD requirement, check `stories.md`. If no story exists for that proof point, suggest adding one.
- **Mode 3** — before generating talking points: read `stories.md`. If existing stories match the role's evaluation criteria, use them as foundation. If empty, generate from CV as currently done.
- **Mode 6** — when selecting proof points for paragraph 2: check `stories.md` first. A well-developed story with a quantified result is stronger than a raw CV bullet.

**Assumption challenged:** The original plan doesn't address how stories get *into* the bank. Mode 1 suggests them, but the user must write them. Consider: should Mode 3 (interview prep) *offer to create* a story entry when it generates a strong talking point? This would make the story bank grow organically instead of requiring manual effort.

**Acceptance:**
- `stories.md` template exists in vault root
- Modes 1, 3, and 6 read from it when it exists
- Mode 1 suggests story contributions
- `stories.md` listed in DATA_CONTRACT.md as user layer
- Mode 3 offers to populate stories from talking points it generates

---

## D.3 — Eval Versioning

**What:** Support re-evaluation of the same role without losing previous versions.

**Where:** SKILL.md Mode 1, dedup check section (as rewritten in [[01-architecture#A.4|A.4]])

**Behavior:**
1. If `evals/eval-[slug]-[date].md` already exists for today:
   - Rename existing to `eval-[slug]-[date]-v1.md`
   - Save new as `eval-[slug]-[date]-v2.md`
   - Increment suffix for further re-evaluations
2. Inform user of both filenames

**Also update:** README.md naming convention section to document the `-v#` suffix.

**Assumption challenged:** What about re-evaluations on different days? If someone evaluated a role on April 10 and re-evaluates on April 15, the files naturally get different dates and don't collide. The versioning only matters for same-day re-evaluations. This is the right design — cross-day re-evals are just new data points at different timestamps.

**Acceptance:**
- Same-day re-evaluations create versioned files, not overwrites
- Previous versions preserved
- User informed of both filenames
- README.md updated

---

## D.4 — ATS-Safe CV Export

**What:** After generating the tailored markdown CV in Mode 11, offer to produce an ATS-safe `.docx` file.

**Where:** SKILL.md Mode 11, new step after saving the markdown file.

**ATS compatibility rules:**
- Single-column layout — no tables, text boxes, graphics, columns
- Standard fonts only: Arial, Calibri, or Times New Roman (11–12pt body, 14pt headers)
- Standard section headers: "Professional Summary", "Experience", "Education", "Skills", "Certifications"
- Name and contact in document body, not header/footer
- Plain dashes or dots for bullets
- Standard date format: "Jan 2022 – Present" or "2022–2024"
- Output as `.docx` — most universally parsed by ATS systems
- Strip the "What Changed" section (that's user-facing only)

**Keyword match score** (appended to user-facing output, not the document):
```
ATS Keyword Match: X/10 requirements explicitly present
Missing: [requirements not found in document text]
```

**Save to:** `Dossier/cv-[company-slug]-[YYYY-MM-DD].docx`

**Dependency:** Requires the docx skill for document generation. The plan should invoke that skill when generating the export.

**Assumption challenged:** The original plan proposes PDF. But ATS parsing of PDFs is less reliable than DOCX parsing. Industry consensus is that `.docx` is the safest submission format. The original gap analysis noted Career-Ops uses HTML→PDF via Puppeteer, but that's for a code-based tool with rendering infrastructure. For a prompt-based skill, `.docx` via the docx skill is the practical choice.

**Acceptance:**
- User offered the export after every Mode 11 run
- Generated docx follows all ATS rules
- Keyword match score reported
- "What Changed" section stripped

---

## D.5 — Offer Comparison

**What:** Structured side-by-side comparison when 2+ offers are in play.

**Where:** SKILL.md Mode 7 (Salary Negotiation), new section after the existing negotiation brief.

**Trigger:** User mentions multiple offers, or 2+ eval files have `status: Offer`.

**Output structure:**
1. **Compensation table** — base, bonus, equity/RSU, signing, total year-1, total year-4
2. **Non-comp factors table** — role fit, growth trajectory, stability, culture, location, strategic value
3. **Decision drivers** — the 2–3 factors that should actually drive the decision (not a table rehash)
4. **Recommendation** — clear recommendation with reasoning, or named tiebreaker question if too close

**Data sources:** Pull from existing Mode 1 evals and Mode 7 negotiation briefs. Flag incomplete data before comparing.

**Revision from original:** The original triggers on "Notion rows in Offer status." In vault-first, this triggers on eval files with `status: Offer` in frontmatter.

**Acceptance:**
- Triggered when multiple offers exist
- Comparison uses existing eval and negotiation data
- Includes clear recommendation or named tiebreaker

---

## D.6 — Starter Vault Examples

**What:** Ship example artifacts so new users understand the expected format.

**Where:** `Dossier/examples/` directory (new, not processed by Dataview queries since it's outside `evals/`)

**Files:**
- `example-eval.md` — a realistic evaluation with complete frontmatter
- `example-outreach.md` — LinkedIn + email outreach draft
- `example-prep.md` — interview prep doc

**Why:** The deep research report noted that top-tier comparable projects ship reference implementations. For a prompt-based skill, "reference implementation" means example artifacts. New users can see what good output looks like before running their first evaluation.

**Acceptance:**
- `examples/` directory exists with 3 files
- Frontmatter in examples matches current schema (including `outcome`, `legitimacy`)
- README.md references the examples directory

---

## Estimated Breakdown

| Task | Hours |
|------|-------|
| D.1 Ghost job detection | 1.5 |
| D.2 STAR Story Bank | 1.5 |
| D.3 Eval versioning | 0.5 |
| D.4 ATS-safe CV export | 2.0 |
| D.5 Offer comparison | 1.0 |
| D.6 Starter vault examples | 0.5 |
| **Total** | **~7** |
