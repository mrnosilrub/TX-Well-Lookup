from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from uuid import uuid4
import random
import os
import time
from sqlalchemy import text

from .db import get_db_session
from .models import WellReport
import math
from fastapi.responses import HTMLResponse, FileResponse
from .security import sign_payload, verify_token
import json
import csv
import zipfile
from pathlib import Path
from io import StringIO
try:
    from data.bundles.bundle_builder import build_bundle as _external_build_bundle
except Exception:  # pragma: no cover - dev fallback when data module not present
    _external_build_bundle = None


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


@app.get("/")
def root() -> Dict[str, Any]:
    return {"ok": True, "service": "tx-well-lookup-api", "version": app.version}


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
credits_store: Dict[str, int] = {}
credit_grants: List[Dict[str, Any]] = []
credit_spends: List[Dict[str, Any]] = []
alerts_store: Dict[str, Dict[str, Any]] = {}


def _get_user_id(x_user: str | None) -> str:
    return x_user or "demo"


def _dev_build_bundle(output_dir: str, lat: float, lon: float) -> Dict[str, str]:
    base = Path(output_dir or ".reports").resolve()
    base.mkdir(parents=True, exist_ok=True)
    run_dir = base / f"r-{int(time.time())}"
    run_dir.mkdir(parents=True, exist_ok=True)
    # csv
    csv_path = run_dir / "nearby.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "lat", "lon", "distance_m"]) 
        writer.writerow(["Sample Well", f"{lat:.6f}", f"{lon:.6f}", "0"]) 
    # geojson
    gj_path = run_dir / "nearby.geojson"
    gj = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Sample Well"},
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        ],
    }
    gj_path.write_text(json.dumps(gj), encoding="utf-8")
    # manifest
    manifest_path = run_dir / "manifest.json"
    manifest = {"generated_at": int(time.time()), "center": {"lat": lat, "lon": lon}}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    # pdf (stub as text)
    pdf_path = run_dir / "report.pdf"
    pdf_path.write_bytes(f"Stub PDF for ({lat:.6f},{lon:.6f})\n".encode("utf-8"))
    # zip bundle
    zip_path = run_dir / "report.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(csv_path, arcname=csv_path.name)
        zf.write(gj_path, arcname=gj_path.name)
        zf.writestr("README.txt", "Stub bundle contents for local dev")
    return {
        "pdf": str(pdf_path),
        "zip": str(zip_path),
        "csv": str(csv_path),
        "geojson": str(gj_path),
        "manifest": str(manifest_path),
    }


def build_bundle(output_dir: str, lat: float, lon: float) -> Dict[str, str]:
    if _external_build_bundle is not None:
        try:
            return _external_build_bundle(output_dir=output_dir, lat=lat, lon=lon)
        except Exception:
            pass
    return _dev_build_bundle(output_dir=output_dir, lat=lat, lon=lon)


@app.post("/v1/reports", status_code=status.HTTP_201_CREATED)
def create_report(payload: Dict[str, Any] | None = None, x_user: str | None = Header(default=None)) -> Dict[str, str]:
    # Create a report bundle immediately in dev and return downloadable URLs
    report_id = str(uuid4())
    user_id = _get_user_id(x_user)
    # Sprint 10: enforce credits
    available = int(credits_store.get(user_id, 0))
    if available <= 0:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient credits")
    # Reserve one credit
    credits_store[user_id] = available - 1
    credit_spends.append({"user_id": user_id, "report_id": report_id, "ts": time.time(), "amount": 1})
    lat = 30.2672
    lon = -97.7431
    if isinstance(payload, dict):
        # Prefer explicit coordinates if provided
        lat = float(payload.get("lat", lat))
        lon = float(payload.get("lon", lon))
        # If only a well_id is provided, try to find coordinates from stub list
        well_id = payload.get("well_id")
        if well_id and not ("lat" in payload and "lon" in payload):
            for it in STUB_ITEMS:
                if it["id"] == well_id:
                    lat = float(it.get("lat", lat))
                    lon = float(it.get("lon", lon))
                    break

    # Write artifacts to a local folder in dev
    out = build_bundle(output_dir=".reports", lat=lat, lon=lon)

    reports_store[report_id] = {
        "status": "ready",
        "paths": out,
        "pdf_url": f"/v1/reports/{report_id}/download?type=pdf",
        "zip_url": f"/v1/reports/{report_id}/download?type=zip",
    }
    return {"report_id": report_id}


@app.get("/v1/reports/{report_id}")
def get_report(report_id: str) -> Dict[str, Any]:
    report = reports_store.get(report_id)
    if not report:
        # Minimal empty job if unknown
        return {"status": "pending"}
    return {
        "status": report.get("status", "pending"),
        "pdf_url": report.get("pdf_url"),
        "zip_url": report.get("zip_url"),
    }


