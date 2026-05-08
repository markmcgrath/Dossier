#!/usr/bin/env python3
"""
verify_skill_artifact.py — structural smoke test for a dossier .skill artifact.

Usage:
    python .github/scripts/verify_skill_artifact.py <path-to-artifact.skill>

Exit codes:
    0 — all checks passed
    1 — one or more checks failed (diagnostic printed to stderr)

Checks performed:
    1. Path exists and is a file.
    2. Valid ZIP (testzip() returns None).
    3. All entries are under the `skill/` prefix; no .pytest_cache,
       __pycache__, .DS_Store, Thumbs.db entries.
    4. Required entries present: skill/SKILL.md,
       skill/references/scoring-guide.md, skill/manifest.json.
    5. skill/SKILL.md parses as YAML-frontmatter-then-markdown; frontmatter
       has `name` and `description`; description <= 1024 chars.
    6. skill/SKILL.md line count is in [300, 2000].
    7. skill/references/scoring-guide.md length > 100 lines.
    8. skill/manifest.json is valid JSON with exactly four keys
       (name, version, built_at, commit); name == "dossier";
       version matches ^v\\d+\\.\\d+\\.\\d+(-[\\w.+-]+)?$.

Stdlib only — no third-party imports. Inline parse_frontmatter helper
duplicates the logic from tests/conftest.py rather than importing it, so
this script can be run without pytest installed.

Authority: features/plan/18-version-tag-release-pipeline.md (Stream A).
"""

import json
import re
import sys
import zipfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """
    Extract YAML frontmatter from markdown text.

    Returns (frontmatter_dict, body_text) on success, or (None, text) if
    no valid YAML frontmatter fence is found.  Frontmatter values are parsed
    with a simple key: value line scanner — sufficient for Dossier's shallow
    frontmatter; no pyyaml dependency required.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text

    # Locate the closing --- fence.
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_lines = lines[1:i]
            body = "\n".join(lines[i + 1:])
            fm = {}
            for line in fm_lines:
                if ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip()
                    # Strip surrounding quotes if present.
                    if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                        value = value[1:-1]
                    if key:
                        fm[key] = value
            return fm, body

    return None, text


def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-artifact.skill>", file=sys.stderr)
        sys.exit(1)

    artifact_path = sys.argv[1]

    # 1. Path exists and is a file.
    import os
    if not os.path.exists(artifact_path):
        fail(f"artifact not found: {artifact_path}")
    if not os.path.isfile(artifact_path):
        fail(f"artifact is not a file: {artifact_path}")

    # 2. Valid ZIP.
    try:
        zf = zipfile.ZipFile(artifact_path, "r")
    except zipfile.BadZipFile as e:
        fail(f"not a valid ZIP archive: {e}")

    bad = zf.testzip()
    if bad is not None:
        fail(f"ZIP is corrupt — bad entry: {bad}")

    names = zf.namelist()

    # 3. All entries under skill/ prefix; no forbidden entries.
    forbidden_patterns = (".pytest_cache", "__pycache__", ".DS_Store", "Thumbs.db")
    for name in names:
        if not name.startswith("skill/"):
            fail(f"entry outside skill/ prefix: {name!r}")
        for pattern in forbidden_patterns:
            if pattern in name:
                fail(f"forbidden entry in artifact: {name!r} (matches {pattern!r})")

    # 4. Required entries present.
    required = [
        "skill/SKILL.md",
        "skill/references/scoring-guide.md",
        "skill/manifest.json",
    ]
    for entry in required:
        if entry not in names:
            fail(f"required entry missing: {entry!r}. Found: {names}")

    # 5. skill/SKILL.md frontmatter.
    skill_md_bytes = zf.read("skill/SKILL.md")
    try:
        skill_md_text = skill_md_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        fail(f"skill/SKILL.md is not valid UTF-8: {e}")

    fm, _ = parse_frontmatter(skill_md_text)
    if fm is None:
        fail("skill/SKILL.md has no parseable YAML frontmatter")
    if "name" not in fm:
        fail("skill/SKILL.md frontmatter missing key: name")
    if "description" not in fm:
        fail("skill/SKILL.md frontmatter missing key: description")
    desc = fm["description"]
    if len(desc) > 1024:
        fail(
            f"skill/SKILL.md frontmatter description is {len(desc)} chars; max 1024"
        )

    # 6. skill/SKILL.md line count in [300, 2000].
    skill_lines = skill_md_text.split("\n")
    line_count = len(skill_lines)
    if not (300 <= line_count <= 2000):
        fail(
            f"skill/SKILL.md has {line_count} lines; expected 300–2000"
        )

    # 7. skill/references/scoring-guide.md length > 100 lines.
    guide_bytes = zf.read("skill/references/scoring-guide.md")
    try:
        guide_text = guide_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        fail(f"skill/references/scoring-guide.md is not valid UTF-8: {e}")
    guide_lines = guide_text.split("\n")
    if len(guide_lines) <= 100:
        fail(
            f"skill/references/scoring-guide.md has {len(guide_lines)} lines; expected > 100"
        )

    # 8. skill/manifest.json shape.
    manifest_bytes = zf.read("skill/manifest.json")
    try:
        manifest_text = manifest_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        fail(f"skill/manifest.json is not valid UTF-8: {e}")
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as e:
        fail(f"skill/manifest.json is not valid JSON: {e}")

    if not isinstance(manifest, dict):
        fail("skill/manifest.json must be a JSON object")
    if set(manifest.keys()) != {"name", "version", "built_at", "commit"}:
        fail(
            f"skill/manifest.json must have exactly the keys "
            f"{{name, version, built_at, commit}}; got {set(manifest.keys())}"
        )
    if manifest["name"] != "dossier":
        fail(
            f"skill/manifest.json name must be 'dossier'; got {manifest['name']!r}"
        )
    version_pattern = r"^v\d+\.\d+\.\d+(-[\w.+-]+)?$"
    if not re.match(version_pattern, manifest["version"]):
        fail(
            f"skill/manifest.json version {manifest['version']!r} does not match "
            f"{version_pattern}"
        )

    zf.close()
    print(f"OK: {artifact_path}")
    print(f"    version={manifest['version']}")
    print(f"    built_at={manifest['built_at']}")
    print(f"    commit={manifest['commit']}")
    print(f"    entries={len(names)}")


if __name__ == "__main__":
    main()
