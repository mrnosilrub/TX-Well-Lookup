-- GWDB wells table
CREATE TABLE IF NOT EXISTS gwdb_wells (
  id TEXT PRIMARY KEY,
  county TEXT,
  total_depth_ft INTEGER,
  aquifer TEXT,
  geom geometry(Point, 4326)
);

-- Links between SDR and GWDB wells
CREATE TABLE IF NOT EXISTS well_links (
  sdr_id TEXT NOT NULL,
  gwdb_id TEXT NOT NULL,
  match_score DOUBLE PRECISION NOT NULL,
  linked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (sdr_id, gwdb_id)
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_gwdb_wells_geom ON gwdb_wells USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_gwdb_wells_county ON gwdb_wells (county);


