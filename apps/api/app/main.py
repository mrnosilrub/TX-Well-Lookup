from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from uuid import uuid4
import random
import os
from sqlalchemy import text

from .db import get_db_session
from .models import WellReport


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
def search_endpoint(q: str | None = None, county: str | None = None, limit: int = 20,
                    lat: float | None = None, lon: float | None = None, radius_m: int = 1609,
                    depth_min: float | None = None, depth_max: float | None = None) -> Dict[str, List[Dict[str, Any]]]:
    # If no DATABASE_URL, fall back to stub items
    if not os.getenv("DATABASE_URL"):
        items = STUB_ITEMS
        if q:
            query = q.lower()
            items = [it for it in items if query in it["name"].lower() or query in it["county"].lower()]
        if county:
            items = [it for it in items if it["county"].lower() == county.lower()]
        if depth_min is not None:
            items = [it for it in items if it.get("depth_ft") is None or it["depth_ft"] >= depth_min]
        if depth_max is not None:
            items = [it for it in items if it.get("depth_ft") is None or it["depth_ft"] <= depth_max]
        return {"items": items[: min(max(limit, 1), 100)]}

    # DB-backed path (expects PostGIS; simplified for now)
    with get_db_session() as session:
        if session is None:
            return {"items": []}
        where = []
        params: Dict[str, Any] = {}
        if q:
            where.append("(owner_name ILIKE :q OR address ILIKE :q)")
            params["q"] = f"%{q}%"
        if county:
            where.append("county = :county")
            params["county"] = county
        if depth_min is not None:
            where.append("depth_ft >= :depth_min")
            params["depth_min"] = depth_min
        if depth_max is not None:
            where.append("depth_ft <= :depth_max")
            params["depth_max"] = depth_max
        if lat is not None and lon is not None:
            where.append("ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:lon,:lat),4326)::geography, :radius)")
            params.update({"lat": lat, "lon": lon, "radius": radius_m})
        sql = "SELECT report_id as id, owner_name as name, county, ST_Y(geom) as lat, ST_X(geom) as lon, depth_ft FROM well_reports"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY date_completed DESC NULLS LAST LIMIT :limit"
        params["limit"] = min(max(limit, 1), 100)
        rows = session.execute(text(sql), params).mappings().all()
        items = [dict(r) for r in rows]
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
    if not os.getenv("DATABASE_URL"):
        for it in STUB_ITEMS:
            if it["id"] == well_id:
                return {
                    **it,
                    "location_confidence": "high",
                    "documents": [{"title": "Well Info Sheet", "url": "/fake/docs/well-info.pdf"}],
                }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Well not found")

    with get_db_session() as session:
        if session is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB session unavailable")
        sql = """
        SELECT report_id as id, owner_name as name, county, ST_Y(geom) as lat, ST_X(geom) as lon,
               depth_ft, COALESCE(location_error_m,0) as location_error_m
        FROM well_reports WHERE report_id = :rid LIMIT 1
        """
        row = session.execute(text(sql), {"rid": well_id}).mappings().first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Well not found")
        err = float(row.get("location_error_m", 0) or 0)
        confidence = "high" if err <= 25 else ("medium" if err <= 100 else "low")
        return {
            "id": row["id"],
            "name": row["name"],
            "county": row["county"],
            "lat": row["lat"],
            "lon": row["lon"],
            "depth_ft": row["depth_ft"],
            "location_confidence": confidence,
            "documents": [{"title": "Well Info Sheet", "url": "/fake/docs/well-info.pdf"}],
        }

