#!/usr/bin/env python3
"""Merge Jennifer González Mapa de Actores Perú 2026 into Nexus ecosystem JSON."""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "static" / "ecosystem" / "data"
OPS = ROOT / "ops" / "ecosystem"
XLSX = Path("/home/debian/.cursor/projects/home-debian/uploads/mapeo-peru-db_5cd5.xlsx")
DECK = Path("/home/debian/.cursor/projects/home-debian/uploads/deck_8fe0.txt")
LIVE_URL = "https://nexus.cleantechhub.net/ecosystem/data/actors.json"
REL_LIVE_URL = "https://nexus.cleantechhub.net/ecosystem/data/relations.json"
SOURCE = "Mapa de Actores Perú 2026"
GEOCODE_CACHE = OPS / "nominatim-cache-peru.json"
UA = "CleantechHUB-Nexus-Ecosystem/1.0 (ops@cleantechhub.net)"

CHALLENGE_TAGS = {"BOS", "AGU", "AZU", "CIR", "AGR", "ENE", "CIU", "FIN", "ARG"}

CITY_COORDS = {
    "lima": (-12.0464, -77.0428),
    "arequipa": (-16.409, -71.5375),
    "trujillo": (-8.1116, -79.0288),
    "cusco": (-13.5319, -71.9675),
    "piura": (-5.1945, -80.6328),
    "chiclayo": (-6.7714, -79.8409),
    "iquitos": (-3.7491, -73.2538),
    "huánuco": (-9.9306, -76.2422),
    "cajamarca": (-7.1617, -78.5128),
    "moquegua": (-17.1934, -70.9357),
    "tacna": (-18.0066, -70.2463),
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
DRIVE_RE = re.compile(r"drive\.google\.com|docs\.google\.com", re.I)
CANVA_RE = re.compile(r"canva\.(com|link)", re.I)
SITIO_RE = re.compile(
    r"Sitio\s*(?:Web)?:?\s*(https?://[^\s]+|gob\.pe/[^\s]+|[a-z0-9.-]+\.[a-z]{2,}[^\s]*)",
    re.I,
)
CHALLENGE_LINE_RE = re.compile(r"\b(BOS|AGU|AZU|CIR|AGR|ENE|CIU|FIN|ARG)\b")

CATEGORY_MAP = {
    "gobierno": "government",
    "gobierno ": "government",
    "academia y centros de investigación": "academia",
    "academia": "academia",
    "incubadora / aceleradora": "accelerator",
    "incubadora": "accelerator",
    "aceleradora": "accelerator",
    "fondo / inversión": "funder",
    "fondo": "funder",
    "inversión": "funder",
    "ong / sociedad civil": "ngo_foundation",
    "ong": "ngo_foundation",
    "fundación": "ngo_foundation",
    "empresa": "corporate",
    "internacional": "international",
    "cooperación internacional": "international",
    "cámara": "chamber",
    "gremio": "chamber",
    "finanzas": "finance",
    "startup": "startup",
    "medios": "media",
    "medio": "media",
}

SECTOR_BY_CATEGORY = {
    "government": "gov",
    "policy": "gov",
    "academia": "civil",
    "ngo_foundation": "civil",
    "accelerator": "private",
    "funder": "private",
    "corporate": "private",
    "finance": "private",
    "chamber": "private",
    "startup": "private",
    "media": "civil",
    "international": "intl",
}

WEBSITE_OVERRIDES = {
    "proinnóvate": "https://www.gob.pe/proinnovate",
    "proinnovate": "https://www.gob.pe/proinnovate",
    "startup perú": "https://startup.proinnovate.gob.pe",
    "cofide": "https://www.cofide.com.pe",
    "minam": "https://www.gob.pe/minam",
    "ministerio de ambiente": "https://www.gob.pe/minam",
    "giz": "https://www.giz.de/en/worldwide/349.html",
    "bid lab": "https://www.idblab.org",
    "bid": "https://www.iadb.org",
    "rootcapital": "https://rootcapital.org",
    "root capital": "https://rootcapital.org",
    "swissep": "https://www.swisscontact.org/es/donde-trabajamos/peru",
    "profenanpe": "https://profonanpe.org.pe",
    "kunan": "https://kunan.com.pe",
    "municipalidad de miraflores": "https://www.miraflores.gob.pe",
    "asep": "https://www.asep.gob.pe",
    "revista ganamás": "https://ganamas.com.pe",
    "haskoningshv": "https://www.haskoning.com",
    "fenix consulting": "https://www.fenixconsulting.com.pe",
    "cide pucp": "https://cide.pucp.edu.pe",
    "cide pucp (universidad católica)": "https://cide.pucp.edu.pe",
}

NAME_ALIASES = {
    "proinnóvate": "ProInnóvate – StartUp Perú",
    "proinnovate": "ProInnóvate – StartUp Perú",
    "profenanpe": "Profonanpe",
    "minam": "MINAM – Ministerio del Ambiente",
    "midagri": "MIDAGRI Ministerio de Desarrollo Agrario y Riego",
    "produce": "PRODUCE – Ministerio de la Producción",
    "minem": "MINEM Ministerio de Energía y Minas",
    "mef": "MEF Ministerio de Economía y Finanzas",
    "1551 incubadora de empresas innovadoras de la unmsm": "1551 Incubadora de Empresas Innovadoras de la UNMSM",
    "emprende up climatech rein hub perú": "Emprende UP – ClimaTech (REIN Hub Perú)",
    "cleantechhub": "CleantechHUB",
    "pvblic foundation": "PVBLIC Foundation",
}

POLICIES = [
    {
        "name": "NDC 3.0 — Nuestro Desafío Climático",
        "slug": "ndc-3-nuestro-desafio-climatico",
        "website": "https://www.gob.pe/minam",
        "challenges": ["BOS", "AGU", "AZU", "CIR", "AGR", "ENE", "CIU", "FIN"],
        "notes": "Contribución Determinada a Nivel Nacional (NDC) 3.0 presentada en 2025; tope absoluto 179 MtCO₂e al 2035.",
        "ministries": ["pe-minam-ministerio-del-ambiente", "pe-mef-ministerio-de-economia-y-finanzas"],
    },
    {
        "name": "Ley Marco sobre Cambio Climático (Ley 30754)",
        "slug": "ley-marco-cambio-climatico-30754",
        "website": "https://www.gob.pe/minam",
        "challenges": ["BOS", "AGU", "AGR", "ENE", "FIN"],
        "notes": "Base legal de la NDC, gobernanza climática y Plataforma Huella de Carbono Perú.",
        "ministries": ["pe-minam-ministerio-del-ambiente"],
    },
    {
        "name": "Hoja de Ruta de Finanzas Verdes",
        "slug": "hoja-ruta-finanzas-verdes",
        "website": "https://www.gob.pe/minam",
        "challenges": ["FIN"],
        "notes": "Movilización estimada ~US$ 5.800 M al 2030 (MINAM).",
        "ministries": ["pe-minam-ministerio-del-ambiente", "pe-mef-ministerio-de-economia-y-finanzas"],
    },
    {
        "name": "StartUp Perú (ProInnóvate)",
        "slug": "startup-peru-proinnovate",
        "website": "https://startup.proinnovate.gob.pe",
        "challenges": ["FIN", "AGR", "ENE", "CIR"],
        "notes": "Capital semilla e innovación emprendedora; convocatorias climáticas vía PRODUCE.",
        "ministries": ["pe-proinnovate-startup-peru", "pe-produce-ministerio-de-la-produccion"],
    },
    {
        "name": "Programa para Bionegocios (MINAM)",
        "slug": "programa-bionegocios-minam",
        "website": "https://www.gob.pe/minam",
        "challenges": ["BOS"],
        "notes": "Crédito para bionegocios amazónicos.",
        "ministries": ["pe-minam-ministerio-del-ambiente"],
    },
    {
        "name": "Programa Bosques (MINAM)",
        "slug": "programa-bosques-minam",
        "website": "https://www.gob.pe/bosques",
        "challenges": ["BOS"],
        "notes": "Conservación de bosques y planes de negocio comunitarios.",
        "ministries": ["pe-minam-ministerio-del-ambiente"],
    },
    {
        "name": "Ley de Gestión Integral de Residuos Sólidos (D.S. 1278)",
        "slug": "ley-gestion-residuos-solidos",
        "website": "https://www.gob.pe/minam",
        "challenges": ["CIR"],
        "notes": "Marco de economía circular y responsabilidad extendida del productor.",
        "ministries": ["pe-minam-ministerio-del-ambiente"],
    },
    {
        "name": "Taxonomía verde / bonos verdes (SBS-SMV)",
        "slug": "taxonomia-verde-bonos",
        "website": "https://www.sbs.gob.pe",
        "challenges": ["FIN"],
        "notes": "Reglas de riesgo climático y emisión de bonos verdes (SBS y SMV).",
        "ministries": ["pe-sbs-superintendencia-de-banca-seguros-y-afp"],
    },
]


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category != "Mn")


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", strip_accents((s or "").lower()))


