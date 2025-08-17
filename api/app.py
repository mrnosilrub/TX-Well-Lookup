from __future__ import annotations

import os
from typing import Optional, List
import time
import uuid
import json
import math

import psycopg2
import psycopg2.pool
from fastapi import FastAPI, Query, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from urllib.parse import urlencode
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel
import zipfile


# Load env vars from api/.env for local/dev runs
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
DATABASE_URL = os.getenv("DATABASE_URL")
ALLOWED_ORIGINS = [s.strip() for s in os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:4321,http://localhost:4321"
).split(",") if s.strip()]
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("1", "true", "yes")
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "120"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
STATEMENT_TIMEOUT_MS = int(os.getenv("STATEMENT_TIMEOUT_MS", "15000"))


class SearchItem(BaseModel):
    id: str
    owner: Optional[str] = None
    county: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    depth_ft: Optional[float] = None
    date_completed: Optional[str] = None
    source: Optional[str] = None
    source_id: Optional[str] = None


class ReportFilters(BaseModel):
    county: Optional[str] = None
    depth_min: Optional[float] = None
    depth_max: Optional[float] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius_m: Optional[int] = None
    limit: Optional[int] = 100
    source: Optional[str] = None  # 'sdr' | 'gwdb' | 'all'

app = FastAPI(title="TX Well Lookup API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    request_id = uuid.uuid4().hex
    request.state.request_id = request_id
    # Simple in-memory fixed-window rate limiter per client IP
    if RATE_LIMIT_ENABLED:
        ip = request.client.host if request.client else "unknown"
        now = int(time.time())
        window = now // RATE_LIMIT_WINDOW_SEC
        bucket = _rate_buckets.get(ip)
        if bucket is None or bucket[0] != window:
            _rate_buckets[ip] = (window, 1)
            remaining = max(0, RATE_LIMIT_PER_MIN - 1)
        else:
            count = bucket[1] + 1
            _rate_buckets[ip] = (window, count)
            remaining = max(0, RATE_LIMIT_PER_MIN - count)
            if count > RATE_LIMIT_PER_MIN:
                retry_after = (window + 1) * RATE_LIMIT_WINDOW_SEC - now
                log = {
                    "event": "rate_limit",
                    "request_id": request_id,
                    "ip": ip,
                    "method": request.method,
                    "path": request.url.path,
                }
                print(json.dumps(log), flush=True)
                return JSONResponse(status_code=429, content={
                    "detail": "Too Many Requests",
                    "request_id": request_id
                }, headers={
                    "X-RateLimit-Limit": str(RATE_LIMIT_PER_MIN),
                    "X-RateLimit-Remaining": str(0),
                    "Retry-After": str(retry_after),
                    "X-Request-ID": request_id,
                })
    start = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = getattr(response, 'status_code', 200)
    except Exception as exc:  # logged by handler as well
        duration_ms = int((time.perf_counter() - start) * 1000)
        log = {
            "event": "http_request_error",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": 500,
            "duration_ms": duration_ms,
            "client": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "error": repr(exc),
        }
        print(json.dumps(log), flush=True)
        raise
    else:
        duration_ms = int((time.perf_counter() - start) * 1000)
        log = {
            "event": "http_request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": status_code,
            "duration_ms": duration_ms,
            "client": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        print(json.dumps(log), flush=True)
        response.headers["X-Request-ID"] = request_id
        if RATE_LIMIT_ENABLED and request.client:
            # attach remaining estimate when available
            ip = request.client.host
            b = _rate_buckets.get(ip)
            if b and b[0] == (int(time.time()) // RATE_LIMIT_WINDOW_SEC):
                remaining = max(0, RATE_LIMIT_PER_MIN - b[1])
                response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_PER_MIN)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, 'request_id', uuid.uuid4().hex)
    log = {
        "event": "unhandled_exception",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "error": repr(exc),
    }
    print(json.dumps(log), flush=True)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error", "request_id": request_id}, headers={"X-Request-ID": request_id})

pool: Optional[psycopg2.pool.SimpleConnectionPool] = None
_rate_buckets: dict[str, tuple[int, int]] = {}


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
        conn = pool.getconn()
        # Liveness check: Neon can drop idle SSL connections
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            try:
                pool.closeall()
            except Exception:
                pass
            pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, dsn=DATABASE_URL)
            conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                # Apply statement_timeout (ms) per connection to bound long queries
                cur.execute("SET LOCAL statement_timeout = %s", (STATEMENT_TIMEOUT_MS,))
        except Exception:
            pass
        return conn
    except Exception:
        # Rebuild the pool on failure (e.g., Neon connection dropped)
        try:
            pool.closeall()
        except Exception:
            pass
        pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, dsn=DATABASE_URL)
        return pool.getconn()


