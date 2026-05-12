---
type: eval
company: "DataCore Systems"
role: "Senior Data Platform Engineer"
grade: A
score: 4.7
status: Evaluating
outcome: Pending
date: 2026-04-15
location: "Remote (PST/PT timezone required)"
compensation: "$200,000–$240,000 + $30K signing + 0.15–0.25% equity"
legitimacy: Verified
model: claude-sonnet-4-6
sources: ["DataCore Systems careers page", "April 2026 Series B announcement (Sequoia/Gradient Ventures)", "Glassdoor (4.6/5, 120 reviews)"]
notes: "Near-perfect fit on data platform engineering scope, Spark/Snowflake stack, and governance depth; Databricks gap is shallow and DataCore is actively evaluating alternatives."
---

<!-- Fictional example. "DataCore Systems" and every detail below are illustrative only. -->

> **REFERENCE OUTPUT — strong-fit eval.** This artifact is a regression anchor for Mode 1 on `tests/fixtures/jd_strong_fit.md`. If a Mode 1 change causes substantive (not formatting) drift on this fixture, escalate before merging — update this golden in the same PR with a CHANGELOG note, or revert the change. See [`README.md`](README.md) for the workflow.

# DataCore Systems — Senior Data Platform Engineer
**Grade: A | Score: 4.7/5 | Legitimacy: Verified**

---

## Summary

DataCore Systems is a well-funded Series B data infrastructure company (150 employees, $50M raised from Sequoia and Gradient Ventures in April 2026) building ETL, governance, and real-time analytics for 500+ mid-market customers. The Senior Data Platform Engineer role sits on the 6-person Core Platform team reporting to VP of Engineering Sarah Chen, with full P0 ownership over infrastructure serving those 500+ deployments. The JD's technical scope — Spark-based processing, multi-tenant governance, access controls, and a Polars/Arrow cost evaluation — maps almost precisely to what this candidate has been building for the last four years. The on-call commitment (1 week/quarter) and twice-weekly PST sync are compatible with the candidate's location preferences. This is a strong yes.

## CV Match

**Strong alignment:**
- 9 years building data platforms at scale maps squarely to the 8+ year floor; current Platform Lead role at a logistics fintech is direct evidence of P0 ownership at comparable deployment scale.
- Hands-on Snowflake + dbt experience from the retail analytics SaaS role (2019–2021) is directly in-stack for DataCore's Snowflake layer, and warehouse cost management experience covers the same optimization problem driving DataCore's Polars/Arrow evaluation.
- Multi-tenant data governance with RLS from the fintech compliance environment is the closest available analog to DataCore's lineage tracking, PII detection, and access controls work — not a stretch, a near-exact reframe.
- Spark cluster optimization at current role is the technical foundation of the existing DataCore processing infrastructure, and Spark-to-DuckDB migration judgment (sub-100MB table routing) is a pattern this candidate has navigated.
- Cross-functional collaboration with analytics, ML, and backend teams is core to the platform lead archetype and matches the mentoring + architectural decision-making responsibilities.

**Gaps and mitigations:**
- No prior hands-on Databricks experience. Databricks is Spark with a managed control plane and Delta Lake as the table format — this candidate knows Spark deeply. Ramp time is estimated at 4 weeks on Databricks-specific APIs, Delta Lake versioning patterns, and the Unity Catalog governance layer. Mitigating factor: DataCore is explicitly evaluating Polars/Arrow as a replacement, so Databricks depth may matter less at the 12-month mark than it does on day one.
- No Polars or Arrow hands-on experience, but these are listed as nice-to-haves rather than requirements, and the candidate's warehouse cost work provides the economic intuition DataCore is trying to apply.

## Level & Seniority

Right level. Senior IC on a 6-person team at a 150-person Series B is squarely where a 9-year platform engineering veteran operates — not a step down, not an overreach. The JD explicitly positions this as a non-junior role with P0 ownership and mentions the team growing from 6 to 8 this year, which opens a natural path to Staff-level scope within 18–24 months. The comp ceiling ($240K base) is consistent with senior IC market rates in SFO and aligns with this profile.

## Compensation

**Above the candidate's floor.** $200–240K base clears the $190K compensation floor with comfortable margin. The $30K signing bonus covers any transition costs. The equity band (0.15–0.25%, 4-year vest with 1-year cliff) is real Series B equity from a company with verifiable Sequoia/Gradient backing — at a modest 3–5x exit multiple, this represents meaningful additional upside. The 4% 401(k) match, 100% employee health premium coverage, and $2K professional development budget are standard Series B benefits and contribute to a strong total package. Year-1 effective comp (base + signing amortized) lands in the $215–255K range depending on base negotiation.

## Growth & Strategic Value

Owning P0 infrastructure across 500+ customer deployments is the kind of verifiable, high-stakes scope that strengthens a resume regardless of how the company performs at exit. The explicit Polars/Arrow evaluation is a genuine technical challenge — whoever architects that decision will have a defensible case study on cost-driven platform evolution. The mentoring responsibility (team growing from 6 to 8) introduces team lead experience without a full management pivot, which is strategically useful for a candidate who may want Staff or Principal IC tracks. DataCore's position at the intersection of ETL, governance, and real-time analytics also keeps options open across three adjacent markets.

