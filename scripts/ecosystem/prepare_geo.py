#!/usr/bin/env python3
"""Country-centroid geocode with deterministic jitter (city override later)."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "static" / "ecosystem" / "data"

ANCHORS = {
    "Peru": (-12.0464, -77.0428),
    "El Salvador": (13.6929, -89.2182),
    "Colombia": (4.711, -74.0721),
    "Guatemala": (14.6349, -90.5069),
    "Costa Rica": (9.9281, -84.0907),
}


def jitter(actor_id: str, spread: float = 2.8) -> tuple[float, float]:
    h = hashlib.sha256(actor_id.encode()).hexdigest()
    a = int(h[:8], 16) / 0xFFFFFFFF * 2 * math.pi
    r = (int(h[8:16], 16) / 0xFFFFFFFF) ** 0.5 * spread
    return r * math.cos(a), r * math.sin(a)


def geocode_actor(a: dict) -> dict:
    """Fallback only: country-level placeholder (no jitter, no map pin)."""
    existing = a.get("geo") or {}
    prec = existing.get("precision")
    if prec in ("address", "city") and existing.get("lat") is not None:
        return {**a, "geo": existing}
    if prec == "country":
        return {**a, "geo": existing}
    country = a.get("country") or "Peru"
    out = {
        **a,
        "geo": {
            "lat": None,
            "lng": None,
            "address": None,
            "city": a.get("city"),
            "country": country,
            "precision": "country",
            "source_url": existing.get("source_url"),
        },
    }
    return out


def main() -> None:
    src = DATA / "actors.raw.json"
    dst = DATA / "actors.json"
    if src.exists():
        actors = json.loads(src.read_text(encoding="utf-8"))
    else:
        actors = json.loads(dst.read_text(encoding="utf-8"))
    enriched = [geocode_actor(a) for a in actors]
    dst.write_text(json.dumps(enriched, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Geocoded {len(enriched)} actors → {dst}")


if __name__ == "__main__":
    main()
