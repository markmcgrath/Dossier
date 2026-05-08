---
type: plan
feature: version-tag-release-pipeline
status: shipped
closed: 2026-05-08
created: 2026-05-07
author: claude
tags: [release, ci, packaging, hardening, versioning, github-actions]
related: "[[09-release-hardening-execution]], [[10-skill-refactor]], [[16-test-suite-hardening]]"
---

# Plan 18 — Version-Tag-Triggered Release Pipeline

## Why this plan exists

Dossier already has the *artifacts* of a public release — `dossier.skill` (a deterministically packed ZIP), a `CHANGELOG.md` in Keep-a-Changelog 1.1.0 form, a passing CI matrix on Python 3.11/3.12, a hardening record (`HARDENING.md`), and a ruleset that gates merges on `pii-scan` + tests. What it does **not** have is a *release event*: there is no automation that, on `git push origin v1.1.0`, builds a versioned, checksummed `.skill`, attaches it to a GitHub Release, and pulls the matching `## [Unreleased]` (or tagged) section out of `CHANGELOG.md` as release notes.

The Commonplace Book skill — Dossier's sibling project in this workspace — has exactly this. The release lives at `Claude Stack/CommonplaceBook/.github/workflows/release.yml`, triggered on `push.tags: v*`, calling `.github/scripts/build_skill.sh` to produce `dist/commonplace-<tag>.skill` plus a `.sha256`, verifying the artifact extracts and runs `python -m operations --help` from a scratch directory, extracting the matching CHANGELOG section, and creating the GitHub Release via `gh release create`. That pattern is proven, in production, and ready to be copied.

This plan adapts that proven pattern to Dossier — copying its mechanics where they apply, adjusting where Dossier differs, and capturing the trade-offs explicitly.

## Goals and non-goals

**Goals.**

1. A push of an annotated tag matching `v*` to `main` produces a GitHub Release with a versioned `dossier-<tag>.skill` and `dossier-<tag>.skill.sha256` attached, and the CHANGELOG section for that tag (or `[Unreleased]` if the tag has no section yet) as the release body.
2. The artifact is verified before publication: it must extract cleanly, contain the expected layout, and pass an isolation smoke test.
3. The CHANGELOG gate that already governs PRs — schema/skill/tests touch ⇒ `## [Unreleased]` must gain a line — is preserved unchanged. Tagging a release is the *consumption* of the Unreleased section, not a bypass of it.
4. The release manifest captures `version`, `built_at`, and `commit` inside the ZIP so an installed skill can self-identify.
5. Branch protection and required-status-check posture from `HARDENING.md` is preserved end-to-end. The release workflow gets the minimum permissions needed (`contents: write` on `release.yml` only; CI stays at `contents: read`).

**Non-goals.**

1. Publishing to PyPI, npm, or any external registry. The artifact remains a GitHub Release asset, consistent with the Commonplace pattern.
2. Cosign / Sigstore / SLSA provenance. Worthwhile in principle; out of scope for this plan because Commonplace also defers it and adopting it Dossier-only would be inconsistent across sibling projects. Tracked in `## Open questions` below.
3. Versioning the `examples/` content separately. The skill version is the project version. Examples drift with the skill.
4. Re-architecting the `dossier.skill` packaging itself. The current deterministic-pack rules from `HARDENING.md §9` (sorted file order, pinned timestamps, DEFLATE) are preserved verbatim and ported into the `build_skill.sh` script.

## What Dossier inherits from Commonplace's pattern

The Commonplace `release.yml` and `build_skill.sh` are the reference implementation. Concretely:

