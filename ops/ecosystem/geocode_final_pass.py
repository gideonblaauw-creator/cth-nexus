#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path

import geocode_actors as g

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "static" / "ecosystem" / "data" / "actors.json"
REVIEW = Path(__file__).resolve().parent / "geocode-review.csv"


def clean(name: str) -> str:
    name = re.split(r"\s[–(-]\s", name)[0]
    return re.sub(r"\s*\([^)]*\)", "", name).strip()


def variants(actor: dict) -> list[str]:
    country = actor["country"]
    cap = g.CAPITAL[country]
    n = clean(actor["name"])
    site = actor.get("website") or ""
    vs = [
        f"{n}, {cap}, {country}",
        f"{n} {cap}",
        n,
        f"{n} headquarters",
    ]
    if "gob.pe/" in site:
        slug = site.rstrip("/").split("/")[-1].replace("-", " ")
        vs.insert(0, f"{slug} {cap} {country}")
    if "edu.pe" in site or site.endswith(".edu.pe"):
        vs.insert(0, site.replace("https://", "").replace("www.", "").split("/")[0])
    return vs


def main() -> None:
    actors = json.loads(DATA.read_text(encoding="utf-8"))
    updated = 0
    for actor in actors:
        geo = actor.get("geo") or {}
        if geo.get("lat") is not None:
            continue
        raw = g.scrape_website(actor.get("website"))
        if raw and raw.get("lat") is None and not raw.get("geocode_query"):
            raw = None
        if not raw or raw.get("lat") is None:
            for q in variants(actor):
                hit = g.nominatim(q, actor.get("country"))
                if hit:
                    raw = {**hit, "source_url": hit["source_url"] + " (final-pass)"}
                    break
        if (not raw or raw.get("lat") is None) and actor.get("category") == "international":
            hit = g.nominatim(clean(actor["name"]), None)
            if hit:
                raw = {
                    **hit,
                    "office_note": "HQ (no in-country office found)",
                    "source_url": hit["source_url"] + " (final-pass-HQ)",
                }
        new_geo = g.finalize_geo(raw, actor) if raw else None
        if new_geo and new_geo.get("lat") is not None:
            actor["geo"] = new_geo
            updated += 1
        time.sleep(0.05)

    DATA.write_text(json.dumps(actors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = []
    for actor in actors:
        geo = actor.get("geo") or {}
        rows.append(
            {
                "name": actor.get("name"),
                "website": actor.get("website"),
                "address": geo.get("address") or "",
                "lat": geo.get("lat"),
                "lng": geo.get("lng"),
                "precision": geo.get("precision") if geo.get("lat") is not None else "not_found",
                "source_url": geo.get("source_url") or "",
                "flags": ";".join(geo.get("flags") or ([] if geo.get("lat") else ["not_found"])),
            }
        )
    with REVIEW.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["name", "website", "address", "lat", "lng", "precision", "source_url", "flags"],
        )
        w.writeheader()
        w.writerows(rows)
    print("final updated", updated, "remaining", sum(1 for a in actors if (a.get("geo") or {}).get("lat") is None))


if __name__ == "__main__":
    main()
