-- Quick verification queries for app.wells
\pset pager off

SELECT 'app schema exists' AS check, EXISTS (
  SELECT 1 FROM information_schema.schemata WHERE schema_name = 'app'
) AS ok;

SELECT 'app.wells view exists' AS check, EXISTS (
  SELECT 1 FROM information_schema.views WHERE table_schema='app' AND table_name='wells'
) AS ok;

-- Sample rows
SELECT * FROM app.wells LIMIT 10;


