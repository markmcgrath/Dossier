---
type: eval
company: "DataCore Systems"
role: "Senior Data Platform Engineer"
grade: A
score: 4.67
status: Evaluating
outcome: Pending
date: 2026-04-15
location: "Remote (PST/PT timezone required, optional SF hybrid)"
compensation: "$200,000–$240,000 base + $30K signing + 0.15–0.25% equity"
legitimacy: Verified
model: claude-sonnet-4-6
sources: ["jd_strong_fit.md (fixture)", "DataCore careers page (cited in JD)", "Series B announcement April 2026 — Sequoia + Gradient Ventures (cited in JD)", "Glassdoor 4.6/5, 120 reviews (cited in JD)"]
notes: "Near-exact fit on platform engineering scope, Spark/Snowflake stack, and multi-tenant governance. Databricks gap is shallow and partially moot given DataCore's active Polars/Arrow evaluation."
---

# DataCore Systems — Senior Data Platform Engineer
**Grade: A | Score: 4.67/5 | Legitimacy: Verified**

---

## Summary

DataCore Systems is a 150-person Series B data infrastructure company ($50M raised April 2026 from Sequoia and Gradient Ventures) building ETL, governance, and real-time analytics for 500+ mid-market customers including Shopify and Notion. The Senior Data Platform Engineer role joins a 6-person Core Platform team under VP Engineering Sarah Chen with P0 ownership over infrastructure backing those 500+ deployments. The technical scope — Spark-based processing, multi-tenant governance (lineage, PII detection, access controls), and an active Polars/Arrow cost-optimization evaluation — maps directly onto the candidate's last four years of work. Comp is above floor, legitimacy is exceptional, and the only substantive gap (Databricks hands-on) is shallow given DataCore's stated openness to migrating off it.

## CV Match

**Strong alignment:**
- 9 years building data platforms at scale clears the 8+ year floor with margin; the current Platform Lead role at a logistics fintech is direct evidence of P0 ownership at comparable deployment scale.
- Snowflake + dbt experience from the retail analytics SaaS role (2019–2021) is in-stack for DataCore's Snowflake layer; warehouse cost management work covers the same optimization problem driving the Polars/Arrow evaluation.
- Multi-tenant governance with RLS from the fintech compliance environment is the closest available analog to DataCore's lineage tracking, PII detection, and access controls — a near-exact reframe, not a stretch.
- Spark cluster optimization at the current role is the foundation of DataCore's existing processing infrastructure; the Spark-to-DuckDB routing pattern (sub-100MB tables) is a judgment call the candidate has navigated.
- Cross-functional collaboration with analytics, ML, and backend teams matches the mentoring + architectural decision-making framing of the role.

**Gaps and mitigations:**
- No prior Databricks hands-on. Databricks is managed Spark with Delta Lake — the candidate knows the substrate. Estimated ramp: ~4 weeks on Databricks-specific APIs, Delta Lake versioning, and Unity Catalog governance. Mitigating factor: DataCore is actively evaluating replacements, so Databricks depth matters less at the 12-month mark than on day one.
- No Polars or Arrow hands-on, but these are nice-to-haves and the candidate's warehouse cost work provides the economic intuition behind the evaluation.

**Story bank check:** A quantified Spark-optimization story tied to a P99 latency outcome would directly serve DataCore's 200ms → 50ms target — worth adding to `stories.md` if not already present.

## Level & Seniority

Right level. Senior IC on a 6-person team at a 150-person Series B is squarely where a 9-year platform engineer operates — not a step down, not an overreach. The JD positions this explicitly as a non-junior P0-ownership role and signals team growth from 6 to 8, opening a natural Staff-level track within 18–24 months. The $240K base ceiling is consistent with senior IC market rates in SFO.

## Compensation

**Above floor.** $200–240K base clears the candidate's $190K floor with comfortable margin. The $30K signing bonus covers transition friction. Equity (0.15–0.25%, 4-year vest, 1-year cliff) is real Series B equity from a company with verifiable Sequoia/Gradient backing — at a 3–5x exit multiple, meaningful upside. 4% 401(k) match, 100% employee health premium coverage, and a $2K professional development budget are standard Series B benefits. Year-1 effective comp lands in the $215–255K range depending on base negotiation.

