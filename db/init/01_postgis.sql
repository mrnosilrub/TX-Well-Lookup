CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Core tables
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

CREATE TABLE IF NOT EXISTS plugging_reports (
  id TEXT PRIMARY KEY,
  well_id TEXT,
  plug_date DATE,
  notes TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_well_reports_geom ON well_reports USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_well_reports_county ON well_reports (county);


