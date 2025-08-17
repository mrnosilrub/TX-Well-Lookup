## System overview — PM‑friendly (plain English)

### Big picture

- **What we’re building**: A simple product that lets users find nearby Texas wells (from SDR), see them on a map, filter by depth/date/county, and export results (CSV/PDF).
- **High‑level flow**:
  - **Ingest**: Copy the public SDR dataset into our database exactly as‑is (no changes) under the `ground_truth` schema.
  - **Serve**: An API reads from the database and answers queries like “wells within 1 mile of this point.”
  - **Show**: A web app calls the API, shows results on a map and list, and offers exports.
  - **Store (optional)**: Exports can be placed in object storage and downloaded via temporary links.
- **Environments**: dev → staging → prod. Each has its own DB, API, site URL, and config.

### Components and what they do

- **Database (Neon Postgres)**: Stores SDR data under `ground_truth` with 1:1 fidelity. Later, we expose “product‑ready” views (e.g., `app.wells`) without modifying the raw data.
- **API service (FastAPI on Render)**: Provides endpoints like `GET /v1/search` and `GET /v1/wells/{id}`. Connects to Neon via `DATABASE_URL` and returns JSON.
- **Web app (e.g., Astro on GitHub Pages)**: The browser UI. Renders map, filters, and results; calls the API. Uses a per‑environment `PUBLIC_API_URL`.
- **Object storage (Cloudflare R2)**: Optional place to store generated CSV/PDF files. The API can return a short‑lived signed URL so the browser can download without credentials.
- **GitHub repo and workflows (CI/CD)**: Automate tasks like loading SDR into the DB and generating `docs/SCHEMA.md`. Deploys services across dev/staging/prod.

#### Data “as-of” date
- The SDR “as-of” date is computed as the maximum of plausible date fields in `ground_truth` (e.g., `WellData.DrillingEndDate`, `PlugData.PluggingDate`).
- A helper script `ground_truth/tools/compute_as_of.py` writes `docs/AS_OF.md` with the current as-of date.
- The CI smoke workflow runs the helper in dev to verify connectivity and compute the as-of value.

### The SDR “ground truth” layer (why it matters)

- **Goal**: Keep a faithful, auditable copy of SDR so we can always trace back to the original.
- **What “1:1” means**:
  - One table per SDR `.txt` file (e.g., `WellData`, `WellLithology`). Table names match the filenames (quoted identifiers).
  - Columns come straight from the header row and are stored as `TEXT`.
  - If headers are duplicated or too long, we make them unique but preserve the original via column `COMMENT`s.
- **Loader script**: `ground_truth/loader/load_ground_truth.py`
  - Creates/cleans the target schema, reads the SDR zip, skips non‑tabular files (ReadMe/Dictionary/etc.), creates tables, and bulk‑loads data using fast `COPY`.
  - Sanitizes rows so each row matches the header width (pads or trims fields).
  - Handles `latin-1` encoding used by SDR files.
- **Schema doc generator**: `ground_truth/tools/generate_schema_md.py`
  - Connects to the DB and writes `docs/SCHEMA.md` with tables, approximate row counts, columns, and comments.
  - This is our living catalog of the raw SDR layer.

### API shape and responsibilities (current skeleton)

- **Endpoints**:
  - `GET /health`: simple health check `{ ok: true }`.
  - `GET /v1/search`: filters by `lat`, `lon`, `radius_m`, `county`, `depth_min`, `depth_max`, optional date range; returns list items with `id`, `name` (owner), `county`, `lat`, `lon`, `depth_ft`, `date_completed`.
  - `GET /v1/wells/{id}`: returns one well with the same fields plus `location_confidence` (planned).
- **Behavior**:
  - Without `DATABASE_URL`, it returns stubbed sample results (handy for local UI development).
  - With `DATABASE_URL`, it queries the DB. Once geometry is available, it can do radius searches.
- **Operational features**:
  - CORS middleware (controls which sites can call the API from a browser).
  - Optional HSTS (encourage HTTPS in browsers; typically set at the edge/CDN).
  - Structured request/error logging for observability.

### How components interact

- **Ingest path**: A GitHub workflow runs the loader against the latest SDR zip → writes tables into Neon’s `ground_truth` schema → another workflow generates `docs/SCHEMA.md`.
- **Read path (user searches)**: Browser UI → calls API `/v1/search` → API queries Neon → returns JSON → UI shows pins/list.
- **Export path**: Browser → calls API `/v1/reports` (planned) → API generates CSV/PDF → optionally stores to R2 → API returns a signed URL → browser downloads.
- **Environments**: Dev is for fast iteration; staging mirrors prod for final checks; prod is customer‑facing with stricter security.

### Environments (mental model)

