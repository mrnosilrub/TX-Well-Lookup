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


