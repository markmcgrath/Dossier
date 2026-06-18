# Plan 24: Send-Ready Contract and Validator

**Status:** Draft — build-ready  
**Item:** Implements the send-ready document contract and an executable CI validator that enforces it.  
**Summary:** Defines what "ready to send" means for tuned CVs and cover letters (and any future outbound markdown), encodes that contract as data-driven rules, provides a Python validator modeled on `pii_scan.py`, wires it into CI, and adds a pytest test module with clean and dirty fixtures.

---

## 1. Contract File: Location Decision

Place the contract at **`skill/references/SEND_READY_CONTRACT.md`**.

Rationale: every other delivery-discipline reference (file naming, story tagging, mode-specific rules) lives under `skill/references/`. That directory is bundled into `dossier.skill` and therefore visible to any user who installs the skill without cloning the repo. Placing the contract there means the skill itself carries the definition of "send-ready," not just the validator. A root-level `SEND_READY_CONTRACT.md` would be invisible to skill-only users and would sit outside the established reference hierarchy.

The validator reads from `skill/references/send_ready_config.json` (see Section 4) rather than hardcoding rules. The contract document is human-readable prose; the config is machine-readable rules.

---

## 2. Send-Ready Document Contract

### File: `skill/references/SEND_READY_CONTRACT.md`

```markdown
# Send-Ready Document Contract

*This file is loaded by the dossier skill on demand. Do not edit without also
updating the pointer in SKILL.md and the machine-readable config at
skill/references/send_ready_config.json.*

A send-ready document is one that can be forwarded to a hiring manager,
recruiter, or other external party without further editing. It contains no
scaffolding, no internal notes, no reviewer commentary, no placeholders, and
no draft markers of any kind. The validator at `.github/scripts/sendready_scan.py`
enforces this contract on every PR.

## Document classes in scope

### 1. Tuned CV (`document_class: tuned_cv`)

Files matching: `packets/**/cv.md`, `cv-*.md`

A tuned CV is a role-specific export derived from the master `cv.md`. It
contains only the sections below (in any order). Every other heading is a
hard failure.

**Allowed headings (case-insensitive, `#` or `##` prefix):**

- Name (the H1 at the top — no `##` required; a bare `# Full Name` line counts)
- Professional Summary
- Summary
- Skills
- Experience
- Professional Experience
- Work Experience
- Employment History
- Education
- Selected Projects
- Selected Architecture Projects
- Architecture Projects
- Projects
- Certifications
- Selected Projects / Certifications
- Earlier Career

No other `##`-level headings are permitted. In particular, the following heading
is a hard failure and must be stripped before the document is sent:

- `What Changed` (or `What Changed (vs. master cv.md)` or any variant)

The `What Changed` section is internal scaffolding produced by Mode 11. Mode 11
instructs the user to remove it before submitting; the validator enforces that
instruction mechanically.

### 2. Cover Letter (`document_class: cover_letter`)

Files matching: `packets/**/cover-letter.md`, `cover-letters/*.md`

A cover letter has no required heading structure — it is prose. The validator
does not check section headings for cover letters. It applies only the global
banned-content ruleset below.

### 3. General Outbound (`document_class: outbound`)

Any other `.md` file explicitly passed to the validator on the command line.
Applies only the global banned-content ruleset; no section-allowlist check.

---

## Global Banned-Content Ruleset

The following patterns are **hard failures** in the body of any send-ready
document (frontmatter is exempt). A file containing any of these may not be
marked `send_ready: true` and must not be sent.

### Category A: Internal scaffolding markers

| Pattern | Description |
| --- | --- |
| `<!-- ... -->` | HTML comment of any kind |
| Lines starting with `NOTE:` or `Note:` or `NOTE ` | Inline note prefix |
| Lines starting with `Q:` or `Q.` | Inline question prefix |
| Lines starting with `TODO` or `FIXME` or `XXX` | Developer task markers |
| The word `DRAFT` as a standalone token on a line | Draft stamp |
| Lines starting with `>` (blockquote) | Blockquotes used as reviewer asides |
| `## What Changed` (or `## What Changed (`) | Trailing change-summary section |

### Category B: Placeholder brackets

| Pattern | Description |
| --- | --- |
| `[COMPANY]`, `[ROLE]`, `[DATE]`, or any `[ALL CAPS]` token | Unfilled template slots |
| `[add ...]` or `[insert ...]` or `[your ...]` | Instruction placeholders |
| `[TBD]` or `[TK]` or `[placeholder]` | Explicit placeholder words |
| Any `[` ... `]` pair where the interior is 3+ uppercase letters | Generic unfilled slot |

### Category C: Reviewer commentary words

The following words trigger a warning (not a hard failure) when they appear
as a standalone sentence or at the start of a line. They are common in
review-cycle drafts but can appear legitimately in body text (e.g., a cover
letter that describes a `memo` the candidate authored).

