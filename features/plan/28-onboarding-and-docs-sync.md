# Plan 28 — Onboarding & Documentation Sync (Modes 14 and 15)

**Status:** Spec — ready for Claude Code CLI execution
**Created:** 2026-06-25
**Implements:** Documentation drift cleanup following Plan 23 (Mode 14, Packet Assembly) and Plan 25 (Mode 15, Target Radar)
**Type:** Documentation-only. No skill-bundle, schema, test, or config-behavior changes.

---

## 1. Summary

Modes 14 (Packet Assembly) and 15 (Target Radar) shipped under Plans 23 and 25. The machine-contract layer was updated in lockstep, but the human-onboarding layer was not. A first-time user following `START_HERE.md` is never told the two newest modes exist, is not guided to create their folders, and is not offered the radar's scheduled-refresh task. For a discovery-led search (for example a single target title across many companies), Target Radar is the single most relevant feature, and it is the one the guided path hides.

This plan resyncs the onboarding and prose documentation to the shipped behavior and mandates a full sweep to catch any drift this plan does not enumerate.

The drift is narrow and well-contained. The contract docs are already correct (see Section 3), so this is low-risk prose work, not a structural change.

---

## 2. What is out of sync (authoritative inventory)

Evidence cited as `file:line` against the live repo as of 2026-06-25. Verify each string before editing; do not trust paraphrase.

| # | File | Location | Problem | Severity |
|---|------|----------|---------|----------|
| D1 | `START_HERE.md` | Step 3, vault folder list | Omits `packets/` (Mode 14) and `target-radar/` (Mode 15). Lists only evals/outreach/cover-letters/interview-prep/research/daily/weekly/archive + dashboard.md. | High |
| D2 | `START_HERE.md` | Step 3, prose | Says "the **eight** folders above and `dashboard.md` are present." Count becomes ten once D1 is fixed. | High |
| D3 | `START_HERE.md` | Step 4, primary mode list | Six entry points (evaluate/search/research/outreach/prep/negotiate). No discovery/radar entry. | High |
| D4 | `START_HERE.md` | Step 4, second-tier mode sentence | Enumerates batch eval, calendar prep, inbox triage, calibration, tailored CVs, LinkedIn. Omits Packet Assembly (Mode 14) and Target Radar (Mode 15). | High |
| D5 | `START_HERE.md` | "Going further > Scheduled tasks" | Lists daily job scan, follow-up reminders, weekly pipeline review. Omits the Weekly Target Radar Refresh, which already exists as a complete prompt at `schedule-prompts.md:103-110`. | Medium |
| D6 | `START_HERE.md` | Step 3 / config handoff | Never tells the user to populate the radar config keys (`target_segments`, `radar_seed_cap`, `radar_decay_days`), which ship commented-out at `config.template.md:62-74`. | Low |
| D7 | `README.md` | Feature/prose sections (`## ` features ~15-16, `## Quick start` :69, `## Core concepts` :111) | Discovery/radar and packets appear only in the directory tree (`:140-141`) and user-layer list (`:202`), never as named capabilities in prose. | Medium |
| D8 | `features/plan/21-target-radar-brief.md` | Body | Banner correctly says "Superseded by Plan 25," but the body still asserts in present tense that Target Radar "is designed as a Commonplace brief... not as a Dossier mode" and "No implementation work is scheduled." Internally contradicts the banner. | Low |

### Sweep findings (appended during execution, Section 6)

Found by the fresh-eyes sweep and fixed in the same pass. Each verified against the live file before editing.

