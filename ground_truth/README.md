# Ground Truth Schema (1:1 SDR mirror)

This module loads the nightly SDR zip into PostgreSQL with exact, 1:1 fidelity:
- One table per .txt file
- Table name = source filename (without extension), quoted (e.g., "WellData")
- Columns = the .txt header row, quoted, stored as TEXT
- No transforms, no coercions. Duplicate headers get suffixed (_2, _3, ...). Long headers are truncated safely, originals preserved via COMMENTs.

Default schema name: ground_truth

Run locally
```bash
python3 ground_truth/loader/load_ground_truth.py \
  --zip /path/to/sdr.zip \
  --database-url "$DATABASE_URL" \
  --schema ground_truth
```

GitHub Action
- Use: Actions → Ground Truth Load (manual)
- Inputs: env (dev/staging/prod), schema (default ground_truth)
- Secrets: DATABASE_URL, SDR_ZIP_URL (or RAW_SDR_* with STORAGE_* for S3-compatible)

Verification
- Tables: SELECT table_name FROM information_schema.tables WHERE table_schema='ground_truth' ORDER BY 1;
- Counts: compare row counts vs. line counts (minus header) in each .txt

Notes
- This is a staging layer for exact capture; product models will be derived later.
