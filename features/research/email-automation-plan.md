# Email Automation Skill — Research, Architecture & Implementation Plan

**Date:** 2026-04-15
**Companion documents:** `dossier-gap-analysis.md`, `dossier-implementation-plan.md`
**Relationship to Dossier:** This is a companion skill, not a replacement. Dossier Mode 9 (Inbox & Follow-up) handles reactive email tasks within a conversation. This skill handles proactive, cadence-driven email automation with stronger guardrails.

---

## 1. Landscape & Prior Art

### What exists today

The email automation space is dominated by **recruiter-side** tooling — platforms built for recruiters sending outreach to candidates. The architecture is well-understood: multi-step sequences with configurable delays, personalization tokens, open/reply tracking, and auto-pause on reply. Key players include Gem, Outreach, Lemlist, Reply.io, SourceWhale, and recruiting platforms like Pin, Juicebox, and GoPerfect.

**Candidate-side** email automation is dramatically underserved. The tools that exist (Sonara, LoopCV, BulkApply) focus on auto-applying — mass-submitting applications — not on intelligent email cadence management. Career-Ops handles email through Claude Code but follows the same pattern as Dossier Mode 9: reactive, single-conversation, draft-only.

No open-source project currently offers a candidate-side email automation system with structured guardrails.

### What the research says about cadence

Data from Gem's analysis of ~8 million outreach sequences and broader industry benchmarks converges on these patterns:

- **3–4 touches** is the sweet spot. Follow-ups increase reply rates by roughly 2.5x over single emails.
- **6 days between touches** is the most common effective cadence. Some data shows 1-day gaps get higher open rates but 6-day gaps get higher response rates.
- **The "breakup email"** (a polite final touch) often converts 10–12% of prior non-respondents.
- **Under 100 words** for follow-ups. Brevity outperforms comprehensiveness.
- **Personalization matters** — but minimal personalization (one specific reference) outperforms heavy personalization that reads like a bot.

These patterns are from recruiter→candidate outreach, but the cadence principles apply in reverse for candidate→recruiter communication.

### What the guardrails literature says

The expert consensus is clear and consistent across sources (Weights & Biases, LangChain, CIO, Zapier, Agno, academic papers on Policy-as-Prompt):

1. **"Prompting is instructing the brain; architecture is tying the hands."** Guardrails must be structural (deterministic code-level constraints), not just prompt-level instructions. You cannot rely on the LLM to enforce its own safety rules.

2. **Three-layer defense:** Policy (the rules), Configuration (the structure/permissions), Runtime (the actual checks before execution).

3. **Draft-before-send is mandatory** for email. Every guardrails guide for email agents recommends starting with "create draft, not send" and only graduating to auto-send after extensive trust-building.

4. **Automation bias is real.** Humans reviewing AI drafts tend to approve them reflexively, especially under time pressure. The guardrail system must make review friction proportional to risk — easy approval for low-stakes follow-ups, forced slowdown for novel outreach.

5. **Least privilege:** The agent should have the minimum permissions needed. Read + draft is the starting position. Send is an upgrade that requires explicit opt-in.

6. **Deterministic checks beat probabilistic ones for safety.** Use regex/rules for recipient validation, rate limiting, and content constraints. Reserve LLM judgment for personalization and tone.

---

## 2. Design Principles

### The core tension

The user wants automation to save time on repetitive email tasks (follow-ups, thank-yous, check-ins). But email is **irreversible and high-stakes** in a job search context — a bad follow-up can burn a warm lead, a premature thank-you can seem insincere, and an email to the wrong person can be career-damaging.

The design must resolve this tension by making the **common case fast** (routine follow-ups on confirmed pipelines) while making the **dangerous case hard** (novel outreach to new contacts, emails with salary information, bulk sends).

### Design principles

1. **Draft-first, send-never (default).** The skill creates Gmail drafts. The user clicks send. Period. This is the same contract as Dossier Mode 9. Auto-send is a graduated privilege, not a default.

2. **Cadence, not spam.** The skill manages structured sequences with defined intervals, personalization, and auto-pause on reply. It does not do mass outreach or spray-and-pray.

