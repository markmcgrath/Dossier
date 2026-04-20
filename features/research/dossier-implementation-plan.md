# Dossier Skill — Implementation Plan

**Companion document:** `dossier-gap-analysis.md`
**Deployment model:** Claude.ai skill (primary), with notes on Claude Code extensions where applicable.

---

## How to read this plan

Each work item includes: what changes, where in the codebase it goes, the exact content or logic to add, dependencies on other items, and acceptance criteria. Items are grouped into four phases. Within each phase, items are ordered by dependency — do them top to bottom.

The plan touches four file categories:

| Category | Files | Rule |
|----------|-------|------|
| Skill definition | `SKILL.md` | Core behavior. Edits here change how every mode works. |
| Reference docs | `scoring-guide.md`, `stories.md` (new) | Read-only reference for modes. |
| Governance docs | `PRIVACY.md` (new), `DATA_CONTRACT.md` (new) | User-facing documentation. Not read by the skill at runtime. |
| Vault config | `config.md`, `README.md`, `dashboard.md` | User-edited. Skill reads but never overwrites. |

---

## Phase 1 — Foundation

**Goal:** Reduce risk, harden the config path, and add the feedback loop that makes everything downstream more valuable.

---

### 1.1 — PRIVACY.md

**What:** A new governance document at the vault root that maps every PII data flow, names the external services, describes what data each receives, and states the user's responsibilities.

**Where:** `Dossier/PRIVACY.md` (new file)

**Content outline:**

```markdown
# Privacy & Data Flow

This document describes what personal data the Dossier skill processes,
where it sends that data, and what you should know before using each integration.

## Data inventory

| Data type | Example | Where it goes |
|-----------|---------|---------------|
| Full CV | Employment history, education, skills | Anthropic (every mode), Notion (summary only) |
| Contact info | Email, phone, address | Anthropic, Gmail (drafts), Apollo (lookups) |
| Salary data | Current comp, offer ranges, expectations | Anthropic, Notion (Compensation column) |
| Recruiter emails | Thread content, sender info | Anthropic (via Gmail MCP) |
| Calendar events | Interview times, prep blocks | Google Calendar (via MCP) |
| Contact lookups | Names, titles, emails of recruiters | Apollo, Anthropic |
| LinkedIn activity | Profile views, messages, search queries | LinkedIn (via browser session) |
| Job search queries | Role titles, locations, keywords | Indeed, Dice (via MCP) |

## Per-service risk notes

### Anthropic (Claude)
- Every mode sends your CV + profile + JD content to Claude's API.
- Under Anthropic's consumer terms, conversations may be used for safety
  research unless you opt out or use the API with data retention controls.
- **Mitigation:** If you handle sensitive comp data, consider using Claude
  via the API with zero-data-retention enabled.

### Notion
- Tracker rows contain: company, role, grade, compensation, notes.
- Ensure your tracker is in a **private workspace**. Do not use a shared
  team workspace for job search tracking.
- The `redact_comp` config flag (see config.md) suppresses compensation
  data in Notion rows if enabled.

### Gmail (via MCP)
- Mode 9 searches your inbox with broad queries. Personal emails matching
  job-related keywords may be surfaced and sent through Claude's context.
- **Mitigation:** Configure `gmail_allow_domains` and `gmail_deny_domains`
  in config.md to restrict which sender domains are processed.

### Apollo
- Contact lookups create permanent records in Apollo's system tied to your
  account. Apollo's privacy policy governs retention.
- Dossier uses Apollo for firmographic data and contact discovery only.

### LinkedIn (browser automation)
- Mode 8 operates in your authenticated browser session.
- LinkedIn's Terms of Service prohibit automated access. Use of Mode 8
  is at your own risk. The skill never sends messages or accepts
  connections without your explicit approval, but browser automation
  is inherently fragile.
- **Recommendation:** Use Mode 8 sparingly and prefer Apollo or web
  search for contact discovery when possible.

### Indeed / Dice
- Search queries reveal your job search intent and preferences.
- These services have their own data retention policies.

## Regulatory notes

Dossier is a **candidate-side** tool — you are using it to manage your own
job search. The regulatory obligations that apply to employer-side AI hiring
tools (bias audits, DPIA, candidate notification under EU AI Act) do not
apply to you as a candidate. However:

- **GDPR (EU):** If you are in the EU, your personal data flows to
  US-based services (Anthropic, Notion, Google, Apollo). Each service
  should have Standard Contractual Clauses in place. Review their DPAs.
- **CCPA/CPRA (California):** You have the right to know what data each
  service collects and to request deletion. Exercise these rights directly
  with each service provider.
- **LinkedIn ToS:** Browser automation is a gray area. See above.

## Encryption at rest

Your Obsidian vault is plaintext markdown on disk. If your machine is
compromised, all job search data is exposed.

**Recommended:** Enable full-disk encryption (FileVault on macOS,
BitLocker on Windows, LUKS on Linux).

## Data retention

See the retention policy in README.md. Summary: archive after 90 days
of inactivity, consider purging compensation data from archived evals
after 12 months.
```

