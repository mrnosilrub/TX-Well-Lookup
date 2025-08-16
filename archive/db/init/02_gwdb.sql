-- GWDB wells table used in Sprint 7 linking
CREATE TABLE IF NOT EXISTS gwdb_wells (
  id TEXT PRIMARY KEY,
  county TEXT,
  total_depth_ft INTEGER,
  aquifer TEXT,
  geom geometry(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_gwdb_wells_geom ON gwdb_wells USING GIST (geom);

-- Link table between SDR and GWDB
CREATE TABLE IF NOT EXISTS well_links (
  sdr_id TEXT,
  gwdb_id TEXT,
  match_score DOUBLE PRECISION,
  PRIMARY KEY (sdr_id, gwdb_id)
);


