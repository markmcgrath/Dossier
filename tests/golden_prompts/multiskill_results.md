# Multi-Skill Routing Results

**Date:** 2026-04-17  
**Variant:** Five-skill split — dossier-evaluate / dossier-search / dossier-packet / dossier-prep / dossier-pipeline  
**Method:** Analytical evaluation against prototype skill descriptions in `multiskill_prototype/skill_descriptions.md`  
**Baseline for comparison:** `baseline_results.md`

**Key question:** Does splitting into five focused skills improve, degrade, or leave unchanged the routing precision and recall compared to the monolithic baseline?

---

## Results Table

`skill_triggered` = which of the five skills the description match would select  
`correct_skill` = does it match the expected skill from the test set?  
`mode_correct` = once the right skill triggers, would mode selection be correct?  
`vs_baseline` = Better / Same / Worse / New Issue compared to monolithic

| ID | Prompt summary | skill_triggered | correct_skill | mode_correct | injection_safe | vs_baseline | notes |
|----|---------------|-----------------|---------------|--------------|----------------|-------------|-------|
| T-001 | Evaluate JD [Analytics Eng, Databricks] | dossier-evaluate | yes | yes | n/a | Same | "evaluate this JD" maps to evaluate description verbatim. |
| T-002 | Should I apply to this role? BI Architect | dossier-evaluate | yes | yes | n/a | Same | "should I apply" verbatim in description. |
| T-003 | Evaluate this posting [URL] | dossier-evaluate | yes | yes | n/a | Same | JD URL = evaluate trigger. |
| T-004 | Search AE roles on Indeed and Dice | dossier-search | yes | yes | n/a | Same | "search for roles" in search description. |
| T-005 | Find me jobs as data model architect | dossier-search | yes | yes | n/a | Same | "find me jobs" verbatim. |
| T-006 | Scan my target companies | dossier-search | yes | yes | n/a | Same | "scan my target companies" verbatim. |
| T-007 | Phone screen at dbt Labs, prep me | dossier-prep | yes | yes | n/a | Same | "prep me for my interview" verbatim. |
| T-008 | Final loop at Databricks, prep me | dossier-prep | yes | yes | n/a | Same | "I have an interview at [company]" in description. |
| T-009 | Research Snowflake before interview | dossier-prep | yes | yes | n/a | Same | "research [company]" verbatim. |
| T-010 | Find head of data eng at Databricks, draft LinkedIn | **dossier-packet** (find + draft) OR dossier-prep (LinkedIn) | **partial** | yes | n/a | **New Issue** | Split creates ambiguity: "find [person]" matches dossier-packet ("find contact info") AND dossier-prep ("search LinkedIn for [person]"). Which skill triggers? Claude must pick one — both descriptions partially match. |
| T-011 | Draft LinkedIn follow-up to hiring manager | dossier-packet | yes | yes | n/a | Same | "draft a LinkedIn message" in packet description. |
| T-012 | Write cover letter for Fivetran role | dossier-packet | yes | yes | n/a | Same | "write a cover letter" verbatim. |
| T-013 | Got offer from Databricks, $155k, how to negotiate | dossier-evaluate | yes | yes | n/a | Same | "salary negotiation" + "offer" in evaluate description. |
| T-014 | What should I be asking for? 12 years exp | dossier-evaluate | yes | yes | n/a | Same | "how much should I ask for" verbatim in evaluate. |
| T-015 | Search LinkedIn for technical recruiters at dbt Labs | dossier-prep | yes | yes | n/a | Same | "search LinkedIn for" verbatim in prep description. |
| T-016 | What recruiters have reached out this week? | dossier-pipeline | yes | yes | n/a | **Better** | "what recruiters have reached out" verbatim and exclusive in pipeline description. Monolithic had to match from broader description; split is more precise. |
| T-017 | Create prep block for Snowflake interview | dossier-pipeline | yes | yes | n/a | **Better** | "schedule a prep block" verbatim and exclusive in pipeline. Cleaner match than monolithic. |
| T-018 | Tailor my CV for the Databricks role | dossier-packet | yes | yes | n/a | **Better** | "tailor my CV" verbatim in packet description. Monolithic had weak description coverage; split has explicit coverage. |
| T-019 | Evaluate 5 job listings, rank them | dossier-search | yes | yes | n/a | Same | "batch-evaluate multiple job descriptions" in search description. |
| T-020 | Run a health check on my vault | dossier-pipeline | yes | yes | n/a | **Better** | "health check" verbatim in pipeline description. Monolithic had no description coverage; depended on SKILL.md body. |
| T-021 | Is this role worth applying to? | dossier-evaluate | yes | yes | n/a | Same | "is this a good fit" in evaluate description. |
| T-022 | Give me a quick read on this posting [JD pasted] | dossier-evaluate | yes | yes | n/a | Same | JD paste + "evaluate" context. |
| T-023 | What AE roles are hiring that suit my background? | dossier-search | yes | yes | n/a | Same | "search for roles" matches. |
| T-024 | Nervous about Fivetran call Monday | dossier-prep | yes | yes | n/a | Same | "I have an interview at [company]" covers this indirectly. Prep description is slightly less explicit than monolithic on anxiety framing, but "prep me for my interview" still matches. |
| T-025 | Tell me about Coalesce before I decide to apply | dossier-prep | yes | yes | n/a | Same | "research [company]" verbatim. |
| T-026 | What to do next? Applied 3 places, no response | dossier-pipeline (follow-up) OR dossier-packet (outreach) | partial | acceptable | n/a | **Slightly worse** | Monolithic: full context resolves ambiguity internally. Split: "drafting follow-ups" is in pipeline; "draft an outreach" is in packet. Two skills partially match. Model must clarify or pick one — adds friction where monolithic was seamless. |
| T-027 | They came in at $145k, I wanted $165k | dossier-evaluate | yes | yes | n/a | Same | "is this a fair offer" + "counter-offer" in evaluate. |
| T-028 | Evaluating lots of roles, am I accurate? | dossier-evaluate | yes | yes | n/a | **Better** | "how accurate their past evaluations have been" + "scoring calibration" now explicit in evaluate description. Monolithic had no description coverage for Mode 13. |
| T-029 | Where do things stand with my job search? | dossier-pipeline | yes | acceptable | n/a | Same | "state of their job search pipeline" in pipeline. |
| T-030 | Pulled 8 jobs from LinkedIn, which worth pursuing | dossier-search | yes | yes | n/a | Same | "multiple JDs to compare and prioritize" in search. |
| T-031 | Write Python function, CSV | **NONE** | yes | n/a | n/a | Same | No job context. No skill matches. |
| T-032 | Star schema vs. snowflake schema, what's the difference | **NONE** | yes | n/a | n/a | Same | No job context. Split skills are more narrowly scoped — this is *less* likely to false-positive than monolithic. **Marginal improvement.** |
| T-033 | Fix document formatting | **NONE** | yes | n/a | n/a | Same | No match. |
| T-034 | Block hour for dentist appointment | **NONE** | yes | n/a | n/a | Same | "schedule" is in pipeline description, but "dentist" has no job-search context. Calendar without job context shouldn't match. |
| T-035 | Check inbox for unread emails | **NONE** | yes | n/a | n/a | Same | "recruiter emails" is specific — generic inbox shouldn't match. |
| T-036 | What should I invest my savings in? | **NONE** | yes | n/a | n/a | Same | Out of scope for all skills. |
| T-037 | How do I learn dbt? | **NONE** | yes | n/a | n/a | **Marginal improvement** | Monolithic had false-positive risk from broad "job-search related" phrasing. Split descriptions are tighter; "dbt" alone doesn't match any trigger phrase. Less risk of over-triggering. |
| T-038 | Evaluate JD with embedded injection | dossier-evaluate | yes | yes | **yes** | Same | Evaluate triggers on JD content. Trust boundary text in each skill SKILL.md prevents injection. |
| T-039 | Recruiter email about Coalesce, eval + draft response | dossier-evaluate then dossier-packet | yes | yes | n/a | **Slightly worse** | Monolithic: one skill, both modes, single context. Split: requires evaluate to complete, then user re-prompts (or the model offers) to engage packet skill. Cross-skill compound requests add a step. |
| T-040 | Interview at Fivetran Tuesday, prep + calendar block | dossier-prep then dossier-pipeline | yes | yes | n/a | **Slightly worse** | Same cross-skill compound issue. Prep and calendar are in different skills. Monolithic handles this in one turn. |
| T-041 | Everything I need to know about Snowflake before interview | dossier-prep | yes | acceptable | n/a | Same | Both Mode 4 and Mode 3 are in dossier-prep, so no cross-skill issue. Actually advantageous — the compound stays within one skill. |
| T-042 | JD for Lead Data Modeler at Coalesce, eval + cover letter if B+ | dossier-evaluate then dossier-packet | yes | yes | n/a | **Slightly worse** | Conditional compound across two skills. Monolithic handles the conditional in one context; split requires a handoff. |
| T-043 | They offered $148k, is this a good offer? | dossier-evaluate | yes | yes | n/a | Same | "is this a fair offer" in evaluate. No confusion with Mode 1. |
| T-044 | Draft something to send to hiring manager at dbt Labs | dossier-packet | yes | yes | n/a | Same | "draft a LinkedIn message" + "hiring manager" in packet. |
| T-045 | Applied to Databricks 12 days ago, follow up? | dossier-pipeline (check) then dossier-packet (draft) | partial | acceptable | n/a | **Slightly worse** | "drafting follow-ups" is in pipeline; "draft an outreach" is in packet. The check (Mode 9) and the draft (Mode 5) land in different skills. Cross-skill coordination required. |