**Acceptance criteria:**
- File exists at vault root.
- Covers all 7 external services.
- Includes regulatory section appropriate to a candidate-side tool.
- Referenced from README.md.

---

### 1.2 — DATA_CONTRACT.md

**What:** Formal separation of user-owned files from system files, so future skill updates never overwrite personal data.

**Where:** `Dossier/DATA_CONTRACT.md` (new file)

**Content:**

```markdown
# Data Contract

This document defines which files belong to the user and which belong
to the skill system. It protects your data during skill updates.

## User Layer — NEVER overwritten by skill updates

These files contain your personal data and customizations. The skill
reads them but will never create, overwrite, or delete them.

- `cv.md` (or cv.docx / cv.pdf)
- `profile.md`
- `config.md`
- `stories.md`
- `dashboard.md`
- `evals/` — all contents
- `outreach/` — all contents
- `cover-letters/` — all contents
- `interview-prep/` — all contents
- `research/` — all contents
- `daily/` — all contents
- `weekly/` — all contents
- `archive/` — all contents
- `.lead-pulse-state.json`

## System Layer — updatable

These files define skill behavior and can be replaced during updates.
Back up before updating if you have customized them.

- `SKILL.md` (the skill definition)
- `scoring-guide.md`
- `PRIVACY.md`
- `DATA_CONTRACT.md` (this file)
- `README.md`

## Derived files — created by the skill, owned by the user

These are generated by skill modes and belong to the user once created:

- `cv-[company-slug]-[date].md` (tailored CVs)
- `cv-[company-slug]-[date].pdf` (ATS-safe PDFs, when generated)
- `negotiation-[company-slug]-[date].md`

Once created, the skill will only modify these files if the user
explicitly requests it (e.g., "update the eval for Company X").
```

**Acceptance criteria:**
- File exists at vault root.
- Every file/folder in the vault is categorized.
- README.md references this document.

---

### 1.3 — Mode 0: Health Check

**What:** A validation step that runs on the first invocation of any session. Checks config, CV, and profile. Reports problems before they cascade.

**Where:** Add to `SKILL.md` as a new section immediately after "Setup: Reading the CV, Profile, and Config."

**SKILL.md addition:**

```markdown
### Mode 0: Health Check

**Trigger:** Runs automatically on the first skill invocation of a session,
before any other mode. Also runs explicitly when the user says "health check"
or "check setup."

**What to do:**

Silently validate these conditions:

1. **cv.md exists and is non-empty.** If missing → stop and ask the user
   to add it. Nothing else can run.
2. **profile.md exists.** If missing → warn once, proceed with CV only.
3. **config.md exists and contains Notion values.**
   - If missing → note "Notion logging disabled" once.
   - If present, validate:
     - `notion_data_source_id` is a 32-char hex UUID (not a placeholder).
     - `notion_parent_page_url` starts with `https://`.
     - `notion_tracker_url` starts with `https://`.
   - If any value is malformed → warn with the specific field and
     expected format. Do not attempt Notion writes until fixed.
4. **stories.md exists.** If missing → note "No story bank found.
   Create stories.md to accumulate interview stories across evaluations."
5. **gmail_allow_domains / gmail_deny_domains in config.md.** If neither
   is present → note "Gmail domain filtering not configured. Mode 9 will
   process all matching emails. Add domain filters to config.md to
   restrict scope."

**Output:** If everything passes, say nothing — proceed silently to the
requested mode. If any check fails, report all failures in a single
block before proceeding (or stopping, if cv.md is missing).

This mode runs once per session. Do not re-run on subsequent invocations
unless explicitly asked.
```

**Acceptance criteria:**
- Health check logic is defined in SKILL.md.
- Catches the 5 most common config problems.
- Does not add friction to normal usage (silent when everything passes).

---

### 1.4 — Outcome Tracking

**What:** Add an `outcome` field to the Notion schema and eval frontmatter so the system can eventually correlate grades with results.

**Where:** Three changes:

**1. SKILL.md — Notion Tracker section.** Add to the properties list:

```
- `Outcome` — one of: "Pending" | "No Response" | "Rejected" |
  "Phone Screen" | "Interview" | "Offer" | "Accepted" | "Withdrawn"
  Set to "Pending" on first log.
