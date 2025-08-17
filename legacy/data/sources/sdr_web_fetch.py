"""
Helpers to fetch TWDB SDR data directly from the web (pipe-delimited files).

Usage:
- Provide one of:
  - SDR_ZIP_URL: URL to a zip containing SDRDownload files
  - SDR_BASE_URL: Base URL where WellData.txt and WellCompletion.txt are hosted

The downloader will populate `dest_dir` with the required files so that
`upsert_sdr_from_twdb_raw(dest_dir, ...)` can run.
"""

from __future__ import annotations

import os
import io
import zipfile
from typing import List, Optional

import requests


REQUIRED_FILES: List[str] = [
    "WellData.txt",
    "WellCompletion.txt",
]
# Case-insensitive match map (zip members can vary casing)
REQUIRED_CANON = {name.lower(): name for name in REQUIRED_FILES}


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _resolve_target_dir(dest_dir: str) -> str:
    """Return a directory that ends with 'SDRDownload' exactly once.

    If dest_dir already ends with SDRDownload, use it as-is; otherwise, append it.
    """
    base = os.path.basename(os.path.normpath(dest_dir))
    return dest_dir if base == "SDRDownload" else os.path.join(dest_dir, "SDRDownload")


def download_sdr_zip(zip_url: str, dest_dir: str) -> None:
    _ensure_dir(dest_dir)
    with requests.get(zip_url, stream=True, timeout=60) as r:
        r.raise_for_status()
        content = io.BytesIO()
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                content.write(chunk)
        content.seek(0)
        with zipfile.ZipFile(content) as zf:
            for member in zf.infolist():
                name = member.filename
                # Extract only the files we require, but allow nested paths
                base = os.path.basename(name)
                key = base.lower()
                if key in REQUIRED_CANON:
                    canon = REQUIRED_CANON[key]
                    target_base = _resolve_target_dir(dest_dir)
                    target_path = os.path.join(target_base, canon)
                    _ensure_dir(os.path.dirname(target_path))
                    with zf.open(member) as src, open(target_path, "wb") as dst:
                        dst.write(src.read())


def download_sdr_files(base_url: str, dest_dir: str) -> None:
    _ensure_dir(dest_dir)
    target_base = _resolve_target_dir(dest_dir)
    _ensure_dir(target_base)
    for fname in REQUIRED_FILES:
        url = base_url.rstrip("/") + "/" + fname
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            target_path = os.path.join(target_base, fname)
            with open(target_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 512):
                    if chunk:
                        f.write(chunk)


def ensure_sdr_from_web(dest_dir: str, zip_url: Optional[str], base_url: Optional[str]) -> None:
    # Accept either dest_dir/[files] or dest_dir/SDRDownload/[files]
    target_base = _resolve_target_dir(dest_dir)
    flat_present = all(os.path.exists(os.path.join(dest_dir, f)) for f in REQUIRED_FILES)
    nested_present = all(os.path.exists(os.path.join(target_base, f)) for f in REQUIRED_FILES)
    if flat_present or nested_present:
        return
    if zip_url:
        download_sdr_zip(zip_url=zip_url, dest_dir=dest_dir)
    elif base_url:
        download_sdr_files(base_url=base_url, dest_dir=dest_dir)
    else:
        raise ValueError("Provide SDR_ZIP_URL or SDR_BASE_URL to fetch SDR data")


