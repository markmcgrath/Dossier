"""
Parity test for the Conventional Commits regex pattern.

The pattern is duplicated in two places — the client-side commit-msg hook
(`.githooks/commit-msg`) and the server-side CI check
(`.github/scripts/check_conventional_commits.sh`). Both must accept and
reject the exact same set of subject lines; otherwise a commit that passes
locally could fail in CI (or vice versa), producing confusing failures.

This test asserts both files declare the same CC_PATTERN string.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / ".githooks" / "commit-msg"
SCRIPT = REPO_ROOT / ".github" / "scripts" / "check_conventional_commits.sh"

# Matches lines like:
#   CC_PATTERN='^(feat|fix|...)(...)?!?: .+$'
# Capture group 1 is the regex itself (between the single quotes).
PATTERN_LINE_RE = re.compile(r"^CC_PATTERN='([^']+)'\s*$", re.MULTILINE)


def _extract_pattern(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = PATTERN_LINE_RE.search(text)
    assert match, (
        f"CC_PATTERN line not found in {path.relative_to(REPO_ROOT)}. "
        f"Expected a line like: CC_PATTERN='^(feat|fix|...)...'"
    )
    return match.group(1)


def test_cc_pattern_matches_between_hook_and_script():
    hook_pattern = _extract_pattern(HOOK)
    script_pattern = _extract_pattern(SCRIPT)
    assert hook_pattern == script_pattern, (
        f"CC_PATTERN drift between commit-msg hook and CI script:\n"
        f"  .githooks/commit-msg:           {hook_pattern}\n"
        f"  check_conventional_commits.sh:  {script_pattern}\n"
        f"Update both in lockstep, or extract to a shared source file."
    )
