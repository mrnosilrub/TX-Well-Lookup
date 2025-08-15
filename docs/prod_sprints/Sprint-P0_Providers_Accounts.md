## Sprint P0 — Providers & Accounts

### Goal
Decide platforms, create accounts, and prepare secure access for later automation.

### Outcomes
- Chosen providers with accounts and billing enabled
- Programmatic access established (API tokens/keys)
- Inventory of providers, envs, and secrets documented

### Prerequisites
- GitHub org/repo access
- Business email for provider accounts

### You — Manual Tasks
- Choose providers (recommended first choices):
  - Database: Neon, CrunchyBridge, or AWS RDS (Postgres 15+)
  - API runtime: Render, Railway, Fly.io, or AWS ECS Fargate
  - Object storage: S3 (AWS) or Cloudflare R2
  - DNS/TLS: Cloudflare (preferred) or registrar DNS
  - Billing: Stripe (start in test mode)
  - Notifications: Postmark/SendGrid/SES or Slack webhook
- Create org/project accounts; enable billing; add MFA for owner/admin.
- Create team/service users as needed; restrict console access to least-privilege.
- Generate API tokens/keys for CI where applicable.

### Agent D — DevOps Tasks
- Create `docs/infra/providers.md` enumerating:
  - Providers, regions, service tiers, SLAs
  - Contacts/owners and escalation paths
  - Secrets catalog: names, locations (platform vault/SSM), rotation policy
  - Environment matrix: dev, staging, prod (URLs, domains)
- Add a `SECURITY.md` note on MFA and access control expectations.

### Deliverables
- Provider inventory doc and secrets catalog committed
- Credentials stored in platform vaults (no secrets in repo)

### Acceptance
- All accounts active; test API calls work with tokens (e.g., list buckets/DBs)

### Verification
- Confirm MFA enforced for owners
- Confirm at least one non-owner can access via role-based policy


