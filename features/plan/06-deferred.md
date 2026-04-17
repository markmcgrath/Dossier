# Stream F — Deferred & Speculative

**Estimated effort:** 30+ hours (if all items are built)
**Depends on:** Streams A–E stable and validated in real use
**Status:** Do not start until the base skill is solid

---

## Why These Are Deferred

These items are either large standalone projects (email automation), dependent on unverified infrastructure (portal scanning), or require accumulated data (weekly trends). Building them on a foundation that's still shifting is wasteful.

The base skill with Streams A–E is a complete, competitive product. Stream F is what makes it exceptional — but only if the foundation holds.

---

## F.1 — Batch Pipeline (Mode 12)

**What:** Accept a list of JD URLs or search results, process each through a lightweight Mode 1, and output a ranked digest.

**Where:** SKILL.md — new mode

**Key design:**
- Maximum 10 per batch in Claude.ai (context window constraint)
- Lightweight Mode 1 per item: one-line summary, score, grade, legitimacy tier. Skip CV tailoring and interview probability.
- Ranked digest table with "Top Picks" (B+) and "Skip" (D or below) sections
- Dedup against local `evals/` before evaluating
- Save digest to `daily/batch-eval-[date].md`
- If Notion enabled, log all with `status: Batch-Evaluated`

**Dependency:** Requires [[04-competitive#D.1|ghost job detection]] for legitimacy tiers.

**Open question:** Is 10 items per batch realistic in a single context window? The skill itself is 764 lines. Each lightweight eval adds ~500 tokens of output. With CV + profile + 10 JDs, we're at roughly 30,000–40,000 tokens of context. This should work with current model context windows but needs empirical validation.

**Estimated effort:** 2–3 hours

---

## F.2 — Portal Scanning

**What:** Session-triggered scan of public ATS endpoints for configured target companies.

**Where:** SKILL.md Mode 2 enhancement (sub-mode)

**ATS endpoints:**
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{token}/jobs`
- Ashby: `https://api.ashbyhq.com/posting-api/job-board/{token}`
- Lever: `https://api.lever.co/v0/postings/{token}`

**Requires:** A `target_companies` list in config.md with company name, ATS type, and board token.

### Feasibility Risk — Must Validate First

The original plan assumes `web_fetch` can reach these ATS API endpoints. This has not been verified. Before spending any implementation time:

1. Test `web_fetch` against `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs`
2. If blocked by content restrictions → this feature needs an alternative approach (browser automation via Claude in Chrome, or manual URL entry)
3. If the APIs are reachable → proceed with the spec

**Do not design or implement until the feasibility test passes.**

**Estimated effort:** 0.5 hours (feasibility test) + 2 hours (implementation if viable)

---

## F.3 — Weekly Trend Report

**What:** Aggregate daily scan data into market trend analysis.

**Where:** SKILL.md — output section of weekly pipeline digest

**Metrics:**
- Total new listings per week (volume trend)
- Grade distribution per week (quality trend)
- Most common role titles and keywords
- Companies appearing most frequently
- Salary range trends (if disclosed)
- Legitimacy distribution (% Verified vs. Suspect)

**Dependency:** Requires 4+ weeks of accumulated daily scan data. If insufficient data exists, skip the trend section gracefully.

**Estimated effort:** 1–1.5 hours

---

## F.4 — Email Automation (Companion Skill)

**What:** A separate skill for proactive, cadence-driven email automation with a three-level trust ladder and structural guardrails.

**Reference:** [[../research/email-automation-plan|Email Automation Plan]] (full spec, 480 lines)

**Estimated effort:** 25–30 hours across 4 phases

### Why This Is Fully Deferred

1. **The base skill has unresolved gaps.** No PRIVACY.md, no outcome tracking, no story bank, no vault-first in Modes 9–10. Fix the foundation before adding a companion skill.

2. **Level 3 (auto-send) feasibility is unverified.** The Gmail MCP may not expose `gmail_send_message`. If it doesn't, the entire Phase 4 of the email automation plan is dead. Test this before investing design time in auto-send workflows.

3. **The spec is still Notion-dependent.** The email automation plan's data flow diagram (§6) and all sequence triggers (§9.9) use Notion as the source of truth. These must be rewritten to use vault-first frontmatter before implementation.

### Reconciliation Required

Before starting email automation work, reconcile these conflicts with the vault-first architecture:

| Email Automation Plan Says | Vault-First Requires |
|---------------------------|---------------------|
| "Notion tracker (source of truth for pipeline state)" §6 | Eval frontmatter is source of truth |
| "Pull the list of applications from Notion" §9.9 triggers | Scan `evals/` frontmatter for status |
| "Notion row in Applied status for 7+ days" §5 Category 1 | `evals/` file with `status: Applied`, `date:` > 7 days |
| "Never writes to Notion" §10 boundary | Correct — maintain this in vault-first |
| "sequences.json tracks notion_row_id" §9.2 | Replace with eval file path reference |

### Recommended Email Automation Sequence (if/when started)

1. **Feasibility test** — verify `gmail_send_message` exists in the MCP (30 min)
2. **Phase 1 only** — config schema, sequence state tracking, audit log, runtime checks. This gives Level 1 (draft-only) capability. (6–8 hours)
3. **Real-world validation** — use Level 1 for 2+ weeks before building further
4. **Phase 2** — template library, draft generation workflow, daily digest (6–8 hours)
5. **Phase 3** — reply detection, sequence management (4–6 hours)
6. **Phase 4** — auto-send, only if `gmail_send_message` is available AND Level 2 is proven stable (4–6 hours)

---

## F.5 — Pipeline State Machine

**What:** Encode explicit pipeline states with transition rules (identified → evaluated → applied → interviewing → offer → closed).

**From:** Deep research report recommendation

**Why deferred:** The vault-first architecture with outcome tracking ([[03-foundation#C.3|C.3]]) gives us the *data* for pipeline state. A formal state machine with enforced transitions is a rigidity vs. flexibility tradeoff. For a prompt-based skill where the AI interprets state rather than code enforcing it, the current approach (valid values documented, Mode 0 spot-checks) is sufficient. Revisit if malformed states become a real problem.

**Estimated effort:** 2 hours (if needed)

---

## Stream F Total Estimates

| Item | Hours | Status |
|------|-------|--------|
| F.1 Batch pipeline | 2–3 | Ready to build after D |
| F.2 Portal scanning | 2.5 | Blocked on feasibility test |
| F.3 Weekly trends | 1–1.5 | Needs 4+ weeks of data |
| F.4 Email automation | 25–30 | Fully deferred |
| F.5 State machine | 2 | Low priority |
| **Total** | **~33–39** | |