- **Trigger.** `on: push: tags: ["v*"]`. Concurrency keyed on `github.ref` so two simultaneous tags-of-the-same-name can't race.
- **Permissions.** Workflow-level `contents: write`. CI keeps `contents: read`.
- **Build path.** `bash .github/scripts/build_skill.sh` produces `dist/dossier-<version>.skill` plus `dist/dossier-<version>.skill.sha256`. The script is stdlib-portable: it uses Python's `zipfile` rather than the `zip` binary so the same script runs on Linux CI, macOS, and Git-Bash on Windows.
- **Version resolution.** Annotated `v*` tag at HEAD ⇒ tag string. Else `v<latest-tag>-dev+<short-sha>`. Else `v0.0.0-dev+<sha>`. Override via `DOSSIER_VERSION=...` (Commonplace uses `CP_VERSION`; mirror the convention with the project prefix).
- **Manifest.** A `manifest.json` is written into the ZIP root with `name`, `version`, `built_at` (UTC ISO-8601), and `commit`. Lets the installed skill self-identify and lets `tests/test_package.py` assert layout.
- **Verification step.** After build, the workflow extracts the ZIP to a `mktemp -d`, asserts the layout, and runs a smoke check. For Commonplace this is `python -m operations --help` and `python -m executor --help` because the package is Python. Dossier's smoke is different — see `## Adaptations` §1.
- **Release body.** Awk-extracts the section matching `## [<tag-without-v>]` from `CHANGELOG.md` if present; falls back to `## [Unreleased]`; falls back to a placeholder. Stashes to `/tmp/release-notes.md` and feeds via `gh release create --notes-file`.
- **Asset upload.** `gh release create "${GITHUB_REF_NAME}" --title "${GITHUB_REF_NAME}" --notes-file /tmp/release-notes.md "${artifact}" "${checksum}"`. No release-draft step — the tag push *is* the publication intent.

## Adaptations specific to Dossier

These are the points where Dossier diverges from the Commonplace template. Each adaptation is a deliberate choice; copying Commonplace's version blindly would produce a broken or wrong-shaped artifact.

### 1. Smoke test target

Commonplace's smoke runs `python -m operations --help`. Dossier's `.skill` is not a Python package — it is a markdown skill bundle (`SKILL.md` + `references/` + `scoring-guide.md`). The smoke test is therefore *structural*, not executable:

- The artifact must be a valid ZIP.
- Top-level entries are exactly `SKILL.md`, `references/`, and `scoring-guide.md` (no extra files; specifically no `.pytest_cache/`, `__pycache__/`, `.DS_Store`).
- `SKILL.md` is parseable as YAML-frontmatter-then-markdown.
- Description length is ≤ 1024 chars (matches the existing routing-golden test from `HARDENING.md §7`).
- Reference files referenced by SKILL.md exist in `references/`.

This smoke is a Python script invoked from the workflow, not the skill itself. Naming: `.github/scripts/verify_skill_artifact.py`. Borrows logic from `tests/test_package.py`, which already implements all of these checks against the on-repo `dossier.skill` — the difference is that it points at the freshly built artifact in `dist/` rather than the committed copy.

### 2. Repo-committed `.skill` vs. release-attached `.skill`

Commonplace does **not** commit its `.skill` to the repo — it is built fresh per release. Dossier currently **does** commit `dossier.skill` (53 KB, last regenerated 2026-05-07 03:32). This is a deliberate Dossier choice (`HARDENING.md §8`: "the shipped repo intentionally contains [...] `dossier.skill` (ZIP artifact rebuilt deterministically from `skill/`)"). Two reasons it's worth keeping:

- The skill is consumed by humans manually downloading from the repo or `git clone`-ing it, not by a package manager. Having the artifact at `HEAD` lets users skip the GitHub Releases page.
- The committed copy is a forcing function for "skill source and skill bundle stay in sync" — drift surfaces as a dirty diff, not as a silent staleness.

The release workflow therefore needs to handle the committed copy:

- Build a fresh artifact under `dist/`, sized + checksummed, and attach *that* to the Release. Do not attach the repo-committed copy directly.
- Verify the freshly built artifact byte-matches `dossier.skill` at HEAD. If they differ, fail the release with a diagnostic — this means a contributor edited `skill/` without re-packing, and the repo-committed bundle is stale. (This guard is the analog of Commonplace's `golden-check` job, which catches the same class of drift for golden test data.)
- The byte-match guard is conditional on the existing deterministic-pack rules holding (`HARDENING.md §9`). If those rules are ever loosened, the byte-match step has to be loosened to a structural-match step (same files, same contents, ignore mtimes) or removed.

### 3. CHANGELOG section name convention

Commonplace's CHANGELOG uses bracketed version headings (`## [0.1.0] — 2026-04-30`), and the awk extractor matches `^## \[?${tag#v}\]?`. Dossier's CHANGELOG already follows the same convention (`## [1.0.0] — 2026-04-16`), so the awk pattern transfers verbatim. Confirmed by reading `CHANGELOG.md` lines 1–32.

### 4. Pre-release tag handling

Commonplace's pattern accepts any tag matching `v*`, which also matches `v1.0.0-rc1` or `v0.2.0-beta`. For Dossier, accept the same range — pre-release tags are useful for shaking out a release candidate before the public tag — and document in the workflow comments that pre-release tags do not require a CHANGELOG section (the awk fallback to `[Unreleased]` covers this).

### 5. Skill source layout

Commonplace ships with `skill/SKILL.md`, `skill/references/`, `skill/operations/`, `skill/executor/`, `skill/bin/`. Dossier ships with `skill/SKILL.md`, `skill/references/`, and a top-level `scoring-guide.md` (not nested under `references/`). The build script's file-list must reflect this — copying Commonplace's `cp -R skill/ stage/` works **only because Dossier also keeps everything bundle-shipped under `skill/`**. Confirmed by inspecting `skill/`. If `scoring-guide.md` is ever moved out of `skill/`, the build script must be updated to copy it explicitly. Add a regression test that asserts the staged tree contents match a frozen list.

### 6. Workflow token permission scoping

Commonplace's `release.yml` declares `permissions: contents: write`. This is the minimum needed to call `gh release create`. Dossier's existing `ci.yml` declares `permissions: contents: read` at the workflow level. The release workflow must declare its own elevated `contents: write`; **do not bump the repo default**, which would also widen the CI workflow's grant. This matches `HARDENING.md §3`'s least-privilege posture.

### 7. Branch-protection interaction

`HARDENING.md §1` records that `main` requires `pii-scan`, `test (3.11)`, and `test (3.12)` as required status checks. The release workflow runs *after* a tag is pushed, which by default is *not* on `main` — but the tag is expected to point at a commit that already merged into `main` and therefore already passed all three. The release workflow re-runs the test suite as defense-in-depth (Commonplace pattern, identical here), but this is belt-and-braces, not a substitute for the merge-time gate. Document in `HARDENING.md §3` that `release.yml` is not a required status check (it cannot be — it triggers on tag push, not branch push) and explain the rationale.

### 8. Maintainer-visible failure modes

The Commonplace release workflow has accumulated some hard-won lessons (see `Claude Stack/CommonplaceBook/.github/scripts/changelog_check.sh` comments — SIGPIPE issues with `set -o pipefail`, awk-extraction edge cases when the heading is in a different hunk than the addition). When porting `changelog_check.sh` and the awk-section-extractor logic to Dossier, **copy them in their post-fix form** (variable-capture-then-match, two-pass section extraction, etc.) and link the comments back to the Commonplace project history rather than re-deriving the fixes.

### 9. Release vs. dossier.skill commit cycle

Today, `dossier.skill` is regenerated and committed manually before tagging. After this plan ships, the canonical workflow is:

1. Maintainer makes changes under `skill/`.
2. Maintainer (or a pre-commit / CI step) regenerates `dossier.skill` deterministically.
3. Both source and bundle are committed in the same PR.
4. PR merges to `main` (CI green).
5. Maintainer updates `CHANGELOG.md` `## [Unreleased]` → `## [1.1.0] — YYYY-MM-DD` if not already done; tags `v1.1.0`; pushes the tag.
6. Release workflow fires; builds a fresh `dist/dossier-v1.1.0.skill`; asserts byte-match against the committed `dossier.skill`; runs the smoke test; awk-extracts release notes; creates the GitHub Release.

Step 2 may be automated later (a pre-commit or a CI job that fails the PR if `dossier.skill` is stale relative to `skill/`). For this plan, manual is fine and matches existing posture.

## File-by-file deliverables

| Path | Purpose | Source pattern |
|---|---|---|
| `.github/workflows/release.yml` | Tag-triggered release workflow | Port from `Claude Stack/CommonplaceBook/.github/workflows/release.yml`; adjust permissions and smoke step |
| `.github/scripts/build_skill.sh` | Deterministic skill packer | Port from Commonplace; replace Commonplace-specific stage layout (operations/executor/bin) with Dossier's (SKILL.md + references/ + scoring-guide.md); add the byte-match-against-committed-bundle assertion |
| `.github/scripts/verify_skill_artifact.py` | Structural smoke for the freshly built artifact | New; mirrors the assertions in `tests/test_package.py` but points at `dist/dossier-*.skill` |
| `.github/scripts/changelog_check.sh` | PR-time CHANGELOG gate | Port from Commonplace's post-fix form; adjust `GATED_PATTERN` to Dossier's gated paths (`skill/`, `tests/`, schema docs if/when they exist) |
| `CHANGELOG.md` | Already exists; no schema changes | The release workflow's awk extractor reads it as-is |
| `HARDENING.md §3` | Add a note on the release workflow's `contents: write` scope and why it isn't a required status check | Edit; one paragraph |
| `HARDENING.md §7` | Add a note that the existing CI matrix is run *again* by the release workflow as defense-in-depth | Edit; one bullet |
| `HARDENING.md §11` | Add a row for "release-time secret scanning" — GitHub's built-in scanner already covers PRs; the release workflow is on the same default policy | Edit; one row |

## Streams and ordering

Streams A and B are independent. C depends on A. D depends on A and C.

| Stream | Name | Estimated effort | Depends on |
|---|---|---|---|
| A | Port `build_skill.sh` and the structural smoke | 2–3 hours | — |
| B | Port `changelog_check.sh` to Dossier and wire it into `ci.yml` as a fourth required status check | 1–2 hours | — |
| C | Add `release.yml` and exercise it on a `v0.0.0-test` tag against a private fork | 2–3 hours | A |
| D | Update `HARDENING.md`, `README.md` install instructions, and the Triage Summary in `09-release-hardening-execution.md` to record this plan as the closure of the originally-deferred release automation | 1 hour | A, C |

Total: 6–9 hours.

### Stream A — `build_skill.sh` and structural smoke

1. Create `.github/scripts/build_skill.sh` from the Commonplace template. Reproduce its version-resolution branch (`DOSSIER_VERSION` override, exact-match tag, latest-tag + sha, fallback). Set `OUT="${DIST_DIR}/dossier-${VERSION}.skill"`.
2. Replace the `cp -R "${SKILL_DIR}/" "${STAGE}/"` step with the Dossier-shaped copy (`skill/SKILL.md`, `skill/references/`, `skill/references/scoring-guide.md` — confirmed layout).
3. Reproduce the strip step (`__pycache__`, `.pyc`, `.DS_Store`, etc.). Most of these don't exist in `skill/`, but the strip is cheap and matches Commonplace's posture.
4. Write `manifest.json` with `name: "dossier"`, `version`, `built_at`, `commit`. Dossier currently has no manifest in the bundle; this is a net-new addition. Update `tests/test_package.py` to expect the manifest.
5. Reproduce the Python `zipfile` packing loop (sorted directory walk, deterministic insertion, executable bits preserved if any — Dossier has no `bin/`, but keep the bit-preservation logic so the script is identical to Commonplace's where possible).
6. Reproduce the SHA256 sidecar generation.
7. Add the byte-match-against-committed-bundle step at the end: `cmp -s dist/dossier-${VERSION}.skill dossier.skill || { echo "fresh artifact differs from committed dossier.skill"; exit 3; }`. Failure mode is informative — the script exits 3, distinct from build (1) and usage (2) errors.
8. Create `.github/scripts/verify_skill_artifact.py`. Reuse assertions from `tests/test_package.py`. Take the artifact path as `sys.argv[1]`. Exit 0 on pass, 1 with a diagnostic on fail.

### Stream B — `changelog_check.sh`

1. Copy the Commonplace `changelog_check.sh` verbatim.
2. Replace `GATED_PATTERN` with `'^(skill/|tests/|dossier\.skill$)'`. The third alternation is Dossier-specific: a change to the committed `.skill` bundle is itself a release-relevant change, so it forces a CHANGELOG entry.
3. Wire into `ci.yml` as a new `changelog-check` job, conditional on `github.event_name == 'pull_request'`, with `fetch-depth: 0`. Mirror the Commonplace job exactly.
4. Add `changelog-check` to the required-status-checks list in the `Public` ruleset (`HARDENING.md §1`). Document in the same edit.

### Stream C — `release.yml`

1. Copy `Claude Stack/CommonplaceBook/.github/workflows/release.yml` to `.github/workflows/release.yml`.
2. Rename `commonplace-` artifact patterns to `dossier-`.
3. Replace the install + test step with Dossier's: `pip install -r requirements.txt` then `python -m pytest tests/ -v` (Dossier uses requirements.txt + plain pytest, not `pip install -e ".[test]"`).
4. Replace the verification step with `python .github/scripts/verify_skill_artifact.py "$art"`.
5. Tag-test on a private fork with `v0.0.0-rc-test` to confirm: tag push fires, tests run, artifact builds, smoke passes, byte-match passes, CHANGELOG fallback to `[Unreleased]` works, GitHub Release is created with both assets attached. Roll back the tag and the test release before merging the workflow to `main`.

### Stream D — Documentation

1. Update `HARDENING.md` per the file-by-file table above.
2. Update `README.md` "Install" / "Get the skill" section (if present; if not, add) to point users at the GitHub Releases page in addition to the repo-committed `dossier.skill`. Mention that release assets carry checksums.
3. Update `features/plan/09-release-hardening-execution.md` triage summary: the originally-deferred release automation is now closed by this plan. Cross-link this plan from there.
4. Update `CHANGELOG.md` `## [Unreleased]` with the workflow addition before tagging — this is the meta-test that the gate works.

## Risks and gaps

**1. Tag-on-wrong-commit.** A maintainer could tag a commit that didn't pass CI. Mitigation: the release workflow runs the test suite again. Cost: ~3 minutes per tag. Worth it.

**2. CHANGELOG section name drift.** If a future contributor uses `## [v1.1.0]` instead of `## [1.1.0]`, the awk extractor's pattern `^## \[?${tag#v}\]?` still matches both — the `?` after the bracket and `${tag#v}` handle it. Verified by tracing the regex against both forms. No mitigation needed.

**3. `gh` CLI version skew.** GitHub-hosted runners ship a recent `gh`. If a release ever runs on a self-hosted runner, pin the gh version. Out of scope today (no self-hosted).

**4. Pre-release tags with no CHANGELOG section.** The fallback to `## [Unreleased]` covers this, but a maintainer might tag `v0.9.0-beta` while `[Unreleased]` is empty. The Commonplace pattern handles this with a placeholder line. Inherit it.

**5. `dossier.skill` byte-mismatch on release.** This is the byte-match guard's *purpose*, but the failure mode is operationally annoying — the maintainer has to delete the tag, regenerate the bundle, recommit, and retag. Document the recovery flow in `HARDENING.md §9` so the failure is recoverable rather than mysterious.

**6. Releases trigger on any `v*` tag, including operational tags.** Commonplace's `build_skill.sh` already filters with `--match 'v*'` for the version-resolution step ("Only consider tags matching the v<MAJOR>.<MINOR>.<PATCH> family. Other tags (e.g. operational/audit markers) must not flow into the artifact version string."). The workflow trigger pattern `v*` is broader than this but adequate as long as Dossier doesn't introduce non-release tags starting with `v`. Document the convention.

**7. Release workflow privilege escalation.** `contents: write` is the minimum, but it's a step up from `read`. Mitigation: the workflow runs only on tag push, not on PR. A malicious PR cannot exfiltrate via the release workflow because PRs don't trigger it. Documented in `HARDENING.md §3`.

## Open questions

1. **SLSA / Sigstore.** Worth adopting alongside Commonplace, not Dossier-only. Track in a separate cross-project plan if pursued.
2. **Should `dossier.skill` continue to be committed to the repo after this lands?** Today: yes (rationale in §2 of Adaptations). Revisit when releases are stable and users have a clear path to `gh release download`.
3. **CHANGELOG automation.** Today, `## [Unreleased]` is hand-edited and manually promoted to a numbered section at tag time. A future plan could automate the promote step (Conventional Commits → `git-cliff`). Not pursued here because Commonplace also keeps it manual; staying consistent across siblings.
4. **Per-release evals.** Should the release workflow re-run the routing-golden test set against the freshly built bundle? Today: no — the test suite already runs the routing-golden checks, and they don't depend on the bundle layout. Revisit if a future routing test ever loads `dossier.skill` directly.

## Appendix — relevant Commonplace artifacts

These are the upstream files this plan adapts. Linked here as the authoritative reference for the patterns ported into Dossier.

- `Claude Stack/CommonplaceBook/.github/workflows/release.yml` — tag-triggered release workflow.
- `Claude Stack/CommonplaceBook/.github/workflows/ci.yml` — six-job CI matrix; `changelog-check` job is the relevant one.
- `Claude Stack/CommonplaceBook/.github/scripts/build_skill.sh` — deterministic packer with version resolution.
- `Claude Stack/CommonplaceBook/.github/scripts/changelog_check.sh` — CHANGELOG gate with bypass-token, two-pass section extraction, SIGPIPE-safe shape.
- `Claude Stack/CommonplaceBook/.github/scripts/install_skill.sh` — optional companion installer (worth inheriting in a follow-on plan if Dossier wants a scripted install).
- `Claude Stack/CommonplaceBook/CHANGELOG.md` — section-heading conventions the awk extractor depends on.
- The Commonplace Book entry `2026-04-29-commonplace-book-stream-09-skill-packaging.md` — the canonical record of why the upstream pattern is shaped this way.
