#!/usr/bin/env bash
# build_skill.sh — package the Dossier skill into a distributable `.skill` archive.
#
# Authority: features/plan/18-version-tag-release-pipeline.md (Stream A).
#
# Output: dist/dossier-<version>.skill — a zip archive whose top-level
# directory is `skill/`. Inside:
#
#   skill/SKILL.md
#   skill/manifest.json
#   skill/references/*.md
#
# Excluded from the artifact: __pycache__, *.pyc, .DS_Store, editor
# metadata, coverage artifacts, pytest cache.
#
# Version resolution (priority order):
#   1. DOSSIER_VERSION env override → use verbatim.
#   2. Annotated v* tag at HEAD → tag string.
#   3. Latest v* ancestor → v<latest>-dev+<short-sha>.
#   4. No tag → v0.0.0-dev+<short-sha>.
#   5. No .git → v0.0.0-unknown.
#
# Exit codes:
#   0 — success
#   1 — build failure
#   2 — usage / environment error
#   3 — byte-mismatch: freshly built artifact differs from committed dossier.skill
#
# Byte-match guard:
#   If dossier.skill is committed and SKIP_BYTE_MATCH is unset, the freshly
#   built artifact must byte-match the committed copy. If they differ, the
#   committed copy is stale — regenerate it:
#     cp dist/dossier-*.skill dossier.skill && git add dossier.skill && git commit
#   Then retag if needed.
#
#   Bootstrap escape hatch (one-time use):
#     SKIP_BYTE_MATCH=1 bash .github/scripts/build_skill.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL_DIR="${REPO_ROOT}/skill"
DIST_DIR="${REPO_ROOT}/dist"

if [[ ! -d "${SKILL_DIR}" ]]; then
    echo "error: ${SKILL_DIR} not found — are you running from the repo root?" >&2
    exit 2
fi

# Resolve a usable Python interpreter (`python3` on Linux/macOS, `python`
# on Windows Git-Bash). Override with PYTHON=... if needed.
if [[ -z "${PYTHON:-}" ]]; then
    if command -v python3 >/dev/null 2>&1; then
        PYTHON="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON="python"
    else
        echo "error: no python interpreter on PATH (tried python3, python)" >&2
        exit 2
    fi
fi

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

if [[ -n "${DOSSIER_VERSION:-}" ]]; then
    VERSION="${DOSSIER_VERSION}"
    if command -v git >/dev/null 2>&1 && [[ -d "${REPO_ROOT}/.git" ]]; then
        COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
    else
        COMMIT="unknown"
    fi
elif command -v git >/dev/null 2>&1 && [[ -d "${REPO_ROOT}/.git" ]]; then
    # Only consider tags matching the v<MAJOR>.<MINOR>.<PATCH> family. Other
    # tags (e.g. operational/audit markers) must not flow into the artifact
    # version string.
    if VERSION="$(git -C "${REPO_ROOT}" describe --tags --exact-match --match 'v*' HEAD 2>/dev/null)"; then
        :
    elif TAG="$(git -C "${REPO_ROOT}" describe --tags --abbrev=0 --match 'v*' HEAD 2>/dev/null)"; then
        SHA="$(git -C "${REPO_ROOT}" rev-parse --short HEAD)"
        VERSION="${TAG}-dev+${SHA}"
    else
        SHA="$(git -C "${REPO_ROOT}" rev-parse --short HEAD)"
        VERSION="v0.0.0-dev+${SHA}"
    fi
    COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
else
    VERSION="v0.0.0-unknown"
    COMMIT="unknown"
fi

# ---------------------------------------------------------------------------
# Stage
# ---------------------------------------------------------------------------

mkdir -p "${DIST_DIR}"
TMPDIR_BUILD="$(mktemp -d -t dossier-skill-build-XXXXXX)"
trap 'rm -rf "${TMPDIR_BUILD}"' EXIT

STAGE="${TMPDIR_BUILD}/skill"
cp -R "${SKILL_DIR}/" "${STAGE}/"

# Strip dev-only artifacts.
find "${STAGE}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${STAGE}" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "${STAGE}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${STAGE}" -type f -name "*.pyo" -delete 2>/dev/null || true
find "${STAGE}" -type f -name ".DS_Store" -delete 2>/dev/null || true
find "${STAGE}" -type f -name "Thumbs.db" -delete 2>/dev/null || true
find "${STAGE}" -type f -name "*.swp" -delete 2>/dev/null || true
find "${STAGE}" -type f -name ".coverage*" -delete 2>/dev/null || true

# Make wrapper scripts executable (Dossier has no bin/, kept for parity).
if [[ -d "${STAGE}/bin" ]]; then
    chmod +x "${STAGE}/bin/"* 2>/dev/null || true
fi

# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

# built_at is pinned to a fixed timestamp — NOT $(date -u ...) — so two
# builds of the same source tree produce byte-identical bundles. Only
# `commit` is volatile between builds.
BUILT_AT="2026-01-01T00:00:00Z"
cat > "${STAGE}/manifest.json" <<MANIFEST
{
  "name": "dossier",
  "version": "${VERSION}",
  "built_at": "${BUILT_AT}",
  "commit": "${COMMIT:-unknown}"
}
MANIFEST

# ---------------------------------------------------------------------------
# Zip
# ---------------------------------------------------------------------------

