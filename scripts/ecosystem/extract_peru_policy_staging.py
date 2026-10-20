#!/usr/bin/env python3
"""Extract Peru policy/gov records from Mapa de Actores 2026 deck + Excel (staging only)."""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
DECK = Path("/home/debian/.cursor/projects/home-debian/uploads/deck_8fe0.txt")
XLSX = Path("/home/debian/.cursor/projects/home-debian/uploads/mapeo-peru-db_5cd5.xlsx")
ACTORS = ROOT / "static" / "ecosystem" / "data" / "actors.json"
OUT_DIR = ROOT / "data" / "ecosystem-policy" / "staging" / "peru-mapa-actores-2026"

DELIVERABLE = "Mapa de Actores & Aliados del Emprendimiento Climático del Perú (Jennifer González, 20 Oct 2026)"

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
CHALLENGE_RE = re.compile(r"\b(BOS|AGU|AZU|CIR|AGR|ENE|CIU|FIN|ARG)\b")


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def slug(s: str) -> str:
    s = strip_accents(s.lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:64]


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", strip_accents(s.lower()))


def deck_source(section: str, start: int, end: int, note: str = "") -> dict:
    return {
        "document": "deck (pdftotext)",
        "deliverable": DELIVERABLE,
        "section": section,
        "lines": [start, end],
        "ref": f"deck:lines:{start}-{end}",
        "note": note or None,
    }


def excel_source(sheet: str, row: int, note: str = "") -> dict:
    return {
        "document": "Base de datos REIN Hub Perú.xlsx",
        "deliverable": DELIVERABLE,
        "sheet": sheet,
        "row": row,
        "ref": f"excel:{sheet}:row:{row}",
        "note": note or None,
    }


def load_actor_index() -> dict[str, str]:
    """norm_name → ecosystem actor id (Peru gov/policy-related)."""
    if not ACTORS.exists():
        return {}
    actors = json.loads(ACTORS.read_text(encoding="utf-8"))
    idx: dict[str, str] = {}
    for a in actors:
        if a.get("country") != "Peru":
            continue
        nn = norm_name(a.get("name", ""))
        if nn:
            idx[nn] = a["id"]
    aliases = {
        "minam": "pe-minam-ministerio-del-ambiente",
        "ministeriodelambiente": "pe-minam-ministerio-del-ambiente",
        "produce": "pe-produce-ministerio-de-la-produccion",
        "midagri": "pe-midagri-ministerio-de-desarrollo-agrario-y-riego",
        "minem": "pe-minem-ministerio-de-energia-y-minas",
        "mef": "pe-mef-ministerio-de-economia-y-finanzas",
        "proinnovate": "pe-proinnovate-startup-peru",
        "proinnovatestartupperu": "pe-proinnovate-startup-peru",
        "cofide": "pe-cofide-fcei",
    }
    for k, aid in aliases.items():
        idx[k] = aid
    return idx


def resolve_actor_id(name: str, idx: dict[str, str]) -> str | None:
    nn = norm_name(name)
    if nn in idx:
        return idx[nn]
    for kn, aid in idx.items():
        if len(nn) >= 6 and (nn in kn or kn in nn):
            return aid
    return None


