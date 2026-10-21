#!/usr/bin/env python3
"""Scrape SINIA normatividad (JSON:API) into Nexus policy records."""
from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ACTORS_PATH = ROOT / "docs/ecosystem/prototype/data/actors.json"
POLICIES_PATH = ROOT / "data/policies.json"
RELS_PATH = ROOT / "policy_relations.json"
BUILDER = Path(__file__).parent / "build_policy_dataset.py"

BASE = "https://sinia.minam.gob.pe"
JSONAPI_LIST = (
    BASE
    + "/jsonapi/node/normatividad"
    + "?filter%5Bfield_estado_de_la_norma%5D=Vigente"
    + "&include=field_tipo_de_norma,field_source_of_information,field_descriptores_tematicos,field_archivo"
    + "&page%5Blimit%5D=25"
)
HEADERS = {"Accept": "application/vnd.api+json", "User-Agent": "NexusEcosystemResearch/1.0"}

# Existing non-SINIA PE policy ids to preserve if not duplicated
PRESERVE_PE_IDS = {
    "policy:pe-ndc-2020",
    "policy:pe-ndc-cpd",
    "policy:pe-programa-bionegocios",
    "policy:pe-programa-bosques",
    "policy:pe-startup-peru-clima",
    "policy:pe-clima-law-cpd",
    "policy:pe-geography-cclw",
}

# Actor id -> phrases that must appear in issuer text (verified issues_policy)
ACTOR_ISSUER_PHRASES: dict[str, list[str]] = {
    "pe-minam-ministerio-del-ambiente": [
        "ministerio del ambiente",
        "minam",
        "ministerio del ambiente y energía",
    ],
    "pe-minem-ministerio-de-energia-y-minas": ["ministerio de energía y minas", "minem"],
    "pe-midagri-ministerio-de-desarrollo-agrario-y-riego": ["midagri", "desarrollo agrario"],
    "pe-produce-ministerio-de-la-produccion": ["ministerio de la producción", "produce"],
    "pe-serfor": ["serfor", "servicio nacional forestal"],
    "pe-ana-autoridad-nacional-del-agua": ["autoridad nacional del agua", " ana"],
    "pe-sernanp": ["sernanp", "servicio nacional de áreas naturales"],
    "pe-senamhi": ["senamhi", "servicio nacional de meteorología"],
    "pe-osinergmin": ["osinergmin", "organismo supervisor"],
    "pe-sunass": ["sunass", "superintendencia nacional de servicios"],
    "pe-imarpe": ["imarpe", "instituto del mar del perú"],
    "pe-inaigem": ["inaigem", "instituto nacional de investigación en glaciares"],
    "pe-mef-ministerio-de-economia-y-finanzas": ["ministerio de economía y finanzas", "mef"],
    "pe-proinnovate-startup-peru": ["proinnovate", "pro innova", "startup perú"],
    "pe-programa-para-bionegocios-minam": ["programa para bionegocios", "bionegocios"],
    "pe-programa-bosques-minam": ["programa nacional de conservación de bosques", "programa bosques"],
    "pe-gobierno-regional-de-amazonas": ["gobierno regional de amazonas", "amazonas"],
    "pe-gobierno-regional-de-loreto": ["gobierno regional de loreto", "loreto"],
    "pe-gobierno-regional-de-madre-de-dios": ["madre de dios"],
    "pe-gobierno-regional-de-san-martin": ["san martín", "san martin"],
    "pe-gobierno-regional-de-ucayali": ["ucayali"],
    "pe-gobierno-regional-y-municipalidad-de-cusco": ["cusco"],
    "pe-concytec-prociencia": ["concytec", "prociencia"],
    "pe-agroideas": ["agroideas"],
    "pe-agrobanco": ["agrobanco"],
    "pe-cofide-fcei": ["cofide"],
    "pe-proinversion": ["proinversión", "proinversion"],
    "pe-promperu": ["promperú", "promperu"],
    "pe-sbs-superintendencia-de-banca-seguros-y-afp": ["sbs", "superintendencia de banca"],
    "pe-smv-superintendencia-del-mercado-de-valores": ["smv", "superintendencia del mercado de valores"],
    "pe-sanipes": ["sanipes"],
    "pe-apci-agencia-peruana-de-cooperacion-internacional": ["apci", "cooperación internacional"],
}

CHALLENGE_SECTOR_MAP = {
    "challenge:PE-1-bosques": {"bosques", "forestal", "biodiversidad", "amazon", "deforest"},
    "challenge:PE-2-agua": {"agua", "hídric", "hidric", "cuenca", "glaciar", "riego"},
}