3. **Pipeline-aware.** Sequences are triggered by pipeline state (Notion tracker status), not by arbitrary user commands. A follow-up fires because the application has been in "Applied" status for 7 days with no email response — not because the user remembered to ask.

4. **Guardrails are structural, not advisory.** Rate limits, recipient validation, content constraints, and escalation triggers are deterministic checks, not LLM suggestions.

5. **Transparent.** Every automated action is logged. The user can see what was drafted, when, and why. No hidden behavior.

6. **Reversible by default.** Drafts can be deleted. Calendar reminders can be dismissed. Nothing is sent without the user's finger on the button (until they explicitly graduate to auto-send).

---

## 3. Trust Ladder — Graduated Autonomy

The skill operates at one of three trust levels. The user explicitly selects their level in config.md. Higher levels require the lower levels to have been active for a minimum period.

| Level | Name | What the skill can do | Constraint |
|-------|------|----------------------|------------|
| 1 | **Draft** (default) | Read inbox, create drafts, create calendar reminders. Never send. | User clicks send on every email. |
| 2 | **Draft + Notify** | Same as Level 1, plus: surfaces a daily digest of pending drafts with one-click approval. Consolidates review. | Requires Level 1 for 2+ weeks with 10+ drafts reviewed. User opts in via config.md. |
| 3 | **Auto-send (constrained)** | Sends pre-approved template categories (follow-ups on confirmed pipelines) automatically. All other categories remain draft-only. | Requires Level 2 for 4+ weeks. Only sends to recipients already in the Notion tracker. Hard cap of 5 auto-sends per day. Every auto-send is logged and surfaced in the daily digest retroactively. |

**Level 3 restrictions (deterministic, not prompt-level):**
- Only sends to email addresses already associated with a Notion tracker row.
- Only sends emails that match a pre-approved template category (see §5).
- Never sends emails containing salary/compensation data, regardless of template.
- Never sends to more than one recipient per email.
- Hard daily cap: 5 auto-sends. Resets at midnight user-local time.
- Auto-pauses the entire sequence for a company if any reply is detected from that company's domain.

---

## 4. Guardrail Architecture

### Layer 1: Policy (encoded in SKILL.md)

These are the rules the LLM is instructed to follow. They are necessary but not sufficient — Layer 2 enforces them structurally.

- Never fabricate a recipient. Only email addresses from the Notion tracker, Apollo lookups, or Gmail thread history.
- Never include salary expectations, current compensation, or offer details in automated emails unless the user has explicitly approved that specific content.
- Never send a follow-up within 5 days of the last outgoing email to the same recipient.
- Never send more than 3 emails total in a sequence to the same recipient without a reply. After 3, the sequence pauses and asks the user whether to send a breakup email or stop.
- Never auto-send a first-contact email. First contact is always draft-only regardless of trust level.
- Never CC or BCC anyone. One recipient per email.

### Layer 2: Configuration (encoded in config.md)

These are structural constraints the user sets. The skill reads them as parameters, not suggestions.

```yaml
email_automation:
  trust_level: 1                    # 1 = draft, 2 = draft+notify, 3 = auto-send
  daily_auto_send_cap: 5            # Hard ceiling, applies at Level 3
  min_days_between_sends: 5         # Minimum gap between emails to same recipient
  max_sequence_length: 3            # Max emails before reply required
  breakup_email_enabled: true       # Offer a "last touch" after max sequence
  blocked_recipients: []            # Never email these addresses
  blocked_domains: []               # Never email anyone at these domains
  require_approval_for:             # Categories that always need manual review
    - first_contact
    - salary_mention
    - rejection_response
  auto_send_categories:             # Only these categories eligible for Level 3
    - follow_up_application
    - follow_up_interview
    - thank_you_post_interview
```

### Layer 3: Runtime (deterministic checks before any email action)

Before creating any draft or sending any email, the skill executes this checklist. Every check is pass/fail. Any failure blocks the action.

