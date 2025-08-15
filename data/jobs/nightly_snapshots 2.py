#!/usr/bin/env python3
"""
Nightly snapshot job that (for now):
  1) Ensures SDR and GWDB sample fixtures exist
  2) Loads SDR into well_reports and GWDB into gwdb_wells
  3) Links SDR↔GWDB within 50m
"""

import os
from pathlib import Path

from data.sources.twdb_sdr import upsert_sdr_from_csv
from data.sources.twdb_gwdb import upsert_gwdb_from_csv
from data.transforms.link_sdr_gwdb import link_within_distance


def main() -> int:
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

    n_sdr = upsert_sdr_from_csv(str(sdr_csv), db_url)
    n_gwdb = upsert_gwdb_from_csv(str(gwdb_csv), db_url)
    n_links = link_within_distance(db_url, radius_m=50.0)
    print(f"SDR upserted: {n_sdr}; GWDB upserted: {n_gwdb}; Links: {n_links}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


