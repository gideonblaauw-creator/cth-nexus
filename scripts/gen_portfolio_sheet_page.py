#!/usr/bin/env python3
"""Generate portfolio-style onepager JSON (xiclo/cirkula layout) from startup metadata."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "onepagers" / "data"

CT_LABELS = {
    "CT-WA-002": "Organic Waste & Composting",
    "CT-AF-009": "Bioeconomy & NbS",
    "CT-WA-003": "Recycling & Materials Recovery",
    "CT-IC-003": "Supply Chain Traceability",
}

THEME = {
    "CE": ("Circular Economy", "Economía circular", "Circular", "Circular"),
    "EN": ("Energy", "Energía", "Energy", "Energía"),
    "BIO": ("Bioeconomy", "Bioeconomía", "Bio", "Bio"),
}

UNSPLASH = {
    "CE": "https://images.unsplash.com/photo-1532996122724-e3c031a396bf?w=1200&q=80",
    "EN": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
    "BIO": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80",
}


def taxonomy_blurb(ct1: str | None, ct2: str | None) -> tuple[str, str]:
    parts = []
    for c in (ct1, ct2):
        if c and c in CT_LABELS:
            parts.append(CT_LABELS[c])
    if not parts:
        return "[PENDIENTE]", "[PENDIENTE]"
    text = " · ".join(parts)
    return text, text


def hero_line(website: str | None, city: str, theme: str, stage: str, ct1: str | None) -> tuple[str, str]:
    theme_en, theme_es, _, _ = THEME[theme]
    site = website or "[PENDIENTE]"
    ct = ct1 or "[PENDIENTE]"
    en = f"{site} &middot; Colombia &middot; {city} &middot; {theme_en} &middot; Stage: {stage} &middot; {ct}"
    es = f"{site} &middot; Colombia &middot; {city} &middot; {theme_es} &middot; Etapa: {stage} &middot; {ct}"
    return en, es


def portfolio_page(
    *,
    slug: str,
    name: str,
    website: str | None,
    city: str,
    program: str,
    theme: str,
    stage: str,
    pitch_en: str,
    pitch_es: str,
    problem_en: str,
    problem_es: str,
    solution_en: str,
    solution_es: str,
    ct1: str | None,
    ct2: str | None,
    members: list[dict],
    hero_image: str | None = None,
) -> dict:
    theme_en, theme_es, ribbon_sector_en, ribbon_sector_es = THEME[theme]
    tax_en, tax_es = taxonomy_blurb(ct1, ct2)
    hero_sub_en, hero_sub_es = hero_line(website, city, theme, stage, ct1)
    badge_en = f"{theme_en} &middot; {program}"
    badge_es = f"{theme_es} &middot; {program}"
    web_href = f"https://{website}" if website else "#"
    cta_btn_en = website or "CleantechHUB"
    cta_btn_es = website or "CleantechHUB"
    bg = hero_image or UNSPLASH[theme]
    market_en = (
        f"Based in Colombia ({city}). Public site: {website}."
        if website
        else f"Based in Colombia ({city}). Verified website: [PENDIENTE]."
    )
    market_es = (
        f"Con base en Colombia ({city}). Sitio público: {website}."
        if website
        else f"Con base en Colombia ({city}). Sitio web verificado: [PENDIENTE]."
    )
    ct_ribbon = ct1 or "[P]"
    return {
        "slug": slug,
        "name": name,
        "website": web_href,
        "badge_en": badge_en,
        "badge_es": badge_es,
        "hero_image": bg,
        "hero_sub_en": hero_sub_en,
        "hero_sub_es": hero_sub_es,
        "pitch_en": pitch_en,
        "pitch_es": pitch_es,
        "cta_pitch_en": solution_en,
        "cta_pitch_es": solution_es,
        "cta_btn_en": cta_btn_en,
        "cta_btn_es": cta_btn_es,
        "ribbon": [
            {
                "val": "CO",
                "lab_en": "Country",
                "lab_es": "País",
                "sub_en": "Colombia",
                "sub_es": "Colombia",
            },
            {
                "val": stage,
                "lab_en": "Stage",
                "lab_es": "Etapa",
                "sub_en": program,
                "sub_es": program,
            },
            {
                "val": ribbon_sector_en,
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
                {"num": "CO", "lab_en": "Colombia", "lab_es": "Colombia"},
            ],
        ],
        "sections": [
            {
                "num": 1,
                "type": "split",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "The Problem",
                "title_es": "El Problema",
                "head_en": problem_en,
                "head_es": problem_es,
                "body_en": problem_en,
                "body_es": problem_es,
                "bg": bg,
            },
            {
                "num": 2,
                "type": "solution",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "The Solution",
                "title_es": "La Solución",
                "steps": [
                    {
                        "icon": "🌱",
                        "label_en": "Focus",
                        "label_es": "Enfoque",
                        "text_en": solution_en,
                        "text_es": solution_es,
                    },
                    {
                        "icon": "🔗",
                        "label_en": "Program",
                        "label_es": "Programa",
                        "text_en": f"{name} — {program} (CleantechHUB).",
                        "text_es": f"{name} — {program} (CleantechHUB).",
                    },
                    {
                        "icon": "🌎",
                        "label_en": "Market",
                        "label_es": "Mercado",
                        "text_en": market_en,
                        "text_es": market_es,
                    },
                ],
                "bg": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200&q=80",
            },
            {
                "num": 3,
                "type": "impact",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "Impact &amp; Program",
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
                        "text_en": tax_en if ct1 else "[PENDIENTE]",
                        "text_es": tax_es if ct1 else "[PENDIENTE]",
                    },
                ],
                "bg": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
            },
            {
                "num": 4,
                "type": "team",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "Leadership",
                "title_es": "Liderazgo",
                "members": members,
                "dream_en": f"Program: {program}. CT taxonomy: {ct_ribbon}. Verified KPIs: [PENDIENTE].",
                "dream_es": f"Programa: {program}. Taxonomía CT: {ct_ribbon}. KPIs verificados: [PENDIENTE].",
                "bg": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1200&q=80",
            },
        ],
    }


STARTUPS = [
    portfolio_page(
        slug="plasfacol",
        name="Plasfacol",
        website="eco-tienda-plasfacol.venndelo.com",
        city="Cali",
        program="CLAC25",
        theme="CE",
        stage="Pre-Seed",
        pitch_en="Manufactures or recycles plastic materials, developing circular solutions for plastic waste recovery and transformation into reusable industrial inputs.",
        pitch_es="Fabrica o recicla materiales plásticos, desarrollando soluciones circulares para la recuperación y transformación de residuos plásticos en insumos industriales reutilizables.",
        problem_en="Plastic waste from appliances, electronics, and packaging lacks circular recovery paths, driving landfill pressure and lost material value in Colombia.",
        problem_es="Los residuos plásticos de electrodomésticos, electrónica y empaques carecen de rutas circulares de recuperación, aumentando la presión sobre rellenos y la pérdida de valor material en Colombia.",
        solution_en="Plasfacol repurposes plastic waste from air conditioners, TVs, and bottle caps into functional products for large-format digital printing and household use.",
        solution_es="Plasfacol reutiliza residuos plásticos de aires acondicionados, televisores y tapas de botellas en productos funcionales para impresión digital a gran formato y uso en el hogar.",
        ct1=None,
        ct2=None,
        members=[
            {
                "name": "Jeison Rodriguez",
                "role_en": "Founder &middot; CLAC25",
                "role_es": "Fundador &middot; CLAC25",
                "bio_en": "Public-facing founder of Plasfacol (Cali). Source: public community introduction.",
                "bio_es": "Fundador público de Plasfacol (Cali). Fuente: presentación pública en comunidad.",
                "initials": "JR",
            }
        ],
        hero_image="https://images.unsplash.com/photo-1611280048847-d352f4e42d3e?w=1200&q=80",
    ),
    portfolio_page(
        slug="pleia",
        name="PLEIA",
        website="pleia.co",
        city="Medellín",
        program="CLAC24",
        theme="BIO",
        stage="Seed",
        pitch_en="B Corp pioneering biotechnology-based pet funeral services, transforming pet remains into nutrient-rich compost and planting trees at reforestation centers across Colombia.",
        pitch_es="B Corp pionera en servicios funerarios para mascotas basados en biotecnología, transformando los restos en compost rico en nutrientes y plantando árboles en centros de reforestación.",
        problem_en="Traditional pet disposal (cremation or burial) generates emissions, contamination risks, or legal barriers, limiting sustainable end-of-life options for companion animals.",
        problem_es="La disposición tradicional de mascotas (cremación o entierro) genera emisiones, riesgos de contaminación o barreras legales, limitando opciones sostenibles al final de su vida.",
        solution_en="PLEIA offers natural pet farewells through biotechnology-based composting, returning nutrients to soil and memorial gardens across Medellín and Bogotá.",
        solution_es="PLEIA ofrece despedidas naturales para mascotas mediante compostaje biotecnológico, devolviendo nutrientes al suelo y jardines conmemorativos en Medellín y Bogotá.",
        ct1="CT-WA-002",
        ct2="CT-AF-009",
        members=[
            {
                "name": "Melissa Naranjo Hoyos",
                "role_en": "CEO &amp; Founder &middot; CLAC24",
                "role_es": "CEO y Fundadora &middot; CLAC24",
                "bio_en": "Veterinarian and CEO of PLEIA. Public LinkedIn profile.",
                "bio_es": "Médica veterinaria y CEO de PLEIA. Perfil público en LinkedIn.",
                "initials": "MN",
                "linkedin": "https://www.linkedin.com/in/melissa-naranjo-hoyos-43a239202",
            },
            {
                "name": "Daniel Correa Jaramillo",
                "role_en": "Chief Growth Officer &middot; CLAC24",
                "role_es": "Chief Growth Officer &middot; CLAC24",
                "bio_en": "Co-founder and growth lead at PLEIA. Public LinkedIn profile.",
                "bio_es": "Cofundador y líder de crecimiento en PLEIA. Perfil público en LinkedIn.",
                "initials": "DC",
                "linkedin": "https://www.linkedin.com/in/daniel-correa-jaramillo-3304a5168",
            },
        ],
    ),
    portfolio_page(
        slug="purest-fuels",
        name="PUREST FUELS",
        website="purestfuels.com",
        city="Cali",
        program="CLAC23",
        theme="EN",
        stage="Pre-Seed",
        pitch_en="Develops hydrogen injection systems for diesel engines using surplus energy and water to produce low-emission hydrogen, reducing CO₂ and fuel consumption.",
        pitch_es="Desarrolla sistemas de inyección de hidrógeno para motores diésel que usan energía excedente y agua para producir hidrógeno de bajas emisiones, reduciendo CO₂ y consumo de combustible.",
        problem_en="Diesel and gasoline engines remain major sources of fuel waste, CO₂ emissions, and air pollution across industrial, transport, and marine applications in Latin America.",
        problem_es="Los motores diésel y gasolina siguen siendo fuentes importantes de desperdicio de combustible, emisiones de CO₂ y contaminación del aire en aplicaciones industriales, de transporte y marinas en América Latina.",
        solution_en="Purest Fuels systems use surplus machinery energy and water to produce hydrogen on demand, injected into engines to improve combustion, save fuel, and cut CO₂.",
        solution_es="Los sistemas Purest Fuels usan energía excedente de maquinaria y agua para producir hidrógeno bajo demanda, inyectado en motores para mejorar la combustión, ahorrar combustible y reducir CO₂.",
        ct1=None,
        ct2=None,
        members=[
            {
                "name": "María del Socorro Aguirre",
                "role_en": "President &amp; Co-founder &middot; CLAC23",
                "role_es": "Presidenta y Cofundadora &middot; CLAC23",
                "bio_en": "Co-founder leading Purest Fuels in Cali. Public LinkedIn profile.",
                "bio_es": "Cofundadora que lidera Purest Fuels en Cali. Perfil público en LinkedIn.",
                "initials": "MA",
                "linkedin": "https://www.linkedin.com/in/mar%C3%ADa-del-socorro-aguirre-3051461b4",
            },
            {
                "name": "Carlos Lora",
                "role_en": "Principal CEO &middot; CLAC23",
                "role_es": "CEO Principal &middot; CLAC23",
                "bio_en": "Executive lead for Purest Fuels hydrogen combustion systems. Public LinkedIn profile.",
                "bio_es": "Líder ejecutivo de los sistemas de combustión con hidrógeno de Purest Fuels. Perfil público en LinkedIn.",
                "initials": "CL",
                "linkedin": "https://www.linkedin.com/in/carlos-lora-4831311b5",
            },
        ],
    ),
    portfolio_page(
        slug="kelab",
        name="R&amp;R Kelab",
        website="kelab.com.co",
        city="Bogotá",
        program="Acceleration",
        theme="CE",
        stage="[PENDIENTE]",
        pitch_en="Environmental consultancy delivering circular-economy strategy, packaging-waste compliance (Clean Pack), and the Co-Workers Cloud digital marketplace for recoverable materials.",
        pitch_es="Consultoría ambiental que ofrece estrategia de economía circular, cumplimiento en envases y empaques (Clean Pack) y el marketplace digital Co-Workers Cloud para materiales aprovechables.",
        problem_en="Industries in Colombia face complex environmental permitting, packaging-waste obligations, and fragmented markets for recoverable materials.",
        problem_es="Las industrias en Colombia enfrentan permisos ambientales complejos, obligaciones de envases y empaques y mercados fragmentados para materiales aprovechables.",
        solution_en="R&amp;R Kelab integrates regulatory consulting, collective packaging plans, and Co-Workers Cloud to connect waste generators, recyclers, and services in one circular platform.",
        solution_es="R&amp;R Kelab integra consultoría regulatoria, planes colectivos de envases y Co-Workers Cloud para conectar generadores, recicladores y servicios en una plataforma circular.",
        ct1=None,
        ct2=None,
        members=[
            {
                "name": "Mario Antonio Ruiz-Vargas",
                "role_en": "CEO &amp; Founder &middot; CleantechHUB Acceleration",
                "role_es": "CEO y Fundador &middot; Aceleración CleantechHUB",
                "bio_en": "Founder and general manager of R&amp;R Kelab S.A.S. Public LinkedIn profile.",
                "bio_es": "Fundador y gerente general de R&amp;R Kelab S.A.S. Perfil público en LinkedIn.",
                "initials": "MR",
                "linkedin": "https://www.linkedin.com/in/phd-c-mario-antonio-ruiz-vargas-b494aa33",
            }
        ],
    ),
    portfolio_page(
        slug="simbiotic",
        name="Simbiotic",
        website="redsimbiotic.com",
        city="Chía",
        program="CLAC22",
        theme="CE",
        stage="Seed",
        pitch_en="Sustainability consultancy connecting businesses with certified waste networks, and developing a platform for regenerative tourism destination management in Colombia.",
        pitch_es="Consultora de sostenibilidad que conecta empresas con redes certificadas de gestión de residuos, y desarrolla una plataforma para la gestión de destinos de turismo regenerativo.",
        problem_en="Companies and tourism destinations lack integrated tools to manage waste responsibly and measure sustainability performance across value chains.",
        problem_es="Las empresas y destinos turísticos carecen de herramientas integradas para gestionar residuos responsablemente y medir desempeño de sostenibilidad en cadenas de valor.",
        solution_en="Simbiotic connects clients with certified waste networks and builds digital platforms (including ADN Sostenible and Triply) for regenerative tourism destination management.",
        solution_es="Simbiotic conecta clientes con redes certificadas de residuos y construye plataformas digitales (incluidas ADN Sostenible y Triply) para gestión de destinos de turismo regenerativo.",
        ct1="CT-WA-003",
        ct2="CT-IC-003",
        members=[
            {
                "name": "Paola Bravo Villacís",
                "role_en": "CEO &amp; Co-founder &middot; CLAC22",
                "role_es": "CEO y Cofundadora &middot; CLAC22",
                "bio_en": "CEO and co-founder of Simbiotic S.A.S. Public LinkedIn profile.",
                "bio_es": "CEO y cofundadora de Simbiotic S.A.S. Perfil público en LinkedIn.",
                "initials": "PB",
                "linkedin": "https://www.linkedin.com/in/paobv11",
            },
            {
                "name": "Jorge Sandoval H.",
                "role_en": "CMO &amp; R&amp;D Co-founder &middot; CLAC22",
                "role_es": "CMO y Cofundador I+D &middot; CLAC22",
                "bio_en": "Co-founder leading innovation and marketing at Simbiotic. Public LinkedIn profile.",
                "bio_es": "Cofundador que lidera innovación y marketing en Simbiotic. Perfil público en LinkedIn.",
                "initials": "JS",
                "linkedin": "https://www.linkedin.com/in/jorgesimbiotic",
            },
        ],
    ),
]


def main() -> None:
    for page in STARTUPS:
        path = OUT / f"{page['slug']}.json"
        path.write_text(json.dumps(page, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
