#!/usr/bin/env python3
"""Geocode ecosystem actors: websites → Wikidata → Nominatim (1 req/s)."""
from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "static" / "ecosystem" / "data" / "actors.json"
OUT = DATA
CACHE_PATH = Path(__file__).resolve().parent / "geocode-cache.json"
REVIEW_CSV = Path(__file__).resolve().parent / "geocode-review.csv"
OVERRIDES_PATH = Path(__file__).resolve().parent / "geocode-overrides.json"

UA = "CleantechHUB-Nexus-Ecosystem-Geocoder/1.0 (https://nexus.cleantechhub.net; ops@cleantechhub.net)"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
PHOTON = "https://photon.komoot.io/api/"
WIKI_SEARCH = "https://www.wikidata.org/w/api.php"
WIKI_ENTITY = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"

COUNTRY_BOUNDS = {
    "Peru": {"lat_min": -18.6, "lat_max": -0.02, "lng_min": -81.5, "lng_max": -68.6},
    "Colombia": {"lat_min": -4.3, "lat_max": 13.5, "lng_min": -79.1, "lng_max": -66.8},
    "El Salvador": {"lat_min": 12.95, "lat_max": 14.45, "lng_min": -90.2, "lng_max": -87.6},
}

CAPITAL = {
    "Peru": "Lima",
    "Colombia": "Bogotá",
    "El Salvador": "San Salvador",
}

CONTACT_PATHS = ("/contacto", "/contact", "/nosotros", "/about")

MAP_COORD_RE = re.compile(
    r"(?:@|!3d)(-?\d+\.\d+)[!,](?:!4d|-)(-?\d+\.\d+)|"
    r"center=(-?\d+\.\d+)%2C(-?\d+\.\d+)|"
    r"q=(-?\d+\.\d+),(-?\d+\.\d+)",
    re.I,
)
JSONLD_ADDR_RE = re.compile(
    r'"@type"\s*:\s*"PostalAddress"[^}]*"streetAddress"\s*:\s*"([^"]+)"[^}]*'
    r'(?:"addressLocality"\s*:\s*"([^"]+)")?',
    re.S | re.I,
)
STREET_RE = re.compile(
    r"(?:Calle|Av\.|Avenida|Jr\.|Jirón|Carrera|Cl\.|Pasaje|Blvd\.|Boulevard)"
    r"[^<\n]{5,120}",
    re.I,
)
CITY_HINT_RE = re.compile(
    r"\b(Lima|San Isidro|Miraflores|Surco|Santiago de Surco|La Molina|"
    r"Barranco|San Borja|San Miguel|Callao|Arequipa|Cusco|Trujillo|Piura|"
    r"Bogotá|Medellín|Cali|Barranquilla|Cartagena|"
    r"San Salvador|Santa Tecla|Antiguo Cuscatlán)\b",
    re.I,
)


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def http_get(url: str, timeout: float = 8.0) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(800_000)
            ctype = resp.headers.get("Content-Type", "")
            charset = "utf-8"
            if "charset=" in ctype:
                charset = ctype.split("charset=")[-1].split(";")[0].strip()
            return raw.decode(charset, errors="replace")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def point_in_country(lat: float, lng: float, country: str) -> bool:
    b = COUNTRY_BOUNDS.get(country)
    if not b:
        return True
    return b["lat_min"] <= lat <= b["lat_max"] and b["lng_min"] <= lng <= b["lng_max"]


_last_nominatim = 0.0
_nominatim_cache: dict[str, dict | None] = {}


def resolve_query(query: str, country: str | None = None) -> dict | None:
    hit = photon(query, country)
    if hit:
        return hit
    return nominatim(query, country)


def _pick_photon_feature(feats: list, country: str | None) -> tuple | None:
    cc = {"Peru": "PE", "Colombia": "CO", "El Salvador": "SV"}.get(country or "")
    capital = CAPITAL.get(country or "", "").lower()
    best = None
    best_score = -999
    for feat in feats:
        props = feat.get("properties") or {}
        if cc and props.get("countrycode", "").upper() != cc:
            continue
        coords = feat["geometry"]["coordinates"]
        lng, lat = float(coords[0]), float(coords[1])
        if country and not point_in_country(lat, lng, country):
            continue
        city = (props.get("city") or props.get("name") or "").lower()
        score = 0
        if capital and capital.split()[0] in city:
            score += 4
        if props.get("street"):
            score += 3
        if props.get("osm_value") in ("bank", "company", "university", "ngo", "government"):
            score += 2
        if props.get("type") in ("house", "building"):
            score += 1
        if score > best_score:
            best_score = score
            best = (feat, lat, lng)
    return best


