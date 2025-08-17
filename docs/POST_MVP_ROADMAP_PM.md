### Ground rules
- UI‑only product; internal endpoints only (strict CORS; no public API/keys).
- Two well sources: SDR and GWDB; user selects via a Data Source toggle.
- Shapefile overlays (Major/Minor Aquifers, Major River Basins) are toggleable layers on the map.
- Exports reflect the active well source and include proper attributions.

### Milestone A — Dual‑source wells (SDR + GWDB)
- **Goal**: Serve GWDB wells alongside SDR with the same UX/filters via a “Data source” toggle.
- **Why it matters**: Broader coverage and a clear differentiator vs incumbents.
- **What we’ll do**:
  - Normalize GWDB wells to a shared shape: `id, owner, county, lat, lon, depth_ft, date_completed, source, source_id`.
  - Views: `app.wells_sdr`, `app.wells_gwdb`; union `app.wells`; API queries select by `source` param.
  - UI: Data Source toggle updates map/list/export; Results limit selector (100, 250, 500, 1000, 2000).
  - Exports: include `source`, `source_id` and surface source in PDF table.
- **Acceptance criteria**:
  - Switching source refreshes pins/list in < 1–2 s; filters behave identically.
  - CSV/PDF reflect active source; fields populated; source indicator present.
- **Risks & mitigations**:
  - GWDB variance → minimal core mapping + docs; surface `source_id`.

### Milestone B — Spatial accuracy + performance (PostGIS)
- **Goal**: Accurate radius search and scalable geo performance.
- **Why it matters**: Trustworthy proximity results at speed.
- **What we’ll do**:
  - Enable PostGIS; add `geom` (POINT, EPSG:4326) to SDR/GWDB; GIST index.
  - Use `ST_DWithin(geom, ST_MakePoint(lon,lat)::geography, radius_m)` for radius.
  - Add btree indexes on `county`, `date_completed`, optional partial indexes for common filters.
  - Query caps and pagination defaults (e.g., 500).
- **Acceptance criteria**:
  - Spot‑checked distances correct; p50 search latency < 500 ms.
- **Risks & mitigations**:
  - Migration cost → staged backfill + checksums; feature flag fallback.

### Milestone C — Overlays ingest (Aquifers & River Basins)
- **Goal**: Add context layers from authoritative Texas sources.
- **Why it matters**: Adds hydrogeologic context beyond points.
- **What we’ll do**:
  - Load to `ref.*` (EPSG:4326, GIST): `ref.major_aquifers(name, geom)`, `ref.minor_aquifers(name, geom)`, `ref.river_basins(name, geom)`.
  - Store metadata/attribution; validate geometry.
  - Generate multi‑resolution simplified geometries for web use.
- **Acceptance criteria**:
  - Counts/CRS match docs; polygons validate; indexes in place.
- **Risks & mitigations**:
  - Heavy polygons → simplify by zoom, clip by viewport.

### Milestone D — Overlay UI
- **Goal**: Toggleable map overlays with clear styling and smooth performance.
- **Why it matters**: Insight without clutter.
- **What we’ll do**:
  - Leaflet overlays: Major/Minor Aquifers, Major River Basins.
  - Styling: subtle fill + outline; legends; hover tooltips.
  - Performance: simplify by zoom, clip to bbox, lazy load.
- **Acceptance criteria**:
  - Smooth pan/zoom with overlays on; readable labels; clear legend.

### Milestone E — Enriched exports (active source + overlays)
- **Goal**: CSV/PDF include overlay context for the active well source.
- **Why it matters**: Client‑ready outputs capture map context.
- **What we’ll do**:
  - Add `major_aquifer`, `minor_aquifer`, `river_basin` via point‑in‑polygon at export time.
  - PDF metadata lists active overlays; update attributions (OSM + SDR/GWDB + overlay sources).
- **Acceptance criteria**:
  - Fields present and correct on spot checks; consistent with on‑screen state.

### Milestone F — Background jobs + R2 storage (internal use)
- **Goal**: Robust handling of long exports; durable delivery without a public API.
- **Why it matters**: Reliability and UX at scale.
- **What we’ll do**:
  - Job queue + worker (RQ/Arq) for PDF/CSV/batch jobs with retries/backoff.
  - Persist outputs (PDF/ZIP) to R2; return signed URLs to the web app.
  - Job status endpoint (internal); idempotency keys; retention/TTL policies.
