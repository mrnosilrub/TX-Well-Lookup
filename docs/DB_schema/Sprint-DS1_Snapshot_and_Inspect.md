## Sprint DS1 — SDR Snapshot & Inspect (No Data in Repo)

### Goal
Safely fetch the full SDR ZIP, extract headers and the first N lines of each `.txt`, and stage artifacts in R2 + CI without committing data. Produce a manifest to drive schema and ETL design.

### Inputs
- Secrets (per environment):
  - `STORAGE_ACCESS_KEY_ID`, `STORAGE_SECRET_ACCESS_KEY`, `STORAGE_ENDPOINT`
  - `SDR_ZIP_URL` (official TWDB ZIP)
- Vars: `RAW_SDR_BUCKET`, `RAW_SDR_PREFIX`
- Dispatch inputs: `env` (dev|staging|prod), `sample_lines` (default 200)

### Steps
1) Create a GitHub Actions workflow: “SDR Snapshot & Inspect”
   - Concurrency: `sdr-inspect-${{ inputs.env }}`
   - Checkout
   - Install AWS CLI
   - Make `data/raw_data/SDRDownload/SDRDownload`
   - Download ZIP with retries to `data/raw_data/sdr.zip`
   - Compute `sha256sum` → record
   - `unzip -n data/raw_data/sdr.zip -d data/raw_data/`
2) Summarize `.txt` files under `data/raw_data/SDRDownload/SDRDownload/`
   - For each `.txt`:
     - size (bytes), `wc -l` count (tolerant to huge files)
     - sha256
     - header fields: read first line, split on `|`
     - sample lines: next `sample_lines` lines into `samples/heads/<name>.head.txt`
   - Build `manifest.json` with: fetched_at, zip_sha256, files[] entries containing name, size_bytes, line_count, sha256, header_fields[], sample_path
3) Upload to R2 at `s3://${RAW_SDR_BUCKET}/${RAW_SDR_PREFIX}/snapshots/${TIMESTAMP}/`
   - `sdr.zip`, `manifest.json`, `samples/heads/*.head.txt`
4) Upload CI artifacts: `manifest.json`, `samples/heads/*`
5) Job Summary (Markdown table): file, size, lines, header columns

### Guardrails
- Do not log raw data beyond headers and the first N lines. Never print secrets.
- Use latin-1 when reading `.txt` for preview to avoid decode errors.
- Fail clearly if ZIP is missing or corrupt.

### Acceptance
- R2 snapshot path contains ZIP + manifest + samples.
- CI artifacts present.
- Job summary lists files and headers.


