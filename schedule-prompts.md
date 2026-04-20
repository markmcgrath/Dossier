# Scheduled Task Templates

These are prompt templates for Cowork's scheduled tasks feature. Adapt them to your own profile, target roles, and schedule. Replace all bracketed placeholders with your own values before use.

---

## Daily Job Scan

**Frequency:** Daily, morning (suggested: 6–9 AM)
**Purpose:** Search Indeed and Dice for new listings matching your target roles, evaluate grade-B-or-better results, and check for stale applications that need follow-up.

**Prompt template:**

> You are running the daily Dossier job scan. **Step 0: Read `Dossier/config.md`** and check whether `notion.enabled` is `true` or `false`. This determines your data source for pipeline state throughout this task. **Step 1: Invoke the `dossier` skill** to load the full playbook. Also read `Dossier/cv.md` and `Dossier/profile.md` silently for context. **Step 2: Run Mode 2 (Job Search)** against the target roles listed in `profile.md` (remote-preferred, US-based). Use Indeed `search_jobs` and Dice `search_jobs` in parallel. Filter out listings already in the pipeline: if Notion is enabled, query the configured data source; if disabled, scan `Dossier/evals/` for existing `eval-*.md` files and read their YAML frontmatter to build the dedup list. **Step 3: For each new listing, run Mode 1 (Offer Evaluator).** Score with the 10-dimension framework. Apply the "Roles to Avoid" list from `profile.md` as penalties on Dimensions 1 and 10. **Step 4: Log grade B-or-better results.** If Notion is enabled, auto-log as Status="Evaluating" via the Notion connector. If disabled, the eval file saved to `Dossier/evals/` is the record. Skip C/D/F silently. **Step 5: Stale application check.** Find evals with `status: Applied` and `date` older than 7 days. For each, search Gmail for the company domain in the last 14 days. If no recent thread exists, flag for follow-up. **Step 6: Write the daily brief** to `Dossier/daily/daily-scan-[YYYY-MM-DD].md` with sections: New Opportunities Logged, Scanned But Not Logged (counts only), Follow-ups Due, Pipeline Snapshot. Keep it terse — no filler.

---

## Daily Digest

**Frequency:** Daily, mid-morning (suggested: run after the job scan and LinkedIn pulse)
**Purpose:** Short, scannable summary of what happened since yesterday's digest — new evals, recruiter leads, action items, and pipeline snapshot.

**Prompt template:**

> You are generating the daily Dossier morning digest. **Step 0: Read `Dossier/config.md`** and check whether `notion.enabled` is `true` or `false`. **Step 1: Read `Dossier/cv.md` and `Dossier/profile.md` silently.** **Step 2: Gather new activity since yesterday.** Scan for eval files dated today or yesterday, any leads files from the last 24 hours, any daily scan briefs, and any recruiter triage files. **Step 3: Pipeline snapshot.** If Notion is enabled, query the configured data source for active rows. If disabled, scan all `Dossier/evals/eval-*.md` files and read frontmatter. Count by status: Evaluating, Applied, Interviewing, Offer. **Step 4: Follow-ups due.** Find evals with `status: Applied` and `date` 7+ days ago. **Step 5: Write the digest** to `Dossier/daily/daily-digest-[YYYY-MM-DD].md` with sections: What's New (jobs evaluated, recruiter leads), Action Items, Pipeline Snapshot, Top Priority, Pace Check. Keep the entire digest under 40 lines. No filler. If nothing happened since the last digest, write one line and stop. **Pace Check (rolling 7 days):** Count roles scanned (from `daily/daily-scan-*.md` files in the last 7 days), evals written (`evals/` files dated in the last 7 days), and applications submitted (evals with `status: Applied` and a date in the last 7 days). Report as a single line: `Roles scanned: N | Evals written: N | Applications submitted: N`. If evals written on any single day in the window exceeds 10, add a warning line: `⚠️ High pace detected on [date] (N evals). Evaluation quality tends to degrade above ~10 targeted evals per day — consider scan-only days to keep quality high.` **Hard rules:** This task is read-only — no Notion writes, no Gmail drafts, no calendar events. Only read vault files and optionally Notion.

---

## LinkedIn Pulse (AM)

**Frequency:** Daily, early morning (suggested: 8 AM)
**Purpose:** Lightweight scan of Gmail for new recruiter signals from LinkedIn notifications and cold outreach. Surface ✓ MATCH leads quickly; stay silent if nothing new has arrived.

**Prompt template:**

