# Status & Outcome State Machine — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

This document defines how the `status` and `outcome` frontmatter fields on eval artifacts are updated together. The two fields are **not aliases** — they express different things:

- **`status`** is the *pipeline state* from your point of view: where the application sits (Evaluating, Applied, Interviewing, Offer, Rejected, Passed, Superseded).
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
| Eval created in error and replaced by a newer eval at same `[company-slug]` and a later `date:` | `Superseded` | *(omit)* | Mode 1 dedup recovery; user manual cleanup |

## Rules

1. **Last-event wins.** If the current outcome is `Interview` and a rejection email arrives, update to `outcome: Rejected` (and `status: Rejected`). Do not preserve the prior outcome; do not append a history. The transition trigger — not the prior state — determines the new values.

2. **Phone Screen → Interview is linear.** Phone Screen is the initial screening call (usually with a recruiter, sometimes a hiring manager at smaller orgs). Interview is what follows — typically remote Teams/Zoom calls with hiring manager + panel. An eval at `outcome: Interview` means at least one phone screen already happened.

3. **Status changes without outcome changes are not allowed.** Every status-write must set an outcome per this table — even if the outcome is staying at its current value. This prevents drift where status moves to `Applied` but outcome is left at `Evaluating`-era `Pending` (which happens to be correct here, but the rule forces the write to be explicit).

4. **Mode 9 batches transitions for user approval.** When Mode 9's Application Status Sync detects an email signal, it proposes both the new status and the new outcome together in the batch diff. The user approves once, and both fields write.

5. **Mode 0 health check validates consistency.** Mode 0 must flag any eval whose (status, outcome) pair does not match a row in the table above. The user is responsible for deciding how to resolve flagged mismatches.

## Terminal states

`Rejected`, `Passed`, `Offer-Declined` are terminal statuses. When status transitions to any terminal value, Mode 9's Application Status Sync folds the archival move into the same batch approval per `references/terminal-archival.md` — the entire company bundle moves to `archive/[slug]/` (or `archive/[slug]-v{N}/` on repeat archivals).

`Superseded` is a *bookkeeping-terminal* status. The eval no longer represents an active assessment — it is preserved (per the no-delete rule) but is not part of the active pipeline. Bookkeeping-terminal evals:

- Carry `status: Superseded` and a `supersedes:` field pointing to the canonical eval at the same `[company-slug]` whose `date:` is later (or, exceptionally, earlier — see "in-error" pattern below).
- Carry a `reason:` field explaining the supersede (typically a Mode 1 dedup glob miss followed by re-detection).
- **Are exempt from grade/score/outcome schema validation.** The frontmatter only requires `type`, `company`, `role`, `status`, `date`. `grade`, `score`, and `outcome` are omitted because the original assessment lives in the canonical eval being pointed to.
- Do **not** trigger archival. They stay in `evals/` so the relationship to the canonical eval is visible alongside it. Archival is reserved for full company-bundle terminal moves.

Cold-detection (`status: Passed` with `outcome: No Response` after 90+ days of silence) is **not currently automated** — it requires date arithmetic that no mode implements today. Handle manually for now.

## Example transitions

- Mode 1 creates `evals/eval-acme-2026-04-17.md` → `status: Evaluating`, `outcome: Pending`.
- User tells Claude they applied → `status: Applied`, `outcome: Pending`.
- Mode 9 finds a recruiter scheduling email → proposes `status: Interviewing`, `outcome: Phone Screen`.
- Mode 9 finds a panel/onsite invite → proposes `status: Interviewing`, `outcome: Interview`.
- Mode 9 finds a rejection email → proposes `status: Rejected`, `outcome: Rejected`. (Last-event wins even if we were at `Interview`.)
- User reports an offer → `status: Offer`, `outcome: Offer`. User accepts → `status: Offer`, `outcome: Accepted`.
- Mode 1's daily-scan dedup glob misses a duplicate and creates `evals/eval-acme-2026-05-02.md` after `evals/eval-acme-2026-04-29.md` already exists. On post-write detection, the newer file is rewritten as `status: Superseded`, `supersedes: eval-acme-2026-04-29.md`, `reason: "Created in error during the daily-scan run on 2026-05-02. ..."`, with `grade`, `score`, and `outcome` omitted.