| # | File | Location | Problem | Disposition |
|---|------|----------|---------|-------------|
| D9 | `README.md` | Core concepts (`:115`) | "**14 named modes**" was stale (the 14 = modes 0 to 13 convention, per Plan 10). Modes 0 to 15 ship now. | Fixed: "16 named modes". |
| D10 | `dashboard.md` | Sections (`:226-232`) | Mode 15 output in `target-radar/` had no dashboard view; only "Research / Target Briefs" (`FROM "research"`) existed. | Fixed: added a "Target Radar — Company Discovery" Dataview section over `target-radar/`. |
| D11 | `README.md` | "How it works" mermaid (`:35`) | Artifacts node enumerated `eval · outreach · prep · research`, omitting packet and target-company. | Fixed: appended `packet · target-company`. |
| D12 | `Diagram.md` | "High-Level Flow" mermaid (`:13`) | Artifact-generation node enumerated `eval, outreach, prep`, omitting packet and target-company. | Fixed: appended `packet, target-company`. |
| D13 | `PRIVACY.md` | Data-flow table, Vault Contents (`:22`) | "Everything in the Dossier folder (evals, outreach, prep, notes)" omitted packets and target-radar. | Fixed: added `packets, target-radar`. |
| D14 | `PRIVACY.md` | Threat model, Vault Contents (`:190`) | Exfiltration-asset list omitted packets and target-radar (both sensitive). | Fixed: added `packets, target-radar artifacts`. |
| D15 | `PRIVACY.md` | Data Retention (`:365`) | Retention enumeration omitted packets and target-radar. | Fixed: added `packets, target-radar`. |

**Rejected sweep findings (verified inert, not fixed):** the sweep proposed adding `packets`/`target-radar` to the date-keyed `FROM` clauses of `dashboard.md`'s "Today's Activity" (`:23`) and "This Week" (`:38`) views. Rejected: `type: packet` files carry `created`/`updated` and `type: target-company` files carry `created_at`/`refreshed_at`, neither has a `date` field, so the existing `WHERE date = date(today)` / `WHERE date >= ...` filters would never match them. A correct fix would require schema-aware multi-field WHERE logic, which is a query-behavior change out of scope for this docs-only plan. The dedicated D10 section is the correct surface for Mode 15 output.

**Post-merge correction (recorded for honesty):** D1/D2's "ten folders" target was itself incomplete. It inherited a pre-existing `START_HERE.md` omission of `negotiation/` (Mode 7 output, scaffolded with `.gitkeep` and present in `README.md`, `skill/SKILL.md`, `file-conventions.md`, and `DATA_CONTRACT.md`). The true scaffolded artifact-folder count is eleven. This plan was scoped to Modes 14/15, so the negotiation gap was out of its hunt; it was found and fixed in a follow-up docs-sync (`START_HERE.md` ten to eleven plus `negotiation/`; `dashboard.md` date views and a dedicated negotiation section), not under Plan 28.

---

## 3. What is already current — DO NOT "fix"

Confirmed correct on 2026-06-25. Editing these risks introducing drift, not removing it.

- `skill/references/file-conventions.md` — folder diagram and type sections already cover `packets/` (Mode 14, `:26`, `:140`) and `target-radar/` (Mode 15, `:30`, `:79`).
- `DATA_CONTRACT.md` — `packets/` and `target-radar/` listed as Sacred (`:35-36`), Mode 15 retention rule (`:39`), 21-file bundle (`:69`), Mode 14 derived files (`:108-111`, `:152`).
- `README.md` — Project-structure tree (`:140-141`) and Governance user-layer list (`:202`) already include both new folders. Only the *prose* needs the D7 touch.
- `config.template.md` — radar keys present and correctly documented (`:62-74`); they are intentionally commented out as scaffolding. Do not uncomment them in the template; D6 is a `START_HERE.md` instruction, not a template edit.
- `dossier.skill` bundle, `tests/`, `EXPECTED_BUNDLE_ENTRIES` — untouched by this plan. This is a docs-only change; do not rebuild the bundle or alter the frozen count.

---

## 4. Scope and non-goals

In scope: `START_HERE.md`, `README.md` prose, `features/plan/21-target-radar-brief.md` body, `CHANGELOG.md`, `features/plan/README.md` index, and the verification sweep.

