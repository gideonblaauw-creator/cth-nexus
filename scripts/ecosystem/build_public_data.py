#!/usr/bin/env python3
"""Sanitize ecosystem bundle for staff UI: geo, nexus.card_slug, no PII/internal fields."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from prepare_geo import geocode_actor

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "static" / "ecosystem" / "data"
ONEPAGERS = REPO / "onepagers" / "data"
ONEPAGER_SITES = REPO / "onepagers" / "sites"

DROP_KEYS = {
    "notes",
    "website_check",
    "website_ok",
    "source_design_id",
    "page",
    "has_nexus_card",
    "nexus_slug",
    "email",
    "phone",
    "drive_url",
    "internal_notes",
}

SENSITIVE_PATTERNS = [
    re.compile(r"@[\w.-]+\.\w+"),
    re.compile(r"drive\.google\.com", re.I),
    re.compile(r"docs\.google\.com", re.I),
    re.compile(r"\+?\d[\d\s\-()]{7,}\d"),
]


GENERIC_HOSTS = frozenset(
    {"facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com", "linktr.ee"}
)


def host_key(url: str | dict | None) -> str | None:
    if not url:
        return None
    if isinstance(url, dict):
        url = url.get("en") or url.get("es") or url.get("url") or ""
    if not isinstance(url, str) or not url.strip():
        return None
    u = url if url.startswith("http") else f"https://{url}"
    try:
        p = urlparse(u)
        h = p.netloc.lower().replace("www.", "")
        if not h or h in GENERIC_HOSTS:
            return None
        return h or None
    except Exception:
        return None


def scrub_value(v):
    if isinstance(v, str):
        for pat in SENSITIVE_PATTERNS:
            if pat.search(v):
                return None
        return v
    if isinstance(v, dict):
        return {k: scrub_value(x) for k, x in v.items() if scrub_value(x) is not None}
    if isinstance(v, list):
        return [scrub_value(x) for x in v if scrub_value(x) is not None]
    return v


def norm_name(s: str | dict | None) -> str:
    if isinstance(s, dict):
        s = s.get("en") or s.get("es") or s.get("EN") or s.get("ES") or ""
    if not isinstance(s, str):
        s = str(s or "")
    s = re.sub(r"[^a-z0-9]+", "", s.lower())
    return s


def load_onepager_index() -> dict[str, str]:
    """website host / slug / name → card slug"""
    by_host: dict[str, str] = {}
    by_slug: dict[str, str] = {}
    by_name: dict[str, str] = {}
    if not ONEPAGERS.is_dir():
        return {"host": by_host, "slug": by_slug, "name": by_name}
    for path in ONEPAGERS.rglob("*.json"):
        if path.name.startswith("s-pages-"):
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        slug = doc.get("slug") or path.stem
        if isinstance(slug, dict):
            slug = slug.get("en") or slug.get("es") or path.stem
        if not isinstance(slug, str):
            slug = str(slug)
        by_slug[slug.lower()] = slug
        raw_name = doc.get("name") or ""
        if isinstance(raw_name, dict):
            raw_name = raw_name.get("value") or raw_name.get("en") or ""
        nm = norm_name(str(raw_name))
        if nm:
            by_name[nm] = slug
        raw_web = doc.get("website")
        if isinstance(raw_web, dict):
            raw_web = raw_web.get("value")
        hk = host_key(raw_web if isinstance(raw_web, str) else None)
        if hk:
            by_host[hk] = slug
    return {"host": by_host, "slug": by_slug, "name": by_name}


def match_card_slug(actor: dict, idx: dict) -> str | None:
    hk = host_key(actor.get("website"))
    if hk and hk in idx["host"]:
        return idx["host"][hk]
    nm = norm_name(actor.get("name") or "")
    if nm and nm in idx["name"]:
        return idx["name"][nm]
    aid = actor.get("id", "")
    if aid.lower() in idx["slug"]:
        return idx["slug"][aid.lower()]
    tail = aid.split("-", 1)[-1] if "-" in aid else aid
    if tail.lower() in idx["slug"]:
        return idx["slug"][tail.lower()]
    return None


def valid_s_slugs() -> set[str]:
    if not ONEPAGER_SITES.is_dir():
        return set()
    return {
        p.name
        for p in ONEPAGER_SITES.iterdir()
        if p.is_dir() and (p / "index.html").is_file()
    }


def resolve_card_slug(raw: dict, idx: dict, valid_s: set[str] | None = None) -> str | None:
    """Match one-pager /s/{slug} from website, name, id, or staff nexus_slug on raw row."""
    valid_s = valid_s or valid_s_slugs()
    slug = match_card_slug(raw, idx)
    if slug and slug in valid_s:
        return slug
    for cand in (raw.get("nexus_slug"), (raw.get("nexus") or {}).get("card_slug")):
        if not cand:
            continue
        key = str(cand).lower()
        if key in idx["slug"] and idx["slug"][key] in valid_s:
            return idx["slug"][key]
        if key in valid_s:
            return key
    return None


def normalize_geo(raw: dict, geo: dict | None) -> dict:
    if not geo:
        return geocode_actor({**raw, "id": raw["id"]})["geo"]
    prec = geo.get("precision")
    if prec in ("address", "city") and geo.get("lat") is not None and geo.get("lng") is not None:
        return {
            k: geo.get(k)
            for k in ("lat", "lng", "address", "city", "country", "precision", "source_url")
            if geo.get(k) is not None or k in ("lat", "lng", "precision")
        }
    if prec == "country" or geo.get("lat") is None:
        return geocode_actor({**raw, "geo": geo, "id": raw["id"]})["geo"]
    # Legacy jittered coords without precision → do not keep fake pins
    return geocode_actor({**raw, "id": raw["id"]})["geo"]


def sanitize_actor(raw: dict, idx: dict, valid_s: set[str] | None = None) -> dict:
    a = {k: v for k, v in raw.items() if k not in DROP_KEYS}
    a = scrub_value(a) or {}
    a["geo"] = normalize_geo(raw, raw.get("geo") or a.get("geo"))
    slug = resolve_card_slug(raw, idx, valid_s)
    nexus = dict(raw.get("nexus") or a.get("nexus") or {})
    nexus.pop("internal", None)
    if slug:
        nexus["card_slug"] = slug
    else:
        nexus.pop("card_slug", None)
    hub_pages_path = DATA / "hub-pages.json"
    valid_hubs = {
        p.name
        for p in (REPO / "site" / "cth-static" / "hubs").iterdir()
        if p.is_dir() and (p / "index.html").is_file()
    } if (REPO / "site" / "cth-static" / "hubs").is_dir() else set()
    if hub_pages_path.exists():
        hub_pages = json.loads(hub_pages_path.read_text(encoding="utf-8"))
        hub_slug = hub_pages.get(a["id"])
        if hub_slug and hub_slug in valid_hubs:
            nexus["hub_slug"] = hub_slug
    a["nexus"] = nexus if nexus else {}
    if raw.get("card"):
        a["card"] = scrub_value(raw["card"])
    if a.get("type") == "person" and not a.get("linkedin"):
        a["linkedin"] = None
    return {k: v for k, v in a.items() if k not in DROP_KEYS}


def sanitize_policies(policies: list) -> list:
    out = []
    for p in policies:
        clean = {k: v for k, v in p.items() if k not in ("notes", "internal_notes")}
        out.append(scrub_value(clean))
    return out


COUNTRY_CODE = {"Peru": "PE", "Colombia": "CO", "El Salvador": "SV"}


def _entity_country_code(
    entity_id: str,
    actors_by_id: dict,
    policies_by_id: dict,
    challenges: dict,
    datasets: dict | None = None,
) -> str | None:
    datasets = datasets or {}
    if entity_id.startswith("challenge:"):
        return COUNTRY_CODE.get((challenges.get(entity_id) or {}).get("country"))
    if entity_id.startswith("policy:"):
        return COUNTRY_CODE.get((policies_by_id.get(entity_id) or {}).get("country"))
    if entity_id.startswith("dataset:"):
        return COUNTRY_CODE.get((datasets.get(entity_id) or {}).get("country"))
    actor = actors_by_id.get(entity_id)
    if actor:
        return COUNTRY_CODE.get(actor.get("country") or (actor.get("geo") or {}).get("country"))
    return None


def drop_cross_country_graph_relations(
    relations: list,
    actors_by_id: dict,
    policies_by_id: dict,
    challenges: dict,
    datasets: dict | None = None,
) -> tuple[list, int]:
    kept = []
    dropped = 0
    for r in relations:
        cs = _entity_country_code(r.get("source", ""), actors_by_id, policies_by_id, challenges, datasets)
        ct = _entity_country_code(r.get("target", ""), actors_by_id, policies_by_id, challenges, datasets)
        if cs and ct and cs != ct:
            dropped += 1
            continue
        kept.append(r)
    return kept, dropped


def drop_cross_country_policy_relations(
    relations: list,
    actors_by_id: dict,
    policies_by_id: dict,
    challenges: dict,
) -> tuple[list, int]:
    """Remove issues_policy / addresses_challenge edges whose endpoints differ in country."""
    kept = []
    dropped = 0
    for r in relations:
        if r.get("type") not in ("issues_policy", "addresses_challenge"):
            kept.append(r)
            continue
        cs = _entity_country_code(r.get("source", ""), actors_by_id, policies_by_id, challenges)
        ct = _entity_country_code(r.get("target", ""), actors_by_id, policies_by_id, challenges)
        if cs and ct and cs != ct:
            dropped += 1
            continue
        kept.append(r)
    return kept, dropped


def sanitize_policy_relations(relations: list) -> list:
    out = []
    for r in relations:
        clean = {
            "source": r.get("source"),
            "target": r.get("target"),
            "type": r.get("type"),
            "verified": r.get("verified"),
            "suggested": r.get("suggested"),
        }
        if clean["verified"] is None and "suggested" in r:
            clean["verified"] = not r["suggested"]
        url = r.get("source_url")
        if isinstance(url, str):
            for pat in SENSITIVE_PATTERNS:
                if pat.search(url):
                    url = None
                    break
        if url:
            clean["source_url"] = url
        out.append({k: v for k, v in clean.items() if v is not None})
    return out


def sanitize_relations(relations: list) -> list:
    out = []
    for r in relations:
        clean = {k: v for k, v in r.items() if k not in ("evidence", "notes")}
        if "evidence" in r and isinstance(r["evidence"], dict):
            ev = {k: v for k, v in r["evidence"].items() if k != "notes"}
            if ev:
                clean["evidence"] = ev
        out.append(scrub_value(clean))
    return out


def main() -> None:
    from merge_geo_from_live import main as merge_geo_main

    merge_geo_main()

    raw_path = DATA / "actors.raw.json"
    actors_path = DATA / "actors.json"
    if not raw_path.exists():
        raw_path.write_text(actors_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Snapshotted source → {raw_path}")

    raw_actors = json.loads(raw_path.read_text(encoding="utf-8"))
    relations = json.loads((DATA / "relations.json").read_text(encoding="utf-8"))
    story_path = DATA / "story-chapters.json"
    challenges = {}
    datasets = {}
    if story_path.exists():
        story_doc = json.loads(story_path.read_text(encoding="utf-8"))
        challenges = story_doc.get("challenges") or {}
        datasets = story_doc.get("datasets") or {}
    idx = load_onepager_index()
    valid_s = valid_s_slugs()

    actors = [sanitize_actor(a, idx, valid_s) for a in raw_actors]
    actors_by_id_pre = {a["id"]: a for a in actors}
    relations, dropped_gr = drop_cross_country_graph_relations(
        relations, actors_by_id_pre, {}, challenges, datasets,
    )
    if dropped_gr:
        print(f"Dropped {dropped_gr} cross-country graph relation(s)")
    relations = sanitize_relations(relations)

    actors_path.write_text(json.dumps(actors, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (DATA / "relations.json").write_text(json.dumps(relations, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    policies_path = DATA / "policies.json"
    policy_rels_path = DATA / "policy_relations.json"
    if policies_path.exists():
        policies = sanitize_policies(json.loads(policies_path.read_text(encoding="utf-8")))
        policies_path.write_text(json.dumps(policies, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if policy_rels_path.exists():
        story_path = DATA / "story-chapters.json"
        challenges = {}
        if story_path.exists():
            challenges = json.loads(story_path.read_text(encoding="utf-8")).get("challenges") or {}
        policies_by_id = {}
        if policies_path.exists():
            for p in json.loads(policies_path.read_text(encoding="utf-8")):
                if p.get("id"):
                    policies_by_id[p["id"]] = p
        actors_by_id = {a["id"]: a for a in actors}
        raw_prel = json.loads(policy_rels_path.read_text(encoding="utf-8"))
        raw_prel, dropped_cc = drop_cross_country_policy_relations(
            raw_prel, actors_by_id, policies_by_id, challenges,
        )
        if dropped_cc:
            print(f"Dropped {dropped_cc} cross-country policy relation(s)")
        prel = sanitize_policy_relations(raw_prel)
        policy_rels_path.write_text(json.dumps(prel, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    with_slug = sum(1 for a in actors if a.get("nexus", {}).get("card_slug"))
    pol_n = len(json.loads(policies_path.read_text())) if policies_path.exists() else 0
    pol_r = len(json.loads(policy_rels_path.read_text())) if policy_rels_path.exists() else 0
    print(f"Public actors: {len(actors)}, card_slug: {with_slug}, relations: {len(relations)}, policies: {pol_n}, policy_relations: {pol_r}")

    try:
        from build_nexus_crosslinks import main as build_crosslinks_main

        build_crosslinks_main()
    except Exception as exc:
        print(f"warn: build_nexus_crosslinks failed: {exc}")


if __name__ == "__main__":
    main()