def _resolve_wells_table(source: Optional[str]) -> str:
    s = (source or "sdr").lower()
    if s == "sdr":
        return "app.wells_sdr"
    if s == "gwdb":
        return "app.wells_gwdb"
    # 'all' and any fallback
    return "app.wells"


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/live")
def live():
    # basic liveness
    return {"live": True}


@app.get("/ready")
def ready():
    # basic readiness: can we get a connection
    if not DATABASE_URL:
        return {"ready": True}
    try:
        c = _get_conn()
        if c:
            try:
                pool and pool.putconn(c)
            except Exception:
                pass
            return {"ready": True}
    except Exception:
        pass
    return JSONResponse(status_code=503, content={"ready": False})


@app.get("/v1/wells/{well_id}", response_model=SearchItem)
def get_well(well_id: str, source: Optional[str] = Query(default="sdr", pattern="^(sdr|gwdb|all)$")):
    if pool is None and not DATABASE_URL:
        # Stub fallback
        return SearchItem(id=well_id)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            table = _resolve_wells_table(source)
            cur.execute(
                """
                SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD'), source, source_id
                FROM {table}
                WHERE id = %s
                LIMIT 1
                """.format(table=table),
                (well_id,),
            )
            row = cur.fetchone()
            if not row:
                return SearchItem(id=well_id)
            return SearchItem(
                id=row[0], owner=row[1], county=row[2], lat=row[3], lon=row[4], depth_ft=row[5], date_completed=row[6], source=row[7], source_id=row[8]
            )
    finally:
        if pool is not None and conn is not None:
            try:
                pool.putconn(conn)
            except Exception:
                pass


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
    source: Optional[str] = Query(default="sdr", pattern="^(sdr|gwdb|all)$"),
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
    table = _resolve_wells_table(source)
    sql = (
        "SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD'), source, source_id "
        f"FROM {table} " + where + " ORDER BY date_completed DESC NULLS LAST, id ASC LIMIT %s"
    )
    params.append(limit)
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [SearchItem(id=r[0], owner=r[1], county=r[2], lat=r[3], lon=r[4], depth_ft=r[5], date_completed=r[6], source=r[7], source_id=r[8]) for r in rows]
    finally:
        if pool is not None and conn is not None:
            pool.putconn(conn)


