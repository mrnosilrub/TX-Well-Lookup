#!/usr/bin/env python3
"""
Extract SDR header alias candidates from DS1 manifest and the SDR Excel dictionary.

Output: JSON mapping by file name with:
- headers_from_manifest: list of header strings from manifest.json
- headers_from_dictionary: list of column names parsed from the Excel dictionary for that file (best effort)

We do not guess normalized field names here; we only aggregate authoritative header variants
to achieve 100% fidelity.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List


def default_dictionary_paths(base_dir: str) -> List[str]:
    # Common paths in the extracted SDR ZIP
    return [
        os.path.join(base_dir, "ReadMe", "SDRDownloadColumnDescriptions.xlsx"),
        os.path.join(os.path.dirname(base_dir), "ReadMe", "SDRDownloadColumnDescriptions.xlsx"),
    ]


def load_dictionary_columns(xlsx_path: str) -> Dict[str, List[str]]:
    try:
        import openpyxl  # type: ignore
    except Exception:
        return {}
    if not os.path.exists(xlsx_path):
        return {}
    try:
        wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    except Exception:
        return {}
    result: Dict[str, List[str]] = {}
    # Heuristic: tabs may be named by file, or a summary sheet lists per-file columns
    for ws in wb.worksheets:
        sheet_name = (ws.title or "").strip()
        headers: List[str] = []
        try:
            # Scan first row for column header labels
            first_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            for cell in first_row:
                if cell is None:
                    continue
                val = str(cell).strip()
                if val:
                    headers.append(val)
        except Exception:
            headers = []
        # If plausible headers are present, store them keyed by sheet name
        if headers:
            result[sheet_name] = headers
    return result


def map_sheet_to_filename(sheet_name: str) -> str:
    # Attempt to align sheet names to SDR filenames
    name = sheet_name.strip()
    # normalize common variations (remove spaces, unify case)
    normalized = name.replace(" ", "")
    candidates = [
        f"{normalized}.txt",
        f"{name}.txt",
    ]
    for cand in candidates:
        return cand
    return name + ".txt"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract SDR header aliases")
    parser.add_argument("--manifest", required=True, help="Path to manifest.json")
    parser.add_argument("--source-dir", required=True, help="Extracted SDRDownload directory (for dictionary)")
    parser.add_argument("--out", required=True, help="Output JSON path (aliases)")
    args = parser.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest_files: List[Dict] = manifest.get("files", [])

    # find dictionary xlsx
    xlsx_paths = default_dictionary_paths(args.source_dir)
    dictionary_cols_by_sheet: Dict[str, List[str]] = {}
    for p in xlsx_paths:
        dictionary_cols_by_sheet = load_dictionary_columns(p)
        if dictionary_cols_by_sheet:
            break

    # Build output structure
    out: Dict[str, Dict[str, List[str]]] = {}
    for entry in manifest_files:
        fname = entry.get("name", "")
        headers = entry.get("header_fields", []) or []
        out_entry: Dict[str, List[str]] = {
            "headers_from_manifest": headers,
            "headers_from_dictionary": [],
        }
        # Try to pull from dictionary by matching sheet names loosely
        match_keys = [
            fname,
            os.path.splitext(fname)[0],
            os.path.splitext(fname)[0].replace(" ", ""),
        ]
        for sheet, cols in dictionary_cols_by_sheet.items():
            key_variants = [
                sheet,
                os.path.splitext(sheet)[0],
                os.path.splitext(sheet)[0].replace(" ", ""),
                map_sheet_to_filename(sheet),
            ]
            if any(kv.lower() in match_keys[0].lower() for kv in key_variants):
                out_entry["headers_from_dictionary"] = cols
                break
        out[fname] = out_entry

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


