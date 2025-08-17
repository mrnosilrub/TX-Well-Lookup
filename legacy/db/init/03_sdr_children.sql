-- Sprint DS2 — Normalized Schema (child tables for SDR files)
-- Notes:
-- - Canonical key across SDR is TrackingNumber → modeled here as sdr_id (TEXT)
-- - Parent table is well_reports(id TEXT PRIMARY KEY) from 03_well_reports_fix.sql
-- - All child tables reference well_reports(id) ON DELETE CASCADE
-- - Index btree(sdr_id) added to each child for join/filter performance

-- =========================
-- Construction (Well*)
-- =========================

CREATE TABLE IF NOT EXISTS well_boreholes (
  sdr_id TEXT NOT NULL,
  borehole_no INTEGER NOT NULL,
  start_depth_ft NUMERIC(10,2),
  end_depth_ft NUMERIC(10,2),
  diameter_in NUMERIC(10,2),
  notes TEXT,
  PRIMARY KEY (sdr_id, borehole_no),
  CONSTRAINT fk_well_boreholes_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_boreholes_sdr ON well_boreholes (sdr_id);

CREATE TABLE IF NOT EXISTS well_casings (
  sdr_id TEXT NOT NULL,
  casing_no INTEGER NOT NULL,
  top_ft NUMERIC(10,2),
  bottom_ft NUMERIC(10,2),
  diameter_in NUMERIC(10,2),
  material TEXT,
  PRIMARY KEY (sdr_id, casing_no),
  CONSTRAINT fk_well_casings_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_casings_sdr ON well_casings (sdr_id);

CREATE TABLE IF NOT EXISTS well_filters (
  sdr_id TEXT NOT NULL,
  filter_no INTEGER NOT NULL,
  top_ft NUMERIC(10,2),
  bottom_ft NUMERIC(10,2),
  size TEXT,
  material TEXT,
  PRIMARY KEY (sdr_id, filter_no),
  CONSTRAINT fk_well_filters_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_filters_sdr ON well_filters (sdr_id);

CREATE TABLE IF NOT EXISTS well_seal_ranges (
  sdr_id TEXT NOT NULL,
  seal_no INTEGER NOT NULL,
  annular_seal TEXT,
  top_ft NUMERIC(10,2),
  bottom_ft NUMERIC(10,2),
  material TEXT,
  PRIMARY KEY (sdr_id, seal_no),
  CONSTRAINT fk_well_seal_ranges_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_seal_ranges_sdr ON well_seal_ranges (sdr_id);

CREATE TABLE IF NOT EXISTS well_packers (
  sdr_id TEXT NOT NULL,
  packer_no INTEGER NOT NULL,
  top_ft NUMERIC(10,2),
  bottom_ft NUMERIC(10,2),
  details TEXT,
  PRIMARY KEY (sdr_id, packer_no),
  CONSTRAINT fk_well_packers_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_packers_sdr ON well_packers (sdr_id);

-- Some SDRs include PlugBack details at the well level
CREATE TABLE IF NOT EXISTS well_plug_back (
  sdr_id TEXT NOT NULL,
  seq_no INTEGER NOT NULL,
  top_ft NUMERIC(10,2),
  bottom_ft NUMERIC(10,2),
  material TEXT,
  notes TEXT,
  PRIMARY KEY (sdr_id, seq_no),
  CONSTRAINT fk_well_plug_back_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_plug_back_sdr ON well_plug_back (sdr_id);

-- =========================
-- Geology / Hydro (Well*)
-- =========================

CREATE TABLE IF NOT EXISTS well_strata (
  sdr_id TEXT NOT NULL,
  seq_no INTEGER NOT NULL,
  migrated_strata_depth NUMERIC(10,2),
  water_type TEXT,
  notes TEXT,
  PRIMARY KEY (sdr_id, seq_no),
  CONSTRAINT fk_well_strata_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_strata_sdr ON well_strata (sdr_id);

CREATE TABLE IF NOT EXISTS well_levels (
  sdr_id TEXT NOT NULL,
  seq_no INTEGER NOT NULL,
  measurement_date DATE,
  water_level_ft NUMERIC(10,2),
  notes TEXT,
  PRIMARY KEY (sdr_id, seq_no),
  CONSTRAINT fk_well_levels_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_levels_sdr ON well_levels (sdr_id);

CREATE TABLE IF NOT EXISTS well_test (
  sdr_id TEXT NOT NULL,
  seq_no INTEGER NOT NULL,
  yield NUMERIC(12,3),
  hours NUMERIC(10,2),
  method TEXT,
  PRIMARY KEY (sdr_id, seq_no),
  CONSTRAINT fk_well_test_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_test_sdr ON well_test (sdr_id);

CREATE TABLE IF NOT EXISTS well_injurious_constituent (
  sdr_id TEXT NOT NULL,
  seq_no INTEGER NOT NULL,
  constituent TEXT,
  concentration NUMERIC(12,4),
  unit TEXT,
  PRIMARY KEY (sdr_id, seq_no),
  CONSTRAINT fk_well_injurious_constituent_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_injurious_constituent_sdr ON well_injurious_constituent (sdr_id);

CREATE TABLE IF NOT EXISTS well_lithology (
  sdr_id TEXT NOT NULL,
  seq_no INTEGER NOT NULL,
  depth_ft NUMERIC(10,2),
  lithology_description TEXT,
  water_type TEXT,
  PRIMARY KEY (sdr_id, seq_no),
  CONSTRAINT fk_well_lithology_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_well_lithology_sdr ON well_lithology (sdr_id);

-- =========================
-- Plugging (Plug*)
-- =========================

CREATE TABLE IF NOT EXISTS plug_reports (
  sdr_id TEXT NOT NULL PRIMARY KEY,
  date_submitted DATE,
  original_drill_date DATE,
  plugging_date DATE,
  comments TEXT,
  original_license_number TEXT,
  CONSTRAINT fk_plug_reports_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plug_boreholes (
  sdr_id TEXT NOT NULL,
  borehole_no INTEGER NOT NULL,
  start_depth_ft NUMERIC(10,2),
  end_depth_ft NUMERIC(10,2),
  diameter_in NUMERIC(10,2),
  notes TEXT,
  PRIMARY KEY (sdr_id, borehole_no),
  CONSTRAINT fk_plug_boreholes_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_plug_boreholes_sdr ON plug_boreholes (sdr_id);

CREATE TABLE IF NOT EXISTS plug_casing (
  sdr_id TEXT NOT NULL,
  casing_no INTEGER NOT NULL,
  top_ft NUMERIC(10,2),
  bottom_ft NUMERIC(10,2),
  diameter_in NUMERIC(10,2),
  material TEXT,
  PRIMARY KEY (sdr_id, casing_no),
  CONSTRAINT fk_plug_casing_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_plug_casing_sdr ON plug_casing (sdr_id);

CREATE TABLE IF NOT EXISTS plug_range (
  sdr_id TEXT NOT NULL,
  range_no INTEGER NOT NULL,
  plug_seal TEXT,
  top_ft NUMERIC(10,2),
  bottom_ft NUMERIC(10,2),
  material TEXT,
  PRIMARY KEY (sdr_id, range_no),
  CONSTRAINT fk_plug_range_report FOREIGN KEY (sdr_id)
    REFERENCES well_reports(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_plug_range_sdr ON plug_range (sdr_id);


