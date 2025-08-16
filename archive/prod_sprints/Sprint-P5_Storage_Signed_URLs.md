## Sprint P5 — Object Storage & Signed URLs (Reports)

### Goal
Generate report artifacts, upload to storage, and return presigned download URLs.

### Outcomes
- Report creation returns `report_id` and later presigned `pdf_url`/`zip_url`
- Storage uses least-privileged credentials; URLs expire quickly

### You — Manual Tasks
- Create per-env bucket(s): `txwl-reports-<env>` on Cloudflare R2 (per providers.md).
- Enable encryption at rest; set lifecycle (e.g., IA after 30 days).
- Store credentials in API platform secrets: `S3_BUCKET`, `S3_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and optional `S3_ENDPOINT` for R2.

### Agent A — Backend Tasks
- Replace report stubs:
  - `POST /v1/reports`: enqueue job; return `report_id`.
  - `GET /v1/reports/{id}`: return status and short-lived presigned URLs.
- Add storage client helper for uploads and signing.

### Agent B — Data Pipeline Tasks
- Add `data/bundles/bundle_builder.py` to build CSV/GeoJSON/manifest around a well radius.
- Render HTML to PDF (e.g., Playwright); zip bundle; upload to storage.

### Agent D — DevOps Tasks
- Optional worker service or in-API background task queue.
- Ensure credentials are least-privilege (R2 bucket-only access); rotate periodically.

### Acceptance
- Creating a report yields downloadable PDF/ZIP via expiring URLs.

### Verification
```bash
curl -s -X POST https://api.<domain>/v1/reports | jq .
curl -s https://api.<domain>/v1/reports/<id> | jq .
```


