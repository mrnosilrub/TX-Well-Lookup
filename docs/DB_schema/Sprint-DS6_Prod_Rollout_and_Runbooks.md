## Sprint DS6 — Production Rollout and Runbooks

### Goal
Roll out the finalized schema and ETL to production with clear runbooks for deploy, verify, and rollback.

### Rollout
- Apply DDL: run “DB Apply & Verify (P1)”
- Run SDR Snapshot & Inspect (optional) and archive manifest in R2
- Run ETL Nightly (manually) for initial full load

### Verify
- Run QA metrics (DS5 queries) against prod
- Confirm `/v1/search` returns database-backed items without errors

### Runbooks
- Re-run ETL: how to trigger, expected durations, interpreting logs
- Recovery: if a step fails, how to resume; how to rollback child tables (truncate/reload)
- Schema migrations: versioned DDL, how to apply safely

### Acceptance
- Prod DB has expected row counts and coverage
- API reads are stable; alerts set for failures


