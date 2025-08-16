## Sprint P3 — Frontend Deployment & DNS

### Goal
Publish the Astro site and wire it to the API via environment configuration and DNS.

### Outcomes
- Web deployed to Pages (or Cloudflare Pages)
- DNS and TLS configured for web and API subdomains

### You — Manual Tasks
- Configure GitHub Pages project (per `docs/infra/providers.md`):
  - Build directory: `apps/web` → output `dist/`.
  - Set build-time env per environment:
    - Dev: `PUBLIC_API_URL=https://api.dev.txwelllookup.com`, `PUBLIC_BASE_PATH=/`
    - Staging: `PUBLIC_API_URL=https://api.staging.txwelllookup.com`, `PUBLIC_BASE_PATH=/`
    - Prod: `PUBLIC_API_URL=https://api.txwelllookup.com`, `PUBLIC_BASE_PATH=/`
- Configure DNS:
  - `www.txwelllookup.com` → GitHub Pages CNAME. Apex `txwelllookup.com` → 301 to `www` (Cloudflare rule).
  - `api.dev.txwelllookup.com` → Render dev service CNAME.
  - `api.staging.txwelllookup.com` → Render staging service CNAME.
  - `api.txwelllookup.com` → Render prod service CNAME. Enable TLS and (optional) HSTS on API platform.

### Agent C — Web Tasks
- Confirm all API calls use `PUBLIC_API_URL` (already in `Search.astro`).
- Add or verify a status widget that pings `/health` and shows status.
- Ensure fallback to local stub is disabled in production builds.

### Agent D — DevOps Tasks
- CI: build on `main` and deploy to Pages; cache npm via `apps/web/package-lock.json`.
- Protect production environment with approvals.

### Acceptance
- Visiting the site shows live API data; status widget reads "ok".

### Verification
```bash
curl -I https://txwl.<domain>/
curl -s https://api.txwl.<domain>/health
```


