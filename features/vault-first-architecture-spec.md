# Vault-First Architecture — Spec for Notion Decoupling

**Status:** Proposed
**Impact:** Touches SKILL.md (all Notion-dependent sections), config.md, README.md, dashboard.md, PRIVACY.md, DATA_CONTRACT.md, email automation plan.

---

## 1. Design Decision

**The Obsidian vault becomes the single source of truth for all pipeline state.** Notion becomes an optional, one-way display mirror — vault writes to Notion, never Notion to vault. If Notion is not configured, nothing is lost. Every feature works fully from local markdown files.

### What this eliminates

| Current problem | Resolution |
|----------------|------------|
| Dual source of truth ("Notion wins for status; markdown wins for content") | One source: the vault. Notion is a read-only projection. |
| Compensation data stored in Notion's cloud | Stays local unless user explicitly opts in. |
| config.md must have valid Notion IDs before the skill works properly | Skill works fully without Notion. Zero config to start. |
| Dedup check requires Notion query | Dedup checks the local `evals/` folder. |
| Mode 9 status sync reads from and writes to Notion | Reads and writes local eval frontmatter. Optionally mirrors to Notion. |
| Mode 10 references "the Notion tracker link" in calendar events | References the dashboard.md file or a vault URI instead. |

### What Notion becomes (if configured)

A **sync target**, not a data source. After any vault write that changes pipeline state (new eval, status update, outcome change), the skill offers to push the change to Notion. The push is:
- One-way: vault → Notion. Never read from Notion to determine state.
- Optional: if Notion isn't configured, the step is silently skipped.
- Batched: status updates are proposed as a batch, not one-by-one.
- Lossy by design: the Notion row is a summary. The markdown file is the full record.

---

## 2. Every Notion Touchpoint — Current vs. Proposed

### 2.1 — Notion Tracker Section (SKILL.md lines 22–52)

**Current:** Defines Notion as the tracker. Config.md must have three Notion IDs. The skill writes rows via `notion-create-pages`.

**Proposed replacement:**

```markdown
## Pipeline Tracker

The pipeline tracker is the **eval frontmatter** across all files in `evals/`.
Every evaluation is a row. The frontmatter fields are the columns. The vault
IS the tracker — no external database is needed.

**Pipeline queries** live in `dashboard.md` and use Dataview to surface:
- Active pipeline (status not in [Rejected, Passed, Archived])
- Follow-ups due (status = Applied, date > 7 days ago, outcome = Pending)
- Interviews this week (status = Interviewing)
- Offers pending (status = Offer)

### Optional: Notion Mirror

If the user wants a visual board view or mobile access, they can configure
a one-way sync to Notion. This is a **display layer**, not a data source.

**Configuration (in config.md):**
```yaml
notion:
  enabled: false                    # Set to true to enable Notion sync
  data_source_id: ""                # 32-char hex UUID
  parent_page_url: ""               # https://app.notion.com/p/<id>
  tracker_url: ""                   # https://www.notion.so/<id>
  sync_compensation: false          # If false, writes "See vault" instead
                                    # of actual salary data
```

**When enabled:**
- After saving an eval to `evals/`, the skill offers: "Push to Notion? [y/n]"
- For batch operations (status sync, batch eval), propose all Notion pushes
  as a single batch for user approval.
- Notion rows contain: Company, Role, Grade, Score, Status, Date, Location,
  Compensation (redacted unless sync_compensation is true), Outcome, Notes.
- If a Notion write fails, warn the user and continue. The vault has the data.
  Notion failure is never blocking.

**When not enabled:**
- All Notion steps are silently skipped. No messages, no warnings after
  the first session.
- The skill works identically in every other respect.
```

### 2.2 — Setup Section (SKILL.md lines 54–67)

**Current:** Reads config.md and warns if Notion values are missing.

**Proposed change:**

Replace the config.md handling:

```markdown
3. **`config.md`** — per-user configuration. Optional. If missing, the skill
   runs with defaults (no Notion, no Gmail domain filtering, default scoring
   weights). The skill never creates config.md — the user creates it when
   they want to customize behavior.
```

