## Sprint DS5 — QA, Validation, and Metrics

### Goal
Verify completeness and correctness after ingest. Establish coverage metrics and quick checks.

### Coverage metrics
- `well_reports`: total, with_geom, with_depth
- Cardinalities per child table
- Counties distribution (top 10)
- Raw vs normalized coverage: top N `sdr_raw.*` counts and matching normalized counts

### Sanity checks
- TX bounds for geom: `lat 25–37`, `lon -107 to -93`
- Date completeness for `date_completed`
- Spot joins: `well + casing/filter/seal/tests`
- Foreign keys: all child `sdr_id` exist in `well_reports`
- Type coercion: numeric/date NULLs as expected (no empty-string insert errors)

### Queries (examples)
- `SELECT COUNT(*) AS total, COUNT(geom) AS with_geom, COUNT(depth_ft) AS with_depth FROM well_reports;`
- `SELECT 'boreholes' n, COUNT(*) FROM well_boreholes UNION ALL SELECT 'casings', COUNT(*) FROM well_casings ...;`
- `SELECT county, COUNT(*) c FROM well_reports GROUP BY county ORDER BY c DESC LIMIT 10;`
- Out-of-bounds: `SELECT id, ST_Y(geom) lat, ST_X(geom) lon FROM well_reports WHERE NOT (ST_Y(geom) BETWEEN 25 AND 37 AND ST_X(geom) BETWEEN -107 AND -93) LIMIT 50;`

### Reporting
- Print metrics in ETL logs and as a CI step summary
- Optionally write a `etl_metrics.json` to R2 per run

### Acceptance
- Metrics available post-run; no gross anomalies (e.g., 0 rows) in core tables