```
PRE-DRAFT CHECKS:
1. Recipient validation
   - Is the recipient email well-formed? (regex)
   - Is the recipient in blocked_recipients or blocked_domains? (exact match)
   - If trust_level = 3: is the recipient associated with a Notion tracker row? (query)

2. Rate limiting
   - Has an email been sent to this recipient within min_days_between_sends? (query Gmail sent folder)
   - Has the daily auto-send cap been reached? (counter)

3. Sequence position
   - How many emails have been sent to this recipient without a reply? (query Gmail threads)
   - If >= max_sequence_length and no reply: BLOCK. Surface to user.

4. Content screening
   - Does the email body contain salary/compensation keywords? (regex scan for
     $, salary, compensation, offer, base, bonus, equity, signing, OTE, TC,
     total comp, pay, wage, stipend, package)
   - If yes AND category is not "salary_mention": BLOCK. Ask user to confirm.

5. Category check
   - What category is this email? (classified by the skill based on context)
   - If category is in require_approval_for: force draft-only regardless of trust level.
   - If trust_level = 3 AND category is in auto_send_categories: eligible for auto-send.
   - Otherwise: draft-only.

PRE-SEND CHECKS (Level 3 only):
6. All PRE-DRAFT checks pass.
7. Reply detection: has a reply been received from this recipient or company
   domain since the last outgoing email? If yes: PAUSE sequence, surface to user.
8. Confirm category is in auto_send_categories.
9. Confirm daily cap not reached.
10. Log the send to the audit trail (see §7).
```

---

## 5. Email Categories & Sequence Templates

Each category has a defined purpose, template structure, cadence rules, and trust-level eligibility.

### Category 1: Follow-up (Application)

**Trigger:** Notion row in "Applied" status for 7+ days with no email response detected.
**Cadence:** Day 7, Day 14, Day 21 (breakup).
**Template structure:**
- Touch 1 (Day 7): Brief, reference role + application date, ask about timeline/next steps. Under 80 words.
- Touch 2 (Day 14): Add one new signal — a recent company achievement, a relevant article, or a specific proof point from the CV that maps to the role. Under 100 words.
- Touch 3 (Day 21, breakup): Polite close. "I'll assume the timing isn't right. I'd welcome the chance to connect in the future." Under 60 words.
**Trust eligibility:** Drafts at Level 1. Auto-send at Level 3.
**Always draft-only if:** First-ever email to this company (no prior thread exists).

### Category 2: Follow-up (Post-Interview)

**Trigger:** Interview logged as complete in Notion, or user says "I just interviewed at [Company]."
**Cadence:** Same day or next morning (thank-you), Day 7 (check-in if no update).
**Template structure:**
- Touch 1 (Day 0–1): Thank-you. Reference one specific discussion point from the interview. Reinforce one proof point. Under 120 words. One per interviewer.
- Touch 2 (Day 7): Brief check-in if no response. "Wanted to follow up on our conversation last [day]. Still very interested — happy to provide any additional information." Under 60 words.
**Trust eligibility:** Thank-you is draft-only at all levels (too important to automate). Day-7 check-in is auto-send eligible at Level 3.
**Always draft-only if:** Thank-you emails (always require personal touch).

### Category 3: Outreach (First Contact)

**Trigger:** User requests outreach, or Mode 5 generates a contact.
**Cadence:** Not a sequence — single email, draft-only.
**Template structure:** Per Mode 5 guidelines (under 150 words, specific, genuine, clear ask).
**Trust eligibility:** Draft-only at ALL levels. First contact is never auto-sent. This is the single most important guardrail in the system.

### Category 4: Re-engagement

**Trigger:** Notion row in "Passed" or "Rejected" status for 90+ days, with a company the user has flagged for re-engagement.
**Cadence:** Single touch.
**Template structure:** Brief note referencing original interaction, noting continued interest if appropriate roles arise. Under 80 words.
**Trust eligibility:** Draft-only at all levels.

### Category 5: Recruiter Reply

**Trigger:** Inbound recruiter email detected in Mode 9 triage.
**Cadence:** Single reply.
**Template structure:** Depends on context — acknowledge interest, express interest/decline, request more info. Per Mode 9 guidelines.
**Trust eligibility:** Draft-only at all levels. Responses to inbound messages are too context-dependent for automation.

---

## 6. Integration with Dossier

