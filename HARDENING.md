# Dossier — Repository Hardening Record

This document describes the security and operational posture of this repository. It exists to make the protections auditable and to capture deliberate trade-offs so future changes don't erode them silently.

---

## 1. Branch protection

Ruleset `Public` is active on the default branch (`main`). It applies to `~DEFAULT_BRANCH` with no bypass actors.

**Rules enforced:**

- `deletion` — `main` cannot be deleted.
- `non_fast_forward` — no force-pushes to `main`.
- `pull_request`
  - `required_approving_review_count: 0` (solo maintainer; GitHub does not allow self-approval, so any non-zero value would lock the sole committer out)
  - `required_review_thread_resolution: true` — unresolved review conversations block merge
  - `allowed_merge_methods: ["squash"]` — squash-only
- `required_status_checks` with `strict_required_status_checks_policy: true`
  - `pii-scan`
  - `test (3.11)`
  - `test (3.12)`
  - Strict mode forces the PR branch to be up to date with `main` so CI re-runs against the current base before merge
- `required_linear_history` — reinforces squash-only; blocks merge commits from ever landing

A second ruleset named `Minimal` exists in disabled state as a fallback baseline (deletion + non-fast-forward only).

**Emergency admin changes** (e.g., history rewrites) go through a deliberate cycle: disable the ruleset, perform the action, re-enable, verify. No actor bypasses are carved out.

---

## 2. Repository settings

| Setting | Value |
|---|---|
| Visibility | Public |
| Default branch | `main` |
| Merge commits | Disabled |
| Squash merging | Enabled (default message: "Pull request title and description") |
| Rebase merging | Disabled |
| Auto-merge | Enabled |
| Auto-delete head branch on merge | Enabled |
| Wiki | Disabled |
| Discussions | Disabled |
| Issues | Enabled |
| Projects | Enabled (not actively used) |
| Forking | Allowed |
| Web-commit signoff required | No |

Merge-strategy constraints are enforced twice: at the repo-settings layer and via the `allowed_merge_methods` key on the `pull_request` rule. Either alone would suffice; both together defend against accidental drift in one without the other.

---

## 3. GitHub Actions

Actions are enabled with a deliberately narrow policy:

- `allowed_actions: selected` (not `all`)
- Explicit allowlist: `actions/*`, `dependabot/*`
- **"Allow actions created by GitHub"**: off — the explicit `actions/*` pattern is tighter and documents intent.
- **"Allow actions by Marketplace verified creators"**: off — surface is opened only when a specific external action is needed.
- **SHA pinning required**: off — deliberate trade-off. The repo only uses first-party GitHub actions (`actions/checkout`, `actions/setup-python`) and accepts tag-based pinning for update ergonomics. Dependabot drives tag bumps.

**Default workflow token permissions:**

- `default_workflow_permissions: read`
- `can_approve_pull_request_reviews: false` — the `GITHUB_TOKEN` cannot self-approve PRs

**CI workflow** (`.github/workflows/ci.yml`) declares `permissions: contents: read` at the workflow level — least privilege even below the repo default.

**Operational verification:** The allowlist was end-to-end tested on PR #18. A misconfigured allowlist (patterns saved as a single CRLF-joined string) produced a `startup_failure`; after splitting into two entries via `PUT /actions/permissions/selected-actions`, CI ran successfully.

---

## 4. Dependabot

`.github/dependabot.yml` defines scheduled version updates. Repository-level toggles enabled:

- Malware alerts
- Dependabot security updates
- Grouped security updates (reduces PR noise by bundling compatible updates)
- Version updates
- Self-hosted runners: not applicable (workflows run on GitHub-hosted `ubuntu-latest`)

Dependabot commits author as a separate identity (`dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>`), distinct from any maintainer.

---

## 5. PII & secret scanning

Local gate: `.github/scripts/pii_scan.py`, wired into CI as a required status check.

**Built-in patterns** (committed, public — 8 regexes that match *shapes* of PII/secrets, never actual values):

| ID | Matches |
|---|---|
| `personal-email` | `\b[\w.+-]+@(?:gmail\|outlook\|yahoo\|hotmail\|icloud\|proton\|protonmail)\.(?:com\|me)\b` |
| `anthropic-key` | `sk-ant-[\w-]{20,}` |
| `openai-key` | `\bsk-[A-Za-z0-9]{40,}\b` |
| `google-key` | `\bAIza[\w-]{35}\b` |
| `notion-token` | `\b(?:ntn_[\w]{20,}\|secret_[A-Za-z0-9]{40,})\b` |
| `private-key-block` | `-----BEGIN [A-Z ]*PRIVATE KEY-----` |
| `windows-user-path` | `[Cc]:[\\/]Users[\\/]\w+` |
| `notion-id-hex` | `\b[a-f0-9]{32}\b` |