def slugify(name: str, max_len: int = 48) -> str:
    s = strip_accents(name.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:max_len].strip("-")


def host_key(url: str | None) -> str | None:
    if not url:
        return None
    u = str(url).strip()
    if "linkedin.com" in u.lower():
        return None
    if not u.startswith("http"):
        u = "https://" + u
    try:
        from urllib.parse import urlparse

        h = urlparse(u).netloc.lower().replace("www.", "")
        return h or None
    except Exception:
        return None


def normalize_website(url: str | None) -> str | None:
    if not url:
        return None
    u = str(url).strip().rstrip(".,;")
    if CANVA_RE.search(u) or DRIVE_RE.search(u):
        return None
    if EMAIL_RE.search(u):
        return None
    if "linkedin.com" in u.lower():
        return None
    if not u.startswith("http"):
        u = "https://" + u
    return u


def scrub_text(s: str | None) -> str | None:
    if not s:
        return None
    t = str(s)
    t = EMAIL_RE.sub("", t)
    t = DRIVE_RE.sub("", t)
    t = CANVA_RE.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t or None


def map_category(raw: str | None) -> str:
    if not raw:
        return "corporate"
    key = strip_accents(str(raw).lower()).strip()
    for k, v in CATEGORY_MAP.items():
        if k in key or key in k:
            return v
    if "universidad" in key or "incub" in key:
        return "accelerator" if "incub" in key else "academia"
    if "ministerio" in key or "gobierno" in key:
        return "government"
    return "corporate"


