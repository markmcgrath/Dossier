---
type: plan
feature: recruiter-inbox-pulse-broadening
status: shipped
created: 2026-04-19
author: claude
tags: [lead-pulse, scheduled-task, gmail, inbox, recruiter-signals]
related: "[[lead-pulse-dedup-v2]]"
---

# Plan: Recruiter Inbox Pulse — Broadening Beyond LinkedIn

## Problem

The `linkedin-pulse` scheduled task is named accurately: it is optimized primarily for LinkedIn InMail signals. Its five Gmail search queries leave several real recruiter signal categories uncovered:

| Signal type | Covered? | Why not |
|---|---|---|
| LinkedIn InMail notifications | ✓ | Queries 1 & 2 |
| LinkedIn job alert emails | ✓ | Query 3 (with profile filter) |
| Self-forwarded leads | ✓ | Query 4 |
| Cold recruiter email (keyword-matched) | Partial | Query 5 — but keyword set is narrow and job board domains are excluded |
| Indeed / Dice recruiter outreach | ✗ | Explicitly excluded from Query 5 |
| Indeed / Dice job alert emails | ✗ | Not queried |
| Google job alert emails | ✗ | Not queried |
| Application status emails (confirmations, rejections, interview invites) | ✗ | Keyword set doesn't cover these |
| Recruiter cold email without trigger keywords | ✗ | "I wanted to connect about a position" would be missed |

The result is a pulse that reliably catches LinkedIn inbound but misses a meaningful slice of the broader recruiter inbox.

---

## Proposed Solution

Broaden the pulse into a **general recruiter inbox scan** by expanding the Gmail query set and adding a new signal category for application status emails. The task can retain its current name or be renamed to `recruiter-inbox-pulse` to reflect the broader scope — the latter is preferred for clarity.

The changes are additive: existing queries are preserved and extended, not replaced.

---

## New and Modified Queries

### Query 1–2 (unchanged)
LinkedIn InMail notifications and reply threads. Keep as-is.

### Query 3 (extended)
Current: `from:jobalerts-noreply@linkedin.com newer_than:3h`

Add parallel queries:
- `from:jobalerts@indeed.com newer_than:3h` — Indeed job alerts
- `from:dice.com newer_than:3h` — Dice job alerts
- `from:jobs-noreply@google.com newer_than:3h` — Google job alerts

Apply the same profile-filter logic already used for LinkedIn alerts: only flag as ✓ MATCH if the role title aligns with target archetypes. Skip silently if clearly off-archetype.

### Query 4 (unchanged)
Self-forwards from the user's own Gmail address. Keep as-is.

### Query 5 (broadened)
Current: `newer_than:3h (recruiter OR "reaching out" OR "opportunity" OR "interested in your background") -from:linkedin.com -from:indeed.com -from:dice.com`

Issues:
- Excludes Indeed and Dice domains, so recruiter messages routed through those platforms are missed.
- Keyword set is narrow — misses polite outreach that doesn't use those exact phrases.

Proposed replacement:
```
newer_than:3h (
  recruiter OR "reaching out" OR "opportunity" OR "interested in your background"
  OR "came across your profile" OR "your experience" OR "wanted to connect"
  OR "open to" OR "considering new" OR "exploring opportunities"
) -from:noreply@linkedin.com -from:messages-noreply@linkedin.com
  -from:inmail-hit-reply@linkedin.com -from:jobalerts-noreply@linkedin.com
```

Changes:
- **Remove the blanket Indeed/Dice domain exclusion.** Replace with exclusions of specific LinkedIn no-reply addresses only (to avoid double-counting queries 1–3), so recruiter messages from Indeed/Dice platforms pass through.
- **Expand keyword set** to catch softer outreach language.

### Query 6 (new) — Application status signals
```
newer_than:3h (
  "your application" OR "application received" OR "application status"
  OR "interview" OR "next steps" OR "move forward" OR "unfortunately"
  OR "we've decided" OR "position has been filled"
) -from:noreply@linkedin.com -from:jobalerts-noreply@linkedin.com
```

