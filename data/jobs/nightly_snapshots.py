#!/usr/bin/env python3
"""
Nightly snapshot job that (for now):
  1) Ensures SDR and GWDB sample fixtures exist
  2) Loads SDR into well_reports and GWDB into gwdb_wells
  3) Links SDR↔GWDB within 50m
"""

import os
from pathlib import Path
from time import perf_counter

from data.sources.twdb_sdr import upsert_sdr_from_csv
from data.sources.twdb_gwdb import upsert_gwdb_from_csv
from data.transforms.link_sdr_gwdb import link_within_distance


def main() -> int:
    start_overall = perf_counter()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is required")
        return 2

    repo_root = Path(__file__).resolve().parents[2]
    sdr_csv = repo_root / "data/fixtures/sdr_sample.csv"
    gwdb_csv = repo_root / "data/fixtures/gwdb_sample.csv"

    if not sdr_csv.exists():
        print(f"Missing SDR sample: {sdr_csv}")
        return 2
    if not gwdb_csv.exists():
        print(f"Missing GWDB sample: {gwdb_csv}")
        return 2

    try:
        t0 = perf_counter()
        n_sdr = upsert_sdr_from_csv(str(sdr_csv), db_url)
        t1 = perf_counter()
        print(f"SDR upserted rows: {n_sdr} in {t1 - t0:.2f}s")

        t2 = perf_counter()
        n_gwdb = upsert_gwdb_from_csv(str(gwdb_csv), db_url)
        t3 = perf_counter()
        print(f"GWDB upserted rows: {n_gwdb} in {t3 - t2:.2f}s")

        t4 = perf_counter()
        n_links = link_within_distance(db_url, radius_m=50.0)
        t5 = perf_counter()
        print(f"Linked pairs total: {n_links} in {t5 - t4:.2f}s (radius=50m)")
    except Exception as exc:
        print(f"Nightly snapshots failed: {exc}")
        return 1

    print(f"Job completed in {perf_counter() - start_overall:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


