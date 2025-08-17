## Future tasks — performance and search optimizations (defer)

These are optional, low‑risk optimizations to apply after MVP search/API is working. They help queries stay fast as data grows, but are not required now.

### 1) Basic btree indexes

Add when API endpoints are in use and we want faster filters/joins. Safe to apply online.

```sql
-- Well by ID (GET /v1/wells/{id})
CREATE INDEX IF NOT EXISTS ix_welldata_wrtn
  ON ground_truth."WellData" ("WellReportTrackingNumber");

-- County filter (GET /v1/search?county=...)
CREATE INDEX IF NOT EXISTS ix_welldata_county
  ON ground_truth."WellData" ("County");

-- Depth aggregation join (improves app.wells join to WellBoreHole)
CREATE INDEX IF NOT EXISTS ix_wellborehole_wrtn
  ON ground_truth."WellBoreHole" ("WellReportTrackingNumber");
```

### 2) Owner name search (optional)

Enable fast ILIKE/contains search on owner names if the product needs it.

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS ix_welldata_owner_trgm
  ON ground_truth."WellData" USING GIN (lower("OwnerName") gin_trgm_ops);
```

### 3) Date range filtering (defer)

Best approach is to materialize a typed `date_completed` field and index it.

```sql
-- Example (post‑M1): materialized view with typed columns for speed
CREATE MATERIALIZED VIEW IF NOT EXISTS app.wells_mat AS
SELECT * FROM app.wells;  -- replace with explicit typed select

-- Then index the date column
-- CREATE INDEX IF NOT EXISTS ix_wells_mat_date ON app.wells_mat (date_completed);

-- Refresh plan (manual or scheduled)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY app.wells_mat;
```

Alternative (not preferred): expression index that parses text dates in `WellData`. This can be brittle; skip unless necessary.

### 4) Spatial radius search (post‑geom)

When we add geometry, use PostGIS and a GIST index for fast radius/bbox queries.

```sql
-- Enable PostGIS once per database
CREATE EXTENSION IF NOT EXISTS postgis;

-- Example materialized view for geometry (build from app.wells where lat/lon present)
-- CREATE MATERIALIZED VIEW app.wells_geom AS
-- SELECT id, owner, county, lat, lon,
--        ST_SetSRID(ST_MakePoint(lon, lat), 4326) AS geom
-- FROM app.wells
-- WHERE lat IS NOT NULL AND lon IS NOT NULL;

-- Spatial index
-- CREATE INDEX IF NOT EXISTS ix_wells_geom_gist
--   ON app.wells_geom USING GIST (geom);

-- Refresh plan
-- REFRESH MATERIALIZED VIEW CONCURRENTLY app.wells_geom;
```

Notes
- You cannot add a normal index to a plain VIEW; use base‑table indexes (above) or materialize a view, then index it.
- Apply these in dev first; verify query plans are using the indexes (EXPLAIN ANALYZE), then promote.


### 5) UI polish and accessibility (defer)

- **Sorted headers (accessibility)**: Reflect sort state with `aria-sort` on the active `th` and ensure headers are keyboard-activable.
- **Row focus and activation**: Rows should have a visible focus style (`:focus`) and Enter/Space should activate selection (in addition to click).
- **Live regions**: Keep `#status` as `aria-live="polite"`; ensure the error banner uses `role="alert"` when shown.

### 6) Empty and error states (audit)

- **Copy and visibility**: Standardize messages for loading, empty (no results), and error with clear actions (retry/adjust filters).
- **Network resilience**: Show error state on timeouts/network failures and recover on retry.

### 7) Responsive/mobile QA (sub‑900px)

- **Layout**: Verify map height, results scroll, and no horizontal scrolling inside the table.
- **Tap targets**: Ensure interactive controls meet minimum touch sizes and spacing.
- **Safari/iOS**: Quick sanity pass for input styling and sticky header behavior.

### 8) Filter persistence (URL sync)

- **Sync to URL**: Reflect current filters/sort/page to query params.
- **Restore on load**: Read from URL on initial load so refresh/back/forward preserves state.

### 9) Visual consistency

- **Theme hover tones**: Confirm header hover/active tones look correct in light/dark.
- **Inputs/selects**: Ensure text colors and borders are consistent across themes.
- **Row interactions**: Finalize hover and active styles; selected marker style on the map matches the table selection.

### 10) Performance and UX

- **Debounce**: Debounce filter applies (e.g., 250–300 ms) to avoid excess fetches.
- **Cancel in‑flight requests**: Use `AbortController` to cancel prior fetch when starting a new one.
- **Page size**: Keep DOM light; paginate results and avoid creating unnecessary map markers.

### 11) CSV export v2 (columns and metadata)

- Add columns pending mapping from SDR:
  - Identification: `well_status`
  - Location details: `address`, `city`, `zip`
  - Specs: `total_depth_ft`, `borehole_diameter_in`, `casing_depth_ft`, `screened_interval_ft`
  - Water: `static_water_level_ft`, `yield_gpm`
  - Use/type: `well_use`, `pump_type`
  - Driller: `driller_name`, `driller_license`
  - Aquifer: `aquifer_name`
  - Links: `source_record_url` (if determinable)
- Include `location_confidence` (near‑term add) to current CSV.
- Add CSV header comment or a small README describing field definitions and caveats.
- Consider server‑side pagination/streaming for very large exports (>10k rows).

### 12) PDF export polish (post‑M5)

- **Branding/logo**: Add a small logo in the PDF header (configurable via env or file path).
- **Bundled map pin**: Ship a local `marker-icon.png` under `api/assets/` and reference it for static map pins (avoid relying on `apps/web/node_modules`).
- **HTTP method**: Switch `GET /v1/reports?format=pdf` to `POST /v1/reports` with JSON body for filters, aligning with the spec and avoiding very long URLs.
- **Storage**: Optionally upload PDFs to R2 and return a short‑lived signed URL; keep streaming for small reports.
- **Typography/spacing**: Final pass on fonts, spacing, and section balance; confirm OSM attribution.

### 13) Batch export v2 (post‑M6)

- **Master CSV**: Include one CSV in the ZIP summarizing each input row → resolved lat/lon (if geocoded), number of wells included, and the corresponding PDF filename.
- **Invalid rows report**: Emit a small CSV of invalid/failed rows (bad coordinates, no geocode hit, etc.).
- **UI upload**: Add a simple upload form in the web app with drag‑and‑drop, template CSV, progress indicator, and clear error messages.
- **Storage**: Upload ZIP to R2 and return a signed URL (TTL), in addition to streaming for small outputs.
- **Concurrency/backpressure**: Cap parallel geocoding and DB queries; add short sleeps or a token bucket to respect Nominatim rate limits.
- **Config**: Make geocoding on/off and provider configurable via env.
- **Resilience**: Add retries with jitter for network calls; timeouts and graceful fallbacks.

