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
import math


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
    {"id": "S-0001", "name": "Sample Well 1", "county": "Travis", "lat": 30.2672, "lon": -97.7431, "depth_ft": 420},
    {"id": "S-0002", "name": "Sample Well 2", "county": "Hays", "lat": 29.9996, "lon": -98.1029, "depth_ft": 350},
    {"id": "S-0003", "name": "Sample Well 3", "county": "Williamson", "lat": 30.5060, "lon": -97.8203, "depth_ft": 500},
    {"id": "S-0004", "name": "Sample Well 4", "county": "Harris", "lat": 29.7604, "lon": -95.3698, "depth_ft": 600},
    {"id": "S-0005", "name": "Sample Well 5", "county": "Dallas", "lat": 32.7767, "lon": -96.7970, "depth_ft": 470},
    {"id": "S-0006", "name": "Sample Well 6", "county": "Bexar", "lat": 29.4241, "lon": -98.4936, "depth_ft": 440},
]


@app.get("/v1/search")
def search_endpoint(q: str | None = None, county: str | None = None, limit: int = 20,
                    lat: float | None = None, lon: float | None = None, radius_m: int = 1609,
                    depth_min: float | None = None, depth_max: float | None = None,
                    include_gwdb: bool = False) -> Dict[str, List[Dict[str, Any]]]:
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
        # Optionally surface a gwdb flag in stub as false
        if include_gwdb:
            for it in items:
                it.setdefault("gwdb_available", False)
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
        select_cols = "report_id as id, owner_name as name, county, ST_Y(geom) as lat, ST_X(geom) as lon, depth_ft"
        join_clause = ""
        order_bias = ""
        if include_gwdb:
            # Bias linked wells to top when requested
            select_cols += ", (wl.gwdb_id IS NOT NULL) as gwdb_available"
            join_clause = " LEFT JOIN well_links wl ON wl.report_id = well_reports.report_id"
            order_bias = " (wl.gwdb_id IS NOT NULL) DESC,"
        sql = f"SELECT {select_cols} FROM well_reports{join_clause}"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += f" ORDER BY{order_bias} date_completed DESC NULLS LAST LIMIT :limit"
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
                    "gwdb_available": False,
                    "gwdb_depth_ft": None,
                    "documents": [{"title": "Well Info Sheet", "url": "/fake/docs/well-info.pdf"}],
                }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Well not found")

    with get_db_session() as session:
        if session is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB session unavailable")
        sql = """
        SELECT wr.report_id as id,
               wr.owner_name as name,
               wr.county,
               ST_Y(wr.geom) as lat,
               ST_X(wr.geom) as lon,
               wr.depth_ft,
               COALESCE(wr.location_error_m,0) as location_error_m,
               (wl.gwdb_id IS NOT NULL) as gwdb_available,
               gw.depth_ft as gwdb_depth_ft
        FROM well_reports wr
        LEFT JOIN well_links wl ON wl.report_id = wr.report_id
        LEFT JOIN gwdb_wells gw ON gw.id = wl.gwdb_id
        WHERE wr.report_id = :rid
        LIMIT 1
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
            "gwdb_available": bool(row.get("gwdb_available", False)),
            "gwdb_depth_ft": row.get("gwdb_depth_ft"),
            "documents": [{"title": "Well Info Sheet", "url": "/fake/docs/well-info.pdf"}],
        }


@app.get("/v1/energy/nearby")
def energy_nearby(lat: float, lon: float, radius_m: int = 1609,
                  status: str | None = None, operator: str | None = None,
                  limit: int = 50) -> Dict[str, Any]:
    # If no DB configured, return empty stub
    if not os.getenv("DATABASE_URL"):
        return {"count": 0, "items": []}
    with get_db_session() as session:
        if session is None:
            return {"count": 0, "items": []}
        where = [
            "ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:lon,:lat),4326)::geography, :radius)"
        ]
        params: Dict[str, Any] = {"lat": lat, "lon": lon, "radius": radius_m}
        if status:
            where.append("status = :status")
            params["status"] = status
        if operator:
            where.append("operator ILIKE :operator")
            params["operator"] = f"%{operator}%"
        sql = """
        SELECT api14, operator, status, permit_date,
               ST_Y(geom) as lat, ST_X(geom) as lon,
               ST_Distance(geom, ST_SetSRID(ST_MakePoint(:lon,:lat),4326)::geography) as distance_m
        FROM rrc_permits
        WHERE {where}
        ORDER BY distance_m ASC
        LIMIT :limit
        """.format(where=" AND ".join(where))
        params["limit"] = min(max(limit, 1), 200)
        rows = session.execute(text(sql), params).mappings().all()
        items = [dict(r) for r in rows]
        return {"count": len(items), "items": items}