- **Dev**: Dev Neon branch, dev API domain, dev site; permissive CORS; test storage bucket.
- **Staging**: Mirrors prod; manual approvals; realistic data; CORS restricted to staging site.
- **Prod**: Public. Strict CORS (only prod site), HTTPS everywhere, HSTS enabled at edge.

### Security and web basics (acronyms in plain English)

- **CORS (Cross‑Origin Resource Sharing)**: Browser rule that controls which websites (origins) can call your API from client‑side JavaScript. We maintain an allowlist per environment.
- **TLS (Transport Layer Security)**: Encryption for data in transit (the “S” in HTTPS). Prevents snooping/tampering.
- **HSTS (HTTP Strict Transport Security)**: Tells browsers “always use HTTPS for this domain for a while.” Prevents accidental HTTP.
- **CDN (Content Delivery Network)**: Caches static files closer to users to speed up loads.
- **CI/CD (Continuous Integration / Continuous Deployment)**: Automation that tests/builds/deploys code consistently across environments.
- **OIDC (OpenID Connect)**: Lets systems (like CI) securely assume roles to access providers without long‑lived secrets.
- **S3‑compatible storage (Cloudflare R2)**: Standardized object storage for files. A “signed URL” is a temporary secret link for downloads.
- **PostGIS**: Geospatial features for Postgres (distance queries like “within 1 mile”).
- **JSON / CSV / PDF**: Formats. JSON for API responses; CSV/PDF for exports.
- **TWDB / SDR / GWDB**: Texas Water Development Board datasets. SDR is our MVP scope; GWDB enrichment can be added later.
- **ELS**: Not used here; if you saw this elsewhere, you likely meant **TLS** above.

### PM‑level details you’ll care about

- **Data modeling strategy**:
  - Keep `ground_truth` pristine for audit/traceability.
  - Expose product views (e.g., `app.wells`) that map SDR fields into user‑friendly columns: `id`, `owner`, `county`, `lat`, `lon`, `depth_ft`, `date_completed`, and a simple `location_confidence` heuristic.
  - Add indexes when needed (spatial for radius; btree for county/date) to keep performance goals.
- **Performance expectations**:
  - Typical searches return in ~1–1.5 s.
  - Exports finish within ~10–30 s for normal result sizes.
- **Security posture**:
  - Per‑environment CORS allowlists and domains.
  - HTTPS everywhere (TLS); HSTS in prod at the edge.
  - Secrets kept in provider vaults and surfaced to CI per environment—never committed.
- **Operability**:
  - Health checks (`/health`). Structured logs. Manual promotion from staging to prod with a short smoke checklist (search, filter, export).
  - When changing workflows or `ground_truth` tooling, refresh `agents/README.md` and rerun the schema‑doc workflow to keep docs current.

### Key scripts and what they do

- **`ground_truth/loader/load_ground_truth.py`**
  - `parse_args`: reads command‑line options (`--zip`, `--database-url`, `--schema`).
  - `_create_schema`: drops/recreates the target schema so each load is clean.
  - `_read_header_from_zip`: reads the first line (header) of each `.txt` to get columns.
  - `_dedupe` / `_pg_ident_truncate`: make header names safe and unique in Postgres.
  - `_create_table`: creates a table with `TEXT` columns; stores original header text in column comments when adjusted.
  - `_copy_into`: sanitizes rows to match the header width and bulk‑loads via `COPY` for speed.
  - `main`: orchestrates the full load (create schema → iterate files → create tables → load rows → commit).

- **`ground_truth/tools/generate_schema_md.py`**
  - `fetch_tables`, `fetch_columns`, `fetch_col_comments`: read table/column details from Postgres.
  - `render_md`: produces human‑readable Markdown.
  - Writes `docs/SCHEMA.md`, our catalog of the raw SDR layer.

- **`legacy/apps/api/app/main.py` (API server skeleton)**
  - CORS and optional HSTS middleware; structured request logging.
  - `GET /health`: uptime check endpoint.
  - `GET /v1/search`: accepts filters (lat/lon, radius, county, depth, date); returns list items. Works with stubs if no DB; uses the DB when configured.
  - Placeholder for GWDB enrichment flags (future enhancement).

### Related reference docs in this repo

- **Product wireframe**: `docs/PROD_WIREFRAME_SDR_MVP.md`
- **MVP scope**: `docs/MVP_SDR_Scope.md`
- **Distribution blueprint**: `docs/Distribution_Blueprint_SDR_MVP.md`
- **Providers & environments**: `docs/providers.md`
- **Raw schema catalog**: `docs/SCHEMA.md`

This document is intended to give PMs a holistic, plain‑English overview of the system: the parts, how they interact, the key acronyms, and the responsibilities of core scripts and services.


