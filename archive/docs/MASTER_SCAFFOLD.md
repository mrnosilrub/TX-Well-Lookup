# MASTER_SCAFFOLD.md — TX Well Lookup

> **Paste this document into a Cursor agent.** It will scaffold a working static site (Astro), a monorepo layout for future work, and generate **sprint prompt files** for each agent. After this runs, you’ll (1) have a repo that loads a static site locally and on GitHub Pages, and (2) a tidy set of sprint docs to execute in order.

---

## Agent Instructions (you = Cursor)
You are an autonomous repo scaffolder. Create the exact files below. Then run the **Post‑Scaffold Commands**. Do not deviate from filenames or contents.

### Repository layout (create exactly this)
```
tx-well-lookup/
  apps/
    web/                  # Astro static site (loads now)
  docs/
    sprints/              # Sprint guides w/ agent prompts
  .github/
    workflows/            # CI + Pages deploy
  .gitignore
  README.md
```

---

## Files to create (exact contents)

=== FILE: README.md
# TX Well Lookup — Monorepo

Minimal static site now; full product later (water wells + energy overlay). This repo was scaffolded by **MASTER_SCAFFOLD.md**.

## Quickstart (local)
```bash
cd apps/web
npm i
npm run dev
# open http://localhost:4321
```

## Deploy to GitHub Pages
1. Enable **Pages → Build & Deployment → GitHub Actions** in repo settings.
2. Push `main`. The action in `.github/workflows/deploy-pages.yml` will publish `apps/web/dist`.
3. If your Pages site uses a project path (e.g. `/tx-well-lookup`), set `PUBLIC_BASE_PATH` in the workflow to that path.

---

## Sprints
Sprint docs live in `docs/sprints/` and are executed in order:
- `sprint1_static_to_foundation.md`
- `sprint2_api_and_db_shell.md`
- `sprint3_search_and_map.md`
- `sprint4_reports_and_paywall_stub.md`
- `sprint5_real_ingest_and_overlays.md`
- `sprint6_db_search_postgis.md`
- `sprint7_sdr_gwdb_ingest.md`
- `sprint8_rrc_overlay_ingest.md`
- `sprint9_reports_storage_signedurls.md`
- `sprint10_billing_alerts_tiles.md`

Each sprint doc contains **Agent A (Backend)**, **Agent B (Data Pipeline)**, **Agent C (Web)**, **Agent D (DevOps)** prompts with tasks, acceptance criteria, and tests.

---

## Contributing
Use feature branches (`feat/...`) + PRs. Keep env values out of the repo.


=== FILE: .gitignore
# Node
node_modules
# Astro
apps/web/.astro
apps/web/dist
# Logs
*.log
# Misc
.DS_Store


=== FILE: .github/workflows/deploy-pages.yml
name: Deploy Astro to GitHub Pages
on:
  push:
    branches: [ main ]
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - name: Install deps
        working-directory: apps/web
        run: npm ci
      - name: Build
        working-directory: apps/web
        env:
          PUBLIC_BASE_PATH: "/" # change to "/<repo>" if publishing at subpath
        run: npm run build
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: apps/web/dist
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4


=== FILE: apps/web/package.json
{
  "name": "tx-well-lookup-web",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "astro dev --host --port 4321",
    "build": "PUBLIC_BASE_PATH=${PUBLIC_BASE_PATH:-/} astro build",
    "preview": "astro preview --host --port 4321"
  },
  "dependencies": {
    "astro": "^4.14.0"
  }
}


=== FILE: apps/web/astro.config.mjs
/** @type {import('astro').AstroUserConfig} */
export default {
  output: 'static',
  base: process.env.PUBLIC_BASE_PATH || '/',
  server: { host: true },
};


=== FILE: apps/web/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "preserve",
    "strict": true,
    "baseUrl": ".",
    "types": ["astro/client"]
  }
}


