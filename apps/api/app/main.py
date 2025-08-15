from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from uuid import uuid4
import random


app = FastAPI(title="TX Well Lookup API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local dev: allow Astro on 4321
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, bool]:
    return {"ok": True}


STUB_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "W-1001",
        "name": "Barton Creek Well",
        "county": "Travis",
        "lat": 30.2672,
        "lon": -97.7431,
        "depth_ft": 420,
    },
    {
        "id": "W-1002",
        "name": "Spring Branch Well",
        "county": "Hays",
        "lat": 29.9996,
        "lon": -98.1029,
        "depth_ft": 350,
    },
    {
        "id": "W-1003",
        "name": "Cedar Park Well",
        "county": "Williamson",
        "lat": 30.5060,
        "lon": -97.8203,
        "depth_ft": 500,
    },
    {
        "id": "W-1004",
        "name": "Buffalo Bayou Well",
        "county": "Harris",
        "lat": 29.7604,
        "lon": -95.3698,
        "depth_ft": 600,
    },
    {
        "id": "W-1005",
        "name": "White Rock Well",
        "county": "Dallas",
        "lat": 32.7767,
        "lon": -96.7970,
        "depth_ft": 470,
    },
    {
        "id": "W-1006",
        "name": "Mission San Jose Well",
        "county": "Bexar",
        "lat": 29.4241,
        "lon": -98.4936,
        "depth_ft": 440,
    },
]


@app.get("/v1/search")
def search_stub(q: str | None = None) -> Dict[str, List[Dict[str, Any]]]:
    # Sprint 3: mirror frontend stub shape: { items: [...] }
    items = STUB_ITEMS
    if q:
        query = q.lower()
        items = [
            it for it in STUB_ITEMS
            if query in it["name"].lower() or query in it["county"].lower()
        ]
    return {"items": items}


reports_store: Dict[str, Dict[str, Any]] = {}


@app.post("/v1/reports", status_code=status.HTTP_201_CREATED)
def create_report_stub(payload: Dict[str, Any] | None = None) -> Dict[str, str]:
    # Sprint 4: randomly simulate 402 Payment Required (no credits)
    if random.random() < 0.3:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient credits")
    report_id = str(uuid4())
    reports_store[report_id] = {"status": "ready", "pdf_url": "/fake/report.pdf"}
    return {"report_id": report_id}


@app.get("/v1/reports/{report_id}")
def get_report_stub(report_id: str) -> Dict[str, str]:
    report = reports_store.get(report_id)
    if not report:
        # For a very simple stub, still return a fixed URL to keep the flow uncomplicated
        return {"pdf_url": "/fake/report.pdf"}
    return {"pdf_url": report.get("pdf_url", "/fake/report.pdf")}


@app.get("/v1/wells/{well_id}")
def get_well_by_id(well_id: str) -> Dict[str, Any]:
    for it in STUB_ITEMS:
        if it["id"] == well_id:
            # minimal detail payload for Sprint 5; DB-backed in Sprint 6
            return {
                **it,
                "documents": [
                    {"title": "Well Info Sheet", "url": "/fake/docs/well-info.pdf"}
                ],
            }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Well not found")