This skill does not replace Dossier Mode 9. It extends it with proactive cadence management.

### Data flow

```
Notion tracker (source of truth for pipeline state)
    ↓
Email Automation Skill (reads status, triggers sequences)
    ↓
Gmail (creates drafts via gmail_create_draft)
    ↓
User (reviews drafts, clicks send — or auto-send at Level 3)
    ↓
Gmail (sends)
    ↓
Email Automation Skill (detects reply via gmail_search_messages, pauses sequence)
    ↓
Dossier Mode 9 (processes the reply, proposes Notion status update)
```

### Shared state

- **Notion tracker** is the single source of truth for which companies are in the pipeline and at what stage. The email skill reads it but never writes to it — Notion updates flow through Dossier Mode 9.
- **Outreach markdown files** (Dossier's `outreach/` folder) are the permanent record. Every email the automation skill drafts is also saved as a markdown file per Dossier's file-first discipline.
- **config.md** is extended with the `email_automation:` block (see §4).
- **Audit log** (new, see §7) is written by the email skill.

### Mode 9 changes

Dossier Mode 9 gains awareness of the email automation skill:

- When triaging the inbox, Mode 9 checks whether an inbound email is a reply to an automated sequence. If so, it auto-pauses that sequence and notes it in the triage output.
- When proposing Notion status updates, Mode 9 checks for active sequences. If a status changes to "Interviewing" or "Rejected," it proposes pausing or terminating the corresponding email sequence.

---

## 7. Audit Log

Every email action is logged to `Dossier/email-audit-log.md` (append-only).

```markdown
## Audit Log

| Timestamp | Action | Category | Recipient | Company | Trust Level | Status | Notes |
|-----------|--------|----------|-----------|---------|-------------|--------|-------|
| 2026-04-15 09:12 | draft_created | follow_up_application | recruiter@acme.example.com | Acme Corp | 1 | pending_review | Touch 2 of 3 |
| 2026-04-15 09:15 | user_sent | follow_up_application | recruiter@acme.example.com | Acme Corp | 1 | sent | User clicked send |
| 2026-04-15 14:30 | auto_sent | follow_up_application | hr@initech.example.com | Initech | 3 | sent | Touch 1 of 3, auto-send |
| 2026-04-15 14:35 | sequence_paused | follow_up_application | hr@initech.example.com | Initech | 3 | paused | Reply detected |
| 2026-04-15 16:00 | draft_created | thank_you_post_interview | jane.doe@bigco.example.com | BigCo | 1 | pending_review | Interviewer 1 of 3 |
```

The audit log serves three purposes:
1. **User visibility.** The user can see exactly what happened and when.
2. **Rate limit enforcement.** Daily auto-send counts are computed from the log.
3. **Calibration.** Over time, the log enables analysis of which categories and cadences produce replies.

---

## 8. Security & Privacy Considerations

### PII in templates

Email bodies may contain the user's name, role title, and CV-derived proof points. The skill should:
- Never include full address, phone number, or social security information in automated emails.
- Strip any salary/compensation data unless the user explicitly approves (enforced by Layer 3 content screening).
- Never include information about other companies the user is interviewing with.

### Recipient data

The skill stores recipient email addresses in the audit log and outreach files. This data is PII. The retention policy from the main Dossier plan applies — archived after 90 days, comp-data redacted after 12 months.

### Gmail permissions

The skill uses `gmail_create_draft` (write) and `gmail_search_messages` (read). It does not:
- Read email body content beyond what Mode 9 already processes.
- Modify, label, archive, or delete any emails.
- Access contacts, calendar, or drive through Gmail's scope.

At Level 3, the skill would need `gmail_send_message` capability. This is a separate permission that must be explicitly granted. If not available, Level 3 falls back to Level 2 behavior (draft + notify).

### Anti-abuse

The daily cap (default 5, configurable) prevents runaway automation. The sequence length limit (default 3) prevents harassment. The blocked-domains list prevents accidental personal-email sends. The first-contact-is-always-draft rule prevents the system from reaching people the user hasn't vetted.

---

## 9. Implementation Plan

### Phase 1 — Cadence Engine (Foundation)

**9.1 — Config schema**
Add `email_automation:` block to config.md template. Document all keys, defaults, and validation rules. This is prerequisite to everything else.

**Where:** SKILL.md (new section), config.md template update.

**9.2 — Sequence state tracking**
Add a `sequences.json` file (or `sequences.md` with YAML frontmatter) to the vault root that tracks active sequences:

```yaml
sequences:
  - company: Acme Corp
    role: Senior Data Engineer
    category: follow_up_application
    recipient: recruiter@acme.example.com
    started: 2026-04-08
    touches_sent: 1
    last_sent: 2026-04-08
    next_due: 2026-04-15
    status: active       # active | paused | complete | cancelled
    notion_row_id: abc123
```

The skill reads this file at the start of every session to determine which sequences need action.

**Where:** New file `Dossier/sequences.json`. SKILL.md references it.

**9.3 — Audit log structure**
Create the audit log file and define the append-only write pattern.

**Where:** New file `Dossier/email-audit-log.md`. SKILL.md defines the write contract.

**9.4 — Runtime check pipeline**
Implement the 10-step pre-draft/pre-send check pipeline as a defined procedure in SKILL.md. Every email action flows through this pipeline.

**Where:** SKILL.md (new section, referenced by all email-producing modes).

### Phase 2 — Template Library & Draft Generation

**9.5 — Category definitions**
Define the 5 email categories with their template structures, cadence rules, and trust eligibility.

**Where:** SKILL.md or a new `email-templates.md` reference file in the vault.

**9.6 — Draft generation workflow**
Define the end-to-end workflow: check sequences.json for due actions → run pre-draft checks → generate personalized email from template + CV + pipeline context → save to outreach/ folder → create Gmail draft → update sequences.json → append to audit log.

**Where:** SKILL.md (new Mode 14: Email Cadence, or extend Mode 9).

**9.7 — Daily digest (Level 2)**
When trust_level ≥ 2, produce a daily summary of pending drafts for batch review:

```
# Email Digest — 2026-04-15

## Pending Drafts (3)

1. **Acme Corp** — Follow-up Touch 2
   To: recruiter@acme.example.com
   Preview: "Hi [Name], I wanted to follow up on my application for..."
   → [Review draft in Gmail] | [Approve] | [Skip] | [Cancel sequence]

2. **BigCo** — Thank-you (Interviewer: Jane Doe)
   To: jane.doe@bigco.example.com
   Preview: "Thank you for taking the time to discuss..."
   → [Review draft in Gmail] | [Skip]

3. **Initech** — Follow-up Touch 1
   To: hr@initech.example.com
   Preview: "Hi, I applied for the Analytics Lead role on..."
   → [Review draft in Gmail] | [Approve] | [Skip] | [Cancel sequence]

## Sequences Paused (1)
- **MegaCorp** — Reply detected from hr@megacorp.example.com.
  Run Mode 9 to triage.

## Auto-Sends Today (Level 3): 0/5
```

**Where:** SKILL.md (within Mode 14 or as a daily scheduled task output).

### Phase 3 — Reply Detection & Sequence Management

**9.8 — Reply detection**
Before processing any sequence action, search Gmail for replies from the recipient or their company domain since the last outgoing email. If found: pause the sequence, flag in the digest, and hand off to Mode 9.

**Where:** SKILL.md (within the runtime check pipeline, check #7).

**9.9 — Notion-driven triggers**
Define the mapping from Notion status changes to sequence actions:

| Notion status → | Sequence action |
|-----------------|-----------------|
| Applied (7+ days, no email) | Start follow_up_application sequence |
| Interviewing → Applied (regression) | Pause any active sequence, surface to user |
| Interview logged complete | Start thank_you_post_interview (draft-only) |
| Rejected | Cancel all active sequences for that company |
| Offer | Cancel follow-up sequences, start offer-response consideration (no automation — user handles) |
| Passed | Cancel all sequences. Optionally start re-engagement after 90 days if flagged. |

**Where:** SKILL.md (Mode 14 trigger logic).

**9.10 — Sequence lifecycle management**
Define how sequences are created, paused, resumed, and terminated. Include user commands: "pause the sequence for [Company]," "cancel all sequences," "show active sequences."

**Where:** SKILL.md (Mode 14 commands).

### Phase 4 — Auto-Send (Level 3)

**9.11 — Auto-send implementation**
Only after Phases 1–3 are stable and the user has opted into Level 3 via config.md. Implement the pre-send checks (#6–#10 from the runtime pipeline). Use `gmail_send_message` if available; fall back to draft + notification if not.

**Where:** SKILL.md (Level 3 extension of Mode 14).

**9.12 — Auto-send monitoring**
After every auto-send, append to the audit log and include in the next daily digest as a retrospective entry: "These emails were auto-sent today. Review for any issues."

**Where:** SKILL.md (daily digest extension).

---

## 10. What This Skill Does NOT Do

Explicit boundaries, documented in the skill definition:

1. **Does not auto-apply to jobs.** This skill manages email communication, not application submission.
2. **Does not scrape email addresses.** Recipients come from the Notion tracker, Apollo lookups (via Dossier Mode 5), or existing Gmail threads.
3. **Does not send mass emails.** Maximum one recipient per email. No BCC, no distribution lists.
4. **Does not handle inbound email processing.** That's Dossier Mode 9. This skill handles outbound cadence.
5. **Does not modify the Notion tracker.** It reads state from Notion to trigger sequences, but all status updates flow through Dossier Mode 9 with user approval.
6. **Does not store passwords, API keys, or credentials.** All authentication flows through the existing MCP connectors.
7. **Does not operate without the user's knowledge.** Every action is logged, and the daily digest surfaces all activity.

---

## 11. Summary: Work Items

| # | Item | Phase | Depends on |
|---|------|-------|------------|
| 9.1 | Config schema | 1 | — |
| 9.2 | Sequence state tracking | 1 | 9.1 |
| 9.3 | Audit log structure | 1 | — |
| 9.4 | Runtime check pipeline | 1 | 9.1, 9.2 |
| 9.5 | Category definitions | 2 | 9.1 |
| 9.6 | Draft generation workflow | 2 | 9.2, 9.3, 9.4, 9.5 |
| 9.7 | Daily digest (Level 2) | 2 | 9.6 |
| 9.8 | Reply detection | 3 | 9.2, 9.6 |
| 9.9 | Notion-driven triggers | 3 | 9.2, Dossier outcome tracking |
| 9.10 | Sequence lifecycle management | 3 | 9.2, 9.8, 9.9 |
| 9.11 | Auto-send (Level 3) | 4 | All of phases 1–3 |
| 9.12 | Auto-send monitoring | 4 | 9.11, 9.7 |

**Estimated effort:** ~25–30 hours across 4 phases.

---

## 12. Quality & Accuracy Self-Assessment

### Scores
- **Quality:** 8.5/10 — The trust ladder, three-layer guardrails, and category system are well-grounded in expert literature. The Notion integration gives it structural advantage over prompt-only approaches.
- **Accuracy:** 8.0/10 — Cadence timing is grounded in Gem's 8M-sequence dataset. Guardrail architecture follows the W&B/LangChain/CIO consensus. The main uncertainty is in Level 3 feasibility — gmail_send_message may not be available in all MCP configurations.

### Key risks
1. **Level 3 may not be possible** in Claude.ai's current MCP Gmail integration. If `gmail_send_message` isn't exposed, Level 3 falls back to Level 2 (draft + notify), which is still highly useful.
2. **Sequence state persistence** depends on `sequences.json` being reliably read/written across sessions. If the user doesn't invoke the skill for several days, sequences may fall behind cadence. Mitigation: scheduled task integration (same pattern as Dossier's daily scan).
3. **Automation bias** is the hardest problem. Even at Level 1 (draft-only), users will tend to approve without reading. The daily digest format (with preview text) is designed to make review fast but not mindless — the preview should contain enough content that the user naturally scans it.

---

*This plan is designed to be implemented incrementally. Level 1 alone — drafts + audit log + sequence tracking — is a significant upgrade over the current Mode 9 reactive model. Levels 2 and 3 are graduated improvements that only unlock after the foundation proves stable.*
