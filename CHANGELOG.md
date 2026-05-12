# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- `CONTRIBUTING.md` §Post-release install smoke step 4: two errors caught while dogfooding the checklist against the v1.3.2 release. (1) The `version` field stores the tag *verbatim* (`v1.3.2`), not the tag *without* the leading `v` as the prior text claimed — corrected the example. (2) `git rev-parse vX.Y.Z` on an annotated tag returns the tag-object SHA, not the commit SHA the tag points at; the manifest stores the commit SHA. Corrected the verification command to `git rev-parse vX.Y.Z^{commit}` with a short note explaining the peeling. A maintainer following the prior text would have seen two false mismatches and falsely concluded the release was broken.

## [1.3.2] — 2026-05-11

Documentation-only patch that closes the Plan 20 follow-on work (Target Radar brief design cross-link, post-release install smoke checklist, regression-anchor goldens). No code, schema, or skill-bundle changes; `dossier.skill` is content-identical to v1.3.1 modulo `manifest.json`.

### Added

- `features/plan/21-target-radar-brief.md` — stub plan-doc cross-linking the canonical Target Radar brief design that now lives in The Commonplace Book vault (`2026-05-11-target-radar-brief-design`). Target Radar is designed as a Commonplace brief upstream of Dossier, not as a Dossier mode; the stub lets anyone walking the dossier plan folder find their way to the canonical design without inheriting the load-bearing decisions in two places. No implementation work scheduled — the canonical design carries `decay_class: slow` (180-day TTL); if Target Radar is still useful at the next vault audit, that's the signal to schedule implementation. Closes Phase 2 of `features/plan/20-v1-3-1-and-phase-2-foundations.md`.
- `examples/golden/` — three regression-anchor artifacts (`eval-strong-fit.md`, `eval-poor-fit-ghost-job.md`, `eval-injection-response.md`) paired one-to-one with the existing `tests/fixtures/jd_*.md` inputs, plus a folder `README.md` documenting the manual workflow. Each artifact carries a banner explaining that substantive drift on the paired fixture during a Mode 1 change is a release-blocking signal — escalate before merging, update the golden in the same PR with a CHANGELOG note, or revert the change. Goldens exercise three distinct paths: Grade-A / Verified legitimacy, gate-pass-rule firing (Dim 1 + Dim 2 ≤ 2 → D) with Likely-Ghost classification, and the Content Trust Boundary refusing prompt-injection attempts with a Prompt Injection Notice + Suspect-tier classification. Manual workflow, NOT a CI gate — Mode 1 output isn't byte-deterministic and a similarity-metric gate is a separate project. See `examples/golden/README.md` for the diff-and-escalate procedure and how these differ from the four `examples/example-*.md` showpieces.

### Documentation

- `CONTRIBUTING.md` adds a `## Post-release install smoke (manual)` section between "Tagging a Release" and "Routing eval (optional, pre-tag)". Seven-step checklist (Release page present → assets attached → release notes match CHANGELOG → checksum verifies → manifest matches tag → install loads → Mode 1 produces a well-shaped eval, optional security check on the injection fixture) the maintainer runs after `release.yml` reports green. Closes the gap between the workflow's structural `verify_skill_artifact.py` smoke (valid ZIP, required entries) and the user-facing install path (download from Release URL, verify sha256, load into Claude, run a mode). Resolves the P2 item the v1.3.0 reviewer flagged and Plan 20 explicitly deferred out of v1.3.1 to keep it docs-only.

## [1.3.1] — 2026-05-11

Documentation-only patch closing the punch list surfaced in the v1.3.0 review. No code, schema, or skill-bundle changes; `dossier.skill` is byte-identical to v1.3.0 modulo `manifest.json`.

### Documentation

