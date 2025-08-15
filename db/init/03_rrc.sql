-- RRC permits and wellbores schema

CREATE TABLE IF NOT EXISTS rrc_permits (
  api14 TEXT PRIMARY KEY,
  operator TEXT,
  status TEXT,
  permit_date DATE,
  geom geometry(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_rrc_permits_geom ON rrc_permits USING GIST (geom);

CREATE TABLE IF NOT EXISTS rrc_wellbores (
  api14 TEXT NOT NULL,
  wellbore TEXT NOT NULL,
  geom geometry(Point, 4326),
  PRIMARY KEY (api14, wellbore)
);

CREATE INDEX IF NOT EXISTS idx_rrc_wellbores_geom ON rrc_wellbores USING GIST (geom);