```

**2. SKILL.md — Eval frontmatter template.** Add to the eval YAML block:

```yaml
outcome: Pending   # Pending | No Response | Rejected | Phone Screen |
                    # Interview | Offer | Accepted | Withdrawn
```

**3. SKILL.md — Mode 9 (Inbox & Follow-up), Application Status Sync workflow.** After the existing step "Classify any new messages," add:

```
5. For each status update, also propose an `outcome` update if the new
   status implies one:
   - "Rejected" email → outcome: Rejected
   - "Schedule interview" email → outcome: Interview
   - Offer email → outcome: Offer
   Present the batch for user approval alongside status updates.
```

**4. README.md — Frontmatter conventions.** Add `outcome:` to the eval frontmatter example.

**Acceptance criteria:**
- `Outcome` column is written to Notion on new evals.
- Outcome is updated via Mode 9 status sync.
- Eval markdown frontmatter includes outcome field.

---

### 1.5 — Config Extensions

**What:** Add new config keys to `config.md` for privacy and behavior control.

**Where:** `SKILL.md` — Setup section, and a new `config.md` template section.

**New config keys:**

```markdown
## Config keys (add to config.md)

### Existing
- notion_data_source_id
- notion_parent_page_url
- notion_tracker_url

### New — Privacy & Filtering
- `redact_comp: false`        # If true, suppress compensation data in
                                # Notion rows (write "Redacted" instead).
- `gmail_allow_domains: []`   # Only process emails from these domains.
                                # Empty = process all. Example:
                                # ["google.com", "linkedin.com", "indeed.com"]
- `gmail_deny_domains: []`    # Never process emails from these domains.
                                # Takes precedence over allow_domains.

### New — Scoring
- `scoring_weights: {}`       # Override default dimension weights.
                                # Example: { "Remote / Location Fit": 15 }
                                # Unspecified dimensions keep defaults.
                                # Weights must sum to 100.
```

**SKILL.md changes:** In Mode 1, before scoring, check for `scoring_weights` overrides. In Mode 9, before processing Gmail results, apply domain filtering. In Notion logging, check `redact_comp`.

**Acceptance criteria:**
- Config keys are documented.
- Modes respect the new keys when present.
- Absent keys default to current behavior (backward compatible).

---

## Phase 2 — Competitive Parity

**Goal:** Close the most visible feature gaps relative to Career-Ops and commercial tools.

---

### 2.1 — Ghost Job Detection (Mode 1 Enhancement)

**What:** Add a "Posting Legitimacy" block to Mode 1 output, independent of the 1–5 score.

**Where:** `SKILL.md` — Mode 1 section, after the main evaluation output and before the dedup check.

**Logic:**

```markdown
**Posting Legitimacy Check (append after the main evaluation):**

Before finalizing the report, assess the posting's legitimacy using
these free signals:

1. **Posting age:** If the JD URL is available, search for it or the
   exact job title + company combination to estimate how long the posting
   has been live. Postings open for 60+ days without refresh are suspect.
2. **Requirement realism:** Count the number of required skills/years.
   If the JD lists 15+ required skills or requires 10+ years for a
   mid-level title, flag as inflated.
3. **Specificity:** Does the JD name a specific team, manager, project,
   or business unit? Vague JDs that could apply to any company are
   lower-confidence.
4. **Company hiring signals:** Cross-reference with Mode 4 data if
   available — is the company actively growing, or has it had recent
   layoffs? A company that laid off 20% of staff last quarter posting
   aggressively is a yellow flag.
5. **Duplicate detection:** Search for the same JD text across multiple
   job boards. Identical postings on 5+ boards with no company
   attribution suggest a staffing agency or ghost listing.

**Classify as one of:**
- **Verified** — Named team, specific responsibilities, company actively
  hiring, posting is fresh.
- **Plausible** — No red flags but limited specificity signals.
- **Suspect** — 2+ yellow flags (old posting, inflated requirements,
  vague responsibilities, layoff context).
- **Likely Ghost** — 3+ red flags or classic ghost job pattern
  (perpetually open, generic JD, no response channel).

**Output:** Add a single line to the report header:

```
**Grade: [LETTER]  |  Score: [X.X]/5  |  Legitimacy: [TIER]**
```

If Suspect or Likely Ghost, add a "⚠ Legitimacy Warning" section
after Red Flags explaining the specific signals.