def timeline_policies(deck_lines: list[str]) -> list[dict]:
    """Structured timeline from deck § Marco normativo (approx lines 162–202)."""
    section = "Marco normativo y de política climática del Perú"
    items = [
        (1997, "law", "Ley de Áreas Naturales Protegidas", "Ley 26834", "Conservación y ecoturismo.", 170, 181),
        (2005, "law", "Ley General del Ambiente", "Ley 28611", "Marco ambiental general.", 170, 181),
        (2008, "regulation", "Promoción de energías renovables", "D. Leg. 1002", "Promoción ER; límites captura anchoveta (D. Leg. 1084).", 170, 181),
        (2009, "law", "Ley de Recursos Hídricos", "Ley 29338", "Gestión por cuencas y derechos de uso de agua.", 170, 181),
        (2011, "law", "Ley Forestal y de Fauna Silvestre", "Ley 29763", "Concesiones, manejo forestal comunitario y bionegocios.", 170, 181),
        (2014, "law", "Mecanismos de Retribución por Servicios Ecosistémicos", "Ley 30215", "Usuarios del agua pagan por conservación de cuencas.", 170, 181),
        (2014, "regulation", "Ley de Gestión Integral de Residuos Sólidos", "D. Leg. 1278", "Prioriza reducir y valorizar residuos; RAP.", 170, 181),
        (2016, "law", "Ley de plásticos de un solo uso", "Ley 30884", "Restricción envases de un solo uso.", 170, 181),
        (2018, "law", "Ley Marco sobre Cambio Climático", "Ley 30754", "Base legal NDC, gobernanza climática, Plataforma Huella de Carbono Perú.", 188, 202),
        (2024, "law", "Ley Forestal / Ley 31973 (empaques)", "Ley 31973", "Modifica Ley Forestal; empaques alternativos y biodegradables; traslado competencias MIDAGRI.", 176, 185),
        (2025, "strategy", "Hoja de Ruta de Finanzas Verdes", None, "~US$ 5.800 M al 2030; crédito verde pymes/startups (MINAM).", 173, 178),
        (2025, "strategy", "NDC 3.0 — Nuestro Desafío Climático", "NDC 3.0", "Tope absoluto 179 MtCO₂e al 2035; COP30 Belém nov 2025.", 203, 231),
        (None, "strategy", "Estrategia Nacional ante el Cambio Climático a 2050", None, "Mencionada junto a Ley Marco (implementación pendiente).", 164, 166),
    ]
    out = []
    for year, kind, name, instrument_id, summary, ls, le in items:
        pid = f"pe-pol-{slug(name)}"
        out.append(
            {
                "id": pid,
                "country": "PE",
                "name": name,
                "kind": kind,
                "instrument_id": instrument_id,
                "year": year,
                "summary": summary,
                "challenges": sorted(set(CHALLENGE_RE.findall(summary))),
                "urls": [],
                "sources": [deck_source(section, ls, le)],
            }
        )
    # International / market context (deck § Contexto internacional)
    section_intl = "Contexto internacional que mueve el mercado"
    out.append(
        {
            "id": f"pe-pol-{slug('Reglamento europeo de deforestación EUDR')}",
            "country": "PE",
            "name": "Reglamento europeo de deforestación (EUDR)",
            "kind": "international_regulation",
            "instrument_id": "EUDR",
            "year": None,
            "summary": "Exige trazabilidad libre de deforestación para café, cacao, palma, ganado y madera; impacto en exportadores peruanos.",
            "challenges": ["BOS", "AGR"],
            "urls": [],
            "sources": [deck_source(section_intl, 232, 239)],
        }
    )
    out.append(
        {
            "id": f"pe-pol-{slug('Alianza por el Clima Perú-Alemania')}",
            "country": "PE",
            "name": "Alianza por el Clima Perú–Alemania",
            "kind": "international_cooperation",
            "instrument_id": None,
            "year": 2022,
            "summary": "Cooperación bilateral climática (mencionada con GIZ).",
            "challenges": ["FIN"],
            "urls": [],
            "sources": [deck_source(section_intl, 241, 242)],
        }
    )
    return out