**Allowlist substrings** (committed) suppress matches for documented fictional examples (`@example.com`, `@example.org`, `@example.net`, `hiring.manager@cipheranalytics.com`, etc.).

**Maintainer-specific regexes** live in `.github/scripts/pii_patterns.local.txt` (gitignored). One Python regex per line, loaded on top of the generic set. The legacy path `.github/scripts/pii_patterns.txt` is still read with a deprecation warning so existing local setups don't silently lose coverage after the rename; both paths are gitignored. The public template at `.github/scripts/pii_patterns.template.txt` documents the format.

**Scope:**

- Scans tracked files only (`git ls-files`), or only staged diff with `--staged`.
- Skips `tests/fixtures/**` (synthetic look-alike data by design).
- Skips a documented set of binary extensions, including `.skill` (the ZIP) — `skill/` source is scanned instead, and `dossier.skill` is rebuilt from that source.

**Success output** explicitly reports whether local patterns were loaded (`(with local patterns)` vs `(generic patterns only)`), so maintainers can confirm scan coverage each run. Either the canonical or legacy local path triggers the "with local patterns" suffix.

**Known limitations — honest:**

1. Scans file *contents* only. Git metadata (author / committer / commit message) is not read. This limitation is what allowed a real personal email to live in commit author metadata for 47+ commits until caught by a manual audit (see §6).
2. `personal-email` regex matches only seven consumer domains. A real corporate-domain email (`recruiter@somecompany.com`) would not be matched.
3. No built-in detection for names, phone numbers, SSNs, or credit card numbers. These belong in the maintainer's local patterns file.
4. The `notion-id-hex` pattern matches any 32-char lowercase hex string; known false-positive sources are explicitly excluded by path (`tests/fixtures/**`).
5. The PII scanner is a first-pass hygiene gate. GitHub's own secret scanning + push protection (see §11) is the compliance-grade complement.

---

## 6. History hygiene

**Commit metadata rewrite.** Prior to the public release, every commit was re-authored via `git filter-repo` to replace a personal consumer-domain email with the GitHub noreply form (`<id>+<username>@users.noreply.github.com`). Completed in a ruleset-disable → force-push → re-enable cycle. Remote `main` now contains zero references to the original email across author, committer, and message fields. A local-only `backup/pre-email-rewrite` ref preserves the pre-rewrite SHAs in case of recovery need.

**Post-rewrite posture:**

- GitHub "Keep my email addresses private" setting: enabled on the maintainer account.
- `git config user.email` set to the noreply form, so any future local commit uses it regardless.
- Dependabot commits were already noreply.

---

## 7. CI and test coverage

**Matrix.** Python 3.11 and 3.12 on `ubuntu-latest`. Triggers: push to `main`, pull_request targeting `main`.

**Required status checks** (all three must pass for merge):

- `pii-scan` — runs the scanner described in §5.
- `test (3.11)` — full pytest suite on Python 3.11.
- `test (3.12)` — full pytest suite on Python 3.12.

**Test surface** (121 passing, 3 skipped as of the last run):

- Routing golden (`tests/test_routing_golden.py`) — guards the SKILL description length (≤ 1024 chars), required trigger phrases, the negative-scope sentence, and cross-document consistency between `routing_test_set.md` and `baseline_results.md`.
- Outcome state machine (`tests/test_outcome_state_machine.py`) — parses the transition table and asserts required `(status, outcome)` pairs, the four skill-side pointers, and example conformance.
- Terminal archival (`tests/test_terminal_archival.py`) — guards the reference file's required content (terminal statuses, bundle scope, `-v2` versioning rule, wikilink rewriting, cold-detection deferral) and the four cross-reference points.
- Story tagging (`tests/test_story_tagging.py`) — guards forward link via `related_stories`, heading-wikilink form, `**Used in:**` back-reference, approval batch rule, top 3–4 match rule, user-layer protection, zero-match behavior.
- Config contract (`tests/test_config_contract.py`) — Notion optionality, config template behavior, fixture parsing.
- Docs consistency (`tests/test_docs_consistency.py`) — cross-document rules, no "Notion primary" language.
- Antipatterns (`tests/test_antipatterns.py`) — vault-first architecture guards (Notion optionality, no mandatory-log phrases, etc.).
- Vault files and schema (`tests/test_vault_files.py`, `tests/test_vault_schema.py`) — required root files, required directories (using `is_dir()` to reject same-named files), example frontmatter shape, schema validation across evals.
- Skill structure (`tests/test_skill_structure.py`) — modes exist, content trust boundary, health check, reference pointers, frontmatter template fields.
- Skill package (`tests/test_package.py`) — `dossier.skill` ZIP contents and sane line count.