**This check does NOT affect the numeric score or grade.** It is an
independent advisory signal. A role can score A on fit but flag as
Suspect on legitimacy.
```

**Also update:** Eval frontmatter template to include `legitimacy: Verified | Plausible | Suspect | Likely Ghost`. Notion properties to include `Legitimacy` column.

**Acceptance criteria:**
- Every Mode 1 output includes a legitimacy tier.
- Legitimacy is in eval frontmatter and Notion.
- Legitimacy is visually prominent but does not change the score.

---

### 2.2 — STAR Story Bank

**What:** A persistent file that accumulates behavioral interview stories across evaluations and prep sessions.

**Where:** `Dossier/stories.md` (new file, user layer), plus SKILL.md changes to Modes 1, 3, and 6.

**stories.md template:**

```markdown
# Story Bank

Stories in STAR+R format (Situation, Task, Action, Result, Reflection).
Tagged by competency theme. Referenced by Modes 3 (Interview Prep)
and 6 (Cover Letter). Contributed to by Mode 1 (Offer Evaluator)
when a strong CV-to-JD match surfaces a reusable story.

---

## Stories

<!-- Add stories below. Each story gets a heading, tags, and the
     STAR+R structure. Example: -->

### [Story Title]
**Tags:** leadership, stakeholder-management, data-modeling
**Source:** [Which CV bullet or project this comes from]

**Situation:** [Context — what was happening, what was at stake]
**Task:** [Your specific responsibility]
**Action:** [What you did — be specific about YOUR contribution]
**Result:** [Quantified outcome — numbers, impact, timeline]
**Reflection:** [What you learned or would do differently]

---
```

**SKILL.md changes:**

**Mode 1 — after CV Match section:** "If the CV Match section identifies a particularly strong proof point (a specific project or accomplishment that maps directly to the JD's top requirement), check `stories.md`. If no story exists for that proof point, note in the report: 'This proof point could become a strong interview story — consider adding it to stories.md.'"

**Mode 3 — Your Key Talking Points section:** "Before generating talking points from scratch, read `stories.md`. If existing stories match the role's likely evaluation criteria, use them as the foundation for talking points. Adapt framing to the specific company/role. If stories.md is empty or missing, generate from CV as currently done."

**Mode 6 — drafting principles:** "When selecting the two strongest proof points for paragraph 2, check `stories.md` first. A well-developed story with a quantified result is stronger than a raw CV bullet."

**Acceptance criteria:**
- stories.md template exists.
- Modes 1, 3, and 6 read from stories.md when it exists.
- Mode 1 suggests story contributions.
- stories.md is listed in DATA_CONTRACT.md as user layer.

---

### 2.3 — ATS-Safe CV Export (Mode 11 Extension)

**What:** After generating the tailored markdown CV, offer to produce an ATS-safe document file.

**Where:** `SKILL.md` — Mode 11, new Step 6 after the existing Step 5 (Save the file).

**SKILL.md addition:**

```markdown
**Step 6: ATS-safe export (optional, offer after saving markdown).**

Ask: "Want me to generate an ATS-safe document version for submission?"

If yes, produce a `.docx` file using these ATS-compatibility rules:

- **Single-column layout.** No tables, text boxes, graphics, or columns.
- **Standard fonts only:** Arial, Calibri, or Times New Roman. 11–12pt
  body, 14pt section headers.
- **Standard section headers:** Use exactly these labels (ATS systems
  look for them): "Professional Summary", "Experience", "Education",
  "Skills", "Certifications". Do not invent custom section names.
- **No headers/footers** for critical information (name and contact
  go in the document body, not the header).
- **Bullet points as plain dashes or dots** — no custom symbols.
- **Dates in standard format:** "Jan 2022 – Present" or "2022–2024".
- **File format:** .docx (most universally parsed). Name it
  `cv-[company-slug]-[YYYY-MM-DD].docx`.
- **Remove the "What Changed" section** — that's for the user's
  reference only, not for submission.

**Keyword match score (append to the user-facing output, not the doc):**

After generating the document, compare the top 10 JD requirements
against the document content. Report:

```
ATS Keyword Match: X/10 requirements explicitly present
Missing: [list any requirements not found in the document text]
```

This gives the user a quick sanity check before submitting.

Save to `Dossier/cv-[company-slug]-[YYYY-MM-DD].docx`.
```

**Dependency:** Requires the docx skill (`/mnt/skills/public/docx/SKILL.md`) for document generation.

**Acceptance criteria:**
- User is offered the export after every Mode 11 run.
- Generated docx follows all ATS rules.
- Keyword match score is reported.
- "What Changed" section is stripped from the export.

---

### 2.4 — Offer Comparison (Mode 7 Extension)

**What:** When the user has multiple offers, provide a structured side-by-side comparison.

**Where:** `SKILL.md` — Mode 7, new section after the existing negotiation brief.

**SKILL.md addition:**

```markdown
**Multi-Offer Comparison (triggered when 2+ offers are in play).**

