#!/usr/bin/env python3
"""Generate portfolio-style /s/ one-pager JSON (sheet batch) and optionally build HTML."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "onepagers" / "data"

SLOW = "https://www.slowreciclaje.com/cdn/shop/files"
TAVI = "https://taviinnova.com/wp-content/uploads/2026/01"
U = lambda pid: f"https://images.unsplash.com/{pid}?w=1200&q=80"

# Per-startup images (hero + 4 sections + CTA). Must be unique across this batch.
STARTUP_IMAGES: dict[str, dict[str, str]] = {
    "suncolombia": {
        "hero": "https://cdn.forbes.co/2023/05/Sun-Colombia-1280x720-1.jpg",
        "problem": U("photo-1497435334942-789819ee7888"),
        "solution": U("photo-1508517748547-fbab89ddf9d9"),
        "impact": U("photo-1581091226825-a6a2a5aee158"),
        "team": U("photo-1621905251189-08cb45d6a269"),
        "cta": U("photo-1613665814317-58a502507d47"),
    },
    "tavi-technology": {
        "hero": f"{TAVI}/Turbina-Hidrica-Home.png",
        "problem": f"{TAVI}/QuienesSomos-BG2-1024x546.png",
        "solution": U("photo-1532601220698-5029272cc54e"),
        "impact": U("photo-1466611653911-950815379e64"),
        "team": f"{TAVI}/Gerente-1.png",
        "cta": U("photo-1548337138-4961de642fff"),
    },
    "valopes": {
        "hero": U("photo-1551288049-bebda4e38f71"),
        "problem": U("photo-1532996122724-e3c031a396bf"),
        "solution": U("photo-1542601906990-b4d3fb778b09"),
        "impact": U("photo-1604187351-d62eae8d5e72"),
        "team": U("photo-1556761175-b413da4d2af6"),
        "cta": U("photo-1454165804606-c3d57bc86b40"),
    },
    "wheelo": {
        "hero": U("photo-1486406146926-c627a92ad1ab"),
        "problem": U("photo-1563986768609-322da13575f3"),
        "solution": U("photo-1517245386807-bb43f82c33c4"),
        "impact": U("photo-1497436073146-47bd4214358c"),
        "team": U("photo-1600880292203-75762f0790e8"),
        "cta": U("photo-1451187580459-43490279c0fa"),
    },
    "tr-global-group": {
        "hero": f"{SLOW}/Banner_SEO.png",
        "problem": f"{SLOW}/BANDEJAIRREGULAR.jpg",
        "solution": f"{SLOW}/florero_Botanic_editorial.jpg",
        "impact": f"{SLOW}/MesadeCentroOrigenNegra.jpg",
        "team": f"{SLOW}/Florero_liso_regenerativo_foto_editorial_blanca.jpg",
        "cta": f"{SLOW}/MOBILIARIO_72311884-2e6a-4bbb-8da3-7fe47c004300.jpg",
    },
}

IMAGE_CREDITS: dict[str, tuple[str, str]] = {
    "suncolombia": (
        "Hero: Forbes Colombia (2023). Sections: Unsplash (solar/rural energy).",
        "Hero: Forbes Colombia (2023). Secciones: Unsplash (energia solar/rural).",
    ),
    "tavi-technology": (
        "Hero/problem/team: taviinnova.com (Tavi Innova, related public brand). Other sections: Unsplash (renewables).",
        "Hero/problema/equipo: taviinnova.com (Tavi Innova, marca publica relacionada). Otras secciones: Unsplash (renovables).",
    ),
    "valopes": (
        "All section photos: Unsplash (industrial data, waste, sustainability).",
        "Fotos de seccion: Unsplash (datos industriales, residuos, sostenibilidad).",
    ),
    "wheelo": (
        "All section photos: Unsplash (cleantech ecosystem / green business). Verified website: [PENDIENTE].",
        "Fotos de seccion: Unsplash (ecosistema cleantech / negocio verde). Sitio web verificado: [PENDIENTE].",
    ),
    "tr-global-group": (
        "All product/brand photos: slowreciclaje.com (SLOW / TR Global Group).",
        "Fotos producto/marca: slowreciclaje.com (SLOW / TR Global Group).",
    ),
}


def _assert_unique_images() -> None:
    seen: dict[str, str] = {}
    for slug, imgs in STARTUP_IMAGES.items():
        for slot, url in imgs.items():
            if url in seen:
                raise ValueError(f"Duplicate image in batch: {url} ({seen[url]} and {slug}.{slot})")
            seen[url] = f"{slug}.{slot}"

CT_LABELS = {
    "CT-EN-001": "Solar PV",
    "CT-EN-002": "Wind Energy",
    "CT-IC-003": "Supply Chain Traceability",
    "CT-WA-003": "Recycling &amp; Materials Recovery",
    "CT-EX-038": "Sustainable Textiles (Wood/Fibre)",
}

THEME = {"EN": ("Energy", "Energia"), "CE": ("Circular", "Circular")}


def portfolio_ribbon(country: str, country_name: str, stage: str, cohort: str, theme: str) -> list:
    sector_en, sector_es = THEME.get(theme, ("Cleantech", "Cleantech"))
    return [
        {
            "val": country,
            "lab_en": "Country",
            "lab_es": "Pais",
            "sub_en": country_name,
            "sub_es": country_name,
        },
        {
            "val": stage[:10],
            "lab_en": "Stage",
            "lab_es": "Etapa",
            "sub_en": cohort,
            "sub_es": cohort,
        },
        {
            "val": sector_en[:10],
            "lab_en": "Sector",
            "lab_es": "Sector",
            "sub_en": "Cleantech",
            "sub_es": "Cleantech",
        },
        {
            "val": "[P]",
            "lab_en": "Metrics",
            "lab_es": "Metricas",
            "sub_en": "[PENDIENTE]",
            "sub_es": "[PENDIENTE]",
        },
    ]


def portfolio_stats(cohort: str, country: str) -> list:
    return [
        [
            {"num": cohort, "lab_en": "Program", "lab_es": "Programa"},
            {"num": "CTH", "lab_en": "Hub", "lab_es": "Hub"},
        ],
        [
            {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
            {"num": country, "lab_en": "Colombia" if country == "CO" else country, "lab_es": "Colombia" if country == "CO" else country},
        ],
    ]


def build_page(
    *,
    slug: str,
    name: str,
    website: str,
    badge_en: str,
    badge_es: str,
    images: dict[str, str],
    image_credits_en: str,
    image_credits_es: str,
    hero_sub_en: str,
    hero_sub_es: str,
    pitch_en: str,
    pitch_es: str,
    problem_en: str,
    problem_es: str,
    solution_en: str,
    solution_es: str,
    program_line_en: str,
    program_line_es: str,
    market_en: str,
    market_es: str,
    taxonomy_en: str,
    taxonomy_es: str,
    ribbon: list,
    problem_stats: list,
    team: list,
    dream_en: str,
    dream_es: str,
    cta_pitch_en: str,
    cta_pitch_es: str,
    cta_btn_en: str = "Visit website",
    cta_btn_es: str = "Visitar sitio",
) -> dict:
    members = []
    for m in team:
        mem = {
            "name": m["name"],
            "role_en": m["role_en"],
            "role_es": m["role_es"],
            "bio_en": m.get("bio_en", ""),
            "bio_es": m.get("bio_es", ""),
            "initials": m.get("initials") or "".join(w[0] for w in m["name"].split()[:2]).upper(),
        }
        if m.get("linkedin"):
            mem["linkedin"] = m["linkedin"]
        members.append(mem)

    return {
        "slug": slug,
        "name": name,
        "website": website,
        "badge_en": badge_en,
        "badge_es": badge_es,
        "hero_image": images["hero"],
        "cta_bg": images["cta"],
        "hero_sub_en": hero_sub_en,
        "hero_sub_es": hero_sub_es,
        "pitch_en": pitch_en,
        "pitch_es": pitch_es,
        "cta_pitch_en": cta_pitch_en,
        "cta_pitch_es": cta_pitch_es,
        "cta_btn_en": cta_btn_en,
        "cta_btn_es": cta_btn_es,
        "ribbon": ribbon,
        "problem_stats": problem_stats,
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
                "bg": images["problem"],
            },
            {
                "num": 2,
                "type": "solution",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "The Solution",
                "title_es": "La Solucion",
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
                        "text_en": program_line_en,
                        "text_es": program_line_es,
                    },
                    {
                        "icon": "🌎",
                        "label_en": "Market",
                        "label_es": "Mercado",
                        "text_en": market_en,
                        "text_es": market_es,
                    },
                ],
                "bg": images["solution"],
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
                        "title_en": "Portfolio source",
                        "title_es": "Fuente portafolio",
                        "text_en": "Profile synced from CleantechHUB Startup Portfolio card and public web sources (Portafolio CTH / Acceleration).",
                        "text_es": "Perfil sincronizado desde tarjeta Startup Portfolio CleantechHUB y fuentes web publicas (Portafolio CTH / Acceleration).",
                    },
                    {
                        "icon": "🎯",
                        "title_en": "Taxonomy",
                        "title_es": "Taxonomia",
                        "text_en": taxonomy_en,
                        "text_es": taxonomy_es,
                    },
                ],
                "bg": images["impact"],
            },
            {
                "num": 4,
                "type": "team",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "Leadership",
                "title_es": "Liderazgo",
                "members": members,
                "dream_en": f"{dream_en} Image credits: {image_credits_en}",
                "dream_es": f"{dream_es} Creditos imagen: {image_credits_es}",
                "bg": images["team"],
            },
        ],
    }


BATCH_12 = [
    build_page(
        slug="suncolombia",
        name="SunColombia",
        website="https://www.suncolombia.co",
        badge_en="Solar PV &middot; CLAC22 &middot; Acceleration",
        badge_es="Solar FV &middot; CLAC22 &middot; Acceleration",
        images=STARTUP_IMAGES["suncolombia"],
        image_credits_en=IMAGE_CREDITS["suncolombia"][0],
        image_credits_es=IMAGE_CREDITS["suncolombia"][1],
        hero_sub_en="suncolombia.co &middot; Colombia &middot; Bogota &middot; Energy &middot; Stage: Series B+",
        hero_sub_es="suncolombia.co &middot; Colombia &middot; Bogota &middot; Energia &middot; Etapa: Series B+",
        pitch_en="Deploys off-grid and on-grid solar systems for rural communities, schools, and telecom towers across Colombia.",
        pitch_es="Despliega sistemas solares fuera y dentro de la red para comunidades rurales, escuelas y torres de telecomunicaciones en Colombia.",
        problem_en="Remote Colombian communities and critical infrastructure often lack reliable grid electricity and bundled essential services (water, connectivity, education).",
        problem_es="Comunidades remotas e infraestructura critica en Colombia a menudo carecen de electricidad confiable de red y servicios esenciales integrados (agua, conectividad, educacion).",
        solution_en="Hybrid solar and storage projects plus modular solar schools and water systems for off-grid and on-grid clients.",
        solution_es="Proyectos solares hibridos con almacenamiento, aulas solares modulares y sistemas de agua para clientes fuera y dentro de la red.",
        program_line_en="SunColombia (SUNCOLOMBIA SAS) — CLAC22 cohort and CTH Acceleration (Portafolio CTH).",
        program_line_es="SunColombia (SUNCOLOMBIA SAS) — cohorte CLAC22 y Acceleration CTH (Portafolio CTH).",
        market_en="Colombia; public site: suncolombia.co. HQ: Bogota (Usaquen).",
        market_es="Colombia; sitio publico: suncolombia.co. Sede: Bogota (Usaquen).",
        taxonomy_en="CT-EN-001 &middot; Solar PV",
        taxonomy_es="CT-EN-001 &middot; Solar FV",
        ribbon=portfolio_ribbon("CO", "Colombia", "Series B+", "CLAC22", "EN"),
        problem_stats=portfolio_stats("CLAC22", "CO"),
        team=[
            {
                "name": "Juan Diego Gomez",
                "role_en": "Co-founder &middot; SunColombia",
                "role_es": "Cofundador &middot; SunColombia",
                "bio_en": "Public-facing co-founder role. Source: Forbes Colombia (2023), SunColombia site, LinkedIn.",
                "bio_es": "Rol publico de cofundador. Fuente: Forbes Colombia (2023), sitio SunColombia, LinkedIn.",
                "linkedin": "https://www.linkedin.com/in/juan-diego-gomez-10270518",
            },
            {
                "name": "Mauricio Hoyos Holguin",
                "role_en": "Co-founder &amp; board &middot; SunColombia",
                "role_es": "Cofundador y junta &middot; SunColombia",
                "bio_en": "Co-founder and board leadership. Source: Forbes Colombia, SEAF, LinkedIn.",
                "bio_es": "Cofundador y liderazgo de junta. Fuente: Forbes Colombia, SEAF, LinkedIn.",
                "linkedin": "https://www.linkedin.com/in/mauriciohoyosholguin",
            },
        ],
        dream_en="Program: CLAC22 + CTH Acceleration. City: Bogota. Verified KPIs on profile: [PENDIENTE]. Pitch deck: [PENDIENTE].",
        dream_es="Programa: CLAC22 + Acceleration CTH. Ciudad: Bogota. KPIs verificados en perfil: [PENDIENTE]. Pitch deck: [PENDIENTE].",
        cta_pitch_en="Solar energy as a platform for rural development, education, and water access across Colombia.",
        cta_pitch_es="Energia solar como plataforma para desarrollo rural, educacion y acceso al agua en Colombia.",
    ),
    build_page(
        slug="tavi-technology",
        name="TAVI Technology",
        website="https://tavitechnology.com.co",
        badge_en="Wind Energy &middot; CLAC21 &middot; Acceleration",
        badge_es="Energia Eolica &middot; CLAC21 &middot; Acceleration",
        images=STARTUP_IMAGES["tavi-technology"],
        image_credits_en=IMAGE_CREDITS["tavi-technology"][0],
        image_credits_es=IMAGE_CREDITS["tavi-technology"][1],
        hero_sub_en="tavitechnology.com.co &middot; Colombia &middot; Cali &middot; Energy &middot; Stage: Seed",
        hero_sub_es="tavitechnology.com.co &middot; Colombia &middot; Cali &middot; Energia &middot; Etapa: Seed",
        pitch_en="Designs and manufactures unconventional energy generators enabling sustainable self-generation for urban and rural Colombian communities, with a local innovation patent.",
        pitch_es="Disena y fabrica generadores de energia no convencionales que permiten la autogeneracion sostenible para comunidades urbanas y rurales colombianas, con patente de innovacion local.",
        problem_en="Urban and rural sites need affordable on-site renewable generation where conventional grid extension or standard turbines are not viable.",
        problem_es="Sitios urbanos y rurales necesitan generacion renovable local asequible donde la extension de red o turbinas convencionales no son viables.",
        solution_en="Patented high-efficiency generators and hybrid hydro/wind kits with local installation and maintenance services.",
        solution_es="Generadores de alta eficiencia patentados y kits hibridos hidro/eolicos con servicios locales de instalacion y mantenimiento.",
        program_line_en="TAVI Technology — CLAC21 cohort and CTH Acceleration (Portafolio CTH).",
        program_line_es="TAVI Technology — cohorte CLAC21 y Acceleration CTH (Portafolio CTH).",
        market_en="Based in Cali, Valle del Cauca. Public site: tavitechnology.com.co.",
        market_es="Con base en Cali, Valle del Cauca. Sitio publico: tavitechnology.com.co.",
        taxonomy_en="CT-EN-002 &middot; Wind Energy",
        taxonomy_es="CT-EN-002 &middot; Energia Eolica",
        ribbon=portfolio_ribbon("CO", "Colombia", "Seed", "CLAC21", "EN"),
        problem_stats=portfolio_stats("CLAC21", "CO"),
        team=[
            {
                "name": "Alonso Landazury Sanclemente",
                "role_en": "Founder &middot; TAVI / Tavi Innova",
                "role_es": "Fundador &middot; TAVI / Tavi Innova",
                "bio_en": "Listed as founder on Tavi Innova public site. Public LinkedIn profile: [PENDIENTE].",
                "bio_es": "Figura como fundador en sitio publico Tavi Innova. Perfil publico LinkedIn: [PENDIENTE].",
            },
        ],
        dream_en="Program: CLAC21 + CTH Acceleration. City: Cali. Founder LinkedIn: [PENDIENTE]. Verified KPIs: [PENDIENTE].",
        dream_es="Programa: CLAC21 + Acceleration CTH. Ciudad: Cali. LinkedIn fundador: [PENDIENTE]. KPIs verificados: [PENDIENTE].",
        cta_pitch_en="Colombian-made unconventional generators for distributed renewable self-generation.",
        cta_pitch_es="Generadores no convencionales hechos en Colombia para autogeneracion renovable distribuida.",
    ),
    build_page(
        slug="valopes",
        name="Valopes",
        website="https://www.valopes.com",
        badge_en="Circular &middot; CLAC22 &middot; Acceleration",
        badge_es="Circular &middot; CLAC22 &middot; Acceleration",
        images=STARTUP_IMAGES["valopes"],
        image_credits_en=IMAGE_CREDITS["valopes"][0],
        image_credits_es=IMAGE_CREDITS["valopes"][1],
        hero_sub_en="valopes.com &middot; Colombia &middot; Bogota &middot; Circular Economy &middot; Stage: Seed",
        hero_sub_es="valopes.com &middot; Colombia &middot; Bogota &middot; Economia Circular &middot; Etapa: Seed",
        pitch_en="Cloud-based waste traceability platform helping companies in Colombia, Chile, and Mexico digitize waste streams and automate regulatory compliance reporting.",
        pitch_es="Plataforma de trazabilidad de residuos en la nube que ayuda a empresas en Colombia, Chile y Mexico a digitalizar flujos de residuos y automatizar reportes de cumplimiento regulatorio.",
        problem_en="Industrial operators struggle to centralize water, energy, waste, and emissions data for compliance and operational decisions.",
        problem_es="Operadores industriales luchan por centralizar datos de agua, energia, residuos y emisiones para cumplimiento y decisiones operativas.",
        solution_en="SaaS climate-governance infrastructure to capture, trace, and report environmental flows across sites.",
        solution_es="Infraestructura SaaS de gobernanza climatica para capturar, trazar y reportar flujos ambientales entre sitios.",
        program_line_en="Valopes — CLAC22 cohort and CTH Acceleration (Portafolio CTH).",
        program_line_es="Valopes — cohorte CLAC22 y Acceleration CTH (Portafolio CTH).",
        market_en="Colombia, Chile, and Mexico; public site: valopes.com. Presence: Bogota.",
        market_es="Colombia, Chile y Mexico; sitio publico: valopes.com. Presencia: Bogota.",
        taxonomy_en="CT-IC-003 &middot; Supply Chain Traceability; CT-WA-003 &middot; Recycling &amp; Materials Recovery",
        taxonomy_es="CT-IC-003 &middot; Trazabilidad de cadena; CT-WA-003 &middot; Reciclaje y valorizacion",
        ribbon=portfolio_ribbon("CO", "Colombia", "Seed", "CLAC22", "CE"),
        problem_stats=portfolio_stats("CLAC22", "CO"),
        team=[
            {
                "name": "Octavio Torres Quintana",
                "role_en": "Co-founder &amp; CEO &middot; Valopes",
                "role_es": "Cofundador y CEO &middot; Valopes",
                "bio_en": "Public-facing CEO role. Source: valopes.com, LinkedIn.",
                "bio_es": "Rol publico de CEO. Fuente: valopes.com, LinkedIn.",
                "linkedin": "https://www.linkedin.com/in/octaviotorresq",
            },
        ],
        dream_en="Program: CLAC22 + CTH Acceleration. City: Bogota. Verified KPIs on profile: [PENDIENTE].",
        dream_es="Programa: CLAC22 + Acceleration CTH. Ciudad: Bogota. KPIs verificados en perfil: [PENDIENTE].",
        cta_pitch_en="Turn dispersed environmental data into operational and compliance intelligence for industry.",
        cta_pitch_es="Convierte datos ambientales dispersos en inteligencia operativa y de cumplimiento para la industria.",
    ),
    build_page(
        slug="wheelo",
        name="Wheelo",
        website="#",
        badge_en="Cleantech Ecosystem &middot; Acceleration",
        badge_es="Ecosistema Cleantech &middot; Acceleration",
        images=STARTUP_IMAGES["wheelo"],
        image_credits_en=IMAGE_CREDITS["wheelo"][0],
        image_credits_es=IMAGE_CREDITS["wheelo"][1],
        hero_sub_en="[PENDIENTE] &middot; Colombia &middot; Medellin &middot; Cleantech &middot; Stage: [PENDIENTE]",
        hero_sub_es="[PENDIENTE] &middot; Colombia &middot; Medellin &middot; Cleantech &middot; Etapa: [PENDIENTE]",
        pitch_en="Sustainability cloud platform mapping and segmenting CleanTech, ClimateTech, and DeepTech startups across circular economy, mobility, and green energy themes.",
        pitch_es="Plataforma cloud de sostenibilidad que mapea y segmenta startups CleanTech, ClimateTech y DeepTech en economia circular, movilidad y energia verde.",
        problem_en="Founders, corporates, and investors lack a structured map of climate startups and segments across Latin America.",
        problem_es="Fundadores, corporativos e inversionistas carecen de un mapa estructurado de startups climaticas y segmentos en America Latina.",
        solution_en="Wheelo (#SaveInGreen) builds a sustainability cloud to discover, categorize, and connect cleantech ventures.",
        solution_es="Wheelo (#SaveInGreen) construye una nube de sostenibilidad para descubrir, categorizar y conectar ventures cleantech.",
        program_line_en="Wheelo — CTH Acceleration (Portafolio CTH).",
        program_line_es="Wheelo — Acceleration CTH (Portafolio CTH).",
        market_en="Based in Medellin, Antioquia. Verified public website: [PENDIENTE].",
        market_es="Con base en Medellin, Antioquia. Sitio web publico verificado: [PENDIENTE].",
        taxonomy_en="CT taxonomy: [PENDIENTE]",
        taxonomy_es="Taxonomia CT: [PENDIENTE]",
        ribbon=portfolio_ribbon("CO", "Colombia", "[P]", "Accel.", "CE"),
        problem_stats=portfolio_stats("Accel.", "CO"),
        team=[
            {
                "name": "Mario Alejandro Muneton Durango",
                "role_en": "Co-founder &amp; CEO &middot; Wheelo",
                "role_es": "Cofundador y CEO &middot; Wheelo",
                "bio_en": "Public-facing CEO role. Source: LinkedIn company profile and founder LinkedIn.",
                "bio_es": "Rol publico de CEO. Fuente: perfil LinkedIn de la empresa y fundador.",
                "linkedin": "https://www.linkedin.com/in/mario-alejandro-mu%C3%B1et%C3%B3n-durango-93b3511b4",
            },
        ],
        dream_en="Program: CTH Acceleration. City: Medellin. Website: [PENDIENTE]. CT taxonomy: [PENDIENTE]. Verified KPIs: [PENDIENTE].",
        dream_es="Programa: Acceleration CTH. Ciudad: Medellin. Sitio web: [PENDIENTE]. Taxonomia CT: [PENDIENTE]. KPIs verificados: [PENDIENTE].",
        cta_pitch_en="Mapping the cleantech startup ecosystem to accelerate climate innovation discovery.",
        cta_pitch_es="Mapeo del ecosistema de startups cleantech para acelerar el descubrimiento de innovacion climatica.",
        cta_btn_en="CleantechHUB",
        cta_btn_es="CleantechHUB",
    ),
    build_page(
        slug="tr-global-group",
        name="TR Global Group",
        website="https://www.slowreciclaje.com",
        badge_en="Textile Circularity &middot; Acceleration",
        badge_es="Circularidad Textil &middot; Acceleration",
        images=STARTUP_IMAGES["tr-global-group"],
        image_credits_en=IMAGE_CREDITS["tr-global-group"][0],
        image_credits_es=IMAGE_CREDITS["tr-global-group"][1],
        hero_sub_en="slowreciclaje.com &middot; Colombia &middot; Medellin &middot; Circular Economy &middot; Stage: [PENDIENTE]",
        hero_sub_es="slowreciclaje.com &middot; Colombia &middot; Medellin &middot; Economia Circular &middot; Etapa: [PENDIENTE]",
        pitch_en="Operates SLOW, collecting and transforming post-consumer and post-industrial textile waste into reusable materials for fashion, furniture, and design.",
        pitch_es="Opera SLOW, recolectando y transformando residuos textiles posconsumo e industriales en materiales reutilizables para moda, mobiliario y diseno.",
        problem_en="Textile waste from production and post-consumer streams often ends in landfill instead of productive reuse loops.",
        problem_es="Residuos textiles de produccion y posconsumo a menudo terminan en relleno en lugar de bucles productivos de reutilizacion.",
        solution_en="SLOW service: collection, sorting, traceability, and material products for architecture, interiors, and brands.",
        solution_es="Servicio SLOW: recoleccion, clasificacion, trazabilidad y productos de material para arquitectura, interiores y marcas.",
        program_line_en="TR GLOBAL GROUP SAS — CTH Acceleration (Portafolio CTH) and REIN Hubs ecosystem.",
        program_line_es="TR GLOBAL GROUP SAS — Acceleration CTH (Portafolio CTH) y ecosistema REIN Hubs.",
        market_en="Medellin, Colombia. Public brand site: slowreciclaje.com.",
        market_es="Medellin, Colombia. Sitio publico de marca: slowreciclaje.com.",
        taxonomy_en="CT-WA-003 &middot; Recycling &amp; Materials Recovery; textile circularity (CT-EX-038 candidate)",
        taxonomy_es="CT-WA-003 &middot; Reciclaje y valorizacion; circularidad textil (candidato CT-EX-038)",
        ribbon=portfolio_ribbon("CO", "Colombia", "[P]", "Accel.", "CE"),
        problem_stats=portfolio_stats("Accel.", "CO"),
        team=[
            {
                "name": "Vanessa Baez Morales",
                "role_en": "CEO &amp; Co-founder &middot; SLOW / TR Global Group",
                "role_es": "CEO y Cofundadora &middot; SLOW / TR Global Group",
                "bio_en": "Public-facing CEO role for SLOW textile recovery. Source: slowreciclaje.com, REIN Hubs press, LinkedIn.",
                "bio_es": "Rol publico de CEO de recuperacion textil SLOW. Fuente: slowreciclaje.com, prensa REIN Hubs, LinkedIn.",
                "linkedin": "https://www.linkedin.com/in/vanessa-baez-morales",
            },
        ],
        dream_en="Program: CTH Acceleration + REIN Hubs. City: Medellin. Stage on card: [PENDIENTE]. Verified KPIs: [PENDIENTE].",
        dream_es="Programa: Acceleration CTH + REIN Hubs. Ciudad: Medellin. Etapa en tarjeta: [PENDIENTE]. KPIs verificados: [PENDIENTE].",
        cta_pitch_en="Regenerative textile materials with traceability for architecture and design projects.",
        cta_pitch_es="Materiales textiles regenerativos con trazabilidad para proyectos de arquitectura y diseno.",
    ),
]


def main() -> None:
    batch_index = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    if batch_index != 12:
        raise SystemExit(f"This script only implements batch 12; got {batch_index}")
    _assert_unique_images()
    slugs = []
    for page in BATCH_12:
        path = OUT / f"{page['slug']}.json"
        path.write_text(json.dumps(page, indent=2, ensure_ascii=False) + "\n")
        slugs.append(page["slug"])
        print(f"Wrote {path.name}")
    if "--build" in sys.argv:
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts" / "build_onepagers.py"), *slugs],
            cwd=str(ROOT),
        )


if __name__ == "__main__":
    main()
