---
type: eval
company: "TechVenture Solutions Inc."
role: "Data Scientist (Mid-Level)"
grade: D
score: 2.03
status: Evaluating
outcome: Pending
date: 2026-04-15
location: "Remote (United States)"
compensation: "Not disclosed"
legitimacy: Likely Ghost
model: claude-sonnet-4-6
sources: ["Indeed (primary)", "LinkedIn", "ZipRecruiter", "Dice — verbatim duplicate across all four"]
notes: "Skip — fundamental role mismatch (platform engineer vs. data scientist) and Likely Ghost posting with five independent red flags."
---

<!-- Fictional example. "TechVenture Solutions Inc." and every detail below are illustrative only. -->

> **REFERENCE OUTPUT — poor-fit eval (ghost-job legitimacy red flags).** This artifact is a regression anchor for Mode 1 on `tests/fixtures/jd_ghost_job.md`. If a Mode 1 change causes substantive (not formatting) drift on this fixture — especially on how the gate-pass rule or Likely-Ghost classification is surfaced — escalate before merging. Update this golden in the same PR with a CHANGELOG note, or revert the change. See [`README.md`](README.md) for the workflow.

# TechVenture Solutions Inc. — Data Scientist (Mid-Level)
**Grade: D  |  Score: 2.03/5  |  Legitimacy: Likely Ghost**

---

## Summary

This is a data science role — modeling, ML frameworks, statistical inference — and the candidate is a data platform engineer. Those are adjacent disciplines that share infrastructure vocabulary, but the core day-to-day work is fundamentally different. The JD's required stack (TensorFlow, PyTorch, Keras, XGBoost, LightGBM, CatBoost) does not appear anywhere in the candidate's CV, and no amount of reframing changes that gap. Compounding the fit problem: the posting itself exhibits five independent ghost-job signals, including 70+ days of staleness, verbatim duplication across four job boards, and 25+ required skills for a nominal "mid-level" title. There is no basis to invest time here.

## CV Match

**Partial infrastructure overlap (not enough):**
- Snowflake and dbt experience from the retail analytics SaaS role (2019–2021) appear in the JD's skill list — but as infrastructure tooling in a platform context, not as a data scientist's analytical tooling
- Spark cluster optimization is listed in the JD requirements; candidate has it, but again in a cost/performance platform role
- SQL is universal and present

**Core gaps — not bridgeable at application stage:**
- No production ML modeling experience of any kind. The JD requires hands-on TensorFlow, PyTorch, Keras, XGBoost, LightGBM, and CatBoost. None of these appear in the CV.
- No statistical modeling, experimentation design, or inference work
- No published or deployed predictive models
- No R, Scala, or Hive experience

The overlap is real but structural: a platform engineer who has supported data scientists is not the same as a data scientist. Surface keyword matches (Snowflake, Spark, SQL) will not survive a technical screen.

**Story bank check:** No relevant story candidates to suggest — the competency gaps are in modeling, not tooling presentation.

## Level & Seniority

The posting is internally inconsistent: it labels the role "mid-level" while requiring 5–10 years of experience and 25+ technologies. That is a senior or staff-level requirements profile misclassified at hire. Candidate has 9 years total, which falls in range — but the seniority question is moot when role fit is this misaligned.

## Compensation

Not disclosed. For a role of this stated scope — 5–10 years, 25+ skills, mid-level label — market data scientist comp in a fully remote US role typically runs $130K–$175K base depending on industry. The candidate's floor is $190K. Even if the role were a fit, the compensation signals here (no range, generic "competitive salary" language) are not encouraging. Likely below floor.

## Growth & Strategic Value

This role would not advance a data platform engineering career. Pivoting into data science at this stage would mean taking a technical step sideways (or back) in a domain where the candidate has no production history. The platform engineering track — Staff engineer, Principal, Head of Data Platform — is the higher-value trajectory. Even if the candidate were interested in a pivot, this particular posting is not a credible vehicle for it.

## Red Flags

- **70-day-old posting with no refresh.** Active requisitions are typically updated or re-posted within 30 days. This one has not been touched since February 5, 2026.
- **25+ required skills for "mid-level."** No real mid-level data scientist role requires the full modeling + cloud + DevOps + BI stack simultaneously. This is either an unfilled senior/staff req mislabeled, or a template dump.
- **Zero specificity.** No team name, no reporting chain, no product area, no business context. "Work with data. Develop models. Improve processes." is not a job description.
- **Verbatim duplication across boards.** Identical text — same formatting, same bullet phrasing — confirmed on Indeed, LinkedIn, ZipRecruiter, and Dice without attribution to a specific staffing agency.
- **No compensation disclosed.** Legitimate data science roles at this experience level routinely include a range, especially in remote postings where geography-based negotiation is limited.

## Legitimacy Warning

**Classification: Likely Ghost** (5 of 5 legitimacy signals triggered — threshold is 3+)

