# Stream E — Advanced Features

**Estimated effort:** 4–5 hours
**Depends on:** [[03-foundation|Stream C]] (config extensions, outcome tracking); [[04-competitive|Stream D]] partial (outcomes need time to accumulate for calibration)
**Blocks:** Nothing — these are the last pre-ship features
**Reference:** [[../research/dossier-implementation-plan|Implementation Plan]] §3.1–3.5

---

## Why These Come Later

These features either depend on accumulated data (calibration needs outcomes), wire up config keys defined in Stream C, or provide polish rather than core functionality. They're valuable but not blocking.

---

## E.1 — Calibration Report (Mode 13)

**What:** Periodic analysis correlating evaluation grades with actual outcomes. Detects scoring drift and identifies which dimensions predict results.

**Where:** SKILL.md — new mode definition

**Trigger:** "How accurate are my evaluations," "calibration report," "check my scoring," or 50+ evaluations / 3+ months of activity.

**What it does:**
1. Scan `evals/` for all files with a non-Pending `outcome`. Minimum 15 needed for meaningful analysis.
2. **Grade-to-outcome correlation** — for each grade band (A, B, C, D, F): total evals, % reaching Interview+, % reaching Offer+, % No Response, % Rejected
3. **Predictive check** — well-calibrated system shows monotonically decreasing interview rate from A→F. Flag breaks in this pattern.
4. **Dimension analysis** — for Interview+ roles vs. No Response roles, compare average score per dimension. Identify which dimensions are most predictive.
5. **Scoring drift** — compute mean score per month. Flag if shifted by 0.5+ points (grade inflation or deflation).

**Output:** Save to `weekly/calibration-report-[date].md`

**Revision from original:** The original queries Notion. This version reads eval frontmatter directly.

**Practical note:** This mode won't produce useful output until the vault has 15+ evaluations with real outcomes. It can be *defined* now but won't be *useful* for weeks or months. Define it, but don't prioritize testing it over features that work immediately.

**Acceptance:**
- Mode 13 defined in SKILL.md
- Produces meaningful report with 15+ outcomes
- Identifies predictive dimensions and drift
- Gracefully handles insufficient data ("Not enough outcomes yet — update outcomes via Mode 9 and try again later")

---

## E.2 — Gmail Domain Filtering

**What:** Wire the `gmail_allow_domains` and `gmail_deny_domains` config keys into Mode 9.

**Where:** SKILL.md Mode 9, new pre-step before all Gmail search workflows.

**Behavior:**
1. Read domain lists from config.md
2. If `gmail_deny_domains` is set: silently drop threads from denied domains. Do not summarize or mention.
3. If `gmail_allow_domains` is set and non-empty: only process threads from allowed domains. Drop all others.
4. Deny takes precedence over allow (if a domain is in both, it's denied).
5. If neither is set: current behavior (process all matching threads with "stay out of personal email" heuristic)

**Why this matters for privacy:** Mode 9's Gmail searches use broad queries (`newer_than:7d (recruiter OR "opportunity")`). Without domain filtering, personal emails matching job-related keywords get surfaced and sent through Claude's context. This is the most likely source of unintended PII exposure.

**Acceptance:**
- Domain filtering runs before any thread processing in Mode 9
- Deny-list takes precedence
- Absent config = current behavior (no regression)

---

## E.3 — Scoring Weight Personalization

**What:** Let the user override default dimension weights via `scoring_weights` in config.md.

**Where:** SKILL.md Mode 1, scoring section (insert before the weight table).

**Behavior:**
1. Before applying defaults, check config.md for `scoring_weights`
2. Only override dimensions explicitly listed. Others keep defaults.
3. After applying overrides, validate weights sum to 100. If not → warn and fall back to defaults.
4. Gate-pass rules still apply regardless of custom weights.
5. Note in output when custom weights are active: "Scored with custom weights (see config.md)."

**Example config:**
```yaml
scoring_weights:
  "Remote / Location Fit": 15
  "Strategic Career Value": 8
```

**Assumption challenged:** Personalized weights are useful, but there's a bootstrapping problem — the user doesn't know which weights to change until they have calibration data, and calibration data requires outcomes, which require time. The default weights should be good enough for the first 20–30 evaluations. This feature is correctly positioned in Stream E, not earlier.

**Acceptance:**
- Custom weights applied when configured
- Validation catches weights that don't sum to 100
- Gate-pass logic unaffected
- Output notes when custom weights active

---

## E.4 — Retention Policy

**What:** Document a data retention policy and periodic cleanup guidance.

**Where:** README.md (new section), cross-referenced from PRIVACY.md.

**Policy:**

### Active Data
`cv.md`, `profile.md`, `config.md`, `stories.md`, all working folders — keep indefinitely while search is active.

### Time-Decay Data
Already covered by existing archival rules in README.md (`daily/` → subfolder after 60 files, `weekly/` → subfolder after 26 files).

### Terminal Data
- Terminal-state companies → `archive/` per existing discipline
- After 12 months in archive: consider redacting compensation data (replace salary figures with "Archived")
- After search concludes: export `stories.md` (most durable asset), consider archiving or deleting the rest

### Quarterly Cleanup Checklist
1. Move terminal-state companies to `archive/`
2. Review `archive/` for files > 12 months — redact comp data
3. Run time-decay archival on `daily/` and `weekly/`
4. Delete `.lead-pulse-state.json` if no longer scanning
5. Confirm config.md values are still valid

**Acceptance:**
- Policy documented in README.md
- PRIVACY.md references the retention policy
- Checklist is actionable without the skill's help

---

## E.5 — Cost Controls and Research Caching

**What:** Add cost awareness notes for batch operations and establish a research caching convention.

**Where:** SKILL.md — note in batch-relevant modes and Mode 4 (Research).

**Cost awareness note** (for Mode 12 and any scanning mode):
```
Approximate token costs:
- Full Mode 1 evaluation: ~3,000–5,000 tokens in, ~2,000–3,000 out
- Batch of 10: ~50,000–80,000 tokens total
- Full Mode 4 company research: ~5,000–10,000 tokens with web search
```

**Research caching rule:** If a Mode 4 research brief exists for a company from the last 30 days, reuse it rather than re-researching. Note the reuse: "Company research from [date], reused."

**Why:** The deep research report flagged token cost as a scalability concern. This is lightweight but establishes the principle before batch processing ships in [[06-deferred#F.2|Stream F]].

**Acceptance:**
- Cost notes present in SKILL.md
- Mode 4 checks for existing briefs before researching
- Research reuse is noted in evaluation output

---

## Estimated Breakdown

| Task | Hours |
|------|-------|
| E.1 Calibration report (Mode 13) | 1.5 |
| E.2 Gmail domain filtering | 0.8 |
| E.3 Scoring weight personalization | 0.8 |
| E.4 Retention policy | 0.4 |
| E.5 Cost controls + caching | 0.3 |
| **Total** | **~3.8** |
