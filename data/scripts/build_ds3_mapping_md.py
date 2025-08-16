#!/usr/bin/env python3
"""
Build a human-readable DS3 mapping markdown from:
- manifest.json (from DS1)
- sdr_header_aliases.json (from DS3 extractor)

Output: Markdown summarizing per-file:
- Target normalized table (heuristic mapping)
- Canonical key detection (headers containing TrackingNumber variants)
- Headers from manifest and from the dictionary (for review)

This does not attempt to fully auto-map every column. It provides a structured,
accurate review doc to finalize ETL mappings.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List, Tuple


TARGET_TABLE_MAP: Dict[str, str] = {
    # Core/enrich
    "welldata": "well_reports",
    "wellcompletion": "well_reports",
    # Construction
    "wellborehole": "well_boreholes",
    "wellcasing": "well_casings",
    "wellfilter": "well_filters",
    "wellsealrange": "well_seal_ranges",
    "wellpackers": "well_packers",
    "wellplugback": "well_plug_back",
    # Geology/hydro/lithology
    "wellstrata": "well_strata",
    "welllevels": "well_levels",
    "welltest": "well_test",
    "wellinjuriousconstituent": "well_injurious_constituent",
    "welllithology": "well_lithology",
    # Plugging
    "plugdata": "plug_reports",
    "plugborehole": "plug_boreholes",
    "plugcasing": "plug_casing",
    "plugrange": "plug_range",
}


def normalize_key(name: str) -> str:
    return (name or "").lower().replace(" ", "").replace("_", "")


def guess_target_table(filename: str) -> str:
    base = os.path.splitext(os.path.basename(filename))[0]
    key = normalize_key(base)
    # try exact, then substring
    if key in TARGET_TABLE_MAP:
        return TARGET_TABLE_MAP[key]
    for k, v in TARGET_TABLE_MAP.items():
        if k in key:
            return v
    return "well_reports"  # fallback


def find_tracking_candidates(headers: List[str]) -> List[str]:
    candidates = []
    for h in headers:
        n = normalize_key(h)
        if any(tok in n for tok in ["trackingnumber", "trackingno", "trkno", "reporttrackingnumber"]):
            candidates.append(h)
    return candidates


def build_markdown(manifest: Dict, aliases: Dict) -> str:
    files: List[Dict] = manifest.get("files", [])
    lines: List[str] = []
    lines.append("## DS3 Mapping — Based on Snapshot")
    lines.append("")
    for entry in files:
        fname = entry.get("name", "")
        if not fname:
            continue
        manifest_headers: List[str] = entry.get("header_fields", []) or []
        alias_entry: Dict = aliases.get(fname, {}) if isinstance(aliases, dict) else {}
        dict_headers: List[str] = alias_entry.get("headers_from_dictionary", []) or []
        target_table = guess_target_table(fname)
        tracking = find_tracking_candidates(manifest_headers + dict_headers)
        lines.append(f"### {fname}")
        lines.append("")
        lines.append(f"- Target table: `{target_table}`")
        if tracking:
            lines.append(f"- SDR ID candidates: {', '.join(tracking)}")
        else:
            lines.append("- SDR ID candidates: (none detected)")
        lines.append("")
        lines.append("- Headers (manifest):")
        for h in manifest_headers:
            lines.append(f"  - {h}")
        if dict_headers:
            lines.append("- Headers (dictionary):")
            for h in dict_headers:
                lines.append(f"  - {h}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Build DS3 mapping markdown")
    p.add_argument("--manifest", required=True)
    p.add_argument("--aliases", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(args.aliases, "r", encoding="utf-8") as f:
        aliases = json.load(f)
    md = build_markdown(manifest, aliases)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(md)
    os.replace(tmp, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


