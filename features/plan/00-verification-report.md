# Pre-Implementation Verification Report

**Date:** 2026-04-15
**Purpose:** Verify the implementation plan against actual file contents before starting work.

---

## 1. Notion Reference Map — Complete

Every Notion reference in SKILL.md, with actual line numbers (from extracted file):

| # | Line(s) | Location | Content | Plan Coverage |
|---|---------|----------|---------|---------------|
| 1 | 5 | Frontmatter `description` | "logged to Notion" | **MISSED.** Not in vault-first spec or plan. Must update. |
| 2 | 19–56 | `## Notion Tracker` section | Full Notion config + write instructions | [[01-architecture#A.3]] ✓ |
| 3 | 66–67 | Setup section, config.md bullet | "Notion tracker IDs" | [[01-architecture#A.3]] ✓ |
| 4 | 73 | Setup section, missing config handling | "do not attempt any Notion writes or reads" | [[01-architecture#A.3]] ✓ |
| 5 | 227–231 | Mode 1, dedup check | `notion-search`, `notion-fetch`, `notion-update-page` | [[01-architecture#A.4]] ✓ |
| 6 | 235 | Mode 1, post-eval step 2 | "log the result to Notion" | [[01-architecture#A.5]] ✓ |
| 7 | 572 | Mode 9, intro paragraph | "the Notion tracker goes stale" | **MISSED.** Flavor text but should be reworded. |
| 8 | 577 | Mode 9, Recruiter Triage step 3 | "Cross-reference against Notion" | **MISSED.** Not in vault-first spec. Must rewrite to check local evals. |
| 9 | 583–587 | Mode 9, Application Status Sync | "Pull from Notion", "Propose Notion status updates", `notion-update-page` | [[01-architecture#A.6]] ✓ |
| 10 | 589 | Mode 9, Follow-up Engine | "Query Notion for rows in Applied status" | [[01-architecture#A.7]] ✓ |
| 11 | 613 | Mode 9, Operating Principles | "Always check Notion before drafting a follow-up" | Vault-first spec §2.7 ✓ |
| 12 | 630–633 | Mode 10, Follow-up Reminders | "logged to Notion", "Notion tracker link" | [[01-architecture#A.8]] ✓ |
| 13 | 641 | Mode 10, Weekly Pipeline Review | "points to the Notion tracker" | [[01-architecture#A.8]] ✓ |
| 14 | 644 | Mode 10, Interview Roster | "company names from Notion" | [[01-architecture#A.8]] ✓ |
| 15 | 659 | General Principles | "Always log evaluations to Notion" | [[01-architecture#A.9]] ✓ |

### Findings

**14 of 15 references are covered by the plan. Three were missed:**

1. **Line 5 (frontmatter description):** The skill's trigger description says "A–F grade + structured report logged to Notion." After vault-first, this should read "A–F grade + structured report saved to vault." This affects skill triggering behavior — test after changing.

2. **Line 572 (Mode 9 intro):** "Without inbox integration, the Notion tracker goes stale" — reword to "Without inbox integration, the pipeline goes stale and follow-ups fall through the cracks."

3. **Line 577 (Mode 9 Recruiter Triage step 3):** "Cross-reference against Notion — does this company/role already have a row?" — rewrite to "Cross-reference against `evals/` — does this company already have an evaluation file?"

**→ AMENDMENT: Add these three items to [[01-architecture]] as sub-tasks of existing items.**

---

## 2. Line Number Verification — Vault-First Spec vs. Reality

The vault-first spec was written against a different line-numbering than the actual extracted SKILL.md. The *content* matches, but line numbers are systematically offset.

| Vault-First Spec Says | Actual Line(s) | Delta | Content Match? |
|----------------------|-----------------|-------|----------------|
| Lines 22–52 | Lines 19–56 | −3 to +4 | ✓ Yes |
| Lines 54–67 | Lines 58–73 | +4 to +6 | ✓ Yes |
| Lines 249–254 | Lines 227–231 | −22 to −23 | ✓ Yes |
| Lines 256–262 | Lines 233–239 | −23 | ✓ Yes |
| Lines 658–662 | Lines 583–587 | −75 | ✓ Yes |
| Lines 664–671 | Lines 589–596 | −75 | ✓ Yes |
| Line 690 | Line 613 | −77 | ✓ Yes |
| Lines 712–715 | Lines 630–633 | −82 | ✓ Yes |
| Lines 721–724 | Lines 641–641 | −80 | ✓ Yes |
| Lines 726–729 | Lines 644–644 | −82 | ✓ Yes |
| Line 751 | Line 659 | −92 | ✓ Yes |

**Conclusion:** All content matches. The line-number delta grows as you go deeper into the file (from −3 at the top to −92 at the bottom), suggesting the spec was written against a version with more whitespace or formatting. **This is not a problem for implementation** — we'll work from content, not line numbers.

---

## 3. Scoring Guide — No Changes Needed

`scoring-guide.md` (124 lines) is a pure reference document. It defines score meanings (1–5) for each of the 10 dimensions and the grade conversion table.

**Findings:**
- No Notion references
- No config dependencies
- No behavioral logic — purely informational
- The gate-pass rule (Dim 1 or 2 ≤ 2 → cap at D) is documented here and echoed in SKILL.md line 211. Consistent.

**Impact on plan:** None. This file survives all streams unchanged. If scoring weight personalization ([[05-advanced#E.3]]) changes default weights, consider adding a note here, but the guide is about *score meaning*, not *weight values*.

---

## 4. Dashboard.md — Three Issues Found

The current `dashboard.md` (251 lines, last rebuilt 2026-04-14) is comprehensive with 14 Dataview queries. However:

### Issue 1: Naming inconsistency
- Line 4: `title: Career Ops Pipeline` → should be `Dossier Pipeline`
- Line 8: "subfolders under `Career Ops/`" → should be `Dossier/`
- Line 6: `# Career Ops Dashboard` → should be `# Dossier Dashboard`

### Issue 2: Source-of-truth statement contradicts vault-first
- Line 10: "**Source of truth:** Notion tracker owns structured pipeline state. This dashboard mirrors it locally"
- **This is the exact opposite of vault-first.** Must be rewritten to: "**Source of truth:** The vault (eval frontmatter) owns all pipeline state. This dashboard provides live views via Dataview queries."

### Issue 3: Missing queries from vault-first spec
The current dashboard has: Today's Activity, This Week, Active Pipeline, Top Priority, Outreach Drafted/Sent, Applied Follow-up, Interviewing, Grade Distribution, Status Distribution, Daily Activity, Weekly Digests, Research, Archive, Quick-Action Checklist.

The vault-first spec proposes: Active Pipeline, Follow-ups Due, Interviews Coming Up, Offers Pending, Recent Evaluations, Grade Distribution, Outreach Pending.

**Overlap is strong.** The current dashboard already covers most of what the spec proposes, and actually has *more* views. The only additions needed:
- **Offers Pending** query (not in current dashboard)
- **Outcome** field in queries once [[03-foundation#C.3]] ships

**→ AMENDMENT: Stream A.11 (dashboard update) is simpler than expected. Focus on fixing naming, source-of-truth statement, and adding the Offers Pending query. Don't rebuild from scratch — the existing dashboard is good.**

---

## 5. Existing Eval Frontmatter — Schema Analysis

All 11 evals have identical field sets:

```yaml
type: eval
company: "..."
role: "..."
grade: A | B+ | B | C
score: 3.7–4.5
status: Evaluating         # All 11 are "Evaluating" — none have progressed
date: 2026-04-14           # All from the same day
location: "..."
compensation: "..."
notes: "..."
```

### What's missing (planned additions):
- `outcome:` — not present. All are "Evaluating" status, so `outcome: Pending` is correct for all.
- `legitimacy:` — not present. Would need re-evaluation to assign honestly.
- `model:` — not present. These were all generated by the current model.
- `sources:` — not present.

### Backfill recommendation:
- **Backfill `outcome: Pending`** on all 11. It's always correct for evals that haven't progressed past Evaluating. Takes 5 minutes. **Do this during Stream C.3.**
- **Do NOT backfill `legitimacy`** — we'd need to re-evaluate each JD. Leave it absent; Dataview handles missing fields gracefully.
- **Do NOT backfill `model` or `sources`** — these are optional provenance fields, not required for queries.

### Naming convention conflict:
SKILL.md line 172: "One file per artifact per company per day. If you re-evaluate the same day, **update the existing file in place** rather than creating a second."

This directly contradicts [[04-competitive#D.3|eval versioning]]. **Stream D.3 must rewrite this line** to support versioned re-evaluations. Already in the plan, but worth noting: this is a *convention change*, not just a mode change. It affects how the skill behaves across all modes that create files.

---

## 6. Design Decision Review

With the full SKILL.md now read, I'm revisiting three design choices in the plan:

### 6a. Mode 9 Recruiter Triage — Notion cross-reference is load-bearing

Line 577: "Cross-reference against Notion — does this company/role already have a row? Flag matches."

This is more important than the vault-first spec acknowledged. When triaging recruiter emails, knowing "you already evaluated this company" is critical context. The vault-first replacement must scan `evals/` for a matching company slug and surface the existing grade/status. This isn't just a find-and-replace of "Notion" → "evals/" — the triage output should include a direct wikilink to the eval file.

**→ AMENDMENT: Add explicit note to A.6 that Recruiter Triage (not just Status Sync) needs vault-first rewrite. The output should show `[[eval-company-slug-date]] — Grade B, status: Applied` for any company that has an existing eval.**

### 6b. Mode 10 references are lighter than expected

Mode 10's Notion references (lines 630, 633, 641, 644) are mostly in event descriptions — "the Notion tracker link" appears in calendar event text. These are simple string replacements: swap the Notion URL for a reference to `dashboard.md` or the eval file path. No behavioral logic changes needed.

**→ No amendment needed.** Stream A.8 already covers this correctly.

### 6c. The "B+" grade is used but not in the grade conversion table

SKILL.md line 103 defines grades as A, B, C, D, F. But the eval frontmatter schema (line 103) allows `B+`, and existing evals use it (Company A, Company B, Company C all have `grade: B+`). The scoring guide also doesn't mention B+.

This isn't a vault-first issue, but it's a consistency gap. B+ falls within the B range (3.75–4.49) but scores at the high end (4.2–4.3). The dashboard's "Top Priority" query explicitly filters for `grade = "A" OR grade = "B+"`.

**→ This is a pre-existing inconsistency, not introduced by our plan. Note it but don't fix it in Stream A — it's a separate calibration issue. Add to [[07-risks]] as an observation.**

---

## 7. Summary of Plan Amendments

| # | Amendment | Affects | Severity |
|---|-----------|---------|----------|
| 1 | Add frontmatter description update (line 5) to Stream A | [[01-architecture]] | Medium — affects skill triggering |
| 2 | Add Mode 9 intro line reword (line 572) to Stream A.6 | [[01-architecture]] | Low — flavor text |
| 3 | Add Mode 9 Recruiter Triage rewrite (line 577) to Stream A.6 | [[01-architecture]] | **High — load-bearing cross-reference** |
| 4 | Simplify A.11 (dashboard update) — existing dashboard is mostly good | [[01-architecture]] | Low — reduces work |
| 5 | Backfill `outcome: Pending` on 11 existing evals during C.3 | [[03-foundation]] | Low — 5 minutes |
| 6 | Note B+ grade inconsistency in risks | [[07-risks]] | Low — pre-existing |

**None of these amendments change the stream ordering or estimates significantly.** Amendment #3 is the most important — it adds a task within A.6 that was missing, but the effort is small (one paragraph rewrite).

---

## 8. Verification Verdict

**The plan is sound. The architecture is correct. The sequencing is right.**

The three missed Notion references (#1, #7, #8 above) are real gaps but small ones — they're additional sub-tasks within work items that already exist. No new streams, no reordering, no blocked dependencies.

The line-number offsets are cosmetic — all content matches. The scoring guide needs no changes. The dashboard needs minor fixes, not a rebuild. The existing eval frontmatter is consistent and clean.

**Ready to implement.**