Non-goals:
- No change to `dossier.skill`, `skill/SKILL.md` mode behavior, schemas, or tests.
- No change to the eval-first "first success" design in `START_HERE.md` Step 5. Discovery is surfaced as an option, not made the mandatory first run. (Respect the existing onboarding sequence.)
- No uncommenting of `config.template.md` radar keys.

---

## 5. Edits

Standard house discipline: read the live file and match the exact current string including whitespace before each Edit. Keep Mark's no-em-dash rule in all new prose (commas, colons, periods, parentheses only).

### Task A — START_HERE.md (the core fix)

**A1 (D1, D2) — Step 3 folder list.** Add `packets/` and `target-radar/` to the enumerated folder list, and update the "eight folders" count to "ten folders."

Current list to extend:
```
- evals/
- outreach/
- cover-letters/
- interview-prep/
- research/
- daily/
- weekly/
- archive/
- dashboard.md
```
Add `- packets/` and `- target-radar/` before `- dashboard.md` (dashboard.md is a file, keep it last). Then change the sentence "the **eight** folders above and `dashboard.md` are present" to "the **ten** folders above and `dashboard.md` are present." Verify the literal word "eight" against the live file before replacing.

**A2 (D3) — Step 4 primary mode list.** Add a discovery entry. Insert after the `search` line:
```
- discover: find target companies worth pursuing (Target Radar)
```
Rationale: for discovery-led searches this is a primary entry point, not a hidden mode. Keep the one-line-per-mode format and verb-first naming used by the existing six.

**A3 (D4) — Step 4 second-tier sentence.** Extend the "additional capability modes" enumeration to include the two new modes. Current sentence:
> Mention — but don't enumerate — that the skill has additional capability modes for batch evaluation, calendar prep blocks, inbox triage, calibration reports, tailored CVs, and LinkedIn workflows.

Add "packet assembly" to the list. (Target Radar is now promoted to the primary list in A2, so it does not also belong here; if the implementer prefers to keep discovery out of the primary list, then add "and Target Radar company discovery" here instead. Pick one placement, not both.)

**A4 (D5) — Scheduled tasks.** Add a fourth bullet to the "Going further > Scheduled tasks" list, after "Weekly pipeline review":
```
- **Weekly Target Radar refresh** — re-scan your target segments and stale tracked companies, refreshing `target-radar/` artifacts. Ready-made prompt in `schedule-prompts.md` (Weekly Target Radar Refresh).
```
Cross-link is to `schedule-prompts.md:103-110`, which already contains the full prompt; do not duplicate the prompt body into START_HERE.

**A5 (D6) — Radar config pointer.** In the config handoff (Step 3, near the `config.template.md` rename instruction, or as a one-line note in "Going further"), add a sentence telling discovery users to uncomment and populate `target_segments` (and optionally `radar_seed_cap`, `radar_decay_days`) in their `config.md` so Target Radar has a default scope. One sentence; do not reproduce the key docs.

### Task B — README.md prose (D7)

Light touch. In the features list (around `:15-16`) or Core concepts (`:111`), add one line each naming Target Radar (company discovery that scores company-level fit and writes `target-radar/` artifacts) and Packets (per-application send-ready bundles assembled by Mode 14). Optionally add a one-line "discover target companies" example to the Quick start block (`:69`). Do not restructure README; do not touch the already-correct tree (`:140-141`) or user-layer list (`:202`).

### Task C — Plan 21 body reconciliation (D8)

In `features/plan/21-target-radar-brief.md`, reconcile the body with the banner. Convert the present-tense old-design assertions to past tense or add an inline "(superseded)" qualifier so the body no longer reads as the current design. Minimal edit; the banner already carries the authoritative pointer to Plan 25. Do not delete the stub (plan-numbering convention).

---

## 6. Documentation sweep (required, beyond the enumerated edits)

The inventory above is what this author found; treat it as a floor, not a ceiling. After Tasks A to C, run a full sweep so no Mode 14 / Mode 15 reference is missed and no other drift survives.

