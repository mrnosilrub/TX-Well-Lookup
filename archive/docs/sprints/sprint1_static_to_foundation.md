# Sprint 1 — Static → Foundation
**Outcome:** Static site runs locally and on GitHub Pages. Monorepo is ready for expansion (API, data, DevOps). Keep it simple and shippable.

## Agent C — Web (Astro)
**Tasks**
1) Confirm local dev works: `npm i && npm run dev` in `apps/web`.
2) Add a second page `about.astro` with project goals; link it from the header.
3) Add a basic component `components/Hero.astro` used on the home page.

**Acceptance**
- Home and About load locally.
- No console errors; Lighthouse Performance ≥ 95 on localhost.

**Tests**
```bash
npm run dev
# visit / and /about
```

## Agent D — DevOps
**Tasks**
1) Enable GitHub Pages (Actions). Push `main` and verify deployment.
2) If publishing under `/REPO`, set `PUBLIC_BASE_PATH` in workflow accordingly.

**Acceptance**
- Pages URL loads the built site, including the About page.

## Agent A — Backend (placeholder for Sprint 2)
_No work in Sprint 1. Ensure repo structure is clean._

## Agent B — Data Pipeline (placeholder for Sprint 2)
_No work in Sprint 1._

---

## Definition of Done
- Site serves locally at `http://localhost:4321`.
- Pages deployment is live and reflects latest commit.