DATOS_ABIERTOS_EVIDENCE = [
    {
        "id": "evidence:pe-datosabiertos-ghg-inventory",
        "name": "Inventario Nacional de GEI (datosabiertos.gob.pe)",
        "source_url": "https://www.datosabiertos.gob.pe/dataset/inventario-nacional-de-emisiones-de-gases-de-efecto-invernadero",
        "sectors": ["energía", "mitigación"],
        "challenges": ["challenge:PE-1-bosques"],
    },
    {
        "id": "evidence:pe-datosabiertos-waste",
        "name": "Composición de residuos sólidos domiciliarios",
        "source_url": "https://sinia.minam.gob.pe/portal/datos-abiertos/",
        "sectors": ["economía circular"],
        "challenges": [],
    },
    {
        "id": "evidence:pe-datosabiertos-wildfires",
        "name": "Puntos de calor / incendios (NASA WMS via SINIA)",
        "source_url": "https://sinia.minam.gob.pe/portal/datos-abiertos/",
        "sectors": ["bosques"],
        "challenges": ["challenge:PE-1-bosques"],
    },
    {
        "id": "evidence:pe-datosabiertos-degraded-areas",
        "name": "Pérdida de bosques / áreas degradadas (SINIA datos abiertos)",
        "source_url": "https://sinia.minam.gob.pe/portal/datos-abiertos/",
        "sectors": ["bosques"],
        "challenges": ["challenge:PE-1-bosques"],
    },
]


def fetch_json(url: str, retries: int = 4) -> dict:
    for i in range(retries):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            time.sleep(2 ** i)
    raise RuntimeError(f"Failed to fetch {url}")


def slugify(text: str, max_len: int = 48) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:max_len] or "norma"


def instrument_from_tipo(tipo: str) -> str:
    t = (tipo or "").lower()
    if "ley" in t:
        return "law"
    if "decreto" in t or "ds" in t or "d.s" in t:
        return "regulation"
    if "resoluc" in t:
        return "regulation"
    if "plan" in t or "política" in t or "politica" in t or "estrateg" in t:
        return "strategy"
    if "ordenanza" in t:
        return "regulation"
    return "regulation"


def sectors_from_descriptors(names: list[str]) -> list[str]:
    blob = " ".join(names).lower()
    out = []
    mapping = [
        ("agua", ["agua", "hídric", "hidric", "cuenca", "mar ", "glaciar"]),
        ("bosques", ["bosque", "forestal", "deforest", "amazon"]),
        ("energía", ["energ", "eléctr", "electr", "combust", "petrol", "gas "]),
        ("adaptación", ["adapt", "cambio clim", "vulnerab"]),
        ("economía circular", ["residuo", "recicl", "circular"]),
        ("agricultura", ["agr", "cultivo", "ganader", "riego"]),
    ]
    for tag, keys in mapping:
        if any(k in blob for k in keys):
            out.append(tag)
    return out or ["adaptación"]


def norm_number_key(num: str | None) -> str | None:
    if not num:
        return None
    return re.sub(r"\D", "", str(num)) or None


def dedupe_key(policy: dict) -> tuple:
    n = norm_number_key(policy.get("sinia_number") or policy.get("name", ""))
    if n:
        return ("num", n)
    return ("url", policy.get("source_url", ""))


def fetch_all_vigente() -> list[dict]:
    url = JSONAPI_LIST
    rows = []
    page = 0
    while url:
        page += 1
        payload = fetch_json(url)
        included = {
            (x["type"], x["id"]): x for x in payload.get("included") or []
        }
        for node in payload.get("data") or []:
            attrs = node["attributes"]
            if attrs.get("field_estado_de_la_norma") != "Vigente":
                continue
            if not attrs.get("status"):
                continue
            rels = node.get("relationships") or {}
            tipo = resolve_taxonomy(rels, "field_tipo_de_norma", included)
            fuentes = resolve_taxonomy_list(rels, "field_source_of_information", included)
            desc = resolve_taxonomy_list(rels, "field_descriptores_tematicos", included)
            pdfs = resolve_files(rels, "field_archivo", included)
            alias = (attrs.get("path") or {}).get("alias") or ""
            if not alias:
                nid = attrs.get("drupal_internal__nid")
                alias = f"/node/{nid}"
            source_url = BASE + alias if alias.startswith("/") else alias
            rows.append(
                {
                    "uuid": node["id"],
                    "nid": attrs.get("drupal_internal__nid"),
                    "title": attrs.get("title") or attrs.get("field_title") or "",
                    "number": attrs.get("field_numero_de_la_norma"),
                    "tipo": tipo,
                    "date": attrs.get("field_fecha_creacion"),
                    "issuers": fuentes,
                    "descriptors": desc,
                    "pdf_urls": pdfs,
                    "source_url": source_url,
                    "body": (attrs.get("body") or {}).get("value") or "",
                }
            )
        url = (payload.get("links") or {}).get("next", {}).get("href")
        if url and url.startswith("http://"):
            url = "https://" + url[len("http://") :]
        if page % 10 == 0:
            print(f"  … page {page}, vigente rows {len(rows)}", flush=True)
        time.sleep(0.08)
    return rows