def photon(query: str, country: str | None = None) -> dict | None:
    params = {"q": query, "limit": 5}
    url = PHOTON + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None
    picked = _pick_photon_feature(data.get("features") or [], country)
    if not picked:
        return None
    feat, lat, lng = picked
    props = feat.get("properties") or {}
    city = props.get("city") or props.get("name")
    street = props.get("street")
    housenumber = props.get("housenumber")
    address = ", ".join(
        x
        for x in (f"{street} {housenumber}".strip() if street else None, city, props.get("country"))
        if x
    )
    precision = "address" if street else ("city" if city else "country")
    return {
        "lat": lat,
        "lng": lng,
        "address": address or None,
        "city": city,
        "country": country or props.get("country"),
        "source_url": url + f" (q={query})",
        "precision": precision,
    }


def nominatim(query: str, country: str | None = None) -> dict | None:
    global _last_nominatim
    cache_key = f"{country or ''}|{query.lower().strip()}"
    if cache_key in _nominatim_cache:
        return _nominatim_cache[cache_key]
    wait = 1.1 - (time.time() - _last_nominatim)
    if wait > 0:
        time.sleep(wait)
    params = {"q": query, "format": "json", "limit": 1, "addressdetails": 1}
    cc = {"Peru": "pe", "Colombia": "co", "El Salvador": "sv"}.get(country or "")
    if cc:
        params["countrycodes"] = cc
    url = NOMINATIM + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
        _last_nominatim = time.time()
        if body.lstrip().startswith("<"):
            alt = photon(query, country)
            _nominatim_cache[cache_key] = alt
            return alt
        data = json.loads(body)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        _last_nominatim = time.time()
        alt = photon(query, country)
        _nominatim_cache[cache_key] = alt
        return alt
    if not data:
        alt = photon(query, country)
        _nominatim_cache[cache_key] = alt
        return alt
    hit = data[0]
    result = {
        "lat": float(hit["lat"]),
        "lng": float(hit["lon"]),
        "address": hit.get("display_name", query),
        "city": _pick_city(hit.get("address") or {}),
        "country": country or hit.get("address", {}).get("country"),
        "source_url": url,
        "precision": _nominatim_precision(hit),
    }
    _nominatim_cache[cache_key] = result
    return result


def _pick_city(addr: dict) -> str | None:
    for k in ("city", "town", "village", "municipality", "county", "state"):
        if addr.get(k):
            return addr[k]
    return None


def _nominatim_precision(hit: dict) -> str:
    typ = hit.get("type", "")
    cls = hit.get("class", "")
    if cls in ("building", "amenity", "office", "shop") or typ in (
        "house",
        "building",
        "commercial",
        "industrial",
        "university",
        "company",
    ):
        return "address"
    if typ in ("city", "town", "village", "suburb", "neighbourhood", "quarter"):
        return "city"
    if typ in ("country", "state", "region"):
        return "country"
    add = hit.get("address") or {}
    if add.get("road") or add.get("house_number"):
        return "address"
    if add.get("city") or add.get("town"):
        return "city"
    return "city"


def wikidata_lookup(name: str) -> dict | None:
    q = urllib.parse.urlencode(
        {"action": "wbsearchentities", "search": name, "language": "es", "format": "json", "limit": 3}
    )
    raw = http_get(f"{WIKI_SEARCH}?{q}", timeout=15)
    if not raw:
        return None
    try:
        hits = json.loads(raw).get("search") or []
    except json.JSONDecodeError:
        return None
    if not hits:
        return None
    qid = hits[0]["id"]
    ent_raw = http_get(WIKI_ENTITY.format(qid=qid), timeout=15)
    if not ent_raw:
        return None
    try:
        ent = json.loads(ent_raw)["entities"][qid]
    except (KeyError, json.JSONDecodeError):
        return None
    claims = ent.get("claims") or {}
    source_url = f"https://www.wikidata.org/wiki/{qid}"

    def coord_from_claim(label: str, prop: str) -> dict | None:
        for c in claims.get(prop, []):
            try:
                lat = c["mainsnak"]["datavalue"]["value"]["latitude"]
                lng = c["mainsnak"]["datavalue"]["value"]["longitude"]
            except (KeyError, TypeError):
                continue
            return {
                "lat": float(lat),
                "lng": float(lng),
                "address": None,
                "city": None,
                "country": None,
                "source_url": source_url + f" ({label})",
                "precision": "city",
            }
        return None

    return coord_from_claim("P625", "P625") or coord_from_claim("P159", "P159")


