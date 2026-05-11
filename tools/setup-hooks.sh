#!/usr/bin/env bash
# setup-hooks.sh — one-shot opt-in for the Dossier commit-msg hook.
#
# Sets git's core.hooksPath to .githooks so the Conventional Commits format
# check runs on every commit. Idempotent — safe to run repeatedly.
#
# Works under POSIX shells and Git Bash on Windows. There's no .ps1
# companion: Git for Windows ships Git Bash, and a separate PowerShell
# wrapper would double the maintenance burden for the same one-liner.
#
# Run from anywhere inside the repo:
#   bash tools/setup-hooks.sh

set -euo pipefail

# Resolve repo root from this script's location so the script works no
# matter where it's invoked from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if ! git -C "${REPO_ROOT}" rev-parse --git-dir >/dev/null 2>&1; then
    echo "error: ${REPO_ROOT} is not a git repository" >&2
    exit 2
fi

if [[ ! -f "${REPO_ROOT}/.githooks/commit-msg" ]]; then
    echo "error: ${REPO_ROOT}/.githooks/commit-msg not found — wrong checkout?" >&2
    exit 2
fi

git -C "${REPO_ROOT}" config core.hooksPath .githooks

current="$(git -C "${REPO_ROOT}" config --get core.hooksPath)"
if [[ "${current}" != ".githooks" ]]; then
    echo "error: core.hooksPath set but readback returned '${current}'" >&2
    exit 1
fi

cat <<'MSG'
ok: core.hooksPath set to .githooks
    commit-msg hook will validate Conventional Commits format on each commit.
    To bypass on a specific commit, include [skip-cc] in the commit message.
MSG
