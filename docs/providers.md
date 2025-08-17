## Providers & Environments Inventory (Sprint P0)

This document tracks provider selections, ownership, secrets, and environment configuration. Fill in the TBD fields once providers are chosen.

### Provider Choices

| Category | Provider | Account/Org | Region | Tier/Plan | SLA/Notes | Status |
|---|---|---|---|---|---|---|
| Database | Neon | You | TBD | Starter | Postgres 15+. PostGIS + pg_trgm required | Active (branches: dev/staging/prod) |
| API Runtime | Render | You | TBD | Starter | Prefer zero-downtime deploys | Active (services: dev/staging/prod) |
| Object Storage | Cloudflare R2 | You | auto | Starter | For reports; S3-compatible signed URLs | Active (buckets: dev/staging/prod) |
| DNS/TLS | Cloudflare | You | Global | Pro | DNS + TLS for domain and APIs | Active |
| Billing | Stripe | You | N/A | Test mode first | PCI handled by provider | Planned (add test keys) |
| Notifications | Postmark | You | TBD | Starter | Domain signing (DKIM) | Active (domain verified) |

### Contacts & Ownership

| Area | Owner (name/email) | Backup | Escalation Path |
|---|---|---|---|
| Platform (overall) | hello@txwelllookup.com | TBD | Provider support → Internal escalation |
| Database | hello@txwelllookup.com | TBD | Neon support → Internal escalation |
| API Runtime | hello@txwelllookup.com | TBD | Render support → Internal escalation |
| Storage | hello@txwelllookup.com | TBD | Cloudflare support → Internal escalation |
| DNS/TLS | hello@txwelllookup.com | TBD | Cloudflare support |
| Billing | hello@txwelllookup.com | TBD | Stripe support |
| Notifications | hello@txwelllookup.com | TBD | Postmark support |

### Environment Matrix

| Env | Domain | App URL | API URL | Storage Bucket/Path | DB (host/db) | Notes |
|---|---|---|---|---|---|---|
| dev | txwelllookup.com | (Planned) https://dev.txwelllookup.com | https://api.dev.txwelllookup.com | r2: txwl-reports-dev | Neon: dev branch (conn string in env) | Internal testing |
| staging | txwelllookup.com | (Planned) https://staging.txwelllookup.com | https://api.staging.txwelllookup.com | r2: txwl-reports-staging | Neon: staging branch (env) | Approval-gated deploys |
| prod | txwelllookup.com | https://www.txwelllookup.com | https://api.txwelllookup.com | r2: txwl-reports-prod | Neon: prod branch (env) | Customer-facing |

### Service endpoints

- API (Render hosts):
  - Dev: https://txwl-api-dev.onrender.com → Custom: https://api.dev.txwelllookup.com
  - Staging: https://txwl-api-staging.onrender.com → Custom: https://api.staging.txwelllookup.com
  - Prod: https://txwl-api-prod.onrender.com → Custom: https://api.txwelllookup.com
- Web (GitHub Pages):
  - Custom domain: https://www.txwelllookup.com (CNAME to GitHub Pages)
  - Apex redirect: txwelllookup.com → www.txwelllookup.com (301 via Cloudflare rule)

### Secrets Catalog (names, locations, rotation)

Do not commit secrets to the repo. Prefer ephemeral OIDC/role assumption where available; otherwise, store in provider vaults and surface to CI via environment-scoped secrets.

| Secret Purpose | Env Var Name | Scope (dev/staging/prod) | Store (Vault/Manager) | Surface to CI (where) | Rotation Policy |
|---|---|---|---|---|---|
| Database connection (Neon) | `DATABASE_URL` | All | Provider vault/TBD | GitHub Environment Secret | Rotate on role/user change; 90 days typical |
| API CORS allowlist | `ALLOWED_ORIGINS` | All | N/A (non-secret) | GitHub Environment Var | Update with domain changes |
| Public API base URL | `PUBLIC_API_URL` | All | N/A (non-secret) | GitHub Environment Var | Update with deploy target |
| Object storage bucket (R2) | `STORAGE_BUCKET` | All | N/A (non-secret) | GitHub Environment Var | On infra changes |
| Object storage endpoint (R2 S3) | `STORAGE_ENDPOINT` | All | N/A (non-secret) | GitHub Environment Var | On infra changes |
| Object storage region | `STORAGE_REGION` | All | N/A (non-secret) | GitHub Environment Var | e.g., `auto` |
| Object storage access key | `STORAGE_ACCESS_KEY_ID` | All | Provider vault/TBD | GitHub Environment Secret | 90 days or on exposure |
| Object storage secret key | `STORAGE_SECRET_ACCESS_KEY` | All | Provider vault/TBD | GitHub Environment Secret | 90 days or on exposure |
| Email provider (Postmark) token | `POSTMARK_SERVER_TOKEN` | All | Provider vault/TBD | GitHub Environment Secret | 90 days or on exposure |
| Email provider name | `EMAIL_PROVIDER` | All | N/A (non-secret) | GitHub Environment Var | `postmark` |
| Stripe API key (test/prod) | `STRIPE_SECRET_KEY` | staging/prod | Provider vault/TBD | GitHub Environment Secret | Provider policy (rotate on exposure) |
| Stripe webhook secret | `STRIPE_WEBHOOK_SECRET` | staging/prod | Provider vault/TBD | GitHub Environment Secret | Provider policy |

Add additional rows as providers are chosen.

### Notes

- Enforce least privilege: scope tokens to environment and service.
- Prefer short‑lived credentials via OIDC if provider supports it; otherwise, use provider vaults and time‑bound keys.
- See `SECURITY.md` for access control, MFA, and incident response.