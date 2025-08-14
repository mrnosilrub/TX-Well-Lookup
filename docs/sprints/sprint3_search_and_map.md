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


