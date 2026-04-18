# Terminal Archival — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

When an eval transitions to a terminal `status` — `Rejected`, `Passed`, or `Offer-Declined` — the entire company bundle auto-moves into `archive/[slug]/`. This lives inside Mode 9's Application Status Sync workflow: the same batch approval that writes the `(status, outcome)` pair also writes the move.

## When this runs

- Only inside Mode 9's Application Status Sync, after the `(status, outcome)` pair has been computed per `status-outcome-state-machine.md`.
- Terminal status values that trigger archival: `Rejected`, `Passed`, `Offer-Declined`.
- The `90+ days cold` case is **not automated yet** — it needs date arithmetic no mode implements. Handle manually.
- Never run archival speculatively, as a background pass, or without the user's explicit approval.

## Bundle scope

The company bundle is every artifact file in these four folders whose filename matches the company slug:

- `evals/eval-[slug]-[date].md`
- `outreach/outreach-[slug]-[date].md`
- `cover-letters/cover-[slug]-[date].md`
- `interview-prep/prep-[slug]-[date].md`

Research briefs in `research/` are **out of scope** — they are not strictly 1:1 per company.

## Slug extraction

Read the slug from the triggering eval's filename, not from the `company:` frontmatter. The filename pattern `eval-[slug]-[date].md` already encodes the canonical slug. Then scan the four bundle folders for any file whose name contains `-[slug]-` between the type prefix and the date segment.

## Destination layout

Preserve the original folder structure underneath the archive root:

```
archive/[slug]/
├── evals/eval-[slug]-[date].md
├── outreach/outreach-[slug]-[date].md
├── cover-letters/cover-[slug]-[date].md
└── interview-prep/prep-[slug]-[date].md
```

Dataview queries keyed on `FROM "evals"` etc. already exclude archived items because they no longer live in those root folders. Queries keyed on `FROM "archive"` (see `dashboard.md`) surface archived items separately.

## Versioning for repeat archivals

If `archive/[slug]/` already exists from a prior archival (the user re-engaged the same company, got another outcome, and is archiving again), do **not** merge into the existing folder. Create a new versioned folder:

- First archival: `archive/[slug]/`
- Second archival: `archive/[slug]-v2/`
- Third archival: `archive/[slug]-v3/`
- …and so on.

Each version holds only the artifacts from that engagement episode. This keeps distinct job-search episodes with the same company cleanly separated. Detect the next version by globbing `archive/[slug]*` and picking `vN+1` where `N` is the highest existing version (treat bare `archive/[slug]/` as v1).

## Cross-reference rewriting

Some artifacts use `related_eval:` or similar frontmatter keys as **path-style** references (e.g. `"examples/example-eval.md"` or `"evals/eval-foo-2026-04-15.md"`). Moving the target file breaks these.

Silently rewrite any path-style reference pointing at an artifact being archived into wikilink form — that is, `[[eval-foo-2026-04-15]]` — before writing the move. Obsidian wikilinks resolve by filename alone, so they survive the folder change without further maintenance. Do not surface this to the user; it's a mechanical follow-through of the archival they approved.

Wikilink-style references (`[[eval-foo-2026-04-15]]`) and `## Related` section links already resolve correctly post-move and need no rewriting.

## Mode 9 batch integration

Application Status Sync's batch diff must:

1. List the eval file, the proposed `(status, outcome)` pair, and — if the new status is terminal — the archival plan: the destination folder (`archive/[slug]/` or `archive/[slug]-v{N}/`), every bundle file that will move, and any cross-reference rewrites required.
2. Get the user's single approval for the whole batch.
3. Write status/outcome first, then move files, then rewrite cross-references.
4. Never send, auto-reply, or move without confirmation — same contract as every other Mode 9 operation.

## What not to do

- Don't archive on non-terminal statuses. `Applied`, `Interviewing`, `Offer`, `Evaluating` are active.
- Don't delete anything. Archival is a move, never a removal.
- Don't merge versioned archive folders after the fact; each episode stays distinct.
- Don't rewrite cross-references that already work (wikilink form, or any reference whose target is not being moved).
