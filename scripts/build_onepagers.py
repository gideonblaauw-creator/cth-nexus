#!/usr/bin/env python3
"""Build Nexus startup one-pagers from JSON data + shared template."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data"
TEMPLATE_CSS = ROOT / "onepagers" / "template" / "styles.css"
OUT_REPO = ROOT / "onepagers" / "sites"
OUT_ARCHIVE = Path("/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20")


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def bar_chart(cols: list[dict], max_h: int = 90) -> str:
    vals = [c.get("height", 30) for c in cols]
    mx = max(vals) if vals else 1
    parts = ['<div class="rev-chart">']
    for c in cols:
        h = max(4, int(c.get("height", 30) * max_h / mx))
        cls = "proj" if c.get("proj") else "actual"
        parts.append(
            f'<div class="rev-col"><div class="rev-val">{c["val"]}</div>'
            f'<div class="rev-bar {cls}" style="height:{h}px;"></div>'
            f'<div class="rev-label">{c["label"]}</div></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def main() -> None:
    OUT_REPO.mkdir(parents=True, exist_ok=True)
    for json_path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(json_path.read_text())
        print(f"Built {data['slug']}")


if __name__ == "__main__":
    main()
