## Sprint DS4 — ETL Orchestration and Logging

### Goal
Orchestrate a complete SDR ingest (all files), idempotent, with per-file row counts and durations printed in logs.

### Execution order
1) WellData.txt → `well_reports` base rows
2) WellCompletion.txt → enrich `depth_ft`, `date_completed`
3) Child tables:
   - WellBoreHole → `well_boreholes`
   - WellCasing → `well_casings`
   - WellFilter → `well_filters`
   - WellSealRange → `well_seal_ranges`
   - WellPackers → `well_packers`
   - WellStrata → `well_strata`
   - WellLevels → `well_levels`
   - WellTest → `well_test`
   - WellInjuriousConstituent → `well_injurious_constituent`
4) WellLithology → `well_lithology` (last; largest)
5) Plug family:
   - PlugData → `plug_reports`
   - PlugBoreHole → `plug_boreholes`
   - PlugCasing → `plug_casing`
   - PlugRange → `plug_range`

### Orchestration
- Implement functions per file (batching with `execute_batch`, page_size=1000)
- Idempotency: `ON CONFLICT` on PKs; optional `source_row_hash`
- Validate and coerce types before upsert
- Geometry only when valid lat/lon within TX bounds

### Logging
- For each step print: `name=WellData rows=NN time=SS.SS` (counts & durations)
- At end print aggregate: `total_rows_by_table={...}`

### Failure policy
- Fail fast on I/O or DDL errors; continue on row-level parse errors with a counter
- Emit a summary of skipped rows per file with reasons (truncated in logs)

### Acceptance
- One run loads all tables; re-running makes minimal changes
- Logs include per-file counts/durations (fulfills scheduling doc requirement)