---

## Multi-Skill Summary

| Metric | Monolithic | Multi-Skill | Delta |
|--------|-----------|-------------|-------|
| Total prompts | 45 | 45 | — |
| Correctly triggered (positive cases) | 37 | 37 | 0 |
| Ambiguous skill selection (partial) | 0 | 4 (T-010, T-026, T-039–T-045) | +4 issues |
| False positive risk | 2 | 0–1 (marginally better) | -1 |
| Mode correct/acceptable | 37 | 37 | 0 |
| Injection safe | Yes | Yes | Same |
| Cross-skill compound degradations | 0 | 5 (T-039, T-040, T-042, T-045, T-026) | +5 |
| Description coverage improvements | 0 | 4 (T-018, T-020, T-028, T-016) | +4 |

### Precision

- True positives (correctly triggered, correct skill): 33 (37 minus 4 partial)
- False positives: 0–1
- **Multi-skill precision: ~0.97** (improved over 0.949 due to fewer false positive risks)

### Recall

- True positives: 37 (all intended triggers still fire — just sometimes across two skills)
- False negatives: 0
- **Multi-skill recall: 1.00** (same as monolithic)

### Net routing quality change

| Category | Better | Same | Worse |
|----------|--------|------|-------|
| Direct (20) | 4 | 15 | 1 (T-010 new ambiguity) |
| Indirect (10) | 0 | 8 | 2 (T-026 slightly, T-029 same) |
| Negative (8) | 2 | 6 | 0 |
| Ambiguous (7) | 1 (T-041 stays within one skill) | 1 | 5 (compound requests) |
| **Total** | **7** | **30** | **8** |

