-- Sprint 8 performance indexes

-- rrc_permits spatial index (table expected from data pipeline sprint)
DO $$ BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables WHERE table_name = 'rrc_permits'
  ) THEN
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_rrc_permits_geom ON rrc_permits USING GIST (geom)';
  END IF;
END $$;

-- well_reports multi-column index for common filters
CREATE INDEX IF NOT EXISTS idx_well_reports_county_date
  ON well_reports (county, date_completed);