def fetch_json(url: str) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def save_geocode_cache(cache: dict) -> None:
    GEOCODE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    GEOCODE_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def nominatim(query: str, cache: dict) -> dict | None:
    q = query.strip()
    if not q:
        return None
    if q in cache:
        return cache[q]
    params = urllib.parse.urlencode({"q": q, "format": "json", "limit": 1, "countrycodes": "pe"})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError):
        data = []
    time.sleep(1.15)
    if not data:
        cache[q] = None
        return None
    hit = data[0]
    geo = {
        "lat": round(float(hit["lat"]), 5),
        "lng": round(float(hit["lon"]), 5),
        "precision": "address" if "," in q and len(q) > 20 else "city",
        "source": "nominatim",
    }
    cache[q] = geo
    return geo


def city_geo(city: str | None) -> dict | None:
    if not city:
        return None
    key = strip_accents(str(city).lower()).strip()
    for name, coords in CITY_COORDS.items():
        if name in key:
            return {
                "lat": coords[0],
                "lng": coords[1],
                "precision": "city",
                "source": "city-centroid",
            }
    return {
        "lat": CITY_COORDS["lima"][0],
        "lng": CITY_COORDS["lima"][1],
        "precision": "city",
        "source": "city-centroid",
    }


def resolve_website(name: str, website: str | None) -> str | None:
    w = normalize_website(website)
    if w:
        return w
    nn = norm_name(name)
    for k, v in WEBSITE_OVERRIDES.items():
        if k in nn or nn in norm_name(k):
            return v
    return None


