#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from typing import List, Tuple

import psycopg2


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="CI smoke: verify DB connectivity and key table counts")
    ap.add_argument("--database-url", default=os.getenv("DATABASE_URL"), required=False)
    ap.add_argument("--schema", default="ground_truth")
    ap.add_argument("--min-tables", type=int, default=10, help="Fail if fewer tables exist")
    return ap.parse_args()


def fetch_table_counts(conn, schema: str) -> List[Tuple[str, int]]:
    # Fetch table list then count per table with properly quoted identifiers
    with conn.cursor() as cur:
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename", (schema,))
        tables = [r[0] for r in cur.fetchall()]
    out: List[Tuple[str, int]] = []
    with conn.cursor() as cur:
        for t in tables:
            cur.execute(f'SELECT COUNT(*) FROM "{schema}"."{t}"')
            out.append((t, int(cur.fetchone()[0] or 0)))
    return out


def main() -> int:
    args = parse_args()
    if not args.database_url:
        print("DATABASE_URL not provided", file=sys.stderr)
        return 2
    conn = psycopg2.connect(args.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            _ = cur.fetchone()
        counts = fetch_table_counts(conn, args.schema)
        if len(counts) < args.min_tables:
            print(f"Too few tables in schema '{args.schema}': {len(counts)} < {args.min_tables}", file=sys.stderr)
            return 3
        # Print a short summary; CI just needs non-zero exit on failure
        top = ", ".join([f"{t}={c}" for t, c in counts[:5]])
        print(f"tables={len(counts)} sample_counts=[{top}]")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())