Remove the line: "Mention once in the first Mode 1 run of the session that tracker logging is off until `config.md` is populated." — Notion is now optional by design, not a missing-configuration state.

### 2.3 — Mode 1: Dedup Check (SKILL.md lines 249–254)

**Current:** Searches Notion for existing entries with the same Company + Role. If Notion isn't configured, skips dedup entirely.

**Proposed replacement:**

```markdown
**Before saving — dedup check:**

Before writing a new eval file, scan `evals/` for an existing file matching
the same company slug. Use the file naming convention: if
`evals/eval-[company-slug]-*.md` exists, read its frontmatter.

If a match exists for the same role:
- Show the user the existing entry (date, grade, status, outcome) and ask:
  "You already evaluated [Role] at [Company] on [date] — grade [X].
  Update that entry, create a versioned re-evaluation, or skip?"
- Default to creating a versioned file (`eval-[slug]-[date]-v2.md`) per
  the eval versioning rules.

If a match exists for a different role at the same company:
- Note it: "You've previously evaluated [Other Role] at [Company]."
  Proceed with the new eval.

If no match exists, proceed with a fresh file.

This check runs against local files. It works whether or not Notion is configured.
```

### 2.4 — Mode 1: Post-Evaluation Steps (SKILL.md lines 256–262)

**Current:** Step 2 is "Run the dedup check, then log the result to Notion."

**Proposed replacement:**

```markdown
After delivering the report:
1. Save the report as `evals/eval-[company-slug]-[date].md` — with
   `type: eval` frontmatter. The report body goes below the frontmatter block.
2. Run the dedup check (against local `evals/` folder, see above).
3. **Notion mirror (if enabled):** Push the eval summary to Notion.
   If `notion.sync_compensation` is false, write "See vault" in the
   Compensation field. Confirm with user before pushing.
4. **Gmail cross-check** (unchanged from current).
5. **Calendar reminder** (unchanged, but reference dashboard.md
   instead of "the Notion tracker link" in event descriptions).
6. **Next-step menu for grade B+** (unchanged).
```

### 2.5 — Mode 9: Application Status Sync (SKILL.md lines 658–662)

**Current:** Pulls applications from Notion, cross-references Gmail, proposes Notion updates.

**Proposed replacement:**

```markdown
**Application Status Sync.** When asked to "update my tracker" or
"see if there are any updates":

1. Scan `evals/` for files with `status: Applied` or `status: Interviewing`
   in their frontmatter. Read the company name, role, date, and status
   from each.
2. For each, search Gmail for the company domain or recruiter name
   in the last 30 days.
3. Classify any new messages: acknowledgment, advancement, rejection,
   offer, or silence.
4. Propose frontmatter updates in a batch for user approval:
   - Show: "[Company] — [Role]: status Applied → Interviewing
     (based on scheduling email from recruiter@company.example.com)"
   - Never write without confirmation.
5. For each approved change, update the eval file's frontmatter
   (`status:` and `outcome:` fields).
6. **Notion mirror (if enabled):** After vault updates are confirmed,
   push the status changes to Notion as a batch.
```

### 2.6 — Mode 9: Follow-up Engine (SKILL.md lines 664–671)

**Current:** Queries Notion for Applied rows older than 7 days.

**Proposed replacement:**

```markdown
**Follow-up Engine.** When asked to "check follow-ups" or periodically:

1. Scan `evals/` for files where:
   - `status: Applied`
   - `date:` is more than 7 days ago
   - `outcome:` is `Pending` (no response yet)
2. For each, search Gmail for any recent thread with that company.
   If there's no response and no active thread, draft a polite follow-up.
3. Surface the drafts for user review. Never send.
```

### 2.7 — Mode 9: Cross-Reference Principle (SKILL.md line 690)

**Current:** "Always check Notion before drafting a follow-up."

**Proposed replacement:**

```markdown
- **Cross-reference before acting.** Always check the eval file's current
  status and outcome before drafting a follow-up — if the user already
  heard back and just didn't update the frontmatter, a follow-up email
  is embarrassing. When in doubt, ask.
```