> You are running the morning LinkedIn lead pulse check. This is a lightweight, fast check — not a full triage. **Step 1: Load state file.** Read `Dossier/.lead-pulse-state.json` to get the list of Gmail thread IDs already seen in prior pulse runs. If the file doesn't exist, treat the seen list as empty. **Step 2: Search Gmail for new recruiter signals** using these queries in parallel: LinkedIn message notifications (newer than 1 day), LinkedIn InMail replies, LinkedIn job alerts (only if role looks like a match per `profile.md`), self-forwarded leads, and cold recruiter outreach not from job boards. **Step 3: Deduplicate** against the seen list. Discard already-seen threads. **Step 4: If zero new threads — stop here. Exit silently.** No file written. **Step 5: For each new thread, extract** recruiter name, company, role, comp signal, and message type. **Step 6: Quick profile filter** — flag as ✓ MATCH, ✗ SKIP, or ? UNCLEAR based on the target roles and roles-to-avoid in `profile.md`. **Step 7: Cross-check pipeline** — is this company already tracked? Check `Dossier/config.md` for `notion.enabled`; query Notion or scan `Dossier/evals/` accordingly. **Step 8: Write the leads file** to `Dossier/leads-[YYYY-MM-DD]-am.md` only if at least one ✓ MATCH or ? UNCLEAR exists. If all threads were ✗ SKIP — silent exit. **Step 9: Update state file.** Append new thread IDs to `.lead-pulse-state.json`. Trim to last 200 entries. **Hard rules:** Read-only on Gmail. No Notion writes. No drafts. No calendar events.

---

## LinkedIn Pulse (PM)

**Frequency:** Daily, afternoon (suggested: 4 PM)
**Purpose:** Identical logic to the AM pulse, scoped to what arrived since approximately 8 AM. Catches mid-day recruiter activity. Silent exit if nothing new.

**Prompt template:**

> You are running the afternoon LinkedIn lead pulse check. Identical logic to the morning pulse but use `newer_than:8h` to focus on the mid-day window. **Step 1: Load state file** `Dossier/.lead-pulse-state.json`. **Step 2: Search Gmail** with the same recruiter signal queries as the AM pulse, using `newer_than:8h`. **Step 3: Deduplicate** against the seen list — discard any thread ID already present. **Step 4: If zero new threads — stop and exit silently.** **Step 5: For each new thread, extract** recruiter name, company, role, comp signal, message type. **Step 6: Quick profile filter** against `profile.md` — ✓ MATCH / ✗ SKIP / ? UNCLEAR. **Step 7: Cross-check pipeline** for each company. Read `config.md` to determine data source (Notion or `Dossier/evals/`). **Step 8: Write the leads file** to `Dossier/leads-[YYYY-MM-DD]-pm.md` only if at least one ✓ MATCH or ? UNCLEAR exists. Silent exit if all are ✗ SKIP. **Step 9: Update state file.** Append thread IDs, trim to last 200. **Hard rules:** Read-only on Gmail. No Notion writes. No drafts. No calendar events.

---

## Mid-Week Triage

**Frequency:** Weekly, mid-week (suggested: Wednesday morning)
**Purpose:** Full recruiter triage session — process all unresolved pulse leads from the week, search the full inbox for recruiter signals, draft replies for the top unresolved matches, and write a triage report.

**Prompt template:**

> You are running the weekly Dossier deep recruiter triage. This is the resolution layer — the AM/PM pulse checks surface leads all week; your job today is to process them thoroughly and draft replies. **Step 0: Read `Dossier/config.md`** and check `notion.enabled`. **Step 1: Load context.** Invoke the `dossier` skill, read `Dossier/cv.md` and `Dossier/profile.md` silently. **Step 2: Collect the week's unresolved pulse leads.** Scan for `leads-[date]-am.md` and `leads-[date]-pm.md` files created since last Wednesday. Build a list of leads flagged "Evaluate JD," "Request JD," or "Reply to engage" that haven't yet been acted on. **Step 3: Run full Mode 9 recruiter triage** against the full inbox using parallel Gmail searches: last-7-days recruiter keywords, job board senders, subject-line signals, LinkedIn notifications. Merge with pulse leads and deduplicate. **Step 4: For each unresolved lead**, assess recruiter name/company/role/comp, days waiting (flag 5+ days as ⚠ AGING), profile match (✓/✗/?), pipeline status. **Step 5: Cross-check pipeline** for each company using the configured data source. **Step 6: Filter and rank** — ✓ MATCH leads oldest-first, then ? UNCLEAR. Drop ✗ SKIP. **Step 7: Create Gmail drafts** for the top 5 unresolved ✓ MATCH leads. Request-JD replies: under 80 words. Engage replies: 2 sentences. Aging leads: acknowledge delay naturally. **Step 8: Write triage report** to `Dossier/recruiter-triage-[YYYY-MM-DD].md` with sections: Priority Queue, New This Week, Reply Drafts Created, Skipped, Inbox Health. **Step 9: Move resolved pulse files** to `Dossier/daily/` for archiving. **Hard rules:** Never send — all writes go to Gmail drafts only. Never mark read, label, or archive Gmail threads.

