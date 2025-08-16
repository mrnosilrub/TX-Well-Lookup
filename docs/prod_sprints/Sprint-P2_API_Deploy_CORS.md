## Sprint P2 — API Deployment & CORS Hardening

### Goal
Deploy FastAPI service using the Dockerfile, wire to managed DB, and harden CORS.

### Outcomes
- Public API with `/health`, `/v1/search`, `/v1/wells/{id}` reachable over HTTPS
- CORS restricted to web origins; autoscaling enabled

### You — Manual Tasks
- Create a service on your chosen platform (Render/Railway/Fly/ECS) pointing to `apps/api/`.
- Configure env variables:
  - `DATABASE_URL` = managed DB URL (TLS)
  - `ALLOWED_ORIGINS` = comma-separated list of web origins (staging, prod)
- Note the service URL for DNS in P3.

### Agent A — Backend Tasks
- Make CORS env-driven in `apps/api/app/main.py`:
  - Read `ALLOWED_ORIGINS` and pass to `CORSMiddleware`.
- Ensure SQL uses correct schema columns:
  - `well_reports.id`, `well_links.sdr_id`, `gwdb_wells.total_depth_ft`.
- Add basic structured logging (JSON) for requests and errors.

### Agent D — DevOps Tasks
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Health checks to `/health`; autoscale min=1, max=3.
- Enforce HTTPS and HSTS on the platform.
- Configure log retention and alerts (5xx rate, p95 latency).

### Acceptance
- `curl -s https://<api>/health` returns `{"ok": true}`.
- `GET /v1/search` returns DB-backed results after P4; CORS blocks disallowed origins.

### Verification
```bash
# Test all API endpoints are reachable and healthy
curl -i https://api.dev.txwelllookup.com/health
curl -i https://api.staging.txwelllookup.com/health  
curl -i https://api.txwelllookup.com/health

# Test search endpoint (returns stub data until P4 ETL)
curl -s https://api.dev.txwelllookup.com/v1/search | jq .
curl -s https://api.staging.txwelllookup.com/v1/search | jq .
curl -s https://api.txwelllookup.com/v1/search | jq .

# Test CORS (should succeed from allowed origins, fail from others)
curl -H "Origin: https://www.txwelllookup.com" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS https://api.txwelllookup.com/v1/search
```

### DevOps Status (P2)
- ✅ Start command configured: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ Health checks: `/health` endpoint configured on all services
- ✅ HTTPS/HSTS: Enforced via Render + custom domains
- ✅ Services deployed: dev, staging, prod with environment-specific `DATABASE_URL` and `ALLOWED_ORIGINS`
- 🔄 Autoscaling: Review Render service settings (recommend min=1, max=3)
- 🔄 Monitoring: Platform logs available; consider structured logging for better observability


