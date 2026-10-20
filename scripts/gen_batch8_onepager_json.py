#!/usr/bin/env python3
"""Generate onepager JSON for sheet-s-pages batch 8 (portfolio-sync layout)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "onepagers" / "data"


def u(photo_id: str, photographer: str) -> dict:
    """Unsplash image with attribution (sector-appropriate fallback)."""
    return {
        "url": f"https://images.unsplash.com/{photo_id}?w=1200&q=80",
        "credit_en": f"Unsplash / {photographer}",
        "credit_es": f"Unsplash / {photographer}",
    }


def web(url: str, label_en: str, label_es: str) -> dict:
    return {"url": url, "credit_en": label_en, "credit_es": label_es}


def pendiente_ribbon(country: str, country_es: str, stage: str, program: str, sector_en: str, sector_es: str):
    return [
        {"val": country, "lab_en": "Country", "lab_es": "País", "sub_en": country_es, "sub_es": country_es},
        {"val": stage, "lab_en": "Stage", "lab_es": "Etapa", "sub_en": program, "sub_es": program},
        {"val": sector_en[:8], "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Cleantech", "sub_es": "Cleantech"},
        {"val": "[P]", "lab_en": "Metrics", "lab_es": "Métricas", "sub_en": "[PENDIENTE]", "sub_es": "[PENDIENTE]"},
    ]


def problem_stats(program: str, country: str, country_es: str):
    return [
        [{"num": program, "lab_en": "Program", "lab_es": "Programa"}, {"num": "CTH", "lab_en": "Hub", "lab_es": "Hub"}],
        [{"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"}, {"num": country, "lab_en": country_es, "lab_es": country_es}],
    ]


def portfolio_sections(
    *,
    problem_head_en: str,
    problem_head_es: str,
    problem_body_en: str,
    problem_body_es: str,
    program: str,
    country: str,
    country_es: str,
    focus_en: str,
    focus_es: str,
    program_blurb_en: str,
    program_blurb_es: str,
    market_en: str,
    market_es: str,
    taxonomy_en: str,
    taxonomy_es: str,
    members: list,
    dream_en: str,
    dream_es: str,
    bg_problem: str,
    bg_solution: str,
    bg_impact: str,
    bg_team: str,
):
    return [
        {
            "num": 1,
            "type": "split",
            "overlay": "rgba(12,73,138,.30)",
            "title_en": "The Problem",
            "title_es": "El Problema",
            "head_en": problem_head_en,
            "head_es": problem_head_es,
            "body_en": problem_body_en,
            "body_es": problem_body_es,
            "bg": bg_problem,
        },
        {
            "num": 2,
            "type": "solution",
            "overlay": "rgba(102,147,72,.30)",
            "title_en": "The Solution",
            "title_es": "La Solución",
            "steps": [
                {"icon": "🌱", "label_en": "Focus", "label_es": "Enfoque", "text_en": focus_en, "text_es": focus_es},
                {"icon": "🔗", "label_en": "Program", "label_es": "Programa", "text_en": program_blurb_en, "text_es": program_blurb_es},
                {"icon": "🌎", "label_en": "Market", "label_es": "Mercado", "text_en": market_en, "text_es": market_es},
            ],
            "bg": bg_solution,
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
                    "text_en": "Profile synced from BookStack Startup Portfolio + Odoo (SoT). CleantechHUB Acceleration cohort (Portafolio CTH).",
                    "text_es": "Perfil sincronizado desde BookStack Startup Portfolio + Odoo (SoT). Cohorte Acceleration CleantechHUB (Portafolio CTH).",
                },
                {
                    "icon": "🎯",
                    "title_en": "Taxonomy",
                    "title_es": "Taxonomía",
                    "text_en": taxonomy_en,
                    "text_es": taxonomy_es,
                },
            ],
            "bg": bg_impact,
        },
        {
            "num": 4,
            "type": "team",
            "overlay": "rgba(12,73,138,.30)",
            "title_en": "Leadership",
            "title_es": "Liderazgo",
            "members": members,
            "dream_en": dream_en,
            "dream_es": dream_es,
            "bg": bg_team,
        },
    ]


def credits_block(slug: str, parts: list[tuple[str, dict]]) -> tuple[str, str]:
    lines_en = [f"Image credits ({slug}):"]
    lines_es = [f"Créditos de imagen ({slug}):"]
    for label, img in parts:
        lines_en.append(f"· {label}: {img['credit_en']}")
        lines_es.append(f"· {label}: {img['credit_es']}")
    return "\n".join(lines_en), "\n".join(lines_es)


# Per-page image packs: hero + §01–§04 + CTA — all URLs unique across batch 8.
ISTMO_IMG = {
    "hero": web(
        "https://lirp.cdn-website.com/317bfb1d/dms3rep/multi/opt/photo-1503327327322-56f962d3fc57-1920w.jpg",
        "Istmo Verde website (istmoverde.com)",
        "Sitio web Istmo Verde (istmoverde.com)",
    ),
    "s1": u("photo-1518709268805-4e9042af2176", "Lukasz Szmigiel"),
    "s2": u("photo-1542601906990-9c710a1061dd", "Matt Artz"),
    "s3": u("photo-1448375241506-7899e3828c0f", "Lucas Sankey"),
    "s4": u("photo-1507003211169-0a1dd7228f2d", "Hans Reniers"),
    "cta": u("photo-1518173941573-c443e494106a", "Lucas Sankey"),
}
KIGUI_IMG = {
    "hero": web(
        "https://www.kigui.io/og-image.png",
        "Kigüi verified website (kigui.mx / kigui.io)",
        "Sitio verificado Kigüi (kigui.mx / kigui.io)",
    ),
    "s1": u("photo-1578916171725-1653917a8149", "NeONBRAND"),
    "s2": u("photo-1604719312566-8912caf2334a", "Nathan Dumlao"),
    "s3": u("photo-1586201375761-83865001e26c", "Gilberto Olimpio"),
    "s4": u("photo-1556742049-0cfed4f6a45d", "Clay Banks"),
    "cta": u("photo-1610832958506-aa56368197cf", "Micheile Henderson"),
}
KIMSA_IMG = {
    "hero": web(
        "https://static.wixstatic.com/media/9d6db3_0f8867f1f73c49b791b94ce91bfd59c6%7Emv2.jpg/v1/fit/w_2500,h_1330,al_c/9d6db3_0f8867f1f73c49b791b94ce91bfd59c6%7Emv2.jpg",
        "KIMSA verified website (kimsa.co)",
        "Sitio verificado KIMSA (kimsa.co)",
    ),
    "s1": u("photo-1563986768609-322da13575f3", "Appolinary Kalashnikova"),
    "s2": u("photo-1611273426858-450d7456a79a", "Li-An Lim"),
    "s3": u("photo-1451187580459-43490279bf0d", "NASA"),
    "s4": u("photo-1551288049-bebda4e38f71", "Luke Chesser"),
    "cta": u("photo-1497435334941-8f4e114e509e", "Johannes Plenio"),
}
KLEANTAB_IMG = {
    "hero": web(
        "https://kleantab.com/cdn/shop/files/Kleantab_Limpieza_Poderosa_y_Saludable.png?v=1779937714&width=1600",
        "Kleantab verified website (kleantab.com product photo)",
        "Sitio verificado Kleantab (foto de producto kleantab.com)",
    ),
    "s1": u("photo-1628177142136-43d9810e5622", "Daian Gan"),
    "s2": u("photo-1563452617894-61fc735e623f", "Daiga Ellaby"),
    "s3": u("photo-1585421514734-121ea5978633", "Sarah Chai"),
    "s4": u("photo-1612815167568-60f89d18be55", "Volodymyr Hryshchenko"),
    "cta": u("photo-1416879595882-3373a0480b5b", "Markus Spiske"),
}
LINKO_IMG = {
    "hero": web(
        "https://i0.wp.com/linko.com.co/wp-content/uploads/2020/07/Grupo-2.png?ssl=1",
        "Linko verified website (linko.com.co brand visual)",
        "Sitio verificado Linko (visual de marca linko.com.co)",
    ),
    "s1": u("photo-1581579186482-1f4a1a8a1f94", "No Revisions"),
    "s2": u("photo-1628348714456-2889e6d6660e", "Towfiqu barbhuiya"),
    "s3": u("photo-1565793298595-6a879b1d9492", "ThisisEngineering RAEng"),
    "s4": u("photo-1632829871091-68de131ce026", "KOBU Agency"),
    "cta": u("photo-1581092160607-ee22621dd758", "ThisisEngineering RAEng"),
}


def attach_images(page: dict, imgs: dict) -> dict:
    cred_en, cred_es = credits_block(
        page["slug"],
        [
            ("Hero", imgs["hero"]),
            ("§01 Problem", imgs["s1"]),
            ("§02 Solution", imgs["s2"]),
            ("§03 Impact", imgs["s3"]),
            ("§04 Leadership", imgs["s4"]),
            ("CTA", imgs["cta"]),
        ],
    )
    page["hero_image"] = imgs["hero"]["url"]
    page["cta_bg"] = imgs["cta"]["url"]
    page["image_credits_en"] = cred_en
    page["image_credits_es"] = cred_es
    return page


PAGES = [
    attach_images({
        "slug": "istmo-verde",
        "name": "Istmo Verde",
        "website": "https://www.istmoverde.com/",
        "badge_en": "Forest Carbon · CLP · Acceleration",
        "badge_es": "Carbono Forestal · CLP · Acceleration",
        "hero_sub_en": "istmoverde.com · Guatemala · Cobán · Energy · Stage: Seed",
        "hero_sub_es": "istmoverde.com · Guatemala · Cobán · Energía · Etapa: Seed",
        "pitch_en": "Guatemala's first company developing forest-sector carbon compensation projects, enabling businesses to offset footprints through verified local reforestation and conservation.",
        "pitch_es": "Primera empresa guatemalteca que desarrolla proyectos de compensación de emisiones en el sector forestal, permitiendo a empresas compensar su huella mediante reforestación y conservación verificadas.",
        "cta_pitch_en": "Forest-sector carbon compensation and conservation projects for businesses in Guatemala and Central America.",
        "cta_pitch_es": "Proyectos de compensación de carbono y conservación forestal para empresas en Guatemala y Centroamérica.",
        "ribbon": pendiente_ribbon("GT", "Guatemala", "Seed", "CLP", "Energy", "Energía"),
        "problem_stats": problem_stats("CLP", "GT", "Guatemala"),
        "sections": portfolio_sections(
            problem_head_en="Companies need credible, local forest-based pathways to compensate emissions.",
            problem_head_es="Las empresas necesitan vías locales y creíbles de compensación basadas en el sector forestal.",
            problem_body_en="Guatemala's first company developing forest-sector carbon compensation projects, enabling businesses to offset footprints through verified local reforestation and conservation.",
            problem_body_es="Primera empresa guatemalteca que desarrolla proyectos de compensación de emisiones en el sector forestal, permitiendo a empresas compensar su huella mediante reforestación verificada local.",
            program="CLP",
            country="GT",
            country_es="Guatemala",
            focus_en="Develop, verify, and commercialize forest carbon and conservation projects for voluntary carbon markets.",
            focus_es="Desarrollar, verificar y comercializar proyectos forestales de carbono y conservación para mercados voluntarios.",
            program_blurb_en="Istmo Verde, S.A. — ClimateLaunchpad (CLP) · CleantechHUB Acceleration.",
            program_blurb_es="Istmo Verde, S.A. — ClimateLaunchpad (CLP) · Acceleration CleantechHUB.",
            market_en="Based in Cobán, Alta Verapaz, Guatemala. Public site: istmoverde.com.",
            market_es="Con base en Cobán, Alta Verapaz, Guatemala. Sitio público: istmoverde.com.",
            taxonomy_en="[PENDIENTE] — forest carbon / compensation (CT node not on portfolio card)",
            taxonomy_es="[PENDIENTE] — carbono forestal / compensación (nodo CT no en tarjeta de portafolio)",
            members=[
                {
                    "name": "Iván E. Barrientos Stubbs",
                    "initials": "IB",
                    "role_en": "Country Manager · Istmo Verde, S.A.",
                    "role_es": "Gerente de País · Istmo Verde, S.A.",
                    "bio_en": "Leads carbon project development for Istmo Verde (public LinkedIn role). Additional founders: [PENDIENTE].",
                    "bio_es": "Lidera desarrollo de proyectos de carbono en Istmo Verde (rol público en LinkedIn). Otros fundadores: [PENDIENTE].",
                    "linkedin": "https://www.linkedin.com/in/iv%C3%A1n-e-barrientos-stubbs-96a23688/",
                }
            ],
            dream_en="Program: CLP + CleantechHUB Acceleration. City: Cobán. Verified KPIs: [PENDIENTE]. Pitch deck on profile: [PENDIENTE].",
            dream_es="Programa: CLP + Acceleration CleantechHUB. Ciudad: Cobán. KPIs verificados: [PENDIENTE]. Pitch deck en perfil: [PENDIENTE].",
            bg_problem=ISTMO_IMG["s1"]["url"],
            bg_solution=ISTMO_IMG["s2"]["url"],
            bg_impact=ISTMO_IMG["s3"]["url"],
            bg_team=ISTMO_IMG["s4"]["url"],
        ),
    }, ISTMO_IMG),
    attach_images({
        "slug": "kigui",
        "name": "Kigüi",
        "website": "https://kigui.mx/",
        "badge_en": "Food Waste · CLAC23 · Acceleration",
        "badge_es": "Desperdicio Alimentario · CLAC23 · Acceleration",
        "hero_sub_en": "kigui.mx · Mexico · Circular Economy · Stage: Seed",
        "hero_sub_es": "kigui.mx · México · Economía Circular · Etapa: Seed",
        "pitch_en": "Food-waste reduction platform connecting retailers and consumers with near-expiry products, preventing disposal and associated CO₂ emissions.",
        "pitch_es": "Plataforma de reducción de desperdicio alimentario que conecta retail y consumidores con productos próximos a vencer, evitando disposición y emisiones de CO₂ asociadas.",
        "cta_pitch_en": "AI copilot for retail execution — inventory, expiry, and in-store operations to cut food waste.",
        "cta_pitch_es": "Copiloto de IA para ejecución en retail — inventario, caducidad y operación en tienda para reducir merma.",
        "ribbon": pendiente_ribbon("MX", "Mexico", "Seed", "CLAC23", "Circular", "Circular"),
        "problem_stats": problem_stats("CLAC23", "MX", "México"),
        "sections": portfolio_sections(
            problem_head_en="Supermarkets and CPG chains lose margin and generate emissions when food expires on shelves.",
            problem_head_es="Supermercados y marcas pierden margen y generan emisiones cuando los alimentos vencen en góndola.",
            problem_body_en="Food-waste reduction app connecting consumers with near-expiry products at up to 60% discount in supermarkets, preventing disposal and associated CO₂ emissions.",
            problem_body_es="App de reducción de desperdicio alimentario que conecta consumidores con productos próximos a vencer con hasta 60% de descuento en supermercados, evitando emisiones de CO₂.",
            program="CLAC23",
            country="MX",
            country_es="México",
            focus_en="Retail tech to track expiry, prioritize in-store tasks, and reduce shrink from unsold food.",
            focus_es="Tecnología retail para rastrear caducidad, priorizar tareas en tienda y reducir merma por alimentos no vendidos.",
            program_blurb_en="Kigüi — CLAC23 (CleantechHUB) · Acceleration portfolio.",
            program_blurb_es="Kigüi — CLAC23 (CleantechHUB) · Portafolio Acceleration.",
            market_en="HQ Argentina; strong Mexico operations. Public site: kigui.mx.",
            market_es="Sede Argentina; operación relevante en México. Sitio público: kigui.mx.",
            taxonomy_en="CT-WA-002 · Organic Waste & Composting",
            taxonomy_es="CT-WA-002 · Residuos Orgánicos y Compostaje",
            members=[
                {
                    "name": "Mauricio Kremer",
                    "initials": "MK",
                    "role_en": "CEO & Co-founder",
                    "role_es": "CEO y Cofundador",
                    "bio_en": "Co-founder leading Kigüi retail and food-waste reduction platform (public LinkedIn).",
                    "bio_es": "Cofundador al frente de la plataforma Kigüi de retail y reducción de merma (LinkedIn público).",
                    "linkedin": "https://www.linkedin.com/in/mauriciokremer/",
                },
                {
                    "name": "Maximiliano Dicranian",
                    "initials": "MD",
                    "role_en": "Co-founder & COO",
                    "role_es": "Cofundador y COO",
                    "bio_en": "Co-founder & COO — operations and LATAM expansion (public LinkedIn).",
                    "bio_es": "Cofundador y COO — operaciones y expansión LATAM (LinkedIn público).",
                    "linkedin": "https://www.linkedin.com/in/maximiliano-dicranian/",
                },
            ],
            dream_en="Program: CLAC23 + Acceleration. Verified KPIs: [PENDIENTE]. Pitch deck: [PENDIENTE].",
            dream_es="Programa: CLAC23 + Acceleration. KPIs verificados: [PENDIENTE]. Pitch deck: [PENDIENTE].",
            bg_problem=KIGUI_IMG["s1"]["url"],
            bg_solution=KIGUI_IMG["s2"]["url"],
            bg_impact=KIGUI_IMG["s3"]["url"],
            bg_team=KIGUI_IMG["s4"]["url"],
        ),
    }, KIGUI_IMG),
    attach_images({
        "slug": "kimsa",
        "name": "KIMSA",
        "website": "https://kimsa.co/",
        "badge_en": "Carbon MRV · CLAC21 · Acceleration",
        "badge_es": "MRV de Carbono · CLAC21 · Acceleration",
        "hero_sub_en": "kimsa.co · Colombia · Bogotá · Energy · Stage: Seed",
        "hero_sub_es": "kimsa.co · Colombia · Bogotá · Energía · Etapa: Seed",
        "pitch_en": "Digitizes carbon measurement and traceability for companies, reducing time and cost of tracking reduction goals while connecting businesses to Colombian offset projects.",
        "pitch_es": "Digitaliza la medición y trazabilidad de carbono para empresas, reduciendo tiempo y costos en el seguimiento de metas y conectando negocios con proyectos de compensación colombianos.",
        "cta_pitch_en": "Climate consulting and CarbonBox SaaS for corporate carbon footprints and decarbonization.",
        "cta_pitch_es": "Consultoría climática y SaaS CarbonBox para huella de carbono corporativa y descarbonización.",
        "ribbon": pendiente_ribbon("CO", "Colombia", "Seed", "CLAC21", "Energy", "Energía"),
        "problem_stats": problem_stats("CLAC21", "CO", "Colombia"),
        "sections": portfolio_sections(
            problem_head_en="Most companies lack affordable, repeatable tools to measure and manage carbon footprints.",
            problem_head_es="La mayoría de empresas carece de herramientas accesibles y repetibles para medir y gestionar su huella de carbono.",
            problem_body_en="Digitizes carbon measurement and traceability for companies, reducing time and cost of tracking reduction goals while connecting businesses to Colombian offset projects.",
            problem_body_es="Digitaliza la medición y trazabilidad de carbono para empresas, reduciendo tiempo y costos en el seguimiento de metas y conectando negocios con proyectos de compensación colombianos.",
            program="CLAC21",
            country="CO",
            country_es="Colombia",
            focus_en="KIMSA — Clima, Conservación y Desarrollo SAS: climate consulting plus CarbonBox digital MRV.",
            focus_es="KIMSA — Clima, Conservación y Desarrollo SAS: consultoría climática más MRV digital CarbonBox.",
            program_blurb_en="Portfolio card: CARBON BOX · CLAC21 · CleantechHUB Acceleration.",
            program_blurb_es="Tarjeta portafolio: CARBON BOX · CLAC21 · Acceleration CleantechHUB.",
            market_en="Based in Bogotá, Colombia. Public site: kimsa.co.",
            market_es="Con base en Bogotá, Colombia. Sitio público: kimsa.co.",
            taxonomy_en="CT-IC-002 · AI-Powered MRV · CT-XS-001 · Carbon Markets & Credits",
            taxonomy_es="CT-IC-002 · MRV con IA · CT-XS-001 · Mercados y Créditos de Carbono",
            members=[
                {
                    "name": "Angela Viviana Bohórquez L",
                    "initials": "VB",
                    "role_en": "Co-founder · KIMSA / CarbonBox",
                    "role_es": "Cofundadora · KIMSA / CarbonBox",
                    "bio_en": "Co-founder and technical director, KIMSA; co-founder CarbonBox (public LinkedIn).",
                    "bio_es": "Cofundadora y directora técnica, KIMSA; cofundadora CarbonBox (LinkedIn público).",
                    "linkedin": "https://www.linkedin.com/in/viviana-boh%C3%B3rquez-l/",
                },
                {
                    "name": "Carlos Felipe Torres Triana",
                    "initials": "CT",
                    "role_en": "Co-founder · CarbonBox / Clima Soluciones",
                    "role_es": "Cofundador · CarbonBox / Clima Soluciones",
                    "bio_en": "Co-founder CarbonBox; CEO Clima Soluciones SAS (public LinkedIn).",
                    "bio_es": "Cofundador CarbonBox; CEO Clima Soluciones SAS (LinkedIn público).",
                    "linkedin": "https://www.linkedin.com/in/carlos-felipe-torres-triana-5864431a5/",
                },
            ],
            dream_en="Program: CLAC21 + Acceleration. Verified KPIs: [PENDIENTE]. Pitch deck: [PENDIENTE].",
            dream_es="Programa: CLAC21 + Acceleration. KPIs verificados: [PENDIENTE]. Pitch deck: [PENDIENTE].",
            bg_problem=KIMSA_IMG["s1"]["url"],
            bg_solution=KIMSA_IMG["s2"]["url"],
            bg_impact=KIMSA_IMG["s3"]["url"],
            bg_team=KIMSA_IMG["s4"]["url"],
        ),
    }, KIMSA_IMG),
    attach_images({
        "slug": "kleantab",
        "name": "Kleantab",
        "website": "https://kleantab.com/",
        "badge_en": "Clean Home · Acceleration",
        "badge_es": "Hogar Limpio · Acceleration",
        "hero_sub_en": "kleantab.com · Costa Rica · Escazú · Circular Economy · Stage: [PENDIENTE]",
        "hero_sub_es": "kleantab.com · Costa Rica · Escazú · Economía Circular · Etapa: [PENDIENTE]",
        "pitch_en": "Soluble eco-friendly cleaning tablets that replace single-use plastic bottles, cutting transport volume and hazardous chemicals in home cleaning.",
        "pitch_es": "Tabletas ecológicas solubles que reemplazan botellas plásticas de un solo uso, reduciendo volumen de transporte y químicos en limpieza del hogar.",
        "cta_pitch_en": "Refillable cleaning — dissolve a tablet at home, reuse the bottle, less plastic and lighter logistics.",
        "cta_pitch_es": "Limpieza recargable — disuelve una tableta en casa, reutiliza el envase, menos plástico y logística más liviana.",
        "ribbon": pendiente_ribbon("CR", "Costa Rica", "[P]", "Acceleration", "Circular", "Circular"),
        "problem_stats": problem_stats("Acceleration", "CR", "Costa Rica"),
        "sections": portfolio_sections(
            problem_head_en="Traditional liquid cleaners ship mostly water in single-use plastic, driving waste and transport emissions.",
            problem_head_es="Los limpiadores líquidos tradicionales transportan principalmente agua en plástico desechable, generando residuos y emisiones logísticas.",
            problem_body_en="Soluble eco-friendly cleaning tablets that replace single-use plastic bottles, cutting transport volume and hazardous chemicals in home cleaning.",
            problem_body_es="Tabletas ecológicas solubles que reemplazan botellas plásticas de un solo uso, reduciendo volumen de transporte y químicos en limpieza del hogar.",
            program="Acceleration",
            country="CR",
            country_es="Costa Rica",
            focus_en="Concentrated cleaning tablets — consumer dissolves at home to fill reusable bottles.",
            focus_es="Tabletas concentradas — el consumidor disuelve en casa para rellenar envases reutilizables.",
            program_blurb_en="Kleantab — CleantechHUB Acceleration (Portafolio CTH).",
            program_blurb_es="Kleantab — Acceleration CleantechHUB (Portafolio CTH).",
            market_en="Based in Escazú / San José, Costa Rica. Public site: kleantab.com.",
            market_es="Con base en Escazú / San José, Costa Rica. Sitio público: kleantab.com.",
            taxonomy_en="[PENDIENTE] — circular consumer cleaning (CT node not on portfolio card)",
            taxonomy_es="[PENDIENTE] — limpieza circular de consumo (nodo CT no en tarjeta de portafolio)",
            members=[
                {
                    "name": "Daniel Kaune",
                    "initials": "DK",
                    "role_en": "Co-founder & CEO",
                    "role_es": "Cofundador y CEO",
                    "bio_en": "Co-founder Kleantab (public LinkedIn).",
                    "bio_es": "Cofundador Kleantab (LinkedIn público).",
                    "linkedin": "https://www.linkedin.com/in/daniel-kaune/",
                },
                {
                    "name": "Alexander Anders",
                    "initials": "AA",
                    "role_en": "Co-founder & CRO",
                    "role_es": "Cofundador y CRO",
                    "bio_en": "Co-founder Kleantab (public LinkedIn).",
                    "bio_es": "Cofundador Kleantab (LinkedIn público).",
                    "linkedin": "https://www.linkedin.com/in/alexander-anders-793ba1100/",
                },
            ],
            dream_en="Stage: [PENDIENTE]. Verified KPIs: [PENDIENTE]. Pitch deck: [PENDIENTE].",
            dream_es="Etapa: [PENDIENTE]. KPIs verificados: [PENDIENTE]. Pitch deck: [PENDIENTE].",
            bg_problem=KLEANTAB_IMG["s1"]["url"],
            bg_solution=KLEANTAB_IMG["s2"]["url"],
            bg_impact=KLEANTAB_IMG["s3"]["url"],
            bg_team=KLEANTAB_IMG["s4"]["url"],
        ),
    }, KLEANTAB_IMG),
    attach_images({
        "slug": "linko-workers",
        "name": "Linko Workers",
        "website": "https://linko.com.co/",
        "badge_en": "Industrial Cleaning · CLAC24 · Acceleration",
        "badge_es": "Limpieza Industrial · CLAC24 · Acceleration",
        "hero_sub_en": "linko.com.co · Colombia · Neiva · Circular Economy · Stage: Pre-Seed",
        "hero_sub_es": "linko.com.co · Colombia · Neiva · Economía Circular · Etapa: Pre-Seed",
        "pitch_en": "Manufactures and commercializes industrial cleaning and disinfection products for institutional and household clients in southern Colombia.",
        "pitch_es": "Fabrica y comercializa productos de limpieza y desinfección industrial para clientes institucionales y domésticos en el sur de Colombia.",
        "cta_pitch_en": "Industrial cleaning and disinfection from Neiva — plus sustainable effervescent tablet line (CleantechHUB wiki).",
        "cta_pitch_es": "Limpieza y desinfección industrial desde Neiva — más línea de tabletas efervescentes sostenibles (wiki CleantechHUB).",
        "ribbon": pendiente_ribbon("CO", "Colombia", "Pre-Seed", "CLAC24", "Circular", "Circular"),
        "problem_stats": problem_stats("CLAC24", "CO", "Colombia"),
        "sections": portfolio_sections(
            problem_head_en="Institutional and household clients in southern Colombia need reliable cleaning and disinfection supply.",
            problem_head_es="Clientes institucionales y domésticos en el sur de Colombia necesitan suministro confiable de limpieza y desinfección.",
            problem_body_en="Manufactures and commercializes industrial cleaning and disinfection products for institutional and household clients in southern Colombia.",
            problem_body_es="Fabrica y comercializa productos de limpieza y desinfección industrial para clientes institucionales y domésticos en el sur de Colombia.",
            program="CLAC24",
            country="CO",
            country_es="Colombia",
            focus_en="Production and sale of industrial and household cleaning and disinfection products; exploring plastic-free effervescent formats.",
            focus_es="Producción y venta de productos de limpieza y desinfección industrial y doméstica; explorando formatos efervescentes sin plástico.",
            program_blurb_en="LINKO WORKERS SAS — CLAC24 · CleantechHUB Acceleration.",
            program_blurb_es="LINKO WORKERS SAS — CLAC24 · Acceleration CleantechHUB.",
            market_en="Based in Neiva, Huila, Colombia. Public site: linko.com.co.",
            market_es="Con base en Neiva, Huila, Colombia. Sitio público: linko.com.co.",
            taxonomy_en="[PENDIENTE] — circular industrial cleaning (CT node not on portfolio card)",
            taxonomy_es="[PENDIENTE] — limpieza industrial circular (nodo CT no en tarjeta de portafolio)",
            members=[
                {
                    "name": "Nicolás Alberto Parra Munar",
                    "initials": "NP",
                    "role_en": "Founder & CEO · Linko (legal rep. LINKO WORKERS SAS)",
                    "role_es": "Fundador y CEO · Linko (rep. legal LINKO WORKERS SAS)",
                    "bio_en": "Founder per public company site and Colombia registry; LinkedIn profile: [PENDIENTE].",
                    "bio_es": "Fundador según sitio público y registro Colombia; perfil LinkedIn: [PENDIENTE].",
                }
            ],
            dream_en="Program: CLAC24 + Acceleration. Verified KPIs: [PENDIENTE]. Pitch deck: [PENDIENTE].",
            dream_es="Programa: CLAC24 + Acceleration. KPIs verificados: [PENDIENTE]. Pitch deck: [PENDIENTE].",
            bg_problem=LINKO_IMG["s1"]["url"],
            bg_solution=LINKO_IMG["s2"]["url"],
            bg_impact=LINKO_IMG["s3"]["url"],
            bg_team=LINKO_IMG["s4"]["url"],
        ),
    }, LINKO_IMG),
]


def collect_image_urls(page: dict) -> list[str]:
    urls = [page["hero_image"], page["cta_bg"]]
    for sec in page["sections"]:
        if sec.get("bg"):
            urls.append(sec["bg"])
    return urls


def main() -> None:
    seen: dict[str, str] = {}
    for page in PAGES:
        for url in collect_image_urls(page):
            if url in seen and seen[url] != page["slug"]:
                raise SystemExit(f"Duplicate image URL across pages: {url} ({seen[url]} vs {page['slug']})")
            seen[url] = page["slug"]
        slug = page["slug"]
        path = OUT / f"{slug}.json"
        path.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
