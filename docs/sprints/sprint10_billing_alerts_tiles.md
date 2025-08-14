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

