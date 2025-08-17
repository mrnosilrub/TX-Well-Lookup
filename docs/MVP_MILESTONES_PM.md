## MVP Roadmap — Milestones (PM-friendly, plain English)

This plan lists small, sequential milestones from the current state (SDR ground truth loaded) to a usable MVP. Each milestone includes goals, why it matters, what we’ll do, acceptance criteria, risks, and environment rollout.

See also: `docs/SYSTEM_OVERVIEW_PM.md` and `docs/PROD_WIREFRAME_SDR_MVP.md`.

### Milestone 0 — Baseline and guardrails (Dev)

- **Goal**: Confirm the raw SDR layer is healthy, documented, and automated.
- **Why it matters**: Establishes trust in data and repeatable operations before building features.
- **What we’ll do**:
  - Regenerate the raw schema catalog via `ground_truth/tools/generate_schema_md.py` → updates `docs/SCHEMA.md`.
  - Add/verify a simple CI smoke step: connect to DB, count a few key tables, and fail fast if unreachable.
  - If workflows or ground_truth tooling change, refresh `agents/README.md` and re-run the schema-doc workflow.
- **Acceptance criteria**:
  - `docs/SCHEMA.md` reflects current dev DB; counts look reasonable.
  - A quick CI job passes on dev and fails meaningfully if DB is misconfigured.
- **Risks & mitigations**:
  - DB connectivity flakiness → keep retries and clear errors in CI.
  - SDR file format drift → loader already pads/trims rows; document anomalies.
- **Environments**: Do in dev only; no user impact.

### Milestone 1 — Minimal product model (read-only views)

- **Goal**: Create a thin, read-only layer that exposes just the fields the app needs, without modifying `ground_truth`.
- **Why it matters**: Keeps raw data pristine and gives the API a clean, stable shape.
- **What we’ll do**:
  - Add an `app` schema with a view `app.wells` that projects essential columns:
    - `id` (SDR WellReportTrackingNumber)
    - `owner` (e.g., `WellData.OwnerName`)
    - `county` (e.g., `WellData.County`)
    - `lat`, `lon` (e.g., `WellData.CoordDDLat`, `WellData.CoordDDLong`)
    - `depth_ft` (best-effort from borehole/completion depths)
    - `date_completed` (best-effort from completion/end dates)
    - `location_confidence` (simple heuristic from coordinate quality fields)
  - Document the initial field mapping assumptions in a short `docs/app_model.md`.
  - Plan spatial support: compute `geom` on the fly in queries or include `geom` in a companion view for radius searches (PostGIS).
- **Acceptance criteria**:
  - `SELECT * FROM app.wells LIMIT 10;` returns plausible rows, many with lat/lon.
  - Field names match what the API/UI expects.
- **Risks & mitigations**:
  - Lat/lon sparsity → allow results without map pins; communicate confidence.
  - Depth/date inconsistencies → clearly mark best-effort logic and refine later.
- **Environments**: Dev first; promote after API integration smoke tests.

### Milestone 2 — API v1 (Search + Well by ID)

- **Goal**: Provide the minimal endpoints the web app needs.
- **Why it matters**: Unblocks UI development; defines the contract.
- **What we’ll do**:
  - Implement `GET /v1/search` with params: `lat`, `lon`, `radius_m`, `county`, `depth_min`, `depth_max`, `date_from`, `date_to`, `limit`.
  - Implement `GET /v1/wells/{id}`: returns a single well with `location_confidence`.
  - Start with attribute filters; then enable radius filtering using PostGIS once `geom` is available.
  - Configure CORS per environment so the correct site can call the API from the browser.
- **Acceptance criteria**:
  - Typical search returns JSON within ~1–1.5 s in dev with realistic data.
  - Radius queries work after spatial is enabled; non-spatial filters work regardless.
- **Risks & mitigations**:
  - Slow queries → add basic indexes (county, date) and paginate.
  - Spatial precision → start simple (WGS84) and document confidence.
- **Environments**: Dev → Staging (manual approval) → Prod when stable.

### Milestone 3 — Web App (Search + Map + List)

- **Goal**: Implement the main “App” screen from the wireframe.
- **Why it matters**: Delivers visible user value and end-to-end flow.
- **What we’ll do**:
  - Filters panel: search, radius, date range, depth range, county; apply/reset.
  - Map: pins for results, fit-to-results, pin click opens a small card.
  - Results list: columns `Well ID`, `Owner`, `County`, `Depth (ft)`, `Completed (date)`; row click syncs with map.
  - States: empty, loading, no results, error (with retry).
  - Show “As-of YYYY-MM-DD” and SDR attribution text.
- **Acceptance criteria**:
  - A user can search an address/point, see pins and a list, and open well details.
  - UI is responsive and accessible basics (tab focus, contrast).
