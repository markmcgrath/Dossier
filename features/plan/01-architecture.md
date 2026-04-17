# Stream A — Architecture: Vault-First Migration

**Estimated effort:** 5–7 hours
**Depends on:** Nothing — start here
**Blocks:** Streams C, D, E, F
**Reference:** [[../vault-first-architecture-spec|Vault-First Architecture Spec]]

---

## Why This Comes First

Every other stream touches the skill file. If we build new features against the current Notion-dependent architecture and then migrate to vault-first, we rewrite everything twice. The vault-first migration changes the substrate — do it first, build on stable ground.

The good news: the skill is already *partially* vault-first. Lines 22–32 of SKILL.md treat Notion as optional for Mode 1. The work is completing the transition in Modes 9–10 and standardizing the pattern everywhere.

---

## A.1 — Back Up and Extract the Skill Package

**What:** Create a timestamped backup of `dossier.skill`, then extract for editing.

**Steps:**
1. Copy `dossier.skill` to `skill-update/dossier.skill.bak-2026-04-15`
2. Extract: `unzip -o dossier.skill -d /tmp/skill-edit/`
3. Confirm `SKILL.md` is 764 lines and `scoring-guide.md` is present

**Acceptance:** Backup exists. Extracted files are readable.

---

## A.2 — Update Skill Frontmatter Description

**What:** The skill's `description` field (line 5 of SKILL.md) says "A–F grade + structured report logged to Notion." After vault-first, update to "A–F grade + structured report saved to your vault."

**Why this matters:** The description field controls skill triggering. Mentioning Notion in the trigger description is misleading when Notion is optional. Test skill triggering after this change.

**Acceptance:** Description no longer mentions Notion as a core feature.

---

## A.3 — Fix Config Naming

**What:** Update `config.md` header from "Career Ops" to "Dossier" for consistency.

**Where:** `config.md` line 1

**Change:** `# Career Ops — Configuration` → `# Dossier — Configuration`

**Acceptance:** Config header matches skill name.

---

## A.3 — Rewrite the Notion Tracker Section

**What:** Replace SKILL.md lines 22–52 (Notion Tracker section) with the vault-first Pipeline Tracker design.

**Key changes:**
- Eval frontmatter across `evals/` becomes the tracker — no external database needed
- Pipeline queries live in `dashboard.md` via Dataview
- Notion becomes an optional one-way mirror behind a `notion:` config block
- `sync_compensation: false` by default — salary data stays local unless opted in

**New config.md structure** (replaces the current three bare keys):

```yaml
# --- Notion Mirror (optional) ---
notion:
  enabled: true
  data_source_id: "<your-notion-data-source-id>"
  parent_page_url: "<your-notion-parent-page-url>"
  tracker_url: "<your-notion-tracker-url>"
  sync_compensation: false
```

**Assumption to verify:** The current config.md has live Notion IDs. The migration must preserve them — set `enabled: true` by default so existing behavior doesn't break. Users who want to drop Notion can set `enabled: false` later.

**Acceptance:**
- SKILL.md Pipeline Tracker section describes vault-first with optional Notion mirror
- Config.md template documents the new `notion:` block
- Existing Notion IDs are preserved and functional

---

## A.4 — Rewrite Mode 1 Dedup Check

**What:** Replace the Notion-based dedup (lines 249–254) with local `evals/` folder scanning.

**New behavior:**
1. Before writing a new eval, scan `evals/` for files matching `eval-[company-slug]-*.md`
2. If same company + same role exists: prompt user (update, versioned re-eval, or skip)
3. If same company + different role: note it, proceed
4. If no match: proceed with fresh file

**Why this matters:** Dedup currently fails silently when Notion isn't configured. Vault-first dedup always works.

**Acceptance:** Dedup runs against local files. Works identically with or without Notion.

---

## A.5 — Rewrite Mode 1 Post-Evaluation Steps

**What:** Update lines 256–262 so the save-to-vault step is primary and Notion mirror is secondary.

