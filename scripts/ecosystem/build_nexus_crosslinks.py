#!/usr/bin/env python3
"""Build nexus-crosslinks.json: validated /s/, /hubs/, /ideas/ hrefs + challenge/policy panels."""
from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "static" / "ecosystem" / "data"
ONEPAGERS = REPO / "onepagers"
SITES = ONEPAGERS / "sites"
ONEPAGER_DATA = ONEPAGERS / "data"
HUBS = REPO / "site" / "cth-static" / "hubs"

COUNTRY_CODE = {
    "Peru": "PE",
    "PE": "PE",
    "Colombia": "CO",
    "CO": "CO",
    "El Salvador": "SV",
    "SV": "SV",
}

CT_RE = re.compile(r"CT-[A-Z]{2}-\d{3}")


def norm_name(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def valid_s_slugs() -> set[str]:
    if not SITES.is_dir():
        return set()
    return {p.name for p in SITES.iterdir() if p.is_dir() and (p / "index.html").is_file()}


def valid_hub_slugs() -> set[str]:
    if not HUBS.is_dir():
        return set()
    return {p.name for p in HUBS.iterdir() if p.is_dir() and (p / "index.html").is_file()}


def extract_ct_codes(obj) -> set[str]:
    found: set[str] = set()
    if isinstance(obj, str):
        found.update(CT_RE.findall(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            found.update(extract_ct_codes(v))
    elif isinstance(obj, list):
        for v in obj:
            found.update(extract_ct_codes(v))
    return found


def country_cc(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = str(raw).strip()
    if len(raw) == 2:
        return raw.upper()
    return COUNTRY_CODE.get(raw)


def load_onepager_records(valid_s: set[str]) -> list[dict]:
    out: list[dict] = []
    for slug in sorted(valid_s):
        path = SITES / slug / "index.html"
        meta_path = ONEPAGER_DATA / f"{slug}.json"
        doc = load_json(meta_path) if meta_path.exists() else {}
        doc = doc or {}
        name = doc.get("name")
        if isinstance(name, dict):
            name = name.get("en") or name.get("es")
        if not name:
            name = slug.replace("-", " ").title()
        cts = extract_ct_codes(doc)
        cc = country_cc(doc.get("country"))
        if not cc and doc.get("hq_country"):
            cc = country_cc(doc.get("hq_country"))
        out.append(
            {
                "kind": "startup",
                "label": str(name),
                "href": f"/s/{slug}/",
                "slug": slug,
                "country": cc,
                "ct_codes": sorted(cts),
                "actor_id": None,
            }
        )
    return out


def iter_curated_ideas(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    for path in paths:
        raw = load_json(path)
        if raw is None:
            continue
        items = raw if isinstance(raw, list) else raw.get("startups") or raw.get("ideas") or []
        for it in items:
            if not isinstance(it, dict):
                continue
            href = it.get("nexus_path") or ""
            if not href.startswith("/ideas/"):
                slug = it.get("slug")
                if slug:
                    href = f"/ideas/{slug}"
            if not href.startswith("/ideas/"):
                continue
            if href in seen:
                continue
            seen.add(href)
            cts = set()
            for k in ("ct1", "ct2", "ct_taxonomy", "ct"):
                v = it.get(k)
                if isinstance(v, str):
                    cts.update(CT_RE.findall(v))
            rows.append(
                {
                    "kind": "idea",
                    "label": it.get("name") or it.get("startup_name") or it.get("n") or href.split("/")[-1],
                    "href": href,
                    "country": country_cc(it.get("country") or it.get("c")),
                    "ct_codes": sorted(cts),
                    "stage": it.get("stage") or it.get("st"),
                }
            )
    return rows


def enrich_ct_from_shareables(catalog: list[dict], ideas_rows: list[dict]) -> None:
    """Attach CT codes from curated/shareable rows to /s/ slugs by normalized label."""
    by_norm: dict[str, set[str]] = {}
    for row in ideas_rows:
        cts = set(row.get("ct_codes") or [])
        if not cts:
            continue
        by_norm[norm_name(row.get("label") or "")] = cts
    for rec in catalog:
        if rec["kind"] not in ("startup", "solution"):
            continue
        slug = rec.get("slug") or ""
        keys = {norm_name(rec.get("label")), norm_name(slug), norm_name(slug.replace("-", " "))}
        merged = set(rec.get("ct_codes") or [])
        for k in keys:
            if k in by_norm:
                merged.update(by_norm[k])
        if merged:
            rec["ct_codes"] = sorted(merged)


def load_portfolio_startups(valid_s: set[str]) -> list[dict]:
    path = REPO / "site" / "nexus-assets" / "previews" / "startups-redesign-20261016" / "portfolio-core.json"
    raw = load_json(path)
    if not raw:
        return []
    out: list[dict] = []
    by_norm: dict[str, str] = {}
    for slug in valid_s:
        by_norm[norm_name(slug)] = slug
        by_norm[norm_name(slug.replace("-", " "))] = slug
    for it in raw.get("startups") or []:
        name = it.get("n") or ""
        nm = norm_name(name)
        slug = by_norm.get(nm)
        if not slug:
            continue
        cts = {it.get("ct1"), it.get("ct2")} - {None}
        cts = sorted({c for c in cts if isinstance(c, str) and c.startswith("CT-")})
        out.append(
            {
                "kind": "solution",
                "label": name,
                "href": f"/s/{slug}/",
                "slug": slug,
                "country": country_cc(it.get("c")),
                "ct_codes": cts,
            }
        )
    return out


def ct_match(codes: set[str], challenge_ct: set[str]) -> bool:
    if not codes or not challenge_ct:
        return False
    if codes & challenge_ct:
        return True
    pref_a = {c[:6] for c in codes}
    pref_b = {c[:6] for c in challenge_ct}
    return bool(pref_a & pref_b)


def theme_match(policy_sectors: list, themes: list[str]) -> bool:
    if not policy_sectors or not themes:
        return False
    joined = " ".join(str(s).lower() for s in policy_sectors)
    return any(t in joined for t in themes)


def link_row(label: str, href: str, inferred: bool, kind: str) -> dict:
    return {"label": label, "href": href, "inferred": inferred, "kind": kind}


def build_challenge_links(
    challenge_id: str,
    ct_cfg: dict,
    challenge_cc: str | None,
    catalog: list[dict],
    relations: list,
    actors_by_id: dict,
    valid_s: set[str],
) -> dict:
    challenge_ct = set(ct_cfg.get("ct_codes") or [])
    verified_actor_ids = {
        r["source"]
        for r in relations
        if r.get("type") == "works_on_challenge" and r.get("target") == challenge_id
    }
    ideas: list[dict] = []
    solutions: list[dict] = []
    startups: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add(bucket: list, row: dict, bucket_key: str):
        key = (bucket_key, row["href"])
        if key in seen:
            return
        seen.add(key)
        bucket.append(row)

    for item in catalog:
        icc = item.get("country")
        if challenge_cc and icc != challenge_cc:
            continue
        kind = item["kind"]
        inferred = True
        if kind == "startup" and item.get("actor_id") in verified_actor_ids:
            inferred = False
        if not ct_match(set(item.get("ct_codes") or []), challenge_ct):
            if kind != "startup" or item.get("actor_id") not in verified_actor_ids:
                continue
        if kind == "idea":
            add(ideas, link_row(item["label"], item["href"], inferred, "idea"), "ideas")
        elif kind in ("startup", "solution"):
            add(solutions, link_row(item["label"], item["href"], inferred, "solution"), "solutions")
            aid = item.get("actor_id")
            if aid and actors_by_id.get(aid, {}).get("category") == "startup":
                add(
                    startups,
                    link_row(
                        item["label"],
                        item["href"],
                        aid not in verified_actor_ids,
                        "startup",
                    ),
                    "startups",
                )

    for aid in verified_actor_ids:
        a = actors_by_id.get(aid)
        if not a:
            continue
        if challenge_cc and country_cc(a.get("country")) != challenge_cc:
            continue
        slug = (a.get("nexus") or {}).get("card_slug")
        if not slug or slug not in valid_s:
            tail = aid.split("-")[-1]
            if tail in valid_s:
                slug = tail
            else:
                continue
        href = f"/s/{slug}/"
        inferred = a.get("category") != "startup"
        add(startups, link_row(a.get("name") or slug, href, inferred, "startup"), "startups")

    cap = 16
    return {
        "ideas": ideas[:cap],
        "solutions": solutions[:cap],
        "startups": startups[:cap],
    }


def build_policy_links(
    policy_id: str,
    policy: dict,
    challenge_map: dict,
    ct_map: dict,
    catalog: list[dict],
    policy_relations: list,
    relations: list,
    actors_by_id: dict,
    valid_s: set[str],
) -> list[dict]:
    p_cc = country_cc(policy.get("country"))
    sectors = policy.get("sectors") or []
    linked_challenges: set[str] = set()
    for r in policy_relations:
        if r.get("source") != policy_id and r.get("target") != policy_id:
            continue
        other = r["target"] if r["source"] == policy_id else r["source"]
        if other.startswith("challenge:"):
            linked_challenges.add(other)

    policy_ct: set[str] = set()
    for ch_id in linked_challenges:
        cfg = ct_map.get(ch_id) or {}
        policy_ct.update(cfg.get("ct_codes") or [])
    if not policy_ct:
        for ch_id, cfg in ct_map.items():
            if theme_match(sectors, cfg.get("policy_themes") or []):
                policy_ct.update(cfg.get("ct_codes") or [])

    out: list[dict] = []
    seen: set[str] = set()

    def add(label, href, inferred):
        if href in seen:
            return
        seen.add(href)
        out.append(link_row(label, href, inferred, "startup"))

    for r in policy_relations:
        if r.get("source") != policy_id and r.get("target") != policy_id:
            continue
        other = r["target"] if r["source"] == policy_id else r["source"]
        a = actors_by_id.get(other)
        if not a or a.get("category") != "startup":
            continue
        if p_cc and country_cc(a.get("country")) != p_cc:
            continue
        slug = (a.get("nexus") or {}).get("card_slug")
        if not slug or slug not in valid_s:
            continue
        inferred = r.get("type") in ("addresses_challenge", "issues_policy") and not r.get("verified", True)
        add(a.get("name") or slug, f"/s/{slug}/", inferred)

    if policy_ct and linked_challenges:
        for item in catalog:
            if item["kind"] not in ("startup", "solution"):
                continue
            icc = item.get("country")
            if p_cc and icc != p_cc:
                continue
            if not ct_match(set(item.get("ct_codes") or []), policy_ct):
                continue
            slug = item.get("slug")
            if not slug or slug not in valid_s:
                continue
            add(item["label"], item["href"], True)

    return out[:24]


def http_ok(origin: str, href: str) -> bool:
    url = origin.rstrip("/") + href
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as resp:
            return 200 <= resp.status < 400
    except Exception:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=8) as resp:
                return 200 <= resp.status < 400
        except Exception:
            return False


def filter_http(origin: str | None, rows: list[dict]) -> list[dict]:
    if not origin:
        return rows
    kept = []
    for row in rows:
        if http_ok(origin, row["href"]):
            kept.append(row)
    return kept


def main() -> None:
    origin = os.environ.get("NEXUS_LINK_ORIGIN", "").strip()
    valid_s = valid_s_slugs()
    valid_hubs = valid_hub_slugs()
    ct_map = load_json(DATA / "challenge-ct-map.json") or {}
    story = load_json(DATA / "story-chapters.json") or {}
    challenges = story.get("challenges") or {}
    actors = load_json(DATA / "actors.json") or []
    if not actors:
        actors = load_json(DATA / "actors.raw.json") or []
    actors_by_id = {a["id"]: a for a in actors}
    relations = load_json(DATA / "relations.json") or []
    policies = load_json(DATA / "policies.json") or []
    policies_by_id = {p["id"]: p for p in policies if p.get("id")}
    policy_relations = load_json(DATA / "policy_relations.json") or []

    curated_paths = [
        REPO / "app" / "nexus-ideas" / "src" / "data" / "imd-peru-curated.json",
        REPO / "app" / "nexus-ideas" / "src" / "data" / "epic-angels-curated.json",
        REPO / "app" / "nexus-ideas" / "deploy" / "imd-peru-shareable.json",
        REPO / "site" / "nexus-assets" / "imd-peru-shareable.json",
        REPO / "site" / "nexus-assets" / "epic-angels-shareable.json",
        REPO / "site" / "nexus-assets" / "clp26-national-shareable.json",
    ]
    ideas = iter_curated_ideas(curated_paths)
    ideas_manifest = {r["href"] for r in ideas}

    catalog: list[dict] = []
    catalog.extend(load_onepager_records(valid_s))
    catalog.extend(load_portfolio_startups(valid_s))
    for idea in ideas:
        catalog.append({**idea, "kind": "idea"})
    for sol in load_portfolio_startups(valid_s):
        catalog.append({**sol, "kind": "solution"})
    enrich_ct_from_shareables(catalog, ideas)

    slug_to_actor: dict[str, str] = {}
    slug_to_country: dict[str, str] = {}
    for a in actors:
        slug = (a.get("nexus") or {}).get("card_slug") or a.get("nexus_slug")
        tail = a["id"].split("-")[-1] if "-" in a["id"] else a["id"]
        cc = country_cc(a.get("country"))
        if tail in valid_s and cc:
            slug_to_country[tail] = cc
        if slug and slug in valid_s:
            slug_to_actor[slug] = a["id"]
            if cc:
                slug_to_country[slug] = cc
    for rec in catalog:
        slug = rec.get("slug")
        if slug and slug in slug_to_country and not rec.get("country"):
            rec["country"] = slug_to_country[slug]
        if rec["kind"] == "startup" and slug in slug_to_actor:
            rec["actor_id"] = slug_to_actor[slug]
            act = actors_by_id[rec["actor_id"]]
            rec["country"] = country_cc(act.get("country")) or rec.get("country")

    by_challenge: dict = {}
    def filter_panel(panel: dict) -> dict:
        out = {}
        for key, rows in panel.items():
            kept = []
            for row in rows:
                href = row["href"]
                if href.startswith("/s/") or href.startswith("/hubs/"):
                    slug = href.strip("/").split("/")[-1]
                    if href.startswith("/s/") and slug not in valid_s:
                        continue
                    if href.startswith("/hubs/") and slug not in valid_hubs:
                        continue
                    if origin and not http_ok(origin, href):
                        continue
                    kept.append(row)
                elif href.startswith("/ideas/"):
                    if href not in ideas_manifest:
                        continue
                    if origin and not http_ok(origin, href):
                        continue
                    kept.append(row)
            out[key] = kept
        return out

    for ch_id, meta in challenges.items():
        cc = country_cc(meta.get("country"))
        cfg = ct_map.get(ch_id) or {}
        panel = build_challenge_links(
            ch_id, cfg, cc, catalog, relations, actors_by_id, valid_s,
        )
        by_challenge[ch_id] = filter_panel(panel)

    by_policy: dict = {}
    for pid, pol in policies_by_id.items():
        rows = build_policy_links(
            pid, pol, challenges, ct_map, catalog, policy_relations, relations, actors_by_id, valid_s,
        )
        filtered = []
        for row in rows:
            href = row["href"]
            if not href.startswith("/s/"):
                continue
            slug = href.strip("/").split("/")[-1]
            if slug not in valid_s:
                continue
            if origin and not http_ok(origin, href):
                continue
            filtered.append(row)
        if filtered:
            by_policy[pid] = filtered

    counts = {
        "s_pages": len(valid_s),
        "hub_pages": len(valid_hubs),
        "ideas_manifest": len(ideas_manifest),
        "challenge_ideas": sum(len(v.get("ideas") or []) for v in by_challenge.values()),
        "challenge_solutions": sum(len(v.get("solutions") or []) for v in by_challenge.values()),
        "challenge_startups": sum(len(v.get("startups") or []) for v in by_challenge.values()),
        "policy_startup_links": sum(len(v) for v in by_policy.values()),
        "actor_card_slug": sum(
            1 for a in actors if (a.get("nexus") or {}).get("card_slug") in valid_s
        ),
    }

    out = {
        "version": 1,
        "valid": {
            "s": sorted(valid_s),
            "hubs": sorted(valid_hubs),
            "ideas": sorted(ideas_manifest),
        },
        "byChallenge": by_challenge,
        "byPolicy": by_policy,
        "counts": counts,
    }
    out_path = DATA / "nexus-crosslinks.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "nexus-crosslinks:",
        f"s={counts['s_pages']}",
        f"hubs={counts['hub_pages']}",
        f"ideas={counts['ideas_manifest']}",
        f"ch_ideas={counts['challenge_ideas']}",
        f"ch_solutions={counts['challenge_solutions']}",
        f"ch_startups={counts['challenge_startups']}",
        f"policy_startups={counts['policy_startup_links']}",
    )


if __name__ == "__main__":
    main()
