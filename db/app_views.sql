-- App schema and minimal product view for wells (read-only)

CREATE SCHEMA IF NOT EXISTS app;

CREATE OR REPLACE VIEW app.wells AS
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
  END AS location_confidence
FROM ground_truth."WellData" wd
LEFT JOIN (
  SELECT
    "WellReportTrackingNumber" AS wrtn,
    MAX(CASE WHEN "BottomDepth" ~ '^\d+(\.\d+)?$' THEN "BottomDepth"::double precision END) AS max_bottom_depth
  FROM ground_truth."WellBoreHole"
  GROUP BY "WellReportTrackingNumber"
) bb
  ON bb.wrtn = wd."WellReportTrackingNumber";


