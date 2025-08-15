# Reports Bundle — Plan (Stub)

This document outlines how the reports bundle will be assembled in later sprints. In Sprint 4 we are only documenting the approach; no runtime code is introduced here.

## Goals

- Provide a downloadable bundle (ZIP) that includes:
  - CSV of wells in scope
  - GeoJSON of the same wells as features (Point geometry)
  - A small JSON manifest with query parameters, counts, and source attributions
- Keep output shapes stable so the web and API layers can link to the same artifacts.

## Inputs (later)

- Primary rows will come from the database (e.g., `well_reports`), filtered by query parameters such as:
  - `q, county, date_from, date_to, depth_min, depth_max, lat, lon, radius_m, limit`
- In early development (before DB), CSV/GeoJSON may be generated from `data/fixtures/wells_stub.json` for parity with stubs.

## Outputs

- `wells.csv`
  - Columns (initial): `id, name, county, lat, lon, depth_ft, date_completed?`
  - CSV, UTF-8, header row present
- `wells.geojson`
  - FeatureCollection of Point features
  - `geometry`: `[lon, lat]`
  - `properties`: `id, name, county, depth_ft, date_completed?`
- `manifest.json`
  - Example shape:
{
  "created_at": "2025-01-01T12:00:00Z",
  "params": { "lat": 30.27, "lon": -97.74, "radius_m": 1609, "q": "smith" },
  "count": 123,
  "files": {
    "csv": "wells.csv",
    "geojson": "wells.geojson"
  },
  "sources": [
    { "name": "TWDB SDR", "license": "Public", "url": "https://www.twdb.texas.gov/" }
  ]
}

## Packaging

- Bundle as a ZIP archive with the three files above at the top level
- File naming convention (subject to refinement): `report_<report_id>.zip`
- Local dev: save under a writable directory (e.g., `./.reports/`)
- Future prod: upload to object storage (S3/R2) and serve via short-lived signed URLs

## Generation Flow (future)

1. Backend `POST /v1/reports` enqueues a job with the query parameters
2. Worker queries DB, exports CSV and GeoJSON, builds manifest
3. Worker zips files and uploads to storage (or writes locally in dev)
4. Backend `GET /v1/reports/{id}` returns status and URLs when ready

## Data Notes

- Coordinates should be normalized to WGS84 (EPSG:4326)
- Ensure numeric fields remain numeric in both CSV and GeoJSON properties
- Keep the CSV column order stable; append new optional columns at the end in future versions

## Testing (dev)

- For stubbed runs, generate outputs from `data/fixtures/wells_stub.json` and validate:
  - CSV row count equals JSON `items.length`
  - GeoJSON `features.length` equals CSV row count
  - Manifest `count` equals both of the above`
