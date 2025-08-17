## Database Schema and ETL Plan — SDR End-to-End

This folder contains bite-sized sprints (one per file) for an agent to execute, from safely inspecting the full SDR ZIP through to a complete, normalized schema and an idempotent ETL for production.

Start with Sprint DS1 and proceed in order:

- `Sprint-DS1_Snapshot_and_Inspect.md` — Download full SDR ZIP, stage in R2, and capture safe previews + manifest for design.
- `Sprint-DS2_Schema_DDL.md` — Finalize normalized tables and indexes for all SDR files (no code, DDL plan only).
- `Sprint-DS3_ETL_Mapping_and_Aliases.md` — Define field mappings and header alias sets (based on manifest and the SDR Excel dictionary).
- `Sprint-DS4_ETL_Orchestration_and_Logging.md` — Orchestrate end-to-end SDR ingest with per-file counts and durations.
- `Sprint-DS5_QA_Validation_and_Metrics.md` — Data quality checks, coverage metrics, and job summaries.
- `Sprint-DS6_Prod_Rollout_and_Runbooks.md` — Production rollout, verification, and rollback.

Notes:
- Large SDR data are never committed to the repo. Snapshots and previews are uploaded to an existing R2 bucket and attached as CI artifacts.
- Use the SDR Excel column dictionary from the official ZIP to confirm field names and types.


