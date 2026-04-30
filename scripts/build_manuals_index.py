#!/usr/bin/env python3
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ASSET_XLSX = Path("/Users/donert/Documents/UACTech/uacdata/assets.xlsx")
MANUALS_ROOT = ROOT / "manuals"
MANUAL_MAP_PATH = MANUALS_ROOT / "asset_manual_map.json"
OUTPUT_PATH = MANUALS_ROOT / "assets_manuals_index.json"

NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def load_asset_rows() -> list[dict]:
    with zipfile.ZipFile(ASSET_XLSX) as zf:
        shared_strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", NS):
                shared_strings.append("".join(t.text or "" for t in si.iterfind(".//a:t", NS)))

        def cell_value(cell: ET.Element) -> str:
            cell_type = cell.attrib.get("t")
            value_node = cell.find("a:v", NS)
            if value_node is None:
                return ""
            value = value_node.text or ""
            if cell_type == "s":
                return shared_strings[int(value)]
            return value

        sheet = ET.fromstring(zf.read("xl/worksheets/sheet2.xml"))
        rows = sheet.findall(".//a:sheetData/a:row", NS)
        if not rows:
            return []

        first_row_cells = rows[0].findall("a:c", NS)
        columns = [re.sub(r"\d+", "", cell.attrib["r"]) for cell in first_row_cells]
        headers = {column: cell_value(cell) for column, cell in zip(columns, first_row_cells)}

        records = []
        for row in rows[1:]:
            cells = {
                re.sub(r"\d+", "", cell.attrib["r"]): cell_value(cell)
                for cell in row.findall("a:c", NS)
            }
            record = {headers[column]: cells.get(column, "") for column in columns}
            if record.get("AssetTag"):
                records.append(record)
        return records


def normalize_manuals(raw_manuals):
    if isinstance(raw_manuals, str):
        manuals = [raw_manuals]
    else:
        manuals = list(raw_manuals or [])
    normalized = []
    for rel_path in manuals:
        normalized.append(
            {
                "name": Path(rel_path).name,
                "path": rel_path,
                "url": f"/manuals/files/{rel_path}",
            }
        )
    return normalized


def build_index() -> list[dict]:
    with MANUAL_MAP_PATH.open() as f:
        manual_map = json.load(f)

    rows = load_asset_rows()
    index = []
    for row in rows:
        asset_tag = row.get("AssetTag", "").strip()
        manuals = normalize_manuals(manual_map.get(asset_tag, []))
        if not manuals:
            continue
        index.append(
            {
                "asset_tag": asset_tag,
                "category": row.get("Category", "").strip(),
                "manufacturer": row.get("Manufacturer", "").strip(),
                "model": row.get("Model", "").strip(),
                "type": row.get("Type", "").strip(),
                "description": row.get("Desc", "").strip(),
                "building": row.get("Building", "").strip(),
                "room": row.get("Room", "").strip(),
                "location": row.get("Location", "").strip(),
                "in_service": row.get("InService", "").strip(),
                "manual_count": len(manuals),
                "manuals": manuals,
            }
        )

    index.sort(key=lambda item: item["asset_tag"])
    return index


def main() -> None:
    index = build_index()
    with OUTPUT_PATH.open("w") as f:
        json.dump(index, f, indent=2)
        f.write("\n")
    print(f"Wrote {len(index)} asset records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
