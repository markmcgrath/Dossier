# Plan 20 — v1.3.1 cleanup and Phase 2 foundations

**Status:** Shipped
**Closed:** 2026-05-11 (v1.3.1 doc patch shipped same day; v1.3.2 follow-up doc fixes shipped same day; `examples/golden/` landed in PR #57; Plan 21 stub landed in PR #58)
**Author:** Mark McGrath (with Claude as drafting partner)
**Created:** 2026-05-11
**Scope:** Three coordinated work streams that close the v1.3.0 review punch list and lay the structural groundwork for Phase 2 without committing to feature code yet.

This plan is decomposed so that the bulk of execution runs on Sonnet subagents working from precise briefs. The main (Opus) context is reserved for synthesis, architectural decisions, and final review — the work where extra reasoning earns its cost. Mechanical work (audits, find/replace, parallel authoring of independent artifacts, post-edit verification) runs on Sonnet to keep main context clean and total spend low.

---

## Goals

1. Ship **v1.3.1** as a documentation-only patch that closes the four P0 doc-staleness items the v1.3.0 review surfaced. No code changes; no schema changes; no skill-bundle changes.
2. Author a **Target Radar Commonplace brief design doc** that establishes Target Radar as an upstream brief feeding Dossier — *not* as a Dossier mode. This is a design artifact only; no implementation.
3. Stand up an **`examples/golden/` regression-anchor folder** with three reference artifacts (strong-fit eval, poor-fit eval, prompt-injection JD response). Manual run only; no CI dependency on Claude.

---

## Non-goals

- No new Dossier modes.
- No schema or state-machine changes.
- No CI dependency on a live Claude call.
- No Target Radar implementation, scraping, or career-site resolver code. Design only.
- No retroactive rebuild of the four existing `examples/example-*.md` files; goldens are a separate, smaller, regression-focused set.

---

## Sequencing and dependency

Phase 1 (v1.3.1) is independent and can ship before either of the other two. Phase 2 (Target Radar brief) and Phase 3 (golden artifacts) are independent of each other and can run in parallel after Phase 1 ships, or even concurrently with Phase 1 if main-context bandwidth allows.

```
Phase 1 (v1.3.1) ──tag──▶ ship
                         │
        ┌────────────────┴────────────────┐
        ▼                                  ▼
Phase 2 (Target Radar brief)     Phase 3 (golden artifacts)
     design doc only                 examples/golden/ committed
```

---

## Agent decomposition principles

These rules govern when a step runs on a Sonnet subagent vs. in main context.

**Delegate to a Sonnet subagent when:**

- The step is an audit or scan that returns a *punch list* rather than file contents (the agent reads many files, the main context only sees the summary).
- The step is a mechanical edit against a precise spec (find this string, replace with that string, in these files).
- The step is independent authoring of a self-contained artifact (each golden artifact is its own brief).
- The step is post-edit verification that re-runs an audit to confirm a fix landed correctly.

**Keep in main context when:**

- The step requires a judgment call (scope, schema, naming, what-counts-as-done).
- The step synthesizes multiple agent outputs into a coherent decision.
- The step is the final review before commit, tag, or push.
- The step touches less than ~100 lines in 1–2 files (overhead of dispatching dominates).

**Cost discipline rules for agent dispatch:**

- Every Sonnet brief is self-contained — file paths, exact strings to look for, expected output shape, and a word cap on the report.
- Agents return punch lists or specs, not full file dumps.
- Multiple independent agent calls go in a single message (parallel execution).
- Verification is cheaper as a fresh Sonnet agent than as re-reads in main context — the agent reads the file, confirms the change, returns a one-line pass/fail.

---

## Phase 1 — v1.3.1 documentation patch

**Target ship date:** within one week of this plan being approved (small enough to fit in a single sitting).
**Surface area:** `tests/README.md`, `DATA_CONTRACT.md`, `README.md`. No `skill/` changes, no schema changes, no `dossier.skill` repack.
**Routing eval:** not required (no skill-body changes), but cheap to re-run as a sanity check.

### 1.1 Audit — Sonnet agent (parallel × 3)

Dispatch three Sonnet agents in a single message. Each gets a tightly-scoped audit brief and returns a punch list, not file contents.

**Agent 1.1.A — `tests/README.md` drift audit**

Brief skeleton:
> Read `tests/README.md` and `.github/workflows/ci.yml` in `dossier-open-source/`. The README's CI section claims "two jobs that produce three required status checks" and lists `test` and `pii-scan`. The workflow actually defines five jobs. Produce a punch list of every line in `tests/README.md` that needs to change, with: (a) line number, (b) current text, (c) replacement text, (d) why. Also list each new test file under `tests/` that's missing from the README's directory tree (lines ~49-69) and from the test stats (line ~144). Cap the report at 400 words.

Expected output: a numbered punch list of edits, ready for mechanical application. No prose beyond what's needed for "why."

**Agent 1.1.B — `DATA_CONTRACT.md` consistency audit**

Brief skeleton:
> Read `DATA_CONTRACT.md` in `dossier-open-source/`. The system-layer code block (around line 60) lists `Diagram.md`. The summary table at line 143 omits it. Confirm the inconsistency, and *also* sweep the rest of the document for any other system-layer / user-layer / derived-files inconsistencies — files mentioned in one section but not another, references that point at outdated paths, or summary-vs-body mismatches. Return a punch list with line numbers and proposed edits. Cap at 300 words.

Expected output: confirmation of the Diagram.md miss plus any sibling drift the agent catches.

**Agent 1.1.C — `README.md` version-staleness sweep**

Brief skeleton:
> Read `README.md` in `dossier-open-source/`. The Upgrading section (around lines 227-235) hard-codes `v1.2.0` URLs in the example. Find every occurrence of a hard-coded version reference (`v1.x.y` patterns) and judge for each whether it should be replaced with `<tag>` placeholder or updated to `v1.3.0`. Also flag any other version-staleness — release-note links, example tags, references to features by old version. Return a punch list with line numbers, current text, recommended replacement, and a one-line rationale. Cap at 300 words.

Expected output: a punch list of version-stale references, each with a clear "placeholder vs. concrete update" recommendation.

**Why parallel:** No agent depends on another's output. Three concurrent calls cost roughly what one serial call would in wall-clock time.

### 1.2 Spec review and edit decisions — main context

Main context reads the three punch lists, accepts/rejects each proposed edit, and folds them into a single edit batch. This is where judgment lives — for example, deciding whether to adopt `<tag>` placeholders or simply bump to `v1.3.0` strings (the reviewer suggested either; pick the one that minimizes future maintenance).

Output: a consolidated `EDIT_BATCH.md` (scratch, not committed) listing every edit with file, find-string, replace-string. This becomes the input to step 1.3.

### 1.3 Edit application — Sonnet agent (single)

Brief skeleton:
> Apply the edits in the attached batch to the listed files in `dossier-open-source/`. Use the Edit tool with exact strings. After all edits, re-read each modified file once and confirm the new strings are present and the old strings are absent. Return a per-file pass/fail line and the total count of edits applied. Cap report at 150 words.

Why an agent: pure mechanical, single-shot, and offloads the Edit-tool sequence from main.

### 1.4 Verification — Sonnet agent (single)

Brief skeleton:
> Re-run the three audits from step 1.1 against the now-edited files. For each audit, return PASS (no findings) or FAIL with the remaining findings. Cap at 200 words.

Why a fresh agent rather than re-reading in main: the agent has no prior assumption that the fix landed; it audits cold.

### 1.5 Tag, push, and post-release sanity — main context

- `[Unreleased]` → `[1.3.1] — YYYY-MM-DD` block in CHANGELOG.md (Documentation section only, four bullets corresponding to the four P0 fixes).
- `git commit -m "docs: v1.3.1 — close v1.3.0 review punch list"`.
- Optional but recommended: re-run `tools/run_routing_evals.py` since CHANGELOG touched but skill body unchanged — should still score 0.967 ± noise.
- Tag `v1.3.1`, push, verify release workflow produces `dist/dossier-v1.3.1.skill` and `.sha256`.

**Phase 1 cost shape:** three parallel Sonnet audits + one Sonnet edit pass + one Sonnet verify. Main context spends maybe 10–15 minutes of attention on synthesis, decisions, and the tag mechanics. Total wall time: under an hour.

---

## Phase 2 — Target Radar brief design doc

**Output:** a single Commonplace Book entry (canonical, in `entries/`) plus a thin cross-link from `dossier-open-source/features/plan/21-target-radar-brief.md` pointing at it.

**Important boundary:** Target Radar is a Commonplace brief, not a Dossier mode. Discovery, scoring, and career-site resolution all live upstream of Dossier in the brief author's territory. The brief's *output* is canonical entries Dossier consumes when evaluating fit. This boundary is the entire point of writing the design doc — to nail it down *before* code happens.

### 2.1 Vault landscape survey — Sonnet agent (single)

Brief skeleton:
> Survey the Commonplace Book vault at `../The Commonplace Book/entries/` (sibling of the dossier-open-source checkout) for any entries that touch target-company discovery, company scoring, market radars, or career-site resolution. Specifically check: `2026-05-10-hr-leader-market-radar.md`, `2026-04-29-dossier-stream-d-competitive.md`, `2026-04-29-dossier-stream-c-foundation.md`, and any other entry whose title or tags suggest discovery/scoring. For each relevant entry, report: (a) one-line summary, (b) what it claims about discovery/scoring/radar work, (c) overlap with Target Radar concept (high/medium/low), (d) is it a decision, a research finding, or a backlog item. Also list the briefs currently in `briefs/` (if any) and the schema they use. Return a structured report. Cap at 600 words.

Expected output: a delta map of what's already in the vault on this topic, so the design doc doesn't re-invent or contradict prior decisions.

### 2.2 Brief format reference — Sonnet agent (single, parallel with 2.1)

Brief skeleton:
> Read the Commonplace skill at `.claude/skills/commonplace/SKILL.md` and any reference docs under it that describe the `briefs/` format. Specifically: what does a brief file look like (frontmatter, sections, decay class), how does the executor consume it, and what are the failure modes (manifest hash bug, source truncation cap, broken-manifest fallback — these are documented in user memory). Return a one-page reference summarizing the brief authoring contract. Cap at 500 words.

Expected output: a self-contained reference that the main-context drafter can lean on without re-reading the skill themselves.

**Why parallel:** vault survey and brief-format reference are independent reads.

### 2.3 Design decisions — main context

Main context now has a vault delta and a format reference. The judgment work:

- **Scope.** What does Target Radar discover? Companies-by-segment? Companies-with-recent-funding? Career-page-changes? Pick a tight v0 scope.
- **Inputs.** What feeds the brief? `profile.md`'s target-roles signal? An explicit allow-list of segments? A scheduled SimilarWeb / Crunchbase query?
- **Outputs.** What does each brief run produce? One canonical entry per company? One entry per radar pass with N companies inside? How does Dossier discover and consume those entries?
- **Schema.** What frontmatter does the output entry need so Dossier's `dossier-stream-d-competitive` lineage and Mode 1's eval flow can read it?
- **Decay.** How fast does a Target Radar entry go stale? `slow` (quarterly), `medium` (monthly), `fast` (weekly)?
- **Boundary enforcement.** Explicit non-goals: no scraping inside Dossier, no Apollo enrichment in this brief, no portal scan handoff (that stays Mode 2).

This is the one part of the plan that *must* live in main context. The synthesis of survey + format + scope decisions is exactly the kind of cross-cutting reasoning that benefits from extra inference budget.

### 2.4 Brief design doc draft — Sonnet agent (single)

Brief skeleton (filled in by main context after 2.3):
> Draft a Commonplace Book canonical entry titled `[YYYY-MM-DD]-target-radar-brief-design.md` based on the attached scope decisions. Sections: Claims (the load-bearing decisions, footnoted), Context (why this is a brief and not a mode), Inputs, Outputs, Schema, Decay, Non-goals, Open Questions. Frontmatter must conform to Commonplace schema (id, schema_version, kind: plan-doc, title, status: draft, created_at, updated_at, version: 1, tags including `target-radar` and `dossier`, domain: orchestrator, decay_class). Write the body with citations to the relevant existing vault entries from the survey. Return the full draft. Cap at 1500 words.

Expected output: a draft entry ready to ingest. Main context reviews, refines, and ingests via `commonplace ingest` per the documented workflow.

### 2.5 Cross-link stub — Sonnet agent (single)

Brief skeleton:
> Create `dossier-open-source/features/plan/21-target-radar-brief.md`. Contents: one paragraph stating that Target Radar is designed as a Commonplace brief upstream of Dossier (not a Dossier mode); a wikilink-style pointer to the canonical Commonplace entry written in step 2.4 by id; an explicit list of what Dossier owns vs. what the brief owns. Cap at 200 words.

### 2.6 Promote the brief design doc to canonical — main context

Run the standard ingest → lint → promote sequence per the documented batch ingest+promote pattern (see user memory). Main context handles this because the partial-success recovery paths (cowork bash mutation gates, manifest hash quirks) are nuanced and benefit from the operator's judgment.

**Phase 2 cost shape:** two parallel Sonnet surveys + one Sonnet draft + one Sonnet stub. Main context owns the design decisions (the load-bearing part) and the promote ceremony. Total: a focused half-day if scope decisions are easy, a full day if scope decisions need a second pass.

---

## Phase 3 — `examples/golden/` regression anchors

**Output:** a new `dossier-open-source/examples/golden/` folder containing three reference artifacts plus a small `README.md` explaining the regression-anchor workflow. Goldens are *manual* references, not CI inputs — the workflow is: when Mode 1 (or Mode 6, etc.) is changed materially, re-run the same fixture inputs by hand, diff against the golden, and escalate any drift.

**Inputs reused:** `tests/fixtures/jd_strong_fit.md`, `tests/fixtures/jd_ghost_job.md`, `tests/fixtures/jd_injection_attempt.md` already exist and serve exactly this purpose as inputs. The work is producing the *expected outputs* and committing them.

### 3.1 Schema and framing decision — main context

Two judgment calls before any artifact authoring:

- **Where do they live and what do they look like?** `examples/golden/eval-strong-fit.md`, `examples/golden/eval-poor-fit.md`, `examples/golden/eval-injection-response.md`? Or a flatter `examples/golden/strong-fit/` subfolder with the JD input and expected eval as separate files? Decide based on whether anyone will want to re-run a single golden in isolation (favors subfolder) or scan all three quickly (favors flat).
- **What's the regression-anchor framing?** Each golden needs a header banner explaining: "this is a reference output for Mode X. If a change to Mode X causes its output on this fixture to drift in substance (not formatting), escalate before merging." Without that banner, the goldens become showpieces and lose their regression value within two releases.

The four existing `examples/example-*.md` artifacts use the *Cipher Analytics* fictional narrative. The reviewer flagged this is the canonical example set. Goldens should use the *same* fictional narrative for consistency, even though the inputs are different fixtures — readers shouldn't have to context-switch between two parallel example universes.

### 3.2 Golden authoring — Sonnet agents (parallel × 3)

Dispatch three independent Sonnet agents in a single message. Each authors one golden against one fixture. The agent should run Mode 1 (or Mode 6 for the cover-letter case if added later) *as documented in `skill/SKILL.md`* against the fixture and produce an artifact that conforms to the canonical eval schema.

**Agent 3.2.A — strong-fit golden**

Brief skeleton:
> Read `dossier-open-source/skill/SKILL.md` Mode 1 instructions and `dossier-open-source/skill/references/scoring-guide.md`. Read the fixture `dossier-open-source/tests/fixtures/jd_strong_fit.md`. Produce the eval artifact Mode 1 would write — full frontmatter (id, kind: eval, company, role, grade, status: Evaluating, outcome: Pending, legitimacy, scoring dimensions, sources), full body (Score, Verdict, Strengths, Risks, Open Questions, Next Steps). Use the Cipher Analytics fictional candidate narrative consistent with `examples/example-eval.md`. Prepend a regression-anchor banner: "REFERENCE OUTPUT — strong-fit eval. If a Mode 1 change causes substantive drift on this fixture, escalate before merging." Return the full artifact. Cap at 1200 words.

**Agent 3.2.B — poor-fit / ghost-job golden**

Brief skeleton:
> [Same as 3.2.A, but use `tests/fixtures/jd_ghost_job.md` and produce an eval that surfaces the legitimacy red flags (likely-ghost, age, vagueness, skill-list bloat, no comp). Grade should reflect the gate-pass logic in scoring-guide.md. Banner: "REFERENCE OUTPUT — poor-fit eval (ghost-job legitimacy red flags)."] Cap at 1000 words.

**Agent 3.2.C — prompt-injection response golden**

Brief skeleton:
> [Same shape, but use `tests/fixtures/jd_injection_attempt.md`. The expected output is *not* a normal eval — it's a Content-Trust-Boundary-respecting response that flags the injection, refuses the injected instructions, and proceeds with a degraded eval (or refuses to evaluate at all, depending on what `skill/SKILL.md` actually specifies). Read the Content Trust Boundary section in SKILL.md carefully and produce the response that section prescribes. Banner: "REFERENCE OUTPUT — prompt-injection JD response. If a Mode 1 change causes drift in injection handling on this fixture, escalate before merging — this is a security-relevant regression."] Cap at 800 words.

**Why parallel:** all three artifacts are independent. Three concurrent dispatches.

### 3.3 Folder README and review — main context

Author `examples/golden/README.md` (~150 words) that:

- Names each golden and its fixture pair.
- Explains the manual workflow: "When you change Mode X, re-run this fixture by hand, diff your output against the golden, and either update the golden in the same PR (with a CHANGELOG note) or revert your change."
- Notes that goldens are *not* in CI.
- Cross-links to the four existing `examples/example-*.md` showpieces and explains the difference (showpieces show what good looks like for new readers; goldens are regression anchors for maintainers).

Main context reviews each of the three drafted goldens, edits for tone and consistency, and commits the folder.

### 3.4 CHANGELOG entry and ship

Add to `[Unreleased]` (or fold into the v1.3.1 batch if Phase 1 hasn't shipped yet):

> ### Added
> - `examples/golden/` — three regression-anchor artifacts paired with the existing `tests/fixtures/jd_*.md` inputs. Manual workflow: re-run on Mode 1 changes, diff for substantive drift. Not a CI gate.

Decide at this point whether Phase 3 ships in a v1.3.2 patch or waits until a feature release.

**Phase 3 cost shape:** three parallel Sonnet authoring calls + main-context review and a small README. The authoring calls are the single largest spend in this plan since each produces 800–1200 words of structured artifact content — but parallelism keeps wall-clock cost low.

---

## Risks and how this plan handles them

**Risk: scope creep into Phase 4-and-beyond.**
Mitigation: every phase has explicit non-goals at the top. Target Radar is design-only; goldens are manual-only; v1.3.1 is docs-only. If a phase starts pulling in adjacent work, stop and write a separate plan.

**Risk: the brief design doc gets stale because the brief itself never gets built.**
Mitigation: the design doc has `decay_class` set in frontmatter so the vault audit will surface it for review. Acceptable to leave the design canonical-but-unimplemented for months — that's exactly what "design doc, not code" means.

**Risk: goldens drift silently because no one diffs them on Mode 1 changes.**
Mitigation: the regression-anchor banner is in-artifact, not in a separate doc. Anyone looking at a golden sees the workflow. The README also calls this out. If after two release cycles the goldens are visibly stale and no one's diffed them, treat that as a signal to either automate (Phase 4 work, separate plan) or delete (don't ship dead goldens).

**Risk: agent dispatch overhead exceeds the work being delegated.**
Mitigation: the agent decomposition principles section has an explicit "less than ~100 lines in 1–2 files → keep in main" carve-out. If a step's brief is longer than the work it produces, do it in main.

---

## Success criteria

- **Phase 1:** v1.3.1 tag pushed; routing eval still ≥0.95; Sonnet verification agent returns PASS on all three audits; the next time someone reads `tests/README.md`'s CI section it matches `.github/workflows/ci.yml`.
- **Phase 2:** A canonical Commonplace entry exists for the Target Radar brief design; `features/plan/21-target-radar-brief.md` cross-links to it; the design clearly states Target Radar is a brief, not a mode, and lists what it owns vs. what Dossier owns.
- **Phase 3:** `examples/golden/` exists with three artifacts and a README; each golden carries the regression-anchor banner; CHANGELOG records the addition.

---

## Open questions

- Should the v1.3.1 patch also adopt the install-from-release smoke checklist the reviewer flagged as P2 (`HARDENING.md` or `CONTRIBUTING.md`)? Probably no — keeps v1.3.1 to docs-only, defers to a P2 batch.
- Should goldens for Mode 5 (outreach) and Mode 6 (cover letter) ship in this Phase 3 batch, or wait until those modes change next? Default: wait. Three artifacts is enough to establish the pattern; grow the set when there's a real regression need.
- Does the Target Radar brief design doc need a `depends_on` link to `dossier-stream-d-competitive`? Likely yes if the survey in 2.1 finds substantive overlap. Decide during step 2.3.
