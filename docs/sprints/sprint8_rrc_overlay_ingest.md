# Sprint 8 — RRC Overlay Ingest + Nearby API
**Outcome:** Ingest RRC permits/wellbores and expose a nearby endpoint.

## Agent B — Data Pipeline
**Tasks**
1) Create `data/sources/rrc_permits.py` to ingest daily permit CSV with lat/lon → `rrc_permits`.
2) Create `data/sources/rrc_wellbores.py` to ingest monthly wellbore file → `rrc_wellbores`.
**Acceptance**
- `rrc_permits` and `rrc_wellbores` non‑empty; spot‑check coordinates in TX.

## Agent A — Backend (FastAPI)
**Tasks**
1) Implement `GET /v1/energy/nearby?lat&lon&radius_m=1609&status=&operator=` returning `{count, items:[api14,operator,status,permit_date,lat,lon,distance_m]}` ordered by distance.
**Acceptance**
- Curl shows plausible nearby items.

## Agent C — Web (Astro)
**Tasks**
1) Add a toggle to show oil/gas pins and a small counts card on the well detail.
**Acceptance**
- Toggle updates pins; counts appear.

## Agent D — DevOps
**Tasks**
1) Add indexes on `rrc_permits(geom)` and `well_reports(county,date_completed)`; enable slow query logging.
**Acceptance**
- Indexes present and used.

---