### 2.8 — Mode 10: Follow-up Reminders (SKILL.md lines 712–715)

**Current:** "When a Mode 1 evaluation is logged to Notion with intent to apply, or when the Notion status changes to Applied..."

**Proposed replacement:**

```markdown
**Follow-up Reminders.** When the user indicates they've applied
(or when a Mode 9 status sync changes status to "Applied"):
1. Create a private all-day event titled `Follow up: [Company] — [Role]`
   at day 7 after application.
2. Event description includes: the role, the eval file path
   (`evals/eval-[slug]-[date].md`), and suggested action
   ("Check Gmail thread; if no response, draft a follow-up via Mode 9").
3. Optionally create a second reminder at day 14.
```

### 2.9 — Mode 10: Weekly Pipeline Review (SKILL.md lines 721–724)

**Current:** Points to "the Notion tracker" in the event description.

**Proposed replacement:**

```markdown
**Weekly Pipeline Review.**
...
2. Create a recurring event titled `Pipeline review — Dossier` with a
   description that lists the review checklist:
   - Open `dashboard.md` for the live pipeline view
   - Check: new grades ≥ B to apply to
   - Check: stale "Applied" rows needing follow-up
   - Check: interviews this week needing prep
   - Check: offers pending decision
```

### 2.10 — Mode 10: Interview Roster (SKILL.md lines 726–729)

**Current:** Uses "specific company names from Notion."

**Proposed replacement:**

```markdown
**Interview Roster View.** When the user asks "what interviews do I have this week":
1. Use `list_events` with a date range filter and search terms like
   `interview` or company names read from eval files with
   `status: Interviewing`.
```

### 2.11 — General Principles (SKILL.md line 751)

**Current:** "Always log evaluations to Notion."

**Proposed replacement:**

```markdown
**Always save evaluations to the vault.** Every completed evaluation must be
saved as a markdown file in `evals/` — don't skip this step even if the
grade is low. The vault is the source of truth. If Notion is configured,
mirror the eval there too.
```

---

## 3. Dashboard.md — The Local Pipeline View

With the vault as the single source of truth, `dashboard.md` becomes the primary pipeline interface. It needs to ship with working Dataview queries.

**Proposed dashboard.md content:**

```markdown
# Pipeline Dashboard

> Requires the Dataview community plugin in Obsidian.

## Active Pipeline

```dataview
TABLE company AS "Company", role AS "Role", grade AS "Grade",
      score AS "Score", status AS "Status", outcome AS "Outcome",
      date AS "Date", location AS "Location"
FROM "evals"
WHERE type = "eval"
  AND status != "Rejected"
  AND status != "Passed"
  AND status != "Archived"
SORT date DESC
```

## Follow-ups Due

```dataview
TABLE company AS "Company", role AS "Role", date AS "Applied",
      outcome AS "Outcome"
FROM "evals"
WHERE type = "eval"
  AND status = "Applied"
  AND outcome = "Pending"
  AND date <= date(today) - dur(7 days)
SORT date ASC
```

## Interviews Coming Up

```dataview
TABLE company AS "Company", role AS "Role", date AS "Date"
FROM "evals"
WHERE type = "eval" AND status = "Interviewing"
SORT date ASC
```

## Offers Pending

```dataview
TABLE company AS "Company", role AS "Role", compensation AS "Comp",
      date AS "Date"
FROM "evals"
WHERE type = "eval" AND status = "Offer"
SORT date DESC
```

## Recent Evaluations (Last 14 Days)

```dataview
TABLE company AS "Company", role AS "Role", grade AS "Grade",
      score AS "Score", legitimacy AS "Legit", status AS "Status"
FROM "evals"
WHERE type = "eval"
  AND date >= date(today) - dur(14 days)
SORT date DESC
```

## Grade Distribution

```dataview
TABLE length(rows) AS "Count"
FROM "evals"
WHERE type = "eval"
GROUP BY grade
SORT grade ASC
```

## Outreach Pending

```dataview
TABLE company AS "Company", role AS "Role", channel AS "Channel",
      status AS "Status"
