#!/usr/bin/env python3
"""
Scan tracked files for high-confidence PII and secret patterns.

Usage:
    python .github/scripts/pii_scan.py            # scan all tracked files
    python .github/scripts/pii_scan.py --staged   # scan only staged changes

Exit code 0 if clean, 1 if any match is found.

The committed regex list contains only generic patterns (safe to publish).
Maintainers can add owner-specific regexes in
`.github/scripts/pii_patterns.local.txt` (gitignored). That file is read
if present; it never needs to be committed.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

GENERIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("personal-email", re.compile(r"\b[\w.+-]+@(?:gmail|outlook|yahoo|hotmail|icloud|proton|protonmail)\.(?:com|me)\b", re.IGNORECASE)),
    ("anthropic-key", re.compile(r"sk-ant-[\w-]{20,}")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{40,}\b")),
    ("google-key", re.compile(r"\bAIza[\w-]{35}\b")),
    ("notion-token", re.compile(r"\b(?:ntn_[\w]{20,}|secret_[A-Za-z0-9]{40,})\b")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("windows-user-path", re.compile(r"[Cc]:[\\/]Users[\\/]\w+", re.IGNORECASE)),
    ("notion-id-hex", re.compile(r"\b[a-f0-9]{32}\b")),
]

ALLOWLIST_SUBSTRINGS: list[str] = [
    "you@example.com",
    "name@company.com",
    "hiring.manager@cipheranalytics.com",
    "@example.com",
    "@example.org",
    "@example.net",
    "user@example",
    "email@example.com",
]

BINARY_EXTENSIONS: set[str] = {
    ".skill", ".zip", ".gz", ".tar", ".7z",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".pyc", ".pyo", ".so", ".dll", ".exe",
    ".woff", ".woff2", ".ttf", ".eot",
}

SCRIPT_REL_PATH = ".github/scripts/pii_scan.py"
LOCAL_PATTERNS_REL_PATH = ".github/scripts/pii_patterns.txt"


def repo_root() -> Path:
    return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())


def tracked_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], text=True)
    return [line for line in out.splitlines() if line]


def staged_files() -> list[str]:
    out = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], text=True
    )
    return [line for line in out.splitlines() if line]


def staged_content(path: str) -> str | None:
    try:
        out = subprocess.check_output(["git", "show", f":{path}"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    try:
        return out.decode("utf-8", errors="replace")
    except Exception:
        return None


def disk_content(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return None


def load_local_patterns(root: Path) -> list[tuple[str, re.Pattern[str]]]:
    local = root / LOCAL_PATTERNS_REL_PATH
    if not local.exists():
        return []
    patterns: list[tuple[str, re.Pattern[str]]] = []
    for i, raw in enumerate(local.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append((f"local:{i}", re.compile(line)))
        except re.error as e:
            print(f"pii_scan: invalid regex in {LOCAL_PATTERNS_REL_PATH}:{i}: {e}", file=sys.stderr)
            sys.exit(2)
    return patterns


def should_skip(path: str) -> bool:
    if path == SCRIPT_REL_PATH:
        return True
    # Test fixtures contain synthetic look-alike data by design.
    if path.startswith("tests/fixtures/"):
        return True
    suffix = Path(path).suffix.lower()
    if suffix in BINARY_EXTENSIONS:
        return True
    return False


def scan_text(text: str, patterns: list[tuple[str, re.Pattern[str]]]) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if any(sub in line for sub in ALLOWLIST_SUBSTRINGS):
            continue
        for pattern_id, rx in patterns:
            if rx.search(line):
                hits.append((lineno, pattern_id, line.strip()[:200]))
                break
    return hits


def main() -> int:
    staged_mode = "--staged" in sys.argv[1:]
    root = repo_root()
    patterns = GENERIC_PATTERNS + load_local_patterns(root)

    files = staged_files() if staged_mode else tracked_files()
    any_hits = False

    for path in files:
        if should_skip(path):
            continue
        text = staged_content(path) if staged_mode else disk_content(root / path)
        if text is None:
            continue
        for lineno, pattern_id, line in scan_text(text, patterns):
            any_hits = True
            print(f"{path}:{lineno}: [{pattern_id}] {line}")

    if any_hits:
        print("\npii_scan: matches found. Fix or add to the allowlist before committing.", file=sys.stderr)
        return 1

    has_local = (root / LOCAL_PATTERNS_REL_PATH).exists()
    mode = "staged" if staged_mode else "all tracked"
    suffix = " (with local patterns)" if has_local else " (generic patterns only)"
    print(f"pii_scan: clean ({mode} files{suffix}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
