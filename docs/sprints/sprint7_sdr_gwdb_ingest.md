# Sprint 7 — SDR & GWDB Ingest + Join
**Outcome:** Ingest real TWDB SDR nightly bulk and GWDB selected wells; link them spatially.

## Agent B — Data Pipeline
**Tasks**
1) Create `data/sources/twdb_sdr.py` to download & parse nightly SDR bulk (pipe‑delimited) and/or shapefiles; UPSERT into `well_reports` & `plugging_reports`.
2) Create `data/sources/twdb_gwdb.py` to load GWDB selected wells into `gwdb_wells`.
3) Create `data/transforms/link_sdr_gwdb.py` to spatially join (≤50m) and write `well_links(match_score)`.
4) Add `data/jobs/nightly_snapshots.py` that runs the above; wire `make ingest.nightly` and a Celery task for future scheduling.
**Acceptance**
- Row counts reflect real scale; `well_links` populated for overlapping points.

## Agent A — Backend (FastAPI)
**Tasks**
1) Extend `/v1/wells/{id}` to include GWDB depth and availability flags when linked.
2) Add optional `include_gwdb=true` to `/v1/search` to bias ranking to linked wells.
**Acceptance**
- Detail and search return GWDB fields when available.

## Agent C — Web (Astro)
**Tasks**
1) Display Aquifer & GCD chips (use placeholder overlays until Sprint 9/10); show GWDB badges on well cards.
**Acceptance**
- Chips and badges render when data present.

## Agent D — DevOps
**Tasks**
1) Add `.github/workflows/ingest-nightly.yml` to invoke `nightly_snapshots.py` (can be a no‑op in forks).
**Acceptance**
- Action runs and logs.

---


