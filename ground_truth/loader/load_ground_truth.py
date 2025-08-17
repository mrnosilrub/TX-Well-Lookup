#!/usr/bin/env python3
"""
Ground Truth Loader — 1:1 SDR mirror

- Drops and recreates a target schema (default: ground_truth)
- For each .txt in the provided zip, creates a table named exactly after the file
  (without extension), quoted as an identifier, with columns taken from the
  header row (also quoted), all typed as TEXT
- Bulk loads the file using COPY FROM STDIN with delimiter '|', HEADER true,
  and latin-1 encoding

Notes
- Duplicate header names in a file are made unique by appending a numeric suffix
  (e.g., "Column", "Column_2", ...). A COMMENT is added to preserve original
  header strings.
- Identifiers longer than 63 bytes are truncated with a numeric suffix if needed
  to maintain uniqueness. Original header text is preserved via COMMENT.
- Table names are quoted and match the file basename exactly (case, spaces,
  punctuation). Identifiers are SQL-escaped.
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import zipfile
import re
from typing import Dict, List, Tuple
import csv
import tempfile

import psycopg2
from psycopg2.extensions import connection as PGConnection
from psycopg2.extensions import cursor as PGCursor
from psycopg2 import sql

# Increase CSV field size limit to handle very large SDR fields
try:
    csv.field_size_limit(1_000_000_000)
except OverflowError:
    csv.field_size_limit(2_147_483_647)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Load SDR zip into ground_truth schema (1:1)")
	parser.add_argument("--zip", dest="zip_path", required=True, help="Path to SDR zip (contains .txt files)")
	parser.add_argument("--database-url", dest="database_url", required=True, help="Postgres connection URL")
	parser.add_argument("--schema", dest="schema", default="ground_truth", help="Target schema name")
	return parser.parse_args()


def _pg_ident_truncate(name: str, max_len: int = 63) -> str:
	# PostgreSQL identifier length limit applies even to quoted idents
	if len(name) <= max_len:
		return name
	base = name[: max_len - 3]
	return base + "_t"


def _dedupe(names: List[str]) -> Tuple[List[str], Dict[str, str]]:
	"""Ensure list is unique within 63-byte identifier limit by suffixing _2, _3, ...
	Return (adjusted_names, original_to_adjusted_map) for COMMENTs.
	"""
	result: List[str] = []
	counts: Dict[str, int] = {}
	mapping: Dict[str, str] = {}
	for original in names:
		candidate = original
		# First, truncate if needed to stay within identifier limit
		candidate = _pg_ident_truncate(candidate)
		key = candidate.lower()
		counts.setdefault(key, 0)
		if key in (n.lower() for n in result):
			# increment until unique
			while True:
				counts[key] += 1
				suffixed = _pg_ident_truncate(f"{candidate}_{counts[key]+1}")
				if suffixed.lower() not in (n.lower() for n in result):
					candidate = suffixed
					break
		result.append(candidate)
		if candidate != original:
			mapping[candidate] = original
	return result, mapping


def _quote_ident(name: str) -> sql.Composed:
	# Properly quote an identifier with potential quotes/spaces
	return sql.SQL('"{}"').format(sql.SQL(name.replace('"', '""')))


def _create_schema(cur: PGCursor, schema: str) -> None:
	cur.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(_quote_ident(schema)))
	cur.execute(sql.SQL("CREATE SCHEMA {}" ).format(_quote_ident(schema)))


def _read_header_from_zip(zf: zipfile.ZipFile, member: str, encoding: str = "latin-1") -> List[str]:
	with zf.open(member, "r") as f:
		# Read first line (header). We do not rely on CSV here; header is simple '|' delimited
		first = f.readline()
		if not first:
			return []
		text = first.decode(encoding, errors="replace").rstrip("\n\r")
		# Split on pipe without CSV semantics (header seldom contains quotes)
		fields = [h for h in text.split("|")] if text else []
		# Require at least 2 columns to treat as tabular; else skip (e.g., ReadMe files)
		return fields if len(fields) >= 2 else []


def _is_data_member(member: str) -> bool:
	"""Heuristically decide if a .txt looks like a tabular data file.

	Skips obvious non-tabular docs like ReadMe, Dictionary, Manifest, License, Notes.
	"""
	base = os.path.basename(member).lower()
	if any(tok in base for tok in ["readme", "dictionary", "manifest", "license", "notes", "howto", "how_to"]):
		return False
	return True


def _create_table(cur: PGCursor, schema: str, table_raw: str, headers_raw: List[str]) -> Tuple[List[str], Dict[str, str]]:
	# Deduplicate/limit identifiers but strive to keep exact originals as much as possible
	adj_cols, mapping = _dedupe(headers_raw)
	# Build CREATE TABLE with quoted table and column identifiers exactly as adjusted
	cols_sql = []
	for adj in adj_cols:
		cols_sql.append(sql.SQL("{} TEXT").format(_quote_ident(adj)))
	create = sql.SQL("CREATE TABLE {}.{} (\n\t{}\n)").format(
		_quote_ident(schema), _quote_ident(table_raw), sql.SQL(",\n\t").join(cols_sql)
	)
	cur.execute(create)
	# Add comments to preserve original header text where adjusted
	for adj, orig in mapping.items():
		comment = sql.SQL("COMMENT ON COLUMN {}.{}.{} IS %s").format(
			_quote_ident(schema), _quote_ident(table_raw), _quote_ident(adj)
		)
		cur.execute(comment, (f"source:{orig}",))
	return adj_cols, mapping


def _copy_into(cur: PGCursor, zf: zipfile.ZipFile, member: str, schema: str, table_raw: str, columns: List[str]) -> int:
	# Sanitize data into a temporary CSV that matches the header column count exactly
	# - Uses Python csv reader (delimiter='|', quotechar='"') for robust parsing
	# - Pads missing fields with empty strings; trims extra fields beyond header count
	# - Writes a new header matching adjusted column identifiers so HEADER true works
	n = len(columns)
	with zf.open(member, "r") as f_in:
		text = io.TextIOWrapper(f_in, encoding="latin-1", errors="replace", newline="")
		reader = csv.reader(text, delimiter='|')
		try:
			_ = next(reader)
		except StopIteration:
			return 0
		tmp_path = None
		with tempfile.NamedTemporaryFile("w", delete=False, encoding="latin-1", newline="") as f_out:
			writer = csv.writer(f_out, delimiter='|', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(columns)
			for row in reader:
				if len(row) < n:
					row = list(row) + [""] * (n - len(row))
				elif len(row) > n:
					row = list(row[:n])
				writer.writerow(row)
			tmp_path = f_out.name
	# COPY from sanitized temp file
	copy_sql = sql.SQL(
		"COPY {}.{} ({}) FROM STDIN WITH (FORMAT csv, DELIMITER '|', HEADER true, ENCODING 'LATIN1')"
	).format(
		_quote_ident(schema),
		_quote_ident(table_raw),
		sql.SQL(', ').join([_quote_ident(c) for c in columns]),
	)
	with open(tmp_path, "rb") as f_bin:
		cur.copy_expert(copy_sql.as_string(cur.connection), f_bin)
	# Return loaded row count
	cur.execute(sql.SQL("SELECT COUNT(*) FROM {}.{}").format(_quote_ident(schema), _quote_ident(table_raw)))
	return int(cur.fetchone()[0] or 0)
	# Return loaded row count
	cur.execute(sql.SQL("SELECT COUNT(*) FROM {}.{}").format(_quote_ident(schema), _quote_ident(table_raw)))
	return int(cur.fetchone()[0] or 0)


def main() -> int:
	args = parse_args()
	if not os.path.exists(args.zip_path):
		print(f"zip not found: {args.zip_path}", file=sys.stderr)
		return 2
	conn: PGConnection = psycopg2.connect(args.database_url)
	conn.autocommit = False
	try:
		with conn.cursor() as cur:
			_create_schema(cur, args.schema)
			with zipfile.ZipFile(args.zip_path, "r") as zf:
				members = [m for m in zf.namelist() if m.lower().endswith(".txt") and not m.endswith("/") and _is_data_member(m)]
				members.sort()
				summary: List[Tuple[str, int]] = []
				for member in members:
					base = os.path.basename(member)
					table_raw = os.path.splitext(base)[0]
					headers = _read_header_from_zip(zf, member, encoding="latin-1")
					if not headers:
						print(f"skip (no header): {member}")
						continue
					cols_adj, _ = _create_table(cur, args.schema, table_raw, headers)
					loaded = _copy_into(cur, zf, member, args.schema, table_raw, cols_adj)
					summary.append((table_raw, loaded))
				print("tables_loaded=", {k: v for k, v in summary})
		conn.commit()
		return 0
	except Exception as exc:
		conn.rollback()
		raise
	finally:
		conn.close()


if __name__ == "__main__":
	sys.exit(main())
