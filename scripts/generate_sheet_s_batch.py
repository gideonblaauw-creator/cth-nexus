#!/usr/bin/env python3
"""Generate portfolio-style /s/ one-pager JSON (xiclo/cirkula layout) for sheet-s batches."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCHES = ROOT / "data" / "sheet-s-pages" / "batches.json"
PORTFOLIO = ROOT / "pages" / "p" / "startup-portfolio" / "index.html"
OUT = ROOT / "onepagers" / "data"

CT_LABELS = {
    "CT-IC-005": "Precision Ag & Smart Grid",
    "CT-WA-001": "Industrial Wastewater Treatment",
    "CT-IN-004": "Industrial Symbiosis",
    "CT-WA-003": "E-Waste & Hazardous Waste",
    "CT-WW-003": "Watershed Conservation",
    "CT-IC-004": "Climate Data Platforms",
}

THEME = {
    "EN": ("Energy", "Energía"),
    "CE": ("Circular Economy", "Economía Circular"),
    "BIO": ("Bioeconomy", "Bioeconomía"),
}

def u(photo_id: str) -> str:
    return f"https://images.unsplash.com/{photo_id}?w=1200&q=80"


# Batch index -> portfolio card match name + public slug + extras
BATCH_SPECS: dict[int, list[dict]] = {
    5: [
        {
            "match": "DEXON SOFTWARE SAS BIC",
            "slug": "dexon-software-sas-bic",
            "display": "Dexon Software",
            "city_en": "Bogotá",
            "city_es": "Bogotá",
            "problem_en": "Large organizations in energy, healthcare, and government still rely on slow, costly BPM implementations to digitize complex processes.",
            "problem_es": "Grandes organizaciones en energía, salud y gobierno aún dependen de implementaciones BPM lentas y costosas para digitalizar procesos complejos.",
            "images": {
                "hero": u("photo-1460925895917-afdab827c52f"),
                "sections": [
                    u("photo-1553877522-43269d4ea984"),
                    u("photo-1517245386807-bb43f82c3364"),
                    u("photo-1563986768609-322da13575f3"),
                    u("photo-1504384308090-c894fdcc538d"),
                ],
                "cta": u("photo-1486406146926-c627a92ad1ab"),
                "credits": [
                    {"slot": "hero", "source_url": u("photo-1460925895917-afdab827c52f"), "credit_en": "Unsplash / Carlos Muza", "credit_es": "Unsplash / Carlos Muza"},
                    {"slot": "problem", "source_url": u("photo-1553877522-43269d4ea984"), "credit_en": "Unsplash / UX Indonesia", "credit_es": "Unsplash / UX Indonesia"},
                    {"slot": "solution", "source_url": u("photo-1517245386807-bb43f82c3364"), "credit_en": "Unsplash / Headway", "credit_es": "Unsplash / Headway"},
                    {"slot": "impact", "source_url": u("photo-1563986768609-322da13575f3"), "credit_en": "Unsplash / Jonas Lee", "credit_es": "Unsplash / Jonas Lee"},
                    {"slot": "leadership", "source_url": u("photo-1504384308090-c894fdcc538d"), "credit_en": "Unsplash / Kaleidico", "credit_es": "Unsplash / Kaleidico"},
                    {"slot": "cta", "source_url": u("photo-1486406146926-c627a92ad1ab"), "credit_en": "Unsplash / Victor Garcia", "credit_es": "Unsplash / Victor Garcia"},
                ],
            },
            "founders": [
                {
                    "name": "Luis B. Chicaiza",
                    "role_en": "CEO &amp; Founder &middot; CLAC22",
                    "role_es": "CEO y Fundador &middot; CLAC22",
                    "bio_en": "Public profile lists CEO and founder of Dexon Software (Dexon BPM). Source: LinkedIn.",
                    "bio_es": "Perfil público como CEO y fundador de Dexon Software (Dexon BPM). Fuente: LinkedIn.",
                    "linkedin": "https://linkedin.com/in/lbchicaiza",
                    "initials": "LC",
                }
            ],
        },
        {
            "match": "ECO BIOSIS",
            "slug": "eco-biosis",
            "display": "Eco Biosis",
            "city_en": "[PENDIENTE]",
            "city_es": "[PENDIENTE]",
            "problem_en": "Vinasse and distillery effluents from industry are difficult to treat and often become waste rather than reusable inputs.",
            "problem_es": "La vinaza y los efluentes de destilerías son difíciles de tratar y muchas veces terminan como residuo en lugar de insumos reutilizables.",
            "images": {
                "hero": u("photo-1581091226825-a6a2a5aee158"),
                "sections": [
                    u("photo-1621451537829-247eb3148060"),
                    u("photo-1579162273420-e891596e860a"),
                    u("photo-1596442284341-43b58098b12a"),
                    u("photo-1532635243-17fbf47abfb9"),
                ],
                "cta": u("photo-1611273626479-c3663a10e7a0"),
                "credits": [
                    {"slot": "hero", "source_url": u("photo-1581091226825-a6a2a5aee158"), "credit_en": "Unsplash / ThisisEngineering", "credit_es": "Unsplash / ThisisEngineering"},
                    {"slot": "problem", "source_url": u("photo-1621451537829-247eb3148060"), "credit_en": "Unsplash / engin akyurt", "credit_es": "Unsplash / engin akyurt"},
                    {"slot": "solution", "source_url": u("photo-1579162273420-e891596e860a"), "credit_en": "Unsplash / Rodrigo Cuel", "credit_es": "Unsplash / Rodrigo Cuel"},
                    {"slot": "impact", "source_url": u("photo-1596442284341-43b58098b12a"), "credit_en": "Unsplash / Sigmund", "credit_es": "Unsplash / Sigmund"},
                    {"slot": "leadership", "source_url": u("photo-1532635243-17fbf47abfb9"), "credit_en": "Unsplash / National Cancer Institute", "credit_es": "Unsplash / National Cancer Institute"},
                    {"slot": "cta", "source_url": u("photo-1611273626479-c3663a10e7a0"), "credit_en": "Unsplash / Appolinary Kalashnikova", "credit_es": "Unsplash / Appolinary Kalashnikova"},
                ],
            },
            "founders": [
                {
                    "name": "Eduardo Creixell",
                    "role_en": "Co-founder &middot; CLAC24",
                    "role_es": "Cofundador &middot; CLAC24",
                    "bio_en": "Identified as Eco Biosis co-founder in public company materials. Current role details: [PENDIENTE].",
                    "bio_es": "Identificado como cofundador de Eco Biosis en materiales públicos de la empresa. Detalle de rol actual: [PENDIENTE].",
                    "linkedin": "https://linkedin.com/in/eduardo-creixell",
                    "initials": "EC",
                },
                {
                    "name": "Miguel Creixell",
                    "role_en": "COO &amp; Business Development &middot; CLAC24",
                    "role_es": "COO y Desarrollo de Negocio &middot; CLAC24",
                    "bio_en": "Public LinkedIn lists leadership roles at Eco Biosis. Source: LinkedIn.",
                    "bio_es": "LinkedIn público lista roles de liderazgo en Eco Biosis. Fuente: LinkedIn.",
                    "linkedin": "https://linkedin.com/in/miguelcreixell",
                    "initials": "MC",
                },
            ],
        },
        {
            "match": "ECO INDUSTRIA SAS",
            "slug": "eco-industria",
            "display": "Eco Industria",
            "city_en": "Mosquera",
            "city_es": "Mosquera",
            "problem_en": "Colombian businesses generate growing volumes of electrical, electronic, and hazardous waste that require licensed circular recovery.",
            "problem_es": "Las empresas colombianas generan volúmenes crecientes de residuos eléctricos, electrónicos y peligrosos que requieren recuperación circular licenciada.",
            "images": {
                "hero": "https://ecoindustriasas.com/wp-content/uploads/2026/07/Ecoindustria-Futuro-01-1-scaled.jpg",
                "sections": [
                    "https://ecoindustriasas.com/wp-content/uploads/2026/04/WhatsApp-Image-2026-03-24-at-12.59.46-PM-.jpeg",
                    "https://ecoindustriasas.com/wp-content/uploads/2026/07/Ecoindustria-Soluciones-Circulares01.jpg",
                    "https://ecoindustriasas.com/wp-content/uploads/2026/03/WhatsApp-Image-2026-03-03-at-9.54.01-AM4.jpeg",
                    "https://ecoindustriasas.com/wp-content/uploads/2022/05/19_DESKTOP-5SC3UB1_ago.-19-112058-2021_CaseConflict.jpg",
                ],
                "cta": "https://ecoindustriasas.com/wp-content/uploads/2020/12/165_DESKTOP-5SC3UB1_ago.-19-112021-2021_CaseConflict.jpg",
                "credits": [
                    {"slot": "hero", "source_url": "https://ecoindustriasas.com/", "credit_en": "Eco Industria SAS / ecoindustriasas.com", "credit_es": "Eco Industria SAS / ecoindustriasas.com"},
                    {"slot": "problem", "source_url": "https://ecoindustriasas.com/", "credit_en": "Eco Industria SAS / ecoindustriasas.com", "credit_es": "Eco Industria SAS / ecoindustriasas.com"},
                    {"slot": "solution", "source_url": "https://ecoindustriasas.com/", "credit_en": "Eco Industria SAS / ecoindustriasas.com", "credit_es": "Eco Industria SAS / ecoindustriasas.com"},
                    {"slot": "impact", "source_url": "https://ecoindustriasas.com/", "credit_en": "Eco Industria SAS / ecoindustriasas.com", "credit_es": "Eco Industria SAS / ecoindustriasas.com"},
                    {"slot": "leadership", "source_url": "https://ecoindustriasas.com/", "credit_en": "Eco Industria SAS / ecoindustriasas.com", "credit_es": "Eco Industria SAS / ecoindustriasas.com"},
                    {"slot": "cta", "source_url": "https://ecoindustriasas.com/", "credit_en": "Eco Industria SAS / ecoindustriasas.com", "credit_es": "Eco Industria SAS / ecoindustriasas.com"},
                ],
            },
            "founders": [
                {
                    "name": "Leonardo Rodriguez",
                    "role_en": "CEO &amp; Co-founder &middot; CLAC25",
                    "role_es": "CEO y Cofundador &middot; CLAC25",
                    "bio_en": "Public profile and company materials list CEO and co-founder of Eco Industria SAS. Source: LinkedIn.",
                    "bio_es": "Perfil público y materiales de la empresa listan CEO y cofundador de Eco Industria SAS. Fuente: LinkedIn.",
                    "linkedin": "https://linkedin.com/in/leoempreco",
                    "initials": "LR",
                }
            ],
        },
        {
            "match": "EMBERGY SAS",
            "slug": "embergy",
            "display": "Embergy",
            "city_en": "Bogotá",
            "city_es": "Bogotá",
            "website_override": "https://embergy.com",
            "problem_en": "Industrial waste streams in the Bogotá metropolitan area often lack pathways to circular recovery and material valorization.",
            "problem_es": "Los flujos de residuos industriales en el área metropolitana de Bogotá muchas veces carecen de rutas hacia recuperación circular y valorización de materiales.",
            "images": {
                "hero": u("photo-1466611655691-538065a56d6c"),
                "sections": [
                    u("photo-1513828583688-c52646db9915"),
                    u("photo-1416879595882-3373a0480b5b"),
                    u("photo-1592982530717-36863a0c4e8a"),
                    u("photo-1542601906990-b4d3fb778b09"),
                ],
                "cta": u("photo-1622273270127-59d0754af457"),
                "credits": [
                    {"slot": "hero", "source_url": u("photo-1466611655691-538065a56d6c"), "credit_en": "Unsplash / Noah Buscher", "credit_es": "Unsplash / Noah Buscher"},
                    {"slot": "problem", "source_url": u("photo-1513828583688-c52646db9915"), "credit_en": "Unsplash / Zbynek Burival", "credit_es": "Unsplash / Zbynek Burival"},
                    {"slot": "solution", "source_url": u("photo-1416879595882-3373a0480b5b"), "credit_en": "Unsplash / Markus Spiske", "credit_es": "Unsplash / Markus Spiske"},
                    {"slot": "impact", "source_url": u("photo-1592982530717-36863a0c4e8a"), "credit_en": "Unsplash / American Public Power Association", "credit_es": "Unsplash / American Public Power Association"},
                    {"slot": "leadership", "source_url": u("photo-1542601906990-b4d3fb778b09"), "credit_en": "Unsplash / Noah Buscher", "credit_es": "Unsplash / Noah Buscher"},
                    {"slot": "cta", "source_url": u("photo-1622273270127-59d0754af457"), "credit_en": "Unsplash / Karsten Wurth", "credit_es": "Unsplash / Karsten Wurth"},
                ],
            },
            "founders": [
                {
                    "name": "Alejandro Nuñez",
                    "role_en": "CEO &amp; Founder &middot; CLAC25",
                    "role_es": "CEO y Fundador &middot; CLAC25",
                    "bio_en": "Public LinkedIn lists CEO and founder of Embergy SAS. Source: LinkedIn.",
                    "bio_es": "LinkedIn público lista CEO y fundador de Embergy SAS. Fuente: LinkedIn.",
                    "linkedin": "https://linkedin.com/in/alejandro-nunez-moreno",
                    "initials": "AN",
                }
            ],
        },
        {
            "match": "FLUVIA",
            "slug": "fluvia",
            "display": "Fluvia",
            "city_en": "Bogotá",
            "city_es": "Bogotá",
            "problem_en": "Water bodies used for environmental studies often lack affordable, reliable real-time hydrological data on flows and dispersion.",
            "problem_es": "Los cuerpos de agua estudiados ambientalmente muchas veces carecen de datos hidrológicos confiables en tiempo real sobre caudales y dispersión.",
            "images": {
                "hero": u("photo-1432405972612-c9b87491f1e5"),
                "sections": [
                    u("photo-1441974231531-c6227db76b1e"),
                    u("photo-1545569341-9ebf19f22461"),
                    u("photo-1494500764526-072aa0227a4f"),
                    u("photo-1518837695005-b208969beeb7"),
                ],
                "cta": u("photo-1527482107873-ffed5449620f"),
                "credits": [
                    {"slot": "hero", "source_url": u("photo-1432405972612-c9b87491f1e5"), "credit_en": "Unsplash / David Clode", "credit_es": "Unsplash / David Clode"},
                    {"slot": "problem", "source_url": u("photo-1441974231531-c6227db76b1e"), "credit_en": "Unsplash / Sebastian Unrau", "credit_es": "Unsplash / Sebastian Unrau"},
                    {"slot": "solution", "source_url": u("photo-1545569341-9ebf19f22461"), "credit_en": "Unsplash / Nong", "credit_es": "Unsplash / Nong"},
                    {"slot": "impact", "source_url": u("photo-1494500764526-072aa0227a4f"), "credit_en": "Unsplash / Adrien Olichon", "credit_es": "Unsplash / Adrien Olichon"},
                    {"slot": "leadership", "source_url": u("photo-1518837695005-b208969beeb7"), "credit_en": "Unsplash / Jeremy Bishop", "credit_es": "Unsplash / Jeremy Bishop"},
                    {"slot": "cta", "source_url": u("photo-1527482107873-ffed5449620f"), "credit_en": "Unsplash / Sean O.", "credit_es": "Unsplash / Sean O."},
                ],
            },
            "founders": [
                {
                    "name": "Julian Ramos Santos",
                    "role_en": "CEO &amp; Co-founder &middot; CLAC23",
                    "role_es": "CEO y Cofundador &middot; CLAC23",
                    "bio_en": "Public LinkedIn lists CEO and co-founder of Fluvia SAS. Source: LinkedIn.",
                    "bio_es": "LinkedIn público lista CEO y cofundador de Fluvia SAS. Fuente: LinkedIn.",
                    "linkedin": "https://linkedin.com/in/juliandrs",
                    "initials": "JR",
                },
                {
                    "name": "Alfredo Constaín Aragón",
                    "role_en": "COO &amp; Co-founder &middot; CLAC23",
                    "role_es": "COO y Cofundador &middot; CLAC23",
                    "bio_en": "Public LinkedIn lists COO and co-founder of Fluvia SAS. Source: LinkedIn.",
                    "bio_es": "LinkedIn público lista COO y cofundador de Fluvia SAS. Fuente: LinkedIn.",
                    "linkedin": "https://linkedin.com/in/alfredo-consta%C3%ADn-arag%C3%B3n-304ab649",
                    "initials": "AC",
                },
            ],
        },
    ],
}


def load_portfolio_cards() -> list[dict]:
    text = PORTFOLIO.read_text(encoding="utf-8")
    m = re.search(r"const S=\[(.*?)\];", text, re.S)
    if not m:
        raise SystemExit("Could not parse portfolio cards")
    arr = "[" + m.group(1) + "]"
    cards = []
    for chunk in re.findall(r"\{n:\"[^\"]+\"[^}]+\}", arr):
        d: dict = {}
        for key in ("n", "p", "c", "w", "t", "st", "d", "ds", "ct1", "ct2"):
            m2 = re.search(rf'{key}:"([^"]*)"', chunk)
            if m2:
                d[key] = m2.group(1)
            elif re.search(rf"{key}:null", chunk):
                d[key] = None
        cards.append(d)
    return cards


def find_card(cards: list[dict], name: str) -> dict:
    target = name.upper()
    for c in cards:
        if c.get("n", "").upper() == target:
            return c
    raise KeyError(name)


def taxonomy_text(card: dict) -> tuple[str, str]:
    parts = []
    for key in ("ct1", "ct2"):
        code = card.get(key)
        if code:
            parts.append(CT_LABELS.get(code, code))
    if not parts:
        return "[PENDIENTE]", "[PENDIENTE]"
    joined = " · ".join(parts)
    return joined, joined


def build_json(spec: dict, card: dict, sheet_program: str) -> dict:
    slug = spec["slug"]
    name = spec["display"]
    theme_en, theme_es = THEME.get(card.get("t") or "CE", ("Cleantech", "Cleantech"))
    country = "Colombia" if card.get("c") == "CO" else (card.get("c") or "[PENDIENTE]")
    program = card.get("p") or "[PENDIENTE]"
    stage = card.get("st") or "[PENDIENTE]"
    site = card.get("w") or ""
    website = spec.get("website_override") or (f"https://{site}" if site else "#")
    site_label = site or ("embergy.com" if slug == "embergy" else "[PENDIENTE]")

    pitch_en = card.get("d") or "[PENDIENTE]"
    pitch_es = card.get("ds") or pitch_en
    solution_en = pitch_en
    solution_es = pitch_es

    city_en = spec["city_en"]
    city_es = spec["city_es"]
    loc_en = f"{city_en}, {country}" if city_en != "[PENDIENTE]" else country
    loc_es = f"{city_es}, {country}" if city_es != "[PENDIENTE]" else country

    ct_codes = " · ".join(filter(None, [card.get("ct1"), card.get("ct2")])) or "[PENDIENTE]"
    hero_sub_en = f"{site_label} &middot; {loc_en} &middot; {theme_en} &middot; Stage: {stage} &middot; {ct_codes}"
    hero_sub_es = f"{site_label} &middot; {loc_es} &middot; {theme_es} &middot; Etapa: {stage} &middot; {ct_codes}"

    tax_en, tax_es = taxonomy_text(card)
    imgs = spec["images"]
    section_bgs = imgs["sections"]

    sector_short = {"EN": "Energy", "CE": "Circular", "BIO": "Bio"}.get(card.get("t"), "Cleantech")

    return {
        "slug": slug,
        "name": name,
        "website": website,
        "badge_en": f"{theme_en} &middot; {program}",
        "badge_es": f"{theme_es} &middot; {program}",
        "hero_image": imgs["hero"],
        "cta_bg": imgs["cta"],
        "image_credits": imgs["credits"],
        "hero_sub_en": hero_sub_en,
        "hero_sub_es": hero_sub_es,
        "pitch_en": pitch_en,
        "pitch_es": pitch_es,
        "cta_pitch_en": solution_en[:220],
        "cta_pitch_es": solution_es[:220],
        "cta_btn_en": "Visit website" if website != "#" else "CleantechHUB",
        "cta_btn_es": "Visitar sitio" if website != "#" else "CleantechHUB",
        "ribbon": [
            {
                "val": card.get("c") or "CO",
                "lab_en": "Country",
                "lab_es": "País",
                "sub_en": country,
                "sub_es": country,
            },
            {
                "val": stage[:12],
                "lab_en": "Stage",
                "lab_es": "Etapa",
                "sub_en": program,
                "sub_es": program,
            },
            {
                "val": sector_short,
                "lab_en": "Sector",
                "lab_es": "Sector",
                "sub_en": "Cleantech",
                "sub_es": "Cleantech",
            },
            {
                "val": "[P]",
                "lab_en": "Metrics",
                "lab_es": "Métricas",
                "sub_en": "[PENDIENTE]",
                "sub_es": "[PENDIENTE]",
            },
        ],
        "problem_stats": [
            [
                {"num": program, "lab_en": "Program", "lab_es": "Programa"},
                {"num": "CTH", "lab_en": "Hub", "lab_es": "Hub"},
            ],
            [
                {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
                {"num": card.get("c") or "CO", "lab_en": country, "lab_es": country},
            ],
        ],
        "sections": [
            {
                "num": 1,
                "type": "split",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "The Problem",
                "title_es": "El Problema",
                "head_en": spec["problem_en"],
                "head_es": spec["problem_es"],
                "body_en": spec["problem_en"],
                "body_es": spec["problem_es"],
                "bg": section_bgs[0],
            },
            {
                "num": 2,
                "type": "solution",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "The Solution",
                "title_es": "La Solución",
                "steps": [
                    {
                        "icon": "🎯",
                        "label_en": "Focus",
                        "label_es": "Enfoque",
                        "text_en": solution_en[:180],
                        "text_es": solution_es[:180],
                    },
                    {
                        "icon": "🔗",
                        "label_en": "Program",
                        "label_es": "Programa",
                        "text_en": f"{name} — {program} (CleantechHUB). Cohort: {sheet_program}.",
                        "text_es": f"{name} — {program} (CleantechHUB). Cohorte: {sheet_program}.",
                    },
                    {
                        "icon": "🌎",
                        "label_en": "Market",
                        "label_es": "Mercado",
                        "text_en": f"Based in {loc_en}."
                        + (f" Public site: {site_label}." if site_label != "[PENDIENTE]" else ""),
                        "text_es": f"Con base en {loc_es}."
                        + (f" Sitio público: {site_label}." if site_label != "[PENDIENTE]" else ""),
                    },
                ],
                "bg": section_bgs[1],
            },
            {
                "num": 3,
                "type": "impact",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "Impact & Program",
                "title_es": "Impacto y Programa",
                "cards": [
                    {
                        "icon": "📋",
                        "title_en": "Wiki source",
                        "title_es": "Fuente Wiki",
                        "text_en": "Profile synced from BookStack Startup Portfolio + Odoo (SoT).",
                        "text_es": "Perfil sincronizado desde BookStack Startup Portfolio + Odoo (SoT).",
                    },
                    {
                        "icon": "🎯",
                        "title_en": "Taxonomy",
                        "title_es": "Taxonomía",
                        "text_en": tax_en if tax_en != "[PENDIENTE]" else f"{ct_codes}",
                        "text_es": tax_es if tax_es != "[PENDIENTE]" else f"{ct_codes}",
                    },
                ],
                "bg": section_bgs[2],
            },
            {
                "num": 4,
                "type": "team",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "Leadership",
                "title_es": "Liderazgo",
                "members": spec["founders"],
                "dream_en": f"Program: {program} · {sheet_program}. City: {city_en}. Verified KPIs: [PENDIENTE]. Pitch deck on profile: [PENDIENTE].",
                "dream_es": f"Programa: {program} · {sheet_program}. Ciudad: {city_es}. KPIs verificados: [PENDIENTE]. Pitch deck en perfil: [PENDIENTE].",
                "bg": section_bgs[3],
            },
        ],
    }


def main() -> None:
    batch_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    if batch_idx not in BATCH_SPECS:
        raise SystemExit(f"No specs for batch {batch_idx}")
    if not BATCHES.is_file():
        raise SystemExit(f"Missing {BATCHES}")
    batches = json.loads(BATCHES.read_text())
    batch = batches[batch_idx]
    cards = load_portfolio_cards()
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for row, spec in zip(batch, BATCH_SPECS[batch_idx]):
        card = find_card(cards, spec["match"])
        page = build_json(spec, card, row.get("program") or "Acceleration")
        path = OUT / f"{spec['slug']}.json"
        path.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(spec["slug"])
        print(f"Wrote {path.name}")
    print(json.dumps({"batch": batch_idx, "slugs": written}))


if __name__ == "__main__":
    main()
