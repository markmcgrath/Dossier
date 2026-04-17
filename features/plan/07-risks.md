# Risks, Gaps & Open Questions

**Purpose:** Cross-cutting issues that affect multiple streams. Review before starting implementation. Revisit after each stream ships.

---

## Confirmed Risks

These are real problems, not speculative. Each has a mitigation.

### R1 — Skill File Edit Workflow Is Fragile

**Risk:** `dossier.skill` is a ZIP package. Every edit requires extract → modify → repack. A bad repack (wrong directory structure, missing file, corrupted zip) bricks the skill.

**Mitigation:**
- Always back up before extracting (`skill-update/dossier.skill.bak-[date]`)
- After repacking, verify: `unzip -l dossier.skill` should show exactly `SKILL.md` and `scoring-guide.md` at the root level (no nested directories)
- Smoke test after every repack with a real Mode 1 invocation

**Severity:** High — a broken skill package means nothing works until fixed.

**Status:** MITIGATED ✓ (2026-04-15)
Four-backup chain maintained through Streams A–E (bak-2026-04-15, bak-stream-c, bak-stream-d, bak-stream-e, bak-stream-f). Backup-before-edit and `unzip -t` verification followed in every stream.

### R2 — No Regression Testing for Prompt Changes

**Risk:** SKILL.md is 764 lines governing 11+ modes. An edit to Mode 1's scoring section could break Mode 9's status sync if they share conventions. There's no automated test suite for a prompt file.

**Mitigation:**
- After each stream ships, run a manual smoke test of every mode that was *not* edited (regression check)
- Keep a running checklist of "modes touched" per stream to know what to regression-test
- Consider: should each stream include a "regression test" section listing modes to verify?

**Severity:** Medium — failures are catchable by manual testing, but easy to skip under time pressure.

**Status:** OPEN (2026-04-15)
No automated test suite exists. Manual smoke tests were run per stream but not formally tracked or documented per stream.

### R3 — Vault-First Query Performance at Scale

**Risk:** Reading frontmatter from 30+ eval files per query is fine now (11 evals exist). At 200+ evals over a long search, this becomes slow and context-heavy.

**Mitigation:**
- The architecture spec recommends archiving terminal-state evals to keep `evals/` focused on live pipeline
- Mode 0 health check could warn when `evals/` exceeds a threshold (e.g., 50 active files)
- For "read frontmatter only, not body" — this works in Claude.ai via targeted file reads but there's no way to enforce it structurally

**Severity:** Low for now. Revisit if any user reports context-window issues with large pipelines.

**Status:** OPEN (2026-04-15)
Mode 0 health check exists but does not yet warn on vault size threshold. Low severity.

### R4 — Config.md Parsing Depends on Claude's Text Interpretation

**Risk:** Config.md is YAML-in-markdown, but there's no real YAML parser — Claude reads the text and interprets it. Complex nested structures (especially the email automation block with nested lists) could be misinterpreted.

**Mitigation:**
- Keep config structure flat or one-level deep
- Defer the complex `email_automation:` block to Stream F
- Mode 0 health check validates critical values (Notion IDs, domain lists)
- Consider: would a simpler format (key: value pairs, no nesting) be more robust?

**Severity:** Medium — misinterpreted config doesn't crash anything but could cause wrong behavior silently.

**Status:** MITIGATED ✓ (2026-04-15)
Config structure kept flat/one-level deep throughout. Mode 0 validates critical config values.

### R5 — B+ Grade Used But Not Formally Defined

**Risk:** SKILL.md defines grades as A, B, C, D, F (line 204–209). But eval frontmatter allows `B+`, and 3 of 11 existing evals use it (Company A at 4.3, Company B at 4.2, Company C at 4.2). The scoring guide also doesn't mention B+. The dashboard's "Top Priority" query filters for `grade = "A" OR grade = "B+"` — so B+ is load-bearing in queries despite not being in the formal spec.

**Mitigation:** This is a pre-existing inconsistency, not introduced by our plan. The B+ scores all fall in the upper B range (3.75–4.49). Two options:
- **Formalize B+:** Add it to the grade conversion table (e.g., B+ = 4.0–4.49, B = 3.75–3.99). This better matches how it's actually used.
- **Leave as-is:** B+ is a natural refinement that Claude applies when a score is strong-B but not quite A. The dashboard handles it. No urgency to change.

