## TX Well Lookup — SDR-Only MVP Scope and Go-To-Market

### Purpose
Deliver a focused, marketable MVP that “consumerizes” the TWDB Statewide Driller’s Report (SDR): a fast, modern way to search, map, and export well information with clear attribution and disclaimers. This narrows scope to SDR only (no GWDB/RRC) to de‑risk delivery and validate demand quickly.

### Who buys this (priority segments)
- Environmental due diligence firms and consultants
- Groundwater/hydrogeology consultants; civil engineering firms
- Water well drillers (small–mid size)
- Real estate appraisers, inspectors, title/escrow teams
- Utilities/public works/county planning staff
- Agriculture/ranch management, land developers
- Insurers/underwriters; spill remediation teams; GCDs (as API/data service)

### Core jobs-to-be-done (use‑cases)
- Property due diligence: identify nearby wells, depths, completion dates, plugging status; produce client‑ready reports (PDF/CSV)
- Pre‑design reconnaissance: estimate likely drilling depths and construction from nearby completions
- Compliance/permitting prep: compile standardized nearby well context
- Risk screening: check buffers/setbacks from wells for planned activities
- Spill/contamination triage: find wells within a radius for notification/monitoring
- Portfolio screening: batch assess many parcels for well proximity/depth

### Why they buy (value prop)
- Saves 20–60 minutes per site vs. legacy portals/manual exports
- Reduces missed wells across boundaries with radius search
- Standardizes deliverables (PDF/CSV) for clients/regulators
- Clear source attribution and “as‑of” timestamps for auditability

### Data source and usage guidance (ship this in product)
- Attribution (show in footer, About, and report footers):
  - “Contains data from the Texas Water Development Board (TWDB) Statewide Driller’s Report (SDR). TWDB provides this data as‑is, without warranty, and does not endorse this product.”
- Accuracy/non‑warranty:
  - “Information is provided ‘as is’ and may contain errors or omissions. Not a substitute for official records or site surveys. Verify with original source and qualified professionals.”
- Non‑endorsement:
  - “Use of TWDB data does not imply endorsement by TWDB.”
- As‑of/refresh cadence:
  - Show: “SDR snapshot: YYYY‑MM‑DD; updated nightly when available.”
  - API headers: `X-Data-Source: TWDB-SDR`, `X-Data-As-Of: <date>`, `X-Data-Refresh: nightly`.
- PII/owner names:
  - Display minimally to identify records; require authentication for raw exports.
  - “Owner names appear as part of public records. Do not use contact info for unlawful or unsolicited marketing.”
- Redistribution/API terms:
  - Allow derived works with attribution and disclaimers; prohibit implying TWDB endorsement.
- Interpretation guidance:
  - Show “Location Confidence” when lat/lon is coarse/missing; enforce TX bounds; show units explicitly (feet).

### MVP features (deliverable scope)
- Search + Map (web)
  - Input: address or point; radius filter; county filter; depth range; date range
  - Results list + pins with: `sdr_id`, owner_name, county, lat/lon, depth_ft, date_completed
  - “As‑of” and attribution visible; location confidence badge
- Export
  - One‑click PDF/CSV with map, table, disclaimers, and source
  - Batch export (up to 50 addresses) → ZIP of PDFs/CSVs via email link
- Accounts & Billing (light)
  - Auth + usage caps; solo/team plans; per‑report overage
  - Admin view for usage metrics and simple refunds
- API (optional v1)
  - `/v1/search`, `/v1/wells/{id}`; documented limits and headers; keys + rate limiting

Out‑of‑scope for MVP (post‑MVP)
- GWDB enrichment and RRC overlays
- Advanced analytics; parcel overlays; complex alerting
- Very large batch (1000+) and enterprise SSO

### Pricing hypotheses (to validate)
- Pros (consultants/drillers): $49–$99/mo solo; $199–$399/mo team; $1–$3/report overage
- Real estate/title: $19–$29 one‑off report; small team plans
- API: metered (e.g., $0.01–$0.05/record) with monthly minimum

### Validation plan
- 10–15 prospect interviews (environmental, drillers, engineers) → paid pilot offers
- Landing page + demo + report sample; collect waitlist; A/B price packaging
- Ads experiments (search/social) targeting “water well report Texas”, “nearby wells depth”
- Offer 3 discounted pilots (60 days); success: ≥N reports/week, time saved, conversion to paid

### Technical scope (data + platform)
- SDR ingest: end‑to‑end inspection → schema → ETL → QA (see docs/DB_schema)
  - Inspect: CI workflow fetches full ZIP, stages in R2, captures headers and first N lines per `.txt`; builds manifest.json
  - Schema: `well_reports` core; typed child tables for WellBoreHole, WellCasing, WellFilter, WellSealRange, WellPackers, WellStrata, WellLevels, WellTest, WellInjuriousConstituent, WellLithology; PlugData family
  - ETL: idempotent upserts; header aliasing via normalized keys; YMD date parsing; TX bounds on geom; batch via `execute_batch`
  - QA: coverage metrics (total, with_geom, with_depth), child table counts, top counties, out‑of‑bounds audit
- API: FastAPI endpoints; CORS locked to web origin; gzip/ETag; structured logs; pagination + keyset; bbox/radius filters
- Web: Astro static site; prod API URL; graceful errors; attribution and “as‑of”; report exporter (PDF/CSV)
- Ops: nightly ETL with counts/durations; alerts on anomalies; backups and R2 lifecycle policies

### Risks & mitigations
- Header drift / field variations → Inspect-first + alias catalogue + alerts on unknown headers
- Large files (lithology) → staged last; batching; potential partitioning
- Sparse geom/depth in some rows → surface coverage stats; location confidence; continuous ETL improvement
- Consumer CAC risk → prioritize B2B pilots and direct outreach; keep consumer flow as add‑on
- Data liability/PII → clear disclaimers; limited PII exposure; takedown contact; compliance in Terms

### Success metrics
- Activation: time to first report < 5 minutes; at least 3 paid pilots completed
- Usage: ≥ 10 reports/week across pilot teams; ≥ 60% repeat weekly users
- Data coverage: ≥ 70% of `well_reports` with valid geom; ≥ 60% with depth_ft (initial target)
- Reliability: nightly ETL success ≥ 29/30 days; API p95 < 300 ms for `/v1/search`

### Roadmap (post‑MVP)
- GWDB enrichment (aquifer, gwdb_depth_ft) and biasing in search
- RRC permits/wellbores overlay for “nearby energy” pins and buffer checks
- Batch 1000+; enterprise features (SSO, audit logs); parcel overlays
- Advanced alerting (geofenced, webhook); internal dashboards

### Deliverables checklist
- SDR Snapshot & Inspect workflow (CI) + R2 manifest and samples
- DDL: finalized SDR schema (`well_reports` + child tables)
- ETL: idempotent loader with counts/durations per file; QA queries documented
- API: `/v1/search`, `/v1/wells/{id}`, docs, and rate limiting
- Web: search/map, filters, PDF/CSV export, attribution + as‑of
- Terms & Usage page: attribution, disclaimers, PII policy, rate limits, contact