@app.post("/v1/search.csv")
def export_search_csv(
    filters: ReportFilters | None = None,
):
    county = filters.county if filters else None
    depth_min = filters.depth_min if filters else None
    depth_max = filters.depth_max if filters else None
    date_from = filters.date_from if filters else None
    date_to = filters.date_to if filters else None
    lat = filters.lat if filters else None
    lon = filters.lon if filters else None
    radius_m = filters.radius_m if filters else None
    limit = (filters.limit if (filters and filters.limit) else 1000)
    source = (filters.source if filters and filters.source else "sdr")
    """Export current filtered results as CSV. Columns match list view and include lat/lon."""
    if pool is None and not DATABASE_URL:
        # Stub empty CSV
        def _empty_gen():
            s = io.StringIO()
            w = csv.writer(s)
            w.writerow(["id", "owner", "county", "lat", "lon", "depth_ft", "date_completed", "source", "source_id"])
            yield s.getvalue()
        filename = f"tx_wells_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(_empty_gen(), media_type="text/csv", headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        })

    clauses: List[str] = []
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
    if lat is not None and lon is not None and radius_m is not None and radius_m > 0:
        delta_lat = radius_m / 111_320.0
        cos_lat = max(0.001, math.cos(math.radians(lat)))
        delta_lon = radius_m / (111_320.0 * cos_lat)
        min_lat, max_lat = lat - delta_lat, lat + delta_lat
        min_lon, max_lon = lon - delta_lon, lon + delta_lon
        clauses.append("lat BETWEEN %s AND %s")
        params.extend([min_lat, max_lat])
        clauses.append("lon BETWEEN %s AND %s")
        params.extend([min_lon, max_lon])
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    table = _resolve_wells_table(source)
    sql = (
        "SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD'), source, source_id "
        f"FROM {table} " + where + " ORDER BY date_completed DESC NULLS LAST, id ASC LIMIT %s"
    )
    params.append(limit)

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        def row_iter():
            sio = io.StringIO()
            writer = csv.writer(sio)
            writer.writerow(["id", "owner", "county", "lat", "lon", "depth_ft", "date_completed", "source", "source_id"])
            yield sio.getvalue()
            sio.seek(0); sio.truncate(0)
            for r in rows:
                writer.writerow([r[0], r[1] or "", r[2] or "", r[3] or "", r[4] or "", r[5] or "", r[6] or "", r[7] or "", r[8] or ""])
                yield sio.getvalue()
                sio.seek(0); sio.truncate(0)

        filename = f"tx_wells_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(row_iter(), media_type="text/csv", headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        })
    finally:
        if pool is not None and conn is not None:
            pool.putconn(conn)


