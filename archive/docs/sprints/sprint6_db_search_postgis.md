# Sprint 6 — DB Search & Detail (Production Path)
**Outcome:** Stand up Postgres + PostGIS, a real FastAPI service with `/v1/search` and `/v1/wells/{id}`, and wire the Astro site to it.

## Agent D — DevOps
**Tasks**
1) Add `docker-compose.yml` at repo root with services: `db` (postgis), `api` (FastAPI), `web` (Astro), `redis` (for later).
2) Add `db/init/01_postgis.sql` enabling `postgis` & `pg_trgm` and creating `well_reports` & `plugging_reports` tables.
3) Add `Makefile` targets: `dev` (compose up), `stop`, `db.shell`, `api.shell`.
**Acceptance**
- `make dev` boots DB/API/Web. `make db.shell` enters psql.

## Agent A — Backend (FastAPI)
**Tasks**
1) Create `apps/api` with `requirements.txt` (fastapi, uvicorn, pydantic, sqlalchemy, psycopg2-binary) and `app/` package: `main.py`, `db.py`, `models.py`, `routers/search.py`, `routers/wells.py`.
2) Implement `/v1/search`:
   - Params: `q, county, date_from, date_to, depth_min, depth_max, has_plug, lat, lon, radius_m=1609, limit<=100`.
   - WHERE: `ST_DWithin(geom, point, radius)` when `lat/lon`; `ILIKE` on `owner_name,address,driller_name` when `q`.
3) Implement `/v1/wells/{id}` with `location_confidence` derived from `location_error_m` and a `documents` array (placeholder URLs).
**Acceptance**
- Curl examples return JSON in <150ms locally.

## Agent B — Data Pipeline
**Tasks**
1) Create `data/fixtures/sdr_sample.csv` with ≥200 rows across ≥5 counties.
2) Add `data/scripts/seed_sdr_sample.py` that UPSERTs rows into `well_reports` and sets `geom`.
3) Make target `seed.sample` that runs the script inside the API container.
**Acceptance**
- `SELECT COUNT(*) FROM well_reports;` ≥200 with non‑null `geom`.

## Agent C — Web (Astro)
**Tasks**
1) Add a minimal search UI that calls `${PUBLIC_API_URL}/v1/search` and renders a list.
2) Create `/well/[id].astro` to fetch `/v1/wells/{id}` and display details.
**Acceptance**
- Typing a seeded term shows results; detail page loads.

---


