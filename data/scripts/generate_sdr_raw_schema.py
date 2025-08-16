#!/usr/bin/env python3
"""
Generate a raw SDR schema SQL from DS1 manifest.json.

Approach for 100% accurate mapping:
- Create schema sdr_raw
- For each .txt file, create table sdr_raw.<snake_case_filename>
- Columns are the header_fields from the manifest, sanitized to snake_case identifiers
- All columns typed as TEXT to avoid incorrect inference
- Add comments preserving original header names
- If a column resembles TrackingNumber (case-insensitive), add a non-unique index for joins

This raw layer is for staging/exact mapping. Normalization happens in DS2 curated DDL.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Dict, List


def to_snake_identifier(name: str) -> str:
    # Lowercase, replace non-alnum with underscore, collapse repeats, trim edges
    s = name.strip()
    s = re.sub(r"[^0-9a-zA-Z]+", "_", s)
    # camelCase or PascalCase -> snake (basic heuristic)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = s.lower()
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "col"
    if re.match(r"^[0-9]", s):
        s = f"c_{s}"
    return s


def make_table_name(filename: str) -> str:
    base = os.path.splitext(os.path.basename(filename))[0]
    return to_snake_identifier(base)


def looks_like_tracking(col: str) -> bool:
    s = col.replace(" ", "").replace("_", "").lower()
    return s in {"trackingnumber", "tracking_no", "trackingnum"}


def generate_sql(manifest: Dict) -> str:
    files: List[Dict] = manifest.get("files", [])
    lines: List[str] = []
    lines.append("-- Auto-generated raw SDR schema from manifest.json")
    lines.append("CREATE SCHEMA IF NOT EXISTS sdr_raw;")
    lines.append("")
    for entry in files:
        name = entry.get("name", "")
        headers: List[str] = entry.get("header_fields", [])
        if not name or not headers:
            continue
        table = make_table_name(name)
        col_map = [(to_snake_identifier(h), h) for h in headers]
        # Ensure unique column identifiers
        seen = set()
        unique_cols = []
        for c_snake, c_raw in col_map:
            candidate = c_snake
            suffix = 1
            while candidate in seen:
                suffix += 1
                candidate = f"{c_snake}_{suffix}"
            seen.add(candidate)
            unique_cols.append((candidate, c_raw))

        lines.append(f"-- File: {name}")
        lines.append(f"CREATE TABLE IF NOT EXISTS sdr_raw.{table} (")
        # TEXT for 100% fidelity mapping; types curated later in normalized layer
        col_defs = [f"  {c} TEXT" for c, _ in unique_cols]
        lines.append(",\n".join(col_defs))
        lines.append(");")
        # Comments with original header
        for c_snake, c_raw in unique_cols:
            safe_raw = c_raw.replace("'", "''")
            lines.append(f"COMMENT ON COLUMN sdr_raw.{table}.{c_snake} IS 'source:{safe_raw}';")
        # Helpful index on TrackingNumber-like columns if present
        track_cols = [c for c, raw in unique_cols if looks_like_tracking(raw)]
        if track_cols:
            idx_name = f"idx_{table}_tracking"[:60]
            lines.append(f"CREATE INDEX IF NOT EXISTS {idx_name} ON sdr_raw.{table} ({track_cols[0]});")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate raw SDR schema from manifest")
    parser.add_argument("--manifest", required=True, help="Path to manifest.json produced by DS1")
    parser.add_argument("--out", required=True, help="Path to write generated SQL")
    args = parser.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    sql = generate_sql(manifest)
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(sql)
    os.replace(tmp, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


