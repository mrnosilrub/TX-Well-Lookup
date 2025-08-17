from __future__ import annotations

import os
from typing import Optional, List
import math

import psycopg2
import psycopg2.pool
from fastapi import FastAPI, Query
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
        return conn
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


@app.get("/v1/search.csv")
def export_search_csv(
    county: Optional[str] = Query(default=None),
    depth_min: Optional[float] = Query(default=None),
    depth_max: Optional[float] = Query(default=None),
    date_from: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    date_to: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    radius_m: Optional[int] = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=10000),
):
    """Export current filtered results as CSV. Columns match list view and include lat/lon."""
    if pool is None and not DATABASE_URL:
        # Stub empty CSV
        def _empty_gen():
            s = io.StringIO()
            w = csv.writer(s)
            w.writerow(["id", "owner", "county", "lat", "lon", "depth_ft", "date_completed"])
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

        def row_iter():
            sio = io.StringIO()
            writer = csv.writer(sio)
            writer.writerow(["id", "owner", "county", "lat", "lon", "depth_ft", "date_completed"])
            yield sio.getvalue()
            sio.seek(0); sio.truncate(0)
            for r in rows:
                writer.writerow([r[0], r[1] or "", r[2] or "", r[3] or "", r[4] or "", r[5] or "", r[6] or ""])
                yield sio.getvalue()
                sio.seek(0); sio.truncate(0)

        filename = f"tx_wells_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(row_iter(), media_type="text/csv", headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        })
    finally:
        if pool is not None and conn is not None:
            pool.putconn(conn)


@app.get("/v1/reports", response_class=StreamingResponse)
def export_pdf(
    format: str = Query(default="pdf", pattern="^(pdf)$"),
    county: Optional[str] = Query(default=None),
    depth_min: Optional[float] = Query(default=None),
    depth_max: Optional[float] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    radius_m: Optional[int] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
):
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
    sql = (
        "SELECT id, owner, county, lat, lon, depth_ft, to_char(date_completed, 'YYYY-MM-DD') "
        "FROM app.wells " + where + " ORDER BY date_completed DESC NULLS LAST, id ASC LIMIT %s"
    )
    params.append(limit)

    rows: List[tuple] = []
    as_of: Optional[str] = None

    def _load_rows_and_asof(cn) -> tuple[list[tuple], Optional[str]]:
        with cn.cursor() as cur:
            cur.execute(sql, params)
            rs = cur.fetchall()
            cur.execute("SELECT to_char(MAX(date_completed), 'YYYY-MM-DD') FROM app.wells")
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
            meta_parts.append(f"SDR as-of {as_of}")
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

        data = [["Well ID", "Owner", "County", "Depth (ft)", "Completed"]]
        for r in rows:
            data.append([r[0], r[1] or "", r[2] or "", r[5] or "", r[6] or ""])

        # Column widths tuned for letter page
        col_widths = [1.2*inch, 3.0*inch, 1.4*inch, 1.1*inch, 1.2*inch]
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


