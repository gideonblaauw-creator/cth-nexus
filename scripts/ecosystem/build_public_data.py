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


def host_key(url: str | None) -> str | None:
    if not url:
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


def norm_name(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "", (s or "").lower())
    return s


def load_onepager_index() -> dict[str, str]:
    """website host / slug / name → card slug"""
    by_host: dict[str, str] = {}
    by_slug: dict[str, str] = {}
    by_name: dict[str, str] = {}
    if not ONEPAGERS.is_dir():
        return {"host": by_host, "slug": by_slug, "name": by_name}
    for path in ONEPAGERS.glob("*.json"):
        if path.name.startswith("s-pages-"):
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        slug = doc.get("slug") or path.stem
        by_slug[slug.lower()] = slug
        nm = norm_name(doc.get("name") or "")
        if nm:
            by_name[nm] = slug
        hk = host_key(doc.get("website"))
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


def sanitize_actor(raw: dict, idx: dict) -> dict:
    a = {k: v for k, v in raw.items() if k not in DROP_KEYS}
    a = scrub_value(a) or {}
    a["geo"] = normalize_geo(raw, raw.get("geo") or a.get("geo"))
    slug = match_card_slug(a, idx)
    nexus = dict(a.get("nexus") or {})
    if slug:
        nexus["card_slug"] = slug
    elif "card_slug" in nexus:
        pass
    else:
        nexus.setdefault("card_slug", None)
    a["nexus"] = nexus
    if a.get("type") == "person" and not a.get("linkedin"):
        a["linkedin"] = None
    return {k: v for k, v in a.items() if k not in DROP_KEYS}


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
    raw_path = DATA / "actors.raw.json"
    actors_path = DATA / "actors.json"
    if not raw_path.exists():
        raw_path.write_text(actors_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Snapshotted source → {raw_path}")

    raw_actors = json.loads(raw_path.read_text(encoding="utf-8"))
    relations = json.loads((DATA / "relations.json").read_text(encoding="utf-8"))
    idx = load_onepager_index()

    actors = [sanitize_actor(a, idx) for a in raw_actors]
    relations = sanitize_relations(relations)

    actors_path.write_text(json.dumps(actors, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (DATA / "relations.json").write_text(json.dumps(relations, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    with_slug = sum(1 for a in actors if a.get("nexus", {}).get("card_slug"))
    print(f"Public actors: {len(actors)}, card_slug: {with_slug}, relations: {len(relations)}")


if __name__ == "__main__":
    main()
