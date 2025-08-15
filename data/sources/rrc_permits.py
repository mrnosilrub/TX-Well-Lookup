"""
RRC Permits ingest — loads daily permit CSV into rrc_permits.
CSV header: api14,operator,status,permit_date,lat,lon
"""
import csv
import os
from typing import Dict, List

import psycopg2
from psycopg2.extras import execute_batch


def upsert_permits_from_csv(csv_path: str, db_url: str) -> int:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[Dict[str, str]] = [r for r in reader]
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            sql = (
                "INSERT INTO rrc_permits (api14, operator, status, permit_date, geom) "
                "VALUES (%(api14)s, %(operator)s, %(status)s, %(permit_date)s, "
                "ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)) "
                "ON CONFLICT (api14) DO UPDATE SET operator = EXCLUDED.operator, status = EXCLUDED.status, "
                "permit_date = EXCLUDED.permit_date, geom = EXCLUDED.geom"
            )
            execute_batch(cur, sql, rows, page_size=1000)
        conn.commit()
    return len(rows)