- `tests/README.md`: CI section now lists all five jobs (`test`, `pii-scan`, `changelog-check`, `conventional-commits`, `skill-parity`) instead of the stale "two jobs / three checks" claim from before PRs #42 and #50 landed. Directory tree refreshed to include all 21 test files currently on disk (was missing 11 added since the README was last updated). Test Statistics block replaced its hard-pinned "Total tests: 123" (actually ~180 today) with a self-derived pointer (`pytest --collect-only -q | tail -1`) and named coverage areas — the count drift problem doesn't return on the next PR. Failure-example block replaced `test_skill_zip_contains_exactly_two_files` (no longer exists) with `test_zip_has_no_unexpected_top_level_entries` from the current frozen-17-entry design.
- `DATA_CONTRACT.md`: Summary Table System Layer row now includes `Diagram.md`, matching the system-layer code block at line 59. Adds a parenthetical disambiguation between the `mode7-salary-negotiation.md` reference filename and the Derived Files `negotiation/` folder so readers don't confuse the two.
- `README.md` §Upgrading: hard-coded `v1.2.0` URLs in the bash example replaced with `<tag>` placeholders plus a one-line "substitute with the release you're upgrading to (e.g. v1.3.0)" comment. The example was documentation about *how to upgrade in general*, not a current-release pointer, so a placeholder removes the maintenance treadmill of bumping the example with every release.

## [1.3.0] — 2026-05-11

