#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import psycopg2


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Generate Markdown schema doc for ground_truth")
    ap.add_argument("--database-url", required=True)
    ap.add_argument("--schema", default="ground_truth")
    ap.add_argument("--out", default="ground_truth/SCHEMA.md")
    return ap.parse_args()


def fetch_tables(conn, schema: str) -> List[Tuple[str, int]]:
    sql = (
        "SELECT c.relname AS table_name, COALESCE(s.n_live_tup, c.reltuples)::bigint AS approx_rows "
        "FROM pg_class c "
        "JOIN pg_namespace n ON n.oid = c.relnamespace "
        "LEFT JOIN pg_stat_all_tables s ON s.relid = c.oid "
        "WHERE n.nspname = %s AND c.relkind = 'r' "
        "ORDER BY c.relname"
    )
    with conn.cursor() as cur:
        cur.execute(sql, (schema,))
        return [(r[0], int(r[1] or 0)) for r in cur.fetchall()]


def fetch_columns(conn, schema: str, table: str) -> List[Tuple[int, str, str, str]]:
    # ordinal_position, column_name, data_type, is_nullable
    sql = (
        "SELECT ordinal_position, column_name, data_type, is_nullable "
        "FROM information_schema.columns "
        "WHERE table_schema=%s AND table_name=%s "
        "ORDER BY ordinal_position"
    )
    with conn.cursor() as cur:
        cur.execute(sql, (schema, table))
        return [(int(r[0]), str(r[1]), str(r[2]), str(r[3])) for r in cur.fetchall()]


def fetch_col_comments(conn, schema: str, table: str) -> Dict[str, str]:
    sql = (
        "SELECT a.attname, d.description "
        "FROM pg_attribute a "
        "JOIN pg_class c ON c.oid = a.attrelid "
        "JOIN pg_namespace n ON n.oid = c.relnamespace "
        "LEFT JOIN pg_description d ON d.objoid = a.attrelid AND d.objsubid = a.attnum "
        "WHERE n.nspname=%s AND c.relname=%s AND a.attnum>0 AND NOT a.attisdropped "
        "ORDER BY a.attnum"
    )
    out: Dict[str, str] = {}
    with conn.cursor() as cur:
        cur.execute(sql, (schema, table))
        for name, desc in cur.fetchall():
            if desc:
                out[str(name)] = str(desc)
    return out


def render_md(schema: str, tables: List[Tuple[str, int]], columns_by_table: Dict[str, List[Tuple[int, str, str, str]]], comments_by_table: Dict[str, Dict[str, str]]) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines: List[str] = []
    lines.append(f"# Ground Truth Schema — {schema}")
    lines.append("")
    lines.append(f"Generated at {ts}")
    lines.append("")
    lines.append(f"Tables: {len(tables)}")
    lines.append("")
    if tables:
        lines.append("## Tables")
        for t, approx in tables:
            lines.append(f"- {t} (approx rows: {approx})")
        lines.append("")
    for t, approx in tables:
        lines.append(f"## {t}")
        lines.append("")
        lines.append(f"Approx rows: {approx}")
        lines.append("")
        lines.append("| Column | Type | Nullable | Comment |")
        lines.append("|---|---|:--:|---|")
        cols = columns_by_table.get(t, [])
        comments = comments_by_table.get(t, {})
        for _, name, dtype, nullable in cols:
            comment = comments.get(name, "")
            lines.append(f"| {name} | {dtype} | {('NO' if nullable.upper()=='NO' else 'YES')} | {comment} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    conn = psycopg2.connect(args.database_url)
    try:
        tables = fetch_tables(conn, args.schema)
        columns_by_table: Dict[str, List[Tuple[int, str, str, str]]] = {}
        comments_by_table: Dict[str, Dict[str, str]] = {}
        for t, _ in tables:
            columns_by_table[t] = fetch_columns(conn, args.schema, t)
            comments_by_table[t] = fetch_col_comments(conn, args.schema, t)
        md = render_md(args.schema, tables, columns_by_table, comments_by_table)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"wrote {args.out}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())


