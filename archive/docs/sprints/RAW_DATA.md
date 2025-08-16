# Raw Data Layout and R2 Upload (SDR)

This project uses the TWDB SDR pipe-delimited download as the raw source for well reports.

## Local directory layout (not committed)

Place the download here (keep out of git; see .gitignore):

```
data/
  raw/
    sdr/
      SDRDownload/
        WellData.txt
        WellCompletion.txt
        WellBoreHole.txt
        WellCasing.txt
        # ... other tables from SDRDownload
```

Notes:
- We no longer keep shapefiles in this repo; address + optional lat/lon from WellData are sufficient for current goals.
- The nightly job looks in `data/raw/SDRDownload` first; it will also detect `data/raw_data/SDRDownload/SDRDownload` for backward compatibility.

## Upload to Cloudflare R2 (recommended)

Create a bucket (example: `txwl-raw`) and upload the SDR directory to a prefix:

- Bucket: `txwl-raw`
- Prefix: `sdr/SDRDownload/`

### CLI (using AWS-compatible API)

Prereqs:
- STORAGE_ENDPOINT = `https://<account_id>.r2.cloudflarestorage.com`
- STORAGE_ACCESS_KEY_ID / STORAGE_SECRET_ACCESS_KEY
- Install AWS CLI: `pip install awscli` or use your platform’s cli

Commands (from repo root):

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=auto
export STORAGE_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com

# create bucket once (skip if exists)
# aws s3 mb s3://txwl-raw --endpoint-url "$STORAGE_ENDPOINT"

# sync local raw data up to R2
aws s3 sync data/raw/SDRDownload s3://txwl-raw/sdr/SDRDownload \
  --endpoint-url "$STORAGE_ENDPOINT" --size-only --no-progress
```

## Configure CI to use R2

In GitHub Environments (dev/staging/prod):
- Variables:
  - RAW_SDR_BUCKET = `txwl-raw`
  - RAW_SDR_PREFIX = `sdr/SDRDownload`
- Secrets:
  - STORAGE_ACCESS_KEY_ID, STORAGE_SECRET_ACCESS_KEY
  - STORAGE_ENDPOINT

The nightly ETL workflow will download from R2 before running when variables are set.
