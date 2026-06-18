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


def parse_frontmatter(text: str) -> str:
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

        # Hard-failure rules. Run before the section allowlist so a banned-content
        # match on a heading line (e.g. `## What Changed`) is reported as its own
        # rule, not masked by the allowlist's generic unknown-section.
        for rule_id, rx in failure_rules:
            if rx.search(line):
                findings.append(Finding(lineno, rule_id, stripped[:200], "failure"))
                break

        # Section allowlist check (tuned_cv only). Additive second pass per the
        # contract: a disallowed `##` heading is its own failure and does not
        # suppress a banned-content match already recorded for the same line.
        if document_class == "tuned_cv" and stripped.startswith("## "):
            heading_text = stripped[3:].strip()
            if not any(
                heading_text.lower() == allowed.lower()
                for allowed in allowed_sections
            ):
                findings.append(Finding(lineno, "unknown-section", stripped[:200], "failure"))

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
