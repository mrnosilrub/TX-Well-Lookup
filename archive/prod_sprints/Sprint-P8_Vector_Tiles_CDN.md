## Sprint P8 — Vector Tiles & CDN

### Goal
Serve scalable custom map layers (PMTiles) via CDN with cache-busting.

### Outcomes
- Nightly PMTiles generated and uploaded; web consumes tiles via CDN URL

### You — Manual Tasks
- Choose Cloudflare CDN; configure origin to Cloudflare R2 and TLS (per providers.md).

### Agent B — Data Pipeline Tasks
- Generate PMTiles for wells/clusters nightly; version filenames (e.g., `wells-<yyyymmdd>.pmtiles`).
- Upload to storage `tiles/` path.

### Agent C — Web Tasks
- Switch to the CDN tile URL; add versioned query param for cache-busting.

### Agent D — DevOps Tasks
- Set CDN cache rules; invalidate or version on updates; monitor bandwidth/cost.

### Acceptance
- Map renders from your tile source; updates propagate after new version upload.

### Verification
```bash
curl -I https://tiles.<domain>/tiles/wells-<yyyymmdd>.pmtiles
```