**Severity:** Low — working correctly in practice despite the spec gap.

**Status:** OPEN (2026-04-15)
B+ continues to work in practice. Recommend formalizing B+ = 4.0–4.49, B = 3.75–3.99 in a future scoring guide update.

### R6 — Existing Evals Missing New Frontmatter Fields

**Risk:** Streams C and D add `outcome`, `legitimacy`, `model`, and `sources` fields to the eval frontmatter template. The 11 existing evals don't have these fields. Dashboard queries and Mode 0 spot-checks need to handle missing fields gracefully.

**Mitigation:**
- Mode 0 should treat missing new fields in old evals as "old format" not "broken format"
- Dataview queries should use `WHERE` clauses that tolerate missing fields (e.g., `WHERE outcome` only filters files that *have* the field)
- Consider: should we backfill the 11 existing evals? It's a small enough batch to do manually.

**Severity:** Low — Dataview handles missing fields well. Just don't write queries that assume all fields exist.

**Status:** PARTIALLY RESOLVED ✓ (2026-04-15)
`outcome: Pending` backfilled on all 11 evals during Stream C. `legitimacy` intentionally not backfilled (requires honest re-evaluation). `model` and `sources` are optional provenance fields, not backfilled.

---

## Open Questions

These need answers before or during implementation. Some may resolve themselves; others need explicit decisions.

### Q1 — Should We Backfill Existing Evals?

The 11 existing evals (all dated 2026-04-14) lack `outcome`, `legitimacy`, `model`, and `sources` fields. Options:
- **Backfill now:** Add `outcome: Pending` and `legitimacy: Plausible` to all 11. Takes 15 minutes. Keeps the vault consistent.
- **Leave as-is:** Old evals are old format. New evals get new fields. Queries handle the gap.
- **Recommendation:** Backfill `outcome: Pending` (it's always correct for a new eval). Skip `legitimacy` (we'd need to re-evaluate to assign it honestly).

**Status:** RESOLVED ✓ (2026-04-15)
`outcome: Pending` backfilled on all 11 evals. `legitimacy` skipped (requires honest re-evaluation). Decision: leave `legitimacy` absent on old evals; Dataview handles missing fields gracefully.

### Q2 — Dataview Plugin Assumption

`dashboard.md` relies on the Dataview community plugin. If a user doesn't have Dataview installed, the dashboard shows raw code blocks.

Options:
- **Document the dependency** in README.md and Mode 0 (can Mode 0 detect Obsidian plugins? Probably not.)
- **Provide a non-Dataview fallback** (static markdown tables manually updated — defeats the purpose)
- **Recommendation:** Document the dependency, accept it as a known limitation. Dataview is the most-installed Obsidian community plugin; expecting it is reasonable.

**Status:** OPEN (2026-04-15)
Dependency documented in README.md and examples. Mode 0 cannot detect plugin status. Accepted as a known limitation.

### Q3 — Stories.md Growth Pattern

The story bank is a single file. At 50+ stories it becomes unwieldy. Options:
- **Single file is fine** for a realistic volume (most people have 10–20 strong stories)
- **Split by competency theme** later if needed (`stories/leadership.md`, `stories/technical.md`)
- **Recommendation:** Ship as single file. Revisit if someone actually accumulates 50+ stories (unlikely in a single job search).

**Status:** RESOLVED ✓ (2026-04-15)
Single-file design confirmed. `stories.md` created at vault root. Revisit at 50+ stories.

### Q4 — `gmail_send_message` Availability

The email automation plan's Level 3 (auto-send) depends on this MCP capability. Before starting Stream F.4:
- Check if the Gmail MCP connector exposes `gmail_send_message`
- If not: Level 3 is not viable. The entire email automation plan caps at Level 2 (draft + notify), which is still valuable.

**Status:** RESOLVED — NOT VIABLE ✗ (2026-04-15)
The Gmail MCP connector does NOT expose `gmail_send_message`. Available tools: `gmail_create_draft`, `gmail_get_profile`, `gmail_list_drafts`, `gmail_list_labels`, `gmail_read_message`, `gmail_read_thread`, `gmail_search_messages`. F.4 Level 3 (auto-send) is not viable with the current connector. **F.4 caps at Level 2 (draft + notify) until a send-capable connector is available.**

