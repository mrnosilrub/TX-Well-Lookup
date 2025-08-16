## Sprint DS3 — ETL Mapping and Header Aliases

### Goal
Define exact field mappings from SDR `.txt` files to normalized tables with robust header aliasing and parsing rules.

### Canonical key
- `sdr_id` = SDR TrackingNumber (aliases: `TrackingNumber`, `TRK_NO`, `ReportTrackingNumber`, etc.)

### Parsing rules
- Encoding: latin-1 for SDR `.txt`
- Delimiter: `|`
- Trim whitespace on keys and values
- Date: Y-M-D (accept common variants), NULL if unparseable
- Numeric: coerce, NULL if invalid
- Geometry: only if lat/lon present and in TX bounds (lat 25–37, lon -107 to -93)

### Core mappings
- WellData.txt → well_reports (base)
  - id: `sdr_id`
  - owner_name: OwnerName | Owner
  - address: compose Street/City/Zip when present
  - county: County | CountyName
  - lat/lon: `CoordDDLat`/`CoordDDLong` | `Latitude`/`Longitude` variants

- WellCompletion.txt → well_reports (enrich)
  - depth_ft: TotalDepth | CompletionDepth | Depth
  - date_completed: CompletionDate | CompletedDate | DateCompleted

### Child mappings (examples)
- WellBoreHole.txt → well_boreholes
  - borehole_no (sequence or explicit), start_depth_ft, end_depth_ft, diameter_in, notes

- WellCasing.txt → well_casings
  - casing_no, top_ft, bottom_ft, diameter_in, material

- WellFilter.txt → well_filters
  - filter_no, top_ft, bottom_ft, size, material

- WellSealRange.txt → well_seal_ranges
  - seal_no, annular_seal, top_ft, bottom_ft, material

- WellLevels.txt → well_levels
  - seq_no, measurement_date, water_level_ft, notes

- WellTest.txt → well_test
  - seq_no, yield, hours, method

- WellInjuriousConstituent.txt → well_injurious_constituent
  - seq_no, constituent, concentration, unit

- WellLithology.txt → well_lithology
  - seq_no, depth_ft, lithology_description, water_type

- PlugData.txt → plug_reports
  - date_submitted, original_drill_date, plugging_date, comments, original_license_number

- PlugBoreHole.txt / PlugCasing.txt / PlugRange.txt → corresponding plug_* tables

### Header alias catalogue
- Maintain alias lists in code (normalized keys), sourced from: manifest headers + SDR Excel dictionary.
- For each target column, list accepted header variants.

### Deliverables
- A mapping table per source file (to be pasted into code).
- Confirmed alias lists extracted from manifest and dictionary.
- Artifacts produced by DS1 workflow:
  - `sdr_header_aliases.json` (manifest + dictionary headers per file)
  - `DS3_mapping.md` (human-readable mapping summary)
  - `sdr_raw_schema.sql` (raw 1:1 staging schema)


