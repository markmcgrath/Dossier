#!/usr/bin/env bash
# changelog_check.sh — CHANGELOG gate for PRs.
#
# Authority: features/plan/18-version-tag-release-pipeline.md (Stream B).
# Execution plan: ~/.claude/plans/lucky-pondering-dragon.md
#
# Rule:
#   If the diff against the base branch touches any of:
#     - skill/**
#     - tests/**
#     - dossier.skill (the committed ZIP artifact)
#   then CHANGELOG.md must also appear in the diff, AND the diff must
#   add at least one line under the `## [Unreleased]` heading.
#
# Bypass:
#   If any commit in the PR range contains the token `[skip-changelog]`
#   in its message, the check is skipped and the token is logged.
#
# Exit codes:
#   0 — check passed (or legitimately skipped: no gated paths, or bypass token)
#   1 — check failed (gated path touched, CHANGELOG not updated)
#   2 — usage / environment error (missing git, missing base ref)
#
# Environment:
#   BASE_REF — base ref to diff against. Defaults to origin/main.
#   HEAD_REF — head ref. Defaults to HEAD.
#
# Run locally:
#   BASE_REF=origin/main bash .github/scripts/changelog_check.sh

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

MERGE_BASE="$(git merge-base "$BASE_REF" "$HEAD_REF")"

# ----- Bypass token scan ---------------------------------------------------
# Any commit in the PR range with `[skip-changelog]` in its message triggers
# a bypass. The token is logged so reviewers can see that a bypass was used.
#
# Note on shape: use bash's built-in glob match instead of `grep -qF`. A
# naïve `git log | grep -qF` pipeline trips ``set -o pipefail`` on some
# runners — when grep matches it exits early and SIGPIPEs git log
# (exit 141), and pipefail propagates that as the pipeline's status. The
# `bash -e` runner shell then aborts the step with no visible script
# output. The glob-match form avoids any pipe.
COMMIT_MSGS="$(git log --format='%B' "${MERGE_BASE}..${HEAD_REF}")"
if [[ "$COMMIT_MSGS" == *'[skip-changelog]'* ]]; then
    echo "NOTICE: [skip-changelog] token found in commit message — changelog-check bypassed"
    exit 0
fi

# ----- Changed-files list --------------------------------------------------
CHANGED_FILES="$(git diff --name-only "${MERGE_BASE}...${HEAD_REF}")"

# ----- Gated-path detection ------------------------------------------------
# Explicit patterns per the plan doc. Using grep -E so the patterns stay
# auditable — no reliance on shell globbing.
GATED_PATTERN='^(skill/|tests/|dossier\.skill$)'

if ! echo "$CHANGED_FILES" | grep -Eq "$GATED_PATTERN"; then
    echo "PASS: no gated paths touched; CHANGELOG update not required"
    exit 0
fi

# At least one gated path was touched — CHANGELOG.md must also be in the diff.
if ! echo "$CHANGED_FILES" | grep -qx 'CHANGELOG.md'; then
    echo "FAIL: gated path touched but CHANGELOG.md not in diff" >&2
    echo "      gated files:" >&2
    echo "$CHANGED_FILES" | grep -E "$GATED_PATTERN" | sed 's/^/        /' >&2
    echo "      action: add an entry under '## [Unreleased]' in CHANGELOG.md" >&2
    exit 1
fi

# CHANGELOG.md is in the diff. Verify at least one added line falls inside
# the `## [Unreleased]` section of the post-change file.
#
# Why two-pass: a unified-diff hunk only includes context lines around each
# changed region, so the `## [Unreleased]` header is usually NOT present in
# the diff body when additions land deep inside an already-large Unreleased
# section. The earlier single-pass approach (look for `+## [Unreleased]`,
# then count `+` lines until the next `## [`) only fired when the header
# happened to be in the same hunk as the addition — which is the wrong
# trigger and produced false-negatives for any post-Phase-1 stream that
# appended to a long-running Unreleased.
#
# Pass 1: read the post-change file (HEAD revision of CHANGELOG.md) and
#         compute the [start, end) line range of the `## [Unreleased]`
#         section (end is the line of the next `## [...]` heading or EOF).
# Pass 2: parse the unified diff's hunk headers (`@@ -a,b +c,d @@`) to
#         track the post-change line number of every `+` line, and count
#         those whose line number falls inside [start, end).

#
# Note on shape: capture `git show` into a variable first, then feed the
# value to awk via `<<<`. An earlier shape used `git show | awk ... exit`,
# but awk's `exit` after matching the next `## [` heading SIGPIPE'd
# git show on some CI runners (exit 141) — same family of failure as the
# bypass-token scan, see commit history. The variable-capture form has
# no live producer to be SIGPIPE'd. awk now reads the whole input and
# emits the range at END.
CHANGELOG_AT_HEAD="$(git show "${HEAD_REF}:CHANGELOG.md")"
UNRELEASED_RANGE="$(
    awk '
        /^## \[Unreleased\]/      { start = NR; next }
        start && !done && /^## \[/ { end = NR; done = 1 }
        END                        { if (start) print start, (done ? end : NR + 1) }
    ' <<< "$CHANGELOG_AT_HEAD"
)"

if [ -z "$UNRELEASED_RANGE" ]; then
    echo "FAIL: '## [Unreleased]' heading not found in CHANGELOG.md at HEAD" >&2
    echo "      action: ensure the heading exists (Keep-a-Changelog 1.1.0 convention)" >&2
    exit 1
fi

UNRELEASED_START="${UNRELEASED_RANGE% *}"
UNRELEASED_END="${UNRELEASED_RANGE#* }"

UNRELEASED_ADDS="$(
    git diff "${MERGE_BASE}...${HEAD_REF}" -- CHANGELOG.md \
        | awk -v start="$UNRELEASED_START" -v end="$UNRELEASED_END" '
            /^\+\+\+ /         { next }           # skip file-header lines
            /^---/             { next }           # skip file-header lines
            /^@@ / {
                # Parse the post-change line range: `@@ -a,b +c,d @@`
                match($0, /\+[0-9]+/)
                cur = substr($0, RSTART + 1, RLENGTH - 1) + 0
                next
            }
            /^\+/              { if (cur >= start && cur < end) count++; cur++; next }
            /^-/               { next }           # removed lines do not advance cur
            { cur++ }                              # context line — advances cur
            END                { print count + 0 }
        '
)"

if [ "${UNRELEASED_ADDS}" -lt 1 ]; then
    echo "FAIL: CHANGELOG.md is in the diff but no lines added under '## [Unreleased]'" >&2
    echo "      action: document the schema/skill/test change under '## [Unreleased]'" >&2
    exit 1
fi

echo "PASS: gated paths touched; CHANGELOG.md updated with ${UNRELEASED_ADDS} line(s) under [Unreleased]"
exit 0
