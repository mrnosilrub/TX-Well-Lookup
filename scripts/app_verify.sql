-- Quick verification queries for app.wells
\pset pager off

SELECT 'app schema exists' AS check, EXISTS (
  SELECT 1 FROM information_schema.schemata WHERE schema_name = 'app'
) AS ok;

SELECT 'app.wells view exists' AS check, EXISTS (
  SELECT 1 FROM information_schema.views WHERE table_schema='app' AND table_name='wells'
) AS ok;

SELECT 'app.wells_sdr view exists' AS check, EXISTS (
  SELECT 1 FROM information_schema.views WHERE table_schema='app' AND table_name='wells_sdr'
) AS ok;

SELECT 'app.wells_gwdb view exists' AS check, EXISTS (
  SELECT 1 FROM information_schema.views WHERE table_schema='app' AND table_name='wells_gwdb'
) AS ok;

-- Sample rows
SELECT * FROM app.wells LIMIT 10;
SELECT * FROM app.wells_sdr LIMIT 5;
SELECT * FROM app.wells_gwdb LIMIT 5;


