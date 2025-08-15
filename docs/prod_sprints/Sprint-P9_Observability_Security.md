## Sprint P9 — Observability, SLOs & Security Hardening

### Goal
Gain runtime visibility, define SLOs, and reduce attack surface.

### Outcomes
- Metrics, logs, and alerts configured; CORS/networking locked down

### You — Manual Tasks
- Define SLOs (availability, p95 latency). Choose alert channels.

### Agent D — DevOps Tasks
- Metrics/alerts: error rate, p95 latency, CPU/mem; uptime check for API.
- Centralize logs (platform or ELK); set retention.
- Enforce: HTTPS-only, HSTS, CORS restricted, DB not public, secret rotation policy.

### Agent A — Backend Tasks
- Add request IDs and structured logs for requests/errors; include latency.

### Acceptance
- Alerts trigger on induced failures; security checks pass.

### Verification
```bash
ab -n 200 -c 20 https://api.<domain>/health
```