def deck_programmes_and_agencies(deck_lines: list[str]) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse deck § SECTOR GOBIERNO (lines ~645–840)."""
    policies: list[dict] = []
    agencies: list[dict] = []
    links: list[dict] = []
    idx = load_actor_index()

    blocks: list[tuple[str, list[str], int, int, list[str]]] = [
        (
            "MINAM – Ministerio del Ambiente",
            [
                "Rector de la política ambiental y climática",
                "Lidera la NDC 3.0, la Hoja de Ruta de Finanzas Verdes, Mi Negocio Verde y Bionegocios",
            ],
            680,
            683,
            ["BOS", "AGU", "AZU", "CIR", "AGR", "ENE", "CIU", "FIN"],
        ),
        (
            "PRODUCE – Ministerio de la Producción",
            [
                "Rector de mypes, industria, pesca y acuicultura",
                "Financia emprendimiento vía ProInnóvate y el FCEI; hojas de ruta de economía circular",
            ],
            686,
            690,
            ["AZU", "CIR", "FIN"],
        ),
        (
            "MIDAGRI Ministerio de Desarrollo Agrario y Riego",
            ["Políticas agrarias, riego y zonificación forestal"],
            694,
            696,
            ["BOS", "AGR", "AGU"],
        ),
        (
            "MINEM Ministerio de Energía y Minas",
            ["Define la matriz eléctrica y la promoción de renovables"],
            700,
            702,
            ["ENE"],
        ),
        (
            "MEF Ministerio de Economía y Finanzas",
            ["Inversión pública y finanzas climáticas junto al MINAM"],
            708,
            710,
            ["FIN"],
        ),
        (
            "SBS y SMV",
            ["Reglas de riesgo climático y emisión de bonos verdes"],
            714,
            719,
            ["FIN"],
        ),
        (
            "Osinergmin, SUNASS",
            [
                "Reguladores de energía y de agua",
                "Marco para generación distribuida y retribución por servicios ecosistémicos",
            ],
            723,
            728,
            ["ENE", "AGU"],
        ),
    ]

    section = "SECTOR GOBIERNO — Ministerios y reguladores"
    for name, roles, ls, le, challenges in blocks:
        aid = resolve_actor_id(name.split("–")[0].strip(), idx)
        agencies.append(
            {
                "id": f"pe-gov-{slug(name)}",
                "ecosystem_actor_id": aid,
                "name": name,
                "roles": roles,
                "challenges": challenges,
                "urls": ["https://www.gob.pe"],
                "sources": [deck_source(section, ls, le)],
            }
        )

    prog_blocks = [
        (
            "ProInnóvate – StartUp Perú",
            "programme",
            ["Programa de PRODUCE para innovación y emprendimiento", "Capital semilla hasta S/ 150 mil; convocatorias climáticas"],
            732,
            737,
            ["https://www.gob.pe/proinnovate", "https://startup.proinnovate.gob.pe"],
            ["FIN", "AGR", "ENE", "CIR"],
            ("PRODUCE – Ministerio de la Producción", "administers", True, "Programa de PRODUCE para innovación y emprendimiento"),
        ),
        (
            "COFIDE – FCEI",
            "programme",
            ["Banco de desarrollo y fondo de fondos de VC", "Inversor ancla; articula Bionegocios"],
            739,
            742,
            ["https://www.cofide.com.pe"],
            ["BOS", "FIN"],
            (None, None, False, None),
        ),
        (
            "Programa para Bionegocios (MINAM)",
            "programme",
            ["Programa de crédito para la Amazonía", "Más de S/ 22 M en créditos a más de 3.900 bionegocios"],
            744,
            747,
            ["https://www.gob.pe/minam"],
            ["BOS"],
            ("MINAM – Ministerio del Ambiente", "administers", True, "Programa para Bionegocios (MINAM)"),
        ),
        (
            "CONCYTEC – ProCiencia",
            "programme",
            ["Consejo y programa de ciencia y tecnología", "Fondos de I+D y desafíos de innovación regional"],
            750,
            755,
            ["https://www.gob.pe/concytec", "https://prociencia.gob.pe"],
            ["BOS", "AGU", "AZU", "CIR", "AGR", "ENE", "CIU", "FIN"],
            (None, None, False, None),
        ),
        (
            "Programa Bosques (MINAM)",
            "programme",
            ["Programa Nacional de Conservación de Bosques", "Financia planes de negocio comunitarios hasta S/ 370 mil"],
            766,
            769,
            ["https://www.gob.pe/bosques"],
            ["BOS"],
            ("MINAM – Ministerio del Ambiente", "administers", True, "Programa Bosques (MINAM)"),
        ),
        (
            "Plataforma Huella de Carbono Perú",
            "programme",
            ["Herramienta de medición vinculada al marco climático"],
            222,
            224,
            ["https://www.gob.pe/minam"],
            ["FIN"],
            ("MINAM – Ministerio del Ambiente", "administers", False, "Plataforma Huella de Carbono Perú (marco NDC)"),
        ),
        (
            "Mi Negocio Verde",
            "programme",
            ["Programa MINAM para MYPE verdes"],
            682,
            682,
            ["https://www.gob.pe/minam"],
            ["CIR", "FIN"],
            ("MINAM – Ministerio del Ambiente", "administers", True, "Lidera … Mi Negocio Verde"),
        ),
    ]

    section_prog = "SECTOR GOBIERNO — Programas, fondos y organismos técnicos"
    for name, kind, desc, ls, le, urls, challenges, (gov_name, rel, verified, evidence) in prog_blocks:
        pid = f"pe-pol-{slug(name)}"
        policies.append(
            {
                "id": pid,
                "country": "PE",
                "name": name,
                "kind": kind,
                "instrument_id": None,
                "year": None,
                "summary": " ".join(desc),
                "challenges": challenges,
                "urls": urls,
                "sources": [deck_source(section_prog, ls, le)],
            }
        )
        if gov_name and rel:
            gov_id = resolve_actor_id(gov_name.split("–")[0].strip(), idx)
            links.append(
                {
                    "gov_actor_name": gov_name,
                    "ecosystem_actor_id": gov_id,
                    "policy_id": pid,
                    "relation": rel,
                    "verified": verified,
                    "evidence": evidence,
                    "sources": [deck_source(section_prog, ls, le, evidence or "")],
                }
            )

    # Explicit ministry → NDC / Finanzas Verdes (deck wording)
    ndc_id = f"pe-pol-{slug('NDC 3.0 — Nuestro Desafío Climático')}"
    hrfv_id = f"pe-pol-{slug('Hoja de Ruta de Finanzas Verdes')}"
    ley_marco_id = f"pe-pol-{slug('Ley Marco sobre Cambio Climático')}"
    minam_id = resolve_actor_id("MINAM", idx)
    mef_id = resolve_actor_id("MEF", idx)
    for pol_id, gov_id, gov_name, rel, verified, ev, ls, le in [
        (ndc_id, minam_id, "MINAM – Ministerio del Ambiente", "leads", True, "Lidera la NDC 3.0", 680, 682),
        (hrfv_id, minam_id, "MINAM – Ministerio del Ambiente", "leads", True, "Lidera la Hoja de Ruta de Finanzas Verdes", 680, 682),
        (hrfv_id, mef_id, "MEF Ministerio de Economía y Finanzas", "co_leads", True, "finanzas climáticas junto al MINAM", 708, 710),
        (ley_marco_id, minam_id, "MINAM", "implements", False, "Rector política ambiental y climática (marco general)", 680, 682),
    ]:
        links.append(
            {
                "gov_actor_name": gov_name,
                "ecosystem_actor_id": gov_id,
                "policy_id": pol_id,
                "relation": rel,
                "verified": verified,
                "evidence": ev,
                "sources": [deck_source(section, ls, le, ev)],
            }
        )

    produce_id = resolve_actor_id("PRODUCE", idx)
    links.append(
        {
            "gov_actor_name": "PRODUCE – Ministerio de la Producción",
            "ecosystem_actor_id": produce_id,
            "policy_id": f"pe-pol-{slug('ProInnóvate – StartUp Perú')}",
            "relation": "administers",
            "verified": True,
            "evidence": "Financia emprendimiento vía ProInnóvate y el FCEI",
            "sources": [deck_source(section, 688, 689)],
        }
    )

    tech_agencies = [
        ("SERFOR, SERNANP", ["Servicios forestal y de áreas protegidas", "Concesiones, manejo forestal y ecoturismo"], 771, 776, ["BOS"]),
        ("INAIGEM, ANA, SENAMHI", ["Glaciares, agua y clima", "Datos y alertas para agua y agro"], 778, 784, ["AGU", "AGR"]),
        ("IMARPE, SANIPES", ["Ciencia marina e inocuidad pesquera"], 807, 812, ["AZU"]),
        ("AGROIDEAS, Agrobanco", ["Cofinanciamiento y banca agraria"], 759, 764, ["AGR"]),
        ("ProInversión, PromPerú", ["Promoción de inversión y exportaciones"], 789, 794, ["ENE", "AGR"]),
        ("APCI", ["Cooperación internacional registrada"], 799, 802, []),
    ]
    section_tech = "SECTOR GOBIERNO — Programas, fondos y organismos técnicos"
    for name, roles, ls, le, challenges in tech_agencies:
        agencies.append(
            {
                "id": f"pe-gov-{slug(name)}",
                "ecosystem_actor_id": resolve_actor_id(name.split(",")[0].strip(), idx),
                "name": name,
                "roles": roles,
                "challenges": challenges,
                "urls": ["https://www.gob.pe"],
                "sources": [deck_source(section_tech, ls, le)],
            }
        )

    return policies, agencies, links


def excel_policy_rows() -> tuple[list[dict], list[dict]]:
    """Government programmes and agencies from Excel (no Invitados; no personal emails)."""
    policies: list[dict] = []
    agencies: list[dict] = []
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Base de datos REIN Perú"]
    headers = None
    seen_prog: set[str] = set()
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if row and row[0] == "Nombre Organización":
            headers = [str(x).strip() if x else "" for x in row]
            continue
        if not headers or not row or not row[0]:
            continue
        rec = dict(zip(headers, row))
        name = str(rec.get("Nombre Organización", "")).strip()
        cat = str(rec.get("Categoría") or "")
        if "gobierno" not in cat.lower():
            continue
        web = rec.get("Website")
        if web and EMAIL_RE.search(str(web)):
            web = None
        if web and "linkedin.com" in str(web).lower():
            web = None
        nn = norm_name(name)
        if nn in seen_prog:
            continue
        # Programmes / convocatorias (unique names with public programme URLs)
        if any(
            k in name.lower()
            for k in ("emprendimientos", "prociencia", "desafío", "desafios", "cambio climático", "cambio climatico")
        ):
            if not web:
                continue
            seen_prog.add(nn)
            pid = f"pe-pol-{slug(name)}"
            policies.append(
                {
                    "id": pid,
                    "country": "PE",
                    "name": name,
                    "kind": "programme",
                    "instrument_id": None,
                    "year": 2024 if "2024" in name else None,
                    "summary": scrub(str(rec.get("Rol / Cargo") or "Convocatoria / programa público (Excel REIN).")),
                    "challenges": ["FIN", "AGR", "ENE", "CIR"],
                    "urls": [str(web).strip()] if web else [],
                    "sources": [excel_source("Base de datos REIN Perú", i)],
                }
            )
        elif name.lower() in ("minam", "ministerio del ambiente", "ministerio de ambiente"):
            agencies.append(
                {
                    "id": "pe-gov-minam-excel",
                    "ecosystem_actor_id": resolve_actor_id("MINAM", load_actor_index()),
                    "name": name,
                    "roles": [scrub(str(rec.get("Rol / Cargo") or "Contacto institucional (organización)."))],
                    "challenges": [],
                    "urls": [str(web)] if web and str(web).startswith("http") else ["https://www.gob.pe/minam"],
                    "sources": [excel_source("Base de datos REIN Perú", i, "Organización; sin dato personal.")],
                }
            )
    return policies, agencies


def scrub(s: str) -> str:
    s = EMAIL_RE.sub("", s)
    return re.sub(r"\s+", " ", s).strip()


def dedupe_policies(items: list[dict]) -> list[dict]:
    by_id: dict[str, dict] = {}
    for p in items:
        pid = p["id"]
        if pid not in by_id:
            by_id[pid] = p
            continue
        ex = by_id[pid]
        ex["sources"] = ex.get("sources", []) + [s for s in p.get("sources", []) if s not in ex.get("sources", [])]
        if p.get("urls"):
            ex["urls"] = list(dict.fromkeys((ex.get("urls") or []) + p["urls"]))
    return list(by_id.values())


def dedupe_links(links: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for l in links:
        key = (l.get("ecosystem_actor_id"), l.get("policy_id"), l.get("relation"), l.get("verified"))
        if key in seen:
            continue
        seen.add(key)
        out.append(l)
    return out


def main() -> None:
    deck_lines = DECK.read_text(encoding="utf-8", errors="replace").splitlines()
    policies = timeline_policies(deck_lines)
    p2, agencies, links = deck_programmes_and_agencies(deck_lines)
    policies.extend(p2)
    px, ax = excel_policy_rows()
    policies.extend(px)
    agencies.extend(ax)
    policies = dedupe_policies(policies)
    links = dedupe_links(links)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "staging_for_branch": "research/ecosystem-policy",
        "consumer_job": "bc-a4128a58",
        "country": "PE",
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "deliverable": DELIVERABLE,
        "privacy": {
            "excluded_sheets": ["Invitados Evento Embajada"],
            "excluded_fields": ["email", "phone", "personal_contact"],
        },
        "counts": {
            "policies": len(policies),
            "gov_agencies": len(agencies),
            "gov_policy_links": len(links),
            "verified_links": sum(1 for l in links if l.get("verified")),
        },
        "files": {
            "policies": "policies.json",
            "gov_agencies": "gov_agencies.json",
            "gov_policy_links": "gov_policy_links.json",
        },
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "policies.json").write_text(json.dumps(policies, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT_DIR / "gov_agencies.json").write_text(json.dumps(agencies, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT_DIR / "gov_policy_links.json").write_text(
        json.dumps(links, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    readme = f"""# Peru policy staging — Mapa de Actores 2026

**Do not deploy to live ecosystem.** Merge via branch `research/ecosystem-policy` (job `bc-a4128a58`).

## Contents

- `policies.json` — laws, regulations, programmes, strategies ({manifest['counts']['policies']} records)
- `gov_agencies.json` — ministries/regulators and roles from deck § Gobierno ({manifest['counts']['gov_agencies']})
- `gov_policy_links.json` — gov actor → policy edges; `verified: true` only when deck states responsibility ({manifest['counts']['verified_links']} verified / {manifest['counts']['gov_policy_links']} total)

## Source refs

Each record includes `sources[]` with `deck:lines:…` or `excel:Sheet:row:…`.

Privacy: **Invitados Evento Embajada** not used; no emails in staging JSON.
"""
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