- **Acceptance criteria**:
  - 10+ concurrent jobs complete; no API timeouts; signed URLs functional.
- **Risks & mitigations**:
  - Queue outages → visibility + retry; heartbeat; dead‑letter review.
  - Storage bloat → TTL lifecycle rules; size caps.

### Milestone G — Batch upload UI (≤ 50 rows)
- **Goal**: In‑app batch with the same source toggle and overlay fields in outputs.
- **Why it matters**: Self‑serve “portfolio” runs; UI‑only.
- **What we’ll do**:
  - Drag‑and‑drop CSV; client validation; progress; invalid‑rows CSV.
  - Uses background job + R2 under the hood; no public API exposure.
- **Acceptance criteria**:
  - ≤ 50 rows reliably produce a ZIP with expected files; clear error reporting.

### Milestone H — Auth + plans + billing (UI‑gated)
- **Goal**: Secure access and monetization; per‑plan limits.
- **Why it matters**: Sustainable business model without public API.
- **What we’ll do**:
  - Auth (Clerk/Auth0/Supabase) + session cookies; UI routes gated.
  - Plan tiers: free/paid; quotas on searches/exports/batch.
  - Stripe checkout/portal; usage metering; receipts.
  - UI messages for limits; upgrade flows.
- **Acceptance criteria**:
  - Tiers enforce correct limits; billing flows pass; downgrade/upgrade safe.
- **Risks & mitigations**:
  - CORS/session quirks → strict origins; test matrix; robust error UX.

### Milestone I — Observability, SLOs, and errors
- **Goal**: Operability at scale with clear SLOs.
- **Why it matters**: Diagnose fast; keep reliability high.
- **What we’ll do**:
  - Metrics (Prometheus/OpenTelemetry): request counts/latencies, job durations, DB timings, error rates.
  - Error aggregation (Sentry) for API and web.
  - Dashboards + alerts for p50/p95 search, job success rates, 5xx/429s.
- **Acceptance criteria**:
  - Dashboards live; alert policies defined; weekly SLO report.
- **Risks & mitigations**:
  - Noise → sampling and tuned thresholds; alert review cadence.

### Milestone J — Security & performance hardening
- **Goal**: Tighten edges; keep things fast under load.
- **Why it matters**: Trust and scale.
- **What we’ll do**:
  - TLS/HSTS at edge; strict per‑env CORS; security headers.
  - Input validation; rate limits/quotas (per plan); statement timeouts (done); connection resiliency (done).
  - CDN for static assets and overlay tiles; cache controls.
  - Backup/restore drills; runbooks; change management gates.
- **Acceptance criteria**:
  - Security checks pass; drills succeed; change gates enforced.
- **Risks & mitigations**:
  - Load spikes → autoscale plan + quotas; graceful degradation.

### Milestone K — Search UX v2
- **Goal**: Faster, friendlier querying.
- **Why it matters**: Power‑user efficiency.
- **What we’ll do**:
  - Owner substring search; county/owner autocomplete.
  - Saved filters; shareable URLs; miles/km toggle.
- **Acceptance criteria**:
  - Saved filters rehydrate UI; autocomplete < 150 ms locally.

### Milestone L — Data governance & licensing
- **Goal**: Clear docs and compliant reuse.
- **Why it matters**: Legal and user trust.
- **What we’ll do**:
  - Source pages for SDR, GWDB, aquifers, basins (license, update cadence).
  - App/exports attributions; disclaimers; “as‑of” surfaced.
- **Acceptance criteria**:
  - Docs complete; attributions present in UI and exports.

### Promotion flow and gates
- **Dev → Staging (gate)**: Data Source toggle works; overlays render; PostGIS radius correct; exports include new fields; basic SLOs logged.
- **Staging → Prod (gate)**: Visual QA for overlays/PDF; performance within targets; auth/billing green; attribution/legal review complete.

### Rough time estimates (sequential)
- **A**: 1–2 days
- **B**: 1–2 days
- **C**: 1–2 days
- **D**: 1–2 days
- **E**: 0.5–1 day
- **F**: 2–3 days
- **G**: 1–2 days
- **H**: 2–4 days
- **I**: 1–2 days
- **J**: 1–2 days
- **K**: 1–2 days
- **L**: 0.5–1 day

- Includes the requested areas: spatial accuracy + performance (B), background jobs + R2 storage (F), auth + plans + billing (H), overlays and exports, observability, and security.


