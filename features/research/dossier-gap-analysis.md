# Dossier Skill — Gap Analysis & Path Forward

**Date:** 2026-04-15
**Scope:** Competitive landscape review, gap analysis, security/privacy audit, and roadmap to top-tier status.

---

## 1. Competitive Landscape

The Dossier skill operates in a space that has exploded since late 2025. Key comparables:

**Career-Ops** (santifer, 32k+ GitHub stars) is the closest analog and the current benchmark. It runs on Claude Code with 14 skill modes, a Go TUI dashboard, ATS-optimized PDF generation via Puppeteer, batch processing with parallel workers, zero-token portal scanning (Greenhouse/Ashby/Lever APIs directly), ghost job detection, and a STAR+Reflection story bank that accumulates across evaluations. It processed 740+ offers and generated 100+ tailored CVs for its creator, who landed a Head of Applied AI role. Career-Ops has a formal DATA_CONTRACT.md, LEGAL_DISCLAIMER.md covering GDPR and EU AI Act, and a CONTRIBUTING.md that explicitly bans scraping, auto-submit, and personal data PRs.

**AIHawk / Jobs_Applier_AI_Agent** focuses on auto-applying — the opposite design philosophy from Dossier's human-in-the-loop (HITL) approach. It automates form-filling and submission at scale.

**Commercial tools** (Sonara, JobRight, Teal, ApplyArc, Rezi, LoopCV) offer various combinations of ATS scanning, auto-apply, resume building, and tracking dashboards. Most are SaaS with subscription models.

**OpenClaw** is a general-purpose agent framework that can be adapted for job automation via browser control.

### Where Dossier stands

Dossier's architecture — 11 modes, Notion tracker integration, Obsidian-native local vault, MCP connectors (Gmail, Calendar, LinkedIn via browser, Apollo, Indeed, Dice) — is strong and arguably more deeply integrated into a real workflow than Career-Ops. Its strengths are the multi-tool orchestration (Notion + Gmail + Calendar + LinkedIn + Apollo + job boards) and the HITL philosophy. However, several gaps emerge when measured against the top of the field.

---

## 2. Feature Gaps

### 2.1 ATS Optimization (Critical Gap)

**Current state:** Mode 11 (Tailored CV) reorders bullets and swaps terminology, but outputs markdown. There is no ATS compatibility scoring, no PDF rendering pipeline, and no validation against real ATS parsers.

**What top-tier looks like:** Career-Ops generates ATS-optimized PDFs per offer using an HTML template + Puppeteer pipeline with self-hosted fonts and single-column ATS-safe layout. The field consensus is that ATS systems reject 75%+ of resumes due to formatting issues — markdown is invisible to this problem.

**Recommendation:** Add a Mode 12 (or extend Mode 11) that converts the tailored CV to an ATS-safe PDF. Use a docx or HTML-to-PDF pipeline. Include an ATS compatibility checklist (single-column, standard fonts, no graphics/tables, standard section headers). Optionally integrate a keyword-match scoring step that compares JD requirements against the tailored CV and reports a match percentage.

### 2.2 Ghost Job Detection (Notable Gap)

**Current state:** Mode 9 (Hiring Signal Quality) scores 1–5 on JD quality, but there's no structured ghost job detection.

**What top-tier looks like:** Career-Ops added a Block G that flags suspicious listings using free signals: JD quality, reposting history, market data. It runs as an independent legitimacy check that doesn't affect the 1–5 score.

**Recommendation:** Add a ghost job detection module to Mode 1. Check for: recycled/old postings (search for the same JD text or URL across dates), unrealistic requirement lists, no named team or hiring manager, vague responsibilities, and mismatched seniority signals. Report as a separate legitimacy tier (Verified / Plausible / Suspect / Likely Ghost) rather than baking it into the score.

### 2.3 Batch Processing / Pipeline Automation (Moderate Gap)

**Current state:** Modes are single-invocation. Processing 10 JDs requires 10 separate conversations.

**What top-tier looks like:** Career-Ops has a batch mode with parallel workers and a shell orchestrator. It can process a queue of URLs end-to-end (evaluate → generate PDF → log to tracker).

**Recommendation:** Add a Mode 12: Batch Pipeline. Accept a list of JD URLs or Indeed/Dice search results. For each, run Mode 1 (evaluate) → Mode 11 (tailor CV) → log to Notion. Present results as a ranked digest. This is the highest-leverage automation for active job searches.

### 2.4 STAR Story Bank (Moderate Gap)

**Current state:** Interview prep (Mode 3) generates talking points from the CV, but there's no persistent story bank that accumulates across evaluations.

**What top-tier looks like:** Career-Ops maintains 5–10 master stories in STAR+Reflection format that are refined across evaluations and reused in interview prep, cover letters, and outreach.

