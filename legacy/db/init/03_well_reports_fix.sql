-- Ensure well_reports has the expected columns used by ingest
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables WHERE table_name = 'well_reports'
  ) THEN
    CREATE TABLE well_reports (
      id TEXT PRIMARY KEY,
      owner_name TEXT,
      address TEXT,
      county TEXT,
      depth_ft INTEGER,
      date_completed DATE,
      location_error_m INTEGER,
      geom geometry(Point, 4326)
    );
  END IF;
END $$;

ALTER TABLE IF EXISTS well_reports
  ADD COLUMN IF NOT EXISTS owner_name TEXT,
  ADD COLUMN IF NOT EXISTS address TEXT,
  ADD COLUMN IF NOT EXISTS county TEXT,
  ADD COLUMN IF NOT EXISTS depth_ft INTEGER,
  ADD COLUMN IF NOT EXISTS date_completed DATE,
  ADD COLUMN IF NOT EXISTS location_error_m INTEGER,
  ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

CREATE INDEX IF NOT EXISTS idx_well_reports_geom ON well_reports USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_well_reports_owner_trgm ON well_reports USING GIN (owner_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_well_reports_address_trgm ON well_reports USING GIN (address gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_well_reports_county ON well_reports (county);


