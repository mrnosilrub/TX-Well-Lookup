# Sprint 2 — API & DB Shell (Scaffold only)
**Outcome:** Create placeholders for API & data layers without functionality, so future sprints can plug in.

## Agent A — Backend (FastAPI)
**Tasks**
1) Create directory `apps/api/` with:
   - `requirements.txt` (fastapi, uvicorn, pydantic)
   - `app/main.py` with `/health` returns `{ ok: true }`
   - `Dockerfile` for local run (optional today)
2) Add `.vscode/launch.json` (optional) for debugging.

**Acceptance**
- `uvicorn app.main:app --reload --port 8000` starts locally.

## Agent B — Data Pipeline
**Tasks**
1) Create directory `data/` with `README.md` explaining future ETL and a `fixtures/` folder.
2) Add `scripts/seed_readme.sh` placeholder that echoes next steps.

**Acceptance**
- Repo compiles and runs without errors; no runtime coupling yet.

## Agent C — Web (Astro)
**Tasks**
1) Add a temporary API status widget on home that fetches `/health` if available (ignore errors silently).

**Acceptance**
- Widget shows `API: offline` when backend not running, `API: ok` when it is.

## Agent D — DevOps
**Tasks**
1) Add `.github/workflows/ci.yml` with simple build of `apps/web`.

**Acceptance**
- CI passes on PR.


