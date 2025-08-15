import csv
import os
import psycopg2

DB_URL = os.getenv('DB_URL_PSY', 'postgresql://postgres:postgres@localhost:5432/txwell')
CSV_PATH = os.getenv('CSV_PATH', '/app/data/fixtures/sdr_sample.csv')

def main() -> None:
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    with open(CSV_PATH, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = float(row['lat'])
            lon = float(row['lon'])
            cur.execute(
                """
                INSERT INTO well_reports (id, name, county, depth_ft, lat, lon, geom)
                VALUES (%s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)
                ON CONFLICT (id) DO UPDATE SET
                  name = EXCLUDED.name,
                  county = EXCLUDED.county,
                  depth_ft = EXCLUDED.depth_ft,
                  lat = EXCLUDED.lat,
                  lon = EXCLUDED.lon,
                  geom = EXCLUDED.geom
                """,
                [row['id'], row['name'], row['county'], int(row['depth_ft']), lat, lon, lon, lat]
            )
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Seed SDR sample CSV into the database's well_reports table.

Requires DATABASE_URL env var or use docker-compose service environment inside the API container.

Usage:
  python data/scripts/seed_sdr_sample.py data/fixtures/sdr_sample.csv
"""
from __future__ import annotations

import csv
import os
import sys
from typing import List, Dict

import psycopg2
from psycopg2.extras import execute_batch


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python seed_sdr_sample.py <csv_path>")
        return 2
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        return 2

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is required")
        return 2

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

    print(f"Seeded {len(rows)} rows into well_reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


