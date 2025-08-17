from __future__ import annotations

import os
from typing import Optional, List

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


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/v1/wells/{well_id}", response_model=SearchItem)
def get_well(well_id: str):
    if pool is None:
        # Stub fallback
        return SearchItem(id=well_id)
    conn = pool.getconn()
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
        pool.putconn(conn)


@app.get("/v1/search", response_model=List[SearchItem])
def search(
    county: Optional[str] = Query(default=None),
    depth_min: Optional[float] = Query(default=None),
    depth_max: Optional[float] = Query(default=None),
    date_from: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    date_to: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    limit: int = Query(default=50, ge=1, le=500),
):
    if pool is None:
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
        clauses.append("date_completed >= %s")
        params.append(date_from)
    if date_to:
        clauses.append("date_completed <= %s")
        params.append(date_to)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = (
        "SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD') "
        "FROM app.wells " + where + " ORDER BY date_completed DESC NULLS LAST, id ASC LIMIT %s"
    )
    params.append(limit)
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [SearchItem(id=r[0], owner=r[1], county=r[2], lat=r[3], lon=r[4], depth_ft=r[5], date_completed=r[6]) for r in rows]
    finally:
        pool.putconn(conn)


