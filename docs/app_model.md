## App Model — Initial Read-Only View

This document captures the minimal fields exposed by `app.wells` and how they map from SDR `ground_truth` and GWDB `gwdb_ground_truth` tables.

Views: `app.wells_sdr`, `app.wells_gwdb`, union view `app.wells`

- app.wells_sdr
  - id: `ground_truth."WellData"."WellReportTrackingNumber"`
  - owner: `ground_truth."WellData"."OwnerName"` (NULL if empty)
  - county: `ground_truth."WellData"."County"` (NULL if empty)
  - lat: parsed numeric from `ground_truth."WellData"."CoordDDLat"` in TX bounds (25..37)
  - lon: parsed numeric from `ground_truth."WellData"."CoordDDLong"` in TX bounds (-107..-93)
  - depth_ft: max numeric `ground_truth."WellBoreHole"."BottomDepth"` grouped by `"WellReportTrackingNumber"`
  - date_completed: best-effort date from `ground_truth."WellData"."DrillingEndDate"` then `"DrillingStartDate"`
  - location_confidence: simple heuristic — 'high' when both lat/lon valid and in bounds; 'medium' when one is present; else 'low'
  - source/source_id: `'sdr'`, `"WellReportTrackingNumber"`

- app.wells_gwdb
  - id: `gwdb_ground_truth."WellMain"."StateWellNumber"`
  - owner: `gwdb_ground_truth."WellMain"."Owner"` (NULL if empty)
  - county: `gwdb_ground_truth."WellMain"."County"` (NULL if empty)
  - lat: parsed numeric from `gwdb_ground_truth."WellMain"."LatitudeDD"` in TX bounds (25..37)
  - lon: parsed numeric from `gwdb_ground_truth."WellMain"."LongitudeDD"` in TX bounds (-107..-93)
  - depth_ft: `gwdb_ground_truth."WellMain"."WellDepth"` if numeric, else max numeric `gwdb_ground_truth."WellBoreHole"."BottomDepth"` grouped by `"StateWellNumber"`
  - date_completed: best-effort date from `gwdb_ground_truth."WellMain"."DrillingEndDate"` then `"DrillingStartDate"`
  - location_confidence: same heuristic as SDR
  - source/source_id: `'gwdb'`, `"StateWellNumber"`

- app.wells
  - UNION ALL of the two views with identical column order

Notes:
- All raw columns are TEXT; parsing is done on the fly within the views.
- Coordinates outside broad TX bounds are treated as NULL to avoid bogus pins.
- This is a read-only projection; the raw SDR/GWDB data remains unmodified.