def scrape_website(base_url: str | None) -> dict | None:
    if not base_url:
        return None
    if not base_url.startswith("http"):
        base_url = "https://" + base_url
    parsed = urllib.parse.urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    urls = [base_url.rstrip("/"), origin + "/contacto", origin + "/contact"]

    for url in urls:
        html = http_get(url, timeout=4.0)
        if not html:
            continue
        html = unescape(html)
        for m in MAP_COORD_RE.finditer(html):
            groups = [g for g in m.groups() if g]
            if len(groups) >= 2:
                lat, lng = float(groups[0]), float(groups[1])
                return {
                    "lat": lat,
                    "lng": lng,
                    "address": None,
                    "city": None,
                    "country": None,
                    "source_url": url,
                    "precision": "address",
                }
        jm = JSONLD_ADDR_RE.search(html)
        if jm:
            street = jm.group(1)
            city = jm.group(2)
            return {
                "lat": None,
                "lng": None,
                "address": street,
                "city": city,
                "country": None,
                "source_url": url,
                "precision": "address",
                "geocode_query": ", ".join(x for x in (street, city) if x),
            }
        streets = STREET_RE.findall(html)
        cities = CITY_HINT_RE.findall(html)
        if streets:
            city = cities[0] if cities else None
            return {
                "lat": None,
                "lng": None,
                "address": streets[0][:200],
                "city": city,
                "country": None,
                "source_url": url,
                "precision": "address",
                "geocode_query": ", ".join(x for x in (streets[0][:120], city) if x),
            }
        if cities:
            return {
                "lat": None,
                "lng": None,
                "address": None,
                "city": cities[0],
                "country": None,
                "source_url": url,
                "precision": "city",
                "geocode_query": f"{cities[0]}",
            }
    return None


def latam_office_query(actor: dict) -> str | None:
    """Prefer in-country office for international actors mapped to a country."""
    if actor.get("category") != "international":
        return None
    country = actor.get("country") or ""
    capital = CAPITAL.get(country, "")
    name = actor.get("name") or ""
    short = re.split(r"[–(/]", name)[0].strip()
    website = (actor.get("website") or "").lower()
    if f"/{country.lower()}" in website or f"/es/{country[:3].lower()}" in website:
        pass
    if "peru" in website and country == "Peru":
        return f"{short} Lima Peru"
    if "colombia" in website and country == "Colombia":
        return f"{short} Bogotá Colombia"
    if country == "El Salvador":
        return f"{short} San Salvador El Salvador"
    if country == "Peru":
        return f"{short} oficina {capital} Peru"
    if country == "Colombia":
        return f"{short} oficina {capital} Colombia"
    return None


def build_queries(actor: dict, scraped: dict | None) -> list[tuple[str, str]]:
    """Return (query, reason) pairs in priority order."""
    country = actor.get("country") or "Peru"
    name = actor.get("name") or ""
    capital = CAPITAL.get(country, "")
    out: list[tuple[str, str]] = []

    if scraped:
        gq = scraped.get("geocode_query")
        if gq:
            out.append((f"{gq}, {country}", "website-text"))
        elif scraped.get("city") and not scraped.get("address"):
            out.append((f"{scraped['city']}, {country}", "website-city"))

    if actor.get("city"):
        out.append((f"{actor['city']}, {country}", "actor-city"))

    latam = latam_office_query(actor)
    if latam:
        out.append((latam, "latam-office"))

    out.append((f"{name}, {capital}, {country}", "name-capital"))
    out.append((f"{name}, {country}", "name-country"))
    # Deduplicate preserving order
    seen = set()
    deduped = []
    for q, r in out:
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append((q, r))
    return deduped


def finalize_geo(raw: dict, actor: dict) -> dict | None:
    country = actor.get("country") or "Peru"
    if raw.get("lat") is None or raw.get("lng") is None:
        gq = raw.get("geocode_query") or raw.get("address") or raw.get("city")
        if not gq:
            return None
        q = gq if country.lower() in gq.lower() else f"{gq}, {country}"
        nom = resolve_query(q, country)
        if not nom:
            return None
        raw = {**raw, **nom}

    lat, lng = raw["lat"], raw["lng"]
    flags = []
    if not point_in_country(lat, lng, country):
        flags.append("country_mismatch")
    geo = {
        "lat": round(lat, 6),
        "lng": round(lng, 6),
        "address": raw.get("address"),
        "city": raw.get("city") or actor.get("city"),
        "country": country,
        "precision": raw.get("precision") or "city",
        "source_url": raw.get("source_url"),
    }
    if flags:
        geo["flags"] = flags
    if raw.get("office_note"):
        geo["office_note"] = raw["office_note"]
    return geo