| Word | Trigger condition |
| --- | --- |
| `memo` | Line starts with `Memo:` or `MEMO:` |
| `placeholder` | Appears anywhere in body |
| `reviewer` | Line starts with `Reviewer:` |
| `see note` | Phrase appears anywhere in line |
| `per your comment` | Phrase appears in line |
| `action item` | Line starts with `Action item:` or `Action Item:` |

### Category D: Trailing question lines

A line that ends with `?` AND is not inside a quoted passage (i.e., not inside
`>` blockquote) AND is not a rhetorical question in a known sentence pattern is
a warning. Exact detection: the validator flags lines where the stripped line
ends with `?` and the line is fewer than 120 characters (long rhetorical
questions in cover-letter prose are unlikely to be internal questions; short
question lines almost always are).

---

## Hard failures vs. warnings

**Hard failure (exit 1):** Categories A and B. The document must not be sent.

**Warning (exit 0 by default, exit 1 with `--strict`):** Categories C and D.

---

## Frontmatter exemption

YAML frontmatter (the block between the opening `---` and the closing `---`) is
not checked for banned content. Frontmatter fields like `notes:` in an eval file
are valid vault metadata, not document body content. The validator strips
frontmatter before scanning.

---

## What Changed exemption for the master cv.md

The master `cv.md` is not a send-ready document and is never validated as one.
Only files matching the send-ready glob patterns are checked. The master is
explicitly excluded.
```

---

## 3. The Validator

### Path

`.github/scripts/sendready_scan.py`

### Language

Python 3.12, matching `pii_scan.py` conventions exactly: `from __future__ import annotations`, stdlib only, single-file, `if __name__ == "__main__": sys.exit(main())`.

### CLI Interface

```
python .github/scripts/sendready_scan.py [paths...] [options]

Positional arguments:
  paths           One or more file paths or glob patterns to scan.
                  If omitted, scans the default target set (see below).

Options:
  --strict        Treat warnings (Categories C and D) as hard failures.
                  Exit 1 if any warning is found.
  --format        Output format: "human" (default) or "json".
  --config PATH   Path to the config JSON file.
                  Default: skill/references/send_ready_config.json
                  relative to the repo root.
  --staged        Scan only files staged in git (analogous to pii_scan.py).
```

### Default Scan Targets

When no paths are given, the validator scans all of the following relative to the repo root:

```
packets/**/cv.md
packets/**/cover-letter.md
cv-*.md
cover-letters/*.md
cover-letters/**/*.md
```

`cv.md` (the master, bare name, repo root) is **always excluded** from the default scan. This exclusion is enforced by an exact-path check after glob expansion, not by pattern: the validator compares each candidate's resolved path to `{repo_root}/cv.md` and skips it.

### Frontmatter Parsing

The validator uses the same `parse_frontmatter` helper that `conftest.py` defines:

```python
def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            body = "\n".join(lines[i + 1:])
            return {}, body   # frontmatter parsed but not returned; body is what matters
    return None, text
```

Only `body` is passed to the detection logic. The frontmatter block is skipped entirely.

### Document Class Detection

```python
def detect_class(path: Path) -> str:
    name = path.name
    parts = [p.name for p in path.parts]
    if name == "cv.md" and "packets" in parts:
        return "tuned_cv"
    if name == "cover-letter.md" and "packets" in parts:
        return "cover_letter"
    if name.startswith("cv-") and name.endswith(".md"):
        return "tuned_cv"
    if "cover-letters" in parts and name.endswith(".md"):
        return "cover_letter"
    return "outbound"
```

### Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | All files clean (warnings present only if `--strict` not passed) |
| 1 | Hard failure found, or `--strict` and warnings found |
| 2 | Config file missing or invalid JSON; scan aborted |

### Output Format: Human (default)

```
cv-autonation-2026-05-12.md:121: [banned-section] ## What Changed (vs. master cv.md)
cv-autonation-2026-05-12.md:122: [internal-note] *This section is for reference only — remove before submitting the CV.*

sendready_scan: 2 failure(s), 0 warning(s) in 1 file(s). Fix before sending.
```

```
packets/acme-corp/sre/cv.md:14: [placeholder] [COMPANY NAME]

