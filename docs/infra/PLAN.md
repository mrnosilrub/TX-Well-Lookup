# Infra Plan — TX Well Lookup

This document outlines a pragmatic path from local development to a small production deployment. It favors simple, low‑ops components first, with clear upgrade paths.

## Goals
- Durable Postgres + PostGIS for geospatial search
- Static web hosting for `apps/web` (Astro)
- Object storage for generated reports/artifacts
- CI/CD with per‑environment secrets and guardrails

## Environments
- Local: docker-compose (introduced in Sprint 6) for DB/API/Web
- Preview: GitHub Actions PR jobs (build only)
- Staging: optional single‑region stack mirroring prod settings
- Production: managed database + containerized API + static web hosting

## Web (Astro)
- Host: GitHub Pages via Actions (already configured)
- Base path: `PUBLIC_BASE_PATH` set in workflow to the repo subpath
- Custom domain (optional): configure in GitHub Pages or behind Cloudflare

## API (FastAPI)
- Runtime: containerized process
- Local: `uvicorn` via `make dev.api`
- Production options (pick 1):
  - Render/Railway/Fly.io (fastest to ship, low ops)
  - AWS ECS on Fargate (more control; pair with ALB + ACM certs)
- Minimum baseline:
  - One small task/container, autoscale 1→3
  - Healthcheck at `/health`
  - CORS allow `Pages URL` origin

## Database (Postgres + PostGIS)
- Local: Postgres 15 with PostGIS extension via docker-compose (Sprint 6)
- Production: managed Postgres (AWS RDS, Neon, or CrunchyBridge)
- Required extensions: `postgis`, `pg_trgm`
- Backups: daily snapshots, 7–30 day retention, PITR where available
- Security: encryption at rest, TLS in transit, restricted network access
- Indexing (initial):
  - `well_reports(geom)` GiST
  - Trigram indexes for text search columns referenced in sprints

## Object Storage (Reports & Tiles)
- Provider: S3 or Cloudflare R2
- Buckets (per env): `txwl-reports-<env>`
- Encryption: SSE enabled
- Lifecycle: transition older objects to infrequent access; optional 90‑day expiry for temp artifacts
- Access: presigned URLs (implemented by backend) with short TTL
- Layout (example):
  - `reports/<yyyy>/<mm>/<dd>/<report_id>/report.pdf`
  - `bundles/<report_id>/bundle.zip`

## CI/CD
- GitHub Actions
  - `ci.yml`: build `apps/web` on push/PR (exists)
  - `deploy-pages.yml`: publishes Astro to Pages (exists)
  - Future: `ingest-nightly.yml` for ETL jobs (Sprint 7)
- Caching: npm cache keyed by `apps/web/package-lock.json`
- Concurrency: limit Pages deploys to one in‑flight
- Environments: `staging`, `production` with required reviewers

## Secrets & Config
- GitHub Actions: store non‑runtime secrets (API URL, tokens for deploy)
- Backend runtime: use cloud secret store (AWS SSM Parameter Store/Secrets Manager) mounted/env‑injected to the API container
- Public config: `PUBLIC_*` env vars for frontend build‑time only

## Networking & Security
- API behind HTTPS (ALB or managed platform), HSTS enabled
- CORS restricted to Pages/staging domains
- Rate limit at edge (platform or gateway) to prevent abuse
- DB access restricted to API only; no public ingress

## Observability
- Logs: structured JSON; aggregate in platform logs or CloudWatch/ELK
- Metrics: basic CPU/mem/requests; alert on error rate and latency
- Traces (optional): OpenTelemetry in later sprints

## Cost Notes (rough)
- GitHub Pages: $0
- Managed Postgres: $15–$50/mo (starter tier)
- Object storage: pennies/GB; egress applies
- API runtime: ~$5–$30/mo depending on platform/uptime

## Timeline
- Sprint 6: introduce `docker-compose` for local DB/API/Web and DB init SQL
- Sprint 7+: nightly ingest workflow and storage usage
- Sprint 9: signed URLs for downloadable artifacts

## Action Items
- Track infra decisions in PRs referencing this plan
- Keep `docs/infra/` as the single source of truth for environment notes


