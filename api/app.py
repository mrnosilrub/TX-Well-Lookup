from __future__ import annotations

import os
from typing import Optional, List
import math

import psycopg2
import psycopg2.pool
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


DATABASE_URL = os.getenv("DATABASE_URL")


class SearchItem(BaseModel):
    id: str
    owner: Optional[str] = None
    county: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    depth_ft: Optional[float] = None
    date_completed: Optional[str] = None


app = FastAPI(title="TX Well Lookup API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:4321",
        "http://localhost:4321",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

pool: Optional[psycopg2.pool.SimpleConnectionPool] = None


@app.on_event("startup")
def on_startup() -> None:
    global pool
    if DATABASE_URL:
        pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, dsn=DATABASE_URL)


@app.on_event("shutdown")
def on_shutdown() -> None:
    global pool
    if pool is not None:
        pool.closeall()
        pool = None


def _get_conn():
    """Get a DB connection, rebuilding the pool if needed.
    Returns None if DATABASE_URL is not configured.
    """
    global pool
    if not DATABASE_URL:
        return None
    if pool is None:
        pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, dsn=DATABASE_URL)
    try:
        return pool.getconn()
    except Exception:
        # Rebuild the pool on failure (e.g., Neon connection dropped)
        try:
            pool.closeall()
        except Exception:
            pass
        pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, dsn=DATABASE_URL)
        return pool.getconn()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/v1/wells/{well_id}", response_model=SearchItem)
def get_well(well_id: str):
    if pool is None and not DATABASE_URL:
        # Stub fallback
        return SearchItem(id=well_id)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD')
                FROM app.wells
                WHERE id = %s
                LIMIT 1
                """,
                (well_id,),
            )
            row = cur.fetchone()
            if not row:
                return SearchItem(id=well_id)
            return SearchItem(
                id=row[0], owner=row[1], county=row[2], lat=row[3], lon=row[4], depth_ft=row[5], date_completed=row[6]
            )
    finally:
        if pool is not None and conn is not None:
            pool.putconn(conn)


@app.get("/v1/search", response_model=List[SearchItem])
def search(
    county: Optional[str] = Query(default=None),
    depth_min: Optional[float] = Query(default=None),
    depth_max: Optional[float] = Query(default=None),
    date_from: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    date_to: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    radius_m: Optional[int] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
):
    if pool is None and not DATABASE_URL:
        # Stub fallback
        return []
    clauses = []
    params: List[object] = []
    if county:
        clauses.append("county = %s")
        params.append(county)
    if depth_min is not None:
        clauses.append("depth_ft >= %s")
        params.append(depth_min)
    if depth_max is not None:
        clauses.append("depth_ft <= %s")
        params.append(depth_max)
    if date_from:
        clauses.append("date_completed >= %s::date")
        params.append(date_from)
    if date_to:
        clauses.append("date_completed <= %s::date")
        params.append(date_to)
    if date_from or date_to:
        clauses.append("date_completed IS NOT NULL")
    # Simple radius filter using a bounding box on lat/lon (non-PostGIS)
    if lat is not None and lon is not None and radius_m is not None and radius_m > 0:
        delta_lat = radius_m / 111_320.0
        # Avoid division by zero at poles
        cos_lat = max(0.001, math.cos(math.radians(lat)))
        delta_lon = radius_m / (111_320.0 * cos_lat)
        min_lat, max_lat = lat - delta_lat, lat + delta_lat
        min_lon, max_lon = lon - delta_lon, lon + delta_lon
        clauses.append("lat BETWEEN %s AND %s")
        params.extend([min_lat, max_lat])
        clauses.append("lon BETWEEN %s AND %s")
        params.extend([min_lon, max_lon])
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = (
        "SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD') "
        "FROM app.wells " + where + " ORDER BY date_completed DESC NULLS LAST, id ASC LIMIT %s"
    )
    params.append(limit)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [SearchItem(id=r[0], owner=r[1], county=r[2], lat=r[3], lon=r[4], depth_ft=r[5], date_completed=r[6]) for r in rows]
    finally:
        if pool is not None and conn is not None:
            pool.putconn(conn)


@app.get("/v1/meta")
def meta():
    if pool is None and not DATABASE_URL:
        return {"as_of": None}
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_char(MAX(date_completed), 'YYYY-MM-DD') FROM app.wells")
            row = cur.fetchone()
            return {"as_of": row[0] if row and row[0] else None}
    finally:
        if pool is not None and conn is not None:
            pool.putconn(conn)


