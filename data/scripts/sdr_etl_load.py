#!/usr/bin/env python3
"""
SDR ETL Orchestrator (DS4)

Loads extracted SDR .txt files into normalized tables, idempotently.
Relies on:
- DS3 alias file for header normalization
- Parsing rules (latin-1, pipe-delimited, trim, type coercion)
- Execution order defined in DS4 doc

Inputs:
- --source-dir: extracted folder with SDR .txt files (e.g., data/raw_data/SDRDownload)
- --aliases: sdr_header_aliases.json
- --database-url: postgres URL
- --batch-size: upsert batch size (default 1000)

Note: This is a focused orchestrator; it demonstrates structure and logging,
and can be extended to cover all edge cases.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

import psycopg2
from psycopg2.extras import execute_batch


def load_aliases(path: str) -> Dict[str, Dict[str, List[str]]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_key(key: str) -> str:
    return (key or "").strip()


def pick_first(headers: Dict[str, List[str]], *candidates: str) -> str | None:
    # Given alias mapping for a file, return the first present candidate header
    # headers: { 'headers_from_manifest': [...], 'headers_from_dictionary': [...] }
    all_headers = set(map(normalize_key, headers.get("headers_from_manifest", []) or []))
    all_headers.update(map(normalize_key, headers.get("headers_from_dictionary", []) or []))
    for c in candidates:
        if normalize_key(c) in all_headers:
            return c
    return None


def parse_rows(file_path: str, delimiter: str = "|") -> Iterable[Dict[str, str]]:
    with open(file_path, "r", encoding="latin-1", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            yield { (k or "").strip(): (v or "").strip() for k, v in row.items() }


def coerce_float(val: str) -> float | None:
    try:
        if val == "":
            return None
        return float(val)
    except Exception:
        return None


def coerce_int(val: str) -> int | None:
    try:
        if val == "":
            return None
        return int(float(val))
    except Exception:
        return None


def coerce_date(val: str) -> str | None:
    # Accept Y-M-D variants; leave as text for DB DATE cast
    t = val.strip()
    if not t:
        return None
    # Let DB parse; otherwise could add python dateutil here
    return t


def within_tx(lat: float | None, lon: float | None) -> bool:
    if lat is None or lon is None:
        return False
    return 25.0 <= lat <= 37.0 and -107.0 <= lon <= -93.0


def upsert(conn, sql: str, rows: List[Tuple], page_size: int) -> int:
    if not rows:
        return 0
    with conn.cursor() as cur:
        execute_batch(cur, sql, rows, page_size=page_size)
    return len(rows)


def etl(source_dir: str, aliases_path: str, database_url: str, batch_size: int = 1000) -> None:
    aliases = load_aliases(aliases_path)
    start_total = time.time()
    totals = defaultdict(int)
    skipped = defaultdict(int)

    conn = psycopg2.connect(database_url)
    conn.autocommit = False
    try:
        def log_step(name: str, rows: int, t0: float):
            print(f"name={name} rows={rows} time={time.time()-t0:.2f}")

        # 1) WellData.txt → well_reports base rows
        f = os.path.join(source_dir, "WellData.txt")
        if os.path.exists(f):
            t0 = time.time()
            hdr = aliases.get("WellData.txt", {})
            id_key = pick_first(hdr, "TrackingNumber", "ReportTrackingNumber", "TRK_NO", "WellReportTrackingNumber")
            name_key = pick_first(hdr, "OwnerName", "Owner")
            addr_key = pick_first(hdr, "Address", "Street")
            county_key = pick_first(hdr, "County", "CountyName")
            lat_key = pick_first(hdr, "CoordDDLat", "Latitude")
            lon_key = pick_first(hdr, "CoordDDLong", "Longitude")
            rows_buf: List[Tuple] = []
            for r in parse_rows(f):
                sdr_id = (r.get(id_key or "", "").strip() if id_key else "")
                if not sdr_id:
                    skipped["well_reports"] += 1
                    continue
                owner = (r.get(name_key or "", "").strip() or None) if name_key else None
                addr = (r.get(addr_key or "", "").strip() or None) if addr_key else None
                county = (r.get(county_key or "", "").strip() or None) if county_key else None
                lat = coerce_float(r.get(lat_key or "", "")) if lat_key else None
                lon = coerce_float(r.get(lon_key or "", "")) if lon_key else None
                # Defer geom; set lat/lon in app later or alter table to include columns if desired
                rows_buf.append((sdr_id, owner, addr, county))
                if len(rows_buf) >= batch_size:
                    totals["well_reports"] += upsert(conn,
                        """
                        INSERT INTO well_reports (id, owner_name, address, county)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                          owner_name = EXCLUDED.owner_name,
                          address = EXCLUDED.address,
                          county = EXCLUDED.county
                        """,
                        rows_buf, batch_size)
                    rows_buf.clear()
            totals["well_reports"] += upsert(conn,
                """
                INSERT INTO well_reports (id, owner_name, address, county)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  owner_name = EXCLUDED.owner_name,
                  address = EXCLUDED.address,
                  county = EXCLUDED.county
                """,
                rows_buf, batch_size)
            log_step("WellData", totals["well_reports"], t0)

        # 2) WellCompletion.txt → enrich depth_ft, date_completed
        f = os.path.join(source_dir, "WellCompletion.txt")
        if os.path.exists(f):
            t0 = time.time()
            hdr = aliases.get("WellCompletion.txt", {})
            id_key = pick_first(hdr, "TrackingNumber", "ReportTrackingNumber", "TRK_NO", "WellReportTrackingNumber")
            depth_key = pick_first(hdr, "TotalDepth", "CompletionDepth", "Depth")
            date_key = pick_first(hdr, "CompletionDate", "CompletedDate", "DateCompleted")
            rows_buf = []
            for r in parse_rows(f):
                sdr_id = (r.get(id_key or "", "").strip() if id_key else "")
                if not sdr_id:
                    continue
                depth = coerce_int(r.get(depth_key or "", "")) if depth_key else None
                datev = coerce_date(r.get(date_key or "", "")) if date_key else None
                rows_buf.append((depth, datev, sdr_id))
                if len(rows_buf) >= batch_size:
                    totals["well_reports_enrich"] += upsert(conn,
                        """
                        UPDATE well_reports
                        SET depth_ft = COALESCE(%s, depth_ft),
                            date_completed = COALESCE(%s, date_completed)
                        WHERE id = %s
                        """,
                        rows_buf, batch_size)
                    rows_buf.clear()
            totals["well_reports_enrich"] += upsert(conn,
                """
                UPDATE well_reports
                SET depth_ft = COALESCE(%s, depth_ft),
                    date_completed = COALESCE(%s, date_completed)
                WHERE id = %s
                """,
                rows_buf, batch_size)
            log_step("WellCompletion", totals["well_reports_enrich"], t0)

        # Child tables loaders (examples shown; pattern can be replicated for all)
        def upsert_child(file_name: str, table: str, field_map: List[Tuple[str, List[str]]], pk_norm_col: str, pk_aliases: List[str]):
            path = os.path.join(source_dir, file_name)
            if not os.path.exists(path):
                return
            t0 = time.time()
            hdr = aliases.get(file_name, {})
            id_key = pick_first(hdr, "TrackingNumber", "ReportTrackingNumber", "TRK_NO", "WellReportTrackingNumber")
            pk_key = pick_first(hdr, *pk_aliases)
            rows_buf: List[Tuple] = []
            seq_by_id: Dict[str, int] = defaultdict(int)
            for r in parse_rows(path):
                sdr_id = (r.get(id_key or "", "").strip() if id_key else "")
                if not sdr_id:
                    continue
                # primary key value from file (if present), else generate per-sdr sequence
                pk_val = r.get(pk_key or "", "").strip() if pk_key else ""
                if pk_val == "":
                    seq_by_id[sdr_id] += 1
                    pk_val = str(seq_by_id[sdr_id])
                values: List[object] = [sdr_id, pk_val]
                for target, candidates in field_map:
                    src = pick_first(hdr, *candidates) or ""
                    values.append(r.get(src, "").strip())
                rows_buf.append(tuple(values))
                if len(rows_buf) >= batch_size:
                    placeholders = ", ".join(["%s"] * len(values))
                    cols = ", ".join(["sdr_id", pk_norm_col] + [t for t, _ in field_map])
                    conflict = ", ".join(["sdr_id", pk_norm_col])
                    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT ({conflict}) DO NOTHING"
                    totals[table] += upsert(conn, sql, rows_buf, batch_size)
                    rows_buf.clear()
            if rows_buf:
                placeholders = ", ".join(["%s"] * len(rows_buf[0]))
                cols = ", ".join(["sdr_id", pk_norm_col] + [t for t, _ in field_map])
                conflict = ", ".join(["sdr_id", pk_norm_col])
                sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT ({conflict}) DO NOTHING"
                totals[table] += upsert(conn, sql, rows_buf, batch_size)
            log_step(file_name.replace('.txt',''), totals[table], t0)

        # Examples: replicate as needed for full coverage
        upsert_child("WellBoreHole.txt", "well_boreholes", [
            ("start_depth_ft", ["StartDepth", "StartDepthFt", "FromDepth", "TopDepth"]) ,
            ("end_depth_ft", ["EndDepth", "EndDepthFt", "ToDepth", "BottomDepth"]),
            ("diameter_in", ["Diameter", "DiameterIn", "BoreDiameter"]),
            ("notes", ["Notes", "Remarks"]),
        ], pk_norm_col="borehole_no", pk_aliases=["BoreHoleNo", "BoreholeNo", "BoreHoleNumber", "SeqNo", "Sequence"])

        upsert_child("WellCasing.txt", "well_casings", [
            ("top_ft", ["TopDepth", "Top", "TopFt"]),
            ("bottom_ft", ["BottomDepth", "Bottom", "BottomFt"]),
            ("diameter_in", ["Diameter", "DiameterIn"]),
            ("material", ["Material", "CasingMaterial"]),
        ], pk_norm_col="casing_no", pk_aliases=["CasingNo", "CasingNumber", "SeqNo", "Sequence"])

        upsert_child("WellFilter.txt", "well_filters", [
            ("top_ft", ["TopDepth", "Top", "TopFt"]),
            ("bottom_ft", ["BottomDepth", "Bottom", "BottomFt"]),
            ("size", ["Size", "SlotSize", "FilterSize"]),
            ("material", ["Material", "FilterMaterial"]),
        ], pk_norm_col="filter_no", pk_aliases=["FilterNo", "FilterNumber", "SeqNo", "Sequence"])

        # Commit once at end for better throughput
        conn.commit()
        print(f"total_rows_by_table={dict(totals)} skipped={dict(skipped)} time_total={time.time()-start_total:.2f}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="SDR ETL Orchestrator (DS4)")
    ap.add_argument("--source-dir", required=True)
    ap.add_argument("--aliases", required=True)
    ap.add_argument("--database-url", required=True)
    ap.add_argument("--batch-size", type=int, default=1000)
    args = ap.parse_args()
    etl(args.source_dir, args.aliases, args.database_url, args.batch_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