---

## 8. Content hygiene

The shipped repo intentionally contains:

- `README.md`, `START_HERE.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`, `PRIVACY.md`, `DATA_CONTRACT.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `.editorconfig`, `.gitignore`
- `skill/` (source markdown) plus `dossier.skill` (ZIP artifact rebuilt deterministically from `skill/`)
- `examples/` — fictional artifacts (Cipher Analytics) with HTML-comment disclaimers after the YAML frontmatter so the parser is not broken
- `features/` — planning archive with a top-level `features/README.md` orientation page
- `tests/` — including `fixtures/` (synthetic config samples) and `golden_prompts/` (ablation test data)

The shipped repo intentionally does NOT contain:

- Real personal files: `cv.md`, `profile.md`, `stories.md`, `config.md` (all gitignored; templates ship instead)
- `.pii_patterns.local.txt` (gitignored, both canonical and legacy paths)
- `archive/dossier-plugin/` — an abandoned plugin conversion attempt, removed from the public release (git history preserves if ever needed)
- `vault-template/` — redundant empty-folder skeleton; the root-level folders already serve that role

**Template-file integrity:** `cv.template.md`, `profile.template.md`, `stories.template.md`, `config.template.md` all use bracketed placeholder markers and are PII-free.

**Cross-reference hygiene:** All `related_*` frontmatter fields use Obsidian wikilink form (`"[[filename]]"` or `"[[stories#Heading]]"`), not path form, so archival moves don't break links.

---

## 9. Operational patterns

- **Every change goes through a PR.** Direct push to `main` is rejected by the ruleset.
- **Squash merges only.** Linear history is enforced.
- **ZIP repack is deterministic.** `dossier.skill` is rebuilt from `skill/` with sorted file order, pinned timestamps (2026-01-01), and DEFLATE compression, so diffs are minimal.
- **User-layer / system-layer separation** is documented in `DATA_CONTRACT.md` and enforced by `.gitignore`. User-layer files (`cv.md`, `profile.md`, `stories.md`, `config.md`, all working folders) are never overwritten by skill updates.
- **Ruleset cycle for admin history changes.** Documented in §1: disable ruleset, perform action, re-enable, verify.
- **Permissions-mode friction is a feature.** Destructive operations (force-push, history rewrite, security policy edits) are gated by the Claude Code permission system. Each gate was lifted only by explicit per-command authorization, not by a broad bypass.

---

## 10. Known trade-offs

Decisions taken deliberately against a stricter alternative, with the reasoning captured:

| Decision | Alternative considered | Why the current choice |
|---|---|---|
| `required_approving_review_count: 0` | `1` | GitHub doesn't allow self-approval; non-zero would lock the solo maintainer out. |
| Bypass actors empty | Add maintainer as bypass | Preserves auditability. Emergency edits go through the ruleset-disable cycle so every force-push is visible. |
| SHA pinning not enforced on Actions | Require 40-char SHA pins | Only uses first-party `actions/*`. SHA pinning adds Dependabot churn for marginal risk reduction. Revisit if external actions are ever added. |
| `allow_forking: true` | Disallow forks | Community contribution is part of the goal. Forks don't receive secrets. |
| `.skill` binary excluded from PII scan | Scan inside the ZIP | The ZIP is rebuilt from `skill/`, which *is* scanned. Scanning both is redundant. |
| `features/` shipped publicly | Strip before publish | The planning archive is evidence of the work behind the skill; it's a feature, not a leak. See `features/README.md` for the drive-by orientation. |

---

## 11. Post-public enablement

GitHub security features that can only be enabled once a repo is public, which complement this document:

- **Dependabot alerts** — already enabled.
- **Secret scanning** — catches 200+ known secret types in content (different from the narrow regex set in §5). Enable in Settings → Code security.
- **Push protection** — blocks commits containing detected secrets before they reach the remote. Enable in the same pane.
- **CodeQL default setup** — static analysis for common vulnerabilities. One-click setup.

Secret scanning specifically closes part of the git-metadata gap called out in §5: it *does* scan commit messages and patch contents, so a future accidental leak in an author email or commit body has an independent safety net.

---

## 12. Review this document when any of the following change

- A rule is added to, removed from, or reconfigured in the `Public` ruleset.
- The Actions allowlist, workflow-token defaults, or SHA-pinning setting changes.
- The PII scanner's pattern set, allowlist, or skip rules change.
- A new required status check is added or removed.
- Repo visibility or merge-strategy settings change.
- Maintainer git identity changes.
- A security feature is enabled or disabled (Dependabot, secret scanning, push protection, CodeQL).

The `git log` on this file is the authoritative record of those changes.
