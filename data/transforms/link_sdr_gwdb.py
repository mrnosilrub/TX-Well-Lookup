"""
Spatially link SDR well_reports with GWDB wells within 50 meters.
Writes pairs into well_links with a simple inverse-distance match_score.
"""

import os
import psycopg2


def link_within_distance(db_url: str, radius_m: float = 50.0) -> int:
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO well_links (sdr_id, gwdb_id, match_score)
                SELECT s.id AS sdr_id,
                       g.id AS gwdb_id,
                       GREATEST(0, 1 - (ST_Distance(s.geom::geography, g.geom::geography) / %s)) AS match_score
                FROM well_reports s
                JOIN gwdb_wells g
                  ON ST_DWithin(s.geom::geography, g.geom::geography, %s)
                ON CONFLICT (sdr_id, gwdb_id) DO UPDATE SET match_score = EXCLUDED.match_score
                """,
                (radius_m, radius_m),
            )
        conn.commit()
        # count links
        with conn.cursor() as cur2:
            cur2.execute("SELECT COUNT(*) FROM well_links")
            (count,) = cur2.fetchone()
    return int(count)


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required")
    n = link_within_distance(url)
    print(f"Linked pairs: {n}")


