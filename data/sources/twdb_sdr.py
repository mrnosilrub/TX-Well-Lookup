"""
TWDB SDR Ingest.

- Existing function `upsert_sdr_from_csv` loads a small sample CSV for demos.
- New function `upsert_sdr_from_twdb_raw` parses the official SDR pipe-delimited
  text downloads from TWDB (WellData.txt + WellCompletion.txt) and upserts them.

Source (reference): https://www.twdb.texas.gov/groundwater/data/drillersdb.asp
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Iterable, Any

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
                "VALUES (\n"
                "  %(id)s, %(owner_name)s, %(address)s, %(county)s, %(depth_ft)s::int, NULLIF(%(date_completed)s, '')::date,\n"
                "  CASE WHEN %(lat)s IS NOT NULL AND %(lon)s IS NOT NULL\n"
                "       THEN ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)\n"
                "       ELSE NULL END\n"
                ")\n"
                "ON CONFLICT (id) DO UPDATE SET\n"
                "  owner_name = EXCLUDED.owner_name,\n"
                "  address = EXCLUDED.address,\n"
                "  county = EXCLUDED.county,\n"
                "  depth_ft = EXCLUDED.depth_ft,\n"
                "  date_completed = EXCLUDED.date_completed,\n"
                "  geom = EXCLUDED.geom"
            )
            execute_batch(cur, sql, rows, page_size=500)
        conn.commit()
    return len(rows)


def _read_pipe_delimited(file_path: str) -> Iterable[Dict[str, str]]:
    """Yield dict rows from a pipe-delimited TWDB text file.

    Handles rows with extra columns (None keys) gracefully and strips whitespace
    from both keys and string values. Extra columns are ignored.
    """
    with open(file_path, newline="", encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            normalized: Dict[str, str] = {}
            for k, v in row.items():
                if k is None:
                    # Extra columns without headers; skip
                    continue
                key = k.strip() if isinstance(k, str) else str(k)
                if isinstance(v, list):
                    # DictReader may pack overflow fields into a list under None key; skip
                    continue
                value = v.strip() if isinstance(v, str) else v
                normalized[key] = value
            yield normalized


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


def _parse_date_iso(value: Optional[str]) -> Optional[str]:
    """Parse a date string in common formats to ISO (YYYY-MM-DD). Returns None on failure."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    # Try a few known formats
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d", "%d-%b-%Y"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    # Fallback: return original if it looks like ISO already
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return text
    return None


def _normalize_key(key: str) -> str:
    """Lowercase alphanumerics only (remove spaces/punct) for robust header matching."""
    return "".join(ch for ch in str(key).lower() if ch.isalnum())


