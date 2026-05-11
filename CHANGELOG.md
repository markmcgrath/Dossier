# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `examples/example-cover-letter.md` — fourth reference artifact, completing the set covering Mode 1 (eval), Mode 5 (outreach), Mode 3 (prep), and now Mode 6 (cover letter). Uses the same fictional "Cipher Analytics / Senior Data Platform Engineer" narrative as the existing eval and outreach examples so the four artifacts form a coherent set. `CONTRIBUTING.md:29` had flagged the gap. `tests/test_vault_files.py` extended to require the new file by name (`test_examples_directory_has_required_files`) plus a `type: cover` frontmatter test.
- `skill/SKILL.md` now contains an explicit `## Integrity Rules` section (grade honestly, don't fabricate, draft only, archive don't delete) directly below the Content Trust Boundary. Previously these rules lived only in `CLAUDE.md`, which is not part of the shipped `dossier.skill` bundle — meaning a user installing the skill in a Cowork project without cloning the repo had no in-skill copy of the integrity constraints. `PRIVACY.md` and `SECURITY.md` now cross-reference the Content Trust Boundary as the prompt-injection mitigation mechanism.

### Fixed

- Skill schema canonicalization: removed unused `B-` grade (the conversion table in `mode1-offer-evaluator.md` never produced it); added `Superseded` and `Offer-Declined` to the `status` enum in `README.md` (both were already used as terminal statuses in narrative docs but missing from the schema), and added the missing `Offer-Declined` row to the status/outcome state-machine transition table; fixed `Offer Declined` → `Offer-Declined` typo in `PRIVACY.md`; aligned optional frontmatter fields (`notes`, `source`, `referral_contact`, `application_method`, `model`, `sources`) across `README.md`, `skill/SKILL.md`, and `skill/references/file-conventions.md`.
- Mode 7 (Salary Negotiation) now saves to a dedicated `negotiation/` folder instead of the vault root; folder registered in `skill/references/file-conventions.md` with a `type: negotiation` schema.
- Mode 12 (Batch Pipeline) dedup step no longer shells out to POSIX `find` (broke on Windows); now uses the skill's existing Glob tool. Notion sync section drops the undocumented `Batch-Evaluated` status in favor of the canonical `Evaluating` per the state machine.

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
