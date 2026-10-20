#!/usr/bin/env python3
"""Build CLP26 national portfolio JSON from slice files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLICES = ROOT / "onepagers" / "data" / "clp26-slices"
OUT = ROOT / "nexus-assets" / "clp26-national-shareable.json"


def field(blob: dict, key: str) -> str | None:
    node = blob.get(key)
    if not isinstance(node, dict):
        return None
    v = node.get("value")
    if v is None:
        return None
    if isinstance(v, str) and not v.strip():
        return None
    return str(v)


def main() -> None:
    startups = []
    for path in sorted(SLICES.glob("*.json")):
        data = json.loads(path.read_text())
        slug = data.get("slug") or path.stem
        desc = field(data, "short_description_es") or ""
        ct_raw = field(data, "taxonomy_link")
        ct1 = ""
        if ct_raw and ct_raw.startswith("CT-"):
            ct1 = ct_raw
        startups.append(
            {
                "slug": slug,
                "name": field(data, "name") or slug,
                "country": field(data, "country") or "",
                "website": field(data, "website") or "",
                "program": "CLP26",
                "stage": field(data, "stage") or "national",
                "theme": "",
                "ct1": ct1,
                "desc_en": desc,
                "desc_es": desc,
            }
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"startups": startups}, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(startups)} startups to {OUT}")


if __name__ == "__main__":
    main()
