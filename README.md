# TX Well Lookup — Monorepo

Minimal static site now; full product later (water wells + energy overlay). This repo was scaffolded by **MASTER_SCAFFOLD.md**.

## Quickstart (local)
```bash
cd apps/web
npm i
npm run dev
# open http://localhost:4321
```

### Make targets
```bash
# run web locally
make dev.web

# run API locally (after Sprint 2 scaffolds FastAPI)
make dev.api
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

## Infra
- See `docs/infra/PLAN.md` for the deployment and environment plan (DB, storage, runners).


