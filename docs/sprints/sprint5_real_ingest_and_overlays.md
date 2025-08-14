# Sprint 5 — Real Ingest & Overlays (Upgrade path)
**Outcome:** Replace stubs with real data sources (SDR, GWDB, RRC) and switch the map to live data.

## Agent B — Data Pipeline
**Tasks**
1) Plan: add Python ETL scripts (TWDB SDR bulk, GWDB selected wells, RRC permits). Document expected schemas.

**Acceptance**
- ETL plan documented; ready for implementation sprints (separate advanced doc).

## Agent A — Backend (FastAPI)
**Tasks**
1) Replace stub `/v1/search` with DB queries; add `/v1/wells/{id}`.

**Acceptance**
- Curl tests return real rows.

## Agent C — Web (Astro)
**Tasks**
1) Wire to real API; add filters and detail page chips.

**Acceptance**
- UX parity with stubs, now with live data.

## Agent D — DevOps
**Tasks**
1) Plan infra (DB, object storage, runners) in `docs/infra/PLAN.md`.

**Acceptance**
- Document checked in and referenced by team.