---

## Weekly Pipeline Digest

**Frequency:** Weekly (suggested: Monday morning)
**Purpose:** Full pipeline review — what's active, what moved in the last 14 days, upcoming interviews, follow-ups due, and recommended focus for the week ahead.

**Prompt template:**

> You are generating the weekly Dossier pipeline digest. **Step 0: Read `Dossier/config.md`** and check `notion.enabled`. **Step 1: Load context.** Invoke the `dossier` skill, read `Dossier/cv.md` and `Dossier/profile.md` silently. **Step 2: Load pipeline state.** If Notion is enabled, query the configured data source for all rows updated in the last 14 days plus all active rows. If disabled, scan all `Dossier/evals/eval-*.md` files and read YAML frontmatter. **Step 3: Classify rows** into Active (Evaluating, Applied, Interviewing), Recently Completed (last 14 days), and New This Week (last 7 days). **Step 4: Cross-reference Gmail** for each active row — search for the company domain in the last 14 days. Note whether a live thread exists. **Step 5: Check Google Calendar** for interviews in the coming 7 days. Flag interviews without a matching prep event. **Step 6: Write the digest** to `Dossier/weekly/pipeline-digest-[YYYY-MM-DD].md` with sections: Active Pipeline (by status), Recently Completed, New This Week, Interviews This Week, Follow-ups Due, Pipeline Health Signals, Suggested Focus for the Week. Keep it scannable — useful at a glance on Monday morning.

---

## Sunday Prep

**Frequency:** Weekly, Sunday evening
**Purpose:** Scan calendar for interviews in the coming week, check whether prep docs exist, auto-generate any missing prep docs via Mode 3, and schedule prep calendar blocks within 24 hours before each interview.

**Prompt template:**

> You are running the Sunday-evening week-ahead interview prep check. **Step 0: Read `Dossier/config.md`** and check `notion.enabled`. **Step 1: Load context.** Invoke the `dossier` skill, read `Dossier/cv.md` and `Dossier/profile.md` silently. **Step 2: Scan Google Calendar** for events in the next 7 days that look like interviews — titles containing "interview," "chat with," "phone screen," "final round," or matching a company name from the pipeline. **Step 3: For each interview found, check whether prep exists** — look for a matching Prep calendar event, a `prep-[company-slug]-*.md` file in `Dossier/interview-prep/`, and notes in the pipeline entry. **Step 4: For any interview WITHOUT prep:** read the Gmail scheduling thread for interviewer names and format, run Mode 3 (Interview Prep) to produce a full prep doc, save to `Dossier/interview-prep/prep-[company-slug]-[YYYY-MM-DD].md`, and create a 90-minute calendar Prep block within 24 hours before the interview with the prep doc in the description and a 15-minute reminder. **Step 5: Write a week-ahead summary** to `Dossier/weekly/week-ahead-[YYYY-MM-DD].md` with sections: Interviews This Week, Prep Docs Drafted, Prep Blocks Scheduled, Recommended Focus, Aging Alerts, Decision Gates, Outreach Follow-ups Due This Week. **Aging Alerts:** Scan `Dossier/evals/` for files where `status: Evaluating` and `date` is 14+ days ago — list each as `[Company] — [Role] | Evaluated [date] | [N] days old — consider applying or passing`. If none, write "No aging evals." **Decision Gates:** Scan `Dossier/evals/` for files whose notes or body mention unresolved conditions (remote policy, end-client disclosure, rate negotiation, clearance, relocation) — list each as `[Company] — Gate: [description] — action needed to unblock`. If none, write "No open gates." **Outreach Follow-ups Due:** Scan `Dossier/outreach/` for files where `sent_date` is populated and the next date in `followup_dates` falls within the coming 7 days — list each as `[Company] — Touch [N] due [date] via [channel]`. If none, write "No follow-ups due." **Hard rules:** Don't send any messages, don't delete events, don't modify events this task didn't create.
