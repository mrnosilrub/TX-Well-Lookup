#!/usr/bin/env python3
"""
SDR Snapshot & Inspect utility

Responsibilities:
- Walk the extracted SDR directory for .txt files
- For each file, compute size, line count, sha256
- Read header line using latin-1 and split on '|'
- Write first N lines (latin-1) to samples/heads/<name>.head.txt
- Produce a manifest.json with fetched_at, zip_sha256, and per-file metadata

This script intentionally avoids logging raw data contents beyond headers.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from typing import List


@dataclass
class FileSummary:
    name: str
    size_bytes: int
    line_count: int
    sha256: str
    header_fields: List[str]
    sample_path: str


def compute_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def count_lines_binary(file_path: str) -> int:
    """Count lines efficiently in binary mode to avoid decoding costs.

    This counts b"\n" bytes, which matches typical line endings in SDR .txt files.
    """
    line_count = 0
    with open(file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            line_count += chunk.count(b"\n")
    return line_count


def read_header_fields(file_path: str, delimiter: str = "|") -> List[str]:
    with open(file_path, "r", encoding="latin-1", errors="replace") as file_handle:
        header_line = file_handle.readline()
    header_line = header_line.rstrip("\r\n")
    return [field.strip() for field in header_line.split(delimiter)] if header_line else []


def derive_sample_head_path(samples_dir: str, original_filename: str) -> str:
    base_name, _ext = os.path.splitext(original_filename)
    return os.path.join(samples_dir, f"{base_name}.head.txt")


def write_sample_head(source_file_path: str, sample_file_path: str, num_lines: int) -> None:
    os.makedirs(os.path.dirname(sample_file_path), exist_ok=True)
    lines_written = 0
    with open(source_file_path, "r", encoding="latin-1", errors="replace") as reader, \
            open(sample_file_path, "w", encoding="latin-1") as writer:
        # Skip header line
        _ = reader.readline()
        for line in reader:
            writer.write(line)
            lines_written += 1
            if lines_written >= num_lines:
                break


def summarize_file(file_path: str, samples_dir: str, sample_lines: int) -> FileSummary:
    file_name = os.path.basename(file_path)
    size_bytes = os.path.getsize(file_path)
    line_count = count_lines_binary(file_path)
    sha256 = compute_sha256(file_path)
    header_fields = read_header_fields(file_path)
    sample_path_relative = os.path.join("samples", "heads", f"{os.path.splitext(file_name)[0]}.head.txt")
    sample_path_absolute = os.path.join(samples_dir, os.path.basename(sample_path_relative))
    write_sample_head(file_path, sample_path_absolute, sample_lines)
    return FileSummary(
        name=file_name,
        size_bytes=size_bytes,
        line_count=line_count,
        sha256=sha256,
        header_fields=header_fields,
        sample_path=sample_path_relative,
    )


def build_manifest(
    source_dir: str,
    samples_dir: str,
    zip_path: str | None,
    sample_lines: int,
) -> dict:
    # Find .txt files. Try direct directory first, then fall back to recursive search.
    direct_pattern = os.path.join(source_dir, "*.txt")
    file_paths = sorted(glob.glob(direct_pattern))
    if not file_paths:
        recursive_pattern = os.path.join(source_dir, "**", "*.txt")
        file_paths = sorted(glob.glob(recursive_pattern, recursive=True))
    summaries: List[FileSummary] = []
    for file_path in file_paths:
        summaries.append(summarize_file(file_path, samples_dir, sample_lines))

    fetched_at = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    manifest = {
        "fetched_at": fetched_at,
        "zip_sha256": compute_sha256(zip_path) if zip_path and os.path.exists(zip_path) else None,
        "files": [asdict(summary) for summary in summaries],
    }
    return manifest


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SDR Snapshot & Inspect")
    parser.add_argument("--source-dir", required=True, help="Directory containing extracted SDR .txt files")
    parser.add_argument("--samples-dir", required=True, help="Directory to write sample head files")
    parser.add_argument("--manifest", required=True, help="Output path for manifest.json")
    parser.add_argument("--sample-lines", type=int, default=200, help="Number of lines to include in sample heads")
    parser.add_argument("--zip-path", default=None, help="Path to the downloaded SDR ZIP (for sha256)")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    if not os.path.isdir(args.source_dir):
        print(f"Source directory does not exist: {args.source_dir}", file=sys.stderr)
        return 2

    os.makedirs(args.samples_dir, exist_ok=True)

    manifest = build_manifest(
        source_dir=args.source_dir,
        samples_dir=args.samples_dir,
        zip_path=args.zip_path,
        sample_lines=args.sample_lines,
    )

    # Write manifest atomically
    manifest_temp = args.manifest + ".tmp"
    with open(manifest_temp, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    os.replace(manifest_temp, args.manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