=== FILE: apps/web/src/pages/index.astro
---
const title = 'TX Well Lookup';
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>
      :root { --ink:#0b0b0c; --bg:#f6f7f9; --card:#fff; --muted:#6b7280; }
      html,body{height:100%} body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.4 system-ui, -apple-system, Segoe UI, Roboto, sans-serif}
      header{position:sticky;top:0;background:var(--card);border-bottom:1px solid #e5e7eb}
      .wrap{max-width:1000px;margin:0 auto;padding:16px}
      .btn{background:#111;color:#fff;border-radius:10px;padding:10px 14px;text-decoration:none}
      .card{background:var(--card);border:1px solid #e5e7eb;border-radius:14px;padding:18px}
      .grid{display:grid;gap:16px;grid-template-columns:1fr}
      @media(min-width:960px){.grid{grid-template-columns: 320px 1fr}}
      small{color:var(--muted)}
      code{background:#f3f4f6;padding:2px 6px;border-radius:6px}
    </style>
  </head>
  <body>
    <header>
      <div class="wrap" style="display:flex;gap:12px;align-items:center;">
        <strong>TX Well Lookup</strong>
        <span style="color:var(--muted)">starter static site</span>
        <a class="btn" href="https://github.com/" rel="noreferrer">GitHub</a>
      </div>
    </header>

    <main class="wrap" style="padding-block:24px">
      <div class="grid">
        <section class="card">
          <h2>It works 🎯</h2>
          <p>This is a minimal Astro site scaffold. Next sprints add API, data pipeline, maps, and paid reports.</p>
          <p><small>Build path base = <code>{Astro.site?.pathname || '/'}</code> • Update via <code>PUBLIC_BASE_PATH</code>.</small></p>
        </section>
        <section class="card">
          <h3>What’s next</h3>
          <ol>
            <li>Read <code>docs/sprints/sprint1_static_to_foundation.md</code> and execute Agent C tasks.</li>
            <li>Follow Sprint 2 to add the API shell; Sprint 3 brings search & map.</li>
          </ol>
        </section>
      </div>
    </main>
  </body>
</html>


=== FILE: docs/sprints/sprint1_static_to_foundation.md
# Sprint 1 — Static → Foundation
**Outcome:** Static site runs locally and on GitHub Pages. Monorepo is ready for expansion (API, data, DevOps). Keep it simple and shippable.

## Agent C — Web (Astro)
**Tasks**
1) Confirm local dev works: `npm i && npm run dev` in `apps/web`.
2) Add a second page `about.astro` with project goals; link it from the header.
3) Add a basic component `components/Hero.astro` used on the home page.

**Acceptance**
- Home and About load locally.
- No console errors; Lighthouse Performance ≥ 95 on localhost.

**Tests**
```bash
npm run dev
# visit / and /about
```

## Agent D — DevOps
**Tasks**
1) Enable GitHub Pages (Actions). Push `main` and verify deployment.
2) If publishing under `/REPO`, set `PUBLIC_BASE_PATH` in workflow accordingly.

**Acceptance**
- Pages URL loads the built site, including the About page.

## Agent A — Backend (placeholder for Sprint 2)
_No work in Sprint 1. Ensure repo structure is clean._

## Agent B — Data Pipeline (placeholder for Sprint 2)
_No work in Sprint 1._

---

## Definition of Done
- Site serves locally at `http://localhost:4321`.
- Pages deployment is live and reflects latest commit.


=== FILE: docs/sprints/sprint2_api_and_db_shell.md
# Sprint 2 — API & DB Shell (Scaffold only)
**Outcome:** Create placeholders for API & data layers without functionality, so future sprints can plug in.

## Agent A — Backend (FastAPI)
**Tasks**
1) Create directory `apps/api/` with:
   - `requirements.txt` (fastapi, uvicorn, pydantic)
   - `app/main.py` with `/health` returns `{ ok: true }`
   - `Dockerfile` for local run (optional today)
2) Add `.vscode/launch.json` (optional) for debugging.

**Acceptance**
- `uvicorn app.main:app --reload --port 8000` starts locally.

## Agent B — Data Pipeline
**Tasks**
1) Create directory `data/` with `README.md` explaining future ETL and a `fixtures/` folder.
2) Add `scripts/seed_readme.sh` placeholder that echoes next steps.

**Acceptance**
- Repo compiles and runs without errors; no runtime coupling yet.

## Agent C — Web (Astro)
**Tasks**
1) Add a temporary API status widget on home that fetches `/health` if available (ignore errors silently).

**Acceptance**
- Widget shows `API: offline` when backend not running, `API: ok` when it is.

## Agent D — DevOps
**Tasks**
1) Add `.github/workflows/ci.yml` with simple build of `apps/web`.

**Acceptance**
- CI passes on PR.


=== FILE: docs/sprints/sprint3_search_and_map.md
# Sprint 3 — Search & Map (Stubbed Data)
**Outcome:** Build the search UI and a map view fed by stubbed JSON (no DB yet). Establish UX and wiring.

## Agent C — Web (Astro)
**Tasks**
1) Add Map (no keys): integrate a simple vector tiles base (or raster OSM) with a single marker.
2) Build a search form that calls `/api/search.json` (static stub you create under `apps/web/src/pages/api/search.json.ts`).
3) Results list with fly‑to behavior.

**Acceptance**
- Searching updates list and map markers using stubbed JSON.

## Agent A — Backend (FastAPI)
**Tasks**
1) Mirror the stub endpoint in FastAPI at `/v1/search` returning the same shape.

**Acceptance**
- Swapping the frontend fetch URL to the FastAPI endpoint produces the same UX locally.

## Agent B — Data Pipeline
**Tasks**
1) Provide a `fixtures/wells_stub.json` used by both the web stub and API stub.

**Acceptance**
- Single source of stub truth.

## Agent D — DevOps
**Tasks**
1) Add `make dev.web` and `make dev.api` scripts to README.

**Acceptance**
- New commands documented and usable.


=== FILE: docs/sprints/sprint4_reports_and_paywall_stub.md
# Sprint 4 — Reports & Paywall (Stub)
**Outcome:** Add the Report button and a stubbed “PDF ready” flow. Add a 402-style response gate to simulate paywall.

