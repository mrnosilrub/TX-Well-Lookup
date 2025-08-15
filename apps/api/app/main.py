from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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
def search_stub() -> Dict[str, List[Dict[str, Any]]]:
    # Sprint 3: mirror frontend stub shape: { items: [...] }
    return {"items": STUB_ITEMS}

