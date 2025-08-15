"""
TWDB SDR Ingest — placeholder for real nightly ingest.

For Sprint 7, we simulate ingest by reading an existing CSV (sdr_sample.csv)
and upserting rows into well_reports. Real implementation would download and
parse official SDR bulk files.
"""

import csv
import os
from typing import Dict, List

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


