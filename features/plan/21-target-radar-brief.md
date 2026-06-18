# Plan 21 — Target Radar (brief, not mode)

> **Superseded by Plan 25.** Target Radar is now implemented as Mode 15 inside Dossier.
> See `features/plan/25-target-radar-component.md`. The Commonplace-brief ownership model
> described here is no longer the design. Vault supersede of entries
> `2026-05-11-target-radar-brief-design` and `2026-05-27-dossier-plan21-target-radar-brief`
> is a separate user-run operation.

**Status:** Design only — see canonical entry
**Created:** 2026-05-11
**Canonical design doc:** [[2026-05-11-target-radar-brief-design]] (in The Commonplace Book vault)

Target Radar is designed as a Commonplace brief upstream of Dossier, not as a Dossier mode. All load-bearing design decisions — scoring logic, URL resolution, entry schema, decay policy — live in the canonical entry linked above. This stub exists in `dossier-open-source/features/plan/` so the plan-numbering convention stays intact and so anyone walking the dossier plan folder can find their way to the design.

## What Dossier owns

- Role-level evaluation (Mode 1)
- Eval frontmatter authoring (Mode 1)
- Portal scan / job-list parsing (Mode 2)
- Outreach drafting (Mode 5)
- Cover letter generation (Mode 6)

## What the Target Radar brief owns

- Discovering target companies in profile.md's target segments
- Resolving career-site URLs (Greenhouse / Lever / Ashby)
- Scoring company-level fit (`fit_score`)
- Producing draft `kind: target-company` entries for user review

## Next step

No implementation work is scheduled. The canonical design doc carries `decay_class: slow` (180-day TTL); if Target Radar is still useful at the next vault audit, that's the signal to schedule implementation.
