#!/usr/bin/env python3
import csv
import os
import random
from datetime import datetime, timedelta


def rand_date(start_year=2020, end_year=2025) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    d = start + timedelta(days=random.randint(0, delta))
    return d.strftime("%Y-%m-%d")


def write_permits(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = []
    seeds = [
        ("42345678901234", "Acme Oil Co", "APPROVED", 29.7604, -95.3698),
        ("42345678901235", "Bluebonnet Energy", "PENDING", 30.2672, -97.7431),
        ("42345678901236", "Longhorn Petroleum", "APPROVED", 32.7767, -96.7970),
        ("42345678901237", "Rio Grande Gas", "APPROVED", 29.4241, -98.4936),
        ("42345678901238", "Trinity Resources", "DENIED", 32.7555, -97.3308),
    ]
    for api14, operator, status, lat, lon in seeds:
        rows.append({
            "api14": api14,
            "operator": operator,
            "status": status,
            "permit_date": rand_date(),
            "lat": f"{lat:.6f}",
            "lon": f"{lon:.6f}",
        })
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["api14", "operator", "status", "permit_date", "lat", "lon"])
        w.writeheader()
        w.writerows(rows)


def write_wellbores(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = []
    seeds = [
        ("42345678901234", "A", 29.7605, -95.3697),
        ("42345678901234", "B", 29.7602, -95.3699),
        ("42345678901235", "A", 30.2671, -97.7430),
        ("42345678901236", "A", 32.7766, -96.7972),
        ("42345678901237", "A", 29.4240, -98.4937),
    ]
    for api14, wb, lat, lon in seeds:
        rows.append({
            "api14": api14,
            "wellbore": wb,
            "lat": f"{lat:.6f}",
            "lon": f"{lon:.6f}",
        })
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["api14", "wellbore", "lat", "lon"])
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    write_permits("data/fixtures/rrc_permits.csv")
    write_wellbores("data/fixtures/rrc_wellbores.csv")
    print("Wrote RRC samples: data/fixtures/rrc_permits.csv, data/fixtures/rrc_wellbores.csv")


