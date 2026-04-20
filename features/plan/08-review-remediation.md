# Review Remediation Plan

**Source:** `features/plan/review-report.md`
**Target file:** `skill-update/SKILL.md` (1,374 lines — restored from `dossier.skill`)
**Scope:** All 13 issues from the review report, triaged against restored full file

---

## Background: File Sync Issue (Resolved)

The review report was written against the 1,374-line SKILL.md packed inside `dossier.skill`. However, `skill-update/SKILL.md` was a stale 764-line draft that predated Streams C–F. This meant nearly half the features the review referenced didn't exist in the editable file.

**Fix applied:** Extracted the full 1,374-line SKILL.md from `dossier.skill`, stripped null bytes, and replaced the stale editable copy. The old 764-line version is preserved as `SKILL.md.bak-764-stale`. The `scoring-guide.md` was also extracted and cleaned.

All line numbers below reference the restored 1,374-line file.

---

## Triage Against Restored File

| # | Issue | Severity | Status | Action |
|---|-------|----------|--------|--------|
| 1 | Dashboard missing legitimacy column | Critical | **RESOLVED** | `dashboard.md` lines 53, 73, 141 already include `legitimacy AS "Legitimacy"` |
| 2 | Calendar reminder references filename | Critical | **RESOLVED** | Line 393 now says "Reference the eval file wikilink (`[[eval-slug-date]]`) in the reminder description." No bare `dashboard.md` filename reference. |
| 3 | Gate-pass rule not clearly separated | Critical | **RESOLVED** | Lines 292–294 are a titled subsection: `### Gate-Pass Rule (Overrides Grade Conversion)` with both dimensions named explicitly. |
| 4 | Mode 9 domain filtering ambiguous | Critical | **RESOLVED** | Lines 956–964 have clear precedence: allow list → strict whitelist, deny list ignored when allow is active. Explicit "deny list is irrelevant when allow list is active" wording. |
| 5 | Example outreach frontmatter | High | **RESOLVED** | Frontmatter matches SKILL.md spec. |
| 6 | Naming convention contradicts versioning | High | **RESOLVED** | Line 228 now says "version the files using a `-v#` suffix rather than overwriting." Matches dedup logic at lines 378–379. |
| 7 | CV Tailoring out of logical order | High | **RESOLVED** | Lines 335–342 show correct order: Red Flags → Interview Probability → Recommendation → CV Tailoring Suggestions. |
| 8 | Mode 0 missing `outcome` validation | High | **RESOLVED** | Line 243 spot-checks for: `type`, `company`, `role`, `grade`, `score`, `status`, `date`, `outcome`. Mode 0 exists at line 230 with all 6 checks. |
| 9 | docx skill invocation not explicit | Medium | **RESOLVED** | Lines 886–909 contain a complete Step 6 for ATS-safe docx export, including docx skill invocation, ATS formatting rules, and keyword match scoring. |
| 10 | Email filtering comment misleading | Medium | **RESOLVED** | Lines 81–85 have a clear header: `# Email Filtering` with subcomment `# (Use to prevent personal email noise during job search — not a privacy control)`. |
| 11 | Dashboard + README missing-fields note | Medium | **UNRESOLVED** | README.md still lacks a note about Dataview queries and incomplete frontmatter. |
| 12 | Mode 7 non-comp levers style | Low | **RESOLVED** | Lines 760–772 include per-lever descriptions with tactical advice. |
| 13 | Mode 2.1 portal scan feasibility | Low | **DEFERRED** | Correctly deferred per `06-deferred.md`. |

**Summary:** 12 of 13 issues are resolved in the restored file. 1 remains.

---

## Remaining Fix

### Issue 11 — Add Dataview completeness note to README.md

**File:** `README.md`
**Location:** After the "Archive discipline" section (after line 188: "Nothing is deleted. Everything remains searchable."), before the "Data retention" section.

**Insert:**

```markdown
---

## Dataview and frontmatter completeness

Dashboard queries filter on frontmatter fields like `status`, `grade`, `legitimacy`, and `outcome`. If an eval file is missing one of these fields, it will silently drop out of filtered views (e.g., `WHERE legitimacy = "Verified"` excludes files without a `legitimacy` field). Run Mode 0 periodically to catch missing fields. All new evals created via Mode 1 include the full field set automatically.
```

**Why:** Users who manually create eval files or import older evals will see rows disappear from filtered dashboard views with no explanation. This note explains the cause and points to Mode 0 as the remedy.

---

## Execution Steps

| Step | File | Action |
|------|------|--------|
| 1 | `README.md` (line 188) | Insert "Dataview and frontmatter completeness" section between "Archive discipline" and "Data retention" |
| 2 | `open-source/README.md` | Copy updated `README.md` to open-source (per CLAUDE.md propagation rules) |
| 3 | `open-source/features/plan/08-review-remediation.md` | Copy this plan file to open-source |
| 4 | Verification | Confirm both README copies have the new section; confirm open-source plan file matches |

**Estimated time:** ~5 minutes.

---

## Already Resolved (No Action)

| # | Issue | How It Was Resolved |
|---|-------|---------------------|
| 1 | Dashboard legitimacy | Already in `dashboard.md` at time of review |
| 2 | Calendar reminder wikilink | Fixed in packed version; line 393 uses eval wikilink |
| 3 | Gate-pass subsection | Fixed in packed version; lines 292–294 are a titled subsection |
| 4 | Domain filtering | Fixed in packed version; lines 956–964 have clear precedence |
| 5 | Example frontmatter | Already correct at time of review |
| 6 | Naming vs. versioning | Fixed in packed version; line 228 references `-v#` suffix |
| 7 | Output template order | Fixed in packed version; CV Tailoring moved to end |
| 8 | Mode 0 + outcome | Fixed in packed version; Mode 0 at line 230, outcome in spot-check |
| 9 | docx skill invocation | Fixed in packed version; lines 886–909 have full ATS export step with docx skill invocation |
| 10 | Email filtering comment | Fixed in packed version; lines 81–85 have clear header |
| 12 | Non-comp levers | Already had per-lever descriptions at time of review |
| 13 | Portal scan | Correctly deferred |

---

## Root Cause

The editable `skill-update/SKILL.md` was not kept in sync with the packed `dossier.skill`. The packed version received all Stream C–F work, but the editable copy was never updated. This created a confusing state where the review report (correctly analyzing the packed version) flagged issues that appeared to be missing features in the editable file.

**Prevention:** After any SKILL.md edit, always repack `dossier.skill` AND update `skill-update/SKILL.md` in the same pass. The two must stay identical. Consider treating `skill-update/SKILL.md` as the source of truth and repacking from it, rather than the other direction.
