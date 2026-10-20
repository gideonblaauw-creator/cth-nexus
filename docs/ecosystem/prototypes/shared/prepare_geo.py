#!/usr/bin/env python3
"""Derive lat/lng for prototype maps from actors.json (no external geocoder)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent.parent / "prototype" / "data"
OUT = ROOT / "actors-geo.json"

ANCHORS = {
    "Peru": (-12.0464, -77.0428),
    "El Salvador": (13.6929, -89.2182),
    "Colombia": (4.711, -74.0721),
    "Guatemala": (14.6349, -90.5069),
    "Costa Rica": (9.9281, -84.0907),
}


def jitter(actor_id: str, spread: float = 2.8):
    h = hashlib.sha256(actor_id.encode()).hexdigest()
    a = int(h[:8], 16) / 0xFFFFFFFF * 6.28318
    r = (int(h[8:16], 16) / 0xFFFFFFFF) ** 0.5 * spread
    return r * __import__("math").cos(a), r * __import__("math").sin(a)


def main():
    actors = json.loads((DATA / "actors.json").read_text())
    enriched = []
    for a in actors:
        country = a.get("country") or "Peru"
        base = ANCHORS.get(country, (-15.0, -60.0))
        if a.get("city") == "San Salvador":
            base = (13.6929, -89.2182)
        dx, dy = jitter(a["id"], 3.2 if country == "Peru" else 1.4)
        lat = base[0] + dx
        lng = base[1] + dy
        enriched.append({**a, "geo": {"lat": round(lat, 5), "lng": round(lng, 5)}})
    OUT.write_text(json.dumps(enriched, ensure_ascii=False, indent=2) + "\n")
    rel_src = DATA / "relations.json"
    rel_dst = ROOT / "relations.json"
    rel_dst.write_text(rel_src.read_text())
    print(f"Wrote {len(enriched)} actors → {OUT}")
    print(f"Copied relations → {rel_dst}")


if __name__ == "__main__":
    main()
