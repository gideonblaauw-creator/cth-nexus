#!/usr/bin/env python3
"""Build portfolio /s/ pages for one batch index from data/sheet-s-pages/batches.json."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCHES = ROOT / "data" / "sheet-s-pages" / "batches.json"
BUILDER = ROOT / "scripts" / "build_onepagers.py"

# Slugs aligned with portfolio cards (website domain or established Nexus slug pattern).
BATCH_SLUGS: dict[str, str] = {
    "Sunco Energy": "suncolombia",
    "SunColombia": "suncolombia",
    "WËIA": "weia",
    "WEIA": "weia",
    "Zhana": "zhana-solutions",
    "AInwater": "ainwater",
    "Air4U": "air4u",
    "AIR 4U": "air4u",
}


def main() -> None:
    batch_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batches = json.loads(BATCHES.read_text())
    batch = batches[batch_idx]
    slugs = []
    for row in batch:
        slug = BATCH_SLUGS.get(row["startup"])
        if slug:
            slugs.append(slug)
    if not slugs:
        print("No slugs resolved for batch", batch_idx, file=sys.stderr)
        sys.exit(1)
    subprocess.run([sys.executable, str(BUILDER), *slugs], check=True)
    print("Built batch", batch_idx, ":", ", ".join(slugs))


if __name__ == "__main__":
    main()
