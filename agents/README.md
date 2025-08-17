# Agents — Continuity Guide

Note: This file is auto-generated. Do not edit manually. Update generators under `agents/tools/`.

This guide documents automation tasks and conventions so any agent (human or AI) can quickly regain context.
Generated at: 2025-08-17 01:20:15Z


## Environments & Secrets
- Secrets referenced in workflows: DATABASE_URL, SDR_ZIP_URL, STORAGE_ACCESS_KEY_ID, STORAGE_ENDPOINT, STORAGE_SECRET_ACCESS_KEY
- Neon Postgres: `DATABASE_URL` (scoped per environment in GitHub)
- SDR zip: `SDR_ZIP_URL` (or RAW_SDR_* with STORAGE_* for S3-compatible storage)


## Ground Truth (1:1 SDR)
- Loader: `ground_truth/loader/load_ground_truth.py`
  - Workflow: `.github/workflows/ground-truth-load.yml` (push on `ground_truth/**`, or manual)
- Schema doc generator: `ground_truth/tools/generate_schema_md.py`
  - Workflow: `.github/workflows/ground-truth-schema.yml` (manual)


## Workflows

### Agents README Update
- **file**: `.github/workflows/agents-readme.yml`

### Ground Truth Load
- **file**: `.github/workflows/ground-truth-load.yml`
- **secrets referenced**: DATABASE_URL, SDR_ZIP_URL, STORAGE_ACCESS_KEY_ID, STORAGE_ENDPOINT, STORAGE_SECRET_ACCESS_KEY

### Ground Truth Schema Doc
- **file**: `.github/workflows/ground-truth-schema.yml`
- **secrets referenced**: DATABASE_URL


## Common Ops
- Wipe database schemas (dev only):
```sql
BEGIN;
DROP SCHEMA IF EXISTS ground_truth CASCADE; -- if present
DROP SCHEMA IF EXISTS sdr_raw CASCADE;
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
CREATE SCHEMA sdr_raw; -- legacy staging, optional
CREATE SCHEMA ground_truth; -- loader will recreate as needed
COMMIT;
```
- Verify ground truth: run the schema doc workflow (manual) and review `ground_truth/SCHEMA.md`



## Conventions
- Do not transform in ground_truth; columns are TEXT; original header names preserved via column comments
- Non-tabular docs are ignored by the loader (ReadMe/Dictionary/etc.)
- Loader sanitizes inconsistent rows (pads/truncates to header width)
