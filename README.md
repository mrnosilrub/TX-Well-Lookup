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
```


