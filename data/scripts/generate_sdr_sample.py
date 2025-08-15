#!/usr/bin/env python3
"""
Generate a synthetic SDR sample CSV with >=200 rows across >=5 counties.

Usage:
  python data/scripts/generate_sdr_sample.py data/fixtures/sdr_sample.csv
"""
from __future__ import annotations

import csv
import os
import random
import sys
from datetime import datetime, timedelta


def random_date(start_year: int = 2012, end_year: int = 2024) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta_days = (end - start).days
    d = start + timedelta(days=random.randint(0, delta_days))
    return d.strftime("%Y-%m-%d")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python generate_sdr_sample.py <output_csv>")
        return 2
    output_csv = sys.argv[1]
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    random.seed(42)

    counties = [
        ("Travis", 30.2672, -97.7431),
        ("Harris", 29.7604, -95.3698),
        ("Dallas", 32.7767, -96.7970),
        ("Bexar", 29.4241, -98.4936),
        ("Tarrant", 32.7555, -97.3308),
        ("Williamson", 30.6333, -97.6770),
    ]

    rows_per_county = 40  # 6 counties * 40 = 240 rows

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "owner_name", "address", "county", "lat", "lon", "depth_ft", "date_completed"])
        seq = 1
        for county, base_lat, base_lon in counties:
            for _ in range(rows_per_county):
                lat = base_lat + random.uniform(-0.2, 0.2)
                lon = base_lon + random.uniform(-0.2, 0.2)
                depth = random.randint(100, 700)
                owner = random.choice([
                    "Smith Farms", "River City Estates", "Metro Water Co", "Hill Country Ranch",
                    "Lone Star Ranch", "Gulf Coast Water", "Plains Cotton", "Round Rock ISD",
                ])
                addr_num = random.randint(100, 9999)
                street = random.choice(["Main St", "Oak Ave", "Pecan Dr", "Maple Rd", "Cedar Ln"]) 
                well_id = f"SDR-{seq:06d}"
                w.writerow([
                    well_id,
                    owner,
                    f"{addr_num} {street}",
                    county,
                    f"{lat:.6f}",
                    f"{lon:.6f}",
                    depth,
                    random_date(),
                ])
                seq += 1

    print(f"Wrote sample CSV: {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


