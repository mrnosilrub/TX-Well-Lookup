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