def canonical_name(name: str) -> str:
    nn = norm_name(name)
    for k, v in NAME_ALIASES.items():
        if norm_name(k) == nn or norm_name(k) in nn:
            return v
    return re.sub(r"\s+", " ", name.strip())


def make_id(name: str, existing_ids: set[str]) -> str:
    base = "pe-" + slugify(name)
    if base not in existing_ids:
        return base
    i = 2
    while f"{base}-{i}" in existing_ids:
        i += 1
    return f"{base}-{i}"


def build_indexes(actors: list[dict]) -> dict:
    by_name: dict[str, dict] = {}
    by_host: dict[str, dict] = {}
    by_id: dict[str, dict] = {}
    for a in actors:
        by_id[a["id"]] = a
        nn = norm_name(a.get("name", ""))
        if nn:
            by_name[nn] = a
        hk = host_key(a.get("website"))
        if hk:
            by_host[hk] = a
    return {"name": by_name, "host": by_host, "id": by_id}


def find_actor(name: str, website: str | None, idx: dict) -> dict | None:
    cn = canonical_name(name)
    for candidate in {name, cn}:
        nn = norm_name(candidate)
        if nn in idx["name"]:
            return idx["name"][nn]
        for kn, act in idx["name"].items():
            if len(nn) >= 8 and (nn in kn or kn in nn):
                return act
    hk = host_key(resolve_website(name, website))
    if hk and hk in idx["host"]:
        return idx["host"][hk]
    return None


def parse_deck_orgs(text: str) -> list[dict]:
    orgs: list[dict] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("Sitio"):
            i += 1
            continue
        block = [line]
        j = i + 1
        while j < len(lines) and j < i + 8:
            nxt = lines[j].strip()
            if re.match(r"^(SECTOR|Desafío|Nivel de|Recomendación|Estado)", nxt):
                break
            if nxt.startswith("Sitio"):
                block.append(nxt)
                j += 1
                while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("Sitio"):
                    if "http" in lines[j] or "gob.pe" in lines[j]:
                        block.append(lines[j].strip())
                    j += 1
                break
            if nxt and not nxt.startswith(""):
                block.append(nxt)
            j += 1
        joined = "\n".join(block)
        sites = SITIO_RE.findall(joined)
        urls = []
        for s in sites:
            w = normalize_website(s)
            if w:
                urls.append(w)
        for m in re.finditer(r"https?://[^\s]+|gob\.pe/[^\s,]+", joined):
            w = normalize_website(m.group(0))
            if w and w not in urls:
                urls.append(w)
        if urls:
            name_line = block[0]
            name = re.split(r"\.\s*$", name_line)[0].strip()
            name = re.sub(r"^\d+\.\s*", "", name)
            if len(name) < 3 or name.lower().startswith("sitio"):
                i += 1
                continue
            challenges = sorted(set(CHALLENGE_LINE_RE.findall(joined)) & CHALLENGE_TAGS)
            desc = scrub_text(" ".join(block[1:3])) if len(block) > 1 else None
            orgs.append({"name": name, "website": urls[0], "websites": urls, "challenges": challenges})
        i += 1
    return orgs