### Q5 — Skill Description Update

The skill's frontmatter `description` field (lines 2–15 of SKILL.md) mentions "logged to Notion" as a core feature. After vault-first migration, this should be updated to reflect the new architecture. But changing the description could affect skill triggering behavior. Test after changing.

**Status:** RESOLVED ✓ (2026-04-15)
Updated in Stream A.2. Frontmatter description now reads "A–F grade + structured report saved to your vault."

---

## Assumptions Made in This Plan

These are things the plan takes as true. If any turn out to be wrong, the affected sections need revision.

| # | Assumption | Affects | Verification Status |
|---|-----------|---------|----------------------|
| 1 | `dossier.skill` ZIP format will remain stable | All streams | **Verified** — held through 6 edit passes |
| 2 | Dataview plugin handles missing frontmatter fields gracefully | Dashboard, Mode 0 | **Assumed true** — not yet empirically tested |
| 3 | 764-line SKILL.md is within Claude's effective instruction-following range | All streams | **No longer applicable** — SKILL.md now 1,044+ lines. Monitor for quality degradation as file grows. |
| 4 | Eval file naming convention (`eval-[slug]-[date].md`) is consistently followed | Dedup, versioning, all queries | **Verified** — spot-checked |
| 5 | The docx skill is available and functional for ATS export | D.4 | **Not yet tested** — empirical test needed before Mode 11 export is validated |
| 6 | Config.md is read reliably when using flat or one-level YAML | C.4, all config-dependent features | **Verified** — used throughout, no issues |
| 7 | Context window can hold CV + profile + skill + 10 JDs for batch mode | F.1 | **Not yet tested** — empirical test needed before F.1 is validated in real use |
| 8 | `web_fetch` can reach public ATS API endpoints | F.2 | **PARTIAL** — Greenhouse API accessible and returns JSON; Lever API returns 404. F.2 viable with Greenhouse; browser fallback recommended for other ATS systems. |

---

## Removed or Deprioritized Items

These appeared in the source documents but are excluded from this plan, with reasons.

| Item | Source | Why Removed |
|------|--------|-------------|
| SLSA-aligned release practices | Deep research report | No releases to sign. Premature for a prompt skill. |
| OpenSSF Scorecard badge | Deep research report | No repo to score. |
| Dependency scanning | Deep research report | No code dependencies. |
| Docker deployment | Deep research report | Skill runs in Claude.ai, not a container. |
| CI/CD pipeline | Deep research report | No code to build or test. |
| SBOM generation | Deep research report | No software supply chain. |
| `dossier new eval` CLI scaffolding | Deep research report | The AI agent is the CLI. Redundant with Mode 1. |
| SECURITY.md + vulnerability disclosure | Deep research report | Only relevant if distributed as a public repo. |
| CONTRIBUTING.md + issue templates | Deep research report | No community to govern (yet). |

These belong in a "Phase 5+" bucket if Dossier ever becomes a distributed code project. For now, they're engineering theater for a prompt-based skill.

---

## Implementation Log

Brief status of each stream as of 2026-04-15:

- **Stream A (Vault-First Architecture):** Complete — 2026-04-15
- **Stream B (Governance Docs):** Complete — 2026-04-15
- **Stream C (Foundation Features):** Complete — 2026-04-15
- **Stream D (Competitive Features):** Complete — 2026-04-15
- **Stream E (Advanced Features):** Complete — 2026-04-15
- **Stream F.1 (Batch Pipeline):** Complete — 2026-04-15
- **Stream F.2 (Portal Scanning):** Viable — Greenhouse API endpoint accessible; Lever API returns 404. F.2 can proceed with Greenhouse fallback; browser automation recommended for multi-ATS support.
- **Stream F.3 (Weekly Trends):** Complete — 2026-04-15
- **Stream F.4 (Email Automation):** Deferred — gmail_send_message not available; caps at Level 2 (draft + notify)
- **Stream F.5 (Pipeline State Machine):** Deferred — low priority
