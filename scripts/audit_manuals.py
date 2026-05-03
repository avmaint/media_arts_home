#!/usr/bin/env python3
"""
Compares PDF files in the manuals/ directory against asset_manual_map.json.
Outputs a JSON report to stdout showing mapped, unmapped, and missing files.
"""
import json
import sys
from pathlib import Path

ROOT         = Path(__file__).resolve().parent.parent
MANUALS_ROOT = ROOT / "manuals"
MANUAL_MAP   = MANUALS_ROOT / "asset_manual_map.json"


def main():
    if not MANUAL_MAP.exists():
        print(json.dumps({"error": f"{MANUAL_MAP} not found"}), file=sys.stderr)
        sys.exit(1)

    with MANUAL_MAP.open() as f:
        manual_map = json.load(f)

    # Build set of all paths referenced in the map (relative to MANUALS_ROOT)
    mapped_paths = {}  # path -> [asset_tags]
    for asset_tag, paths in manual_map.items():
        for p in (paths if isinstance(paths, list) else [paths]):
            mapped_paths.setdefault(p, []).append(asset_tag)

    # Build set of all PDFs on disk (relative to MANUALS_ROOT)
    disk_paths = set()
    for pdf in MANUALS_ROOT.rglob("*.pdf"):
        rel = pdf.relative_to(MANUALS_ROOT).as_posix()
        disk_paths.add(rel)

    mapped_set   = set(mapped_paths.keys())
    unmapped     = sorted(disk_paths - mapped_set)   # on disk, not in map
    missing      = sorted(mapped_set - disk_paths)   # in map, not on disk
    matched      = sorted(disk_paths & mapped_set)   # in both

    result = {
        "summary": {
            "total_pdfs_on_disk":      len(disk_paths),
            "mapped":                  len(matched),
            "unmapped":                len(unmapped),
            "missing_from_filesystem": len(missing),
        },
        "unmapped_pdfs": [
            {"asset_tag": "", "path": p, "filename": Path(p).name}
            for p in unmapped
        ],
        "missing_from_filesystem": [
            {"asset_tag": mapped_paths[p], "path": p, "filename": Path(p).name}
            for p in missing
        ],
        "mapped_pdfs": [
            {"asset_tag": mapped_paths[p], "path": p, "filename": Path(p).name}
            for p in matched
        ],
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