FROM "outreach"
WHERE type = "outreach" AND status = "drafted"
SORT date DESC
```

## Recent Daily Activity

```dataview
LIST
FROM "daily"
SORT file.name DESC
LIMIT 10
```
```

---

## 4. How the Skill Reads Pipeline State (Without Notion)

The critical question: how does the skill query the vault when it can't use Dataview at runtime?

**Answer:** The skill reads eval files directly. In Claude.ai, this means using the `view` tool to list `evals/` and read frontmatter from individual files. In Claude Code, this means shell commands (`grep`, `head`, `yq`).

**Practical approach for SKILL.md:**

```markdown
## Reading Pipeline State

When a mode needs to query the pipeline (e.g., "which companies am I
waiting to hear from?"), use this approach:

1. List the files in `evals/` (and `archive/` if historical data is needed).
2. Read the frontmatter of each file. Focus on: `company`, `role`,
   `status`, `outcome`, `date`, `grade`, `score`.
3. Filter in-memory based on the query (e.g., status = "Applied",
   date > 7 days ago).
4. If the folder has more than ~30 active eval files, read frontmatter
   only (not the full report body) to keep context manageable.

This is less efficient than a database query but works reliably with
local files. For users with large pipelines (100+ evaluations),
recommend archiving terminal-state evaluations to keep `evals/` focused.
```

**Performance reality check:** At the scale of a personal job search (10–50 active evaluations, maybe 200 total over a search), reading frontmatter from markdown files is fast and well within context limits. This is not a scalability concern at realistic pipeline sizes.

---

## 5. Config.md — Simplified

With Notion optional, config.md simplifies significantly. A user can start with zero configuration.

**Proposed config.md template:**

```yaml
# Dossier Configuration
# All sections are optional. The skill runs with defaults if this file
# is missing or empty.

# --- Notion Mirror (optional) ---
# Enable to push eval summaries to a Notion board for visual tracking.
# The vault remains the source of truth regardless.
notion:
  enabled: false
  data_source_id: ""           # 32-char hex UUID from your Notion database
  parent_page_url: ""          # https://app.notion.com/p/<id>
  tracker_url: ""              # https://www.notion.so/<id>
  sync_compensation: false     # If false, salary data stays local

# --- Privacy & Filtering ---
redact_comp: false             # If true, suppress comp data in all
                               # non-local outputs (Notion, calendar events)
gmail_allow_domains: []        # Only process emails from these domains
gmail_deny_domains: []         # Never process emails from these domains

# --- Scoring ---
scoring_weights: {}            # Override default dimension weights
                               # Example: { "Remote / Location Fit": 15 }
                               # Must sum to 100. Unspecified = default.

# --- Email Automation (companion skill) ---
email_automation:
  trust_level: 1               # 1 = draft, 2 = draft+notify, 3 = auto-send
  daily_auto_send_cap: 5
  min_days_between_sends: 5
  max_sequence_length: 3
```

---

## 6. Impact on Other Documents

### README.md

**Remove:** "Source-of-truth ownership" section that says "Notion tracker owns structured pipeline state."

**Replace with:**

```markdown
## Source of Truth

The Obsidian vault is the single source of truth for all pipeline data.
Eval files in `evals/` contain the authoritative status, grade, outcome,
and compensation data. `dashboard.md` provides live pipeline views via
Dataview queries.

Notion is an optional display mirror. If configured, the skill pushes
eval summaries to Notion after vault writes. Notion never overwrites
vault data. If the vault and Notion disagree, the vault wins — always.
```

### PRIVACY.md

**Remove Notion from the "high risk" category.** It moves to "optional, user-controlled" with a clear note:

```markdown
### Notion (optional mirror)
- If enabled, eval summaries are pushed to Notion: company, role, grade,
  score, status, date, location, outcome, notes.
- Compensation data is NOT sent unless `sync_compensation: true` in config.md.
- To disable Notion entirely: set `notion.enabled: false` or omit the
  section from config.md.
- If you never configure Notion, no data ever reaches Notion's servers.
```

