-- Idempotent apply for app schema/views
BEGIN;
\i db/app_views.sql
COMMIT;


