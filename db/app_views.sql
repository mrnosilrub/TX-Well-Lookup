-- App schema and minimal product views for wells (read-only)

CREATE SCHEMA IF NOT EXISTS app;

-- SDR view
CREATE OR REPLACE VIEW app.wells_sdr AS
SELECT
  wd."WellReportTrackingNumber" AS id,
  NULLIF(wd."OwnerName", '') AS owner,
  NULLIF(wd."County", '') AS county,
  CASE
    WHEN wd."CoordDDLat" ~ '^[-]?\d+(\.\d+)?$' AND wd."CoordDDLat"::double precision BETWEEN 25 AND 37
      THEN wd."CoordDDLat"::double precision
    ELSE NULL
  END AS lat,
  CASE
    WHEN wd."CoordDDLong" ~ '^[-]?\d+(\.\d+)?$' AND wd."CoordDDLong"::double precision BETWEEN -107 AND -93
      THEN wd."CoordDDLong"::double precision
    ELSE NULL
  END AS lon,
  bb.max_bottom_depth::double precision AS depth_ft,
  COALESCE(
    CASE
      WHEN wd."DrillingEndDate" ~ '^\d{4}-\d{2}-\d{2}$' THEN wd."DrillingEndDate"::date
      WHEN wd."DrillingEndDate" ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(wd."DrillingEndDate", 'MM/DD/YYYY')
      WHEN wd."DrillingEndDate" ~ '^\d{4}/\d{2}/\d{2}$' THEN to_date(wd."DrillingEndDate", 'YYYY/MM/DD')
    END,
    CASE
      WHEN wd."DrillingStartDate" ~ '^\d{4}-\d{2}-\d{2}$' THEN wd."DrillingStartDate"::date
      WHEN wd."DrillingStartDate" ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(wd."DrillingStartDate", 'MM/DD/YYYY')
      WHEN wd."DrillingStartDate" ~ '^\d{4}/\d{2}/\d{2}$' THEN to_date(wd."DrillingStartDate", 'YYYY/MM/DD')
    END
  ) AS date_completed,
  CASE
    WHEN (wd."CoordDDLat" ~ '^[-]?\d+(\.\d+)?$' AND wd."CoordDDLat"::double precision BETWEEN 25 AND 37)
       AND (wd."CoordDDLong" ~ '^[-]?\d+(\.\d+)?$' AND wd."CoordDDLong"::double precision BETWEEN -107 AND -93)
      THEN 'high'
    WHEN (wd."CoordDDLat" ~ '^[-]?\d+(\.\d+)?$' OR wd."CoordDDLong" ~ '^[-]?\d+(\.\d+)?$')
      THEN 'medium'
    ELSE 'low'
  END AS location_confidence,
  'sdr'::text AS source,
  wd."WellReportTrackingNumber" AS source_id
FROM ground_truth."WellData" wd
LEFT JOIN (
  SELECT
    "WellReportTrackingNumber" AS wrtn,
    MAX(CASE WHEN "BottomDepth" ~ '^\d+(\.\d+)?$' THEN "BottomDepth"::double precision END) AS max_bottom_depth
  FROM ground_truth."WellBoreHole"
  GROUP BY "WellReportTrackingNumber"
) bb
  ON bb.wrtn = wd."WellReportTrackingNumber";

-- GWDB view
CREATE OR REPLACE VIEW app.wells_gwdb AS
SELECT
  wm."StateWellNumber" AS id,
  NULLIF(wm."Owner", '') AS owner,
  NULLIF(wm."County", '') AS county,
  CASE
    WHEN wm."LatitudeDD" ~ '^[-]?\d+(\.\d+)?$' AND wm."LatitudeDD"::double precision BETWEEN 25 AND 37
      THEN wm."LatitudeDD"::double precision
    ELSE NULL
  END AS lat,
  CASE
    WHEN wm."LongitudeDD" ~ '^[-]?\d+(\.\d+)?$' AND wm."LongitudeDD"::double precision BETWEEN -107 AND -93
      THEN wm."LongitudeDD"::double precision
    ELSE NULL
  END AS lon,
  COALESCE(
    CASE WHEN wm."WellDepth" ~ '^\d+(\.\d+)?$' THEN wm."WellDepth"::double precision END,
    bb.max_bottom_depth
  ) AS depth_ft,
  COALESCE(
    CASE
      WHEN wm."DrillingEndDate" ~ '^\d{4}-\d{2}-\d{2}$' THEN wm."DrillingEndDate"::date
      WHEN wm."DrillingEndDate" ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(wm."DrillingEndDate", 'MM/DD/YYYY')
      WHEN wm."DrillingEndDate" ~ '^\d{4}/\d{2}/\d{2}$' THEN to_date(wm."DrillingEndDate", 'YYYY/MM/DD')
    END,
    CASE
      WHEN wm."DrillingStartDate" ~ '^\d{4}-\d{2}-\d{2}$' THEN wm."DrillingStartDate"::date
      WHEN wm."DrillingStartDate" ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(wm."DrillingStartDate", 'MM/DD/YYYY')
      WHEN wm."DrillingStartDate" ~ '^\d{4}/\d{2}/\d{2}$' THEN to_date(wm."DrillingStartDate", 'YYYY/MM/DD')
    END
  ) AS date_completed,
  CASE
    WHEN (wm."LatitudeDD" ~ '^[-]?\d+(\.\d+)?$' AND wm."LatitudeDD"::double precision BETWEEN 25 AND 37)
       AND (wm."LongitudeDD" ~ '^[-]?\d+(\.\d+)?$' AND wm."LongitudeDD"::double precision BETWEEN -107 AND -93)
      THEN 'high'
    WHEN (wm."LatitudeDD" ~ '^[-]?\d+(\.\d+)?$' OR wm."LongitudeDD" ~ '^[-]?\d+(\.\d+)?$')
      THEN 'medium'
    ELSE 'low'
  END AS location_confidence,
  'gwdb'::text AS source,
  wm."StateWellNumber" AS source_id
FROM gwdb_ground_truth."WellMain" wm
LEFT JOIN (
  SELECT
    "StateWellNumber" AS swn,
    MAX(CASE WHEN "BottomDepth" ~ '^\d+(\.\d+)?$' THEN "BottomDepth"::double precision END) AS max_bottom_depth
  FROM gwdb_ground_truth."WellBoreHole"
  GROUP BY "StateWellNumber"
) bb
  ON bb.swn = wm."StateWellNumber";

-- Union view used by API when source=all
CREATE OR REPLACE VIEW app.wells AS
SELECT id, owner, county, lat, lon, depth_ft, date_completed, location_confidence, source, source_id FROM app.wells_sdr
UNION ALL
SELECT id, owner, county, lat, lon, depth_ft, date_completed, location_confidence, source, source_id FROM app.wells_gwdb;


