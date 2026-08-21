#!/usr/bin/env python3
"""Build Nexus startup one-pagers from JSON data + shared template."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data"
TEMPLATE_CSS = ROOT / "onepagers" / "template" / "styles.css"
OUT_REPO = ROOT / "onepagers" / "sites"
OUT_ARCHIVE = Path("/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20")


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def main() -> None:
    OUT_REPO.mkdir(parents=True, exist_ok=True)
    for json_path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(json_path.read_text())
        slug = data["slug"]
        print(f"Built {slug}")


if __name__ == "__main__":
    main()
