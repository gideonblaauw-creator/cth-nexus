#!/usr/bin/env python3
"""Second pass: re-geocode actors stuck at country / not_found."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import geocode_actors as g

DATA = Path(__file__).resolve().parents[2] / "static" / "ecosystem" / "data" / "actors.json"
REVIEW = Path(__file__).resolve().parent / "geocode-review.csv"


def clean_name(name: str) -> str:
    name = re.split(r"\s[–(-]\s", name)[0]
    name = re.sub(r"\s*\([^)]*\)", "", name)
    return name.strip()


def extra_queries(actor: dict) -> list[str]:
    country = actor.get("country") or "Peru"
    capital = g.CAPITAL.get(country, "")
    base = clean_name(actor.get("name") or "")
    site = actor.get("website") or ""
    out = [
        f"{base} {capital} {country}",
        f"{base} {country}",
        base,
    ]
    if "gob.pe/" in site:
        slug = site.rstrip("/").split("/")[-1]
        out.insert(0, f"{slug.replace('-', ' ')} {capital} {country}")
    return out


def main() -> None:
    actors = json.loads(DATA.read_text(encoding="utf-8"))
    updated = 0
    for actor in actors:
        geo = actor.get("geo") or {}
        if geo.get("lat") is not None and geo.get("precision") != "country":
            continue
        raw = None
        scraped = g.scrape_website(actor.get("website"))
        if scraped:
            raw = scraped
        if not raw or raw.get("lat") is None:
            for q in extra_queries(actor):
                hit = g.resolve_query(q, actor.get("country"))
                if hit:
                    raw = {**hit, "source_url": hit["source_url"] + " (retry)"}
                    break
        new_geo = g.finalize_geo(raw, actor) if raw else None
        if new_geo and new_geo.get("lat") is not None:
            actor["geo"] = new_geo
            if new_geo.get("city") and not actor.get("city"):
                actor["city"] = new_geo["city"]
            updated += 1

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
                "precision": geo.get("precision") or "not_found",
                "source_url": geo.get("source_url") or "",
                "flags": ";".join(geo.get("flags") or []),
            }
        )
    with REVIEW.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["name", "website", "address", "lat", "lng", "precision", "source_url", "flags"],
        )
        w.writeheader()
        w.writerows(rows)
    print(f"retry updated {updated}")


if __name__ == "__main__":
    main()
