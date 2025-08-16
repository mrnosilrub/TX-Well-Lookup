## SDR‑Only MVP — Product Wireframe (Beginner‑Friendly)

This document explains, in plain language, what the first version of the product does, what each screen looks like, and how a non‑technical user moves through it. It also shows what data appears, where it comes from, and exactly what buttons do.

### Scope (what’s in, what’s out)
- In: Texas SDR search and map, filters, exports (PDF/CSV), small batch (≤ 50 addresses), basic account + billing, usage/attribution messaging
- Out (for now): GWDB enrichment, RRC overlays, very large batch, advanced alerting, enterprise SSO

### Personas (who uses it)
- Environmental/real‑estate pros: need a quick, reliable nearby‑wells report for a property
- Drillers and consultants: want nearby depths + completion dates to scope jobs
- Title/escrow: need a printable summary as part of due diligence

## Information Architecture (top‑level navigation)
- Home: marketing summary + link to App
- App: Search + Map (main workspace)
- Reports: Download recent PDF/CSV exports (optional shortcut from App)
- Account: Sign in, plan/usage, billing
- About: Data sources, disclaimers, “as‑of” date, contact

## Screen 1 — Home (public landing)
- Goal: explain value in one sentence and get users into the App
- Sections:
  - Hero: “Texas well lookups in minutes” + a single CTA button: “Open App”
  - How it works: 3 steps — Search → Filter → Export
  - Sample report: links to a sample PDF and CSV (opens in new tab)
  - Trust: source attribution + “as‑of” date
  - Footer: disclaimers, contact, terms/privacy

Copy (you can paste):
- Hero: “Search SDR wells by address or point, filter by depth/date, and export client‑ready PDF/CSV instantly.”
- Attribution: “Contains data from the Texas Water Development Board (TWDB) Statewide Driller’s Report (SDR). TWDB provides this data as‑is, without warranty, and does not endorse this product.”
- As‑of: “SDR snapshot: YYYY‑MM‑DD; updated nightly when available.”

## Screen 2 — App (Search + Map)
- Goal: let users find nearby wells around an address/point, see results on a map and list, then export

Layout (left → right):
- Left column: Filters panel
  - Search input (address or place)
  - Radius slider: 0.25, 0.5, 1, 2, 5 miles
  - Date range: completion date (from/to)
  - Depth range: min/max (feet)
  - County: dropdown (optional)
  - Buttons: Apply filters, Reset
  - As‑of badge: “As‑of YYYY‑MM‑DD”
- Center: Map
  - Base map (streets)
  - Pins for wells (blue dots)
  - Fit to results button
  - Clicking a pin opens a Well card (small popup)
- Right column: Results list
  - Columns: Well ID, Owner, County, Depth (ft), Completed (date)
  - Pagination or “Load more”
  - Row click: focuses map + opens the same Well card
  - Export: top‑right — “Export PDF” and “Export CSV”

Well card (popup/drawer):
- Fields: Well ID, Owner, County, Depth (ft) or “—”, Completed (date) or “—”, Coordinates
- Location confidence: “High / Medium / Low” depending on source accuracy
- Action: “Add to report selection” (optional multi‑select)

Empty, loading, error states:
- Empty: “Search by address or click on the map to get started.”
- Loading: spinner + “Finding nearby wells…”
- No results: “No wells found. Try increasing radius or removing filters.”
- API error: “We couldn’t load results. Please try again or use sample data.” (show retry)

What appears in results (exact fields):
- Well ID: SDR sdr_id
- Owner: SDR OwnerName/Owner
- County: SDR County/CountyName
- Depth (ft): from WellCompletion (TotalDepth/CompletionDepth/Depth)
- Completed: CompletionDate/CompletedDate/DateCompleted (Y‑M‑D)
- Latitude/Longitude: used for map pins; shown in card

## Screen 3 — Export (PDF/CSV)
- Goal: produce a clean, client‑ready summary of current results

