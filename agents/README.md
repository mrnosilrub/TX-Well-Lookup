# Agents — Continuity Guide

This folder documents automation tasks and conventions so any agent (human or AI) can quickly regain context.

## Environments & Secrets
- Neon Postgres: `DATABASE_URL` (dev/staging/prod environments in GitHub)
- SDR zip: `SDR_ZIP_URL` (or RAW_SDR_* with STORAGE_* for S3-compatible storage)

## Ground Truth (1:1 SDR)
- Loader workflow: `.github/workflows/ground-truth-load.yml`
  - Runs on push to `ground_truth/**` (defaults to dev) or manually for any env
- Schema doc workflow: `.github/workflows/ground-truth-schema.yml`
  - Builds `ground_truth/SCHEMA.md` from the live database
- Local tools:
  - `ground_truth/loader/load_ground_truth.py`
  - `ground_truth/tools/generate_schema_md.py`

## Common Ops
- Wipe database schemas (dev only):
```
BEGIN;
DROP SCHEMA IF EXISTS ground_truth CASCADE; -- if present
DROP SCHEMA IF EXISTS sdr_raw CASCADE;
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
CREATE SCHEMA sdr_raw; -- legacy staging, optional
CREATE SCHEMA ground_truth; -- loader will recreate as needed
COMMIT;
```
- Trigger load (dev): push a change under `ground_truth/**` or run the workflow manually
- Verify:
  - Neon console → check `ground_truth` tables & row counts
  - Or run schema doc workflow and open `ground_truth/SCHEMA.md`

## Conventions
- Do not transform in ground_truth; all columns are TEXT, exact header names recorded via column comments
- Non-tabular docs are ignored by the loader (ReadMe/Dictionary/etc.)
- Loader sanitizes inconsistent rows (pads/truncates to header width)

## Maintenance
- Keep this file current when workflows, secrets, or procedures change
- Capture noteworthy repo changes in `CHANGELOG.md` (top-level)
- Run the schema doc workflow manually after successful loads to update `ground_truth/SCHEMA.md`

## Next Steps (Design)
- Define minimal views on top of ground_truth for the website
- Plan normalized schemas separately under `legacy/` (reference only) and new design docs in `docs/`