def resolve_taxonomy(rels, field, included):
    data = (rels.get(field) or {}).get("data")
    if not data:
        return ""
    if isinstance(data, list):
        data = data[0] if data else None
    if not data:
        return ""
    ent = included.get((data["type"], data["id"]))
    return (ent or {}).get("attributes", {}).get("name") or ""


def resolve_taxonomy_list(rels, field, included):
    data = (rels.get(field) or {}).get("data") or []
    if isinstance(data, dict):
        data = [data]
    names = []
    for ref in data:
        ent = included.get((ref["type"], ref["id"]))
        if ent:
            n = ent.get("attributes", {}).get("name")
            if n:
                names.append(n)
    return names


def resolve_files(rels, field, included):
    data = (rels.get(field) or {}).get("data") or []
    if isinstance(data, dict):
        data = [data]
    urls = []
    for ref in data:
        ent = included.get((ref["type"], ref["id"]))
        if not ent:
            continue
        uri = ent.get("attributes", {}).get("uri") or {}
        url = uri.get("url") or ""
        if url.startswith("public://"):
            url = BASE + "/sites/default/files/" + urllib.parse.quote(url[len("public://") :])
        elif url and not url.startswith("http"):
            url = BASE + url
        if url:
            urls.append(url)
    return urls


def sinia_to_policy(row: dict) -> dict:
    year = None
    if row.get("date"):
        try:
            year = int(str(row["date"])[:4])
        except ValueError:
            year = None
    name = row["title"].strip()
    if row.get("number") and str(row["number"]) not in name:
        name = f"{row.get('tipo') or 'Norma'} N° {row['number']} — {name}"
    pid = f"policy:pe-sinia-{row['nid'] or slugify(name)}"
    return {
        "id": pid,
        "type": "Policy",
        "name": name[:240],
        "country": "Peru",
        "instrument": instrument_from_tipo(row.get("tipo") or ""),
        "year": year,
        "sectors": sectors_from_descriptors(row.get("descriptors") or []),
        "status": "in_force",
        "source_url": row["source_url"],
        "registry": "SINIA",
        "sinia_number": row.get("number"),
        "sinia_type": row.get("tipo"),
        "sinia_date": row.get("date"),
        "issuing_authority": row.get("issuers") or [],
        "descriptors": row.get("descriptors") or [],
        "pdf_url": (row.get("pdf_urls") or [None])[0],
        "pdf_urls": row.get("pdf_urls") or [],
    }


def match_actors(policy: dict, actors: list[dict]) -> list[tuple[str, str, str]]:
    """Return list of (actor_id, source_url, note) for verified issues_policy."""
    # Verified only when SINIA issuer taxonomy or norm page body names issuer/implementer.
    issuer_blob = " ".join(policy.get("issuing_authority") or []).lower()
    body_blob = (policy.get("body") or "").lower()
    name_blob = (policy.get("name") or "").lower()

    matches = []
    for actor in actors:
        if actor.get("country") != "Peru" or actor.get("category") != "government":
            continue
        aid = actor["id"]
        phrases = ACTOR_ISSUER_PHRASES.get(aid, [])
        aname = (actor.get("name") or "").lower()
        for field_name, blob in (
            ("issuing_authority", issuer_blob),
            ("norm_page", body_blob),
            ("title", name_blob),
        ):
            if not blob:
                continue
            if aname and len(aname) > 12 and aname in blob:
                matches.append(
                    (
                        aid,
                        policy["source_url"],
                        f"SINIA {field_name} nombra «{actor.get('name')}»",
                    )
                )
                break
            for ph in phrases:
                if ph in blob:
                    matches.append(
                        (aid, policy["source_url"], f"SINIA {field_name} match: {ph}")
                    )
                    break
            else:
                continue
            break
    return matches


def sector_matches_challenge(sectors, challenge_id):
    keys = CHALLENGE_SECTOR_MAP.get(challenge_id, set())
    blob = " ".join(sectors).lower()
    return any(k in blob for k in keys)