@app.post("/v1/reports", response_class=StreamingResponse)
def export_pdf(
    format: str = Query(default="pdf", pattern="^(pdf)$"),
    filters: ReportFilters | None = None,
):
    # Unpack filters (supports both body and missing body)
    county = filters.county if filters else None
    depth_min = filters.depth_min if filters else None
    depth_max = filters.depth_max if filters else None
    date_from = filters.date_from if filters else None
    date_to = filters.date_to if filters else None
    lat = filters.lat if filters else None
    lon = filters.lon if filters else None
    radius_m = filters.radius_m if filters else None
    limit = (filters.limit if (filters and filters.limit) else 100)
    source = (filters.source if (filters and filters.source) else "sdr")
    """Simple PDF export summarizing current result set (first page list)."""
    # Reuse the same filter building
    clauses: List[str] = []
    params: List[object] = []
    if county:
        clauses.append("county = %s"); params.append(county)
    if depth_min is not None:
        clauses.append("depth_ft >= %s"); params.append(depth_min)
    if depth_max is not None:
        clauses.append("depth_ft <= %s"); params.append(depth_max)
    if date_from:
        clauses.append("date_completed >= %s::date"); params.append(date_from)
    if date_to:
        clauses.append("date_completed <= %s::date"); params.append(date_to)
    if date_from or date_to:
        clauses.append("date_completed IS NOT NULL")
    if lat is not None and lon is not None and radius_m is not None and radius_m > 0:
        delta_lat = radius_m / 111_320.0
        cos_lat = max(0.001, math.cos(math.radians(lat)))
        delta_lon = radius_m / (111_320.0 * cos_lat)
        min_lat, max_lat = lat - delta_lat, lat + delta_lat
        min_lon, max_lon = lon - delta_lon, lon + delta_lon
        clauses.append("lat BETWEEN %s AND %s"); params.extend([min_lat, max_lat])
        clauses.append("lon BETWEEN %s AND %s"); params.extend([min_lon, max_lon])
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    table = _resolve_wells_table(source)
    sql = (
        "SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD'), source, source_id "
        f"FROM {table} " + where + " ORDER BY date_completed DESC NULLS LAST, id ASC LIMIT %s"
    )
    params.append(limit)

    rows: List[tuple] = []
    as_of: Optional[str] = None

    def _load_rows_and_asof(cn) -> tuple[list[tuple], Optional[str]]:
        with cn.cursor() as cur:
            cur.execute(sql, params)
            rs = cur.fetchall()
            cur.execute(f"SELECT to_char(MAX(date_completed), 'YYYY-MM-DD') FROM {table}")
            r = cur.fetchone()
            return rs, (r[0] if r and r[0] else None)

    conn_primary = _get_conn()
    if conn_primary is not None:
        try:
            try:
                rows, as_of = _load_rows_and_asof(conn_primary)
            except psycopg2.OperationalError:
                # Retry once with a fresh connection
                conn_retry = _get_conn()
                if conn_retry is not None:
                    try:
                        rows, as_of = _load_rows_and_asof(conn_retry)
                    finally:
                        try:
                            pool and pool.putconn(conn_retry)
                        except Exception:
                            pass
        finally:
            try:
                pool and pool.putconn(conn_primary)
            except Exception:
                pass

    def pdf_iter():
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch
        )
        styles = getSampleStyleSheet()
        elements = []

        title = Paragraph("TX Well Lookup — Results", styles['Title'])
        when = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        meta_parts = [f"Generated: {when}"]
        if as_of:
            meta_parts.append(f"as-of {as_of}")
        # Filter summary
        filt = []
        if county: filt.append(f"County: {county}")
        if depth_min is not None: filt.append(f"Depth ≥ {depth_min}")
        if depth_max is not None: filt.append(f"Depth ≤ {depth_max}")
        if date_from: filt.append(f"From: {date_from}")
        if date_to: filt.append(f"To: {date_to}")
        if radius_m and lat is not None and lon is not None:
            filt.append(f"Radius: {radius_m} m @ {lat:.4f},{lon:.4f}")
        meta_line = Paragraph(" | ".join(meta_parts), styles['Normal'])
        filt_line = Paragraph("Filters: " + (", ".join(filt) if filt else "None"), styles['Normal'])

        elements += [title, Spacer(1, 8), meta_line, Spacer(1, 4), filt_line, Spacer(1, 16)]

        # Map snapshot (server-side render via staticmap)
        try:
            from staticmap import StaticMap, CircleMarker, IconMarker
            latlons = [(r[3], r[4]) for r in rows if r[3] is not None and r[4] is not None]
            # Higher pixel resolution for sharper rendering in PDF
            img_w, img_h = 1600, 800
            m = StaticMap(
                img_w,
                img_h,
                padding_x=60,
                padding_y=60,
                url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            )
            # Try to use Leaflet's default pin icon for visual parity with the site
            leaflet_icon_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'apps', 'web', 'node_modules', 'leaflet', 'dist', 'images', 'marker-icon.png')
            )
            use_leaflet_icon = os.path.exists(leaflet_icon_path)
            for ll in latlons[:200]:
                if use_leaflet_icon:
                    try:
                        m.add_marker(IconMarker((float(ll[1]), float(ll[0])), leaflet_icon_path, 12, 41))
                    except Exception:
                        m.add_marker(CircleMarker((float(ll[1]), float(ll[0])), '#2563eb', 6))
                else:
                    m.add_marker(CircleMarker((float(ll[1]), float(ll[0])), '#2563eb', 6))
            zoom: int | None = None
            center: tuple[float, float] | None = None
            if radius_m and lat is not None and lon is not None:
                # Radius-aware zoom around provided center
                center = (float(lon), float(lat))
                c_lat = float(lat)
                # Slightly less tight than before
                desired_width_m = max(1000.0, 2.0 * float(radius_m))
                mpp_equator = 156543.03392
                cos_lat = max(0.001, math.cos(math.radians(c_lat)))
                zoom_calc = int(math.log2((mpp_equator * cos_lat * img_w) / desired_width_m))
                zoom = max(3, min(17, zoom_calc))
            elif latlons:
                # Start from auto-fit but nudge one level out for more context
                try:
                    auto_zoom = m._calculate_zoom()  # type: ignore[attr-defined]
                except Exception:
                    auto_zoom = None
                if auto_zoom is not None:
                    zoom = max(3, min(17, auto_zoom))
                else:
                    zoom = None
            else:
                # Default to Texas center, a bit more zoomed-in
                center = (-99.0, 31.0)
                zoom = 6
            if radius_m and lat is not None and lon is not None:
                center_marker = CircleMarker((float(lon), float(lat)), '#ef4444', 8)
                m.add_marker(center_marker)
            image = m.render(zoom=zoom, center=center)
            out = io.BytesIO()
            image.save(out, format='PNG')
            out.seek(0)
            # Scale to available doc width, preserve aspect
            map_img = Image(out, width=doc.width, height=doc.width * (img_h / img_w))
            elements += [map_img, Spacer(1, 12), Paragraph("Map data © OpenStreetMap contributors", styles['Normal']), Spacer(1, 16)]
        except Exception:
            pass

        data = [["Well ID", "Owner", "County", "Depth (ft)", "Completed", "Source", "Source ID"]]
        for r in rows:
            data.append([r[0], r[1] or "", r[2] or "", r[5] or "", r[6] or "", r[7] or "", r[8] or ""])

        # Column widths tuned for letter page
        col_widths = [1.2*inch, 2.6*inch, 1.2*inch, 1.0*inch, 1.1*inch, 0.9*inch, 1.6*inch]
        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('ALIGN', (0,0), (-1,0), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#e5e7eb')),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        elements.append(tbl)

        def add_footer(canvas_obj, doc_obj):
            canvas_obj.setFont('Helvetica', 8)
            page_num = canvas_obj.getPageNumber()
            canvas_obj.drawRightString(doc_obj.pagesize[0]-0.75*inch, 0.5*inch, f"Page {page_num}")

        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
        buf.seek(0)
        yield buf.getvalue()

    filename = f"tx_wells_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(pdf_iter(), media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=\"{filename}\""
    })


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