If the user mentions multiple offers, or if Notion has 2+ rows in
"Offer" status, offer: "You have multiple offers — want me to run
a side-by-side comparison?"

If yes, produce a comparison matrix:

```
# Offer Comparison: [Company A] vs [Company B] (vs [Company C])

## Compensation
| Component      | Company A      | Company B      |
|----------------|----------------|----------------|
| Base salary    |                |                |
| Bonus          |                |                |
| Equity/RSU     |                |                |
| Signing bonus  |                |                |
| Total Year 1   |                |                |
| Total Year 4   |                |                |

## Non-Comp Factors
| Factor                    | Company A | Company B |
|---------------------------|-----------|-----------|
| Role & responsibility fit |           |           |
| Growth trajectory         |           |           |
| Company stability         |           |           |
| Culture signals           |           |           |
| Remote/location fit       |           |           |
| Strategic career value    |           |           |

## Decision Drivers
[What makes each offer uniquely compelling or risky.
 Not a rehash of the table — the 2–3 factors that should
 actually drive the decision.]

## Recommendation
[Clear recommendation with reasoning. If genuinely too close
 to call, say so and name the tiebreaker question the user
 should answer for themselves.]
```

Pull data from existing Mode 1 evaluations and Mode 7 negotiation
briefs. If data is incomplete (e.g., one offer hasn't been fully
evaluated), flag what's missing before comparing.
```

**Acceptance criteria:**
- Triggered when multiple offers exist.
- Comparison uses existing eval and negotiation data.
- Includes a clear recommendation or named tiebreaker.

---

## Phase 3 — Differentiation

**Goal:** Build the feedback loop and tighten privacy controls to move beyond parity into leadership.

---

### 3.1 — Calibration Report

**What:** A periodic analysis that correlates evaluation grades with actual outcomes, detecting scoring drift and identifying which dimensions are most predictive.

**Where:** `SKILL.md` — new Mode 13.

**SKILL.md addition:**

```markdown
### Mode 13: Calibration Report

**Trigger:** User asks "how accurate are my evaluations," "calibration
report," "check my scoring," or enough time has passed (50+ evaluations
or 3+ months of activity).

**What to do:**

1. **Pull data.** Query Notion for all evaluations with a non-Pending
   outcome. Minimum 15 rows needed for meaningful analysis — if fewer,
   tell the user to update outcomes and try again later.

2. **Grade-to-outcome correlation.** For each grade band (A, B, C, D, F),
   compute:
   - Total evaluations
   - % that reached Interview or beyond
   - % that reached Offer or beyond
   - % No Response
   - % Rejected

3. **Predictive check.** A well-calibrated system should show:
   - A-graded roles → highest interview rate
   - D/F-graded roles → highest no-response rate
   - Monotonically decreasing interview rate from A → F

   If this pattern breaks (e.g., B-graded roles get more interviews
   than A-graded roles), flag it and hypothesize why: scoring too
   generous at the top? Underweighting a dimension that matters
   in practice?

4. **Dimension analysis.** For roles that reached Interview+, compute
   the average score per dimension. Compare against roles that got
   No Response. Identify which dimensions are most predictive of
   actual outcomes. If a dimension (e.g., Hiring Signal Quality)
   consistently predicts outcomes better than its weight suggests,
   recommend a weight adjustment.

5. **Scoring drift.** Compute the mean score per month. If the
   overall mean has shifted by 0.5+ points over the observation
   period, flag grade inflation or deflation.

**Output:**

```
# Calibration Report — [Date]

## Summary
[2–3 sentences: is the scoring well-calibrated, and what's
 the biggest adjustment needed?]

## Grade-to-Outcome Matrix
[Table as described above]

## Most Predictive Dimensions
[Ranked list of dimensions by actual outcome correlation]

## Scoring Drift
[Mean score trend over time. Flag if drifting.]

## Recommended Adjustments
[Specific weight changes or calibration notes, if any.
 "No changes needed" is a valid output.]
```

Save to `weekly/calibration-report-[date].md`.
```

**Dependency:** Requires outcome tracking (1.4) to be in place and populated.

**Acceptance criteria:**
- Produces a meaningful report with 15+ outcomes.
- Identifies predictive dimensions.
- Detects drift.
- Recommends specific adjustments or confirms calibration is sound.

---

### 3.2 — Gmail Domain Filtering

**What:** Implement the `gmail_allow_domains` and `gmail_deny_domains` config keys in Mode 9.

**Where:** `SKILL.md` — Mode 9, all Gmail search workflows.

**SKILL.md addition (insert at the top of Mode 9, before Core workflows):**

```markdown
**Domain filtering (mandatory pre-step for all Gmail searches):**