Recommended: run this sweep as a fresh-eyes pass (a subagent with no memory of the edits above is ideal for catching what the author anchored past).

Sweep procedure:
1. Enumerate every mode reference across docs:
   `grep -rinE "mode ?[0-9]+|six (modes|entry)|eight folders|ten folders|17 (file|entr)|21 (file|entr)" --include=*.md . | grep -vE "\.pytest_cache"`
   Confirm every mode-count and folder-count statement matches the shipped reality (modes 0 to 15; bundle 21 files; vault folder set including `packets/` and `target-radar/`).
2. Cross-check the user-facing mode inventory in `skill/SKILL.md` against `START_HERE.md` and `README.md`: every mode a user can trigger should be discoverable from at least one onboarding doc, even if only by the "read the full list in skill/SKILL.md" pointer.
3. Spot-check the README `## Support matrix`, `## How it works` diagram, and `dashboard.md` for any "all modes / all folders" enumeration that silently excludes 14 or 15.
4. Verify no doc still describes Target Radar as a Commonplace brief or as unscheduled/unbuilt (the Plan 21 / Plan 25 reversal).
5. Record anything found as additional D-items appended to Section 2, fix them in the same pass, and note them in the CHANGELOG entry (Task D).

---

## 7. Housekeeping (same commit)

Per execution principle "update docs in the same commit as the change":

- **Register this plan.** Add a row to the "Subsequent plans" table in `features/plan/README.md`: `| 28 | [[28-onboarding-and-docs-sync]] | Onboarding & docs sync for Modes 14 and 15 |`.
- **CHANGELOG.md.** Add an entry under the appropriate Unreleased/next-version heading: documentation sync surfacing Mode 14 (Packet Assembly) and Mode 15 (Target Radar) in `START_HERE.md` and `README.md`, plus the Weekly Target Radar Refresh schedule and Plan 21 body reconciliation. Documentation-only; no bundle or schema change.

---

## 8. Verification and acceptance criteria

Done when all of the following hold:

1. `grep -niE "target-radar|packets|mode ?14|mode ?15|radar" START_HERE.md` returns hits in the folder list, the mode list, and the scheduled-tasks section.
2. `START_HERE.md` no longer says "eight folders"; it says "ten."
3. A reader of `START_HERE.md` alone can learn that company discovery (Target Radar) and packet assembly exist and how to trigger or schedule them.
4. `README.md` prose names Target Radar and packets as capabilities, not only as folders.
5. `features/plan/21-target-radar-brief.md` body no longer asserts the superseded design in present tense.
6. Plan 28 is registered in `features/plan/README.md`; CHANGELOG entry present.
7. Sweep (Section 6) completed; any new findings fixed and logged.
8. No change to `dossier.skill`, tests, schemas, or `EXPECTED_BUNDLE_ENTRIES`. `git diff --stat` shows only `.md` files.

---

## 9. Execution order

1. Task A (START_HERE.md) — highest user impact.
2. Task B (README prose).
3. Task C (Plan 21 body).
4. Section 6 sweep (fresh-eyes subagent) — may surface additional edits; apply them.
5. Task D housekeeping (index + CHANGELOG), capturing anything the sweep added.
6. Section 8 verification gate before commit.

---

## 10. Guardrails

- **Verify-before-edit.** Every old-string target in Section 5 must be matched against the live file at edit time. Counts and list contents drift; do not trust this doc's quotes blindly.
- **Docs-only.** If any planned edit would touch `dossier.skill`, a test, a schema, or `EXPECTED_BUNDLE_ENTRIES`, stop: it is out of scope for Plan 28 and indicates a miscategorized change.
- **Respect existing design choices.** Eval-first onboarding (Step 5) stays. Radar config keys stay commented in the template. Discovery is offered, not forced.
- **No em-dashes** in any new or edited prose, per repo authoring convention. Use commas, colons, periods, or parentheses.
- **One placement for the discovery mode** (primary list in A2 OR second-tier sentence in A3), never both.
