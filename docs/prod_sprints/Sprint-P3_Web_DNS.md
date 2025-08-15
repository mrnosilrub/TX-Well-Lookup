## Sprint P3 — Frontend Deployment & DNS

### Goal
Publish the Astro site and wire it to the API via environment configuration and DNS.

### Outcomes
- Web deployed to Pages (or Cloudflare Pages)
- DNS and TLS configured for web and API subdomains

### You — Manual Tasks
- Configure Pages project:
  - Build directory: `apps/web` → output `dist/`.
  - Set build-time env: `PUBLIC_API_URL=https://api.<domain>/`, `PUBLIC_BASE_PATH=/` (custom domain) or `/<repo>/` (project pages).
- Configure DNS:
  - `txwl.<domain>` → Pages CNAME.
  - `api.txwl.<domain>` → API service CNAME; enable TLS and HSTS.

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


