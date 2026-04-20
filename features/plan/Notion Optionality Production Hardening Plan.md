# Notion Optionality Production Hardening Plan

## Purpose

Harden Dossier for public release by enforcing a strict optional-integration contract for Notion:

- Vault remains the source of truth in all cases
    
- Core workflows function without Notion
    
- Notion behavior is strictly conditional on config
    
- Documentation and tests stay aligned over time
    

---

## Scope

This plan implements three workstreams:

1. Replace brittle Notion anti-pattern tests with contract-based assertions
    
2. Add config-state permutation fixtures/tests for optional Notion behavior
    
3. Add documentation consistency checks across core files
    

---

## Goals and Non-Goals

### Goals

- Prevent regressions that accidentally make Notion mandatory
    
- Validate behavior across realistic config states
    
- Ensure docs consistently describe Notion as optional
    
- Keep CI failures actionable and low-noise
    

### Non-Goals

- Implementing runtime Notion API calls
    
- End-to-end MCP integration testing
    
- Expanding feature scope beyond optionality contract enforcement
    

---

## Workstream 1 — Contract-based Notion Optionality Tests

### Problem

Current tests in `tests/test_antipatterns.py` rely heavily on string scanning and include disabled/non-failing logic. This creates false confidence and misses behavioral contract regressions.

### Deliverables

- Refactor `tests/test_antipatterns.py` to enforce explicit contract states:
    
    1. Notion disabled path (or missing config) must preserve vault-only operation
        
    2. Notion enabled path must be conditional and explicit
        
    3. Core modes must remain functional without Notion
        

### Implementation Notes

- Target specific sections in `skill/SKILL.md` rather than whole-file heuristics:
    
    - “Pipeline Tracker”
        
    - “Setup: Reading the CV, Profile, and Config”
        
    - “Mode 0: Health Check”
        
    - “Mode 1: Offer Evaluator”
        
- Prefer localized text-window assertions around headings (stable intent checks).
    
- Remove unconditional skips for these core contract checks.
    
- Ensure test failures include:
    
    - Expected contract rule
        
    - Missing/violating phrase context
        
    - Suggested fix area (section heading)
        

### Acceptance Criteria

- No unconditional `pytest.skip()` for core optionality contract tests
    
- Tests fail when wording implies Notion requirement for core workflows
    
- Tests pass when Notion is clearly described as optional and conditional
    

---

## Workstream 2 — Config Permutation Fixtures + Tests

### Problem

There is no fixture-driven validation for common config states (missing, disabled, malformed enabled), which are high-frequency real-world scenarios.

### Deliverables

- Add new fixtures under `tests/fixtures/config/`:
    
    - `config_missing.md` (simulated absence via test setup)
        
    - `config_notion_disabled.md`
        
    - `config_notion_enabled_missing_ids.md`
        
    - `config_notion_enabled_valid_sample.md`
        
- Add `tests/test_config_contract.py` validating declared behavior across config states.
    

### Test Matrix

1. **No config present**
    
    - Expected: proceed with defaults, vault-only path
        
2. **Notion explicitly disabled**
    
    - Expected: vault-only path, no mandatory Notion steps
        
3. **Notion enabled but incomplete**
    
    - Expected: warning/validation language, no hard failure for core modes
        
4. **Notion enabled and valid**
    
    - Expected: optional mirror behavior permitted, vault still primary
        

### Implementation Notes

- Validate declared behavior in:
    
    - `skill/SKILL.md`
        
    - `config.template.md`
        
- Use deterministic, text-contract assertions (no network calls, no runtime connectors).
    

### Acceptance Criteria

- New config contract tests run in CI
    
- Failures clearly identify which state/contract rule regressed
    
- Core-mode independence from Notion is explicitly protected
    

---

## Workstream 3 — Cross-Doc Consistency Enforcement

### Problem

Optionality language can drift across docs, causing user confusion and support issues.

### Deliverables

- Add `tests/test_docs_consistency.py` to enforce consistent optionality statements across:
    
    - `README.md`
        
    - `START_HERE.md`
        
    - `config.template.md`
        
    - `skill/SKILL.md`
        
    - `DATA_CONTRACT.md`
        

### Required Consistency Rules

All core docs must remain aligned on:

1. Vault is source of truth
    
2. Notion is optional
    
3. Missing/disabled Notion does not block core evaluation workflow
    
4. Notion (when enabled) is mirror/secondary behavior
    

### Implementation Notes

- Use compact rule definitions in test code for maintainability.
    
- Keep phrasing tolerance reasonable (intent-level checks, not exact sentence matches).
    
- Fail with actionable “file + rule + expected language intent” output.
    

### Acceptance Criteria

- CI catches doc drift on optionality claims
    
- Contributors can quickly resolve mismatches with clear error messages
    

---

## File Changes Summary

### New files

- `tests/test_config_contract.py`
    
- `tests/test_docs_consistency.py`
    
- `tests/fixtures/config/config_notion_disabled.md`
    
- `tests/fixtures/config/config_notion_enabled_missing_ids.md`
    
- `tests/fixtures/config/config_notion_enabled_valid_sample.md`
    

### Modified files

- `tests/test_antipatterns.py`
    
- (Optional) `tests/README.md` to document new coverage areas and fixture usage
    

---

## CI Integration

No new dependencies required.  
Ensure new tests are included under existing pytest discovery in `.github/workflows/ci.yml`.

Suggested verification command:

DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v

---

## Risk Assessment

### Risks

- Overly strict phrase matching may produce false positives
    
- Under-specified assertions may miss subtle regressions
    

### Mitigations

- Assert on intent in section context, not exact strings
    
- Add narrow allowlist patterns only when justified
    
- Keep failure messages explicit and remediation-oriented
    

---

## Definition of Done

-  Optionality contract tests are active and non-skipped
    
-  Config permutation fixtures and tests are added and passing
    
-  Cross-doc consistency tests are added and passing
    
-  CI fails on Notion-mandatory regressions
    
-  Tests remain fast and deterministic
    
-  `tests/README.md` reflects added coverage (if updated)
    

---

## Suggested Implementation Order

1. Refactor `tests/test_antipatterns.py` (highest risk reduction)
    
2. Add config fixtures + `tests/test_config_contract.py`
    
3. Add `tests/test_docs_consistency.py`
    
4. Update `tests/README.md` (optional but recommended)
    
5. Run full test suite and address any regressions