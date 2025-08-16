"""
TWDB SDR Ingest.

- Existing function `upsert_sdr_from_csv` loads a small sample CSV for demos.
- New function `upsert_sdr_from_twdb_raw` parses the official SDR pipe-delimited
  text downloads from TWDB (WellData.txt + WellCompletion.txt) and upserts them.

Source (reference): https://www.twdb.texas.gov/groundwater/data/drillersdb.asp
"""

import csv
import os
from typing import Dict, List, Optional, Iterable
import csv

import psycopg2
from psycopg2.extras import execute_batch


def upsert_sdr_from_csv(csv_path: str, db_url: str) -> int:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[Dict[str, str]] = list(reader)
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            sql = (
                "INSERT INTO well_reports (id, owner_name, address, county, depth_ft, date_completed, geom) "
                "VALUES (%(id)s, %(owner_name)s, %(address)s, %(county)s, %(depth_ft)s, %(date_completed)s, "
                "ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)) "
                "ON CONFLICT (id) DO UPDATE SET owner_name = EXCLUDED.owner_name, address = EXCLUDED.address, "
                "county = EXCLUDED.county, depth_ft = EXCLUDED.depth_ft, date_completed = EXCLUDED.date_completed, "
                "geom = EXCLUDED.geom"
            )
            execute_batch(cur, sql, rows, page_size=500)
        conn.commit()
    return len(rows)


def _read_pipe_delimited(file_path: str) -> Iterable[Dict[str, str]]:
    """Yield dict rows from a pipe-delimited TWDB text file."""
    with open(file_path, newline="", encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            yield {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


def _first_nonempty(row: Dict[str, str], keys: List[str]) -> Optional[str]:
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return None


def _parse_float(value: Optional[str]) -> Optional[float]:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(str(value).strip())
    except Exception:
        return None


def upsert_sdr_from_twdb_raw(raw_dir: str, db_url: str, limit: Optional[int] = None) -> int:
    """
    Ingest SDR from official TWDB pipe-delimited files located in `raw_dir`.

    Expected files:
      - WellData.txt (ids, owner, address, county, possibly lat/lon)
      - WellCompletion.txt (depth, completion date)
    If lat/lon are missing in WellData, geom will be NULL (acceptable; can be
    enriched later).
    """
    import os

    well_data_path = os.path.join(raw_dir, "WellData.txt")
    completion_path = os.path.join(raw_dir, "WellCompletion.txt")
    if not os.path.exists(well_data_path):
        raise FileNotFoundError(well_data_path)

    # Build a small lookup for completion fields (depth/date)
    completion_by_id: Dict[str, Dict[str, Optional[str]]] = {}
    if os.path.exists(completion_path):
        for row in _read_pipe_delimited(completion_path):
            tid = _first_nonempty(row, [
                "TrackingNumber",
                "TRK_NO",
                "ReportTrackingNumber",
            ])
            if not tid:
                continue
            depth = _first_nonempty(row, [
                "TotalDepth",
                "CompletionDepth",
                "Depth",
            ])
            date_completed = _first_nonempty(row, [
                "CompletionDate",
                "CompletedDate",
                "DateCompleted",
            ])
            completion_by_id[tid] = {
                "depth_ft": depth,
                "date_completed": date_completed,
            }

    # Stream rows and upsert in batches
    batch: List[Dict[str, Optional[str]]] = []
    total = 0
    BATCH_SIZE = 1000

    def flush(rows: List[Dict[str, Optional[str]]]) -> int:
        if not rows:
            return 0
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                sql = (
                    "INSERT INTO well_reports (id, owner_name, address, county, depth_ft, date_completed, geom) "
                    "VALUES (%(id)s, %(owner_name)s, %(address)s, %(county)s, %(depth_ft)s, %(date_completed)s, "
                    "ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)) "
                    "ON CONFLICT (id) DO UPDATE SET owner_name = EXCLUDED.owner_name, address = EXCLUDED.address, "
                    "county = EXCLUDED.county, depth_ft = EXCLUDED.depth_ft, date_completed = EXCLUDED.date_completed, "
                    "geom = EXCLUDED.geom"
                )
                execute_batch(cur, sql, rows, page_size=500)
            conn.commit()
        return len(rows)

    for row in _read_pipe_delimited(well_data_path):
        tid = _first_nonempty(row, [
            "TrackingNumber",
            "TRK_NO",
            "ReportTrackingNumber",
        ])
        if not tid:
            continue

        owner = _first_nonempty(row, ["OwnerName", "Owner"]) or None
        street = _first_nonempty(row, ["StreetAddress", "Address", "Addr1"]) or ""
        city = _first_nonempty(row, ["City"]) or ""
        zipc = _first_nonempty(row, ["Zip", "ZIP"])
        address = ", ".join([p for p in [street, city, (zipc or "")] if p]).strip(", ") or None
        county = _first_nonempty(row, ["County", "CountyName"]) or None

        lat = _parse_float(_first_nonempty(row, [
            "Latitude", "LatitudeDD", "LatDD", "Lat", "WellLatitude"
        ]))
        lon = _parse_float(_first_nonempty(row, [
            "Longitude", "LongitudeDD", "LongDD", "Lon", "WellLongitude"
        ]))

        comp = completion_by_id.get(tid, {})
        depth_ft = _parse_float(comp.get("depth_ft"))
        date_completed = comp.get("date_completed")

        batch.append({
            "id": tid,
            "owner_name": owner,
            "address": address,
            "county": county,
            "depth_ft": depth_ft,
            "date_completed": date_completed,
            "lat": lat,
            "lon": lon,
        })

        if len(batch) >= BATCH_SIZE:
            total += flush(batch)
            batch = []
            if limit and total >= limit:
                break

    total += flush(batch)
    return total