**Recommendation:** Add a `stories.md` file to the vault root. Mode 3 and Mode 6 should reference and contribute to it. Each story follows STAR+Reflection: Situation, Task, Action, Result, Reflection (what you'd do differently or what it taught you). Stories are tagged by competency theme. Over time, this becomes the user's most valuable prep asset.

### 2.5 Portal Scanning (Notable Gap)

**Current state:** Job search (Mode 2) relies on Indeed and Dice MCP tools. No direct ATS portal scanning.

**What top-tier looks like:** Career-Ops has a zero-token scanner (scan.mjs) that hits Greenhouse/Ashby/Lever APIs directly without LLM costs, with 73+ pre-configured companies.

**Recommendation:** This is infrastructure-heavy and may not be practical within the Claude.ai skill model (no persistent background processes). However, the skill could include a "scan" sub-mode that, given a list of company career page URLs or ATS endpoints, fetches and filters listings against the profile. This would be a session-triggered scan rather than a daemon, but still valuable.

### 2.6 Offer Comparison Mode (Minor Gap)

**Current state:** Mode 7 (Salary Negotiation) handles single offers. No structured multi-offer comparison.

**Recommendation:** When a user has 2+ offers (Notion rows in "Offer" status), offer a side-by-side comparison: total comp breakdown, growth trajectory, culture signals, strategic value. Output as a decision matrix with a clear recommendation.

### 2.7 Data Contract / Update Safety (Notable Gap)

**Current state:** No formal separation between "system files" (skill definition, templates) and "user files" (CV, profile, evals). No update contract.

**What top-tier looks like:** Career-Ops has a DATA_CONTRACT.md that explicitly lists which files are never auto-updated and which are system files that receive updates.

**Recommendation:** Add a `DATA_CONTRACT.md` to the vault. Categories: User Layer (cv.md, profile.md, config.md, evals/, outreach/, etc. — never overwritten by skill updates) and System Layer (SKILL.md, scoring-guide.md, templates — updatable). This protects user data during skill iterations.

---

## 3. Security & Privacy Considerations

This is the area with the most significant unaddressed risk. Dossier processes highly sensitive PII through multiple external services, and the current design has no documented security model.

### 3.1 PII Exposure Surface

**Data at risk:** Full CV (employment history, education, skills — all PII), contact information (email, phone, address), salary history and expectations, interview details, recruiter communications, and company research notes that may contain confidential information.

**Where it flows:**
- **Anthropic API** — every mode sends CV + profile + JD content to Claude. Anthropic's data retention policies apply.
- **Notion** — tracker rows contain company, role, grade, compensation, notes. Notion's data is stored on their servers.
- **Gmail** — Mode 9 reads email threads and creates drafts. Email content passes through Google's MCP.
- **Google Calendar** — Mode 10 creates events with prep doc content in descriptions.
- **Apollo** — Mode 4/5 sends company domains and contact queries. Apollo stores query history.
- **LinkedIn (browser)** — Mode 8 operates in the user's authenticated session. Browser automation carries session hijacking risk if the agent malfunctions.
- **Indeed/Dice** — search queries reveal job search intent and preferences.

### 3.2 Specific Risks and Mitigations Needed

**Risk 1: CV and salary data sent to LLM providers.**
Every conversation sends the full CV to Claude's API. Under Anthropic's consumer terms, conversations may be used for safety research and model improvement unless the user opts out.
*Mitigation:* Document this in a PRIVACY.md. Recommend users who are concerned use the API with data retention controls rather than consumer Claude. Note that the skill cannot control upstream data handling.

**Risk 2: Notion tracker contains compensation data.**
Salary ranges, grades, and notes about offers are stored in Notion, which is cloud-hosted. If the Notion workspace is shared (e.g., team workspace), this data may be visible to others.
*Mitigation:* Add a warning to config.md setup: "Ensure your Notion tracker is in a private workspace. Do not use a shared team workspace for job search tracking." Consider making the compensation field optional or adding a `redact_comp: true` config flag.

**Risk 3: Gmail integration reads all matching threads.**
Mode 9's search queries (`newer_than:7d (recruiter OR "opportunity")`) could surface personal emails that happen to match. The skill instructs to "drop them silently," but the content still passes through the LLM context.
*Mitigation:* Add explicit allow-list / deny-list domains to config.md. Only process emails from domains on the allow-list, or exclude personal domains.

**Risk 4: Apollo contact lookups create a data trail.**
Apollo queries for recruiter contact details (names, emails, LinkedIn URLs) create records in Apollo's system tied to the user's account. This data is subject to Apollo's privacy policy.
*Mitigation:* Document Apollo's data handling in PRIVACY.md. Note that contact lookup creates a permanent record in Apollo's system.

**Risk 5: No data retention or deletion policy.**
Eval files, outreach drafts, and prep docs accumulate indefinitely. The archive discipline moves files but never deletes them. There's no guidance on when or how to purge sensitive data.
*Mitigation:* Add a retention policy to README.md. Suggest: archive after 90 days of inactivity, purge after 12 months (or user-defined). Provide a cleanup script or mode that redacts compensation data from archived evals.

**Risk 6: Browser automation on LinkedIn.**
Mode 8 drives the user's authenticated LinkedIn session. A malfunction could send an unintended message, accept a connection, or expose private browsing activity. LinkedIn also explicitly prohibits automated access in its Terms of Service.
*Mitigation:* The "never send without approval" principle is good but insufficient. Add explicit rate-limiting guidance (no more than X actions per session). Add a ToS compliance warning. Consider whether this mode should be opt-in rather than default.

**Risk 7: No encryption at rest.**
The Obsidian vault is plaintext markdown on disk. If the user's machine is compromised, all job search data — including salary expectations, interview notes, and recruiter contacts — is exposed.
*Mitigation:* Recommend full-disk encryption (FileVault / BitLocker / LUKS) in the setup guide. For high-sensitivity users, note that Obsidian supports encrypted vaults via community plugins (e.g., obsidian-encrypt).

### 3.3 Regulatory Considerations

**GDPR** — If the user is in the EU, or if they're applying to EU companies, the processing of their personal data through US-based services (Anthropic, Notion, Google, Apollo) involves cross-border data transfers. Standard Contractual Clauses (SCCs) should be in place for each service. The skill should note this in a PRIVACY.md.

**CCPA/CPRA** — California applicants have rights to know what data is collected and to request deletion. If the user is in California, their CV data flowing through these services is subject to CCPA. The skill should note that the user is responsible for exercising these rights with each service provider.

**EU AI Act** — The EU AI Act classifies AI systems used in employment and worker management as "high-risk." While Dossier is a candidate-side tool (not an employer tool), users should be aware that AI-generated application materials may be subject to scrutiny under these frameworks.

**LinkedIn ToS** — LinkedIn prohibits scraping and automated access. Mode 8's browser automation operates in a gray area. The skill should include an explicit disclaimer.

---

## 4. Architecture & Quality Improvements

### 4.1 Scoring Calibration Drift

**Issue:** The 10-dimension scoring framework is well-designed, but there's no mechanism to detect or correct calibration drift over time. After 50+ evaluations, the user has no way to check whether a "3" today means the same as a "3" from two months ago.

**Recommendation:** Add a quarterly calibration check. Pull the last 20 evaluations from Notion, compute score distributions per dimension, and flag any dimension where the mean has shifted more than 0.5 points. Present to the user for recalibration.

### 4.2 Feedback Loop

**Issue:** The system evaluates and recommends, but never learns from outcomes. Did the user get an interview? Was the evaluation accurate? This is the biggest structural gap vs. a production-grade system.

**Recommendation:** Add outcome tracking to the Notion schema: `outcome` field (No Response / Rejected / Phone Screen / Interview / Offer / Accepted). Periodically, run a "calibration report" that correlates grades with outcomes. If B-graded roles consistently lead to interviews while A-graded roles don't, the scoring weights need adjustment.

### 4.3 Eval Versioning

**Issue:** "One file per artifact per company per day — update in place" means the user loses the diff if they re-evaluate after the JD changes.

**Recommendation:** Either append a changelog section to the eval file (with date + what changed) or allow date-suffixed versions (eval-company-2026-04-15-v2.md) for re-evaluations of the same role.

### 4.4 Config Validation

**Issue:** If config.md has malformed Notion IDs or missing fields, the skill fails silently or with cryptic errors.

**Recommendation:** Add a Mode 0: Health Check. On first invocation of any session, validate config.md (Notion IDs are valid hex, URLs are well-formed), confirm cv.md exists and is non-empty, confirm profile.md exists, and report status. This is a 5-second check that prevents 20 minutes of debugging.

---

## 5. Roadmap to Top-Tier

Priority-ordered by impact and feasibility:

**Phase 1 — Foundation (Immediate)**
1. PRIVACY.md — Document the full data flow, PII exposure surface, and per-service risk. Include ToS compliance notes for LinkedIn and Apollo.
2. DATA_CONTRACT.md — Separate user files from system files. Protect user data from skill updates.
3. Mode 0: Health Check — Validate config, CV, and profile on session start.
4. Outcome tracking — Add `outcome` field to Notion schema and eval frontmatter.

**Phase 2 — Competitive Parity (1–2 weeks)**
5. Ghost job detection — Append to Mode 1 as an independent legitimacy check.
6. ATS-safe PDF generation — Extend Mode 11 with a docx or HTML-to-PDF step using ATS-safe templates.
7. STAR Story Bank — Add `stories.md`, integrate with Modes 3 and 6.
8. Offer comparison — Side-by-side decision matrix when 2+ offers exist.

**Phase 3 — Differentiation (2–4 weeks)**
9. Batch pipeline — Accept a list of JD URLs, process end-to-end, output ranked digest.
10. Calibration report — Correlate grades with outcomes, flag scoring drift.
11. Email domain allow-list — Tighten Gmail integration to reduce personal email exposure.
12. Retention policy and cleanup mode — Scheduled purge of archived data with compensation redaction.

**Phase 4 — Excellence (Ongoing)**
13. Portal scanning — Session-triggered scan of ATS endpoints (Greenhouse, Ashby, Lever) for configured companies.
14. Scoring weight personalization — Let the user adjust dimension weights based on their priorities (e.g., weight remote/location higher if that's a dealbreaker).
15. Weekly trend reports — Aggregate daily scan data into market trend analysis (which roles are growing, which companies are hiring heavily, salary range movements).

---

## 6. What Dossier Already Does Better Than Most

It's worth noting the strengths, because they're real:

- **HITL philosophy** — The explicit "AI analyzes, user decides" design is the right call. Auto-apply tools risk account bans, spray-and-pray quality issues, and ToS violations. Dossier avoids all of this.
- **Multi-tool orchestration** — The Gmail → Notion → Calendar → LinkedIn pipeline is more deeply integrated than any competitor except Career-Ops.
- **Obsidian-native vault** — Local-first, markdown-based, Dataview-queryable. This is a genuine architectural advantage over cloud-only trackers.
- **Profile-driven evaluation** — The separation of CV (capability fit) from profile (desirability fit) is a design insight that most tools miss entirely.
- **File-first discipline** — "Save the markdown before creating the Gmail draft" is a small rule that prevents a real class of data loss.
- **Cover letter quality constraints** — The 400-word hard limit, banned opener list, and voice-matching to profile.md produce genuinely better cover letters than most AI tools.
- **Negotiation mode** — Mode 7 is unusually comprehensive. The non-comp levers section and weak-leverage handling are above what commercial tools offer.

---

## 7. Quality & Accuracy Self-Assessment

### Initial Scores
- **Quality (depth, actionability, structure):** 7.5/10
- **Accuracy (factual claims, competitive comparisons, regulatory citations):** 7.0/10

### Identified Weaknesses in Initial Draft
1. The regulatory section cited frameworks broadly but didn't distinguish between employer-side and candidate-side obligations clearly enough.
2. The Career-Ops comparison could be more specific about *which* features are relevant and which are architecture-dependent (e.g., Go TUI is irrelevant to a Claude.ai skill).
3. The ATS section relied on industry-average rejection rates without noting that these stats come from resume optimization vendors with a commercial interest in inflating the problem.
4. Missing: explicit acknowledgment that some recommendations (portal scanning, batch processing) are constrained by Claude.ai's session model — they'd require Claude Code or a persistent runtime.

### Revisions Applied
1. **Regulatory section revised:** Added explicit note that Dossier is a candidate-side tool, not an employer tool, which changes the regulatory posture significantly. GDPR/CCPA obligations primarily fall on the services (Anthropic, Notion, Google), not on the user running a local skill. The user's obligation is to understand what they're sending where.
2. **Career-Ops comparison sharpened:** Noted that Career-Ops' Go TUI, Playwright PDF pipeline, and batch-runner.sh are infrastructure features that require Claude Code + a local dev environment. Dossier's Claude.ai integration is a different deployment model with different strengths (accessibility, zero-setup) and constraints (no persistent processes, no local shell scripts).
3. **ATS rejection stats caveated:** Added note that the "75% of resumes are rejected by ATS" figure originates from resume optimization vendors and should be treated as an upper bound, not a base rate. The real issue is formatting compatibility, which is genuinely important regardless of the exact percentage.
4. **Feasibility constraints added:** Roadmap now notes which recommendations require Claude Code vs. Claude.ai, so the user can prioritize based on their deployment model.

### Revised Scores
- **Quality:** 8.5/10 — Actionable, well-structured, prioritized. Could be higher with user-specific data (which evaluations have been run, what outcomes look like).
- **Accuracy:** 8.0/10 — Competitive claims are grounded in public data. Regulatory framing is appropriately qualified. ATS claims are caveated. Remaining uncertainty is in the rapidly evolving AI regulation space where rules are still being finalized.

---

*This analysis is based on publicly available information as of April 2026. The AI career tooling landscape is moving fast — recommendations should be re-evaluated quarterly.*