PDF content:
- Header: Product name, logo, “As‑of YYYY‑MM‑DD”, user info (optional)
- Map snapshot: extent of current results + pins
- Table: Well ID, Owner, County, Depth (ft), Completed (date)
- Footer: full attribution + non‑endorsement + “as‑is” disclaimer

CSV content:
- One row per well; columns match the results list; include lat, lon

Export actions:
- Export PDF: generates and downloads a PDF of current filtered results
- Export CSV: downloads a CSV of current filtered results

## Screen 4 — Batch (≤ 50 addresses)
- Goal: process small sets for portfolio screens

Flow:
- Upload CSV: one column with addresses (or two columns: lat, lon)
- Validation: show how many addresses valid/invalid
- Process: background job; show “Preparing ZIP…” progress
- Delivery: email link and/or in‑app list to download a ZIP of per‑address PDFs + one master CSV

## Screen 5 — Account & Billing (simple)
- Goal: let users sign in, pick a plan, see usage

Sections:
- Sign in / Sign up: email + magic link or password (keep it simple)
- Plan picker: Solo / Team (see MVP pricing)
- Usage: this month’s reports generated, remaining exports
- Billing: card on file, download invoices

## About / Legal (always visible)
- Data source and attribution (verbatim on site and reports)
- Accuracy disclaimer (as‑is; verify with official records)
- As‑of date and refresh cadence (nightly)
- Owner names/PII policy: minimal exposure; authentication for raw exports; no unsolicited marketing

## What happens when I click things (event mapping)
- Search: geocodes the address, sets map center, and triggers /v1/search with lat, lon, radius_m, depth_min/max, date range, county
- Map zoom/drag: optional; “Refine with current map view” toggles a bounding‑box search
- Result row click / pin click: opens the Well card and highlights the pin
- Export PDF/CSV: calls /v1/reports or a dedicated export endpoint and starts file download
- Batch upload: posts CSV to a job endpoint; shows progress; provides link to ZIP
- Sign in: unlocks higher export limits and batch processing

## API endpoints (what the UI calls)
- GET /v1/search: returns wells near lat,lon with filters; fields: id (sdr_id), name (owner), county, lat, lon, depth_ft, date_completed
- GET /v1/wells/{id}: returns a single well (same fields plus location_confidence)
- POST /v1/reports (PDF/CSV export): accepts current filters, returns downloadable URLs

## Copy blocks (ready to use)
- Attribution: “Contains data from the Texas Water Development Board (TWDB) Statewide Driller’s Report (SDR). TWDB provides this data as‑is, without warranty, and does not endorse this product.”
- Accuracy: “Information is provided ‘as is’ and may contain errors or omissions. Not a substitute for official records or site surveys. Verify with the original source and qualified professionals.”
- As‑of: “SDR snapshot: YYYY‑MM‑DD; updated nightly when available.”

## Accessibility and responsiveness
- Keyboard: all controls reachable via Tab; visible focus states
- Color/contrast: WCAG AA for text and icons on the map
- Mobile: filters collapse; map fits width; results list becomes stacked cards

## Performance and reliability (simple rules)
- Search returns in ≤ 1.5 s for common radii; paginate after 200 results
- Map shows up to ~2,000 pins before clustering (optional later)
- Exports finish within 10–30 s for typical result sizes; show progress

## Acceptance criteria (what “done” looks like)
- I can enter an address, see a radius circle on the map, and load wells within 5 seconds
- I can filter by depth and date and see the list/map update
- I can click a well and see its details (ID, Owner, County, Depth, Completed, Coordinates)
- I can click Export PDF and download a professional‑looking PDF with a map and table
- I can upload a CSV of up to 50 addresses and receive a ZIP of reports within a few minutes
- I can see the “as‑of” date and the SDR attribution on the site and in the report

## Future (nice‑to‑have after MVP)
- GWDB enrichment (aquifer, gwdb depth)
- RRC overlays (nearby energy)
- Saved searches and alerts
- Larger batch, enterprise features (SSO, admin, audit log)
