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
- Data source: TWDB SDR official zip (no buckets needed)
  - `SDR_ZIP_URL=https://www.twdb.texas.gov/groundwater/data/SDRDownload.zip` (set as Environment Variable in GitHub for dev/staging/prod)
  - The ETL will download `WellData.txt` and `WellCompletion.txt` on each run into a temp folder under `data/raw_data/SDRDownload/SDRDownload` (these paths are git‑ignored; they are not committed).
- Implement/validate idempotent upserts using:
  - `data/sources/twdb_sdr.py: upsert_sdr_from_twdb_raw(raw_dir, db_url)` → writes to `well_reports`
  - `data/sources/twdb_gwdb.py` → writes to `gwdb_wells` (sample GWDB remains for now)
- Column mapping (SDR → well_reports):
  - `id`: TrackingNumber | TRK_NO | ReportTrackingNumber
  - `owner_name`: OwnerName | Owner
  - `address`: StreetAddress + City + Zip (when present)
  - `county`: County | CountyName
  - `depth_ft`: (WellCompletion.txt) TotalDepth | CompletionDepth | Depth
  - `date_completed`: (WellCompletion.txt) CompletionDate | CompletedDate | DateCompleted
  - `lat`/`lon`: use if present; otherwise leave geom NULL
- Geometry: EPSG:4326 via `ST_SetSRID(ST_MakePoint(lon,lat),4326)` when coordinates exist.
- Linking: ensure `data/transforms/link_sdr_gwdb.py` updates `well_links` within 50 m.
- Emit row counts and durations in logs.

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


