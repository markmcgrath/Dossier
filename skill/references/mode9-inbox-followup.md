# Mode 9: Inbox & Follow-up (Gmail) — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User asks "what recruiters have reached out," "any updates on my applications," "draft a follow-up," "write a thank-you note for [interview]," or wants to scan recruiter emails, triage the inbox, or process application status updates.

**Why this mode exists:** Most job-search activity eventually flows through email — recruiter outreach, application acknowledgments, rejections, interview scheduling, offers. Without inbox integration, the pipeline goes stale and follow-ups fall through the cracks. This mode closes that loop using Gmail's `search_messages`, `read_thread`, and `create_draft` tools to surface and act on email signals.

**Domain Filtering (apply before any thread processing):**

1. Read `gmail_allow_domains` and `gmail_deny_domains` from config.md.
2. If `gmail_allow_domains` is set and non-empty: **only** process threads from domains in the allow list. Drop all others silently — the deny list is irrelevant when allow list is active.
3. If `gmail_allow_domains` is empty or absent AND `gmail_deny_domains` is set: drop threads from denied domains only; process all others normally.
4. If both lists are empty or absent: process all matching threads (use existing "stay out of personal email" heuristic).
5. Never summarize, mention, or count dropped threads.

**Why this matters:** Mode 9's Gmail searches use broad queries (`newer_than:7d (recruiter OR "opportunity")`). Without domain filtering, personal emails matching job-related keywords get surfaced through Claude's context — this is the primary PII exposure risk in this skill.

**Core workflows:**

**Recruiter Triage.** When asked "what's in my recruiter inbox" or similar:
1. Search Gmail with queries like `newer_than:7d (recruiter OR "opportunity" OR "role at" OR "interested in your")` and `newer_than:14d from:(linkedin.com OR indeed.com OR dice.com OR hired.com)`.
2. For each thread, read the latest message and summarize: sender, company (if derivable from email domain or signature), role mentioned, stage (cold outreach / replied / scheduling / declined), and freshness.
3. Cross-reference against `evals/` — does this company already have an evaluation file? If so, surface it with a wikilink: `[[eval-company-slug-date]] — Grade [X], status: [Y]`. Flag matches.
4. Surface the top 3–5 worth acting on, with a one-line recommendation for each (reply / ignore / evaluate the role / already in pipeline).
5. Offer to draft replies for the ones the user flags.

**Application Status Sync.** When asked to "update my tracker" or "see if there are any updates":
1. Scan `evals/` for files where `status: Applied` or `status: Interviewing` in the frontmatter.
2. For each, search Gmail for the company domain or recruiter name in the last 30 days.
3. Classify any new messages and map to a `(status, outcome)` pair per `references/status-outcome-state-machine.md`:
   - Acknowledgment ("we received your application") → `status: Applied`, `outcome: Pending`
   - Phone screen / recruiter scheduling invite → `status: Interviewing`, `outcome: Phone Screen`
   - Panel / onsite / loop invite (post-phone-screen, typically a Teams/Zoom call with hiring manager + panel) → `status: Interviewing`, `outcome: Interview`
   - Rejection ("not moving forward") → `status: Rejected`, `outcome: Rejected` (last-event wins — apply even if the current outcome is `Interview`)
   - Offer email → `status: Offer`, `outcome: Offer`
   - Silence → no change proposed
4. Propose frontmatter updates in a batch for user approval (show both the new `status` and `outcome` before writing). Every proposed status change must include the paired outcome per the state machine — never propose one without the other. If the new `status` is terminal (`Rejected`, `Passed`, `Offer-Declined`), the batch must also include the archival plan per `references/terminal-archival.md` — destination folder (versioned if the slug already has an archive), every bundle file that will move, and any path-style cross-references that will be rewritten to wikilink form. One approval covers the status/outcome write, the file moves, and the rewrites. Update the eval files with confirmed changes. Optionally: if `notion.enabled: true`, offer to mirror these updates to Notion after vault updates are confirmed.

**Follow-up Engine.** When asked to "check follow-ups" or periodically:
1. Scan `evals/` for files where `status: Applied`, `date:` > 7 days ago, and `outcome: Pending`. Search Gmail for each. Draft follow-ups for those with no response.
2. For each match, search Gmail for any recent thread with that company. If there's no response and no active thread, draft a polite follow-up using `create_draft`:
   - Reference the role and application date
   - Keep it under 100 words
   - Express continued interest without desperation
   - Ask a specific question (timeline, next steps) rather than a vague nudge
3. Surface the drafts for user review. Never send — Gmail drafts wait for the user to click send.

**Post-Interview Thank-You.** When an interview is logged as complete, or when asked "draft a thank-you":
1. Pull interviewer names from the Mode 3 prep doc if it exists, or ask the user.
2. Search Gmail for the scheduling thread to confirm interviewer email addresses.
3. Draft a separate thank-you per interviewer using `create_draft` — each one references something specific from the conversation (user tells you what was discussed) rather than recycling the same template.
4. Keep each under 150 words: thank them, reference one specific thread from the conversation, reinforce one proof point relevant to what they probed, close with continued interest.
5. Aim to have drafts ready within 24 hours of the interview — timing matters.

**Interview Scheduling Assist.** When asked "what interviews do I have coming up" or to prep:
1. Search Gmail for recent calendar invites and scheduling threads (`subject:(interview OR "chat with" OR "call with")`).
2. Surface upcoming interviews with date, company, role, and interviewer names if visible.
3. Offer to run Mode 3 (Interview Prep) for any of them.

**Operating principles:**

- **Never send, never auto-reply.** All Gmail writes go to drafts. The user clicks send.
- **Batch, don't badger.** Don't ask for approval on 10 separate status updates one at a time. Propose the full diff, let the user approve in one pass.
- **Respect the inbox.** Don't mark things read, don't label, don't archive. Read-only plus draft-only is the contract.
- **Cross-reference before acting.** Always check the `evals/` folder before drafting a follow-up — confirm the application is still active and no response has been received.
- **Stay out of personal email.** Filter aggressively to job-related threads. If a query surfaces personal messages, drop them silently rather than summarizing.
