## Sprint P1 — Database (Managed Postgres + PostGIS)

### Goal
Provision managed Postgres 15+ with PostGIS and pg_trgm, apply schema, secure access.

### Outcomes
- Managed DB created with extensions enabled
- Schema and indexes from `db/init/` applied
- Network and backup policies in place

### You — Manual Tasks
- Provision DB (Neon/CrunchyBridge/RDS). Create database `txwl`.
- Create app user with least-privilege (no superuser).
- Restrict network: only API egress IPs/VPC can connect; force TLS.
- Enable automated backups and PITR (7–30 days retention).

### Agent D — DevOps Tasks
- Apply SQL in order (psql or platform SQL runner):
  1. `db/init/01_postgis.sql`
  2. `db/init/02_gwdb.sql` or `db/init/02_gwdb_links.sql`
  3. `db/init/03_well_reports_fix.sql`
- Verify extensions:
  - `SELECT postgis_full_version();`
  - `CREATE EXTENSION IF NOT EXISTS pg_trgm;`
- Verify tables/indexes exist:
  - GiST on `well_reports(geom)` and `gwdb_wells(geom)`
  - GIN trigram on `owner_name`, `address`
- Document connection string `DATABASE_URL` (TLS), store in secrets.

### Acceptance
- Queries succeed; `well_reports`, `gwdb_wells`, `well_links` present with indexes.
- DB is not publicly accessible.

### Verification
```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM pg_extension WHERE extname IN ('postgis','pg_trgm');"
psql "$DATABASE_URL" -c "\d+ well_reports"
psql "$DATABASE_URL" -c "SELECT * FROM well_reports LIMIT 1;" # after P4
```


