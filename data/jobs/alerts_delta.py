#!/usr/bin/env python3
"""
Scan for new SDR and RRC rows within any alert radius and enqueue notifications (dev: insert rows).
This is a minimal simulation for Sprint 10.
"""
import os
from typing import List, Tuple
import psycopg2


def fetch_alerts(conn) -> List[Tuple[str, float, float, int]]:
    with conn.cursor() as cur:
        cur.execute("SELECT id::text, lat, lon, radius_m FROM alerts")
        return cur.fetchall()


def notify_nearby(conn, table: str, id_col: str, alerts: List[Tuple[str, float, float, int]]) -> int:
    count = 0
    for aid, lat, lon, radius in alerts:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO alert_notifications (id, alert_id, source, source_id)
                SELECT gen_random_uuid(), %s, %s, t.{id_col}
                FROM {table} t
                WHERE ST_DWithin(t.geom::geography, ST_SetSRID(ST_MakePoint(%s,%s),4326)::geography, %s)
                ON CONFLICT DO NOTHING
                """,
                (aid, table, lon, lat, radius),
            )
            count += cur.rowcount or 0
    return count


def main() -> int:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL required")
        return 2
    with psycopg2.connect(db_url) as conn:
        alerts = fetch_alerts(conn)
        if not alerts:
            print("no alerts configured")
            return 0
        total = 0
        total += notify_nearby(conn, "well_reports", "id", alerts)
        total += notify_nearby(conn, "rrc_permits", "api14", alerts)
        conn.commit()
        print(f"notifications inserted: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


