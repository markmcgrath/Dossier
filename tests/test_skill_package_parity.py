"""
Parity tests — every file inside dossier.skill must match the on-disk source
under skill/. Catches stale repacks where source was edited but the ZIP was
not regenerated, or vice versa.
"""
from pathlib import Path

import pytest


def _normalize(b: bytes) -> bytes:
    """Normalize line endings so CRLF vs LF differences do not flag parity."""
    return b.replace(b"\r\n", b"\n")


def test_zip_entries_match_source_files(skill_zip, vault_path):
    """Every entry in dossier.skill must exactly match the file under skill/."""
    src_root = vault_path / "skill"
    assert src_root.is_dir(), f"skill/ source directory not found at {src_root}"

    mismatches = []
    for name in skill_zip.namelist():
        if name.endswith("/"):
            continue  # directory entry, nothing to compare
        if not name.startswith("skill/"):
            mismatches.append((name, "ZIP entry not under skill/ prefix"))
            continue
        rel = name[len("skill/"):]
        src_file = src_root / rel
        if not src_file.exists():
            mismatches.append((name, "no matching source file under skill/"))
            continue
        zip_bytes = skill_zip.read(name)
        src_bytes = src_file.read_bytes()
        if _normalize(zip_bytes) != _normalize(src_bytes):
            mismatches.append(
                (name, f"content differs (zip={len(zip_bytes)}B, src={len(src_bytes)}B)")
            )

    assert not mismatches, (
        "dossier.skill is out of sync with skill/ source. Repack required.\n"
        + "\n".join(f"  - {n}: {why}" for n, why in mismatches)
    )


def test_source_files_all_present_in_zip(skill_zip, vault_path):
    """Every file under skill/ must appear in dossier.skill (no orphans on disk)."""
    src_root = vault_path / "skill"
    assert src_root.is_dir(), f"skill/ source directory not found at {src_root}"

    src_entries = set()
    for f in src_root.rglob("*"):
        if f.is_file():
            rel = f.relative_to(src_root).as_posix()
            src_entries.add(f"skill/{rel}")

    zip_entries = {n for n in skill_zip.namelist() if not n.endswith("/")}

    missing_from_zip = src_entries - zip_entries
    extra_in_zip = zip_entries - src_entries

    assert not missing_from_zip, (
        "Source files under skill/ are missing from dossier.skill: "
        f"{sorted(missing_from_zip)}. Repack required."
    )
    assert not extra_in_zip, (
        "dossier.skill contains entries with no source file under skill/: "
        f"{sorted(extra_in_zip)}. Either delete the entry or add the source file."
    )