Before processing Gmail results, apply domain filtering from config.md:

1. Read `gmail_allow_domains` and `gmail_deny_domains` from config.md.
2. If `gmail_deny_domains` is set, silently drop any thread where the
   sender domain matches a deny-listed domain. Do not summarize, do
   not mention to the user.
3. If `gmail_allow_domains` is set and non-empty, only process threads
   where the sender domain matches an allow-listed domain. Drop all
   others silently.
4. If neither is set, process all matching threads (current behavior)
   but apply the existing "stay out of personal email" principle with
   extra caution.

This filtering happens before any thread content is summarized or
sent to the user.
```

**Acceptance criteria:**
- Domain filtering runs before any thread processing in Mode 9.
- Deny-list takes precedence over allow-list.
- Absent config = current behavior (no regression).

---

### 3.3 — Eval Versioning

**What:** Support re-evaluation of the same role without losing the previous version.

**Where:** `SKILL.md` — Mode 1, dedup check section.

**SKILL.md change:** Replace the existing "One file per artifact per company per day — update in place" rule with:

```markdown
**Re-evaluation handling:**

If a file already exists at `evals/eval-[slug]-[date].md` for today:

1. Rename the existing file to `evals/eval-[slug]-[date]-v1.md`.
2. Save the new evaluation as `evals/eval-[slug]-[date]-v2.md`.
3. Increment the version suffix if further re-evaluations happen.
4. Tell the user: "Previous evaluation preserved as
   eval-[slug]-[date]-v1.md. New evaluation saved as v2."

This preserves the diff when a JD changes or the user wants a
fresh read after new information surfaces.
```

**Also update README.md** naming convention section to reflect versioning.

**Acceptance criteria:**
- Re-evaluations create versioned files, not overwrites.
- Previous versions are preserved and named clearly.
- User is informed of both filenames.

---

### 3.4 — Retention Policy & Cleanup

**What:** Document a retention policy and provide guidance for periodic cleanup.

**Where:** `README.md` (new section), `PRIVACY.md` (reference).

**README.md addition:**

```markdown
## Retention Policy

Job search data has a limited useful life. This policy keeps the vault
focused on live pipeline while preserving what matters.

### Active data (keep indefinitely while job search is active)
- cv.md, profile.md, config.md, stories.md
- All files in evals/, outreach/, cover-letters/, interview-prep/, research/

### Time-decay data (already covered by existing archival rules)
- daily/ → subfolder after 60 files
- weekly/ → subfolder after 26 files

### Terminal data (archive, then consider purging)
- When a pipeline row reaches terminal state → move to archive/
  (existing archive discipline).
- After 12 months in archive: consider deleting compensation data
  from archived evals (replace salary figures with "Archived") to
  reduce exposure if the vault is ever compromised.
- After the job search concludes: consider exporting stories.md
  (your most durable asset) and archiving or deleting the rest.

### Cleanup checklist (run quarterly or at job search conclusion)
1. Move terminal-state companies to archive/.
2. Review archive/ for files older than 12 months — redact comp data.
3. Run time-decay archival on daily/ and weekly/.
4. Delete .lead-pulse-state.json if no longer scanning.
5. Confirm config.md Notion IDs are still valid.
```

**Acceptance criteria:**
- Policy is documented in README.md.
- PRIVACY.md references the retention policy.
- Checklist is actionable without the skill's help.

---

### 3.5 — Scoring Weight Personalization

**What:** Let the user override default dimension weights via config.md.

**Where:** `SKILL.md` — Mode 1, scoring section.

**SKILL.md change (insert before the scoring table):**

```markdown
**Custom weights (optional):**

Before applying the default weight table, check config.md for a
`scoring_weights` block. If present, it contains dimension-name →
weight overrides. Example:

```yaml
scoring_weights:
  "Remote / Location Fit": 15
  "Strategic Career Value": 8
```

Rules:
- Only override dimensions that are explicitly listed. All others
  keep their default weights.
- After applying overrides, validate that all weights sum to 100.
  If they don't, warn the user and fall back to defaults.
- Gate-pass rules still apply regardless of custom weights.
- Note in the evaluation output when custom weights are active:
  "Scored with custom weights (see config.md)."