sendready_scan: 1 failure(s) in 1 file(s). Fix before sending.
```

Clean output:
```
sendready_scan: 3 file(s) clean.
```

### Output Format: JSON (`--format json`)

```json
{
  "files_scanned": 3,
  "files_with_failures": 1,
  "files_with_warnings": 0,
  "results": [
    {
      "path": "cv-autonation-2026-05-12.md",
      "document_class": "tuned_cv",
      "failures": [
        {"line": 121, "rule": "banned-section", "text": "## What Changed (vs. master cv.md)"},
        {"line": 122, "rule": "internal-note", "text": "*This section is for reference only..."}
      ],
      "warnings": []
    }
  ]
}
```

### Detection Logic: Full Regex/String Rules Table

The validator iterates the body line by line. For each line it runs the rule table below in order. The first matching rule in each category wins for that line (a line can trigger at most one failure rule and at most one warning rule independently).

#### Hard-Failure Rules (Category A: Scaffolding markers)

| Rule ID | Match condition | Regex or string test |
| --- | --- | --- |
| `html-comment` | Line contains `<!--` | `re.search(r'<!--', line)` |
| `note-prefix` | Line body starts with `NOTE:`, `NOTE `, `Note:` | `re.match(r'\s*(NOTE:|Note:|NOTE\s)', line)` |
| `question-prefix` | Line starts with `Q:` or `Q.` | `re.match(r'\s*Q[:.]\s', line)` |
| `todo-marker` | Line starts with `TODO`, `FIXME`, or `XXX` | `re.match(r'\s*(TODO|FIXME|XXX)\b', line)` |
| `draft-marker` | `DRAFT` appears as standalone word | `re.search(r'\bDRAFT\b', line)` |
| `blockquote` | Line starts with `>` | `re.match(r'\s*>', line)` |
| `banned-section` | `## What Changed` (case-insensitive) | `re.match(r'##\s+What Changed', line, re.IGNORECASE)` |
| `internal-note` | Line matches the "for reference only" boilerplate | `re.search(r'for reference only', line, re.IGNORECASE)` |

#### Hard-Failure Rules (Category B: Placeholder brackets)

| Rule ID | Match condition | Regex |
| --- | --- | --- |
| `placeholder` | `[ALL CAPS]` token (3+ uppercase letters) | `re.search(r'\[[A-Z][A-Z ]{2,}\]', line)` |
| `placeholder` | `[add ...]`, `[insert ...]`, `[your ...]` | `re.search(r'\[(add|insert|your)\s', line, re.IGNORECASE)` |
| `placeholder` | `[TBD]`, `[TK]`, `[placeholder]` | `re.search(r'\[(TBD|TK|placeholder)\]', line, re.IGNORECASE)` |

The config file (Section 4) provides the full list of banned placeholder phrases as data rather than hardcoded strings. The regex patterns above are the defaults.

#### Warning Rules (Category C: Reviewer commentary)

| Rule ID | Match condition | Regex |
| --- | --- | --- |
| `memo-prefix` | Line starts with `Memo:` or `MEMO:` | `re.match(r'\s*(Memo:|MEMO:)', line)` |
| `placeholder-word` | The literal word `placeholder` in body | `re.search(r'\bplaceholder\b', line, re.IGNORECASE)` |
| `reviewer-prefix` | Line starts with `Reviewer:` | `re.match(r'\s*Reviewer:', line, re.IGNORECASE)` |
| `see-note` | Phrase `see note` in line | `re.search(r'\bsee note\b', line, re.IGNORECASE)` |
| `per-your-comment` | Phrase `per your comment` in line | `re.search(r'\bper your comment\b', line, re.IGNORECASE)` |
| `action-item-prefix` | Line starts with `Action item:` | `re.match(r'\s*Action [Ii]tem:', line)` |

#### Warning Rules (Category D: Trailing question lines)

| Rule ID | Match condition |
| --- | --- |
| `trailing-question` | Stripped line ends with `?`, line length <= 120 chars, line does not start with `>` |

#### Section Allowlist (tuned_cv only)

After body lines are scanned for banned content, the validator performs a second pass for `tuned_cv` documents: it collects all `##`-prefixed headings in the body and checks each against the allowed list loaded from the config. Any heading not in the allowlist is a hard failure with rule ID `unknown-section`.

The H1 line (single `#`) is always the candidate's name and is always allowed without checking against the allowlist.

### Reference Implementation Sketch

The full implementation follows the structure of `pii_scan.py`. Key functions:

