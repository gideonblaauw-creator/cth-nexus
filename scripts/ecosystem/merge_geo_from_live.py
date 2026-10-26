#!/usr/bin/env python3
"""Merge geocode results into actors.raw.json (GitHub-first; no live /opt reads)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from prepare_geo import geocode_actor

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "static" / "ecosystem" / "data" / "actors.raw.json"
GEO_BY_ID = REPO / "ops" / "ecosystem" / "geocode-by-id.json"
CACHE = REPO / "ops" / "ecosystem" / "geocode-cache.json"
APPLY_SV = REPO / "ops" / "ecosystem" / "apply_sv_geocodes.py"
CO_V1_REPORT = REPO / "ops" / "ecosystem" / "colombia-v1-merge-report.json"


def colombia_v1_added_ids() -> set[str] | None:
    """When building Colombia v1, only merge geo onto newly added actor ids."""
    if not CO_V1_REPORT.is_file():
        return None
    doc = json.loads(CO_V1_REPORT.read_text(encoding="utf-8"))
    ids = doc.get("added_ids")
    if not ids:
        return None
    return set(ids)


def is_sv_city_guess(geo: dict) -> bool:
    if not geo:
        return False
    src = (geo.get("source_url") or "").lower()
    return geo.get("precision") == "city" or "actor-city" in src


def run_sv_geocode_policy() -> None:
    """Refresh geocode-by-id.json for sv-* (address overrides or country badge; no city guesses)."""
    if not APPLY_SV.is_file():
        return
    subprocess.run([sys.executable, str(APPLY_SV)], cwd=REPO, check=True)


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
            if aid.startswith("sv-"):
                # SV pins are governed by apply_sv_geocodes + geocode-by-id, not live/cache city guesses.
                continue
            if isinstance(row, dict) and row.get("geo"):
                out[aid] = row["geo"]
    return out


def main() -> None:
    touch_only = colombia_v1_added_ids()
    if touch_only is None:
        run_sv_geocode_policy()
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}")
    actors = json.loads(RAW.read_text(encoding="utf-8"))
    merged = geo_by_id()
    n = 0
    for a in actors:
        aid = a["id"]
        if touch_only is not None and aid not in touch_only:
            continue
        g = merged.get(aid)
        if aid.startswith("sv-") and is_sv_city_guess(g or {}):
            g = None
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
