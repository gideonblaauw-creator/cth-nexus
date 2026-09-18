#!/usr/bin/env python3
"""Generate CLP26 Colombia Nexus one-pager JSON for the remaining 20 startups."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_SRC = Path("/opt/cth-nexus/data/clp26_colombia_ideas.json")
OUT_DIR = ROOT / "onepagers" / "data"

# LATAM-appropriate Unsplash backgrounds (agriculture, tropics, Colombia context)
BG = {
    "farm": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80",
    "coffee": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1200&q=80",
    "crop": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80",
    "water": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1200&q=80",
    "recycle": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200&q=80",
    "industry": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200&q=80",
    "tech": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80",
    "forest": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80",
    "team": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1200&q=80",
    "urban": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200&q=80",
    "mushroom": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=1200&q=80",
    "pet": "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=1200&q=80",
    "greenhouse": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80",
}

SLUG_MAP: dict[str, str | dict] = {
    "artexlab": "ArtexLab",
    "agrolider": "AGROLIDER",
    "airthnova": "AirthNova",
    "climatik": {"override": "climatik_wiki"},
    "nux": {"override": "nux_wiki"},
    "circuito-cero": "Circuito cero",
    "planta-comunitaria-wpc": "Implementación de una Planta Comunitaria",
    "kuo": "KUO",
    "el-ocambulo": "El Ocámbulo",
    "dantium": "DANTIUM",
    "honeyb": "HoneyB",
    "sie-waka": "SIÉ WAKA",
    "reporti": "REPORTI",
    "sekpos": "SEKPOS",
    "clean-sim": "Clean Sim",
    "agrodata-connect": "AgroData Connect",
    "aterna": "Aterna",
    "nextgen-nutrition": "NextGen Nutrition",
    "modular-agrosolutions": "Modular Agrosolutions",
    "eco-bloque": {"override": "eco_bloque_stub"},
}

CLIMATIK_WIKI = {
    "startup_name": "CLIMATIK",
    "legal_name": "BARUK COMPANY BIO CLIMATIK SAS",
    "founder": "Allan Engelberth Figueredo Vargas",
    "category": "Clean Industry",
    "stage": "Private Beta",
    "website": "",
    "ct_taxonomy": "[PENDIENTE]",
    "description": "Intelligent bioclimatic greenhouses for food sovereignty and protection of ancestral seeds — sustainable infrastructure even without traditional power grids, plus bioclimatic retrofits for existing buildings.",
    "problem": "Global hunger and the need for year-round food production without fertile land or high carbon footprints — especially for indigenous communities and farmer associations.",
    "solution": "Bioclimatic smart greenhouses with block_line® construction material (fire-resistant, thermo-acoustic, antifungal) enabling 24/7 production and seed preservation with minimal carbon footprint.",
    "revenue_model": "Franchise model for bioclimatic greenhouse deployments; B2G and international partnership sales.",
    "target_market": "Farmer associations, indigenous communities, and countries seeking food-sovereignty infrastructure.",
}

NUX_WIKI = {
    "startup_name": "NUX",
    "founder": "[PENDIENTE]",
    "category": "Not Assigned / Unknown",
    "stage": "Unknown",
    "website": "",
    "ct_taxonomy": "[PENDIENTE]",
    "description": "CLP26 Colombia cohort startup — details pending Odoo/Wiki sync.",
    "problem": "[PENDIENTE]",
    "solution": "[PENDIENTE]",
    "revenue_model": "[PENDIENTE]",
    "target_market": "[PENDIENTE]",
    "impact_areas": "Circular Economy",
}

ECO_BLOQUE_STUB = {
    "startup_name": "Eco-Bloque",
    "founder": "[PENDIENTE]",
    "category": "[PENDIENTE]",
    "stage": "[PENDIENTE]",
    "website": "",
    "ct_taxonomy": "[PENDIENTE]",
    "description": "CLP26 Colombia cohort startup — application data not yet mirrored in clp26_colombia_ideas.json or Wiki.",
    "problem": "[PENDIENTE]",
    "solution": "[PENDIENTE]",
    "revenue_model": "[PENDIENTE]",
    "target_market": "[PENDIENTE]",
}


def load_clp26() -> list[dict]:
    return json.loads(DATA_SRC.read_text())


def find_record(data: list[dict], needle: str) -> dict | None:
    n = needle.lower()
    for row in data:
        if n in row.get("startup_name", "").lower():
            return row
    return None


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def trunc(s: str, n: int = 220) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    if len(s) <= n:
        return s
    return s[: n - 1].rsplit(" ", 1)[0] + "…"


def cat_badge(category: str) -> tuple[str, str]:
    c = category or "[PENDIENTE]"
    return c, c


def display_name(rec: dict, slug: str) -> str:
    if slug == "planta-comunitaria-wpc":
        return "Planta Comunitaria WPC"
    if slug == "climatik":
        return "CLIMATIK"
    if slug == "clean-sim":
        return "Clean Sim"
    if slug == "nextgen-nutrition":
        return "NextGen Nutrition"
    return rec.get("startup_name", slug).split("(")[0].strip()


def hero_sub(rec: dict, slug: str, name: str) -> tuple[str, str]:
    website = rec.get("website") or ""
    stage = rec.get("stage") or "[PENDIENTE]"
    cat = rec.get("category") or "[PENDIENTE]"
    tax = rec.get("ct_taxonomy") or "[PENDIENTE]"
    loc = "Colombia"
    site = website.replace("https://", "").replace("http://", "").rstrip("/") if website else "[PENDIENTE]"
    en = f"{site} &middot; {loc} &middot; {cat} &middot; Stage: {stage} &middot; {tax}"
    es = f"{site} &middot; {loc} &middot; {cat} &middot; Etapa: {stage} &middot; {tax}"
    if slug == "climatik":
        en = f"BARUK COMPANY BIO CLIMATIK SAS &middot; Colombia &middot; Clean Industry &middot; Stage: Private Beta"
        es = f"BARUK COMPANY BIO CLIMATIK SAS &middot; Colombia &middot; Industria Limpia &middot; Etapa: Beta Privada"
    return en, es


def ribbon_from_rec(rec: dict) -> list[dict]:
    stage = rec.get("stage") or "[PENDIENTE]"
    cat = (rec.get("category") or "[PENDIENTE]")[:12]
    tax = rec.get("ct_taxonomy") or "[PENDIENTE]"
    funded = "Yes" if rec.get("funded") else ("No" if "funded" in rec else "[PENDIENTE]")
    if isinstance(rec.get("funded"), bool):
        funded = "Yes" if rec["funded"] else "No"
    else:
        funded = "[PENDIENTE]"
    team = rec.get("team_size")
    try:
        team_s = str(int(float(team))) if team not in (None, "", "—") else "[PENDIENTE]"
    except (TypeError, ValueError):
        team_s = "[PENDIENTE]"
    return [
        {"val": stage[:10], "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CLP26 CO", "sub_es": "CLP26 CO"},
        {"val": cat, "lab_en": "Category", "lab_es": "Categoría", "sub_en": "Cleantech", "sub_es": "Cleantech"},
        {"val": tax, "lab_en": "CT Taxonomy", "lab_es": "Taxonomía CT", "sub_en": "CTH", "sub_es": "CTH"},
        {"val": team_s, "lab_en": "Team", "lab_es": "Equipo", "sub_en": "Application", "sub_es": "Aplicación"},
    ]


def problem_stats(rec: dict) -> list[list[dict]]:
    return [
        [
            {"num": "CLP", "lab_en": "2026 Colombia", "lab_es": "2026 Colombia"},
            {"num": "CTH", "lab_en": "Accelerator", "lab_es": "Acelerador"},
        ],
        [
            {"num": "[P]", "lab_en": "Metrics pending", "lab_es": "Métricas pendientes"},
            {"num": "CO", "lab_en": "Colombia", "lab_es": "Colombia"},
        ],
    ]


def build_page(slug: str, rec: dict) -> dict:
    name = display_name(rec, slug)
    desc = rec.get("description") or "[PENDIENTE]"
    problem = rec.get("problem") or "[PENDIENTE]"
    solution = rec.get("solution") or "[PENDIENTE]"
    founder = rec.get("founder") or "[PENDIENTE]"
    website = rec.get("website") or "#"
    cat_en, cat_es = cat_badge(rec.get("category", ""))
    hero_sub_en, hero_sub_es = hero_sub(rec, slug, name)

    badge_en = f"{cat_en} &middot; CLP26 Colombia"
    badge_es = f"{cat_es} &middot; CLP26 Colombia"

    pitch_en = trunc(desc, 280)
    pitch_es = pitch_en  # source mostly EN; ES mirror with note in team section

    cta_en = trunc(solution, 200)
    cta_es = cta_en

    tax = rec.get("ct_taxonomy") or "[PENDIENTE]"
    dream_en = (
        f"CT taxonomy: {tax}. CLP 2026 Colombia bootcamp cohort — CleantechHUB accelerator. "
        f"Pitch deck: [PENDIENTE]. Revenue / ARR: [PENDIENTE]."
    )
    dream_es = (
        f"Taxonomía CT: {tax}. Cohorte bootcamp CLP 2026 Colombia — acelerador CleantechHUB. "
        f"Pitch deck: [PENDIENTE]. Ingresos / ARR: [PENDIENTE]."
    )

    if slug == "climatik":
        dream_en = (
            "Legal entity: BARUK COMPANY BIO CLIMATIK SAS. CT taxonomy: [PENDIENTE]. "
            "CLP 2026 Colombia bootcamp cohort — CleantechHUB. Wiki source; not in clp26_colombia_ideas.json. "
            "Pitch deck: [PENDIENTE]."
        )
        dream_es = dream_en.replace("Legal entity", "Entidad legal").replace("bootcamp cohort", "cohorte bootcamp")

    if slug == "nux":
        dream_en = (
            "NUX — not in clp26_colombia_ideas.json or Odoo res.partner. "
            "Wiki BookStack page nux-not-assigned-unknown (2025-09-18). CLP26 end-report mention. "
            "Founder, stage, website: [PENDIENTE]."
        )
        dream_es = dream_en

    if slug == "eco-bloque":
        dream_en = (
            "Eco-Bloque — not in clp26_colombia_ideas.json or Wiki as of 2025-09-18. "
            "CLP26 Colombia roster slug reserved. All fields [PENDIENTE] pending data sync."
        )
        dream_es = dream_en

    initials = "".join(w[0] for w in founder.replace("[PENDIENTE]", "P").split()[:2]).upper() or "??"

    bg_sets = {
        "artexlab": (BG["recycle"], BG["industry"], BG["urban"], BG["recycle"], BG["team"]),
        "agrolider": (BG["crop"], BG["farm"], BG["coffee"], BG["tech"], BG["team"]),
        "airthnova": (BG["forest"], BG["tech"], BG["industry"], BG["forest"], BG["team"]),
        "climatik": (BG["greenhouse"], BG["farm"], BG["greenhouse"], BG["crop"], BG["team"]),
        "nux": (BG["recycle"], BG["industry"], BG["tech"], BG["urban"], BG["team"]),
        "circuito-cero": (BG["recycle"], BG["urban"], BG["recycle"], BG["forest"], BG["team"]),
        "planta-comunitaria-wpc": (BG["recycle"], BG["industry"], BG["recycle"], BG["urban"], BG["team"]),
        "kuo": (BG["urban"], BG["tech"], BG["recycle"], BG["urban"], BG["team"]),
        "el-ocambulo": (BG["mushroom"], BG["urban"], BG["mushroom"], BG["recycle"], BG["team"]),
        "dantium": (BG["recycle"], BG["industry"], BG["recycle"], BG["farm"], BG["team"]),
        "honeyb": (BG["forest"], BG["industry"], BG["forest"], BG["farm"], BG["team"]),
        "sie-waka": (BG["water"], BG["tech"], BG["water"], BG["water"], BG["team"]),
        "reporti": (BG["tech"], BG["industry"], BG["tech"], BG["urban"], BG["team"]),
        "sekpos": (BG["urban"], BG["tech"], BG["urban"], BG["industry"], BG["team"]),
        "clean-sim": (BG["industry"], BG["tech"], BG["urban"], BG["industry"], BG["team"]),
        "agrodata-connect": (BG["crop"], BG["tech"], BG["farm"], BG["coffee"], BG["team"]),
        "aterna": (BG["farm"], BG["industry"], BG["crop"], BG["farm"], BG["team"]),
        "nextgen-nutrition": (BG["pet"], BG["recycle"], BG["pet"], BG["farm"], BG["team"]),
        "modular-agrosolutions": (BG["crop"], BG["tech"], BG["farm"], BG["tech"], BG["team"]),
        "eco-bloque": (BG["recycle"], BG["industry"], BG["recycle"], BG["urban"], BG["team"]),
    }
    bgs = bg_sets.get(slug, (BG["farm"], BG["tech"], BG["crop"], BG["forest"], BG["team"]))

    target = trunc(rec.get("target_market") or "[PENDIENTE]", 120)
    revenue = trunc(rec.get("revenue_model") or "[PENDIENTE]", 120)
    demand = trunc(rec.get("demand_evidence") or "[PENDIENTE]", 120)

    page = {
        "slug": slug,
        "name": name,
        "website": website if website else "#",
        "badge_en": badge_en,
        "badge_es": badge_es,
        "hero_image": bgs[0],
        "hero_sub_en": hero_sub_en,
        "hero_sub_es": hero_sub_es,
        "pitch_en": esc(pitch_en),
        "pitch_es": esc(pitch_es),
        "cta_pitch_en": esc(cta_en),
        "cta_pitch_es": esc(cta_es),
        "cta_btn_en": "Visit website" if website and website != "#" else "CleantechHUB",
        "cta_btn_es": "Visitar sitio" if website and website != "#" else "CleantechHUB",
        "ribbon": ribbon_from_rec(rec),
        "problem_stats": problem_stats(rec),
        "sections": [
            {
                "num": 1,
                "type": "split",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "The Problem",
                "title_es": "El Problema",
                "head_en": trunc(problem, 100),
                "head_es": trunc(problem, 100),
                "body_en": esc(trunc(problem, 400)),
                "body_es": esc(trunc(problem, 400)),
                "bg": bgs[0],
            },
            {
                "num": 2,
                "type": "solution",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": f"How {name} Works",
                "title_es": f"Cómo Funciona {name}",
                "steps": [
                    {
                        "icon": "🎯",
                        "label_en": "Focus",
                        "label_es": "Enfoque",
                        "text_en": esc(trunc(solution, 160)),
                        "text_es": esc(trunc(solution, 160)),
                    },
                    {
                        "icon": "⚙️",
                        "label_en": "Model",
                        "label_es": "Modelo",
                        "text_en": esc(revenue),
                        "text_es": esc(revenue),
                    },
                    {
                        "icon": "🌎",
                        "label_en": "Market",
                        "label_es": "Mercado",
                        "text_en": esc(target),
                        "text_es": esc(target),
                    },
                    {
                        "icon": "📈",
                        "label_en": "Traction",
                        "label_es": "Tracción",
                        "text_en": esc(demand),
                        "text_es": esc(demand),
                    },
                ],
                "bg": bgs[1],
            },
            {
                "num": 3,
                "type": "table",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "Business Snapshot",
                "title_es": "Resumen del Negocio",
                "headers": [
                    ["Dimension", "Dimensión"],
                    ["Detail (EN)", "Detalle"],
                    ["Status", "Estado"],
                ],
                "rows": [
                    [
                        ["Category", "Categoría"],
                        [cat_en, cat_es],
                        ["CLP26", "CLP26"],
                    ],
                    [
                        ["Stage", "Etapa"],
                        [rec.get("stage") or "[PENDIENTE]", rec.get("stage") or "[PENDIENTE]"],
                        ["Application", "Aplicación"],
                    ],
                    [
                        ["CT Taxonomy", "Taxonomía CT"],
                        [tax, tax],
                        ["CTH", "CTH"],
                    ],
                ],
                "bg": bgs[2],
            },
            {
                "num": 4,
                "type": "impact",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "Climate &amp; Impact",
                "title_es": "Clima e Impacto",
                "cards": [
                    {
                        "icon": "🌱",
                        "title_en": "Climate focus",
                        "title_es": "Enfoque climático",
                        "text_en": esc(trunc(problem, 180)),
                        "text_es": esc(trunc(problem, 180)),
                    },
                    {
                        "icon": "💡",
                        "title_en": "Solution",
                        "title_es": "Solución",
                        "text_en": esc(trunc(solution, 180)),
                        "text_es": esc(trunc(solution, 180)),
                    },
                    {
                        "icon": "🤝",
                        "title_en": "CLP 2026",
                        "title_es": "CLP 2026",
                        "text_en": "ClimateLaunchpad Colombia 2026 bootcamp cohort — CleantechHUB accelerator knowledge transfer.",
                        "text_es": "Cohorte bootcamp ClimateLaunchpad Colombia 2026 — transferencia de conocimiento acelerador CleantechHUB.",
                    },
                    {
                        "icon": "📋",
                        "title_en": "External support",
                        "title_es": "Apoyo externo",
                        "text_en": esc(trunc(rec.get("external_support") or "[PENDIENTE]", 180)),
                        "text_es": esc(trunc(rec.get("external_support") or "[PENDIENTE]", 180)),
                    },
                ],
                "bg": bgs[3],
            },
            {
                "num": 5,
                "type": "team",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "Leadership",
                "title_es": "Liderazgo",
                "members": [
                    {
                        "name": founder if founder != "[PENDIENTE]" else "[PENDIENTE]",
                        "role_en": "Founder &middot; CLP26 Colombia",
                        "role_es": "Fundador(a) &middot; CLP26 Colombia",
                        "bio_en": esc(trunc(rec.get("expertise") or rec.get("team_roles") or "[PENDIENTE]", 220)),
                        "bio_es": esc(trunc(rec.get("expertise") or rec.get("team_roles") or "[PENDIENTE]", 220)),
                        "initials": initials,
                    }
                ],
                "dream_en": dream_en,
                "dream_es": dream_es,
                "bg": bgs[4],
            },
        ],
    }
    return page


def resolve_record(slug: str, spec: str | dict, data: list[dict]) -> dict:
    if isinstance(spec, dict):
        if spec.get("override") == "climatik_wiki":
            return CLIMATIK_WIKI
        if spec.get("override") == "nux_wiki":
            return NUX_WIKI
        if spec.get("override") == "eco_bloque_stub":
            return ECO_BLOQUE_STUB
        needle = spec.get("match", "")
        rec = find_record(data, needle)
        return rec or {}
    rec = find_record(data, spec)
    return rec or {}


def main() -> None:
    data = load_clp26()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for slug, spec in SLUG_MAP.items():
        rec = resolve_record(slug, spec, data)
        if not rec:
            print(f"WARN: no data for {slug}")
            continue
        page = build_page(slug, rec)
        path = OUT_DIR / f"{slug}.json"
        path.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