### DATA_CONTRACT.md

**No change.** Notion config values are already in the user layer (config.md). The contract is unchanged.

### Email Automation Plan

**Change:** Replace all references to "reads pipeline state from Notion" with "reads pipeline state from eval frontmatter." The sequence trigger logic (§9.9) now reads:

```
| Eval frontmatter status → | Sequence action |
|---------------------------|-----------------|
| status: Applied, date > 7 days, outcome: Pending | Start follow_up_application |
| status: Interviewing (interview logged complete) | Start thank_you_post_interview |
| status: Rejected | Cancel all active sequences |
| status: Offer | Cancel follow-up sequences |
| status: Passed | Cancel all sequences |
```

The Notion MCP is no longer in the data flow for sequence triggers.

### Consolidated Assessment

**Change:** The Privacy section's PII exposure surface shrinks. Notion drops from a mandatory data sink to an opt-in display layer. The risk profile improves.

---

## 7. Migration Path for Existing Users

If someone is already using Dossier with Notion:

1. **Nothing breaks immediately.** Setting `notion.enabled: true` in config.md
   preserves current behavior — the skill still pushes to Notion.
2. **The vault becomes authoritative.** Status changes now update the eval
   file first, then mirror to Notion. If a conflict exists, the eval file wins.
3. **Gradual transition.** Users can stop using Notion at any time by setting
   `notion.enabled: false`. All data remains in the vault.
4. **No data loss.** Every eval was already being saved as a markdown file.
   The Notion rows were always copies.

---

## 8. Summary of All SKILL.md Changes

| Section | Change type | Summary |
|---------|------------|---------|
| Notion Tracker (lines 22–52) | **Rewrite** | Becomes "Pipeline Tracker" with vault-first design + optional Notion mirror. |
| Setup (lines 54–67) | **Edit** | config.md is optional. No Notion warnings. |
| Mode 1 dedup (lines 249–254) | **Rewrite** | Scans `evals/` folder instead of Notion. |
| Mode 1 post-eval (lines 256–262) | **Edit** | Step 2 saves to vault first, then optionally mirrors to Notion. |
| Mode 9 status sync (lines 658–662) | **Rewrite** | Reads/writes eval frontmatter, optionally mirrors to Notion. |
| Mode 9 follow-up (lines 664–671) | **Rewrite** | Scans eval frontmatter for Applied > 7 days. |
| Mode 9 cross-reference (line 690) | **Edit** | "Check eval file" replaces "check Notion." |
| Mode 10 follow-up reminders (lines 712–715) | **Edit** | References eval file path, not Notion link. |
| Mode 10 weekly review (lines 721–724) | **Edit** | References dashboard.md, not Notion tracker. |
| Mode 10 interview roster (lines 726–729) | **Edit** | Reads company names from eval files, not Notion. |
| General principles (line 751) | **Edit** | "Always save to vault" replaces "always log to Notion." |
| New section: Reading Pipeline State | **Add** | Defines how the skill queries the vault without Dataview. |

**Estimated effort:** 3–4 hours to rewrite all affected sections. No new modes required. The changes simplify rather than add complexity.

---

## 9. What This Gains

| Before | After |
|--------|-------|
| Two sources of truth with conflict rules | One source of truth (vault) |
| Compensation data in Notion's cloud by default | Compensation data local by default |
| config.md must have 3 valid Notion IDs to work properly | config.md is optional; skill works with zero config |
| Dedup requires a Notion API query | Dedup scans local files (faster, no API dependency) |
| Mode 9 reads pipeline from Notion | Mode 9 reads pipeline from local frontmatter |
| Notion outage blocks pipeline operations | Notion outage blocks nothing; mirror catches up later |
| Privacy analysis must document Notion as a data sink | Notion is opt-in; users who don't configure it have no cloud exposure beyond Anthropic |
| 7 external services in the PII exposure surface | 6 (Notion drops to opt-in, not default) |
