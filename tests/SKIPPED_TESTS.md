# Skipped Tests — Accountability Table

This file is the single source of truth for every `pytest.skip()` site in the test suite. Every skip must appear here with a named exit criterion. Adding a new skip without updating this table is a documentation regression.

**Last reconciled:** 2026-06-17 (Plan 27 closed the three plan-13 hard skips) against test suite at commit on `main`.

---

## Skip sites

| # | Test / Fixture | File:Line | Skip kind | Reason | Exit criterion | Release blocker? |
|---|---|---|---|---|---|---|
| 1 | `test_schema_validation.py` (module) | `tests/test_schema_validation.py:16` | environment-conditional | `jsonschema` is an optional dependency. The whole module skips at import if `jsonschema` is missing, so JSON-Schema validation of example artifacts does not run. | Install `jsonschema>=4.0.0` (declared in `requirements.txt` and `pyproject.toml`'s `dev` extras). CI installs it; the skip only fires in environments where `pip install` was incomplete. | **No** — the underlying schemas are validated by `tests/test_vault_schema.py`'s frontmatter checks; `test_schema_validation.py` is the strict-schema layer. |
| 2 | `config_template_text` fixture | `tests/test_config_contract.py:219` | vault-layout-conditional | The fixture skips downstream tests if `config.template.md` is absent from the vault root (e.g., a private vault that uses `config.md` instead of the template). | Vault root contains `config.template.md`. The open-source vault always ships it, so this skip never fires here; the guard exists so the same suite runs cleanly against private vault layouts. | **No** — open-source vault always has the template. |
| 3 | `test_applicable_rules` (parametrized) | `tests/test_docs_consistency.py:194` | vault-layout-conditional | Each parametrized row skips if its target document is absent from the vault layout (e.g., `config.template.md` missing in a private layout). | Vault layout contains every key in `_CANONICAL_KEYS`. The open-source vault does; private layouts may not. | **No** — same as #2. |
| 4 | `test_no_notion_primary_language` (parametrized) | `tests/test_docs_consistency.py:230` | vault-layout-conditional | Skips per-document if the target doc is absent from the vault. The substantive check (no "Notion is the source of truth" language) runs only against present docs. | Same as #3. | **No** — same as #2. |
| 5 | `test_stories_template_has_star_format` | `tests/test_vault_files.py:199` | vault-layout-conditional | Skips if neither `stories.md` nor `stories.template.md` is present in the vault root. | Vault root contains one of the two. The open-source vault ships `stories.template.md`. | **No** — open-source vault always has the template. |

---

## Summary

- The three plan-13 hard skips (Gate-Pass placement, bias-caveat assertion target, config-key docs) were **resolved in Plan 27 (A-1/A-2/A-3)**: the assertions now pass against this repo and the `pytest.skip()` sites were removed.
- **1 environment-conditional skip** (#1) only fires when `jsonschema` is missing. CI never sees it because `jsonschema` is in `requirements.txt`.
- **4 vault-layout-conditional skips** (#2–5) are guards for running the suite against private vault layouts. The open-source vault has every file these guards check for, so they don't fire in CI or local runs against this repo.

**Typical pytest output:**

- Against the open-source vault with `jsonschema` installed: **0 skips**.
- Against the open-source vault without `jsonschema`: **1 skip** (the `test_schema_validation` module, #1).
- Against a private vault missing one or more layout files: variable, governed by which of #2–5 trigger.

---

## When to update this file

1. **Adding a new skip:** add a row before merging. The PR-reviewer should reject any new `pytest.skip()` or `@pytest.mark.skip` without a corresponding row.
2. **Resolving a skip:** delete the row in the same commit that removes the `pytest.skip()` call. Cross-reference the resolving plan/PR in the commit message.
3. **Reconciling drift:** run `DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -rs` and confirm every entry in pytest's "short test summary info" appears here.

---

## Related

- [`ROADMAP.md`](../ROADMAP.md) carries the plan-13 narrative for the three hard skips that Plan 27 resolved.
- [`tests/semantic-review-checklist.md`](semantic-review-checklist.md) covers what tests intentionally do **not** check (LLM output quality).
- [`HARDENING.md`](../HARDENING.md) §7 documents the broader test surface and required-checks contract.
