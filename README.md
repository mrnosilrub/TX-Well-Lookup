## TX Well Lookup — Dev Notes

Quick commands:

```bash
# Generate raw schema catalog (docs/SCHEMA.md)
python3 ground_truth/tools/generate_schema_md.py --database-url "$DATABASE_URL" --schema ground_truth --out docs/SCHEMA.md

# Compute SDR as-of date (docs/AS_OF.md)
python3 ground_truth/tools/compute_as_of.py --database-url "$DATABASE_URL" --schema ground_truth --out docs/AS_OF.md

# CI smoke (connectivity + counts)
python3 scripts/ci_smoke_db.py --database-url "$DATABASE_URL" --schema ground_truth
```