This catches: application confirmations, interview invitations, rejection emails, and "next steps" follow-ups. These are not recruiter outreach leads — they are **pipeline status signals** and should be classified and reported differently (see Output Changes below).

---

## Signal Classification Update

The current output uses three categories: ✓ MATCH, ? UNCLEAR, ✗ SKIP. Add a fourth:

**📋 STATUS UPDATE** — for signals from Query 6 that represent application status changes rather than new inbound leads. These get a separate section in the leads file and a different suggested action (e.g., "Update eval frontmatter status" rather than "Evaluate JD / Reply to engage").

Output format for status updates:
```
### 📋 [Company] — [Status Signal Type]
- Source: Application status email
- Signal: [1 sentence — what the email says]
- In pipeline: [Yes — current status: X / No — consider creating eval]
- Suggested action: [Update status to X / Archive / No action needed]
```

---

## Output Changes

### Leads file header
Update the summary line to reflect the new category:

```
## New Signals ([N] total — [N] match, [N] unclear, [N] status updates, [N] skipped)
```

### Separate sections
```
## New Leads
### ✓ ...
### ? ...

## Application Status Updates
### 📋 ...

## Skipped (off-archetype or noise)
```

---

## Task Rename

Rename `linkedin-pulse` → `recruiter-inbox-pulse` (or keep existing name with a scope note in the task definition header). The output file naming convention can stay as `daily/leads-[date]-[time].md` since these are still "lead signals" in the broad sense — or introduce `daily/inbox-pulse-[date]-[time].md` if the distinction from prior files matters for Dataview queries.

**Recommendation:** Keep `leads-*.md` naming for continuity. Update Dataview queries in `dashboard.md` only if new signal types need separate views.

---

## Interaction with Dedup Plan

The dedup v2 plan (`lead-pulse-dedup-v2.md`) adds fingerprint suppression to the state file. That logic applies cleanly to the broadened query set — fingerprinting works on any recruiter signal regardless of source. Implement dedup v2 first, then apply this broadening on top. Doing it the other way around would require revisiting the fingerprint extraction logic for non-LinkedIn email formats.

**Fingerprint extraction note for non-LinkedIn sources:**
- **Cold email / Indeed / Dice outreach:** sender email address is reliable and specific — use it directly as the recruiter key (no LinkedIn slug fallback needed).
- **Application status emails (Query 6):** these are classified as STATUS UPDATE, not leads — fingerprinting is not needed. Dedup for status emails is handled by thread ID alone.

---

## Files to Change

1. **Scheduled task definition** — update the five existing queries and add Query 6; add STATUS UPDATE classification logic; update output template.
2. **`dashboard.md`** — assess whether any Dataview queries need updating to handle the new signal type in leads files. Likely no change needed if file naming stays the same.
3. **Open-source propagation** — not applicable (task definition is user-specific).

---

## Implementation Order

1. Complete and validate `lead-pulse-dedup-v2` first.
2. Implement this broadening as a follow-on update.
3. After first broadened run, verify Query 6 (status signals) is not generating false positives (marketing emails from job boards that happen to contain "your application").

---

## Open Questions

- **Query 6 false positive risk:** "your application" and "interview" are high-recall but potentially noisy. A job board marketing email ("Complete your application for these 10 jobs!") could match. May need a `-from:jobalerts` style exclusion list tuned after the first few runs.
- **Indeed / Dice recruiter message format:** messages routed through those platforms may arrive as notifications (with a platform-specific from address) rather than direct recruiter emails. The domain-inclusion change in Query 5 should catch them, but this needs verification against a real example.
- **Leads file naming:** `leads-*.md` vs. `inbox-pulse-*.md` — decide before implementation to avoid mixed naming in `daily/`.