@app.post("/v1/batch")
def batch_zip(
    file: UploadFile = File(...),
    limit: int = Query(default=50, ge=1, le=50),
):
    """Accept a small CSV of addresses or lat/lon and return a ZIP of PDFs.
    CSV columns (any one of):
      - address (freeform)
      - lat, lon
    """
    # Read CSV
    try:
        content = file.file.read()
    finally:
        try:
            file.file.close()
        except Exception:
            pass
    try:
        text = content.decode('utf-8', errors='ignore')
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV encoding")
    import csv as _csv
    import io as _io
    rdr = _csv.DictReader(_io.StringIO(text))
    tasks: list[dict] = []
    for row in rdr:
        task: dict = {}
        if row.get('lat') and row.get('lon'):
            try:
                task['lat'] = float(row['lat'])
                task['lon'] = float(row['lon'])
            except Exception:
                continue
        elif row.get('address'):
            # naive: geocode via Nominatim
            try:
                import requests as _req
                resp = _req.get('https://nominatim.openstreetmap.org/search', params={
                    'q': row['address'], 'format': 'json', 'limit': 1
                }, headers={'User-Agent':'TX Well Lookup Batch'}, timeout=10)
                j = resp.json()
                if j:
                    task['lat'] = float(j[0]['lat'])
                    task['lon'] = float(j[0]['lon'])
            except Exception:
                continue
        if 'lat' in task and 'lon' in task:
            tasks.append(task)
        if len(tasks) >= limit:
            break
    if not tasks:
        raise HTTPException(status_code=400, detail="No valid rows found (need address or lat/lon)")

    # Generate PDFs into memory
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for idx, t in enumerate(tasks, start=1):
            # Reuse export_pdf flow by calling the same PDF builder via HTTP params
            # Simpler: call our internal function through a tiny inline builder duplicating key bits
            # Build rows for a specific small query around this point
            county = None; depth_min=None; depth_max=None; date_from=None; date_to=None; radius_m=5000; lim=200
            # Query DB for matching rows
            clauses: List[str] = []
            params: List[object] = []
            lat = t['lat']; lon = t['lon']
            delta_lat = radius_m / 111_320.0
            cos_lat = max(0.001, math.cos(math.radians(lat)))
            delta_lon = radius_m / (111_320.0 * cos_lat)
            min_lat, max_lat = lat - delta_lat, lat + delta_lat
            min_lon, max_lon = lon - delta_lon, lon + delta_lon
            clauses.append("lat BETWEEN %s AND %s"); params.extend([min_lat, max_lat])
            clauses.append("lon BETWEEN %s AND %s"); params.extend([min_lon, max_lon])
            where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
            sql = (
                "SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD') "
                "FROM app.wells " + where + " ORDER BY date_completed DESC NULLS LAST, id ASC LIMIT %s"
            )
            params.append(lim)

            rows: List[tuple] = []
            as_of: Optional[str] = None
            conn = _get_conn()
            if conn is not None:
                try:
                    with conn.cursor() as cur:
                        cur.execute(sql, params)
                        rows = cur.fetchall()
                        cur.execute("SELECT to_char(MAX(date_completed), 'YYYY-MM-DD') FROM app.wells")
                        r = cur.fetchone(); as_of = r[0] if r and r[0] else None
                finally:
                    try:
                        pool and pool.putconn(conn)
                    except Exception:
                        pass

            # Build a tiny one-page PDF for this task
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch,
                                     topMargin=0.6*inch, bottomMargin=0.6*inch)
            styles = getSampleStyleSheet()
            elems: list = []
            title = Paragraph(f"TX Well Lookup — Results @ {lat:.4f},{lon:.4f}", styles['Title'])
            when = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
            meta_parts = [f"Generated: {when}"]
            if as_of: meta_parts.append(f"SDR as-of {as_of}")
            elems += [title, Spacer(1, 8), Paragraph(" | ".join(meta_parts), styles['Normal']), Spacer(1, 12)]
            # Map image (reuse staticmap code)
            try:
                from staticmap import StaticMap, IconMarker, CircleMarker
                img_w, img_h = 1400, 700
                m = StaticMap(img_w, img_h, padding_x=60, padding_y=60, url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
                latlons = [(r[3], r[4]) for r in rows if r[3] is not None and r[4] is not None]
                leaflet_icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'apps', 'web', 'node_modules', 'leaflet', 'dist', 'images', 'marker-icon.png'))
                use_icon = os.path.exists(leaflet_icon_path)
                for ll in latlons[:200]:
                    if use_icon:
                        try:
                            m.add_marker(IconMarker((float(ll[1]), float(ll[0])), leaflet_icon_path, 12, 41))
                        except Exception:
                            m.add_marker(CircleMarker((float(ll[1]), float(ll[0])), '#2563eb', 6))
                    else:
                        m.add_marker(CircleMarker((float(ll[1]), float(ll[0])), '#2563eb', 6))
                m.add_marker(CircleMarker((float(lon), float(lat)), '#ef4444', 8))
                image = m.render(zoom=None)
                out = io.BytesIO(); image.save(out, format='PNG'); out.seek(0)
                elems += [Image(out, width=doc.width, height=doc.width * (img_h / img_w)), Spacer(1, 8), Paragraph("Map data © OpenStreetMap contributors", styles['Normal']), Spacer(1, 12)]
            except Exception:
                pass
            data = [["Well ID", "Owner", "County", "Depth (ft)", "Completed"]]
            for r in rows:
                data.append([r[0], r[1] or "", r[2] or "", r[5] or "", r[6] or ""])
            tbl = Table(data, colWidths=[1.2*inch, 3.0*inch, 1.4*inch, 1.1*inch, 1.2*inch], repeatRows=1)
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f2937')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('ALIGN', (0,0), (-1,0), 'LEFT'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#e5e7eb')),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            elems.append(tbl)
            doc.build(elems)
            buf.seek(0)
            zf.writestr(f"tx_wells_{idx:02d}.pdf", buf.read())

    zip_buf.seek(0)
    return StreamingResponse(zip_buf, media_type='application/zip', headers={
        'Content-Disposition': f"attachment; filename=\"tx_wells_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip\""
    })

