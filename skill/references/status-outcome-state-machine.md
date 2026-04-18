# Status & Outcome State Machine — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

This document defines how the `status` and `outcome` frontmatter fields on eval artifacts are updated together. The two fields are **not aliases** — they express different things:

- **`status`** is the *pipeline state* from your point of view: where the application sits (Evaluating, Applied, Interviewing, Offer, Rejected, Passed).
- **`outcome`** is the *response/advancement state* from the employer's side: what the most recent signal was (Pending, No Response, Phone Screen, Interview, Offer, Accepted, Rejected, Withdrawn).

They can legitimately diverge — e.g. `status: Applied` with `outcome: Pending` means you've applied and nothing has come back yet.

## Transition Table

Every status-write on an eval must also write the outcome per this table. The `outcome` column is the value to set when the trigger fires.

| Trigger | status | outcome | Driven by |
|---|---|---|---|
| New eval created | `Evaluating` | `Pending` | Mode 1, Mode 12 (batch) |
| Application submitted | `Applied` | `Pending` | User action; Mode 9 detects acknowledgment emails |
| Phone screen scheduled or occurred | `Interviewing` | `Phone Screen` | Mode 9 (recruiter scheduling email) |
| Interview (post-phone-screen, typically a Teams/Zoom call with hiring manager or panel) | `Interviewing` | `Interview` | Mode 9 (onsite/loop invite) |
| Rejection received | `Rejected` | `Rejected` | Mode 9 (rejection email) |
| Offer received | `Offer` | `Offer` | Mode 9 (offer email) or user-reported |
| User accepts offer | `Offer` | `Accepted` | User action |
| User withdraws / decides not to pursue | `Passed` | `Withdrawn` | User action |

## Rules

1. **Last-event wins.** If the current outcome is `Interview` and a rejection email arrives, update to `outcome: Rejected` (and `status: Rejected`). Do not preserve the prior outcome; do not append a history. The transition trigger — not the prior state — determines the new values.

2. **Phone Screen → Interview is linear.** Phone Screen is the initial screening call (usually with a recruiter, sometimes a hiring manager at smaller orgs). Interview is what follows — typically remote Teams/Zoom calls with hiring manager + panel. An eval at `outcome: Interview` means at least one phone screen already happened.

3. **Status changes without outcome changes are not allowed.** Every status-write must set an outcome per this table — even if the outcome is staying at its current value. This prevents drift where status moves to `Applied` but outcome is left at `Evaluating`-era `Pending` (which happens to be correct here, but the rule forces the write to be explicit).

4. **Mode 9 batches transitions for user approval.** When Mode 9's Application Status Sync detects an email signal, it proposes both the new status and the new outcome together in the batch diff. The user approves once, and both fields write.

5. **Mode 0 health check validates consistency.** Mode 0 must flag any eval whose (status, outcome) pair does not match a row in the table above. The user is responsible for deciding how to resolve flagged mismatches.

## Terminal states

`Rejected`, `Passed`, `Offer-Declined` are terminal statuses (see `file-conventions.md` for archival discipline). When status transitions to any terminal value, the outcome per the table applies, and the eval becomes eligible for `archive/[company-slug]/` move per existing archive rules.

Cold-detection (`status: Passed` with `outcome: No Response` after 90+ days of silence) is **not currently automated** — it requires date arithmetic that no mode implements today. Handle manually for now.

## Example transitions

- Mode 1 creates `evals/eval-acme-2026-04-17.md` → `status: Evaluating`, `outcome: Pending`.
- User tells Claude they applied → `status: Applied`, `outcome: Pending`.
- Mode 9 finds a recruiter scheduling email → proposes `status: Interviewing`, `outcome: Phone Screen`.
- Mode 9 finds a panel/onsite invite → proposes `status: Interviewing`, `outcome: Interview`.
- Mode 9 finds a rejection email → proposes `status: Rejected`, `outcome: Rejected`. (Last-event wins even if we were at `Interview`.)
- User reports an offer → `status: Offer`, `outcome: Offer`. User accepts → `status: Offer`, `outcome: Accepted`.
