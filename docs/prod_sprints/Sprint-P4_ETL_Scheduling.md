## Sprint P4 — ETL Scheduling (SDR + GWDB + Linking)

### Goal
Nightly ingest of SDR and GWDB, followed by spatial linking, with idempotence and monitoring.

### Outcomes
- Scheduled job runs nightly, updates tables, and logs row counts
- Failures alert; linking within 50 m produces entries in `well_links`

### You — Manual Tasks
- Choose a scheduler: GitHub Actions cron (preferred) or Render cron.
- Add `DATABASE_URL` secret from Neon (env-specific) to the scheduler environment.

### Agent B — Data Pipeline Tasks
- Validate idempotent upserts:
  - `data/sources/twdb_sdr.py` → `well_reports`
  - `data/sources/twdb_gwdb.py` → `gwdb_wells`
- Confirm geometries are EPSG:4326 and use `ST_SetSRID(ST_MakePoint(lon,lat),4326)`.
- Ensure `data/transforms/link_sdr_gwdb.py` updates `well_links` with 50 m radius.
- Emit row counts and durations.

### Agent D — DevOps Tasks
- Add a workflow to run `data/jobs/nightly_snapshots.py` with `DATABASE_URL`.
- Route logs to platform; alert on non-zero exit or anomaly in row deltas.

### Acceptance
- Nightly run succeeds; tables updated; `well_links` non-empty where expected.

### Verification
```bash
# GitHub → Actions → ETL Nightly (P4) → Run workflow → env: dev (repeat for staging/prod)
# The job runs data/jobs/nightly_snapshots.py and prints row counts.
# To manually verify:
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM well_reports;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM gwdb_wells;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM well_links;"
```


