## Sprint DS2 — Normalized Schema (DDL Plan)

### Goal
Design normalized tables and indexes for all SDR files using `sdr_id` (TrackingNumber) as the canonical key. No code changes yet; deliver a concrete DDL plan.

### Tables
- Core: `well_reports(sdr_id PK, owner_name, address, county, depth_ft, date_completed, geom, location_error_m, source_row_hash, ingested_at)`
- Construction details (m:1 per well):
  - `well_boreholes(sdr_id, borehole_no, start_depth_ft, end_depth_ft, diameter_in, notes, PRIMARY KEY(sdr_id,borehole_no))`
  - `well_casings(sdr_id, casing_no, top_ft, bottom_ft, diameter_in, material, PRIMARY KEY(sdr_id,casing_no))`
  - `well_filters(sdr_id, filter_no, top_ft, bottom_ft, size, material, PRIMARY KEY(sdr_id,filter_no))`
  - `well_seal_ranges(sdr_id, seal_no, annular_seal, top_ft, bottom_ft, material, PRIMARY KEY(sdr_id,seal_no))`
  - `well_packers(sdr_id, packer_no, top_ft, bottom_ft, details, PRIMARY KEY(sdr_id,packer_no))`
- Geology / hydro:
  - `well_strata(sdr_id, seq_no, migrated_strata_depth, water_type, notes, PRIMARY KEY(sdr_id,seq_no))`
  - `well_levels(sdr_id, seq_no, measurement_date, water_level_ft, notes, PRIMARY KEY(sdr_id,seq_no))`
  - `well_test(sdr_id, seq_no, yield, hours, method, PRIMARY KEY(sdr_id,seq_no))`
  - `well_injurious_constituent(sdr_id, seq_no, constituent, concentration, unit, PRIMARY KEY(sdr_id,seq_no))`
- Lithology (large):
  - `well_lithology(sdr_id, seq_no, depth_ft, lithology_description, water_type, PRIMARY KEY(sdr_id,seq_no))`
- Plugging:
  - `plug_reports(sdr_id PK, date_submitted, original_drill_date, plugging_date, comments, original_license_number)`
  - `plug_boreholes(sdr_id, borehole_no, start_depth_ft, end_depth_ft, diameter_in, notes, PRIMARY KEY(sdr_id,borehole_no))`
  - `plug_casing(sdr_id, casing_no, top_ft, bottom_ft, diameter_in, material, PRIMARY KEY(sdr_id,casing_no))`
  - `plug_range(sdr_id, range_no, plug_seal, top_ft, bottom_ft, material, PRIMARY KEY(sdr_id,range_no))`

### Constraints & Indexes
- FKs: All child tables `REFERENCES well_reports(sdr_id)` ON DELETE CASCADE
- Indexes:
  - `well_reports`: GIST(geom); btree(county); btree(date_completed); pg_trgm(owner_name, address)
  - Each child table: btree(sdr_id)
  - `well_lithology`: btree(sdr_id); consider partitioning later

### Types
- Dates: DATE (Y-M-D)
- Depths/levels: NUMERIC or INTEGER (as appropriate per dictionary)
- Text: TEXT
- Geometry: `geometry(Point,4326)`

### Deliverables
- New file `db/init/03_sdr_children.sql` implementing the above DDL.
- Update `db-apply.yml` to include `03_sdr_children.sql`.


