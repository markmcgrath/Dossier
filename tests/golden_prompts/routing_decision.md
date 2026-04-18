# Routing Decision — Phase 2 Gate

**Date:** 2026-04-17  
**Decision:** ❌ **Do not proceed with Phase 3 skill split at this time**  
**Recommendation:** Stay monolithic. Implement targeted description improvements identified by this experiment. Revisit split after Claude Code adds cross-skill coordination primitives or after compound-request behavior is empirically validated.

---

## Decision Criteria (from plan 11, section 2.4)

> **Proceed if:** Multi-skill routing is equal or better on 90%+ of prompts AND no critical regression on negative triggers (false positives).
>
> **Do not proceed if:** Multi-skill routing degrades on >10% of prompts OR introduces false positives on negative triggers.

---

## Results Against Criteria

| Criterion | Threshold | Result | Pass? |
|-----------|-----------|--------|-------|
| Routing equal or better on 90%+ of prompts | ≥ 40.5/45 prompts | **37/45 same or better, 8 worse (82%)** | ❌ Fails |
| No critical regression on negative triggers | 0 false positives introduced | 0 new false positives in split | ✓ Passes |
| Precision ≥ 0.90 | 0.90 | Monolithic: 0.949 / Split: 0.97 | ✓ Both pass |
| Recall ≥ 0.90 | 0.90 | Both: 1.00 | ✓ Both pass |
| Injection safe | T-038 pass | Both pass | ✓ Both pass |

**Critical failure:** 8 of 45 prompts (17.8%) have worse routing quality in the multi-skill variant. This exceeds the 10% degradation threshold.

---

## What the Split Gets Right

The split delivers four genuine improvements:

1. **Better description coverage for three undercovered modes** — "tailor my CV" (Mode 11), "health check" (Mode 0), and "calibration" (Mode 13) are now explicit in skill descriptions, not buried in SKILL.md body text. These are real gaps in the monolithic description that should be fixed regardless of the split decision.

2. **Reduced false positive risk on adjacent topics** — The monolithic description's "job-search related" framing is broad enough that analytics questions without job context (star schema explanation, dbt learning path) could trigger incorrectly. Narrower descriptions reduce this risk.

3. **Cleaner single-intent triggers** — For unambiguous single-mode requests, the split is equally good and occasionally cleaner (inbox triage, calendar scheduling land in exclusive homes).

4. **Marginally better precision** — 0.97 vs. 0.949 baseline, because the split descriptions are tighter and less likely to over-trigger.

---

## What the Split Breaks

The split fails on compound and sequential requests, which represent a disproportionately important class of real-world job-search workflows:

| Prompt | Monolithic | Split |
|--------|-----------|-------|
| T-039: Recruiter email → eval + draft response | One context, two modes, seamless | Two skills, requires re-prompt or model offers second skill |
| T-040: Interview scheduled → prep + calendar block | One context, modes 3 + 10 | dossier-prep + dossier-pipeline, two turns |
| T-042: Eval JD + cover letter if B+ | One context, conditional branch | Two skills, conditional state doesn't transfer |
| T-045: Should I follow up? → inbox check + follow-up draft | Mode 9 → Mode 5, one context | dossier-pipeline + dossier-packet, handoff required |
| T-026: What's my next step? (ambiguous) | Model resolves with full context | Two skills partially match, clarification needed |

**The compound-request problem is structural, not cosmetic.** These workflows are exactly what Dossier is for — multi-step job-search sequences where the output of one step feeds the next. The monolithic skill's single context window is a structural advantage here. The split fragments these flows.

**The root cause** is what the architecture document (and plan 11, G2) already identified: Claude's public documentation supports description-based skill matching, but does NOT document a first-class inter-skill call primitive. In practice, a user has to re-prompt, or the model has to explicitly offer to engage a second skill. That's friction on the most valuable use cases.

---

## What Changes Now (Immediate)

The experiment identified three concrete improvements to the monolithic description that should be implemented immediately, regardless of the split decision:

### Fix 1: Add "tailor my CV" to description

The monolithic description doesn't mention CV tailoring. Mode 11 is only reachable via body text. Add:

> "Also trigger for CV tailoring requests ('tailor my CV for this role')..."

### Fix 2: Add "health check" and "calibration" to description

Mode 0 and Mode 13 have no description coverage. Add:

> "...vault health checks, and scoring calibration reviews."

### Fix 3: Tighten "job-search related" framing

The current description opens broadly with "ALWAYS use this skill for anything job-search related." This is correct but could over-trigger on analytics topics without application context. The false positive risk is low now (one user, one domain), but will matter for public release.

Proposed addition at the end of the description:

> "Only trigger when there is a clear job application, offer, interview, or outreach context. Do not trigger for general technical questions (data modeling, tool learning, etc.) without that context."

---

## Recommended Description Update

The updated SKILL.md description (unchanged mode routing, only description modified):

```
ALWAYS use this skill for anything job-search related. This includes: evaluating a job
description or offer (A–F grade + structured report saved to your vault), searching for jobs
on Indeed or Dice, preparing for a specific interview, researching a company before applying
or interviewing, and drafting LinkedIn outreach messages. Trigger immediately when the user
pastes or describes a job description, mentions an upcoming interview, asks "should I apply",
"is this a good fit", "find me jobs", "search for roles", "research [company]", "tailor my CV",
"health check", "calibration report", or wants to message a recruiter or hiring manager.
Also trigger for offer comparisons, phone screen prep, cover letters, salary negotiation,
triaging recruiter emails, drafting follow-ups or thank-you notes, syncing application statuses
to tracker, scheduling prep blocks or follow-up reminders, and any request to act on LinkedIn
directly (search jobs or people, send InMail, scan recruiter inbox, check a profile).
Only trigger when there is a clear job application, offer, interview, or outreach context.
Do not attempt these tasks without this skill.
```

**Net additions:** "tailor my CV", "health check", "calibration report" — explicitly covered. Final negative-scope sentence added.

---

## Conditions for Revisiting the Split

The split should be reconsidered when one or more of the following is true:

1. **Claude Code documents a cross-skill call primitive** — if skills can explicitly hand off to another skill or the model is documented to coordinate multi-skill sequences without user re-prompting, the compound-request problem is solved architecturally.

2. **Compound request behavior is empirically validated** — if live testing with real Claude sessions shows that the model naturally sequences skills on compound requests (e.g., "eval this and draft a response" triggers evaluate, completes, then automatically engages packet), the structural concern is overstated.

3. **Vault size grows to 20+ concurrent active skills** — at that scale, the monolithic description's broad coverage becomes a matching liability. A split would improve signal-to-noise even if compound requests add friction.

4. **A specific mode is reliably missed** — if Mode 0, 11, or 13 show empirical miss rates even after the description improvements above, that's evidence that description coverage matters more than assumed and a narrower skill with exclusive coverage would help.

---

## Files Produced

| File | Purpose |
|------|---------|
| `routing_test_set.md` | 45-prompt golden set covering all categories |
| `baseline_results.md` | Monolithic skill routing analysis (precision: 0.949, recall: 1.00) |
| `multiskill_prototype/skill_descriptions.md` | Five candidate skill descriptions for the split |
| `multiskill_results.md` | Multi-skill routing analysis (precision: 0.97, recall: 1.00, 8 degradations) |
| `routing_decision.md` | This document — gate decision and immediate remediation |

---

## Next Step

Apply the description improvements to `skill/SKILL.md` and sync to open-source. Then update the plan 11 Phase 2 execution log and mark Phase 2 complete.
