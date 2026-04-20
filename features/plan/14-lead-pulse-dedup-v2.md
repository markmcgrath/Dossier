---
type: plan
feature: lead-pulse-dedup-v2
status: draft
created: 2026-04-19
author: claude
tags: [lead-pulse, scheduled-task, dedup, state-management]
---

# Plan: Lead Pulse Dedup v2 — Recruiter + Role Fingerprinting

## Problem

The current `linkedin-pulse` scheduled task deduplicates incoming recruiter signals using **Gmail thread IDs** stored in `.lead-pulse-state.json`. This handles the most common case (same thread re-appearing across runs) correctly.

It does not handle:

1. **Same recruiter, new follow-up thread.** If a recruiter sends a second InMail about the same role, it generates a new Gmail thread ID and surfaces as a fresh lead.
2. **Same company, different recruiter.** Two recruiters at the same agency reaching out about identical roles appear as distinct leads.
3. **No cross-check against prior leads files.** If a lead from a previous session was already logged to `daily/leads-*.md`, the pulse has no memory of that — only of thread IDs from the last 200 threads it has seen.

In all three cases, the result is duplicate entries in `daily/leads-*.md` files, which degrades the signal-to-noise ratio and creates extra triage work.

---

## Proposed Solution

Extend `.lead-pulse-state.json` to track a **lead fingerprint** alongside each thread ID. The fingerprint is a normalized string derived from two fields present in virtually all recruiter InMails:

- **Sender email or LinkedIn profile URL** (recruiter identity)
- **Normalized role title** (what they're recruiting for)

A fingerprint match suppresses the lead even if the thread ID is new.

---

## State File Schema Change

### Current schema

```json
{
  "seen_thread_ids": ["abc123", "def456"],
  "last_updated": "2026-04-19T20:00:00-05:00"
}
```

### Proposed schema

```json
{
  "seen_thread_ids": ["abc123", "def456"],
  "seen_fingerprints": [
    {
      "fingerprint": "[recruiter-key]|analytics-engineer",
      "thread_id": "[thread-id-1]",
      "first_seen": "YYYY-MM-DDTHH:MM:SS-05:00",
      "company_hint": "[Company (unnamed)]"
    }
  ],
  "last_updated": "YYYY-MM-DDTHH:MM:SS-05:00"
}
```

**Retention:** `seen_thread_ids` stays capped at 200. `seen_fingerprints` is capped at 200 entries as well, trimmed oldest-first when the limit is reached.

---

## Fingerprint Construction

The fingerprint is built as: `{recruiter_key}|{role_key}`

### Recruiter key

Priority order (use the first available):

1. **Sender email address** — normalized to lowercase, whitespace stripped. For LinkedIn InMails forwarded via Gmail, the `From:` header is `inmail-hit-reply@linkedin.com`, which is not recruiter-specific. In this case, fall through to (2).
2. **LinkedIn profile URL slug** — extracted from the InMail body (links like `linkedin.com/comm/in/[recruiter-slug]` → `[recruiter-slug]`). Normalize to lowercase.
3. **Recruiter name** — extracted from the message signature, normalized: lowercase, spaces replaced with hyphens, punctuation stripped. Use only as last resort.

### Role key

1. Extract the role title from: subject line, message body header, or "Must Haves" section heading.
2. Normalize: lowercase, remove stop words (`a`, `an`, `the`, `senior`, `lead`, `remote`, `opening`, `opportunity`, `role`), replace spaces with hyphens, strip punctuation.
3. Truncate to first 4 significant tokens.

**Examples:**

| Raw title | Normalized role key |
|---|---|
| "Remote Analytics Engineer Opening" | `analytics-engineer` |
| "Senior Lead Analytics Engineer — Healthcare" | `analytics-engineer-healthcare` |
| "Analytics Engineering Opportunity" | `analytics-engineering` |
| "BI Platform Architect (Remote, Direct Hire)" | `bi-platform-architect` |

**Fuzzy match rule:** If a new role key shares 3 of 4 tokens with a fingerprint already in `seen_fingerprints`, treat it as a match and suppress. This handles minor title variations from the same recruiter.

---

## Suppression Logic

When processing a new thread:

1. Build the candidate fingerprint.
2. Check `seen_fingerprints` for an exact or fuzzy match (per fuzzy rule above).
3. If match found → suppress silently. Do not add to the leads file. **Do** add the new thread ID to `seen_thread_ids` so it won't re-appear in thread-ID dedup either.
4. If no match → process normally. Add both the thread ID and the new fingerprint entry to the state file.

**Grace period:** If the fingerprint match is older than **21 days** (`first_seen`), do not suppress — re-surface the lead. Recruiters genuinely follow up on stale outreach, and a 3-week gap likely means a new position or a genuine retry worth reviewing. When re-surfacing, note in the leads file: *"Previously seen [date] — re-surfacing after 21-day grace period."*

---

## Leads File Output Change

When a lead is suppressed by fingerprint (but not thread ID — meaning the thread ID is new), log a count of suppressed leads at the bottom of the leads file if at least one non-suppressed lead exists:

```markdown
## Suppressed (fingerprint duplicates)
1 lead suppressed as a duplicate of a prior signal (same recruiter/role seen previously).
```

If all leads are suppressed: still exit silently (no file written), consistent with the current behavior for all-SKIP runs.

---

## Files to Change

### 1. Scheduled task definition

The `linkedin-pulse` task file controls the pulse behavior. The relevant changes are:

- **Step 3 (Deduplicate):** Extend to check both `seen_thread_ids` AND `seen_fingerprints` with the fuzzy match rule and 21-day grace period.
- **Step 5 (Extract data per thread):** Add extraction of recruiter key (email → LinkedIn slug → name fallback) and role key from subject/body.
- **Step 8 (Write leads file):** Add the suppressed-count footer block when applicable.
- **Step 9 (Update state file):** Write back the new `seen_fingerprints` array alongside `seen_thread_ids`, capped at 200 each.

The task file lives at the path referenced in the scheduled task configuration. Its current content is the task definition prose — changes are made to that prose directly.

### 2. `.lead-pulse-state.json`

Schema migration: on first run after the update, if `seen_fingerprints` is absent from the file, initialize it as an empty array. No data loss; existing `seen_thread_ids` are preserved.

### 3. `open-source/` propagation

The scheduled task definition is not part of the open-source vault (it contains user-specific configuration). No open-source propagation needed for this change.

---

## What This Does Not Fix

- **Same company, different recruiter for a genuinely different role.** This is correct behavior — that is a new lead and should surface. The role key component of the fingerprint ensures these are treated distinctly.
- **Cross-leads-file historical check.** The `seen_fingerprints` list acts as this memory, bounded by the 200-entry cap and the 21-day grace period. A full scan of `daily/leads-*.md` on every run would be expensive and is not warranted given the rolling state file approach.
- **Notion dedup.** The pulse is read-only on Notion (and read-only on all write channels). Pipeline cross-check remains informational only, as designed.

---

## Implementation Steps

1. Update the `linkedin-pulse` task definition prose to reflect the new Step 3, Step 5, Step 8, and Step 9 logic (as described above).
2. On next pulse run, the state file will self-migrate (empty `seen_fingerprints` initialized automatically).
3. Manually backfill any leads already logged since the last pulse run into `seen_fingerprints`, so the first post-update run doesn't re-surface them.

---

## Open Questions

- **Fuzzy match threshold (3 of 4 tokens):** this is a judgment call. Too tight and title variations slip through; too loose and genuinely different roles get suppressed. Revisit after 2–3 weeks of pulse data.
- **Grace period (21 days):** chosen to cover typical recruiter follow-up cadence (1–2 weeks) while still re-surfacing stale roles. Adjust if false negatives surface in practice.
- **Recruiter key priority order:** LinkedIn profile slug is preferred over name because names can be ambiguous (two recruiters with the same name at different firms). If the slug extraction proves fragile, fall back to name and note in the pulse output.
