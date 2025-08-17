import csv
import io
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import psycopg2
from fpdf import FPDF


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	r = 6371000.0
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	dphi = math.radians(lat2 - lat1)
	dlam = math.radians(lon2 - lon1)
	a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return r * c


def _fetch_from_db(db_url: str, lat: float, lon: float, radius_m: int, limit: int) -> List[Dict[str, Any]]:
	with psycopg2.connect(db_url) as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT id,
				       owner_name AS name,
				       county,
				       ST_Y(geom) AS lat,
				       ST_X(geom) AS lon,
				       depth_ft,
				       date_completed::text AS date_completed
				FROM well_reports
				WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s)
				LIMIT %s
				""",
				(lon, lat, radius_m, limit),
			)
			cols = [c[0] for c in cur.description]
			rows = [dict(zip(cols, r)) for r in cur.fetchall()]
	return rows


def _fetch_from_fixture(repo_root: Path, lat: float, lon: float, radius_m: int, limit: int) -> List[Dict[str, Any]]:
	fixture = repo_root / "data/fixtures/wells_stub.json"
	if not fixture.exists():
		return []
	data = json.loads(fixture.read_text())
	items = data.get("items", []) if isinstance(data, dict) else []
	filtered: List[Dict[str, Any]] = []
	for it in items:
		try:
			d = _haversine_m(lat, lon, float(it["lat"]), float(it["lon"]))
			if d <= radius_m:
				filtered.append({
					"id": it.get("id"),
					"name": it.get("name"),
					"county": it.get("county"),
					"lat": it.get("lat"),
					"lon": it.get("lon"),
					"depth_ft": it.get("depth_ft"),
					"date_completed": it.get("date_completed"),
				})
		except Exception:
			continue
	return filtered[:limit]


def fetch_wells(lat: float, lon: float, radius_m: int = 1609, limit: int = 500) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
	repo_root = Path(__file__).resolve().parents[2]
	db_url = os.getenv("DATABASE_URL")
	if db_url:
		rows = _fetch_from_db(db_url, lat, lon, radius_m, limit)
	else:
		rows = _fetch_from_fixture(repo_root, lat, lon, radius_m, limit)
	params = {"lat": lat, "lon": lon, "radius_m": radius_m, "limit": limit}
	return rows, params


def write_csv(rows: List[Dict[str, Any]], path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	fieldnames = ["id", "name", "county", "lat", "lon", "depth_ft", "date_completed"]
	with path.open("w", newline="", encoding="utf-8") as f:
		w = csv.DictWriter(f, fieldnames=fieldnames)
		w.writeheader()
		for r in rows:
			w.writerow({k: r.get(k) for k in fieldnames})


def write_geojson(rows: List[Dict[str, Any]], path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	fc = {
		"type": "FeatureCollection",
		"features": [
			{
				"type": "Feature",
				"geometry": {"type": "Point", "coordinates": [r.get("lon"), r.get("lat")]},
				"properties": {
					"id": r.get("id"),
					"name": r.get("name"),
					"county": r.get("county"),
					"depth_ft": r.get("depth_ft"),
					"date_completed": r.get("date_completed"),
				},
			}
			for r in rows
		],
	}
	path.write_text(json.dumps(fc))


def write_manifest(rows: List[Dict[str, Any]], params: Dict[str, Any], path: Path, files: Dict[str, str]) -> None:
	manifest = {
		"created_at": datetime.now(timezone.utc).isoformat(),
		"params": params,
		"count": len(rows),
		"files": files,
		"sources": [
			{"name": "TWDB SDR", "license": "Public", "url": "https://www.twdb.texas.gov/"},
			{"name": "TX RRC", "license": "Public", "url": "https://www.rrc.texas.gov/"},
		],
	}
	path.write_text(json.dumps(manifest, indent=2))


def write_pdf(rows: List[Dict[str, Any]], params: Dict[str, Any], path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	pdf = FPDF()
	pdf.set_auto_page_break(auto=True, margin=15)
	pdf.add_page()
	pdf.set_font("Helvetica", size=14)
	pdf.cell(0, 10, "TX Well Lookup - Report", ln=True)
	pdf.set_font("Helvetica", size=10)
	pdf.cell(0, 8, f"Params: lat={params['lat']}, lon={params['lon']}, radius_m={params['radius_m']}", ln=True)
	pdf.cell(0, 8, f"Count: {len(rows)}", ln=True)
	pdf.ln(4)
	for r in rows[:50]:
		line = f"{r.get('id')} - {r.get('name')} ({r.get('county')}), depth {r.get('depth_ft')} ft"
		pdf.cell(0, 6, line, ln=True)
	pdf.output(str(path))


def build_bundle(output_dir: str, lat: float, lon: float, radius_m: int = 1609, limit: int = 500) -> Dict[str, str]:
	rows, params = fetch_wells(lat=lat, lon=lon, radius_m=radius_m, limit=limit)
	out = Path(output_dir)
	out.mkdir(parents=True, exist_ok=True)
	tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
	base = out / f"report_{tag}"
	csv_path = base.with_suffix(".csv")
	geojson_path = base.with_suffix(".geojson")
	manifest_path = base.with_suffix(".json")
	pdf_path = base.with_suffix(".pdf")
	zip_path = base.with_suffix(".zip")

	write_csv(rows, csv_path)
	write_geojson(rows, geojson_path)
	write_pdf(rows, params, pdf_path)
	write_manifest(rows, params, manifest_path, {
		"csv": csv_path.name,
		"geojson": geojson_path.name,
		"pdf": pdf_path.name,
	})

	import zipfile
	with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
		z.write(csv_path, arcname=csv_path.name)
		z.write(geojson_path, arcname=geojson_path.name)
		z.write(manifest_path, arcname=manifest_path.name)
		z.write(pdf_path, arcname=pdf_path.name)

	return {
		"csv": str(csv_path),
		"geojson": str(geojson_path),
		"manifest": str(manifest_path),
		"pdf": str(pdf_path),
		"zip": str(zip_path),
	}


