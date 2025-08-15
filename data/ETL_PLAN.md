# ETL Plan — SDR, GWDB, RRC (Sprint 5)

This document outlines the initial ingest plan and expected schemas for migrating from stubs to real data.

## Sources

- TWDB SDR (Statewide Driller's Report) — bulk nightly files (pipe-delimited) and/or shapefile
- TWDB GWDB (Groundwater Database) — selected wells export
- TX RRC (Railroad Commission) — permits and wellbores CSVs

## Landing Tables (proposed)

- `well_reports` (SDR)
  - `id` (PK, text) — stable synthetic key (e.g., `sdr:<original_id>`)
  - `owner_name` (text)
  - `well_name` (text)
  - `county` (text)
  - `lat` (double precision)
  - `lon` (double precision)
  - `geom` (geometry(Point, 4326))
  - `date_completed` (date)
  - `depth_ft` (integer)
  - `source_row_hash` (text) — dedup aid
  - `ingested_at` (timestamptz default now())

- `plugging_reports` (SDR)
  - `id` (PK, text)
  - `well_id` (text, FK to `well_reports.id` where applicable)
  - `date_plugged` (date)
  - `notes` (text)

- `gwdb_wells` (GWDB)
  - `id` (PK, text) — `gwdb:<original_id>`
  - `county` (text)
  - `lat` (double precision)
  - `lon` (double precision)
  - `geom` (geometry(Point, 4326))
  - `total_depth_ft` (integer)
  - `aquifer` (text)

- `rrc_permits`
  - `api14` (PK, text)
  - `operator` (text)
  - `status` (text)
  - `permit_date` (date)
  - `lat` (double precision)
  - `lon` (double precision)
  - `geom` (geometry(Point, 4326))

- `rrc_wellbores`
  - `api14` (PK, text)
  - `wellbore` (text)
  - `lat` (double precision)
  - `lon` (double precision)
  - `geom` (geometry(Point, 4326))

- `well_links`
  - `sdr_id` (text)
  - `gwdb_id` (text)
  - `match_score` (double precision)
  - `linked_at` (timestamptz)

## Ingest Strategy

- Use Python with `pandas` for parsing and `psycopg2` or `SQLAlchemy` for UPSERTs
- Normalize coordinates to EPSG:4326 and set `geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326)`
- Idempotency via `ON CONFLICT (id) DO UPDATE` and `source_row_hash` change detection
- Minimal transforms in landing tables; enrichments happen in separate views/materialized tables later

## File Handling

- Prefer streaming and chunked inserts for large SDR files
- Validate row coordinates are within Texas bounding box
- Log and skip rows with missing or invalid coordinates

## Parity With Stubs (transition)

- Ensure `/v1/search` returns fields compatible with current stub shape
- For early demos, a small seed (≤1k rows) may be derived from `data/fixtures/wells_stub.json`

## Dependencies (future)

- Python: `pandas`, `psycopg2-binary`, `sqlalchemy`, `shapely` (optional)
- DB: Postgres + PostGIS