## Red Flags

- **Series B execution risk** is the only meaningful flag. DataCore is well-funded and has a real customer base (500+ deployments, named customers including Shopify and Notion), but Series B is still early enough that product-market fit can shift. This is standard startup risk, not a disqualifying signal.
- **Weekly chaos engineering** is listed as part of the testing culture. This is actually a positive signal for a high-rigor engineering organization, but it implies a team that operates at sustained high intensity. Confirm in screen that work-life balance during non-on-call weeks is healthy.
- No red flags on the posting itself — see Legitimacy Assessment.

## CV Tailoring Suggestions

1. Retitle the current role's governance work from compliance-specific language (e.g., "fintech RLS") to platform-neutral framing: "multi-tenant access control and PII governance at scale." DataCore's customer base is not fintech-specific, and the expertise should read across verticals.
2. Elevate the Spark optimization case study from current role into a lead bullet with a concrete cost or latency metric. DataCore's P99 target (200ms → 50ms) signals they value measurable outcomes, not just "I worked with Spark."
3. Surface the Snowflake cost management work explicitly — this is the cost optimization narrative that DataCore is running with their Polars/Arrow evaluation. Frame it as a total cost of ownership analysis, not just a tuning exercise.
4. Add a line about the dbt experience from the retail analytics SaaS role, even in passing. DataCore's stack is listed as Python + Scala + SQL, and dbt experience signals fluency in the modern data stack idiom.
5. If any public contribution (blog post, talk, OSS issue) exists on data infrastructure topics, add it. The JD's nice-to-haves lean heavily on OSS and published work, and even a single public artifact in this space improves signal.

## Interview Probability

**High.** The candidate meets all core requirements with depth — years of experience, at least three of the four required languages (Python, Scala, SQL), and direct experience with two of the required warehouse/compute platforms (Spark, Snowflake). The Databricks gap is real but will not disqualify at the phone screen stage; it will surface in the take-home architecture challenge. The 85% test coverage culture and weekly chaos engineering are green flags for a technically rigorous interview loop — come prepared for system design on large-scale distributed processing and on a cost optimization scenario.

## Recommendation

**Apply immediately.** This role is a near-exact fit on scope, stack, and compensation, with the only substantive gap (Databricks hands-on) being shallow and partially moot given DataCore's active platform evaluation. The legitimacy signals are exceptional for a Series B posting, and the hiring timeline (April 15 deadline) means there is no time to delay.

---

## 10-Dimension Scores

| # | Dimension | Score | Weight | Contribution |
|---|-----------|-------|--------|--------------|
| 1 | Role & Responsibility Match | 5.0 | 20% | 1.00 |
| 2 | Skills & Experience Alignment | 4.5 | 20% | 0.90 |
| 3 | Seniority & Level Fit | 5.0 | 10% | 0.50 |
| 4 | Compensation vs. Market | 5.0 | 10% | 0.50 |
| 5 | Growth & Advancement Potential | 4.5 | 10% | 0.45 |
| 6 | Company Strength & Stability | 4.0 | 10% | 0.40 |
| 7 | Culture & Values Signals | 4.5 | 8% | 0.36 |
| 8 | Remote / Location Fit | 4.5 | 5% | 0.23 |
| 9 | Hiring Signal Quality | 5.0 | 4% | 0.20 |
| 10 | Strategic Career Value | 4.5 | 3% | 0.14 |
| | **Weighted Total** | | | **4.68** |

*Dimension 6 reflects standard Series B execution variance — DataCore's Sequoia/Gradient backing and named customer traction (Shopify, Notion) push this above 3.5 despite early-stage risk. Dimension 8 scores 4.5 rather than 5 because the twice-weekly PST sync and optional SF hybrid requirement impose a minor scheduling constraint for a non-PST candidate, though both are within stated tolerance.*

---

## Legitimacy Assessment

**Tier: Verified**

- Posting age: 3 days (April 12 posting, evaluated April 15) — active hiring window, no staleness concern ✓
- Requirement realism: 8–10 core skills, 8+ year floor with legitimate OSS/paper alternative — realistic and well-calibrated for senior IC ✓
- Specificity: Named team (Core Platform Engineering), named manager (Sarah Chen, VP Engineering), named customers, specific P99 target (200ms → 50ms), explicit hiring timeline with dates ✓
- Company hiring signals: April 2026 Series B from Sequoia and Gradient Ventures confirmed; Glassdoor 4.6/5 across 120 reviews; no layoff signals ✓
- Duplicate detection: Custom-written JD; not boilerplate; sourced from company careers page; specific architectural decisions (Spark → DuckDB, Polars/Arrow evaluation) are unique to this role ✓

All five legitimacy signals pass. This is a genuine, well-run open req with active headcount and a real hiring timeline.

---

*This evaluation was generated by an AI model and reflects pattern-matching against the provided JD and CV. It may not capture context only a human would know — use it as one input to your decision, not the decision itself.*
