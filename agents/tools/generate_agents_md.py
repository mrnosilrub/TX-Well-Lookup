#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


HEADER = """# Agents — Continuity Guide

Note: This file is auto-generated. Do not edit manually. Update generators under `agents/tools/`.

This guide documents automation tasks and conventions so any agent (human or AI) can quickly regain context.
Generated at: {ts}
"""


WIPE_SQL = """
BEGIN;
DROP SCHEMA IF EXISTS ground_truth CASCADE; -- if present
DROP SCHEMA IF EXISTS sdr_raw CASCADE;
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
CREATE SCHEMA sdr_raw; -- legacy staging, optional
CREATE SCHEMA ground_truth; -- loader will recreate as needed
COMMIT;
"""


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Generate agents/README.md from workflows")
    ap.add_argument("--workflows-dir", default=".github/workflows")
    ap.add_argument("--out", default="agents/README.md")
    return ap.parse_args()


def find_workflows(path: str) -> List[Path]:
    root = Path(path)
    if not root.exists():
        return []
    files: List[Path] = []
    for p in sorted(root.glob("*.yml")):
        files.append(p)
    for p in sorted(root.glob("*.yaml")):
        files.append(p)
    return files


def collect_secrets_from_obj(obj: Any, found: Set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            collect_secrets_from_obj(k, found)
            collect_secrets_from_obj(v, found)
    elif isinstance(obj, list):
        for it in obj:
            collect_secrets_from_obj(it, found)
    elif isinstance(obj, str):
        for m in re.findall(r"secrets\.([A-Z0-9_]+)", obj):
            found.add(m)


def simplify_triggers(on_node: Any) -> List[str]:
    out: List[str] = []
    if isinstance(on_node, dict):
        for key, val in on_node.items():
            if isinstance(val, dict) and "paths" in val:
                paths = val.get("paths", [])
                if isinstance(paths, list):
                    out.append(f"{key} (paths: {', '.join(paths)})")
                else:
                    out.append(str(key))
            else:
                out.append(str(key))
    elif isinstance(on_node, list):
        out.extend([str(x) for x in on_node])
    elif isinstance(on_node, str):
        out.append(on_node)
    return out


def render_workflows_section(workflows: List[Tuple[str, Dict[str, Any]]]) -> str:
    lines: List[str] = []
    lines.append("\n## Workflows")
    if not workflows:
        lines.append("\n_No workflows found under .github/workflows._")
        return "\n".join(lines)
    for path, data in workflows:
        name = str(data.get("name") or Path(path).name)
        triggers = simplify_triggers(data.get("on", {}))
        secrets: Set[str] = set()
        collect_secrets_from_obj(data.get("jobs", {}), secrets)
        collect_secrets_from_obj(data.get("env", {}), secrets)
        lines.append(f"\n### {name}")
        lines.append(f"- **file**: `{path}`")
        if triggers:
            lines.append(f"- **triggers**: {', '.join(triggers)}")
        if secrets:
            lines.append(f"- **secrets referenced**: {', '.join(sorted(secrets))}")
    return "\n".join(lines)


def render_env_section(all_secrets: Set[str]) -> str:
    lines: List[str] = []
    lines.append("\n## Environments & Secrets")
    if all_secrets:
        lines.append("- Secrets referenced in workflows: " + ", ".join(sorted(all_secrets)))
    lines.append("- Neon Postgres: `DATABASE_URL` (scoped per environment in GitHub)")
    lines.append("- SDR zip: `SDR_ZIP_URL` (or RAW_SDR_* with STORAGE_* for S3-compatible storage)")
    return "\n".join(lines)


def render_ground_truth_section() -> str:
    return """
\n## Ground Truth (1:1 SDR)
- Loader: `ground_truth/loader/load_ground_truth.py`
  - Workflow: `.github/workflows/ground-truth-load.yml` (push on `ground_truth/**`, or manual)
- Schema doc generator: `ground_truth/tools/generate_schema_md.py`
  - Workflow: `.github/workflows/ground-truth-schema.yml` (manual)
"""


def render_ops_section() -> str:
    return f"""
\n## Common Ops
- Wipe database schemas (dev only):
```sql
{WIPE_SQL.strip()}
```
- Verify ground truth: run the schema doc workflow (manual) and review `ground_truth/SCHEMA.md`
"""


def render_conventions_section() -> str:
    return """
\n## Conventions
- Do not transform in ground_truth; columns are TEXT; original header names preserved via column comments
- Non-tabular docs are ignored by the loader (ReadMe/Dictionary/etc.)
- Loader sanitizes inconsistent rows (pads/truncates to header width)
"""


def main() -> int:
    args = parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    files = find_workflows(args.workflows_dir)
    workflows: List[Tuple[str, Dict[str, Any]]] = []
    all_secrets: Set[str] = set()
    for p in files:
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        workflows.append((str(p), data))
        collect_secrets_from_obj(data, all_secrets)

    parts: List[str] = []
    parts.append(HEADER.format(ts=ts))
    parts.append(render_env_section(all_secrets))
    parts.append(render_ground_truth_section())
    parts.append(render_workflows_section(workflows))
    parts.append(render_ops_section())
    parts.append(render_conventions_section())
    content = "\n".join(parts).strip() + "\n"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    old = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
    if old.strip() != content.strip():
        out_path.write_text(content, encoding="utf-8")
        print(f"updated {out_path}")
    else:
        print("no changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


