## Sprint P6 — Billing (Credits) & Paywall Enforcement

### Goal
Charge for report generation using a credits model; Stripe in test mode.

### Outcomes
- Checkout creates credit grants; webhook processes events; credits enforced on report creation

### You — Manual Tasks
- Setup Stripe (test): product/price for credits.
- Configure webhook endpoint (API URL) and store webhook secret in API platform.

### Agent A — Backend Tasks
- Endpoints:
  - `POST /billing/checkout` → Stripe checkout session; returns URL/id.
  - `POST /billing/webhook` → verify signature; on success: insert into `credit_grants`.
- Tables:
  - `credit_grants(user_id, amount, source, created_at)`
  - `credit_spends(user_id, amount, report_id, created_at)`
- Enforce credits in `POST /v1/reports`; 402 when insufficient; record spend on success.

### Agent C — Web Tasks
- Add UI to purchase credits; show current balance; gate the "Generate Report" button.

### Agent D — DevOps Tasks
- Store `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` securely.
- Add CI/CD env separation for staging vs production keys.

### Acceptance
- 0 credits → 402 on report; after checkout (test) → success and spend recorded.

### Verification
```bash
curl -s -X POST https://api.<domain>/billing/checkout | jq .
stripe listen --forward-to https://api.<domain>/billing/webhook # staging
```


