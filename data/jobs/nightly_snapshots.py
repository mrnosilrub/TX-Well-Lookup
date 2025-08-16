#!/usr/bin/env python3
"""
Nightly snapshot job that (for now):
  1) Ensures SDR and GWDB sample fixtures exist
  2) Loads SDR into well_reports and GWDB into gwdb_wells
  3) Links SDR↔GWDB within 50m
"""

import os
import time
from pathlib import Path

from data.sources.twdb_sdr import upsert_sdr_from_csv, upsert_sdr_from_twdb_raw
from data.sources.twdb_gwdb import upsert_gwdb_from_csv
from data.transforms.link_sdr_gwdb import link_within_distance
from data.sources.sdr_web_fetch import ensure_sdr_from_web


def main() -> int:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is required")
        return 2

    repo_root = Path(__file__).resolve().parents[2]
    sdr_csv = repo_root / "data/fixtures/sdr_sample.csv"
    raw_sdr_dir = os.getenv("RAW_SDR_DIR") or str(repo_root / "data/raw_data/SDRDownload/SDRDownload")
    gwdb_csv = repo_root / "data/fixtures/gwdb_sample.csv"

    if not sdr_csv.exists():
        print(f"Missing SDR sample: {sdr_csv}")
        return 2
    if not gwdb_csv.exists():
        print(f"Missing GWDB sample: {gwdb_csv}")
        return 2

    t0 = time.time()
    # Accept either raw_sdr_dir/WellData.txt or raw_sdr_dir/SDRDownload/WellData.txt
    raw_sdr_ok = False
    sdr_candidates = [
        os.path.join(raw_sdr_dir, "WellData.txt"),
        os.path.join(raw_sdr_dir, "SDRDownload", "WellData.txt"),
    ]
    for candidate in sdr_candidates:
        if os.path.isfile(candidate):
            raw_sdr_ok = True
            # Normalize to the parent folder of the detected file
            raw_sdr_dir = os.path.dirname(candidate)
            break
    if not raw_sdr_ok:
        zip_url = os.getenv("SDR_ZIP_URL")
        base_url = os.getenv("SDR_BASE_URL")
        if zip_url or base_url:
            try:
                print("SDR raw missing; attempting web fetch...")
                ensure_sdr_from_web(dest_dir=raw_sdr_dir, zip_url=zip_url, base_url=base_url)
                for candidate in sdr_candidates:
                    if os.path.isfile(candidate):
                        raw_sdr_ok = True
                        raw_sdr_dir = os.path.dirname(candidate)
                        break
            except Exception as e:
                print(f"SDR web fetch failed: {e}")
    if raw_sdr_ok:
        n_sdr = upsert_sdr_from_twdb_raw(raw_sdr_dir, db_url, limit=None)
        sdr_source = "twdb_raw"
    else:
        if raw_sdr_dir:
            print(f"TWDB raw not found at {raw_sdr_dir}; falling back to sample CSV")
        n_sdr = upsert_sdr_from_csv(str(sdr_csv), db_url)
        sdr_source = "sample_csv"
    t1 = time.time()
    n_gwdb = upsert_gwdb_from_csv(str(gwdb_csv), db_url)
    t2 = time.time()
    n_links = link_within_distance(db_url, radius_m=50.0)
    t3 = time.time()
    print(
        f"SDR upserted: {n_sdr} (source={sdr_source}, {t1 - t0:.2f}s); "
        f"GWDB upserted: {n_gwdb} ({t2 - t1:.2f}s); "
        f"Links: {n_links} ({t3 - t2:.2f}s)"
    )
    if sdr_source == "sample_csv":
        print("Note: Using sample CSV (no SDR raw detected). Set SDR_ZIP_URL or SDR_BASE_URL to ingest live TWDB data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


