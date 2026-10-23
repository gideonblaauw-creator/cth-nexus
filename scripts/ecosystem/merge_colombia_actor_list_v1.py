#!/usr/bin/env python3
"""Merge Colombia actor list v1 (docs/colombia/actor-list-v1.csv) into actors.raw.json."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "static" / "ecosystem" / "data" / "actors.raw.json"
CSV_PATH = ROOT / "docs" / "colombia" / "actor-list-v1.csv"
CANDIDATES = ROOT / "ops" / "ecosystem" / "colombia-v1-address-candidates.json"
GEO_BY_ID = ROOT / "ops" / "ecosystem" / "geocode-by-id.json"
SOURCE = "Colombia actor list v1 (PR #122)"
UA = "CleantechHUB-Nexus-Ecosystem/1.0 (merge colombia v1)"

BAD_ADDRESS = re.compile(
    r"(?i)\b(consejos|comenzar|no es una ley|producto de|horario de atenc|tel\b|línea de servicio)"
)


def plausible_address(line: str) -> bool:
    s = (line or "").strip()
    if len(s) < 12 or len(s) > 95:
        return False
    if not re.search(r"\d", s):
        return False
    if BAD_ADDRESS.search(s):
        return False
    if not re.match(
        r"(?i)(Calle|Carrera|Cra\.?|Cl\.?|Av\.?|Avenida|Diagonal|Transversal|Km\.?)",
        s,
    ):
        return False
    return True


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return "co-" + re.sub(r"-+", "-", s)


def nominatim(street: str, city: str) -> tuple[float, float] | None:
    q = f"{street}, {city}, Colombia"
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1, "countrycodes": "co"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        rows = json.loads(resp.read())
    if not rows:
        return None
    return round(float(rows[0]["lat"]), 6), round(float(rows[0]["lon"]), 6)


def country_geo() -> dict:
    return {
        "lat": None,
        "lng": None,
        "address": None,
        "city": None,
        "country": "Colombia",
        "precision": "country",
        "source_url": None,
    }


def resolve_geo(aid: str, city: str, candidates: dict) -> dict:
    hits = (candidates.get(aid) or {}).get("hits") or []
    addr = None
    src = None
    for hit in hits:
        for cand in hit.get("addresses") or []:
            if plausible_address(cand):
                addr = cand.strip()
                src = hit.get("url")
                break
        if addr:
            break
    if not addr:
        return country_geo()
    seed = {
        "precision": "address",
        "address": addr,
        "city": city or "Bogotá",
        "country": "Colombia",
        "source_url": src,
    }
    coords = nominatim(seed["address"], seed.get("city") or city or "Bogotá")
    if coords:
        seed["lat"], seed["lng"] = coords
        return seed
    return country_geo()


def actor_from_row(row: dict, candidates: dict) -> dict:
    aid = (row.get("ecosystem_id") or "").strip() or slugify(row["name"])
    category = row["category"].strip()
    role = (row.get("ecosystem_role") or "").strip()
    desc = role if role else f"Actor del ecosistema climático y de innovación en Colombia."
    is_policy = category == "policy"
    geo = resolve_geo(aid, (row.get("city") or "").strip(), candidates)
    out = {
        "id": aid,
        "name": row["name"].strip(),
        "type": "policy" if is_policy else "org",
        "category": category,
        "country": "Colombia",
        "city": (row.get("city") or "").strip() or None,
        "website": (row.get("website") or "").strip() or None,
        "page": None,
        "notes": f"Colombia actor list v1 — {category}",
        "geo": country_geo(),
        "nexus": {"card_slug": None},
        "card": {
            "ecosystem_role": role[:500] if role else None,
            "description": desc,
        },
    }
    if not out["card"]["ecosystem_role"]:
        del out["card"]["ecosystem_role"]
    return out, geo


def main() -> None:
    if not CSV_PATH.is_file():
        raise SystemExit(f"Missing {CSV_PATH}")
    rows = list(csv.DictReader(CSV_PATH.read_text(encoding="utf-8").splitlines()))
    candidates = {}
    if CANDIDATES.is_file():
        candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))

    actors = json.loads(RAW.read_text(encoding="utf-8"))
    by_id = {a["id"]: a for a in actors}
    existing_names = {a["name"].lower().strip() for a in actors}
    geo_blob = json.loads(GEO_BY_ID.read_text(encoding="utf-8"))

    skipped: list[str] = []
    added: list[str] = []
    seen_csv: set[str] = set()

    new_rows: list[dict] = []
    for row in rows:
        aid = (row.get("ecosystem_id") or "").strip() or slugify(row["name"])
        name = row["name"].strip()
        if aid in seen_csv:
            skipped.append(f"{name} ({aid}) duplicate CSV row")
            continue
        seen_csv.add(aid)
        if aid in by_id:
            skipped.append(f"{name} ({aid}) existing id")
            continue
        if name.lower() in existing_names:
            skipped.append(f"{name} ({aid}) existing name")
            continue
        actor, geo = actor_from_row(row, candidates)
        actor["geo"] = geo
        geo_blob[aid] = geo
        new_rows.append(actor)
        by_id[aid] = actor
        added.append(aid)

    # Append new Colombia actors after last co-* entry (stable block)
    co_indices = [i for i, a in enumerate(actors) if str(a.get("id", "")).startswith("co-")]
    insert_at = co_indices[-1] + 1 if co_indices else len(actors)
    out = actors[:insert_at] + new_rows + actors[insert_at:]

    RAW.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    GEO_BY_ID.write_text(json.dumps(geo_blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "added": len(added),
        "skipped": len(skipped),
        "skipped_detail": skipped,
        "added_ids": added,
    }
    report_path = ROOT / "ops" / "ecosystem" / "colombia-v1-merge-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"added": len(added), "skipped": len(skipped)}, indent=2))


if __name__ == "__main__":
    main()