| Signal | Status | Detail |
|--------|--------|--------|
| Posting age | FAIL | Posted February 5, 2026; evaluated April 15, 2026 — 69 days, no refresh |
| Requirement realism | FAIL | 25+ required skills for a "mid-level" title; 5–10 years experience also listed |
| Specificity | FAIL | No team, no manager, no product, no business unit named anywhere in JD |
| Duplicate detection | FAIL | Verbatim text confirmed on 4 job boards with no agency attribution |
| Compensation transparency | FAIL | No range, no band, no "see job posting" reference — entirely absent |

Recommendation: Do not invest application effort. If a recruiter inbound from TechVenture Solutions Inc. arrives referencing this role, treat it as a sourcing touch, not a real pipeline entry.

## CV Tailoring Suggestions

Not applicable given recommendation to skip. If the candidate were pursuing a deliberate data science pivot — which would require significant upskilling before application — the priority would be adding at least one production ML project (even a personal project using XGBoost or PyTorch) before targeting any data scientist JD. Applying to this role with the current CV would not survive a technical screen regardless of how it is framed.

## Interview Probability

**Near-zero.** The role requires a production ML modeling background the candidate does not have. Recruiter screens at competent data science teams filter on this explicitly. The ghost-job classification compounds this: if the role is not a real active hire, there is no screen to reach.

## Recommendation

**Skip.** The gate-pass rule applies: both Dimension 1 (Role & Responsibility Match, score 2) and Dimension 2 (Skills & Experience Alignment, score 2) score at or below the gate-pass threshold of 2. Per the Mode 1 specification, a score of 2 or below on either gate-pass dimension caps the final grade at D regardless of the weighted average — strong scores in other dimensions cannot compensate for a broken fit foundation. The weighted average (2.03) independently confirms the D band. Legitimacy is a separate and independent failure: five ghost-job signals make this posting a poor use of application effort even if the role were a fit.

---

## 10-Dimension Scores

| # | Dimension | Score | Weight | Contribution |
|---|-----------|-------|--------|--------------|
| 1 | Role & Responsibility Match | 2 | 20% | 0.40 |
| 2 | Skills & Experience Alignment | 2 | 20% | 0.40 |
| 3 | Seniority & Level Fit | 3 | 10% | 0.30 |
| 4 | Compensation vs. Market | 2 | 10% | 0.20 |
| 5 | Growth & Advancement Potential | 2 | 10% | 0.20 |
| 6 | Company Strength & Stability | 1 | 10% | 0.10 |
| 7 | Culture & Values Signals | 2 | 8% | 0.16 |
| 8 | Remote / Location Fit | 4 | 5% | 0.20 |
| 9 | Hiring Signal Quality | 1 | 4% | 0.04 |
| 10 | Strategic Career Value | 1 | 3% | 0.03 |
| | **Weighted Total** | | | **2.03** |

*Gate-pass rule applied: Dimension 1 (Role Match) = 2 and Dimension 2 (Skills Alignment) = 2 — both at or below the gate-pass threshold. Final grade is capped at D regardless of weighted average. The weighted average of 2.03 independently places this in the D band (2.00–2.99), so no score inflation occurred even without the cap.*

---

## Legitimacy Assessment

**Tier: Likely Ghost**

- **Posting age:** FAIL. Posted February 5, 2026. Evaluated April 15, 2026. 69 days old with no update date and no re-activation. Active requisitions are typically refreshed within 30 days. This crosses the 60-day archival threshold by a full work-week margin.
- **Requirement realism:** FAIL. 25+ listed required skills for a role titled "mid-level." The JD simultaneously requires 5–10 years of experience — a senior-to-staff experience range. This is either a template pasted without editing or a role that has been open long enough that requirements have accumulated across multiple hiring managers' wish lists.
- **Specificity:** FAIL. Zero unique organizational details. No team name, no reporting structure, no product line, no geographic center of gravity beyond "United States," no business context ("Work with data. Develop models."). This level of vagueness does not appear in genuine job postings from companies with active data science hiring.
- **Duplicate detection:** FAIL. JD text confirmed verbatim on Indeed, LinkedIn, ZipRecruiter, and Dice — four boards, same formatting, same bullet structure, no staffing agency attribution. Legitimate company postings cross-posted this way typically carry ATS source tracking or slight reformatting per board. Identical verbatim copy across four boards is a staffing aggregator or ghost-job pattern.
- **Compensation transparency:** FAIL. No range, no band, no reference to where a range might be found. For a remote US data science role at 5–10 years experience, omitting compensation entirely is a strong filter-suppression signal — either the role does not exist or the offer is expected to disappoint.

**Verdict:** 5 of 5 legitimacy signals fail. Classification is Likely Ghost. No legitimacy check passed.

---

*This evaluation was generated by an AI model and reflects pattern-matching against the provided JD and CV. It may not capture context only a human would know — use it as one input to your decision, not the decision itself.*
