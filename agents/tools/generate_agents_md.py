#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import os


def main() -> int:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = []
    lines.append("# Agents — Continuity Guide")
    lines.append("")
    lines.append("Note: This file is auto-generated. Do not edit manually. Update generators under `agents/tools/`.")
    lines.append("")
    lines.append("This guide documents automation tasks and conventions so any agent (human or AI) can quickly regain context.")
    lines.append(f"Generated at: {generated_at}")
    lines.append("")
    lines.append("")
    lines.append("## Environments & Secrets")
    lines.append("- Secrets referenced in workflows: DATABASE_URL")
    lines.append("- Neon Postgres: `DATABASE_URL` (scoped per environment in GitHub)")
    lines.append("")
    lines.append("")
    lines.append("## Ground Truth (1:1 SDR)")
    lines.append("- Loader: `ground_truth/loader/load_ground_truth.py`")
    lines.append("- Schema doc generator: `ground_truth/tools/generate_schema_md.py`")
    lines.append("")
    lines.append("")
    lines.append("## Workflows")
    lines.append("")
    lines.append("### CI Smoke (DB)")
    lines.append("- **file**: `.github/workflows/ci-smoke.yml`")
    lines.append("")
    lines.append("### Ground Truth Schema Doc")
    lines.append("- **file**: `.github/workflows/ground-truth-schema.yml`")
    lines.append("")
    lines.append("### Update Agents README")
    lines.append("- **file**: `.github/workflows/agents-readme.yml`")
    lines.append("")
    lines.append("")
    lines.append("## Common Ops")
    lines.append("- Verify ground truth: run the schema doc workflow (manual) and review `docs/SCHEMA.md`.")
    lines.append("")
    lines.append("")
    lines.append("## Conventions")
    lines.append("- Do not transform in `ground_truth`; columns are TEXT; original header names preserved via column comments.")
    lines.append("- Non-tabular docs are ignored by the loader (ReadMe/Dictionary/etc.).")
    lines.append("- Loader sanitizes inconsistent rows (pads/trims to header width).")

    os.makedirs(os.path.dirname("agents/README.md"), exist_ok=True)
    with open("agents/README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote agents/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


