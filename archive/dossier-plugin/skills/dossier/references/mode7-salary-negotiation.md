# Mode 7: Salary Negotiation — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User has received an offer, or is approaching the negotiation stage (verbal offer, recruiter discussing ranges, post-final-round). Also triggers on phrases like "how much should I ask for," "they offered X," "counter-offer," "is this a fair offer."

**What to do:**

Gather the inputs needed to negotiate from evidence, not vibes:

1. **The offer.** Base, bonus, equity, benefits, signing bonus, location/remote, start date, any other components.
2. **The role and level.** From Mode 1 if available, or ask directly.
3. **The user's current comp** (optional — don't push if they don't volunteer).
4. **User's walk-away line.** What's the floor where this stops being worth it?

Then gather market data in parallel:

- `WebSearch` for `"[Role Title]" salary "[Location or Remote]" 2026` and `levels.fyi "[Company]"` and `glassdoor "[Company]" salary "[Role]"`
- `WebSearch` for recent discussions: `"[Role]" salary reddit` or `"[Role]" negotiation blind`
- If the company is listed on Levels.fyi, pull the specific band for the level; if not, use comp at comparable companies at comparable stage/size

**Output the negotiation brief:**

```
# Negotiation Brief: [Company] — [Role]

## The Offer on the Table
[Clean breakdown of every component with dollar values]

## Market Context
[2–4 bullet points: what the market pays for this role/level/location,
 with sources. Call out whether the offer is below, at, or above band.]

## Leverage Assessment
[What working in the user's favor: competing offers, in-demand skills,
 time pressure on the company, late-stage in process. What's not:
 economic conditions, single offer in hand, junior-to-role.]

## Counter-Offer Recommendation
- **Target (ask for this):** $X base + $Y signing + [equity ask]
- **Acceptable (land here):** $X base + $Y signing
- **Walk-away (below this, decline):** $X base

## Counter-Offer Script
[Literal text the user can paste into email or say on a call. Keep it
 short: thank them, state the counter with a one-sentence rationale,
 leave room for them to respond.]

## Responses to Common Pushback
- "This is our best offer" → [script]
- "We don't negotiate" → [script]
- "The budget is fixed" → [script]
- "Can you come down?" → [script]

## Non-Comp Levers to Pull If Base Is Stuck
[List ALL of these individually — do not compress into a generic line. Evaluate each one:
 - **Signing bonus** — one-time cash; often easier to approve than raising the base band
 - **Accelerated performance review** — ask for a 6-month review instead of standard 12, with a defined raise trigger if targets are met
 - **Equity / RSU refresh** — if the company grants equity, ask for an above-band initial grant
 - **Remote flexibility** — if the role has any in-office requirement, negotiate frequency or geography
 - **Start date** — later start = more time to consider or exhaust other pipelines; earlier start = signals urgency on their side that you can leverage
 - **PTO / vacation bank** — one-time extra PTO days are a soft-dollar cost that HR can often approve when base is locked
 - **Title bump** — going from "Senior" to "Lead" or "Principal" costs nothing and matters for future comp anchoring
 - **Relocation / home office stipend** — one-time cost, often pre-approved in HR systems]

**Weak-leverage note:** When the user's position is weak (single offer, employment gap, deadline pressure), the Non-Comp Levers section becomes MORE important, not less. A negotiation that can't move base can often move two or three of the above. Always enumerate all of them — don't assume they're off the table just because leverage is low.

## What NOT to Do
[Common traps: naming a number first, accepting on the call, apologizing
 for asking, revealing current comp unless asked and beneficial, etc.]
```

**Principles to embed in the output:**

- Never negotiate against yourself. One counter, stated clearly, then silence.
- Always anchor with data. "Levels.fyi shows the band for this level is $X–$Y" beats "I was hoping for more."
- Keep everything in email if the user is nervous on calls. "Can I send a quick note tonight?" is a valid move.
- The ask is ALWAYS more than the target. Room to meet in the middle is the whole point.

Save to `negotiation-[company-slug]-[date].md` in the Dossier folder. Offer to draft the actual counter-offer email if the user is ready to send.

## Offer Comparison (multiple offers)

**Trigger:** Automatically invoked when the user mentions multiple offers OR when scanning the vault reveals 2+ eval files with `status: Offer` in frontmatter.

**What to do:**

Read all eval files with `status: Offer` from the `evals/` folder. If 2+ exist, and the user hasn't yet asked for a comparison, surface it proactively: "I see you have [N] offers. Want me to run a side-by-side comparison?"

If the user accepts or asks for a comparison directly:

1. **Pull compensation and role details** from each offer and related eval file. Flag incomplete data explicitly (e.g., "Equity details missing for Company B — comparison may be incomplete").

2. **Output structure:**

```
# Offer Comparison

## Compensation Table
| Company | Base | Bonus | Equity/RSU | Signing | Total Year 1 | Total Year 4 |
|---------|------|-------|-----------|---------|-------------|-------------|
| A | ... | ... | ... | ... | ... | ... |
| B | ... | ... | ... | ... | ... | ... |
```

## Non-Compensation Factors
| Factor | Company A | Company B |
|--------|-----------|-----------|
| Role Fit (1–5) | [from eval] | [from eval] |
| Growth Trajectory | [team size, advancement signals] | [team size, advancement signals] |
| Company Stability | [funding, headcount trend] | [funding, headcount trend] |
| Culture Signals | [from eval Red Flags or research] | [from eval Red Flags or research] |
| Location / Remote | [policy] | [policy] |
| Strategic Value | [how it advances your trajectory] | [how it advances your trajectory] |

## Decision Drivers
[2–3 factors that should actually move the decision — not a table rehash. Example: "Role fit is identical, so comp and growth trajectory are the real trade-off. Company A offers 18% more base but slower growth; Company B is a higher-growth environment with lower comp."]

## Recommendation
[Clear recommendation with reasoning, or a named tiebreaker question if too close to call. Example: "Company B — the growth trajectory and brand fit are worth the comp difference. Ask: Is the team stable, or is there churn risk?"]
```

3. **Save to** `Dossier/offer-comparison-[YYYY-MM-DD].md` with `type: offer-comparison` frontmatter.