```python
# .github/scripts/sendready_scan.py

#!/usr/bin/env python3
"""
Scan send-ready documents for scaffolding, placeholders, and disallowed sections.

Usage:
    python .github/scripts/sendready_scan.py            # scan default targets
    python .github/scripts/sendready_scan.py --staged   # staged files only
    python .github/scripts/sendready_scan.py path/to/cv.md --strict
    python .github/scripts/sendready_scan.py --format json

Exit code 0 if clean, 1 if failures (or warnings under --strict), 2 on config error.

Config: skill/references/send_ready_config.json (see that file for format).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_GLOBS = [
    "packets/**/cv.md",
    "packets/**/cover-letter.md",
    "cv-*.md",
    "cover-letters/*.md",
    "cover-letters/**/*.md",
]

CONFIG_REL_PATH = "skill/references/send_ready_config.json"


@dataclass
class Finding:
    lineno: int
    rule: str
    text: str
    severity: str  # "failure" or "warning"


@dataclass
class FileResult:
    path: str
    document_class: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def failures(self):
        return [f for f in self.findings if f.severity == "failure"]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity == "warning"]


def repo_root() -> Path:
    return Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    )


def parse_frontmatter(text: str) -> tuple[str]:
    """Return body text with frontmatter stripped."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:])
    return text


def detect_class(path: Path) -> str:
    name = path.name
    parts = {p.name for p in path.parents}
    if name == "cv.md" and "packets" in parts:
        return "tuned_cv"
    if name == "cover-letter.md" and "packets" in parts:
        return "cover_letter"
    if name.startswith("cv-") and name.endswith(".md"):
        return "tuned_cv"
    if "cover-letters" in parts and name.endswith(".md"):
        return "cover_letter"
    return "outbound"


def load_config(root: Path, config_path_override: str | None = None) -> dict:
    cfg_path = Path(config_path_override) if config_path_override else root / CONFIG_REL_PATH
    if not cfg_path.exists():
        print(f"sendready_scan: config not found at {cfg_path}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"sendready_scan: invalid JSON in config: {e}", file=sys.stderr)
        sys.exit(2)


def build_rules(config: dict) -> tuple[list, list]:
    """Return (failure_rules, warning_rules) each as list of (rule_id, compiled_re)."""
    failure_rules = [
        (r["id"], re.compile(r["pattern"], re.IGNORECASE if r.get("ignore_case") else 0))
        for r in config.get("failure_patterns", [])
    ]
    warning_rules = [
        (r["id"], re.compile(r["pattern"], re.IGNORECASE if r.get("ignore_case") else 0))
        for r in config.get("warning_patterns", [])
    ]
    return failure_rules, warning_rules


def scan_body(
    body: str,
    document_class: str,
    failure_rules: list,
    warning_rules: list,
    allowed_sections: list[str],
) -> list[Finding]:
    findings: list[Finding] = []
    lines = body.split("\n")

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Section allowlist check (tuned_cv only)
        if document_class == "tuned_cv" and stripped.startswith("## "):
            heading_text = stripped[3:].strip()
            if not any(
                heading_text.lower() == allowed.lower()
                for allowed in allowed_sections
            ):
                findings.append(Finding(lineno, "unknown-section", stripped[:200], "failure"))
                continue  # Don't double-report the same line

        # Hard-failure rules
        for rule_id, rx in failure_rules:
            if rx.search(line):
                findings.append(Finding(lineno, rule_id, stripped[:200], "failure"))
                break

        # Warning rules
        for rule_id, rx in warning_rules:
            if rx.search(line):
                findings.append(Finding(lineno, rule_id, stripped[:200], "warning"))
                break

    return findings


def default_targets(root: Path) -> list[Path]:
    master_cv = (root / "cv.md").resolve()
    results: list[Path] = []
    for pattern in DEFAULT_GLOBS:
        for p in root.glob(pattern):
            if p.resolve() != master_cv:
                results.append(p)
    return sorted(set(results))


def staged_files(root: Path) -> list[Path]:
    out = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], text=True
    )
    master_cv = (root / "cv.md").resolve()
    results = []
    for line in out.splitlines():
        p = (root / line).resolve()
        if p.suffix == ".md" and p != master_cv:
            results.append(p)
    return results


def format_human(results: list[FileResult], strict: bool) -> tuple[str, bool]:
    lines = []
    any_failure = False
    for r in results:
        for f in r.failures:
            lines.append(f"{r.path}:{f.lineno}: [{f.rule}] {f.text}")
            any_failure = True
        if strict:
            for w in r.warnings:
                lines.append(f"{r.path}:{w.lineno}: [warning:{w.rule}] {w.text}")
                any_failure = True
        elif r.warnings:
            for w in r.warnings:
                lines.append(f"{r.path}:{w.lineno}: [warning:{w.rule}] {w.text}")

    total_failures = sum(len(r.failures) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    files_scanned = len(results)

    if any_failure or total_warnings:
        summary = f"sendready_scan: {total_failures} failure(s), {total_warnings} warning(s) in {files_scanned} file(s). Fix before sending."
    else:
        summary = f"sendready_scan: {files_scanned} file(s) clean."
    lines.append(summary)
    return "\n".join(lines), any_failure


def format_json(results: list[FileResult], strict: bool) -> tuple[str, bool]:
    any_failure = any(r.failures for r in results)
    if strict:
        any_failure = any_failure or any(r.warnings for r in results)
    out = {
        "files_scanned": len(results),
        "files_with_failures": sum(1 for r in results if r.failures),
        "files_with_warnings": sum(1 for r in results if r.warnings),
        "results": [
            {
                "path": r.path,
                "document_class": r.document_class,
                "failures": [{"line": f.lineno, "rule": f.rule, "text": f.text} for f in r.failures],
                "warnings": [{"line": f.lineno, "rule": f.rule, "text": f.text} for f in r.warnings],
            }
            for r in results
        ],
    }
    return json.dumps(out, indent=2), any_failure


def main() -> int:
    args = sys.argv[1:]
    strict = "--strict" in args
    staged_mode = "--staged" in args
    fmt = "json" if "--format" in args and args[args.index("--format") + 1] == "json" else "human"
    config_override = None
    if "--config" in args:
        config_override = args[args.index("--config") + 1]

    # Collect explicit paths (positional args, excluding flags)
    explicit = [a for a in args if not a.startswith("--")]

    root = repo_root()
    config = load_config(root, config_override)
    failure_rules, warning_rules = build_rules(config)
    allowed_sections = config.get("allowed_cv_sections", [])

    if staged_mode:
        targets = staged_files(root)
    elif explicit:
        targets = [Path(p) for p in explicit]
    else:
        targets = default_targets(root)

    results: list[FileResult] = []
    for target in targets:
        path = target if target.is_absolute() else root / target
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        body = parse_frontmatter(text)
        doc_class = detect_class(path)
        findings = scan_body(body, doc_class, failure_rules, warning_rules, allowed_sections)
        results.append(FileResult(str(target), doc_class, findings))

    if fmt == "json":
        output, has_failure = format_json(results, strict)
    else:
        output, has_failure = format_human(results, strict)

    print(output)
    return 1 if has_failure else 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 4. Config File: `skill/references/send_ready_config.json`

This file is the machine-readable source of truth for allowed sections and banned patterns. The validator reads it at runtime; rules are data, not code. Operators can adjust the allowlist and pattern list without touching the Python script.

### Format

```json
{
  "$comment": "Send-ready document contract config. Read by .github/scripts/sendready_scan.py.",
  "version": "1",
  "allowed_cv_sections": [
    "Professional Summary",
    "Summary",
    "Skills",
    "Experience",
    "Professional Experience",
    "Work Experience",
    "Employment History",
    "Education",
    "Selected Projects",
    "Selected Architecture Projects",
    "Architecture Projects",
    "Projects",
    "Certifications",
    "Selected Projects / Certifications",
    "Earlier Career"
  ],
  "failure_patterns": [
    {
      "id": "html-comment",
      "pattern": "<!--",
      "ignore_case": false,
      "description": "HTML comment"
    },
    {
      "id": "note-prefix",
      "pattern": "^\\s*(NOTE:|Note:|NOTE\\s)",
      "ignore_case": false,
      "description": "Inline note prefix"
    },
    {
      "id": "question-prefix",
      "pattern": "^\\s*Q[:.] ",
      "ignore_case": false,
      "description": "Inline question prefix"
    },
    {
      "id": "todo-marker",
      "pattern": "^\\s*(TODO|FIXME|XXX)\\b",
      "ignore_case": false,
      "description": "Developer task marker"
    },
    {
      "id": "draft-marker",
      "pattern": "\\bDRAFT\\b",
      "ignore_case": false,
      "description": "DRAFT stamp"
    },
    {
      "id": "blockquote",
      "pattern": "^\\s*>",
      "ignore_case": false,
      "description": "Blockquote (used as reviewer aside)"
    },
    {
      "id": "banned-section",
      "pattern": "^##\\s+What Changed",
      "ignore_case": true,
      "description": "What Changed section (Mode 11 scaffolding)"
    },
    {
      "id": "internal-note",
      "pattern": "for reference only",
      "ignore_case": true,
      "description": "Internal reference note boilerplate"
    },
    {
      "id": "placeholder",
      "pattern": "\\[[A-Z][A-Z ]{2,}\\]",
      "ignore_case": false,
      "description": "Unfilled ALL-CAPS placeholder bracket"
    },
    {
      "id": "placeholder",
      "pattern": "\\[(add|insert|your)\\s",
      "ignore_case": true,
      "description": "Instruction placeholder bracket"
    },
    {
      "id": "placeholder",
      "pattern": "\\[(TBD|TK|placeholder)\\]",
      "ignore_case": true,
      "description": "Explicit placeholder word in bracket"
    }
  ],
  "warning_patterns": [
    {
      "id": "memo-prefix",
      "pattern": "^\\s*(Memo:|MEMO:)",
      "ignore_case": false,
      "description": "Memo prefix"
    },
    {
      "id": "placeholder-word",
      "pattern": "\\bplaceholder\\b",
      "ignore_case": true,
      "description": "The word placeholder in body text"
    },
    {
      "id": "reviewer-prefix",
      "pattern": "^\\s*Reviewer:",
      "ignore_case": true,
      "description": "Reviewer prefix"
    },
    {
      "id": "see-note",
      "pattern": "\\bsee note\\b",
      "ignore_case": true,
      "description": "See note phrase"
    },
    {
      "id": "per-your-comment",
      "pattern": "\\bper your comment\\b",
      "ignore_case": true,
      "description": "Per your comment phrase"
    },
    {
      "id": "action-item-prefix",
      "pattern": "^\\s*Action [Ii]tem:",
      "ignore_case": false,
      "description": "Action item prefix"
    },
    {
      "id": "trailing-question",
      "pattern": "^.{1,119}\\?$",
      "ignore_case": false,
      "description": "Short trailing question line (likely internal)"
    }
  ]
}
```

### Adding custom patterns

Operators can add entries to `failure_patterns` or `warning_patterns` without editing the validator script. Each entry needs `id`, `pattern` (Python regex), `ignore_case` (boolean), and `description` (string). The `allowed_cv_sections` list is also data: add a new section heading string to extend the allowlist for custom CV layouts.

---

## 5. CI Wiring

### Addition to `.github/workflows/ci.yml`

Add the following job after the `pii-scan` job. It matches the same structure: separate job, Ubuntu, Python 3.12, 2-minute timeout.

```yaml
  send-ready-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Run send-ready scan
        run: python .github/scripts/sendready_scan.py
