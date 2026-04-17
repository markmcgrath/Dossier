---
type: dashboard
title: Dossier Pipeline
---

# Dossier Dashboard

Live pipeline view powered by Dataview. Requires the Dataview community plugin in Obsidian. All queries read frontmatter from the subfolders under `Dossier/`.

> **Source of truth:** The vault (eval frontmatter) owns all pipeline state. This dashboard provides live views via Dataview queries.

---

## Today's Activity

Everything with today's date, across all artifact types. Useful for "what did I do today" review.

```dataview
TABLE WITHOUT ID
  file.link AS "File",
  type AS "Type",
  company AS "Company"
FROM "evals" OR "outreach" OR "cover-letters" OR "interview-prep" OR "daily" OR "weekly" OR "research"
WHERE date = date(today)
SORT type ASC, file.name ASC
```

## This Week — Last 7 Days

All artifacts dated within the last week. The natural "what's moving" view.

```dataview
TABLE WITHOUT ID
  file.link AS "File",
  type AS "Type",
  company AS "Company",
  date AS "Date"
FROM "evals" OR "outreach" OR "cover-letters" OR "interview-prep" OR "daily" OR "weekly" OR "research"
WHERE date >= date(today) - dur(7 days)
SORT date DESC, type ASC
```

---

## Active Pipeline — Ranked by Score

Everything not yet in a terminal state, sorted strongest fit first. Click a company to open its eval.

```dataview
TABLE WITHOUT ID
  file.link AS "Eval",
  grade AS "Grade",
  legitimacy AS "Legitimacy",
  score AS "Score",
  status AS "Status",
  compensation AS "Comp",
  location AS "Location"
FROM "evals"
WHERE type = "eval" AND status != "Rejected" AND status != "Passed" AND status != "Offer-Declined"
SORT score DESC
```

---

## Top Priority — Grade A & B+

The rows that deserve attention first. If a row here has `status: Evaluating` for more than 5 days, something is stuck — either apply or explicitly pass.

```dataview
TABLE WITHOUT ID
  file.link AS "Eval",
  grade AS "Grade",
  legitimacy AS "Legitimacy",
  score AS "Score",
  status AS "Status",
  notes AS "Read"
FROM "evals"
WHERE type = "eval" AND (grade = "A" OR grade = "B+") AND status != "Rejected" AND status != "Passed"
SORT score DESC
```

---

## Outreach — Drafted But Not Sent

Files in `outreach/` where `status: drafted`. These are the easy unlocks — a draft sitting in the folder is a decision not yet made.

```dataview
TABLE WITHOUT ID
  file.link AS "Outreach",
  company AS "Company",
  channel AS "Channel",
  date AS "Drafted"
FROM "outreach"
WHERE type = "outreach" AND status = "drafted"
SORT date DESC
```

---

## Outreach — Sent, Awaiting Reply

Once you flip a draft's frontmatter to `status: sent`, it shows up here. If anything sits >10 days without a reply, that's a nudge candidate.

```dataview
TABLE WITHOUT ID
  file.link AS "Outreach",
  company AS "Company",
  channel AS "Channel",
  date AS "Sent"
FROM "outreach"
WHERE type = "outreach" AND status = "sent"
SORT date DESC
```

---

## Applied — Follow-up Watch

Evals flipped to `status: Applied`. The skill's Mode 10 logic recommends a day-7 follow-up; this table lets you eyeball which are due.

```dataview
TABLE WITHOUT ID
  file.link AS "Eval",
  grade AS "Grade",
  date AS "Applied Date",
  (date(today) - date(date)).days AS "Days Since"
FROM "evals"
WHERE type = "eval" AND status = "Applied"
SORT date ASC
```

---

## Interviewing

```dataview
TABLE WITHOUT ID
  file.link AS "Eval",
  grade AS "Grade",
  legitimacy AS "Legitimacy",
  score AS "Score",
  notes AS "Notes"
FROM "evals"
WHERE type = "eval" AND status = "Interviewing"
SORT score DESC
```

Related prep docs:

```dataview
LIST
FROM "interview-prep"
WHERE type = "prep"
SORT file.name DESC
```

---

## Offers Pending

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

---

## Pipeline by Grade — Count

```dataview
TABLE WITHOUT ID
  grade AS "Grade",
  length(rows) AS "Count"
FROM "evals"
WHERE type = "eval" AND status != "Rejected" AND status != "Passed"
GROUP BY grade
SORT grade ASC
```

---

## Pipeline by Status — Count

```dataview
TABLE WITHOUT ID
  status AS "Status",
  length(rows) AS "Count"
FROM "evals"
WHERE type = "eval"
GROUP BY status
```

---

## Recent Daily Activity

Last 7 daily scans and lead pulses, newest first.

```dataview
LIST
FROM "daily"
SORT file.name DESC
LIMIT 14
```

---

## Recent Weekly Digests

```dataview
LIST
FROM "weekly"
SORT file.name DESC
LIMIT 8
```

---

## Research / Target Briefs

```dataview
LIST
FROM "research"
SORT file.name DESC
```

---

## Archive (Terminal Rows)

Rows that have reached a terminal state and been moved to `archive/[company-slug]/`. Searchable but out of the active pipeline.

```dataview
LIST
FROM "archive"
SORT file.name DESC
LIMIT 25
```

---

## Canonical Reference Docs

- [[cv]] — work history, capability fit
- [[profile]] — target archetype, desirability fit
- [[README]] — folder conventions

---

## Quick-Action Checklist

- [ ] Any **drafted** outreach older than today? Send or delete.
- [ ] Any **Applied** row past 7 days with no interview scheduled? Follow up.
- [ ] Any **Interviewing** row without a prep doc in `interview-prep/`? Build one.
- [ ] Any `Evaluating` row older than 5 days? Decide: apply or pass.
- [ ] Any Rejected/Passed row still in `evals/`? Move bundle to `archive/`.