OUT="${DIST_DIR}/dossier-${VERSION}.skill"
rm -f "${OUT}" "${DIST_DIR}/dossier-${VERSION}.skill.sha256"

# Use Python's stdlib `zipfile` rather than the external `zip` binary so
# this script is portable across CI runners (Ubuntu has zip, macOS has
# zip, but Windows Git-Bash often does not). Deterministic insertion
# order: the directory walk is sorted so the resulting archive is
# byte-stable across builds.
#
# Critical: info.date_time is pinned to (2026, 1, 1, 0, 0, 0) for every
# entry BEFORE writestr() so ZIP internal timestamps are also fixed. This
# is what makes the byte-match guard meaningful.
"${PYTHON:-python3}" - "$TMPDIR_BUILD" "$OUT" <<'PYEOF'
import os
import sys
import zipfile
from pathlib import Path

src = Path(sys.argv[1]) / "skill"
out = Path(sys.argv[2])

with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        arcname = str(Path("skill") / path.relative_to(src)).replace(os.sep, "/")
        # Preserve executable bits for files under bin/.
        info = zipfile.ZipInfo.from_file(path, arcname=arcname)
        if "/bin/" in arcname:
            info.external_attr = (0o755 << 16) | (info.external_attr & 0xFFFF)
        # Pin mtime to a fixed timestamp so two builds of the same source
        # produce byte-identical archives.
        info.date_time = (2026, 1, 1, 0, 0, 0)
        # ZipInfo.from_file() defaults compress_type to ZIP_STORED regardless
        # of the parent ZipFile's compression= setting; writestr(info, ...)
        # uses the per-entry value, so set it explicitly to honour the
        # DEFLATE invariant from HARDENING.md §9.
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, path.read_bytes())
PYEOF

# ---------------------------------------------------------------------------
# Checksum
# ---------------------------------------------------------------------------

if command -v sha256sum >/dev/null 2>&1; then
    (cd "${DIST_DIR}" && sha256sum "dossier-${VERSION}.skill" > "dossier-${VERSION}.skill.sha256")
elif command -v shasum >/dev/null 2>&1; then
    (cd "${DIST_DIR}" && shasum -a 256 "dossier-${VERSION}.skill" > "dossier-${VERSION}.skill.sha256")
else
    echo "warn: neither sha256sum nor shasum available — skipping checksum file" >&2
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

SIZE="$(wc -c < "${OUT}" | tr -d ' ')"
echo "Built:   ${OUT}"
echo "Size:    ${SIZE} bytes"
echo "Version: ${VERSION}"
echo "Commit:  ${COMMIT:-unknown}"
if [[ -f "${DIST_DIR}/dossier-${VERSION}.skill.sha256" ]]; then
    echo "SHA256:  $(cut -d' ' -f1 "${DIST_DIR}/dossier-${VERSION}.skill.sha256")"
fi

# ---------------------------------------------------------------------------
# Content-match guard (Dossier-specific)
# ---------------------------------------------------------------------------
#
# If dossier.skill is committed and SKIP_BYTE_MATCH is unset, every entry
# under skill/ in the freshly built artifact must match the committed copy
# byte-for-byte — EXCEPT skill/manifest.json, whose `commit` and `version`
# fields necessarily change with each HEAD commit. Exit 3 on mismatch so CI
# distinguishes a build failure (1) from a stale committed bundle (3).
#
# A whole-file byte-match is unworkable because the bundle's manifest tracks
# the HEAD commit SHA: any commit landing after the bundle was packed would
# spuriously fail the guard. The content-match below preserves the spirit
# (catch contributors who edit skill/ without re-running the packer) without
# the false-positive on commit-SHA churn.
#
# Recovery: cp dist/dossier-*.skill dossier.skill && git add dossier.skill
#           && git commit && git push && retag

if [[ -f "${REPO_ROOT}/dossier.skill" ]] && [[ -z "${SKIP_BYTE_MATCH:-}" ]]; then
    "${PYTHON:-python3}" - "${OUT}" "${REPO_ROOT}/dossier.skill" <<'PYEOF'
import sys
import zipfile

fresh_path, committed_path = sys.argv[1], sys.argv[2]
SKIP = {"skill/manifest.json"}

with zipfile.ZipFile(fresh_path) as a, zipfile.ZipFile(committed_path) as b:
    a_names = sorted(n for n in a.namelist() if n not in SKIP)
    b_names = sorted(n for n in b.namelist() if n not in SKIP)
    if a_names != b_names:
        only_a = sorted(set(a_names) - set(b_names))
        only_b = sorted(set(b_names) - set(a_names))
        print("error: bundle entry list mismatch", file=sys.stderr)
        if only_a:
            print(f"       only in fresh build:  {only_a}", file=sys.stderr)
        if only_b:
            print(f"       only in committed:    {only_b}", file=sys.stderr)
        print(f"       to recover: cp {fresh_path} dossier.skill && commit",
              file=sys.stderr)
        sys.exit(3)
    diffs = [name for name in a_names if a.read(name) != b.read(name)]
    if diffs:
        print("error: skill/ content drift between fresh and committed bundle",
              file=sys.stderr)
        print(f"       differing entries: {diffs}", file=sys.stderr)
        print(f"       to recover: cp {fresh_path} dossier.skill && commit",
              file=sys.stderr)
        sys.exit(3)
PYEOF
    echo "content-match: passed (manifest.json excluded — see HARDENING.md §9)"
fi