**New sequence:**
1. Save report as `evals/eval-[company-slug]-[date].md` with full frontmatter
2. Run dedup check (local)
3. If `notion.enabled`: offer to push summary to Notion. Confirm before pushing.
4. Gmail cross-check (unchanged)
5. Calendar reminder — reference `dashboard.md` instead of "the Notion tracker link"
6. Next-step menu for grade B+ (unchanged)

**Acceptance:** Eval is always saved locally first. Notion push is conditional and requires confirmation.

---

## A.6 — Rewrite Mode 9 Status Sync and Recruiter Triage

**What:** Replace the Application Status Sync (lines 583–587), the Recruiter Triage Notion cross-reference (line 577), and the Mode 9 intro (line 572) with vault-first versions.

**Status Sync — current:** Pulls applications from Notion, cross-references Gmail, proposes Notion updates.
**Status Sync — new:** Scans `evals/` for `status: Applied` or `status: Interviewing` in frontmatter, cross-references Gmail, proposes frontmatter updates. Optionally mirrors to Notion after vault updates are confirmed.

**Recruiter Triage — current (line 577):** "Cross-reference against Notion — does this company/role already have a row? Flag matches."
**Recruiter Triage — new:** "Cross-reference against `evals/` — does this company already have an evaluation file? If so, surface it with a wikilink: `[[eval-company-slug-date]] — Grade [X], status: [Y]`. Flag matches."

This is load-bearing: when triaging recruiter emails, knowing "you already evaluated this company as a B+" is critical context for deciding whether to respond. The vault-first version must produce the same cross-reference from local files.

**Mode 9 intro (line 572):** "Without inbox integration, the Notion tracker goes stale" → "Without inbox integration, the pipeline goes stale and follow-ups fall through the cracks."

This is the most impactful change in the migration. Mode 9 is the primary pipeline-state-management mode.

**Acceptance:**
- Status sync reads from eval frontmatter, not Notion
- Recruiter triage cross-references `evals/` folder, including wikilinks to existing evals
- Frontmatter is updated first, then Notion (if enabled)
- Mode 9 intro contains no Notion references
- Works fully without Notion configured

---

## A.7 — Rewrite Mode 9 Follow-up Engine

**What:** Replace lines 664–671 with vault-first follow-up logic.

**New:** Scan `evals/` for files where `status: Applied`, `date:` > 7 days ago, and `outcome: Pending`. Search Gmail for each. Draft follow-ups for those with no response.

**Acceptance:** Follow-up engine runs entirely from local frontmatter.

---

## A.8 — Update Mode 10 References

**What:** Update all Notion references in Mode 10 (Calendar Ops, lines 695–738).

**Changes:**
- Line 712: "When a Mode 1 evaluation is logged to Notion" → "When the user indicates they've applied (or when Mode 9 status sync changes status to Applied)"
- Line 714: "the Notion tracker link" → "the eval file path and dashboard.md"
- Lines 721–724: "points to the Notion tracker" → "points to dashboard.md"
- Lines 726–729: "company names from Notion" → "company names from eval files with `status: Interviewing`"

**Acceptance:** Mode 10 contains zero Notion-as-source references. All pipeline state comes from eval frontmatter.

---

## A.9 — Update General Principles

**What:** Replace line 751 ("Always log evaluations to Notion") with vault-first principle.

**New:** "Always save evaluations to the vault. Every completed evaluation must be saved as a markdown file in `evals/` — don't skip this step even if the grade is low. The vault is the source of truth. If Notion is configured, mirror the eval there too."

**Acceptance:** General principles section is vault-first.

---

## A.10 — Add Pipeline State Reading Instructions

**What:** Add a new section to SKILL.md (after Setup) explaining how to query the vault without Dataview.

