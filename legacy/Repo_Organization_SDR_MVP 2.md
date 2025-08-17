## Repo Organization Plan — SDR‑Only MVP

This is a safe, step‑by‑step plan to tidy the repo around the SDR‑only MVP. It does NOT execute any moves yet. Use the commands below when you’re ready.

### Goal
Keep only what’s needed for: SDR database + minimal API + web search/map + PDF/CSV exports. Archive everything else for later.

### Target high‑level layout
```
TX-Well-Lookup/
  apps/
    api/            # keep core endpoints: /health, /v1/search, /v1/wells/{id}, /v1/reports
    web/            # keep Home + App (Search+Map+Export); remove non‑MVP UI
  data/
    sources/
      twdb_sdr.py   # keep (SDR ingest)
      ...           # (archive RRC/GWDB sources)
    transforms/
      ...           # (archive GWDB link scripts)
    jobs/
      nightly_snapshots.py  # scope to SDR only
  db/
    init/
      01_postgis.sql         # keep
      03_well_reports_fix.sql# keep
      03_sdr_children.sql    # add later (child tables for SDR files)
      ...                    # (archive RRC/GWDB DDL)
  docs/
    MVP_SDR_Scope.md
    PRODUCTION: wireframe, distribution, DB_schema/*
  archive/        # new folder (git‑tracked) for non‑MVP code/docs
```

### What to KEEP (MVP)
- SDR ingest: `data/sources/twdb_sdr.py`, `data/jobs/nightly_snapshots.py`
- DB init: `db/init/01_postgis.sql`, `db/init/03_well_reports_fix.sql` (and later `03_sdr_children.sql`)
- API: only `/health`, `/v1/search`, `/v1/wells/{id}`, `/v1/reports`
- Web: Home + App (Search/Map/Export), docs under `docs/`

### What to ARCHIVE (for later)
- GWDB: `data/sources/twdb_gwdb*.py`, `data/transforms/link_sdr_gwdb*.py`, `db/init/02_gwdb*.sql`
- RRC: `data/sources/rrc_*.py`, `db/init/03_rrc.sql`
- API extras: alerts, billing, energy endpoints (any files supporting these)
- Web extras: `NearbyEnergy` component, GWDB chips/labels not backed by SDR
- Infra/docs unrelated to SDR MVP (CDN/vector tiles, advanced sprints)

### Create archive folders (dry run — do not execute yet)
```
mkdir -p archive/data/sources archive/data/transforms archive/db/init archive/apps/api archive/apps/web archive/docs
```

### Suggested git moves (use in a feature branch)
Run from repo root (replace paths as needed if some files don’t exist):
```
git checkout -b mvp-sdr

# GWDB
git mv data/sources/twdb_gwdb*.py archive/data/sources/ 2>/dev/null || true
git mv data/transforms/link_sdr_gwdb*.py archive/data/transforms/ 2>/dev/null || true
git mv db/init/02_gwdb*.sql archive/db/init/ 2>/dev/null || true

# RRC
git mv data/sources/rrc_*.py archive/data/sources/ 2>/dev/null || true
git mv db/init/03_rrc.sql archive/db/init/ 2>/dev/null || true

# API extras (only if present)
git mv apps/api/app/*alerts* archive/apps/api/ 2>/dev/null || true
git mv apps/api/app/*billing* archive/apps/api/ 2>/dev/null || true
git mv apps/api/app/*energy* archive/apps/api/ 2>/dev/null || true

# Web extras (only if present)
git mv apps/web/src/components/NearbyEnergy.astro archive/apps/web/ 2>/dev/null || true

# Optional: move non‑MVP docs
git mv docs/sprints archive/docs/ 2>/dev/null || true
```

### After moving, do this
- Search for broken imports/usages (grep for moved module names)
- Confirm API only exposes MVP endpoints
- Rebuild web; remove buttons that call archived endpoints/components
- Update README to “SDR‑only MVP”

### Rollback plan
- Every move is in git history. To undo: `git checkout main` or `git revert` the move commit.

### Notes
- Archiving avoids deleting work while reducing cognitive load
- Once SDR is solid, you can bring GWDB/RRC back from `archive/` incrementally


