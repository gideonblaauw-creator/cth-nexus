#!/usr/bin/env python3
"""Read-only location inventory for Nexus entity bundles (no API writes)."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_MD = Path(__file__).resolve().parent / "LOCATION-AUDIT.md"
OUT_CSV = Path(__file__).resolve().parent / "location-gaps.csv"

CAPITAL = {
    "Peru": (-12.0464, -77.0428),
    "Colombia": (4.711, -74.0721),
    "El Salvador": (13.6929, -89.2182),
    "Guatemala": (14.6349, -90.5069),
    "Costa Rica": (9.9281, -84.0907),
}
HUB_COUNTRY = {
    "externado": "CO",
    "landivar": "GT",
    "emprende-up": "PE",
    "el-salvador": "SV",
    "lci-veritas": "CR",
}
COUNTRY_FROM_CODE = {
    "CO": "Colombia",
    "PE": "Peru",
    "SV": "El Salvador",
    "GT": "Guatemala",
    "CR": "Costa Rica",
    "HN": "Honduras",
    "MX": "Mexico",
    "NI": "Nicaragua",
    "PA": "Panama",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def scrub(text: str | None) -> str:
    if not text:
        return ""
    t = EMAIL_RE.sub("[redacted]", str(text))
    t = PHONE_RE.sub("[redacted]", t)
    return t


def round_pair(lat: float, lng: float, places: int = 4) -> tuple[float, float]:
    return (round(lat, places), round(lng, places))


def pin_flags(geo: dict | None, entity_id: str = "") -> list[str]:
    if not geo:
        return ["no-geo-object"]
    flags: list[str] = []
    src = (geo.get("source_url") or "").lower()
    prec = geo.get("precision") or ""
    if "actor-city" in src:
        flags.append("actor-city-guess")
    if "hq-fallback" in src:
        flags.append("hq-fallback")
    if "wikidata" in src:
        flags.append("wikidata")
    if "photon.komoot.io" in src or "nominatim" in src:
        flags.append("geocoder-api")
    if prec == "city" and geo.get("lat") is not None:
        flags.append("city-pin")
    if not src and geo.get("lat") is not None:
        flags.append("missing-source-url")
    if prec == "legacy":
        flags.append("legacy-precision")
    return flags


def tier_from_geo(geo: dict | None, country: str | None) -> str:
    if not geo:
        return "none" if not country else "country-only"
    prec = geo.get("precision") or ("legacy" if geo.get("lat") is not None else "missing")
    has_coords = geo.get("lat") is not None and geo.get("lng") is not None
    if prec == "address" and has_coords:
        return "verified-address+coords"
    if prec == "city" and has_coords:
        return "city-only"
    if prec == "country" or (not has_coords and (geo.get("country") or country)):
        return "country-only"
    if not has_coords and not country:
        return "none"
    if has_coords:
        return "city-only" if prec != "address" else "verified-address+coords"
    return "country-only"


def policy_status(tier: str, flags: list[str], geo: dict | None) -> str:
    """Strict policy: map pin only with verified street address from website or official directory."""
    if tier == "verified-address+coords":
        bad = {"actor-city-guess", "hq-fallback", "city-pin", "wikidata", "geocoder-api", "missing-source-url"}
        if bad.intersection(flags):
            return "suspect-pin"
        src = (geo or {}).get("source_url") or ""
        if src.startswith("http") and "photon" not in src and "nominatim" not in src:
            return "policy-ok"
        if (geo or {}).get("address"):
            return "policy-ok"
        return "suspect-pin"
    if tier == "city-only":
        return "suspect-pin"
    return "no-pin"


def is_verified_address_strict(geo: dict | None, flags: list[str]) -> bool:
    return policy_status(tier_from_geo(geo, (geo or {}).get("country")), flags, geo) == "policy-ok"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def portfolio_startups() -> list[dict]:
    path = ROOT / "site/nexus-assets/previews/startups-redesign-20261016/portfolio-core.json"
    if path.exists():
        return load_json(path)["startups"]
    return []


def onepager_country(data: dict) -> str | None:
    for rib in data.get("ribbon") or []:
        if rib.get("lab_en") == "Country" or rib.get("lab_es") == "País":
            return rib.get("sub_en") or rib.get("sub_es") or rib.get("val")
    return None


def summarize(rows: list[dict]) -> dict:
    total = len(rows)
    tier = Counter(r["location_tier"] for r in rows)
    suspect = sum(1 for r in rows if r["pin_policy_status"] == "suspect-pin")
    no_pin = sum(1 for r in rows if r["pin_policy_status"] == "no-pin")
    policy_ok = sum(1 for r in rows if r["pin_policy_status"] == "policy-ok")
    return {
        "total": total,
        "strict_verified_address_coords": policy_ok,
        "address_precision_with_coords": tier.get("verified-address+coords", 0),
        "city_only": tier.get("city-only", 0),
        "country_only": tier.get("country-only", 0),
        "none": tier.get("none", 0),
        "policy_ok_pins": policy_ok,
        "suspect_or_guessed_pins": suspect,
        "no_pin_expected": no_pin,
    }


def suspect_examples(rows: list[dict], n: int = 3) -> list[dict]:
    bad = [r for r in rows if r["pin_policy_status"] == "suspect-pin"]
    bad.sort(key=lambda r: (r["entity_type"], r["entity_id"]))
    return bad[:n]


def audit_ecosystem_actors() -> list[dict]:
    actors = load_json(ROOT / "static/ecosystem/data/actors.json")
    rows = []
    for a in actors:
        geo = a.get("geo") or {}
        flags = pin_flags(geo, a["id"])
        tier = tier_from_geo(geo, a.get("country"))
        rows.append(
            {
                "entity_type": "ecosystem_actor",
                "entity_id": a["id"],
                "name": a.get("name"),
                "country": a.get("country"),
                "location_tier": tier,
                "pin_policy_status": policy_status(tier, flags, geo),
                "precision": geo.get("precision"),
                "lat": geo.get("lat"),
                "lng": geo.get("lng"),
                "source_url": scrub(geo.get("source_url")),
                "flags": ";".join(flags),
                "notes": scrub(geo.get("address") or ""),
            }
        )
    return rows


def audit_actor_subset(rows: list[dict], categories: set[str], entity_type: str) -> list[dict]:
    actors = load_json(ROOT / "static/ecosystem/data/actors.json")
    ids = {a["id"] for a in actors if a.get("category") in categories}
    return [{**r, "entity_type": entity_type} for r in rows if r["entity_id"] in ids]


def audit_hubs() -> list[dict]:
    hubs = load_json(ROOT / "site/cth-static/hubs/hubs-data.json")["hubs"]
    rows = []
    for h in hubs:
        geo = h.get("geo") or {}
        cc = h.get("country") or HUB_COUNTRY.get(h["id"], "")
        country = COUNTRY_FROM_CODE.get(cc, cc)
        flags = pin_flags(geo, h["id"])
        tier = tier_from_geo(geo, country)
        rows.append(
            {
                "entity_type": "hub_hubmap",
                "entity_id": h["id"],
                "name": (h.get("name") or {}).get("EN") or h["id"],
                "country": country,
                "location_tier": tier,
                "pin_policy_status": policy_status(tier, flags, geo),
                "precision": geo.get("precision"),
                "lat": geo.get("lat"),
                "lng": geo.get("lng"),
                "source_url": scrub(geo.get("source_url")),
                "flags": ";".join(flags) if flags else "",
                "notes": scrub(geo.get("address") or h.get("short", {}).get("EN", "")),
            }
        )
    return rows


def audit_portfolio() -> list[dict]:
    rows = []
    for s in portfolio_startups():
        cc = s.get("c")
        loc = s.get("loc") or {}
        country = loc.get("country") or COUNTRY_FROM_CODE.get(cc, cc)
        geo = {
            "precision": loc.get("precision"),
            "lat": loc.get("lat"),
            "lng": loc.get("lng"),
            "source_url": loc.get("source_url"),
            "address": loc.get("address"),
            "country": country,
        }
        flags = pin_flags(geo if loc else None)
        tier = tier_from_geo(geo if loc else None, country)
        rows.append(
            {
                "entity_type": "portfolio_startup",
                "entity_id": s.get("slug") or s.get("n", "").lower().replace(" ", "-"),
                "name": s.get("n"),
                "country": country,
                "location_tier": tier,
                "pin_policy_status": policy_status(tier, flags, geo if loc else None),
                "precision": loc.get("precision"),
                "lat": loc.get("lat"),
                "lng": loc.get("lng"),
                "source_url": scrub(loc.get("source_url")),
                "flags": ";".join(flags) if flags else ("country-code-only" if not loc else ""),
                "notes": f"program={s.get('p')}",
            }
        )
    return rows


def audit_onepagers() -> list[dict]:
    rows = []
    data_dir = ROOT / "onepagers/data"
    for path in sorted(data_dir.glob("*.json")):
        data = load_json(path)
        country = onepager_country(data)
        loc = data.get("location") or {}
        if loc.get("country"):
            country = loc.get("country")
        geo = {
            "precision": loc.get("precision"),
            "lat": loc.get("lat"),
            "lng": loc.get("lng"),
            "source_url": loc.get("source_url") or data.get("website"),
            "address": loc.get("address"),
            "country": country,
        }
        flags = pin_flags(geo if loc else None)
        tier = tier_from_geo(geo if loc else None, country)
        rows.append(
            {
                "entity_type": "startup_onepager_s",
                "entity_id": data.get("slug") or path.stem,
                "name": data.get("name"),
                "country": country,
                "location_tier": tier,
                "pin_policy_status": policy_status(tier, flags, geo if loc else None),
                "precision": loc.get("precision"),
                "lat": loc.get("lat"),
                "lng": loc.get("lng"),
                "source_url": scrub(loc.get("source_url") or data.get("website")),
                "flags": ";".join(flags) if flags else ("no-geo-field" if not loc else ""),
                "notes": "",
            }
        )
    return rows


def audit_mentors() -> list[dict]:
    mentors = load_json(ROOT / "data/clp26/mentor_cards.json")["mentors"]
    rows = []
    for i, m in enumerate(mentors):
        prec = m.get("location_precision")
        country = m.get("country")
        city = m.get("city")
        tier = "none"
        if prec == "city" and city:
            tier = "city-only"
        elif prec == "country" and country:
            tier = "country-only"
        elif country:
            tier = "country-only"
        rows.append(
            {
                "entity_type": "mentor_clp26",
                "entity_id": m.get("nexus_id") or f"mentor-{i+1}",
                "name": m.get("name"),
                "country": country,
                "location_tier": tier,
                "pin_policy_status": "no-pin",
                "precision": prec,
                "lat": None,
                "lng": None,
                "source_url": scrub(m.get("location_source_url") or m.get("linkedin_url")),
                "flags": "no-map-pin",
                "notes": scrub(m.get("location_note") or ""),
            }
        )
    return rows


def audit_investors_crm() -> list[dict]:
    inv = load_json(ROOT / "site/investors/data/investors.json")["investors"]
    rows = []
    for i in inv:
        country = i.get("country")
        prec = i.get("location_precision")
        city = i.get("hq_city")
        tier = "none"
        if prec == "city" and city:
            tier = "city-only"
        elif prec == "country" and country:
            tier = "country-only"
        elif country:
            tier = "country-only"
        rows.append(
            {
                "entity_type": "investor_crm",
                "entity_id": str(i.get("id")),
                "name": i.get("name"),
                "country": country,
                "location_tier": tier,
                "pin_policy_status": "no-pin",
                "precision": prec,
                "lat": None,
                "lng": None,
                "source_url": scrub(i.get("hq_source_url") or i.get("website")),
                "flags": "no-map-pin",
                "notes": scrub(i.get("hq_evidence") or ""),
            }
        )
    return rows


def audit_ideas_curated() -> list[dict]:
    """Offline proxy: BookStack ideas API not available in this environment."""
    rows = []
    for rel, etype in (
        ("app/nexus-ideas/src/data/imd-peru-curated.json", "idea_curated_imd_pe"),
        ("app/nexus-ideas/src/data/epic-angels-curated.json", "idea_curated_epic"),
    ):
        path = ROOT / rel
        if not path.exists():
            continue
        items = load_json(path)
        if isinstance(items, dict):
            items = items.get("ideas") or items.get("startups") or []
        for it in items:
            cc = it.get("country")
            country = COUNTRY_FROM_CODE.get(cc, cc) if cc and len(cc) == 2 else cc
            loc = it.get("location") or {}
            if loc.get("country"):
                country = loc.get("country")
            prec = loc.get("precision")
            tier = "none"
            if prec == "city" and loc.get("city"):
                tier = "city-only"
            elif prec == "country" and country:
                tier = "country-only"
            elif country:
                tier = "country-only"
            rows.append(
                {
                    "entity_type": etype,
                    "entity_id": it.get("slug") or it.get("startup_name", ""),
                    "name": it.get("name") or it.get("startup_name"),
                    "country": country,
                    "location_tier": tier,
                    "pin_policy_status": "no-pin",
                    "precision": prec,
                    "lat": loc.get("lat"),
                    "lng": loc.get("lng"),
                    "source_url": scrub(loc.get("source_url") or it.get("website")),
                    "flags": "bookstack-live-no-snapshot" if not loc else "no-map-pin",
                    "notes": scrub(loc.get("location_note") or "city in page markdown only"),
                }
            )
    return rows


def audit_policies() -> list[dict]:
    policies = load_json(ROOT / "static/ecosystem/data/policies.json")
    rows = []
    for i, p in enumerate(policies):
        rows.append(
            {
                "entity_type": "policy_ecosystem",
                "entity_id": f"policy-{i+1}",
                "name": p.get("name"),
                "country": p.get("country"),
                "location_tier": "country-only" if p.get("country") else "none",
                "pin_policy_status": "no-pin",
                "precision": None,
                "lat": None,
                "lng": None,
                "source_url": scrub(p.get("source_url")),
                "flags": "no-geo-field",
                "notes": p.get("registry") or "",
            }
        )
    return rows


def audit_jury() -> list[dict]:
    jurors = load_json(ROOT / "data/clp26/jury_cards.json")["jurors"]
    rows = []
    for i, j in enumerate(jurors):
        prec = j.get("location_precision")
        country = j.get("country")
        city = j.get("city")
        tier = "none"
        if prec == "city" and city:
            tier = "city-only"
        elif country:
            tier = "country-only"
        rows.append(
            {
                "entity_type": "jury_clp26",
                "entity_id": f"juror-{i+1}",
                "name": j.get("name"),
                "country": country,
                "location_tier": tier,
                "pin_policy_status": "no-pin",
                "precision": prec,
                "lat": None,
                "lng": None,
                "source_url": scrub(j.get("location_source_url") or j.get("linkedin_url")),
                "flags": "no-map-pin",
                "notes": scrub(j.get("location_note") or j.get("organisation") or ""),
            }
        )
    return rows


def write_csv(all_rows: list[dict]) -> None:
    gaps = [r for r in all_rows if r["pin_policy_status"] != "policy-ok"]
    fields = [
        "entity_type",
        "entity_id",
        "name",
        "country",
        "location_tier",
        "pin_policy_status",
        "precision",
        "lat",
        "lng",
        "source_url",
        "flags",
        "notes",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in gaps:
            w.writerow({k: r.get(k) for k in fields})


def write_md(sections: dict[str, list[dict]]) -> None:
    today = date.today().isoformat()
    lines = [
        "# Nexus location audit (read-only)",
        "",
        f"Generated: **{today}** from repo bundles (`static/ecosystem/data/actors.json` post [#63](https://github.com/gideonblaauw-creator/cth-nexus/pull/63) / [#79](https://github.com/gideonblaauw-creator/cth-nexus/pull/79) geocoding policy).",
        "",
        "## Policy (audit baseline)",
        "",
        "Map pins should appear **only** at a **verified street address** sourced from the entity's own website or an official directory. Otherwise treat as **location unknown** (country badge / text only).",
        "",
        "Under this strict rule, `precision: city` pins, Nominatim/Photon name+city queries, Wikidata city coordinates, HQ fallbacks, and country-capital hub coordinates count as **suspect** even when lat/lng exist.",
        "",
        "## Summary",
        "",
        "| Entity type | Total | Verified address + coords (strict) | Address precision + coords | City-only (plotted) | Country-only | None | Suspect / guessed pins |",
        "|-------------|------:|-----------------------------------:|-----------------------------:|--------------------:|-------------:|-----:|-----------------------:|",
    ]
    for label, rows in sections.items():
        s = summarize(rows)
        lines.append(
            f"| {label} | {s['total']} | {s['strict_verified_address_coords']} | {s['address_precision_with_coords']} | {s['city_only']} | "
            f"{s['country_only']} | {s['none']} | {s['suspect_or_guessed_pins']} |"
        )

    lines.extend(
        [
            "",
            "Gap export: [`location-gaps.csv`](./location-gaps.csv) (entities not meeting strict verified-address policy; no personal emails/phones).",
            "",
            "### Ideas (BookStack)",
            "",
            "Live Idea Browser pages are served from BookStack (`BOOKSTACK_*` not set in this audit run). Counts above for **idea_curated_*** rows are **offline curated subsets only**, not the full catalog. Full ideas have `country` tags and optional city in markdown — **no lat/lng in the list API**.",
            "",
            "### Portfolio vs `/s/` one-pagers",
            "",
            f"- Portfolio grid (`portfolio-core.json`): **{len(sections.get('portfolio_startup', []))}** startups — ISO country code only.",
            f"- `/s/` JSON one-pagers (`onepagers/data/`): **{len(sections.get('startup_onepager_s', []))}** files; `nexus-crosslinks.json` lists **121** valid slugs.",
            "",
            "## Per-type notes",
            "",
        ]
    )

    notes = {
        "ecosystem_actor": (
            "Primary map dataset for `/ecosystem/`. Plottable pins use `geo.precision` `address` or `city` "
            "(`static/ecosystem/geo-utils.mjs`). Country-precision actors (223) show as country badges only."
        ),
        "ecosystem_funder": "Subset of ecosystem actors with `category` in `funder`, `finance`, `international`.",
        "hub_hubmap": "HubMap (`site/cth-static/hubs/hubs-data.json`). Geo is a single lat/lng per hub; several match national capital coordinates.",
        "portfolio_startup": "No geo fields; legacy `nexus-latam-map.js` used country centroids + jitter (not used by ecosystem MapLibre).",
        "startup_onepager_s": "Public `/s/{slug}` cards — country ribbon only.",
        "mentor_clp26": "CLP26 mentor directory — country string only.",
        "investor_crm": "Investors SPA JSON — `country` sparse; `geo_focus` is investment geography, not office location.",
        "idea_curated_imd_pe": "Proxy subset; not a full BookStack export.",
        "idea_curated_epic": "Epic Angels curated list; not map-backed.",
        "jury_clp26": "Event jury cards — no location fields.",
        "policy_ecosystem": "Policy nodes in ecosystem story — country metadata only (no map pins).",
    }
    for label, rows in sections.items():
        s = summarize(rows)
        lines.append(f"### {label}")
        lines.append("")
        lines.append(notes.get(label, ""))
        lines.append("")
        if label == "ecosystem_actor":
            actor_rows = rows
            by_country = Counter(r["country"] for r in actor_rows)
            lines.append("**By country (actors):** " + ", ".join(f"{c} {n}" for c, n in sorted(by_country.items(), key=lambda x: -x[1])))
            lines.append("")
            plottable = sum(1 for r in actor_rows if r["location_tier"] in ("verified-address+coords", "city-only"))
            lines.append(f"- Map-plottable pins (address+city precision): **{plottable}**")
            lines.append(f"- Policy-ok verified address pins: **{s['policy_ok_pins']}**")
            lines.append(f"- Country badge only: **{s['country_only']}**")
            lines.append("")
        ex = suspect_examples(rows, 4)
        if ex:
            lines.append("**Suspect / non-compliant pin examples:**")
            lines.append("")
            for r in ex:
                lines.append(
                    f"- `{r['entity_id']}` — {r['name']} ({r['country'] or '?'}) "
                    f"tier={r['location_tier']} flags={r['flags'] or '—'}"
                )
            lines.append("")

    lines.extend(
        [
            "## Ecosystem actor precision (deployed bundle)",
            "",
        ]
    )
    actors = load_json(ROOT / "static/ecosystem/data/actors.json")
    prec = Counter((a.get("geo") or {}).get("precision") for a in actors)
    for k in ("address", "city", "country"):
        lines.append(f"- `{k}`: **{prec.get(k, 0)}**")
    lines.append("")
    lines.append("## Regenerate")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 ops/geo/location_audit.py")
    lines.append("```")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    actor_rows = audit_ecosystem_actors()
    funder_rows = audit_actor_subset(actor_rows, {"funder", "finance", "international"}, "ecosystem_funder")

    sections = {
        "ecosystem_actor": actor_rows,
        "ecosystem_funder": funder_rows,
        "hub_hubmap": audit_hubs(),
        "portfolio_startup": audit_portfolio(),
        "startup_onepager_s": audit_onepagers(),
        "mentor_clp26": audit_mentors(),
        "investor_crm": audit_investors_crm(),
        "idea_curated_imd_pe": [r for r in audit_ideas_curated() if r["entity_type"] == "idea_curated_imd_pe"],
        "idea_curated_epic": [r for r in audit_ideas_curated() if r["entity_type"] == "idea_curated_epic"],
        "jury_clp26": audit_jury(),
        "policy_ecosystem": audit_policies(),
    }

    all_rows: list[dict] = []
    for rows in sections.values():
        all_rows.extend(rows)

    write_csv(all_rows)
    write_md(sections)
    print(f"Wrote {OUT_MD} and {OUT_CSV} ({len(all_rows)} entities, {sum(1 for r in all_rows if r['pin_policy_status']!='policy-ok')} gaps)")


if __name__ == "__main__":
    main()
