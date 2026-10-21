#!/usr/bin/env python3
"""Apply El Salvador geocode policy: verified address overrides or country badge (no city guess pins)."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEO_BY_ID = Path(__file__).resolve().parent / "geocode-by-id.json"
SV_OVERRIDES = Path(__file__).resolve().parent / "geocode-sv-overrides.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geocode_actors import finalize_geo, resolve_query  # noqa: E402


def country_only(country: str = "El Salvador") -> dict:
    return {
        "lat": None,
        "lng": None,
        "address": None,
        "city": None,
        "country": country,
        "precision": "country",
        "source_url": None,
    }


def main() -> None:
    blob = json.loads(GEO_BY_ID.read_text(encoding="utf-8"))
    overrides = json.loads(SV_OVERRIDES.read_text(encoding="utf-8"))
    sv_ids = sorted(k for k in blob if k.startswith("sv-"))
    n_addr = n_country = 0

    refresh = os.environ.get("SV_GEOCODE_REFRESH", "").lower() in ("1", "true", "yes")

    for aid in sv_ids:
        if aid in overrides:
            existing = blob.get(aid) or {}
            if (
                not refresh
                and existing.get("precision") == "address"
                and existing.get("lat") is not None
                and existing.get("address")
            ):
                n_addr += 1
                continue
            ov = overrides[aid]
            q = ov.get("geocode_query") or ov.get("address")
            raw = resolve_query(q, "El Salvador") if q else None
            if raw:
                geo = finalize_geo(
                    {
                        **raw,
                        "source_url": ov.get("source_url") or raw.get("source_url"),
                        "office_note": ov.get("office_note"),
                    },
                    {"id": aid, "country": "El Salvador"},
                )
                if geo and geo.get("precision") == "address":
                    blob[aid] = geo
                    n_addr += 1
                    time.sleep(1.05)
                    continue
            blob[aid] = country_only()
            n_country += 1
            continue

        existing = blob.get(aid) or {}
        src = (existing.get("source_url") or "").lower()
        if existing.get("precision") == "city" or "actor-city" in src:
            blob[aid] = country_only()
            n_country += 1
        elif existing.get("precision") == "address" and existing.get("lat") is not None:
            if not existing.get("address"):
                blob[aid] = country_only()
                n_country += 1
            else:
                n_addr += 1
        else:
            blob[aid] = country_only()
            n_country += 1

    GEO_BY_ID.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SV geocode: {n_addr} address pins, {n_country} country-badge ({len(sv_ids)} total)")


if __name__ == "__main__":
    main()