def parse_excel(path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    org_rows: list[dict] = []
    host_relations: list[dict] = []
    people: list[dict] = []

    ws = wb["Base de datos REIN Perú"]
    headers = None
    for row in ws.iter_rows(values_only=True):
        if row and row[0] == "Nombre Organización":
            headers = [str(x).strip() if x else "" for x in row]
            continue
        if not headers or not row or not row[0]:
            continue
        rec = dict(zip(headers, row))
        name = rec.get("Nombre Organización")
        if not name:
            continue
        web = rec.get("Website")
        linkedin = None
        if web and "linkedin.com" in str(web).lower():
            linkedin = normalize_website(web)
            web = None
        org_rows.append(
            {
                "name": str(name).strip(),
                "category": map_category(rec.get("Categoría")),
                "city": rec.get("Ciudad") or "Lima",
                "website": resolve_website(str(name), web),
                "challenges": [],
                "notes": scrub_text(rec.get("Rol / Cargo")),
                "linkedin_org": linkedin,
            }
        )
        contact = rec.get("Contacto")
        if contact and contact != "-" and linkedin:
            people.append({"name": str(contact).strip(), "linkedin": linkedin, "org": str(name).strip()})

    ws = wb["Centros de emprendimiento"]
    headers = None
    for row in ws.iter_rows(values_only=True):
        if row and row[0] == "Nombre Organización":
            headers = [str(x).strip() if x else "" for x in row]
            continue
        if not headers or not row or not row[0]:
            continue
        rec = dict(zip(headers, row))
        inc_name = str(rec.get("Nombre Organización", "")).strip()
        uni = rec.get("Universidad")
        if inc_name and uni:
            host_relations.append({"university": str(uni).strip(), "incubator": inc_name})
        org_rows.append(
            {
                "name": inc_name,
                "category": map_category(rec.get("Categoría") or "incubadora"),
                "city": rec.get("Ciudad") or "Lima",
                "website": resolve_website(inc_name, rec.get("Website")),
                "challenges": [],
                "notes": scrub_text(rec.get("Rol / Cargo")),
            }
        )

    ws = wb["Adicionales"]
    for row in ws.iter_rows(values_only=True):
        if not row or not row[3]:
            continue
        if row[0] == "Cooperación internacional" or row[3]:
            name = row[3]
            if str(name).strip() in ("Earth Innovation Institute",):
                org_rows.append(
                    {
                        "name": str(name).strip(),
                        "category": "international",
                        "city": "Lima",
                        "website": resolve_website(str(name), "https://earthinnovation.org"),
                        "challenges": [],
                        "notes": scrub_text(row[2]),
                    }
                )
            elif str(name).strip() in ("BID", "CAF"):
                sites = {"BID": "https://www.iadb.org", "CAF": "https://www.caf.com"}
                org_rows.append(
                    {
                        "name": str(name).strip(),
                        "category": "international",
                        "city": "Lima",
                        "website": sites.get(str(name).strip()),
                        "challenges": [],
                        "notes": scrub_text(row[2]),
                    }
                )

    return org_rows, host_relations, people


def merge_actor_fields(existing: dict, incoming: dict) -> dict:
    out = dict(existing)
    if incoming.get("city") and not out.get("city"):
        out["city"] = incoming["city"]
    if incoming.get("address") and not out.get("address"):
        out["address"] = incoming["address"]
    if incoming.get("website") and not out.get("website"):
        out["website"] = incoming["website"]
    inc_ch = set(existing.get("challenges") or []) | set(incoming.get("challenges") or [])
    if inc_ch:
        out["challenges"] = sorted(inc_ch)
    if incoming.get("sector"):
        out["sector"] = incoming["sector"]
    elif out.get("category"):
        out["sector"] = SECTOR_BY_CATEGORY.get(out["category"], "private")
    src = out.get("source")
    if SOURCE not in (src or ""):
        out["source"] = SOURCE if not src else f"{src}; {SOURCE}"
    if incoming.get("notes"):
        new = scrub_text(incoming["notes"])
        if new and len(new) <= 240:
            old = scrub_text(out.get("notes") or "") or ""
            if new and new not in old:
                out["notes"] = scrub_text(f"{old} {new}".strip()) if old else new
    if existing.get("geo"):
        out["geo"] = existing["geo"]
    return out


def actor_public(a: dict) -> dict:
    clean = {}
    for k, v in a.items():
        if k in ("email", "phone", "drive_url", "website_check", "website_ok", "source_design_id"):
            continue
        if isinstance(v, str):
            v = scrub_text(v)
        clean[k] = v
    if clean.get("type") != "person":
        clean.pop("linkedin", None)
    return clean


def main() -> int:
    base_path = OPS / "live-clean-base.json"
    if base_path.exists():
        print(f"Loading base actors from {base_path}")
        live_actors = json.loads(base_path.read_text(encoding="utf-8"))
        rel_base = OPS / "relations-clean-base.json"
        live_relations = json.loads(rel_base.read_text(encoding="utf-8")) if rel_base.exists() else fetch_json(REL_LIVE_URL)
    else:
        print("Fetching live actors…")
        live_actors = fetch_json(LIVE_URL)
        live_relations = fetch_json(REL_LIVE_URL)
    print("Re-fetching live for geo preservation…")
    try:
        live_now = fetch_json(LIVE_URL)
        geo_by_id = {a["id"]: a.get("geo") for a in live_now if a.get("geo")}
        for a in live_actors:
            if a["id"] in geo_by_id:
                a["geo"] = geo_by_id[a["id"]]
    except Exception as exc:
        print(f"WARN: could not refresh live geo: {exc}")
    print(f"Live: {len(live_actors)} actors, {len(live_relations)} relations")

    deck_text = DECK.read_text(encoding="utf-8", errors="replace")
    deck_orgs = parse_deck_orgs(deck_text)
    excel_orgs, host_rels, people = parse_excel(XLSX)

    incoming: dict[str, dict] = {}
    for src in excel_orgs + deck_orgs:
        name = canonical_name(src["name"])
        web = resolve_website(name, src.get("website"))
        if not web:
            continue
        key = norm_name(name)
        rec = incoming.get(key) or {
            "name": name,
            "type": "org",
            "category": src.get("category") or map_category(None),
            "country": "Peru",
            "city": src.get("city") or "Lima",
            "website": web,
            "challenges": src.get("challenges") or [],
            "notes": src.get("notes"),
            "source": SOURCE,
            "sector": SECTOR_BY_CATEGORY.get(src.get("category") or "corporate", "private"),
        }
        rec["challenges"] = sorted(set(rec.get("challenges") or []) | set(src.get("challenges") or []))
        if src.get("notes"):
            rec["notes"] = scrub_text(f"{rec.get('notes') or ''} {src['notes']}".strip())
        incoming[key] = rec

    actors = [dict(a) for a in live_actors]
    idx = build_indexes(actors)
    existing_ids = {a["id"] for a in actors}
    stats = {"new": 0, "merged": 0, "skipped_no_web": 0, "people": 0}
    merged_ids: set[str] = set()

    geocode_cache: dict = {}
    if GEOCODE_CACHE.exists():
        geocode_cache = json.loads(GEOCODE_CACHE.read_text(encoding="utf-8"))

    merged_names: list[str] = []

    for rec in incoming.values():
        match = find_actor(rec["name"], rec["website"], idx)
        if match:
            updated = merge_actor_fields(match, rec)
            match.clear()
            match.update(updated)
            if match["id"] not in merged_ids:
                merged_ids.add(match["id"])
                stats["merged"] += 1
                merged_names.append(rec["name"])
        else:
            aid = make_id(rec["name"], existing_ids)
            existing_ids.add(aid)
            rec["id"] = aid
            query = f"{rec.get('address') or rec['name']}, {rec.get('city') or 'Lima'}, Peru"
            geo = nominatim(query, geocode_cache) or city_geo(rec.get("city"))
            if geo:
                rec["geo"] = geo
            actors.append(rec)
            idx = build_indexes(actors)
            stats["new"] += 1

    save_geocode_cache(geocode_cache)

    for pol in POLICIES:
        pid = f"pe-policy-{pol['slug']}"
        if pid in idx["id"]:
            continue
        actor = {
            "id": pid,
            "name": pol["name"],
            "type": "policy",
            "category": "policy",
            "country": "Peru",
            "city": "Lima",
            "website": pol["website"],
            "challenges": pol["challenges"],
            "notes": scrub_text(pol["notes"]),
            "source": SOURCE,
            "sector": "gov",
        }
        geo = nominatim(f"MINAM, Lima, Peru", geocode_cache) or city_geo("Lima")
        if geo:
            actor["geo"] = geo
        actors.append(actor)
        stats["new"] += 1
        idx = build_indexes(actors)

    save_geocode_cache(geocode_cache)

    relations = [dict(r) for r in live_relations]
    rel_keys = {(r["source"], r["target"], r.get("type")) for r in relations}
    new_rel = 0

    for hr in host_rels:
        u = find_actor(hr["university"], None, idx)
        inc = find_actor(hr["incubator"], None, idx)
        if u and inc:
            key = (u["id"], inc["id"], "hosts")
            if key not in rel_keys:
                relations.append(
                    {
                        "source": u["id"],
                        "target": inc["id"],
                        "type": "hosts",
                        "verified": True,
                        "source_note": SOURCE,
                    }
                )
                rel_keys.add(key)
                new_rel += 1

    for pol in POLICIES:
        pid = f"pe-policy-{pol['slug']}"
        for mid in pol["ministries"]:
            if mid in idx["id"] or find_actor(mid.replace("-", " "), None, idx):
                target = mid if mid in idx["id"] else find_actor(mid.replace("-", " "), None, idx)["id"]
                key = (pid, target, "administered_by")
                if key not in rel_keys:
                    relations.append(
                        {
                            "source": pid,
                            "target": target,
                            "type": "administered_by",
                            "verified": True,
                            "source_note": f"{SOURCE} (marco normativo y programas)",
                        }
                    )
                    rel_keys.add(key)
                    new_rel += 1

    rein_id = "pe-emprende-up-climatech-rein-hub-peru"
    cth = find_actor("CleantechHUB", "https://cleantechhub.net", idx)
    pvblic = find_actor("PVBLIC Foundation", None, idx)
    for partner in (cth, pvblic):
        if partner and rein_id in idx["id"]:
            key = (rein_id, partner["id"], "partner")
            if key not in rel_keys:
                relations.append(
                    {
                        "source": rein_id,
                        "target": partner["id"],
                        "type": "partner",
                        "verified": True,
                        "source_note": f"{SOURCE} (REIN Hub Perú / Emprende UP ClimaTech)",
                    }
                )
                rel_keys.add(key)
                new_rel += 1

    seen_people = set()
    for p in people:
        if not p.get("linkedin"):
            continue
        nn = norm_name(p["name"])
        if nn in seen_people:
            continue
        seen_people.add(nn)
        if find_actor(p["name"], p["linkedin"], idx):
            continue
        pid = make_id(p["name"], existing_ids)
        existing_ids.add(pid)
        person = {
            "id": pid,
            "name": p["name"],
            "type": "person",
            "category": "media",
            "country": "Peru",
            "linkedin": p["linkedin"],
            "website": p["linkedin"],
            "source": SOURCE,
            "notes": scrub_text(f"Contacto público — {p.get('org', '')}"),
        }
        actors.append(person)
        stats["people"] += 1
        idx = build_indexes(actors)

    actors_out = [actor_public(a) for a in actors]
    relations_out = []
    for r in relations:
        rc = dict(r)
        for k in list(rc.keys()):
            if isinstance(rc[k], str):
                rc[k] = scrub_text(rc[k])
        relations_out.append(rc)

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "actors.json").write_text(json.dumps(actors_out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (DATA / "relations.json").write_text(json.dumps(relations_out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    report = {
        "new_actors": stats["new"],
        "merged": stats["merged"],
        "new_relations": new_rel,
        "people_added": stats["people"],
        "merged_names_sample": merged_names[:30],
        "total_actors": len(actors_out),
        "total_relations": len(relations_out),
        "peru_actors": sum(1 for a in actors_out if a.get("country") == "Peru"),
        "policies": sum(1 for a in actors_out if a.get("type") == "policy"),
    }
    (OPS / "merge-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
