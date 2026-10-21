#!/usr/bin/env python3
"""Merge geocode results into actors.raw.json (GitHub-first; no live /opt reads)."""
from __future__ import annotations

import json
from pathlib import Path

from prepare_geo import geocode_actor

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "static" / "ecosystem" / "data" / "actors.raw.json"
GEO_BY_ID = REPO / "ops" / "ecosystem" / "geocode-by-id.json"
CACHE = REPO / "ops" / "ecosystem" / "geocode-cache.json"


def geo_by_id() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if GEO_BY_ID.is_file():
        blob = json.loads(GEO_BY_ID.read_text(encoding="utf-8"))
        for aid, g in blob.items():
            if isinstance(g, dict):
                out[aid] = g
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
        for aid, row in cache.items():
            if isinstance(row, dict) and row.get("geo"):
                out[aid] = row["geo"]
    return out


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}")
    actors = json.loads(RAW.read_text(encoding="utf-8"))
    merged = geo_by_id()
    n = 0
    for a in actors:
        g = merged.get(a["id"])
        if g:
            a["geo"] = g
            if g.get("city") and not a.get("city"):
                a["city"] = g["city"]
            n += 1
            continue
        # Enrichment-only actors (e.g. Peru #58) without geocode-by-id: country badge only.
        base = {k: v for k, v in a.items() if k != "geo"}
        geocoded = geocode_actor({
            **base,
            "geo": {"precision": "country", "country": a.get("country")},
        })
        a["geo"] = geocoded["geo"]
    RAW.write_text(json.dumps(actors, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Merged geo onto {n}/{len(actors)} actors in {RAW}")


if __name__ == "__main__":
    main()