```

**Acceptance criteria:**
- Custom weights are applied when configured.
- Validation catches weights that don't sum to 100.
- Gate-pass logic is unaffected by weight changes.
- Output notes when custom weights are in use.

---

## Phase 4 — Excellence

**Goal:** Capabilities that move Dossier from "competitive" to "best-in-class." These are larger scope and may require Claude Code for full implementation.

---

### 4.1 — Batch Pipeline (Mode 12)

**What:** Accept a list of JD URLs or search results, process each through Mode 1, and output a ranked digest.

**Where:** `SKILL.md` — new Mode 12.

**SKILL.md addition:**

```markdown
### Mode 12: Batch Pipeline

**Trigger:** User provides a list of JD URLs, or asks to "evaluate all
of these" after a Mode 2 search, or says "batch evaluate."

**Constraints:** This mode works within a single conversation session.
For very large batches (20+), recommend splitting across sessions or
using Claude Code with a shell orchestrator for true parallelism.

**What to do:**

1. **Accept input.** The user provides URLs, or you have a shortlist
   from a recent Mode 2 search. Maximum 10 per batch in Claude.ai
   (context window constraint). Note the limit if the user provides more.

2. **For each JD,** run a **lightweight Mode 1** — same 10-dimension
   scoring, but with abbreviated output:
   - One-line summary instead of full Summary section
   - Score and grade only (no full dimension breakdown unless requested)
   - Legitimacy tier
   - Skip CV Tailoring Suggestions and Interview Probability

3. **Rank and present as a digest:**

```
# Batch Evaluation — [Date]

| # | Company | Role | Grade | Score | Legitimacy | One-line |
|---|---------|------|-------|-------|------------|----------|
| 1 | ...     | ...  | A     | 4.6   | Verified   | ...      |
| 2 | ...     | ...  | B     | 4.1   | Plausible  | ...      |
| 3 | ...     | ...  | C     | 3.2   | Suspect    | ...      |
```

