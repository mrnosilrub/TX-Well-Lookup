## TX Well Lookup — Dev Notes

Quick commands:

```bash
# Generate raw schema catalog (docs/SCHEMA.md)
python3 ground_truth/tools/generate_schema_md.py --database-url "$DATABASE_URL" --schema ground_truth --out docs/SCHEMA.md

# CI smoke (connectivity + counts)
python3 scripts/ci_smoke_db.py --database-url "$DATABASE_URL" --schema ground_truth

# Apply app views (Milestone 1)
psql "$DATABASE_URL" -f scripts/app_apply_views.sql

# Verify view and sample rows
psql "$DATABASE_URL" -f scripts/app_verify.sql

# Run API locally (Milestone 2)
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="$DATABASE_URL"
uvicorn app:app --reload --port 8000
```


### Web App (Milestone 3–4)

Run the Astro dev server:

```bash
cd apps/web
npm install
npm run dev
```

UI features:
- Search + filters (county, depth, date, optional radius around map center)
- Map pins synchronized with the results list
- Dark/light theme toggle
- As‑of date shown in header/footer (from API /v1/meta)
- Export CSV (Milestone 4):
  - Button in header labeled “Export CSV”
  - Exports columns: `id, owner, county, lat, lon, depth_ft, date_completed`
  - Uses current filters (including radius) and downloads a timestamped filename