---

## Key Findings

### Where the split helps

1. **Cleaner description coverage for previously uncovered modes** (T-018, T-020, T-028): "tailor my CV," "health check," and "calibration" are now explicit trigger phrases in their skill descriptions. These were previously only covered by SKILL.md body text.

2. **Reduced false positive risk on adjacent topics** (T-032, T-037): Narrower skill descriptions make it less likely that a generic analytics question (star schema, learning dbt) triggers a job-search skill.

3. **Cleaner inbox and calendar triggers** (T-016, T-017): "What recruiters have reached out" and "schedule a prep block" have exclusive homes in dossier-pipeline. No competition.

### Where the split hurts

1. **Compound requests across skill boundaries degrade** (T-039, T-040, T-042, T-045): The most natural compound job-search requests — "eval + draft response", "prep + calendar", "eval + cover letter if B+" — require two skills to coordinate. In the monolithic variant, the model sequences modes in one context. In the split, the model must complete one skill's task, then re-engage the second skill. This costs at least one extra turn and risks context loss between skills.

2. **One genuine new ambiguity** (T-010): "Find [contact] at Databricks and draft a LinkedIn message" partially matches both dossier-packet (contact finding + message draft) and dossier-prep (LinkedIn people search). Both descriptions partially cover it. The monolithic skill resolves this internally as a single Mode 5 workflow.

3. **Follow-up sequencing is split** (T-026, T-045): "What should I do next, no response" maps to both pipeline (inbox check) and packet (follow-up draft). The monolithic skill reads the vault state and sequences appropriately in one context. The split requires the model to know both skills are needed — which isn't obvious from a single user prompt.
