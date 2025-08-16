"""
TWDB GWDB Ingest — placeholder for selected wells ingest.

For Sprint 7, we simulate a small GWDB CSV and load into gwdb_wells.
"""

import csv
import os
from typing import Dict, List

import psycopg2
from psycopg2.extras import execute_batch


def upsert_gwdb_from_csv(csv_path: str, db_url: str) -> int:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[Dict[str, str]] = list(reader)
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            sql = (
                "INSERT INTO gwdb_wells (id, county, total_depth_ft, aquifer, geom) "
                "VALUES (\n"
                "  %(id)s, %(county)s, %(total_depth_ft)s::int, %(aquifer)s,\n"
                "  CASE WHEN %(lat)s IS NOT NULL AND %(lon)s IS NOT NULL\n"
                "       THEN ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)\n"
                "       ELSE NULL END\n"
                ")\n"
                "ON CONFLICT (id) DO UPDATE SET\n"
                "  county = EXCLUDED.county,\n"
                "  total_depth_ft = EXCLUDED.total_depth_ft,\n"
                "  aquifer = EXCLUDED.aquifer,\n"
                "  geom = EXCLUDED.geom"
            )
            execute_batch(cur, sql, rows, page_size=500)
        conn.commit()
    return len(rows)


