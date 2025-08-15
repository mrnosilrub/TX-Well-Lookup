CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Minimal tables for Sprint 6
CREATE TABLE IF NOT EXISTS well_reports (
  id TEXT PRIMARY KEY,
  name TEXT,
  county TEXT,
  depth_ft INTEGER,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  geom GEOGRAPHY(POINT, 4326)
);

CREATE INDEX IF NOT EXISTS idx_well_reports_geom ON well_reports USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_well_reports_county ON well_reports (county);
CREATE INDEX IF NOT EXISTS idx_well_reports_name_trgm ON well_reports USING GIN (name gin_trgm_ops);

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Wells table (minimal for Sprint 6)
CREATE TABLE IF NOT EXISTS well_reports (
  id TEXT PRIMARY KEY,
  owner_name TEXT,
  address TEXT,
  county TEXT,
  depth_ft INTEGER,
  date_completed DATE,
  location_error_m INTEGER,
  geom geometry(Point, 4326)
);

-- Plugging reports (placeholder)
CREATE TABLE IF NOT EXISTS plugging_reports (
  id TEXT PRIMARY KEY,
  well_id TEXT,
  plug_date DATE,
  notes TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_well_reports_geom ON well_reports USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_well_reports_owner_trgm ON well_reports USING GIN (owner_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_well_reports_address_trgm ON well_reports USING GIN (address gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_well_reports_county ON well_reports (county);


