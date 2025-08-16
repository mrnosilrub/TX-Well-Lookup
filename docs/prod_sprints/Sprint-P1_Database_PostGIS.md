## Sprint P1 — Database (Managed Postgres + PostGIS)

### Goal
Provision managed Postgres 15+ with PostGIS and pg_trgm, apply schema, secure access.

### Outcomes
- Managed DB created with extensions enabled
- Schema and indexes from `db/init/` applied
- Network and backup policies in place

### You — Manual Tasks
- Provision DB on Neon (per providers.md). Create database `txwl` (branches: dev/staging/prod).
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
- Document Neon connection string `DATABASE_URL` (TLS), store in env-scoped secrets (dev/staging/prod).

### Acceptance
- Queries succeed; `well_reports`, `gwdb_wells`, `well_links` present with indexes.
- DB is not publicly accessible.

### Verification
```bash
# GitHub → Actions → DB Apply & Verify (P1) → Run workflow → env: dev (or staging/prod)
# The job applies db/init/*.sql and prints extension/table/index checks.
```


