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


