# Data Pipeline — Scaffold 

This directory will house the data ingestion and transformation code used to power TX Well Lookup. For Sprint 2, this is a minimal scaffold with no runtime coupling to the app. Future sprints will add real ETL for SDR, GWDB, and RRC sources.

## Structure

- `fixtures/` — Small sample/stub datasets used during early development and tests.
- `sources/` — Extractors that download or read raw source files (to be added in later sprints).
- `transforms/` — Cleaning, normalization, and joins (later).
- `bundles/` — Report assembly and export utilities (later).
- `jobs/` — Orchestration scripts (later).

## Next Steps

1. Add initial stub fixtures (CSV/JSON) as needed by web/API stubs.
2. Draft ETL interfaces for SDR and GWDB loaders.
3. Keep this layer decoupled from runtime until DB/API are introduced (Sprint 3+).

## Current Fixtures

- `fixtures/wells_stub.json` — Canonical stub used by the web stub endpoint and the API stub to ensure consistent results across layers.

## Plans & Specs

- See `ETL_PLAN.md` for Sprint 5 ingest plan and expected schemas (SDR, GWDB, RRC).

