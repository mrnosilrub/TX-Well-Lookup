# TX Well Lookup — Astro + FastAPI Monorepo (Dev Scaffold)

Address‑first reports for Texas water wells (TWDB SDR/GWDB + TCEQ links) with an Energy Overlay (RRC). This scaffold boots a local stack via Docker Compose: Astro web, FastAPI backend, Postgres+PostGIS, Redis, and a Celery worker.

> **Status:** Developer scaffold. Endpoints return stubs; DB tables are created. Swap stubs with real ingest + search when ready.

## Quickstart

```bash
# 1) clone and enter
# git clone <your repo> && cd tx-well-lookup

# 2) copy environment
cp .env.example .env

# 3) boot dev stack
docker compose up --build

# Web:   http://localhost:4321
# API:   http://localhost:8000/docs
# DB:    localhost:5432  (txwell/txwell)
# Redis: localhost:6379
```

## What’s here
- **apps/web** — Astro + Tailwind + MapLibre (OSM raster style). Uses `PUBLIC_API_URL` to call API.
- **apps/api** — FastAPI with CORS; stub routes for `/v1/search` and `/v1/wells/{id}`.
- **apps/worker** — Celery worker scaffold for nightly/delta jobs.
- **db/init** — PostGIS + minimal tables auto‑created at container init.
- **docker-compose.yml** — Dev orchestration; mounts code for hot‑reload.
- **Makefile** — Convenience targets.

## Next steps (swap stubs → real data)
1. Implement SDR nightly loader in `data-pipeline/jobs/nightly_snapshots.py`.
2. Add delta polling job for SDR FeatureServer; commit to `apps/worker` task.
3. Build RRC permit + wellbore ingesters; expose `/v1/energy/nearby`.
4. Replace `/v1/search` to query PostGIS (radius + facets).
5. Ship PDF generator route and Stripe credit gates.

---

## Project Structure
```
tx-well-lookup/
  apps/
    web/           # Astro front-end (SSR-capable, but dev uses preview)
    api/           # FastAPI backend
    worker/        # Celery worker for ETL/alerts
  data-pipeline/
    jobs/          # ETL scripts (stubs)
    sources/       # connectors (add later)
    transforms/    # normalizers (add later)
  db/
    init/          # SQL executed at DB init (PostGIS + tables)
  infra/
    terraform/     # IaC (placeholder)
  .github/
    workflows/     # CI/CD (placeholders)
  docker-compose.yml
  Makefile
  .env.example
  .gitignore
  README.md
```

---

## License & Attribution
Public data from TWDB (SDR/GWDB), TCEQ (historic scans), and RRC (permits/wellbores). Include clear attribution and disclaimers in production.