## Growth & Strategic Value

Owning P0 infrastructure across 500+ customer deployments is the kind of verifiable, high-stakes scope that strengthens a resume regardless of how the company exits. The Polars/Arrow evaluation is a genuine architectural decision — whoever leads that call will have a defensible cost-driven-platform-evolution case study. The team growth (6 → 8) introduces team-lead experience without forcing a management pivot, which keeps Staff and Principal IC tracks open. Position at the intersection of ETL, governance, and real-time analytics keeps options across three adjacent markets.

## Red Flags

- **Series B execution risk** is the only real flag. DataCore is well-funded with a real customer base, but Series B is still early enough that PMF can shift. Standard startup risk, not a disqualifier.
- **Weekly chaos engineering** signals a high-rigor engineering culture (positive), but also a sustained intensity that's worth probing in screen. Confirm work-life balance during non-on-call weeks.
- No red flags on the posting itself — see Legitimacy Assessment.

## Interview Probability

**High.** All core requirements are met with depth: 9 years experience, three of the four required languages (Python, Scala, SQL), two of the required compute/warehouse platforms (Spark, Snowflake). The Databricks gap won't disqualify at phone screen; it will surface in the take-home architecture challenge. The 85% coverage / chaos-engineering culture signals a technically rigorous loop — expect deep system design on distributed processing and a cost optimization scenario.

## Recommendation

**Apply immediately.** Near-exact fit on scope, stack, and compensation. The only substantive gap is shallow and partially moot. Legitimacy signals are exceptional. The April 15 deadline means no time to delay.

## CV Tailoring Suggestions

1. Retitle the current role's governance work from fintech-specific framing (e.g., "fintech RLS") to vertical-neutral language: "multi-tenant access control and PII governance at scale."
2. Elevate the Spark optimization work to a lead bullet with a concrete latency or cost metric — DataCore signals they value measurable outcomes (the 200ms → 50ms P99 target is in the JD).
3. Surface Snowflake cost management explicitly — this is the same total-cost-of-ownership narrative DataCore is running with Polars/Arrow. Frame as TCO analysis, not tuning.
4. Add the dbt experience from the retail analytics SaaS role even in passing — DataCore's stack signals modern-data-stack fluency.
5. If any public artifact (blog post, talk, OSS issue) exists on data infrastructure topics, surface it. The nice-to-haves lean on OSS and published work — even a single public artifact improves signal.

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
| 8 | Remote / Location Fit | 4.5 | 5% | 0.225 |
| 9 | Hiring Signal Quality | 5.0 | 4% | 0.20 |
| 10 | Strategic Career Value | 4.5 | 3% | 0.135 |
| | **Weighted Total** | | | **4.67** |

*Dim 6 reflects standard Series B execution variance — Sequoia/Gradient backing and named customer traction (Shopify, Notion) keep this above 3.5 despite early-stage risk. Dim 8 is 4.5 rather than 5 because the 2x/week PST sync and optional SF hybrid impose a minor scheduling constraint for non-PST candidates, within stated tolerance.*

---

## Legitimacy Assessment

**Tier: Verified**

- Posting age: 3 days (April 12 posted, April 15 evaluated) — active hiring window ✓
- Requirement realism: 8–10 core skills, 8+ year floor with OSS/paper alternative — well-calibrated for senior IC ✓
- Specificity: Named team (Core Platform Engineering), named manager (Sarah Chen, VP Engineering), named customers (Shopify, Notion), explicit P99 latency target, full hiring timeline with dates ✓
- Company hiring signals: April 2026 Series B confirmed in JD; Glassdoor 4.6/5 across 120 reviews; no layoff signals ✓
- Duplicate detection: Custom-written JD; architectural specifics (Spark → DuckDB, Polars/Arrow eval) are unique to this role ✓

All five legitimacy signals pass. Genuine, well-run open req with active headcount and a real hiring timeline.

---

*This evaluation was generated by an AI model and reflects pattern-matching against the provided JD and CV. It may not capture context only a human would know — use it as one input to your decision, not the decision itself.*
