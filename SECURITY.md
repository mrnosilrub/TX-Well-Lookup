## Security Policy and Access Control

This repository follows a least‑privilege, environment‑scoped security model. No secrets are committed to the repository. Production access is gated and auditable.

### MFA

- Require multi‑factor authentication for: GitHub organization, cloud/provider consoles, billing, storage, DNS/TLS, and email/notification providers.
- Enforce MFA for all owner/admin accounts. Prefer hardware keys where possible.

### Roles and Access

- Use role‑based access control (RBAC). Limit owner/admin roles to the minimum set of people.
- Prefer service roles or service users for automation with the minimal scopes required.
- Break‑glass access should be time‑bound, audited, and rotated immediately after use.

### Secrets Management

- Do not store secrets in the codebase. Use provider secret managers (e.g., AWS SSM/Secrets Manager, platform vaults) and surface to CI via environment‑scoped secrets.
- Prefer federated identity (OIDC from GitHub Actions) to assume roles and mint short‑lived credentials where supported. Fall back to long‑lived keys only if necessary, and rotate regularly.
- Follow the naming and storage guidance in `docs/infra/providers.md` (Secrets Catalog). Typical env vars include `DATABASE_URL`, `PUBLIC_API_URL`, `STORAGE_*`, `EMAIL_*`, and `STRIPE_*`.

### CI/CD and Environments

- Restrict token permissions in CI jobs to the minimum needed.
- Protect the `prod`/`production` environment with required reviewers and manual approvals for deploys.
- Use separate secrets per environment (dev, staging, prod). Avoid organization‑level secrets unless strictly necessary.

### Incident Response and Rotation

- Rotate credentials on suspected exposure, personnel changes, or per provider policy (90 days typical for long‑lived keys).
- Revoke tokens/keys immediately upon compromise and audit usage logs.
- Document rotations and ownership in `docs/infra/providers.md`.