@app.get("/v1/reports/{report_id}/html", response_class=HTMLResponse)
def get_report_html(report_id: str) -> HTMLResponse:
    report = reports_store.get(report_id) or {}
    well_id = report.get("well_id") or "—"
    html = f"""
    <!doctype html>
    <html lang=\"en\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Well Report {report_id}</title>
        <style>
          body {{ font: 14px/1.5 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; color:#0b0b0c; }}
          .wrap {{ max-width: 800px; margin: 24px auto; padding: 0 16px; }}
          .card {{ border:1px solid #e5e7eb; border-radius: 12px; padding:16px; }}
          h1 {{ margin: 0 0 8px 0; }}
          small {{ color:#6b7280; }}
          table {{ width:100%; border-collapse: collapse; margin-top:12px; }}
          td,th {{ border:1px solid #e5e7eb; padding:8px; text-align:left; }}
        </style>
      </head>
      <body>
        <div class=\"wrap\">
          <h1>Well Report</h1>
          <div class=\"card\">
            <div><strong>Report ID:</strong> {report_id}</div>
            <div><strong>Well ID:</strong> {well_id}</div>
            <div style=\"margin-top:8px\"><small>Stub HTML for printing. Sprint 9 will render a real template later.</small></div>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/v1/reports/{report_id}/download")
def download_report_file(report_id: str, type: str = "pdf"):
    report = reports_store.get(report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    paths: Dict[str, str] = report.get("paths", {})
    key = type.lower()
    if key not in {"pdf", "zip", "csv", "geojson", "manifest"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid type")
    path = paths.get(key)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not available")
    media = "application/pdf" if key == "pdf" else ("application/zip" if key == "zip" else "application/octet-stream")
    filename = os.path.basename(path)
    return FileResponse(path, media_type=media, filename=filename)


# Sprint 9: signed download proxy endpoints
@app.get("/v1/reports/{report_id}/signed")
def get_signed_download(report_id: str) -> Dict[str, str]:
    # short-lived token (5 minutes)
    object_key = f"reports/{report_id}/report.pdf"
    token = sign_payload({"k": object_key, "exp": time.time() + 300})
    return {"token": token}


@app.get("/v1/download")
def proxy_signed_download(token: str):
    payload = verify_token(token)
    object_key = payload.get("k")
    if not object_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing key")
    # Dev: redirect to fake path; prod would stream from S3/R2
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/fake/{object_key}")


# ===== Sprint 10: Billing (test mode) =====
@app.post("/billing/checkout")
def billing_checkout(credits: int = 1, x_user: str | None = Header(default=None)) -> Dict[str, Any]:
    user_id = _get_user_id(x_user)
    add = max(int(credits), 1)
    credits_store[user_id] = credits_store.get(user_id, 0) + add
    credit_grants.append({"user_id": user_id, "ts": time.time(), "amount": add, "source": "checkout_test"})
    return {"status": "success", "granted": add, "credits_available": credits_store[user_id]}


@app.post("/billing/webhook")
def billing_webhook(event: Dict[str, Any]) -> Dict[str, Any]:
    user_id = str(event.get("user_id", "demo"))
    add = max(int(event.get("credits", 1)), 1)
    credits_store[user_id] = credits_store.get(user_id, 0) + add
    credit_grants.append({"user_id": user_id, "ts": time.time(), "amount": add, "source": "webhook_test"})
    return {"ok": True}


@app.get("/billing/credits")
def billing_credits(x_user: str | None = Header(default=None)) -> Dict[str, Any]:
    user_id = _get_user_id(x_user)
    return {"user_id": user_id, "credits_available": credits_store.get(user_id, 0)}


# ===== Sprint 10: Alerts CRUD =====
@app.post("/v1/alerts", status_code=status.HTTP_201_CREATED)
def create_alert(payload: Dict[str, Any], x_user: str | None = Header(default=None)) -> Dict[str, str]:
    user_id = _get_user_id(x_user)
    try:
        lat = float(payload["lat"])
        lon = float(payload["lon"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="lat/lon required")
    alert_id = str(uuid4())
    alert = {
        "id": alert_id,
        "user_id": user_id,
        "lat": lat,
        "lon": lon,
        "radius_m": int(payload.get("radius_m", 1609)),
        "email": payload.get("email"),
        "webhook_url": payload.get("webhook_url"),
        "status": "active",
        "created_at": time.time(),
    }
    alerts_store[alert_id] = alert
    return {"id": alert_id}


@app.get("/v1/alerts")
def list_alerts(x_user: str | None = Header(default=None)) -> Dict[str, Any]:
    user_id = _get_user_id(x_user)
    items = [a for a in alerts_store.values() if a.get("user_id") == user_id]
    return {"items": items}


@app.get("/v1/alerts/{alert_id}")
def get_alert(alert_id: str, x_user: str | None = Header(default=None)) -> Dict[str, Any]:
    user_id = _get_user_id(x_user)
    alert = alerts_store.get(alert_id)
    if not alert or alert.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@app.delete("/v1/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: str, x_user: str | None = Header(default=None)) -> None:
    user_id = _get_user_id(x_user)
    alert = alerts_store.get(alert_id)
    if not alert or alert.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    del alerts_store[alert_id]
    return None


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

