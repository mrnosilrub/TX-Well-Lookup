## App Model — Initial Read-Only View

This document captures the minimal fields exposed by `app.wells` and how they map from SDR `ground_truth` tables.

View: `app.wells`

- id: `WellData.WellReportTrackingNumber`
- owner: `WellData.OwnerName` (NULL if empty)
- county: `WellData.County` (NULL if empty)
- lat: parsed numeric from `WellData.CoordDDLat` in TX bounds (25..37)
- lon: parsed numeric from `WellData.CoordDDLong` in TX bounds (-107..-93)
- depth_ft: max numeric `BottomDepth` from `WellBoreHole` for the same `WellReportTrackingNumber`
- date_completed: best-effort date from `WellData.DrillingEndDate` then `DrillingStartDate` using common formats (Y-M-D, M/D/Y, Y/M/D)
- location_confidence: simple heuristic — 'high' when both lat/lon valid and in bounds; 'medium' when one is present but suspect; else 'low'

Notes:
- All `ground_truth` columns are TEXT; parsing is done on the fly within the view.
- Coordinates outside broad TX bounds are treated as NULL to avoid bogus pins.
- This is a read-only projection; the raw SDR data remains unmodified.