## Agent C — Web (Astro)
**Tasks**
1) Add a `Generate Report` button on the detail view. POST to `/v1/reports` (or stub) and show spinner → success state with fake URL.
2) If API returns 402, show modal to “Buy credits” (just closes modal in stub).

**Acceptance**
- Flow feels real even with stubs.

## Agent A — Backend (FastAPI)
**Tasks**
1) Add POST `/v1/reports` that returns `{ report_id }` and, randomly, 402 to simulate no credits.
2) Add GET `/v1/reports/{id}` that returns `{ pdf_url: "/fake/report.pdf" }`.

**Acceptance**
- Frontend flow works against stub endpoints.

## Agent B — Data Pipeline
**Tasks**
1) Add a `reports/README.md` describing how CSV/GeoJSON will be bundled later.

**Acceptance**
- Documentation exists.

## Agent D — DevOps
**Tasks**
1) Ensure CI builds still pass.

**Acceptance**
- Green CI.


=== FILE: docs/sprints/sprint5_real_ingest_and_overlays.md
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


---

## Post‑Scaffold Commands (run after file creation)
1) **Install & run web locally**
```bash
cd apps/web
npm i
npm run dev
```
2) **Commit & push**
```bash
git add .
git commit -m "chore: scaffold astro static site and sprint docs"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```
3) **Enable GitHub Pages (Actions)** and verify deploy.

---

## Notes
- This scaffold intentionally keeps the static site minimal to avoid friction. All deeper functionality (API, data pipelines, billing, tiles) is deferred to the sprint documents inside `docs/sprints/`.
- If you need Tailwind, MapLibre, or Docker from day one, add them in follow‑up PRs or extend Sprint 1’s tasks.







=== FILE: docs/sprints/sprint6_db_search_postgis.md
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

=== FILE: docs/sprints/sprint7_sdr_gwdb_ingest.md
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

=== FILE: docs/sprints/sprint8_rrc_overlay_ingest.md
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

=== FILE: docs/sprints/sprint9_reports_storage_signedurls.md
# Sprint 9 — Reports, Storage, Signed URLs
**Outcome:** Generate a real PDF & ZIP bundle, store in object storage (or local in dev), and serve via signed URLs.

## Agent A — Backend (FastAPI)
**Tasks**
1) Add `POST /v1/reports` to create a job and `GET /v1/reports/{id}` to fetch status + URLs.
2) Add an internal `/v1/reports/{id}/html` that renders report HTML for printing.
**Acceptance**
- POST returns an ID; later GET returns `pdf_url` and `zip_url`.

## Agent B — Data Pipeline
**Tasks**
1) Add `data/bundles/bundle_builder.py` to produce CSV & GeoJSON for wells within radius and a JSON manifest of source links.
2) Add a worker task to call Playwright (HTML→PDF) and zip artifacts; upload to S3/R2 (or save locally in dev).
**Acceptance**
- Downloadable PDF & ZIP exist; manifest contains source URLs.

## Agent C — Web (Astro)
**Tasks**
1) On `/well/[id]`, implement "Generate Report" → POST, poll, then show download links. Handle error states.
**Acceptance**
- End‑to‑end flow works locally.

## Agent D — DevOps
**Tasks**
1) Provision object storage (S3/R2) and set env vars; in dev, fallback to local path.
2) Implement signed download endpoint that proxies to storage with short‑lived tokens.
**Acceptance**
- Links are time‑limited; direct bucket access isn’t exposed.

---

=== FILE: docs/sprints/sprint10_billing_alerts_tiles.md
# Sprint 10 — Billing, Alerts, Vector Tiles
**Outcome:** Stripe credits gate reports; alerts notify on new SDR/RRC near a saved location; map uses vector tiles for scale.

## Agent A — Backend (FastAPI)
**Tasks**
1) Add `/billing/checkout` + `/billing/webhook` (test mode). On success, insert `credit_grants`.
2) Enforce credits in `POST /v1/reports`; insert `credit_spends` on success.
3) Add `/v1/alerts` CRUD and alert fanout to email/webhook.
**Acceptance**
- 0 credits → 402; after test purchase → report succeeds; alert records exist.

## Agent B — Data Pipeline
**Tasks**
1) Add delta pollers for SDR and RRC; on new rows within any alert radius, enqueue notifications.
2) Build nightly vector tiles (PMTiles) for well clusters and publish to storage.
**Acceptance**
- Alert simulation works; PMTiles generated and accessible.

## Agent C — Web (Astro)
**Tasks**
1) Add “Watch this area” UI; list alerts in a dashboard; allow delete.
2) Switch to our vector tile layer for wells; keep OSM as base.
**Acceptance**
- Alerts are creatable/deletable; tiles render smoothly.

## Agent D — DevOps
**Tasks**
1) CDN in front of storage for tiles; cache‑bust nightly. Add Terraform plan stub if applicable.
2) Secrets management for Stripe; split envs (dev/staging/prod) in Actions.
**Acceptance**
- Tiles served via CDN; deploy pipeline supports staging; secrets not in repo.