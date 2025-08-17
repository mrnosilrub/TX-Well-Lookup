#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
import os
import sys
from typing import Optional, Tuple

import psycopg2
from psycopg2 import sql


DATE_CANDIDATE_COLUMNS = [
    # WellData (drilling/completion)
    ("WellData", "DrillingEndDate"),
    ("WellData", "DrillingStartDate"),
    # PlugData (plugging)
    ("PlugData", "PluggingDate"),
    ("PlugData", "DateSubmitted"),
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Compute SDR as-of date across ground_truth tables")
    ap.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    ap.add_argument("--schema", default="ground_truth")
    ap.add_argument("--out", default="docs/AS_OF.md")
    return ap.parse_args()


def _parse_date_ymd(text: Optional[str]) -> Optional[date]:
    if not text:
        return None
    t = text.strip()
    if not t:
        return None
    # Accept YYYY-MM-DD or YYYY/MM/DD or MM/DD/YYYY; fall back silently if unparsable
    fmts = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y")
    for fmt in fmts:
        try:
            from datetime import datetime
            return datetime.strptime(t, fmt).date()
        except Exception:
            pass
    return None


def fetch_max_date(conn, schema: str, table: str, column: str) -> Optional[date]:
    # Columns are TEXT in ground_truth; pull max after normalizing to dates in SQL when possible
    # Try safe SQL normalization first; otherwise fallback to client-side parse of top values
    with conn.cursor() as cur:
        # Get top 500 non-null values ordered desc to quickly find a plausible max
        query = sql.SQL(
            "SELECT {col} FROM {schema}.{table} "
            "WHERE {col} IS NOT NULL AND trim({col}) <> %s "
            "ORDER BY {col} DESC NULLS LAST LIMIT 500"
        ).format(
            col=sql.Identifier(column),
            schema=sql.Identifier(schema),
            table=sql.Identifier(table),
        )
        cur.execute(query, ("",))
        vals = [r[0] for r in cur.fetchall() if r and r[0]]
    best: Optional[date] = None
    for v in vals:
        d = _parse_date_ymd(v)
        if d and (best is None or d > best):
            best = d
    return best


def compute_as_of(conn, schema: str) -> Tuple[Optional[date], list]:
    candidates = []
    for table, column in DATE_CANDIDATE_COLUMNS:
        try:
            d = fetch_max_date(conn, schema, table, column)
            candidates.append(((table, column), d))
        except Exception as exc:
            candidates.append(((table, column), None))
    best = None
    for (_, _), d in candidates:
        if d and (best is None or d > best):
            best = d
    return best, candidates


def main() -> int:
    args = parse_args()
    if not args.database_url:
        print("DATABASE_URL not provided", file=sys.stderr)
        return 2
    conn = psycopg2.connect(args.database_url)
    try:
        best, candidates = compute_as_of(conn, args.schema)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write("## SDR As-of Date\n\n")
            if best:
                f.write(f"As-of: {best.isoformat()}\n\n")
            else:
                f.write("As-of: unknown\n\n")
            f.write("Checked columns (table.column → parsed max):\n\n")
            for (t, c), d in candidates:
                f.write(f"- {t}.{c}: {d.isoformat() if d else 'n/a'}\n")
        print(f"wrote {args.out}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())