- **Risks & mitigations**:
  - Geocoding dependence → allow map click to start search as fallback.
  - Many pins → cap results and consider clustering later.
- **Environments**: Dev connected to dev API; promote after a short smoke checklist.

### Milestone 4 — CSV export (server-generated)

- **Goal**: Download current filtered results as a CSV.
- **Why it matters**: Immediate utility for users; simpler than PDF.
- **What we’ll do**:
  - API `POST /v1/reports?format=csv` accepts current filters.
  - For small results, stream the CSV directly; for larger, write to Cloudflare R2 and return a short-lived signed URL.
  - Add an “Export CSV” button in the UI.
- **Acceptance criteria**:
  - Exported CSV columns match the list view and include `lat`, `lon`.
  - Typical exports complete within 10–30 s.
- **Risks & mitigations**:
  - Large result sets → enforce server-side limits; page server-side and stream.
  - Permissions on files → use signed URLs with TTL.
- **Environments**: Dev first; staging test with realistic sizes; then prod.

### Milestone 5 — PDF export (client-ready)

- **Goal**: Produce a professional-looking PDF with a map snapshot and table.
- **Why it matters**: Matches the wireframe’s deliverable and client expectations.
- **What we’ll do**:
  - API `POST /v1/reports?format=pdf` generates a PDF server-side (headless browser or server template approach).
  - Include header (name/logo/as-of), map snapshot, results table, and legal footer.
  - Store in R2 with TTL; return signed URL.
  - Add “Export PDF” button in the UI.
- **Acceptance criteria**:
  - PDF looks like the wireframe and downloads within ~10–30 s for typical sizes.
  - Text is selectable; map is high enough resolution.
- **Risks & mitigations**:
  - Rendering reliability → test common OS/viewers; keep fonts embedded.
  - Map snapshot source → decide on static map provider or client-provided image.
- **Environments**: Dev → Staging visual review → Prod.

### Milestone 6 — Small batch (≤ 50 addresses)

- **Goal**: Process a small CSV of addresses into a ZIP of PDFs + one master CSV.
- **Why it matters**: Enables portfolio-style workflows for early users.
- **What we’ll do**:
  - API `POST /v1/batch`: upload CSV (addresses or lat/lon), validate, then process.
  - Start synchronous with light concurrency; if needed, add a background worker later.
  - Store the ZIP in R2; return a signed URL (and optionally email via Postmark).
- **Acceptance criteria**:
  - A 50-address CSV completes within a few minutes and produces a downloadable ZIP.
  - Invalid rows are reported clearly.
- **Risks & mitigations**:
  - Long-running jobs → cap size at 50; add backpressure and progress updates later.
  - Geocoding rate limits → batch/throttle; allow lat/lon inputs.
- **Environments**: Dev with small sets; staging with realistic; prod after.

### Milestone 7 — Hardening and polish

- **Goal**: Improve performance, security, and operability for production readiness.
- **Why it matters**: Keeps user experience fast, safe, and reliable.
- **What we’ll do**:
  - Performance: materialize `app.wells` if needed; add GIST on `geom`, btree on `county`/`date`.
  - Observability: structured logs (already), add basic request metrics and error aggregation.
  - Security: strict per-env CORS, rate limits, input validation, HTTPS/HSTS.
  - Docs/process: ensure “as-of” surfaced; confirm attribution and disclaimers in app and exports.
- **Acceptance criteria**:
  - Staging meets performance targets; error rates are low; logs are actionable.
  - Security checks pass (CORS, TLS/HSTS, secrets via envs).
- **Risks & mitigations**:
  - Unexpected heavy queries → improve indexes and pagination; profile slow paths.
  - Edge caching quirks → use CDN for static; don’t cache API unless safe.
- **Environments**: Staging soak → Prod with confidence.

### Promotion flow and gates (dev → staging → prod)

- **Dev → Staging (gate)**: API endpoints stable; UI smoke passes (search, filter, map, list); CSV export works for typical result sizes.
- **Staging → Prod (gate)**: Visual QA for PDF; performance within targets; environment variables set (CORS, URLs, secrets); HSTS confirmed at edge; run a final smoke script.

### Rough time estimates (sequential)

- **M0**: 0.5–1 day
- **M1**: 1–2 days
- **M2**: 1–2 days
- **M3**: 2–3 days
- **M4**: 0.5–1 day
- **M5**: 1–2 days
- **M6**: 2–3 days
- **M7**: 1–2 days

Notes:
- This roadmap assumes no new infra. It builds on `ground_truth`, the existing FastAPI skeleton, and the three environments already wired together.
- For any workflow or tool changes in `ground_truth`, refresh `agents/README.md` and re-run the schema-doc workflow.