```

This job scans the default target set (all tracked `packets/**/cv.md`, `packets/**/cover-letter.md`, `cv-*.md`, `cover-letters/*.md`). In the open-source repo there are no tracked send-ready documents so this job will report "0 file(s) clean" and pass. Once a user's fork has tracked packets, it enforces the contract on every PR.

Notes on scope:
- `--strict` is intentionally omitted from the CI step. Warnings are informational in CI; only hard failures block merge.
- The job does not need `DOSSIER_VAULT` because the validator uses `git rev-parse --show-toplevel`, not the env var.
- If a future PR adds `--staged` mode to CI (pre-merge), the step command becomes `python .github/scripts/sendready_scan.py --staged`. That is a one-line change.

### Test Module: `tests/test_sendready_contract.py`

```python
"""
Tests for the send-ready contract validator.

Covers:
  - A dirty tuned CV fixture is flagged (What Changed section, placeholder bracket, html comment).
  - A clean tuned CV fixture passes.
  - A dirty cover letter fixture is flagged (NOTE: prefix, blockquote).
  - A clean cover letter fixture passes.
  - The section allowlist rejects an unknown heading in a tuned CV.
  - Frontmatter content is NOT flagged as a failure.

These tests import the validator module directly rather than calling subprocess,
matching the pattern used in test_antipatterns.py.
"""
import sys
from pathlib import Path
import importlib.util
import json
import tempfile
import textwrap

import pytest


# ---------------------------------------------------------------------------
# Helper: load the validator module by path so tests don't depend on install.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def sendready_scan(vault_path):
    script = vault_path / ".github" / "scripts" / "sendready_scan.py"
    assert script.exists(), f"sendready_scan.py not found at {script}"
    spec = importlib.util.spec_from_file_location("sendready_scan", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def sr_config(vault_path):
    cfg_path = vault_path / "skill" / "references" / "send_ready_config.json"
    assert cfg_path.exists(), f"send_ready_config.json not found at {cfg_path}"
    return json.loads(cfg_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Fixtures: dirty and clean documents
# ---------------------------------------------------------------------------

DIRTY_CV = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    notes: "Internal note in frontmatter — should NOT be flagged."
    ---

    # Jane Smith

    Remote | jane@example.com

    ---

    ## Professional Summary

    Experienced engineer with a focus on <!-- TODO: refine this --> distributed systems.

    ---

    ## Skills

    Python, Go, [ADD YOUR SKILLS HERE]

    ---

    ## Experience

    ### Senior Engineer — Acme Corp
    2022 – Present

    - Led migration of legacy [SYSTEM NAME] to Kubernetes.

    ---

    ## What Changed (vs. master cv.md)
    *This section is for reference only — remove before submitting the CV.*

    - Summary rewritten.
""")

CLEAN_CV = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    ---

    # Jane Smith

    Remote | jane@example.com

    ---

    ## Professional Summary

    Experienced engineer with a focus on distributed systems and platform reliability.

    ---

    ## Skills

    Python, Go, Kubernetes, PostgreSQL

    ---

    ## Experience

    ### Senior Engineer — Acme Corp
    2022 – Present

    - Led migration of legacy monolith to Kubernetes, reducing deploy time by 60%.
    - Designed incident response runbooks adopted by a 12-person SRE team.

    ---

    ## Education

    **B.S. Computer Science** — State University, 2015
""")

DIRTY_COVER = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    ---

    Dear Hiring Team,

    NOTE: Insert a stronger opening here.

    > Reviewer: this paragraph needs a better hook.

    I am excited to apply for the Senior Engineer role at Acme.

    Sincerely,
    Jane Smith
""")

CLEAN_COVER = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    ---

    Dear Acme Hiring Team,

    I have spent the last five years building distributed systems at scale, most recently
    at a fintech startup where I owned the platform reliability function for a system
    processing two million transactions per day.

    I would welcome the chance to discuss how this experience maps to your Senior
    Engineer opening.

    Sincerely,
    Jane Smith
    jane@example.com
""")

DIRTY_CV_BAD_SECTION = textwrap.dedent("""\
    ---
    type: cover
    company: "Acme"
    ---

    # Jane Smith

    Remote | jane@example.com

    ## Professional Summary

    Experienced engineer.

    ## Hobbies and Interests

    Mountain biking, pottery.

    ## Experience

    ### Engineer — Acme
    2022 – Present

    - Built things.
""")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDirtyCV:
    def test_html_comment_flagged(self, sendready_scan, sr_config, tmp_path):
        cv_file = tmp_path / "cv-acme-2026-01-01.md"
        cv_file.write_text(DIRTY_CV, encoding="utf-8")
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "html-comment" in failure_rules_hit, "Expected html-comment failure"

    def test_placeholder_flagged(self, sendready_scan, sr_config, tmp_path):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "placeholder" in failure_rules_hit, "Expected placeholder failure"

    def test_what_changed_section_flagged(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "banned-section" in failure_rules_hit, "Expected banned-section failure for What Changed"

    def test_frontmatter_notes_not_flagged(self, sendready_scan, sr_config):
        """notes: field in frontmatter must not produce a failure."""
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV)
        # The body must not contain the frontmatter notes line
        assert 'notes: "Internal note in frontmatter' not in body


class TestCleanCV:
    def test_clean_cv_passes(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(CLEAN_CV)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failures = [f for f in findings if f.severity == "failure"]
        assert not failures, f"Expected no failures in clean CV, got: {failures}"


class TestDirtyCoverLetter:
    def test_note_prefix_flagged(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_COVER)
        findings = sendready_scan.scan_body(body, "cover_letter", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "note-prefix" in failure_rules_hit, "Expected note-prefix failure"

    def test_blockquote_flagged(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_COVER)
        findings = sendready_scan.scan_body(body, "cover_letter", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "blockquote" in failure_rules_hit, "Expected blockquote failure"


class TestCleanCoverLetter:
    def test_clean_cover_passes(self, sendready_scan, sr_config):
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(CLEAN_COVER)
        findings = sendready_scan.scan_body(body, "cover_letter", failure_rules, warning_rules, allowed)
        failures = [f for f in findings if f.severity == "failure"]
        assert not failures, f"Expected no failures in clean cover letter, got: {failures}"


class TestSectionAllowlist:
    def test_unknown_section_flagged(self, sendready_scan, sr_config):
        """A ## heading not in the allowlist must produce an unknown-section failure."""
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV_BAD_SECTION)
        findings = sendready_scan.scan_body(body, "tuned_cv", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "unknown-section" in failure_rules_hit, (
            "Expected unknown-section failure for 'Hobbies and Interests'"
        )

    def test_unknown_section_not_flagged_for_cover_letter(self, sendready_scan, sr_config):
        """Section allowlist does not apply to cover letters."""
        failure_rules, warning_rules = sendready_scan.build_rules(sr_config)
        allowed = sr_config.get("allowed_cv_sections", [])
        body = sendready_scan.parse_frontmatter(DIRTY_CV_BAD_SECTION)
        findings = sendready_scan.scan_body(body, "cover_letter", failure_rules, warning_rules, allowed)
        failure_rules_hit = {f.rule for f in findings if f.severity == "failure"}
        assert "unknown-section" not in failure_rules_hit
```

Note: no fixture files are written to `tests/fixtures/` for this test. The contract document contents are defined as module-level string constants inside the test file, which is the same pattern used in `test_antipatterns.py` for inline fixture data. This avoids the question of whether `tests/fixtures/` paths are skipped by other validators.

---

## 6. Integration with Packet Finalization and Mode 0

### Packet finalization (`send_ready: true`)

The packet structure (defined in Plan 23) includes a frontmatter field `send_ready: true` in the packet manifest or in each component file. The rule is:

**A file must not have `send_ready: true` set in its frontmatter until `sendready_scan.py` exits 0 for that file.**

Mode 11 (Tailored CV) and Mode 6 (Cover Letter) are the two modes that produce send-ready candidates. When either mode finishes generating a document that lives in a packet, it must:

1. Save the file (without `send_ready: true`).
2. Instruct the user: "Run `python .github/scripts/sendready_scan.py packets/[company-slug]/[role-slug]/cv.md` to verify this document is clean before sending."
3. Only after the user confirms the scan passes (or the CI job passes on their local branch) does the mode set `send_ready: true` in the file's frontmatter.

Modes must never auto-set `send_ready: true` without a successful scan. This is an integrity rule, not a convenience feature.

The skill reference file (`skill/references/SEND_READY_CONTRACT.md`) must be cited in the Mode 11 and Mode 6 reference files as the authority for what "send-ready" means. A pointer line like `*Send-ready requirements: see [SEND_READY_CONTRACT.md](SEND_READY_CONTRACT.md).*` is sufficient.

### Mode 0 (Health Check) integration

Mode 0 currently checks vault structure, required files, and frontmatter validity. The send-ready scan should be added as an optional health check step:

```
Send-ready check (packets only):
  Run: python .github/scripts/sendready_scan.py
  Expected: "N file(s) clean." or "0 file(s) clean."
  If failures: list the offending files and prompt the user to fix before sending.
```

This is a non-blocking check in Mode 0 (Mode 0 does not fail if send-ready violations exist; it reports them). The CI job is the hard gate. Mode 0 is the diagnostic view.

The SKILL.md Mode 0 section should be updated to include "Send-ready scan (packets)" in its checklist table, with status "pass/fail" derived from the validator exit code.

---

## 7. Acceptance Criteria

- [ ] `skill/references/SEND_READY_CONTRACT.md` exists and defines the three document classes (tuned_cv, cover_letter, outbound), the section allowlist for tuned CVs, and the global banned-content ruleset with hard-failure vs. warning distinction.
- [ ] `skill/references/send_ready_config.json` exists, is valid JSON, contains `allowed_cv_sections` (15+ entries), `failure_patterns` (10+ entries), and `warning_patterns` (6+ entries). All patterns are valid Python regexes.
- [ ] `.github/scripts/sendready_scan.py` exists, is executable Python 3.12, follows `pii_scan.py` conventions (stdlib only, `from __future__ import annotations`, `if __name__ == "__main__": sys.exit(main())`).
- [ ] Running `python .github/scripts/sendready_scan.py` with no tracked send-ready files exits 0 and prints "0 file(s) clean." (or equivalent).
- [ ] Running the validator against the live `cv-anthropic-fde-2026-06-08.md` file exits 1 and reports `banned-section` for the `## What Changed` line.
- [ ] Running the validator against a file with `[ADD YOUR SKILLS HERE]` exits 1 and reports `placeholder`.
- [ ] Running the validator against `cover-autonation-2026-05-12.md` exits 0 (the file is clean).
- [ ] `--strict` flag causes Category C and D warnings to produce exit 1.
- [ ] `--format json` produces valid JSON matching the schema described in Section 3.
- [ ] Frontmatter content (including `notes:` fields) is not flagged as a failure.
- [ ] The master `cv.md` is excluded from the default scan.
- [ ] `.github/workflows/ci.yml` has a `send-ready-scan` job that runs `python .github/scripts/sendready_scan.py` and passes on the open-source repo (zero tracked send-ready files).
- [ ] `tests/test_sendready_contract.py` exists with at least 9 test functions across the 4 test classes defined in Section 5.
- [ ] `pytest tests/test_sendready_contract.py` passes with no skips and no failures.
- [ ] `skill/references/SEND_READY_CONTRACT.md` is listed in the dossier skill's reference index (wherever `mode11-tailored-cv.md` and `file-conventions.md` are enumerated) so it is bundled into `dossier.skill`.

---

## Appendix: Ambiguities and Defaults Chosen

**Blockquote rule:** Markdown blockquotes (`>`) are banned in send-ready documents. This is a hard failure, not a warning. Rationale: no legitimate CV or cover letter uses blockquote syntax; they appear exclusively as reviewer-aside convention in drafting workflows.

**Trailing question (Category D):** The 120-character threshold was chosen because a short internal question like "Should I add a metric here?" is 36 characters; a genuine rhetorical sentence in a cover letter like "What does it take to build a data platform that executives actually trust?" is over 70 characters but still under 120. The threshold errs toward flagging rather than missing. The rule is a warning, so false positives are visible but not blocking.

**`--staged` default not in CI:** The CI job scans all default targets, not just staged files. This is consistent with how `pii_scan.py` works in CI (it also runs without `--staged`). The `--staged` flag is for local pre-commit use only.

**`cv.md` exclusion mechanism:** The master CV is excluded by exact resolved-path comparison, not by name pattern. If a user names a packet CV literally `cv.md` inside a `packets/` subdirectory it is still included. Only the bare `{repo_root}/cv.md` is excluded.

**Section allowlist case sensitivity:** Heading comparison is case-insensitive in the validator (`heading_text.lower() == allowed.lower()`). The config stores headings in their canonical mixed-case form for readability.