**Content:** When a mode needs pipeline state:
1. List files in `evals/` (and `archive/` if historical data needed)
2. Read frontmatter from each file — focus on `company`, `role`, `status`, `outcome`, `date`, `grade`, `score`
3. Filter in-memory based on the query
4. For 30+ active evals, read frontmatter only (not full body) to keep context manageable

**Acceptance:** Section exists. Modes 9 and 10 reference it for their pipeline queries.

---

## A.12 — Update Dashboard.md

**What:** Fix naming, remove Notion-as-source-of-truth language, and add missing queries.

**Verification finding:** The existing `dashboard.md` is already comprehensive (251 lines, 14 Dataview queries). It does NOT need a rebuild. Three targeted fixes:

1. **Naming:** Change "Career Ops Pipeline" / "Career Ops Dashboard" → "Dossier Pipeline" / "Dossier Dashboard". Fix line 8 reference to "Career Ops/" → "Dossier/".

2. **Source-of-truth statement (line 10):** Replace "Notion tracker owns structured pipeline state. This dashboard mirrors it locally" with "The vault (eval frontmatter) owns all pipeline state. This dashboard provides live views via Dataview queries."

3. **Add Offers Pending query** — the only missing view from the vault-first spec. Insert after the Interviewing section:
   ```dataview
   TABLE WITHOUT ID
     file.link AS "Eval",
     grade AS "Grade",
     compensation AS "Comp",
     date AS "Date"
   FROM "evals"
   WHERE type = "eval" AND status = "Offer"
   SORT date DESC
   ```

4. **Future-proof:** After Stream C.3 ships (outcome tracking), add `outcome` column to the Active Pipeline and Applied Follow-up queries. Not needed now — Dataview gracefully ignores missing fields.

**Acceptance:** Dashboard says "Dossier" not "Career Ops." Source-of-truth statement is vault-first. Offers Pending query exists.

---

## A.12 — Update Config.md Template and README.md

**What:** Align config.md with the new structure. Update README.md's source-of-truth section.

**Config.md changes:**
- Rename header to "Dossier — Configuration"
- Restructure Notion keys under `notion:` block with `enabled:` flag
- Add placeholder sections for new keys coming in Stream C (privacy, scoring)

**README.md changes:**
- Replace any "Notion tracker owns structured pipeline state" language
- Add: "The Obsidian vault is the single source of truth for all pipeline data"

**Acceptance:** Config and README reflect vault-first architecture.

---

## A.13 — Repack and Verify

**What:** Repackage `dossier.skill` and run smoke tests.

**Steps:**
1. Repack: `cd /tmp/skill-edit && zip -r dossier.skill SKILL.md scoring-guide.md`
2. Copy to Dossier folder, replacing the working copy
3. Smoke test: Run a Mode 1 evaluation with a real JD
4. Smoke test: Invoke Mode 9 status sync (with Notion enabled)
5. Smoke test: Invoke Mode 9 status sync concept without Notion (set `enabled: false`)
6. Regression check: Confirm Mode 2 (job search), Mode 3 (prep), Mode 5 (outreach) still work

**Acceptance:** All smoke tests pass. No references to Notion as a data source remain outside the optional mirror sections.

---

## Estimated Breakdown

| Task | Hours |
|------|-------|
| A.1 Backup and extract | 0.1 |
| A.2 Frontmatter description update | 0.1 |
| A.3 Config naming fix | 0.1 |
| A.4 Pipeline Tracker rewrite | 1.0 |
| A.5 Mode 1 dedup rewrite | 0.5 |
| A.6 Mode 1 post-eval update | 0.5 |
| A.7 Mode 9 status sync + recruiter triage rewrite | 1.2 |
| A.8 Mode 9 follow-up rewrite | 0.5 |
| A.9 Mode 10 reference updates | 0.5 |
| A.10 General principles update | 0.1 |
| A.11 Pipeline state reading section | 0.5 |
| A.12 Dashboard.md update | 0.3 |
| A.13 Config + README update | 0.5 |
| A.14 Repack and verify | 0.5 |
| **Total** | **~6.4** |
