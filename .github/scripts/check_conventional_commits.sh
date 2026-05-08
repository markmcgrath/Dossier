#!/usr/bin/env bash
# check_conventional_commits.sh — Server-side Conventional Commits gate for PRs.
#
# Authority: features/plan/18-version-tag-release-pipeline.md (Stream A follow-up).
# Plan: ~/.claude/plans/lucky-pondering-dragon.md (Plan 19, Stream A).
#
# Rule:
#   Every commit subject in the PR range must conform to Conventional Commits
#   format, unless a bypass token is present or the subject is an auto-generated
#   git message (Merge ..., Revert ...).
#
# Bypass:
#   If any commit message in the PR range contains the token `[skip-cc]`, the
#   check is skipped and the token is logged. This is parallel to the
#   `[skip-changelog]` bypass in changelog_check.sh.
#
# Exit codes:
#   0 — all subjects pass (or legitimately bypassed)
#   1 — one or more subjects fail the CC format check
#   2 — usage / environment error (missing git, bad BASE_REF)
#
# Environment:
#   BASE_REF — base ref to diff against. Defaults to origin/main.
#   HEAD_REF — head ref. Defaults to HEAD.
#
# Run locally:
#   BASE_REF=origin/main bash .github/scripts/check_conventional_commits.sh

set -euo pipefail

BASE_REF="${BASE_REF:-origin/main}"
HEAD_REF="${HEAD_REF:-HEAD}"

if ! command -v git >/dev/null 2>&1; then
    echo "FAIL: git not found on PATH" >&2
    exit 2
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "FAIL: not a git repository" >&2
    exit 2
fi

# Resolve refs. If BASE_REF is not reachable, the check cannot run — this is
# an environment issue (e.g. workflow forgot fetch-depth: 0), not a content
# violation. Exit 2 keeps the CI signal truthful.
if ! git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
    echo "FAIL: base ref '$BASE_REF' not found (did the workflow set fetch-depth: 0?)" >&2
    exit 2
fi

# ----- Bypass token scan ---------------------------------------------------
# Any commit in the PR range with `[skip-cc]` in its full message triggers a
# bypass. The token is logged so reviewers can see a bypass was used.
#
# Uses bash glob-match (not grep in a pipeline) to avoid the SIGPIPE / set -e
# interaction that can produce exit 141 on some runners — same rationale as
# changelog_check.sh's bypass scan.
COMMIT_MSGS="$(git log --format='%B' "${BASE_REF}..${HEAD_REF}")"
if [[ "$COMMIT_MSGS" == *'[skip-cc]'* ]]; then
    echo "NOTICE: [skip-cc] token found in commit message — conventional-commits check bypassed"
    exit 0
fi

# ----- Collect subjects ----------------------------------------------------
# %s gives the subject line (first paragraph) only.
SUBJECTS="$(git log --format='%s' "${BASE_REF}..${HEAD_REF}")"

if [[ -z "$SUBJECTS" ]]; then
    echo "PASS: no commits in range ${BASE_REF}..${HEAD_REF}"
    exit 0
fi

# ----- Validate each subject -----------------------------------------------
# Conventional Commits regex — identical to the commit-msg hook.
CC_PATTERN='^(feat|fix|docs|perf|refactor|revert|chore|build|ci|style|test)(\(.+\))?!?: .+$'

FAIL=0
OFFENDERS=()

while IFS= read -r subject; do
    [[ -z "$subject" ]] && continue

    # Allow auto-generated git messages (Merge, Revert) unchecked.
    if [[ "$subject" =~ ^Merge\  ]] || [[ "$subject" =~ ^Revert\  ]]; then
        continue
    fi

    if ! [[ "$subject" =~ $CC_PATTERN ]]; then
        OFFENDERS+=("  - ${subject}")
        FAIL=1
    fi
done <<< "$SUBJECTS"

if [[ "$FAIL" -eq 1 ]]; then
    echo "FAIL: the following commit subjects do not follow Conventional Commits:" >&2
    for offender in "${OFFENDERS[@]}"; do
        echo "$offender" >&2
    done
    cat >&2 <<'EOF'
Expected: <type>(<scope>)?(!)?: <description>
  types: feat, fix, docs, perf, refactor, revert, chore, build, ci, style, test
  example: feat(release): add structured manifest
Add [skip-cc] to any commit message in this PR range to bypass the check.
EOF
    exit 1
fi

echo "PASS: all ${#OFFENDERS[@]} commit subjects in ${BASE_REF}..${HEAD_REF} follow Conventional Commits"
exit 0