This release lands the audit-cleanup series (PRs #47–#54). No backwards-incompatible changes: `B-` and `Batch-Evaluated` were removed from schemas but neither was ever emitted by any mode; everything else is additive. Routing-evals run before tagging scored 0.967 (43.5/45 credit; three pre-existing ambiguous-mode partial-credits; no regressions from the cleanup).

### Added

- `skill/SKILL.md` now contains an explicit `## Integrity Rules` section (grade honestly, don't fabricate, draft only, archive don't delete) directly below the Content Trust Boundary. Previously these rules lived only in `CLAUDE.md`, which is not part of the shipped `dossier.skill` bundle — meaning a user installing the skill in a Cowork project without cloning the repo had no in-skill copy of the integrity constraints. `PRIVACY.md` and `SECURITY.md` now cross-reference the Content Trust Boundary as the prompt-injection mitigation mechanism.
- `Offer-Declined` added as a first-class `status` value (distinct from `Passed`, which now strictly covers withdrawing *before* an offer was received). State-machine transition table gains the corresponding row.
- `examples/example-cover-letter.md` — fourth reference artifact, completing the canonical set covering Mode 1 (eval), Mode 5 (outreach), Mode 3 (prep), and Mode 6 (cover letter). Uses the same fictional *Cipher Analytics / Senior Data Platform Engineer* narrative as the existing examples so the four artifacts form a coherent end-to-end set.
- `tools/setup-hooks.sh` — idempotent one-shot opt-in for the commit-msg hook. Resolves repo root from its own location, verifies `.githooks/commit-msg` is present, runs `git config core.hooksPath .githooks`, and reads back to confirm. Works under POSIX shells and Git Bash on Windows. `CONTRIBUTING.md` updated to point at the helper.
- CI `skill-parity` job (`.github/workflows/ci.yml`) — runs `build_skill.sh` on every PR and push to `main`, exiting non-zero if the freshly-built bundle's content drifts from the committed `dossier.skill`. Previously the guard only ran on tag pushes via `release.yml`, meaning a contributor could edit `skill/*.md` without repacking and CI would still greenlight the PR.
- `tests/test_cc_pattern_parity.py` — asserts the Conventional Commits regex is identical between `.githooks/commit-msg` (client-side) and `.github/scripts/check_conventional_commits.sh` (server-side).
- `tests/test_dashboard.py` — light syntactic checks on `dashboard.md`'s Dataview code blocks (fence pairing, balanced parens, FROM clause presence). Dataview silently renders an empty table on a broken query rather than erroring, so this catches typos that would otherwise ship invisibly.
- `tests/test_terminal_archival.py::test_no_cold_detection_implementation_symbols` — regression test that fails loudly if any implementation symbol for the deferred cold-detection feature (`cold_threshold_days`, `days_until_cold`, `stale_application_days`, `auto_archive_cold`) lands under `skill/` while the docs still describe it as manual.

### Fixed

- Skill schema canonicalization: removed unused `B-` grade (the conversion table in `mode1-offer-evaluator.md` never produced it); added `Superseded` and `Offer-Declined` to the `status` enum in `README.md` (both were already used as terminal statuses in narrative docs but missing from the schema); fixed `Offer Declined` → `Offer-Declined` typo in `PRIVACY.md`; aligned optional frontmatter fields (`notes`, `source`, `referral_contact`, `application_method`, `model`, `sources`) across `README.md`, `skill/SKILL.md`, and `skill/references/file-conventions.md`. `tests/test_vault_schema.py` `VALID_GRADES` and `VALID_STATUSES` aligned to the canonical schema.
- Mode 7 (Salary Negotiation) now saves to a dedicated `negotiation/` folder instead of the vault root; folder registered in `skill/references/file-conventions.md` with a `type: negotiation` schema.
- Mode 12 (Batch Pipeline) dedup step no longer shells out to POSIX `find` (broke on Windows); now uses the skill's existing Glob tool. Notion sync section drops the undocumented `Batch-Evaluated` status in favor of the canonical `Evaluating` per the state machine.
- `requirements.txt` now installs `tomli` on Python <3.11 (`tests/test_cliff_config.py` imports it as a fallback for the stdlib `tomllib` that landed in 3.11). CI matrix is 3.11+3.12 so it passes today, but any contributor running tests locally on 3.10 hit `ModuleNotFoundError`.
- `tests/test_commit_msg_hook.py` now copies the hook with `write_bytes`/`read_bytes` instead of `write_text`/`read_text`. On Windows, the text-mode copy translated LF to CRLF and would corrupt the bash shebang, making the hook fail with `bad interpreter` on Windows test runs.

### Documentation

- `DATA_CONTRACT.md` "What's inside `dossier.skill`" updated from the stale two-file description to the actual 17-file layout (`SKILL.md`, `manifest.json`, 15 references). Derived Files section now mentions the `negotiation/` folder. Notion section now points readers at the canonical sync rules in `config.template.md` and `skill/SKILL.md §Pipeline Tracker` instead of a dead-end `PRIVACY.md` pointer. `Diagram.md` added to the system-layer file list.
- `README.md` — new `## Upgrading` section with the two upgrade paths (clone vs. release artifact) including SHA256 verification. `Diagram.md` added to the system-layer file list under §Governance. Data-retention section now notes that 90-day cold detection is manual today.
- `START_HERE.md` — mode-list section now distinguishes the six user-facing entry points from the additional capability modes (Mode 0/2.1/8/9/10/11/12/13/Weekly Trend) rather than presenting six modes alongside the "14 named modes" claim with no reconciliation.
- `CLAUDE.md` — integrity rule for archival now notes that Mode 9 auto-proposes terminal-state archival but 90-day cold detection is manual.
- `CONTRIBUTING.md §"Tagging a Release"` — pre-tag steps checklist now cross-links to `§"Routing eval (optional, pre-tag)"` (new step 2). A maintainer working through the checklist could previously miss the routing-eval reminder because the two sections were separated by the `---` divider with no internal link.
- `tests/conftest.py` — comment on the `eval_files` fixture explaining why the glob is intentionally scoped to top-level `evals/` and exempts `archive/` (archived evals were valid against older schemas; revalidating them would break local test runs for users who archived under pre-1.3.0 enums).

## [1.2.0] — 2026-05-09

### Added

- Conventional Commits enforcement: `commit-msg` hook (`.githooks/`) + CI check (`.github/scripts/check_conventional_commits.sh`). Opt-in via `git config core.hooksPath .githooks`. Bypass token: `[skip-cc]`. (Plan 19 Stream A)
- `cliff.toml` configures git-cliff for maintainer-aided CHANGELOG promotion at tag time. CC type → section mapping: feat→Added, fix→Fixed, perf/refactor→Changed, docs→Documentation. (Plan 19 Stream A)
- Routing eval harness `tools/run_routing_evals.py` — maintainer-side aid that runs the 45 golden prompts (`tests/golden_prompts/routing_test_set.md`) through the local `claude` CLI with the `skill/SKILL.md` frontmatter as system context, scores routing decisions, and writes a markdown report. Uses Claude Code subscription auth (no Anthropic SDK, no API key). Optional pre-tag check; not a CI gate. (Plan 19 Stream B)

### Changed

- Release workflow's `on.push.tags` glob tightened from `v*` to `v[0-9]*.[0-9]*.[0-9]*` (with pre-release variant). Operational tag prefixes `snapshot-*`, `archive-*`, `wip-*` are now reserved for non-release uses; tags like `v-snapshot-2026-q3` no longer trigger publication. (Plan 19 Stream C)

### Fixed

- `build_skill.sh` byte-match guard reworked as a **content-match** that excludes `skill/manifest.json`. The original byte-match was unworkable because the manifest's `commit` and `version` fields reflect HEAD at pack time and necessarily drift across commits, producing false-positive failures on every PR after the bundle was last regenerated. The content-match preserves the guard's intent (catch stale `skill/` content) without the churn. HARDENING.md §9 updated to match.
- `verify_skill_artifact.py` version regex relaxed from `^v\d+\.\d+\.\d+(-[\w.+]+)?$` to `^v\d+\.\d+\.\d+(-[\w.+-]+)?$` so pre-release suffixes containing hyphens (e.g. `v0.0.0-rc-test`, `v1.0.0-beta-1`) are accepted. Standard semver allows hyphens in pre-release identifiers; the original regex was over-strict.
- `tools/run_routing_evals.py` Windows compatibility: drop `--bare` (which forces `ANTHROPIC_API_KEY` and disables OAuth — defeats the redesign's purpose); resolve `claude` via `shutil.which()` so `subprocess.run` finds the `.cmd` shim on Windows; pass only the SKILL.md frontmatter (~1KB) as `--system-prompt` instead of the full body (32KB), staying under Windows `CreateProcess` argv limit (~32,767 chars). Frontmatter-only is also the more accurate model of real routing — Claude only sees the description when picking a skill, not the body.

## [1.1.0] — 2026-05-08

### Added

- Deterministic skill packer (`.github/scripts/build_skill.sh`) replaces manual repack. `dossier.skill` now contains `skill/manifest.json` and pinned `2026-01-01` timestamps for byte-stable rebuilds.
- CHANGELOG gate (`.github/scripts/changelog_check.sh`) added as a CI status check on PRs. Touching `skill/`, `tests/`, or `dossier.skill` requires a corresponding entry under `## [Unreleased]`. Bypass token: `[skip-changelog]`.
- Tag-triggered GitHub Release workflow (`.github/workflows/release.yml`). Pushing an annotated `v*` tag to `main` builds `dist/dossier-<tag>.skill` + `.sha256`, runs the structural smoke verifier, awk-extracts the matching CHANGELOG section as release notes, and creates the GitHub Release. Workflow declares `contents: write`; CI's `contents: read` is unchanged.
- Status/outcome state machine — `skill/references/status-outcome-state-machine.md` defines a transition table binding every `status` value to an `outcome` value. Mode 1 sets the initial `(Evaluating, Pending)` pair; Mode 9's Application Status Sync proposes `(status, outcome)` updates together from email signals; Mode 0 health check flags any eval whose pair is not a row in the table. Last-event-wins — a rejection email applied to an `outcome: Interview` eval moves it to `(Rejected, Rejected)` without preserving the prior outcome. 90+ days cold detection is deferred (requires date arithmetic not yet implemented).
- Automatic terminal archival — `skill/references/terminal-archival.md` defines the archival procedure. When Mode 9's Application Status Sync proposes a terminal status (`Rejected`, `Passed`, `Offer-Declined`), the same batch approval also moves the company bundle (eval + outreach + cover-letter + interview-prep) into `archive/[slug]/`, preserving original folder nesting. Repeat archivals of the same company are versioned (`archive/[slug]-v2/`, `-v3/`, …) rather than merged. Path-style cross-references to artifacts being moved are silently rewritten to wikilink form so they survive the relocation. 90+ days cold detection remains manual.
- Interview story tagging — `skill/references/story-tagging.md` defines how Mode 3 matches `stories.md` entries to a prep artifact by tag overlap (top 3–4 matches, substring + case-insensitive). Prep frontmatter gains a `related_stories:` list of Obsidian heading wikilinks (`"[[stories#Story Title]]"`). Back-references are proposed as a single approval batch: `**Used in:**` lines appended under each matched story in `stories.md`. `stories.md` remains user-layer — no reformatting, no tag rewrites, only the sanctioned `**Used in:**` mutation on approval.

### Changed

Routing ablation experiment (45-prompt golden test set, monolithic vs. five-skill split) found that splitting degraded 17.8% of prompts — all compound multi-step workflows — exceeding the 10% degradation threshold. Decision: remain monolithic. The experiment identified three description gaps that are fixed regardless of split decision:

- SKILL.md description: added `"tailor my CV"` as an explicit trigger phrase (Mode 11 was only reachable via body text)
- SKILL.md description: added `"health check"` and `"calibration report"` as explicit trigger phrases (Modes 0 and 13 had no description coverage)
- SKILL.md description: added negative scope sentence — `"Only trigger when there is a clear job application, offer, interview, or outreach context."` — to reduce false-positive risk on adjacent analytics topics
- LinkedIn pulse dedup v2 — the AM/PM pulse scheduled prompts now deduplicate not just by Gmail thread ID but by a `{recruiter_key}|{role_key}` fingerprint. Fuzzy match on 3-of-4 role-key tokens catches minor title variants; 21-day grace period re-surfaces genuinely stale follow-ups. `.lead-pulse-state.json` gains a `seen_fingerprints` array alongside `seen_thread_ids`; both cap at 200 entries, oldest-first. Fingerprint-suppressed leads are counted in a footer when the run also has surviving leads. Full spec in `features/plan/14-lead-pulse-dedup-v2.md`.
- Recruiter inbox pulse broadening — the pulse (renamed from "LinkedIn Pulse" to "Recruiter Inbox Pulse") now scans across LinkedIn, Indeed, Dice, and Google job alerts, broadened cold-recruiter keywords, and a new Query 6 for application-status signals (application confirmations, interview invitations, rejections, "next steps"). A fourth classification category `📋 STATUS UPDATE` is added alongside `✓ MATCH` / `? UNCLEAR` / `✗ SKIP`. Leads-file output gains a separate `## Application Status Updates` section. Skill-boundary rule enforced: the pulse remains read-only; STATUS UPDATE entries always route to Mode 9 (Application Status Sync) for the actual transition via the status/outcome state machine and terminal-archival flow. Q6 status signals dedupe by thread ID only (no fingerprinting). Full spec in `features/plan/15-recruiter-inbox-pulse-broadening.md`.

### Planned

- 90+ days cold auto-detection — flag stale `Applied` or `Interviewing` evals that have gone cold, and propose terminal archival automatically (requires date arithmetic not yet implemented).
- Scoring calibration feedback loop — use Mode 13 calibration reports to auto-adjust dimension weights when grade-to-outcome correlation data is sufficient.

## [1.0.0] — 2026-04-16

### Added

- Vault-first architecture: all pipeline state owned by local markdown files
- 14 workflow modes: Evaluate (Mode 1), Search (Mode 2), Portal Scan (Mode 2.1), Interview Prep (Mode 3), Company Research (Mode 4), Outreach (Mode 5), Cover Letter (Mode 6), Salary Negotiation (Mode 7), LinkedIn Browser (Mode 8), Gmail Inbox (Mode 9), Calendar Ops (Mode 10), Tailored CV with ATS export (Mode 11), Batch Pipeline (Mode 12), Calibration Report (Mode 13)
- Mode 0 health check with 6 validation checks
- 10-dimension scoring system with gate-pass override and configurable weights
- Notion optionality — Notion tracker is an optional mirror, not a requirement; vault-first workflow works without any Notion configuration
- Skill refactor: SKILL.md restructured to under 500 lines with 11 reference files in `references/` directory, loaded on demand to stay within token budget
- Open-source release: `open-source/` subfolder with PII-clean content, template personal files (`cv.template.md`, `profile.template.md`, `stories.template.md`, `config.template.md`), and public README
- `examples/` directory with fictional-company reference artifacts showing correct frontmatter, naming, and content structure
