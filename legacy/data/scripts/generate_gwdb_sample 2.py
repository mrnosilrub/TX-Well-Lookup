#!/usr/bin/env python3

import csv
import os
import random
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python generate_gwdb_sample.py <output_csv>")
        return 2
    output_csv = sys.argv[1]
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    random.seed(7)
    # roughly near some counties used in SDR sample
    seeds = [
        ("GWDB-000001", "Travis", 410, "Trinity", 30.2672, -97.7431),
        ("GWDB-000002", "Harris", 580, "Gulf Coast", 29.7604, -95.3698),
        ("GWDB-000003", "Dallas", 460, "Woodbine", 32.7767, -96.7970),
        ("GWDB-000004", "Bexar", 430, "Edwards", 29.4241, -98.4936),
        ("GWDB-000005", "Tarrant", 390, "Trinity", 32.7555, -97.3308),
        ("GWDB-000006", "Williamson", 520, "Edwards", 30.6333, -97.6770),
    ]

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "county", "total_depth_ft", "aquifer", "lat", "lon"])
        for rid, county, depth, aquifer, lat, lon in seeds:
            # exact seeds to guarantee some spatial joins with SDR centers
            w.writerow([rid, county, depth, aquifer, f"{lat:.6f}", f"{lon:.6f}"])

    print(f"Wrote GWDB sample CSV: {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


