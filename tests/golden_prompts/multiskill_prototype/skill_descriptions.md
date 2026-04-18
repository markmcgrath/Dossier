# Multi-Skill Prototype — Skill Descriptions

**Date:** 2026-04-17  
**Purpose:** Defines the five candidate skill descriptions for the Phase 2 routing ablation experiment. These are prototype descriptions — they do not require full SKILL.md files to test routing behavior. The routing test evaluates description match only.

**Source:** Plan 11, Phase 3 default split (section 3.1), adjusted per G2 (drop dossier-core router) and G3 (drop dossier-guard, replace with hooks).

---

## dossier-evaluate

**Modes owned:** 1 (Offer Evaluator), 7 (Salary Negotiation), 13 (Calibration Report)

**Description (prototype):**
> Use when the user asks whether to apply to a role, whether a role is a good fit, how to evaluate a job description, how to grade or compare opportunities, or how to negotiate compensation. Also trigger when the user pastes or shares a job description or JD link, asks "should I apply", "is this a good fit", "is this a fair offer", "how much should I ask for", "counter-offer", or asks how accurate their past evaluations have been. Trigger for salary questions, offer comparisons, and scoring calibration.

**Character count:** 605 chars (well under 1,536 limit)

**Trigger phrases covered:**
- "Evaluate this JD / posting"
- "Should I apply"
- "Is this a good fit"
- "Is this a fair offer"
- "How much should I ask for"
- "Counter-offer"
- "Am I grading accurately"
- "Calibration report"

---

## dossier-search

**Modes owned:** 2 (Job Search), 2.1 (Portal Scan), 12 (Batch Pipeline)

**Description (prototype):**
> Use when the user wants to find job listings, search for roles by title or keyword, scan target company career pages for new postings, or batch-evaluate multiple job descriptions at once. Trigger on "find me jobs", "search for roles", "portal scan", "scan my target companies", "batch eval", "rank these listings", or when the user provides multiple JDs or JD URLs to compare and prioritize.

**Character count:** 393 chars

**Trigger phrases covered:**
- "Search for [role] jobs"
- "Find me jobs"
- "Scan my target companies"
- "Portal scan"
- "Batch eval / evaluate these listings"
- Multiple JD URLs provided

---

## dossier-packet

**Modes owned:** 5 (Outreach), 6 (Cover Letter), 11 (Tailored CV)

**Description (prototype):**
> Use when the user needs to draft an outreach message to a recruiter or hiring manager, write a cover letter for a specific role, tailor their CV for an application, or find contact information for someone at a target company. Trigger on requests to "draft a LinkedIn message", "write a cover letter", "tailor my CV", "find the head of [function] at [company]", or any request to create a job application artifact.

**Character count:** 421 chars

**Trigger phrases covered:**
- "Draft a LinkedIn message / outreach"
- "Write a cover letter"
- "Tailor my CV"
- "Find the hiring manager / recruiter at [company]"
- "Draft something to send to [person]"

---

## dossier-prep

**Modes owned:** 3 (Interview Prep), 4 (Company Research), 8 (LinkedIn Browser)

**Description (prototype):**
> Use when the user wants to prepare for an upcoming interview, research a company before applying or interviewing, or use LinkedIn directly (search for people, scan recruiter messages, check a profile, or prepare a connection request). Trigger on "prep me for my interview", "tell me about [company]", "research [company]", "I have an interview at", "search LinkedIn for", "check [person]'s profile", or any pre-interview or company intelligence request.

**Character count:** 452 chars

**Trigger phrases covered:**
- "Prep me for my interview"
- "I have an interview at [company]"
- "Research / tell me about [company]"
- "Search LinkedIn for [person / title]"
- "Check [person]'s LinkedIn profile"
- "Scan recruiter messages on LinkedIn"

---

## dossier-pipeline

**Modes owned:** 0 (Health Check), 9 (Inbox / Follow-up), 10 (Calendar Ops), Weekly Trend Report

**Description (prototype):**
> Use when the user asks about the state of their job search pipeline, wants to triage recruiter emails, sync application statuses, draft follow-up or thank-you notes, schedule prep blocks or interview-related calendar events, or review weekly pipeline trends. Trigger on "what recruiters have reached out", "any updates on my applications", "draft a follow-up", "write a thank-you note", "schedule a prep block", "health check", "what do I have coming up", or "weekly trends".

**Character count:** 466 chars

**Trigger phrases covered:**
- "What recruiters have reached out"
- "Any updates on my applications"
- "Draft a follow-up / thank-you note"
- "Schedule a prep block"
- "Health check on my vault"
- "Weekly pipeline trends"
- "What do I have coming up"

---

## Total description budget

| Skill | Chars | % of 1,536 limit |
|-------|-------|-----------------|
| dossier-evaluate | 605 | 39% |
| dossier-search | 393 | 26% |
| dossier-packet | 421 | 27% |
| dossier-prep | 452 | 29% |
| dossier-pipeline | 466 | 30% |
| **Total** | **2,337** | Across 5 skills (each assessed individually — no combined limit) |

Each skill description is well under the 1,536-character per-skill limit. Combined total across five descriptions is 2,337 characters — equivalent to about 29% of a single 8,000-character context window fallback budget if all five were active simultaneously.