def geocode_actor(actor: dict, overrides: dict, cache: dict) -> tuple[dict | None, list[str]]:
    aid = actor["id"]
    if aid in cache:
        return cache[aid].get("geo"), cache[aid].get("flags", [])

    flags: list[str] = []
    raw = None
    scraped = None

    if aid in overrides:
        raw = dict(overrides[aid])
        raw.setdefault("office_note", overrides[aid].get("office_note", "override"))

    scraped = None
    if (not raw or raw.get("lat") is None) and actor.get("city"):
        nom = resolve_query(f"{actor['city']}, {actor.get('country')}", actor.get("country"))
        if nom:
            raw = {**nom, "source_url": nom["source_url"] + " (actor-city)"}

    if not raw or raw.get("lat") is None:
        for query, reason in build_queries(actor, None)[:3]:
            nom = resolve_query(query, actor.get("country"))
            if nom:
                raw = {**nom, "source_url": nom["source_url"] + f" ({reason})"}
                if reason == "latam-office":
                    raw["office_note"] = "LATAM/country office (international actor)"
                break

    if not raw or raw.get("lat") is None:
        scraped = scrape_website(actor.get("website"))
        if scraped:
            raw = scraped

    if (not raw or raw.get("precision") in (None, "city", "country")) and actor.get("website"):
        scraped = scraped or scrape_website(actor.get("website"))
        if scraped and (scraped.get("lat") is not None or scraped.get("geocode_query")):
            upgraded = finalize_geo(scraped, actor)
            if upgraded and upgraded.get("precision") == "address":
                raw = {**upgraded, "source_url": scraped.get("source_url")}

    if (not raw or raw.get("lat") is None) and actor.get("category") == "international":
        nom = resolve_query(actor.get("name") or "", None)
        if nom:
            raw = {
                **nom,
                "office_note": "HQ (no in-country office found)",
                "source_url": nom["source_url"] + " (HQ-fallback)",
            }
            flags.append("hq_fallback")

    if (not raw or raw.get("lat") is None) and not scraped:
        wd = wikidata_lookup(actor.get("name") or "")
        if wd:
            raw = wd

    geo = finalize_geo(raw, actor) if raw else None

    if not geo:
        # country-only: no coordinates for map jitter
        geo = {
            "lat": None,
            "lng": None,
            "address": None,
            "city": actor.get("city"),
            "country": actor.get("country"),
            "precision": "country",
            "source_url": None,
        }
        flags.append("not_found")

    cache[aid] = {"geo": geo, "flags": flags}
    return geo, flags


def main() -> None:
    overrides = load_json(OVERRIDES_PATH, {})
    cache = load_json(CACHE_PATH, {})
    actors = json.loads(DATA.read_text(encoding="utf-8"))
    review_rows = []

    for i, actor in enumerate(actors):
        geo, flags = geocode_actor(actor, overrides, cache)
        if geo and geo.get("lat") is not None:
            actor["geo"] = geo
        elif geo:
            actor["geo"] = geo
        if geo and geo.get("city") and not actor.get("city"):
            actor["city"] = geo["city"]
        review_rows.append(
            {
                "name": actor.get("name"),
                "website": actor.get("website"),
                "address": (geo or {}).get("address") or "",
                "lat": (geo or {}).get("lat"),
                "lng": (geo or {}).get("lng"),
                "precision": (geo or {}).get("precision") or "not_found",
                "source_url": (geo or {}).get("source_url") or "",
                "flags": ";".join(flags + ((geo or {}).get("flags") or [])),
            }
        )
        save_json(CACHE_PATH, cache)
        print(f"{i + 1}/{len(actors)} {actor['id']} {geo.get('precision') if geo else '?'}", flush=True)

    save_json(CACHE_PATH, cache)
    OUT.write_text(json.dumps(actors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with REVIEW_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["name", "website", "address", "lat", "lng", "precision", "source_url", "flags"],
        )
        w.writeheader()
        w.writerows(review_rows)

    from collections import Counter

    prec = Counter(r["precision"] for r in review_rows)
    nf = sum(1 for r in review_rows if "not_found" in r["flags"] or r["precision"] == "country")
    mm = [r["name"] for r in review_rows if "country_mismatch" in r["flags"]]
    print("precision counts:", dict(prec))
    print("not_found/country-only:", nf)
    print("country_mismatch:", len(mm))
    for n in mm[:20]:
        print("  -", n)


if __name__ == "__main__":
    main()
