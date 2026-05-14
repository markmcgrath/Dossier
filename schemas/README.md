# Schemas

## Purpose

Machine-readable JSON Schemas for Dossier vault frontmatter. These schemas complement the test-based validation in `tests/test_vault_schema.py` by providing a format that external tooling (editors, linters, CI scripts) can consume without reverse-engineering the Python test suite.

## Schemas in this directory

- `eval.schema.json` — Validates `type: eval` frontmatter (evals/ artifacts produced by Mode 1).
- `outreach.schema.json` — Validates `type: outreach` frontmatter (outreach/ artifacts produced by Mode 5).

## How to validate manually

Install the dependency:

```bash
pip install jsonschema pyyaml
```

Validate a vault file's frontmatter against a schema:

```python
import json, yaml, jsonschema

with open("evals/eval-acme-corp-2026-04-15.md") as f:
    text = f.read()

# Strip YAML frontmatter
lines = text.split("\n")
end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
fm = yaml.safe_load("\n".join(lines[1:end]))

schema = json.load(open("schemas/eval.schema.json"))
jsonschema.validate(fm, schema)
print("Valid")
```

Replace `eval.schema.json` with `outreach.schema.json` for outreach files.

## Scope note

Five other vault artifact types (`cover`, `prep`, `negotiation`, `daily`, `weekly`, `research`) intentionally remain prose-only for now. Their frontmatter contracts are documented in `skill/references/file-conventions.md` but are not yet stable enough to encode as versioned schemas. Schemas for those types will be added when their frontmatter contracts harden.

## Source of truth note

Enum values in these schemas mirror the constants in `tests/test_vault_schema.py` (`VALID_GRADES`, `VALID_STATUSES`, `VALID_OUTCOMES`, `VALID_LEGITIMACIES`). If those constants change, the schemas must be updated in lockstep to prevent drift between runtime test validation and static schema validation.