def _first_nonempty_norm(row_norm: Dict[str, Any], keys: List[str]) -> Optional[str]:
    for k in keys:
        v = row_norm.get(_normalize_key(k))
        if v is None:
            continue
        s = str(v).strip()
        if s != "":
            return s
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
    def _detect_tracking_key(row_norm_keys: List[str]) -> Optional[str]:
        # Preferred exact candidates (normalized)
        preferred = [
            _normalize_key(k) for k in (
                "WellReportTrackingNumber",
                "Well Report Tracking Number",
                "TrackingNumber",
                "TRK_NO",
                "TRK NO",
                "ReportTrackingNumber",
                "Report Tracking Number",
                "Tracking No",
                "Tracking_No",
                "ReportTrackingNo",
                "Report Tracking No",
            )
        ]
        keys_set = set(row_norm_keys)
        for cand in preferred:
            if cand in keys_set:
                return cand
        # Heuristic fallback: any key that contains both "tracking" and "number"
        for k in row_norm_keys:
            if "tracking" in k and ("number" in k or k.endswith("no") or "trackingno" in k):
                return k
        # Heuristic fallback: any key that contains "trk" and "no"
        for k in row_norm_keys:
            if "trk" in k and "no" in k:
                return k
        return None

    comp_tracking_key: Optional[str] = None
    if os.path.exists(completion_path):
        for row in _read_pipe_delimited(completion_path):
            row_norm: Dict[str, Any] = {_normalize_key(k): v for k, v in row.items()}
            if comp_tracking_key is None:
                comp_tracking_key = _detect_tracking_key(list(row_norm.keys()))
            tid = None if comp_tracking_key is None else row_norm.get(comp_tracking_key)
            if tid is None or str(tid).strip() == "":
                tid = _first_nonempty_norm(row_norm, [
                    "TrackingNumber",
                    "TRK_NO",
                    "ReportTrackingNumber",
                    "Report Tracking Number",
                    "TRK NO",
                ])
            if not tid:
                continue
            depth = _first_nonempty_norm(row_norm, [
                "TotalDepth",
                "CompletionDepth",
                "Depth",
                "PumpDepth",
            ])
            date_completed = _first_nonempty_norm(row_norm, [
                "CompletionDate",
                "CompletedDate",
                "DateCompleted",
                "Completion Date",
                "Completed Date",
                "Date Completed",
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
                    "VALUES (\n"
                    "  %(id)s, %(owner_name)s, %(address)s, %(county)s, %(depth_ft)s::int, NULLIF(%(date_completed)s, '')::date,\n"
                    "  CASE WHEN %(lat)s IS NOT NULL AND %(lon)s IS NOT NULL\n"
                    "       THEN ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)\n"
                    "       ELSE NULL END\n"
                    ")\n"
                    "ON CONFLICT (id) DO UPDATE SET\n"
                    "  owner_name = EXCLUDED.owner_name,\n"
                    "  address = EXCLUDED.address,\n"
                    "  county = EXCLUDED.county,\n"
                    "  depth_ft = EXCLUDED.depth_ft,\n"
                    "  date_completed = EXCLUDED.date_completed,\n"
                    "  geom = EXCLUDED.geom"
                )
                execute_batch(cur, sql, rows, page_size=500)
            conn.commit()
        return len(rows)

    skipped_missing_id = 0
    scanned_rows = 0
    well_tracking_key: Optional[str] = None
    for row in _read_pipe_delimited(well_data_path):
        scanned_rows += 1
        row_norm: Dict[str, Any] = {_normalize_key(k): v for k, v in row.items()}
        if well_tracking_key is None:
            well_tracking_key = _detect_tracking_key(list(row_norm.keys()))
        tid = None if well_tracking_key is None else row_norm.get(well_tracking_key)
        if tid is None or str(tid).strip() == "":
            tid = _first_nonempty_norm(row_norm, [
                "TrackingNumber",
                "TRK_NO",
                "ReportTrackingNumber",
                "Report Tracking Number",
                "TRK NO",
            ])
        if not tid:
            skipped_missing_id += 1
            continue

        owner = _first_nonempty_norm(row_norm, ["OwnerName", "Owner", "Owner Name"]) or None
        street = _first_nonempty_norm(row_norm, ["WellAddress1", "StreetAddress", "Address", "Addr1", "Addr 1", "Addr"]) or ""
        city = _first_nonempty_norm(row_norm, ["WellCity", "City", "CityName"]) or ""
        zipc = _first_nonempty_norm(row_norm, ["WellZip", "Zip", "ZIP", "ZipCode", "ZIP Code"]) or None
        address = ", ".join([p for p in [street, city, (zipc or "")] if p]).strip(", ") or None
        county = _first_nonempty_norm(row_norm, ["County", "CountyName", "County Name"]) or None

        lat = _parse_float(_first_nonempty_norm(row_norm, [
            "CoordDDLat", "Latitude", "LatitudeDD", "LatDD", "Lat", "WellLatitude", "Latitude (Decimal Degrees)"
        ]))
        lon = _parse_float(_first_nonempty_norm(row_norm, [
            "CoordDDLong", "Longitude", "LongitudeDD", "LongDD", "Lon", "WellLongitude", "Longitude (Decimal Degrees)"
        ]))

        comp = completion_by_id.get(tid, {})
        depth_ft = _parse_float(comp.get("depth_ft"))
        date_completed = _parse_date_iso(comp.get("date_completed"))

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
    # Light telemetry in logs to help diagnose zero-ingest cases
    try:
        print(f"SDR parsed rows scanned={scanned_rows}, skipped_missing_id={skipped_missing_id}, upserted={total}")
    except Exception:
        pass
    return total


