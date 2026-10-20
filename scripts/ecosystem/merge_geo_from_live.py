#!/usr/bin/env python3
"""Merge geo from wt-eco-geo / live ecosystem actors into wt-eco-d3 raw bundle."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "static" / "ecosystem" / "data" / "actors.raw.json"
SOURCES = [
    Path("/home/debian/wt-eco-geo/static/ecosystem/data/actors.json"),
    Path("/opt/cth-nexus/static/ecosystem/data/actors.json"),
]
CACHE = Path("/home/debian/wt-eco-geo/ops/ecosystem/geocode-cache.json")


def geo_by_id() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
        for aid, row in cache.items():
            if isinstance(row, dict) and row.get("geo"):
                out[aid] = row["geo"]
    for src in SOURCES:
        if not src.is_file():
            continue
        for a in json.loads(src.read_text(encoding="utf-8")):
            g = a.get("geo")
            if g and isinstance(g, dict):
                out[a["id"]] = g
    return out


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}")
    actors = json.loads(RAW.read_text(encoding="utf-8"))
    merged = geo_by_id()
    n = 0
    for a in actors:
        g = merged.get(a["id"])
        if not g:
            continue
        a["geo"] = g
        if g.get("city") and not a.get("city"):
            a["city"] = g["city"]
        n += 1
    RAW.write_text(json.dumps(actors, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Merged geo onto {n}/{len(actors)} actors in {RAW}")


if __name__ == "__main__":
    main()
