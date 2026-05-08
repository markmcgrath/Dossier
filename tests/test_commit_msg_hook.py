"""Boots a tmp git repo and exercises .githooks/commit-msg."""
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / ".githooks" / "commit-msg"

@pytest.fixture
def tmp_git_repo(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    hook_target = hooks_dir / "commit-msg"
    hook_target.write_text(HOOK.read_text())
    hook_target.chmod(0o755)
    (tmp_path / "x.txt").write_text("hi")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    return tmp_path

@pytest.mark.parametrize("msg,should_pass", [
    ("feat: add thing", True),
    ("fix(scope): repair", True),
    ("docs: clarify", True),
    ("feat!: breaking", True),
    ("feat(scope)!: breaking", True),
    ("Merge branch 'foo'", True),
    ("Revert \"feat: x\"", True),
    ("just a freeform message", False),
    ("feat add thing", False),  # missing colon
    ("FEAT: add thing", False),  # type must be lowercase
    ("frob: add thing", False),  # unknown type
])
def test_commit_msg_hook(tmp_git_repo, msg, should_pass):
    result = subprocess.run(
        ["git", "commit", "-m", msg], cwd=tmp_git_repo, capture_output=True, text=True
    )
    if should_pass:
        assert result.returncode == 0, f"hook rejected {msg!r}: {result.stderr}"
    else:
        assert result.returncode != 0, f"hook accepted {msg!r} but should not"
