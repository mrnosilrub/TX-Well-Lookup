## Sprint P10 — Launch Readiness & Rollback

### Goal
Validate end-to-end, prepare documentation, and define rollback procedures.

### Outcomes
- Smoke/load tests pass; DNS cutover complete; rollback plan ready

### You — Manual Tasks
- Set final DNS for web and API; confirm SSL; schedule launch window.
- Approve production deploy in CI when ready.

### Agent D — DevOps Tasks
- Take a fresh DB snapshot; validate restore playbook on staging.
- Finalize CI environment approvals and release tagging.

### Agent A/B/C — App Tasks
- Smoke tests:
  - `/health`, `/v1/search`, `/v1/wells/{id}` return as expected.
  - Report creation → presigned URLs download.
  - Optional: billing (test mode) and alert simulation.
- Load test key endpoints at realistic limits.

### Acceptance
- All checks green; backup ready; rollback documented.

### Verification
```bash
curl -s https://api.<domain>/health
curl -s "https://api.<domain>/v1/search?q=Travis&limit=10" | jq .
```