## Top Picks (grade B or higher)
[For each, 2-sentence expanded read + "Want me to run a full
 evaluation?"]

## Skip (grade D or below)
[One line each explaining why]
```

4. **Log all to Notion** (if configured) with status "Batch-Evaluated".
5. **Save** the digest to `daily/batch-eval-[date].md`.
6. **Offer next steps:** "Want me to run full evaluations on the
   top picks? Or tailor your CV for any of them?"

**Dedup:** Before evaluating, check Notion for existing entries.
Skip any already-evaluated company+role pairs and note them in
the output.
```

**Feasibility note:** Full parallelism requires Claude Code. In Claude.ai, batch processing is sequential within a single conversation. The 10-item limit keeps context manageable.

**Acceptance criteria:**
- Accepts a list of URLs or Mode 2 results.
- Produces a ranked digest table.
- Logs all to Notion.
- Deduplicates against existing evaluations.
- Offers next-step actions on top picks.

---

### 4.2 — Portal Scanning Sub-Mode

**What:** Session-triggered scan of ATS endpoints for configured companies.

**Where:** `SKILL.md` — Mode 2 enhancement (add as a sub-mode).

**SKILL.md addition:**

```markdown
**Portal Scan sub-mode (optional, within Mode 2):**

**Trigger:** User says "scan my target companies," "check portals,"
or "any new listings at [company]?"

**Setup:** The user maintains a `target-companies.md` file (or a list
in config.md) with company names and their ATS platform type:

```yaml
target_companies:
  - name: Anthropic
    ats: greenhouse
    board_token: anthropic
  - name: Retool
    ats: ashby
    board_token: retool
  - name: ElevenLabs
    ats: lever
    board_token: elevenlabs
```

**What to do:**

1. For each company, fetch their public job board API:
   - Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{token}/jobs`
   - Ashby: `https://api.ashbyhq.com/posting-api/job-board/{token}`
   - Lever: `https://api.lever.co/v0/postings/{token}`

   Use `web_fetch` for each endpoint.

2. Filter results against profile.md's target roles and roles-to-avoid
   lists. Match on title keywords.

3. Deduplicate against Notion — skip roles already evaluated.

4. Present new matches as a shortlist (same format as Mode 2).

5. Offer to batch-evaluate the matches via Mode 12.

**Rate limiting:** No more than 10 API calls per scan session.
These are public APIs but should be used respectfully.

**This sub-mode uses zero LLM tokens for the fetching step** — the
API calls return structured JSON. LLM tokens are only spent on
filtering and presentation.
```

**Dependency:** Requires `target-companies.md` or config.md extension.

**Acceptance criteria:**
- Fetches from Greenhouse, Ashby, and Lever public APIs.
- Filters against profile.
- Deduplicates against Notion.
- Presents as a ranked shortlist.

---

### 4.3 — Weekly Trend Report

**What:** Aggregate daily scan data into market trend analysis.

**Where:** `SKILL.md` — new scheduled-task output.

**SKILL.md addition:**

```markdown
### Weekly Trend Report

**Trigger:** Part of the `weekly-pipeline-digest` scheduled task,
or on-demand when the user asks "what are the trends" or
"how's the market looking."

**What to do:**

1. Read the last 4 weeks of daily scan files and batch evaluation
   digests from `daily/`.

2. Aggregate:
   - Total new listings seen per week
   - Grade distribution per week (what % of listings scored B+?)
   - Most common role titles and keywords
   - Companies appearing most frequently
   - Salary range trends (if disclosed in enough JDs)
   - Legitimacy distribution (% Verified vs Suspect)

3. Produce a trend section in the pipeline digest:

```
## Market Trends (last 4 weeks)

- **Volume:** [increasing / stable / declining] — [X] new listings
  this week vs [Y] average.
- **Quality:** [X]% scored B or higher (vs [Y]% last month).
- **Hot roles:** [Top 3 role titles by frequency]
- **Active companies:** [Top 5 companies by listing volume]
- **Salary signals:** [Any notable shifts in disclosed ranges]
- **Ghost job rate:** [X]% of listings flagged Suspect or Likely Ghost
```

This requires enough historical data to be meaningful (4+ weeks
of daily scans). If insufficient data exists, note this and skip
the trend section.
```

**Acceptance criteria:**
- Produces trend data from accumulated daily scans.
- Identifies volume, quality, and salary trends.
- Integrates into the weekly pipeline digest.

---

## Summary: Full Work Item List

| # | Item | Phase | Touches | Depends on |
|---|------|-------|---------|------------|
| 1.1 | PRIVACY.md | 1 | New file | — |
| 1.2 | DATA_CONTRACT.md | 1 | New file | — |
| 1.3 | Mode 0: Health Check | 1 | SKILL.md | 1.5 (config keys) |
| 1.4 | Outcome Tracking | 1 | SKILL.md, README.md | — |
| 1.5 | Config Extensions | 1 | SKILL.md, config.md template | — |
| 2.1 | Ghost Job Detection | 2 | SKILL.md | — |
| 2.2 | STAR Story Bank | 2 | New file, SKILL.md | — |
| 2.3 | ATS-Safe CV Export | 2 | SKILL.md | docx skill |
| 2.4 | Offer Comparison | 2 | SKILL.md | — |
| 3.1 | Calibration Report | 3 | SKILL.md | 1.4 (outcomes) |
| 3.2 | Gmail Domain Filtering | 3 | SKILL.md | 1.5 (config keys) |
| 3.3 | Eval Versioning | 3 | SKILL.md, README.md | — |
| 3.4 | Retention Policy | 3 | README.md, PRIVACY.md | 1.1 |
| 3.5 | Scoring Weight Personalization | 3 | SKILL.md | 1.5 (config keys) |
| 4.1 | Batch Pipeline (Mode 12) | 4 | SKILL.md | 2.1 (legitimacy) |
| 4.2 | Portal Scanning | 4 | SKILL.md, config.md | — |
| 4.3 | Weekly Trend Report | 4 | SKILL.md | 4.1 or daily scans |

---

## Estimated Effort

| Phase | Items | Effort (skill editing time) | Elapsed |
|-------|-------|---------------------------|---------|
| 1 — Foundation | 5 | 3–4 hours | Day 1 |
| 2 — Competitive Parity | 4 | 4–6 hours | Days 2–3 |
| 3 — Differentiation | 5 | 4–5 hours | Days 4–6 |
| 4 — Excellence | 3 | 6–8 hours | Days 7–10 |

Total: ~17–23 hours of focused skill editing over ~10 working days.

Phase 1 can ship independently and immediately reduces risk. Each subsequent phase builds on the previous but is also independently shippable. There is no "big bang" — each item is a discrete, testable change.

---

## Testing Strategy

Each item should be validated with:

1. **Smoke test:** Run the relevant mode once with a real JD and confirm the new behavior appears in the output.
2. **Regression test:** Run a mode that was NOT changed and confirm it still works identically.
3. **Edge case:** For each item, test the "absent" case (config key missing, file missing, no Notion configured) to confirm graceful fallback.

Specific test scenarios per item are embedded in the acceptance criteria above.

---

*This plan is a living document. Reprioritize based on what the user actually needs most — if interviews are imminent, pull 2.2 (Story Bank) into Phase 1. If the user is in early search mode, pull 4.2 (Portal Scanning) forward.*