def main():
    actors = json.loads(ACTORS_PATH.read_text())
    pe_gov = [a for a in actors if a.get("country") == "Peru" and a.get("category") == "government"]

    existing = json.loads(POLICIES_PATH.read_text())
    non_pe = [p for p in existing if p.get("country") != "Peru"]
    old_pe = [p for p in existing if p.get("country") == "Peru"]

    print("Fetching SINIA normatividad (vigente)…", flush=True)
    sinia_rows = fetch_all_vigente()
    print(f"SINIA vigente rows: {len(sinia_rows)}", flush=True)

    sinia_policies = [sinia_to_policy(r) for r in sinia_rows]
    sinia_keys = {dedupe_key(p) for p in sinia_policies}

    kept_legacy = []
    for p in old_pe:
        if p.get("registry") == "SINIA":
            continue
        if p["id"] in PRESERVE_PE_IDS:
            kept_legacy.append(p)
            continue
        num = None
        m = re.search(r"(\d{4,6})", p.get("name", ""))
        if m:
            num = m.group(1)
        dup = bool(num and ("num", num) in sinia_keys)
        if dup and p.get("registry") != "SINIA":
            continue
        kept_legacy.append(p)

    policies = non_pe + kept_legacy + sinia_policies
    policies.sort(key=lambda p: (p["country"], p.get("year") or 0, p["id"]))

    # Relations: rebuild from builder for CO/SV + add SINIA PE issues_policy
    import importlib.util

    spec = importlib.util.spec_from_file_location("build_policy", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    rels = mod.build_relations([p for p in policies if p["country"] in mod.NEXUS_COUNTRIES])

    seen_ip = {(r["source"], r["target"]) for r in rels if r["type"] == "issues_policy"}
    body_by_nid = {r["nid"]: r.get("body", "") for r in sinia_rows if r.get("nid")}
    for p in sinia_policies:
        nid = p["id"].replace("policy:pe-sinia-", "")
        try:
            nid_int = int(nid)
        except ValueError:
            nid_int = None
        body = body_by_nid.get(nid_int, "") if nid_int else ""
        for aid, url, note in match_actors({**p, "body": body}, pe_gov):
            key = (aid, p["id"])
            if key in seen_ip:
                continue
            seen_ip.add(key)
            rels.append(
                {
                    "source": aid,
                    "target": p["id"],
                    "type": "issues_policy",
                    "verified": True,
                    "suggested": False,
                    "source_url": url,
                    "notes": note,
                }
            )

    # addresses_challenge for all PE policies
    seen_ac = {(r["source"], r["target"]) for r in rels if r["type"] == "addresses_challenge"}
    for p in policies:
        if p.get("country") != "Peru":
            continue
        for ch_id in CHALLENGE_SECTOR_MAP:
            if not sector_matches_challenge(p.get("sectors") or [], ch_id):
                continue
            key = (p["id"], ch_id)
            if key in seen_ac:
                continue
            seen_ac.add(key)
            rels.append(
                {
                    "source": p["id"],
                    "target": ch_id,
                    "type": "addresses_challenge",
                    "verified": False,
                    "suggested": True,
                    "source_url": p["source_url"],
                    "notes": f"Inferred from sectors {p.get('sectors')}",
                }
            )

    # Optional datos abiertos evidence -> addresses_challenge
    for ev in DATOS_ABIERTOS_EVIDENCE:
        for ch in ev["challenges"]:
            key = (ev["id"], ch)
            if key in seen_ac:
                continue
            seen_ac.add(key)
            rels.append(
                {
                    "source": ev["id"],
                    "target": ch,
                    "type": "addresses_challenge",
                    "verified": False,
                    "suggested": True,
                    "source_url": ev["source_url"],
                    "notes": "MINAM datos abiertos evidence (catalog reference)",
                }
            )

    POLICIES_PATH.write_text(json.dumps(policies, ensure_ascii=False, indent=2) + "\n")
    RELS_PATH.write_text(json.dumps(rels, ensure_ascii=False, indent=2) + "\n")

    gov_ids = {a["id"] for a in pe_gov}
    linked = {r["source"] for r in rels if r["type"] == "issues_policy" and r["source"] in gov_ids}
    stats = {
        "sinia_vigente_scraped": len(sinia_policies),
        "pe_policies_total": sum(1 for p in policies if p["country"] == "Peru"),
        "pe_legacy_kept": len(kept_legacy),
        "issues_policy_pe": sum(1 for r in rels if r["type"] == "issues_policy" and r["source"] in gov_ids),
        "addresses_challenge": sum(1 for r in rels if r["type"] == "addresses_challenge"),
        "gov_linked": len(linked),
        "gov_unlinked": sorted(gov_ids - linked),
    }
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
