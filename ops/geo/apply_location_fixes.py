#!/usr/bin/env python3
"""Apply ops/geo/fixes/*.csv rows to Nexus JSON bundles (assembler)."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

_GEO_DIR = Path(__file__).resolve().parent
import sys

sys.path.insert(0, str(_GEO_DIR))
from json_bundle_io import write_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIXES_DIR = Path(__file__).resolve().parent / "fixes"

COUNTRY_TO_CODE = {
    "Peru": "PE",
    "Colombia": "CO",
    "El Salvador": "SV",
    "Guatemala": "GT",
    "Costa Rica": "CR",
    "Honduras": "HN",
    "Mexico": "MX",
    "Nicaragua": "NI",
    "Panama": "PA",
    "Chile": "CL",
    "Argentina": "AR",
    "Brazil": "BR",
    "United States": "US",
    "Netherlands": "NL",
    "United Kingdom": "GB",
    "Germany": "DE",
    "France": "FR",
    "Spain": "ES",
    "Switzerland": "CH",
    "South Korea": "KR",
    "Singapore": "SG",
    "India": "IN",
    "Canada": "CA",
    "Australia": "AU",
    "Belgium": "BE",
    "Sweden": "SE",
    "Denmark": "DK",
    "Norway": "NO",
    "Finland": "FI",
    "Ireland": "IE",
    "Israel": "IL",
    "Japan": "JP",
    "China": "CN",
    "Portugal": "PT",
    "Italy": "IT",
    "Austria": "AT",
    "Luxembourg": "LU",
    "Ecuador": "EC",
    "Bolivia": "BO",
    "Paraguay": "PY",
    "Uruguay": "UY",
    "Venezuela": "VE",
}


def norm_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def norm_slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_float(v: str | None):
    if v is None or str(v).strip() == "":
        return None
    return float(v)


def normalize_precision(row: dict) -> str:
    prec = (row.get("precision") or "unknown").strip().lower()
    if prec not in ("address", "city", "country", "unknown"):
        return "unknown"
    lat = parse_float(row.get("lat"))
    lng = parse_float(row.get("lng"))
    street = (row.get("street_address") or "").strip()
    if prec == "address":
        if lat is None or lng is None:
            return "city" if street or (row.get("city") or "").strip() else "country"
        return "address"
    return prec


def geo_from_row(row: dict) -> dict | None:
    prec = normalize_precision(row)
    city = (row.get("city") or "").strip() or None
    country = (row.get("country") or "").strip() or None
    street = (row.get("street_address") or "").strip() or None
    source_url = (row.get("source_url") or "").strip() or None
    notes = (row.get("notes") or "").strip()
    hq_abroad = "hq_abroad" in notes.lower() or "| hq_abroad" in notes.lower()

    lat = lng = None
    if prec == "address":
        lat = parse_float(row.get("lat"))
        lng = parse_float(row.get("lng"))
        if lat is None or lng is None:
            prec = "city"

    geo: dict = {"precision": prec}
    if street:
        geo["address"] = street
    if city:
        geo["city"] = city
    if country:
        geo["country"] = country
    if source_url:
        geo["source_url"] = source_url
    if lat is not None and lng is not None and prec == "address":
        geo["lat"] = lat
        geo["lng"] = lng
    if hq_abroad:
        geo["hq_abroad"] = True
    if notes:
        geo["location_note"] = notes.split("|")[0].strip()
    return geo


def loc_from_row(row: dict) -> dict:
    geo = geo_from_row(row) or {"precision": "unknown"}
    return {
        "precision": geo.get("precision", "unknown"),
        "city": geo.get("city"),
        "country": geo.get("country"),
        "address": geo.get("address"),
        "lat": geo.get("lat"),
        "lng": geo.get("lng"),
        "source_url": geo.get("source_url"),
        "hq_abroad": geo.get("hq_abroad"),
        "location_note": geo.get("location_note"),
    }


def load_all_fix_rows() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(FIXES_DIR.glob("*.csv")):
        with path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                r["_source_file"] = path.name
                rows.append(r)
    return rows


def apply_ecosystem_actor(actors: list[dict], row: dict) -> bool:
    aid = row["id"]
    for a in actors:
        if a.get("id") != aid:
            continue
        geo = geo_from_row(row)
        if geo:
            a["geo"] = geo
        if row.get("city"):
            a["city"] = row["city"].strip()
        if row.get("country"):
            a["country"] = row["country"].strip()
        return True
    return False


def apply_hub(hubs: list[dict], row: dict) -> bool:
    hid = row["id"]
    for h in hubs:
        if h.get("id") != hid:
            continue
        geo = geo_from_row(row)
        if geo:
            h["geo"] = geo
        cc = COUNTRY_TO_CODE.get((row.get("country") or "").strip())
        if cc:
            h["country"] = cc
        return True
    return False


def portfolio_index(core_startups: list[dict]) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for s in core_startups:
        keys = {norm_slug(s.get("n", "")), norm_key(s.get("n", ""))}
        if s.get("w"):
            keys.add(norm_key(s["w"].split(".")[0]))
        for k in keys:
            if k:
                idx[k] = s
    return idx


def match_portfolio(idx: dict[str, dict], row_id: str, name: str) -> dict | None:
    for key in (norm_slug(row_id), norm_key(row_id), norm_slug(name), norm_key(name)):
        if key in idx:
            return idx[key]
    rid = row_id.lstrip("+")
    for key in (norm_slug(rid), norm_key(rid)):
        if key in idx:
            return idx[key]
    return None


def apply_portfolio(core: dict, row: dict, idx: dict[str, dict]) -> bool:
    s = match_portfolio(idx, row["id"], row.get("name") or "")
    if not s:
        return False
    s["loc"] = loc_from_row(row)
    cc = COUNTRY_TO_CODE.get((row.get("country") or "").strip())
    if cc:
        s["c"] = cc
    return True


def apply_onepager(path: Path, row: dict) -> bool:
    if not path.exists():
        return False
    data = load_json(path)
    loc = loc_from_row(row)
    data["location"] = loc
    city = loc.get("city")
    country = loc.get("country")
    cc = COUNTRY_TO_CODE.get(country or "")
    if city or country:
        en = " · ".join(x for x in [f"City: {city}" if city else None, f"Country: {country}" if country else None] if x)
        es_city = city
        es = " · ".join(
            x
            for x in [
                f"Ciudad: {es_city}" if es_city else None,
                f"País: {country}" if country else None,
            ]
            if x
        )
        if data.get("portfolio"):
            data["portfolio"]["location_en"] = en
            data["portfolio"]["location_es"] = es
            if cc:
                data["portfolio"]["country_code"] = cc
                data["portfolio"]["country_name_en"] = country
                data["portfolio"]["country_name_es"] = country
        for rib in data.get("ribbon") or []:
            if rib.get("lab_en") == "Country" or rib.get("lab_es") == "País":
                if country:
                    rib["sub_en"] = country
                    rib["sub_es"] = country
                if cc:
                    rib["val"] = cc
    write_json(path, data)
    return True


def apply_idea(path: Path, row: dict) -> bool:
    if not path.exists():
        return False
    items = load_json(path)
    if not isinstance(items, list):
        return False
    for it in items:
        if it.get("slug") != row["id"]:
            continue
        loc = loc_from_row(row)
        it["location"] = loc
        if loc.get("city"):
            it["city"] = loc["city"]
        cc = COUNTRY_TO_CODE.get(loc.get("country") or "")
        if cc:
            it["country"] = cc
        return True
    return False


def apply_investor(investors: list[dict], row: dict) -> bool:
    rid = int(row["id"])
    for inv in investors:
        if inv.get("id") != rid:
            continue
        prec = normalize_precision(row)
        inv["location_precision"] = prec
        city = (row.get("city") or "").strip() or None
        country = (row.get("country") or "").strip() or None
        if country:
            inv["country"] = country
        inv["hq_city"] = city
        src = (row.get("source_url") or "").strip() or None
        if src:
            inv["hq_source_url"] = src
        ev = (row.get("evidence") or row.get("notes") or "").strip()
        if ev:
            inv["hq_evidence"] = ev
        return True
    return False


def apply_mentor(mentors: list[dict], row: dict) -> bool:
    mid = row["id"]
    target = None
    if mid.startswith("mentor-") and mid[7:].isdigit():
        i = int(mid[7:]) - 1
        if 0 <= i < len(mentors):
            target = mentors[i]
    else:
        for m in mentors:
            if m.get("nexus_id") == mid or m.get("name") == row.get("name"):
                target = m
                break
    if not target:
        return False
    prec = normalize_precision(row)
    target["location_precision"] = prec
    city = (row.get("city") or "").strip() or None
    country = (row.get("country") or "").strip() or None
    if city:
        target["city"] = city
    if country:
        target["country"] = country
    src = (row.get("source_url") or "").strip()
    if src:
        target["location_source_url"] = src
    note = (row.get("notes") or "").strip()
    if note:
        target["location_note"] = note
    return True


def apply_juror(jurors: list[dict], row: dict) -> bool:
    jid = row["id"]
    if not jid.startswith("juror-") or not jid[6:].isdigit():
        return False
    i = int(jid[6:]) - 1
    if i < 0 or i >= len(jurors):
        return False
    j = jurors[i]
    prec = normalize_precision(row)
    j["location_precision"] = prec
    city = (row.get("city") or "").strip() or None
    country = (row.get("country") or "").strip() or None
    if city:
        j["city"] = city
    if country:
        j["country"] = country
    src = (row.get("source_url") or "").strip()
    if src:
        j["location_source_url"] = src
    note = (row.get("notes") or "").strip()
    if note:
        j["location_note"] = note
    return True


def main() -> None:
    rows = load_all_fix_rows()
    stats: dict[str, list[str]] = defaultdict(list)

    actors_path = ROOT / "static/ecosystem/data/actors.json"
    actors = load_json(actors_path)
    hubs_path = ROOT / "site/cth-static/hubs/hubs-data.json"
    hubs_doc = load_json(hubs_path)
    hubs = hubs_doc["hubs"]
    portfolio_path = ROOT / "site/nexus-assets/previews/startups-redesign-20261016/portfolio-core.json"
    portfolio_doc = load_json(portfolio_path)
    portfolio_idx = portfolio_index(portfolio_doc["startups"])
    investors_path = ROOT / "site/investors/data/investors.json"
    investors_doc = load_json(investors_path)
    mentors_path = ROOT / "data/clp26/mentor_cards.json"
    mentors_doc = load_json(mentors_path)
    jury_path = ROOT / "data/clp26/jury_cards.json"
    jury_doc = load_json(jury_path)

    for row in rows:
        et = row.get("entity_type")
        ok = False
        if et == "ecosystem_actor":
            ok = apply_ecosystem_actor(actors, row)
        elif et == "hub_hubmap":
            ok = apply_hub(hubs, row)
        elif et == "portfolio_startup":
            ok = apply_portfolio(portfolio_doc, row, portfolio_idx)
        elif et == "startup_onepager_s":
            ok = apply_onepager(ROOT / "onepagers/data" / f"{row['id']}.json", row)
        elif et == "idea_curated_imd_pe":
            ok = apply_idea(ROOT / "app/nexus-ideas/src/data/imd-peru-curated.json", row)
        elif et == "idea_curated_epic":
            ok = apply_idea(ROOT / "app/nexus-ideas/src/data/epic-angels-curated.json", row)
        elif et == "investor_crm":
            ok = apply_investor(investors_doc["investors"], row)
        elif et == "mentor_clp26":
            ok = apply_mentor(mentors_doc["mentors"], row)
        elif et == "jury_clp26":
            ok = apply_juror(jury_doc["jurors"], row)
        if not ok:
            stats["missing"].append(f"{et}:{row.get('id')}")

    write_json(actors_path, actors)
    write_json(hubs_path, hubs_doc)
    write_json(portfolio_path, portfolio_doc)
    write_json(investors_path, investors_doc)
    write_json(mentors_path, mentors_doc)
    write_json(jury_path, jury_doc)

    print(f"Applied {len(rows)} fix rows; missing {len(stats['missing'])}")
    if stats["missing"]:
        for m in stats["missing"][:20]:
            print("  ", m)


if __name__ == "__main__":
    main()
