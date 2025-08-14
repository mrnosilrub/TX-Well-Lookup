-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Minimal tables (expand with proper types/constraints later)
CREATE TABLE IF NOT EXISTS well_reports (
  id TEXT PRIMARY KEY,
  owner_name TEXT,
  address TEXT,
  county TEXT,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  geom GEOMETRY(Point, 4326),
  date_completed DATE,
  proposed_use TEXT,
  well_type TEXT,
  borehole_depth_ft NUMERIC,
  driller_name TEXT,
  plugging_report_id TEXT,
  location_error_m NUMERIC,
  source_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS well_reports_geom_idx ON well_reports USING GIST (geom);
CREATE INDEX IF NOT EXISTS well_reports_owner_trgm ON well_reports USING GIN (owner_name gin_trgm_ops);

CREATE TABLE IF NOT EXISTS plugging_reports (
  id TEXT PRIMARY KEY,
  county TEXT,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  geom GEOMETRY(Point, 4326),
  date_plugged DATE,
  notes TEXT,
  source_url TEXT
);
CREATE INDEX IF NOT EXISTS plugging_reports_geom_idx ON plugging_reports USING GIST (geom);

CREATE TABLE IF NOT EXISTS gwdb_wells (
  id TEXT PRIMARY KEY,
  owner_name TEXT,
  aquifer TEXT,
  well_depth_ft NUMERIC,
  has_water_level BOOLEAN,
  has_water_quality BOOLEAN,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  geom GEOMETRY(Point, 4326),
  source_url TEXT
);
CREATE INDEX IF NOT EXISTS gwdb_wells_geom_idx ON gwdb_wells USING GIST (geom);

CREATE TABLE IF NOT EXISTS rrc_permits (
  api14 TEXT PRIMARY KEY,
  operator TEXT,
  status TEXT,
  permit_date DATE,
  county TEXT,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  geom GEOMETRY(Point, 4326),
  source_ref TEXT
);
CREATE INDEX IF NOT EXISTS rrc_permits_geom_idx ON rrc_permits USING GIST (geom);

CREATE TABLE IF NOT EXISTS rrc_wellbores (
  api14 TEXT,
  wb_id TEXT,
  status TEXT,
  spud_date DATE,
  PRIMARY KEY (api14, wb_id)
);

CREATE TABLE IF NOT EXISTS well_links (
  sdr_id TEXT,
  gwdb_id TEXT,
  match_score NUMERIC,
  PRIMARY KEY (sdr_id, gwdb_id)
);

-- Users / billing (skeleton)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  plan TEXT,
  seat_org_id UUID,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS credit_grants (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  amount INTEGER,
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS credit_spends (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  amount INTEGER,
  object_type TEXT,
  object_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  address TEXT,
  center GEOMETRY(Point, 4326),
  radius_m INT,
  pdf_url TEXT,
  zip_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alerts (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  center GEOMETRY(Point, 4326),
  radius_m INT,
  created_at TIMESTAMPTZ DEFAULT now()
);