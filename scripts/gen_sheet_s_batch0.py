#!/usr/bin/env python3
"""Generate onepager JSON for sheet-s-pages batch 0 (Top StartUps)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "onepagers" / "data"

def u(photo_id: str) -> str:
    return f"https://images.unsplash.com/{photo_id}?w=1200&q=80"


# Unique hero + section backgrounds per slug (no URL reused across batch 0).
PAGE_IMAGES: dict[str, dict[str, str]] = {
    "b-kapz": {
        "hero": u("photo-1625246333195-78d9c38ad449"),
        "problem": u("photo-1416879595882-3373a0480b5b"),
        "solution": u("photo-1500382017468-9049fed747ef"),
        "impact": u("photo-1447933601403-0c6688de566e"),
        "team": u("photo-1576086213369-97a306d36557"),
        "cta": u("photo-1511497584788-876760111969"),
    },
    "elastic-energy": {
        "hero": "https://framerusercontent.com/images/igNXB7ftfNaHqTcfuSwEw6H2bO4.png?width=2186&height=1324",
        "problem": "https://framerusercontent.com/images/0Djozuq5MuH9xNWt7gw7lrO8.png?width=1732&height=1936",
        "solution": u("photo-1451187580459-43490279c0fa"),
        "impact": u("photo-1441974231531-c6227db76b6e"),
        "team": u("photo-1518977676601-b53f82aba655"),
        "cta": u("photo-1497366216548-37526070297c"),
    },
    "mubon": {
        "hero": u("photo-1542601906990-b4d3fb778b09"),
        "problem": u("photo-1470071459604-3b5ec3a7fe05"),
        "solution": u("photo-1551288049-bebda4e38f71"),
        "impact": u("photo-1518770660439-4636190af475"),
        "team": u("photo-1521791136064-7986c2920216"),
        "cta": u("photo-1529156069898-49953e39b3ac"),
    },
    "novatio": {
        "hero": "https://novatio.com.co/wp-content/uploads/2022/08/Energia-que-transforma-1024x768.jpg",
        "problem": "https://novatio.com.co/wp-content/uploads/2022/08/Palma-aceitera.jpg",
        "solution": "https://novatio.com.co/wp-content/uploads/2022/08/Porcicultura.jpg",
        "impact": "https://novatio.com.co/wp-content/uploads/2022/08/Programas-de-impacto.jpg",
        "team": "https://novatio.com.co/wp-content/uploads/2022/08/espejo-otros-sectores.jpg",
        "cta": u("photo-1460925895917-afdab827c52f"),
    },
    "plasticos-ambientales": {
        "hero": "https://plasticosambientales.com/wp-content/uploads/2023/08/Plastico_Reciclado_Postconsumo_2.png",
        "problem": u("photo-1532996122724-e3c354a0b15b"),
        "solution": u("photo-1581092160607-ee22621dd758"),
        "impact": u("photo-1504307651254-35680f356dfd"),
        "team": u("photo-1522071820081-009f0129c71c"),
        "cta": u("photo-1501339847302-ac426a4a7cbb"),
    },
}

IMAGE_CREDITS: dict[str, dict[str, str]] = {
    "b-kapz": {
        "hero": "Unsplash (photo-1625246333195) — cropland / agrifood",
        "problem": "Unsplash (photo-1416879595882) — greenhouse agriculture",
        "solution": "Unsplash (photo-1500382017468) — farmland horizon",
        "impact": "Unsplash (photo-1447933601403) — coffee/agriculture landscape",
        "team": "Unsplash (photo-1576086213369) — laboratory microscope",
        "cta": "Unsplash (photo-1511497584788) — roasted coffee / agrifood",
    },
    "elastic-energy": {
        "hero": "elasticenergy.co — tree-sap storage product render",
        "problem": "elasticenergy.co — elastic storage hardware visual",
        "solution": "Unsplash (photo-1451187580459) — energy / earth from space",
        "impact": "Unsplash (photo-1441974231531) — forest canopy",
        "team": "Unsplash (photo-1518977676601) — solar panels",
        "cta": "Unsplash (photo-1497366216548) — sustainable workspace",
    },
    "mubon": {
        "hero": "Unsplash (photo-1542601906990) — clean air / urban mobility context",
        "problem": "Unsplash (photo-1470071459604) — mountain road infrastructure",
        "solution": "Unsplash (photo-1551288049) — analytics dashboard (smart platform)",
        "impact": "Unsplash (photo-1518770660439) — technology / circuits",
        "team": "Unsplash (photo-1521791136064) — partnership / deployment",
        "cta": "Unsplash (photo-1529156069898) — team collaboration",
    },
    "novatio": {
        "hero": "novatio.com.co — Energía que transforma (project photo)",
        "problem": "novatio.com.co — oil-palm effluent / biogas context",
        "solution": "novatio.com.co — swine farming biodigester application",
        "impact": "novatio.com.co — community impact programs",
        "team": "novatio.com.co — cross-sector project mirror",
        "cta": "Unsplash (photo-1460925895917) — business / project analytics",
    },
    "plasticos-ambientales": {
        "hero": "plasticosambientales.com — post-consumer recycled plastic product",
        "problem": "Unsplash (photo-1532996122724) — plastic materials handling",
        "solution": "Unsplash (photo-1581092160607) — industrial processing",
        "impact": "Unsplash (photo-1504307651254) — construction / materials site",
        "team": "Unsplash (photo-1522071820081) — team planning",
        "cta": "Unsplash (photo-1501339847302) — workspace / operations",
    },
}


def portfolio_profile(
    *,
    slug: str,
    name: str,
    website: str,
    badge_en: str,
    badge_es: str,
    hero_image: str,
    hero_sub_en: str,
    hero_sub_es: str,
    pitch_en: str,
    pitch_es: str,
    cta_pitch_en: str,
    cta_pitch_es: str,
    ribbon: list,
    problem_head_en: str,
    problem_head_es: str,
    problem_body_en: str,
    problem_body_es: str,
    stat_row1: list,
    stat_row2: list,
    solution_steps: list,
    impact_cards: list,
    team_members: list,
    dream_en: str,
    dream_es: str,
    images: dict[str, str],
    credits: dict[str, str],
) -> dict:
    credit_line_en = "Image credits — Hero: {hero}; §01: {problem}; §02: {solution}; §03: {impact}; §04: {team}; CTA: {cta}.".format(**credits)
    credit_line_es = credit_line_en
    return {
        "slug": slug,
        "name": name,
        "website": website,
        "badge_en": badge_en,
        "badge_es": badge_es,
        "hero_image": hero_image,
        "hero_sub_en": hero_sub_en,
        "hero_sub_es": hero_sub_es,
        "pitch_en": pitch_en,
        "pitch_es": pitch_es,
        "cta_pitch_en": cta_pitch_en,
        "cta_pitch_es": cta_pitch_es,
        "cta_btn_en": "Visit website",
        "cta_btn_es": "Visitar sitio",
        "cta_bg": images["cta"],
        "ribbon": ribbon,
        "problem_stats": [stat_row1, stat_row2],
        "sections": [
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
                "bg": images["problem"],
            },
            {
                "num": 2,
                "type": "solution",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "The Solution",
                "title_es": "La Solución",
                "steps": solution_steps,
                "bg": images["solution"],
            },
            {
                "num": 3,
                "type": "impact",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "Impact &amp; Program",
                "title_es": "Impacto y Programa",
                "cards": impact_cards,
                "bg": images["impact"],
            },
            {
                "num": 4,
                "type": "team",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "Leadership",
                "title_es": "Liderazgo",
                "members": team_members,
                "dream_en": dream_en + " " + credit_line_en,
                "dream_es": dream_es + " " + credit_line_es,
                "bg": images["team"],
            },
        ],
    }


STARTUPS = [
    portfolio_profile(
        slug="b-kapz",
        name="b-Kapz",
        website="https://www.b-kapz.com/",
        badge_en="AgTech &middot; Microencapsulation &middot; CleantechHUB Acceleration",
        badge_es="AgTech &middot; Microencapsulación &middot; Aceleración CleantechHUB",
        hero_image=PAGE_IMAGES["b-kapz"]["hero"],
        images=PAGE_IMAGES["b-kapz"],
        credits=IMAGE_CREDITS["b-kapz"],
        hero_sub_en="b-kapz.com &middot; Buenos Aires, Argentina &middot; AgTech / BioTech &middot; Stage: Validation &middot; CT taxonomy: [PENDIENTE]",
        hero_sub_es="b-kapz.com &middot; Buenos Aires, Argentina &middot; AgTech / BioTech &middot; Etapa: Validación &middot; Taxonomía CT: [PENDIENTE]",
        pitch_en="Microencapsulation platform that turns unstable liquid agricultural bioinputs into stable, concentrated solid formats — improving shelf life, logistics, and compatibility with conventional inputs.",
        pitch_es="Plataforma de microencapsulación que convierte bioinsumos agrícolas líquidos inestables en formatos sólidos estables y concentrados — mejorando vida útil, logística y compatibilidad con insumos convencionales.",
        cta_pitch_en="Unlock scalable biological inputs for agriculture through stable microencapsulation (also operating as BeCaps).",
        cta_pitch_es="Desbloquear bioinsumos agrícolas escalables mediante microencapsulación estable (también operando como BeCaps).",
        ribbon=[
            {"val": "AR", "lab_en": "Country", "lab_es": "País", "sub_en": "Argentina", "sub_es": "Argentina"},
            {"val": "Valid.", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "Pre-Seed", "sub_es": "Pre-Seed"},
            {"val": "AgTech", "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Bioinputs", "sub_es": "Bioinsumos"},
            {"val": "[P]", "lab_en": "Metrics", "lab_es": "Métricas", "sub_en": "[PENDIENTE]", "sub_es": "[PENDIENTE]"},
        ],
        problem_head_en="Low adoption of bioinputs due to instability, short shelf life, and logistics complexity.",
        problem_head_es="Baja adopción de bioinsumos por inestabilidad, corta vida útil y complejidad logística.",
        problem_body_en="Liquid microbial and biological products often need refrigeration, degrade in the field, and cannot easily combine with chemical fertilizers — making them costly and hard to scale for farmers and input companies.",
        problem_body_es="Los productos microbianos y biológicos líquidos suelen requerir refrigeración, degradarse en campo y no combinarse fácilmente con fertilizantes químicos — encareciendo y limitando la escala para agricultores y empresas de insumos.",
        stat_row1=[
            {"num": "CTH", "lab_en": "Acceleration", "lab_es": "Aceleración"},
            {"num": "B2B", "lab_en": "Model", "lab_es": "Modelo"},
        ],
        stat_row2=[
            {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
            {"num": "CABA", "lab_en": "City", "lab_es": "Ciudad"},
        ],
        solution_steps=[
            {
                "icon": "🧬",
                "label_en": "Encapsulate",
                "label_es": "Encapsular",
                "text_en": "Proprietary matrix and spray-drying process protect microbes and convert liquids into concentrated solids.",
                "text_es": "Matriz propia y proceso de spray-drying protegen microbios y convierten líquidos en sólidos concentrados.",
            },
            {
                "icon": "📦",
                "label_en": "Stabilize",
                "label_es": "Estabilizar",
                "text_en": "Extended shelf life at room temperature and reduced volume/weight simplify storage and transport.",
                "text_es": "Mayor vida útil a temperatura ambiente y menor volumen/peso simplifican almacenamiento y transporte.",
            },
            {
                "icon": "🌾",
                "label_en": "Integrate",
                "label_es": "Integrar",
                "text_en": "Enables hybrid formulations compatible with conventional fertilizers and broader field use.",
                "text_es": "Permite formulaciones híbridas compatibles con fertilizantes convencionales y mayor uso en campo.",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Portfolio source",
                "title_es": "Fuente portafolio",
                "text_en": "CleantechHUB Top StartUps (Portafolio CTH sheet) — Acceleration track; public company data from b-kapz.com / becaps.bio.",
                "text_es": "Top StartUps CleantechHUB (hoja Portafolio CTH) — track Aceleración; datos públicos en b-kapz.com / becaps.bio.",
            },
            {
                "icon": "🎯",
                "title_en": "Taxonomy",
                "title_es": "Taxonomía",
                "text_en": "AgTech / biological inputs — formal CT node: [PENDIENTE].",
                "text_es": "AgTech / bioinsumos — nodo CT formal: [PENDIENTE].",
            },
        ],
        team_members=[
            {
                "name": "Emiliano Agustín Barbero",
                "initials": "EB",
                "role_en": "Co-founder &amp; CEO",
                "role_es": "Cofundador y CEO",
                "bio_en": "Public-facing CEO. Source: b-kapz.com team page; Argentina Ministry trade profile.",
                "bio_es": "CEO público. Fuente: web b-kapz.com; perfil Next from Argentina.",
                "linkedin": "https://www.linkedin.com/in/emilianobarbero",
            },
            {
                "name": "Juan Manuel Crespo",
                "initials": "JC",
                "role_en": "Co-founder &amp; COO",
                "role_es": "Cofundador y COO",
                "bio_en": "Operations and bioprocess scale-up. Source: b-kapz.com team page.",
                "bio_es": "Operaciones y escalado de bioprocesos. Fuente: web b-kapz.com.",
                "linkedin": "https://www.linkedin.com/in/juanmanuelcrespo",
            },
            {
                "name": "María Flavia Luna",
                "initials": "ML",
                "role_en": "Co-founder &amp; CSO",
                "role_es": "Cofundadora y CSO",
                "bio_en": "Chief Scientific Officer — microencapsulation R&amp;D. Source: b-kapz.com team page.",
                "bio_es": "Directora científica — I+D en microencapsulación. Fuente: web b-kapz.com.",
                "linkedin": "https://www.linkedin.com/in/maria-flavia-luna-a5bb8322",
            },
        ],
        dream_en="Program: CleantechHUB Acceleration (Top StartUps). Verified KPIs on profile: [PENDIENTE]. Pitch deck: [PENDIENTE].",
        dream_es="Programa: Aceleración CleantechHUB (Top StartUps). KPIs verificados en perfil: [PENDIENTE]. Pitch deck: [PENDIENTE].",
    ),
    portfolio_profile(
        slug="elastic-energy",
        name="Elastic Energy",
        website="https://elasticenergy.co/",
        badge_en="Clean Energy Storage &middot; CleantechHUB Top StartUps",
        badge_es="Almacenamiento de energía limpia &middot; Top StartUps CleantechHUB",
        hero_image=PAGE_IMAGES["elastic-energy"]["hero"],
        images=PAGE_IMAGES["elastic-energy"],
        credits=IMAGE_CREDITS["elastic-energy"],
        hero_sub_en="elasticenergy.co &middot; Bogotá, Colombia &middot; Energy storage &middot; Stage: [PENDIENTE] &middot; CT taxonomy: [PENDIENTE]",
        hero_sub_es="elasticenergy.co &middot; Bogotá, Colombia &middot; Almacenamiento de energía &middot; Etapa: [PENDIENTE] &middot; Taxonomía CT: [PENDIENTE]",
        pitch_en="Mechanical energy storage using natural tree-sap rubber elastic bands — mineral-free alternative designed for off-grid communities paired with solar generation.",
        pitch_es="Almacenamiento mecánico de energía con bandas elásticas de caucho natural de savia arbórea — alternativa sin minerales diseñada para comunidades off-grid con generación solar.",
        cta_pitch_en="Store renewable electricity with bio-based elastic storage — safer, longer-lasting cycles without lithium chemistry.",
        cta_pitch_es="Almacenar electricidad renovable con almacenamiento elástico bio-basado — ciclos más duraderos sin química de litio.",
        ribbon=[
            {"val": "CO", "lab_en": "Country", "lab_es": "País", "sub_en": "Colombia", "sub_es": "Colombia"},
            {"val": "[P]", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "[PENDIENTE]", "sub_es": "[PENDIENTE]"},
            {"val": "Storage", "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Clean energy", "sub_es": "Energía limpia"},
            {"val": "[P]", "lab_en": "Metrics", "lab_es": "Métricas", "sub_en": "[PENDIENTE]", "sub_es": "[PENDIENTE]"},
        ],
        problem_head_en="Billions lack reliable electricity while grid-scale storage relies on minerals and chemical batteries.",
        problem_head_es="Miles de millones carecen de electricidad confiable mientras el almacenamiento a escala depende de minerales y baterías químicas.",
        problem_body_en="Intermittent renewables need storage; conventional batteries raise cost, safety, and supply-chain concerns. Rural off-grid communities need clean power overnight after solar generation.",
        problem_body_es="Las renovables intermitentes requieren almacenamiento; las baterías convencionales elevan costo, riesgo y dependencia de minerales. Comunidades rurales off-grid necesitan energía limpia nocturna tras generación solar.",
        stat_row1=[
            {"num": "CTH", "lab_en": "Top StartUps", "lab_es": "Top StartUps"},
            {"num": "SAS", "lab_en": "Entity CO", "lab_es": "Entidad CO"},
        ],
        stat_row2=[
            {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
            {"num": "BOG", "lab_en": "Bogotá", "lab_es": "Bogotá"},
        ],
        solution_steps=[
            {
                "icon": "☀️",
                "label_en": "Charge",
                "label_es": "Cargar",
                "text_en": "Renewable sources (e.g. solar) power a motor that stretches elastic bands wound on a core.",
                "text_es": "Fuentes renovables (p. ej. solar) accionan un motor que estira bandas elásticas en un núcleo.",
            },
            {
                "icon": "🌳",
                "label_en": "Store",
                "label_es": "Almacenar",
                "text_en": "Natural tree-sap rubber stores mechanical energy without lithium or thermal runaway risk.",
                "text_es": "Caucho natural de savia almacena energía mecánica sin litio ni riesgo de thermal runaway.",
            },
            {
                "icon": "⚡",
                "label_en": "Discharge",
                "label_es": "Descargar",
                "text_en": "When demand rises, bands unwind and drive a generator for usable electricity.",
                "text_es": "Ante demanda, las bandas se desenrollan y accionan un generador para electricidad usable.",
            },
        ],
        impact_cards=[
            {
                "icon": "🌍",
                "title_en": "Off-grid focus",
                "title_es": "Enfoque off-grid",
                "text_en": "Designed for rural communities without traditional grid infrastructure, paired with solar (public site narrative).",
                "text_es": "Diseñado para comunidades rurales sin red tradicional, combinado con solar (narrativa del sitio público).",
            },
            {
                "icon": "🏆",
                "title_en": "Recognition",
                "title_es": "Reconocimientos",
                "text_en": "Colombia eAwards 2025 national winner (NTT DATA Foundation) — public press release; no audited KPIs on profile.",
                "text_es": "Ganador nacional eAwards Colombia 2025 (Fundación NTT DATA) — comunicado público; sin KPIs auditados en perfil.",
            },
        ],
        team_members=[
            {
                "name": "Samuel Bendek",
                "initials": "SB",
                "role_en": "Co-founder &amp; CEO",
                "role_es": "Cofundador y CEO",
                "bio_en": "Leads Elastic Energy development. Source: elasticenergy.co team page.",
                "bio_es": "Lidera el desarrollo de Elastic Energy. Fuente: web elasticenergy.co.",
                "linkedin": "https://www.linkedin.com/in/ceo-elastic-energy",
            },
            {
                "name": "Juliana Bendek",
                "initials": "JB",
                "role_en": "Co-founder &amp; COO",
                "role_es": "Cofundadora y COO",
                "bio_en": "Operations and growth. Source: elasticenergy.co team page.",
                "bio_es": "Operaciones y crecimiento. Fuente: web elasticenergy.co.",
                "linkedin": "https://www.linkedin.com/in/juliana-bendek",
            },
        ],
        dream_en="Program/cohort on CTH sheet: [PENDIENTE detail]. Marketing claims on website (e.g. cycle life, cost vs batteries) not copied as verified KPIs. Pitch deck: [PENDIENTE].",
        dream_es="Programa/cohorte en hoja CTH: [PENDIENTE detalle]. Claims de marketing en web no copiados como KPIs verificados. Pitch deck: [PENDIENTE].",
    ),
    portfolio_profile(
        slug="mubon",
        name="MubOn",
        website="https://mubon.co/",
        badge_en="Electric Mobility &middot; CLAC24 &middot; Growth + Acceleration",
        badge_es="Movilidad eléctrica &middot; CLAC24 &middot; Growth + Aceleración",
        hero_image=PAGE_IMAGES["mubon"]["hero"],
        images=PAGE_IMAGES["mubon"],
        credits=IMAGE_CREDITS["mubon"],
        hero_sub_en="mubon.co &middot; Cali, Colombia &middot; Seed &middot; CT-TR-001 &middot; CT-IC-005",
        hero_sub_es="mubon.co &middot; Cali, Colombia &middot; Seed &middot; CT-TR-001 &middot; CT-IC-005",
        pitch_en="Colombian-made EV charging hardware and smart management platform for shared charging in residential and commercial spaces — expanding electric mobility infrastructure.",
        pitch_es="Hardware de carga VE hecho en Colombia y plataforma inteligente para carga compartida en espacios residenciales y comerciales — expandiendo infraestructura de movilidad eléctrica.",
        cta_pitch_en="Design, install, and operate reliable charging networks with locally manufactured stations and software.",
        cta_pitch_es="Diseñar, instalar y operar redes de carga confiables con estaciones fabricadas localmente y software de gestión.",
        ribbon=[
            {"val": "CO", "lab_en": "Country", "lab_es": "País", "sub_en": "Colombia", "sub_es": "Colombia"},
            {"val": "Seed", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CLAC24", "sub_es": "CLAC24"},
            {"val": "CT-TR", "lab_en": "Taxonomy", "lab_es": "Taxonomía", "sub_en": "CT-TR-001", "sub_es": "CT-TR-001"},
            {"val": "[P]", "lab_en": "Metrics", "lab_es": "Métricas", "sub_en": "[PENDIENTE]", "sub_es": "[PENDIENTE]"},
        ],
        problem_head_en="Electric vehicle adoption needs dependable, scalable charging where people live, work, and travel.",
        problem_head_es="La adopción de vehículos eléctricos requiere carga confiable y escalable donde las personas viven, trabajan y se desplazan.",
        problem_body_en="Fragmented charging experiences and infrastructure gaps slow EV uptake. Fleet, dealership, and property operators need integrated hardware, operations, and payment-ready management.",
        problem_body_es="Experiencias de carga fragmentadas y brechas de infraestructura frenan la adopción de VE. Flotas, concesionarios y operadores inmobiliarios necesitan hardware integrado, operación y gestión lista para pagos.",
        stat_row1=[
            {"num": "CLAC24", "lab_en": "Program", "lab_es": "Programa"},
            {"num": "CTH", "lab_en": "Growth + Acc.", "lab_es": "Growth + Acel."},
        ],
        stat_row2=[
            {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
            {"num": "Cali", "lab_en": "City", "lab_es": "Ciudad"},
        ],
        solution_steps=[
            {
                "icon": "⚡",
                "label_en": "Manufacture",
                "label_es": "Fabricar",
                "text_en": "Locally made EV chargers including fast and ultra-fast stations (portfolio card summary).",
                "text_es": "Cargadores VE de producción local, incluyendo estaciones rápidas y ultrarrápidas (resumen tarjeta portafolio).",
            },
            {
                "icon": "📱",
                "label_en": "Manage",
                "label_es": "Gestionar",
                "text_en": "Software platform for shared charging, user access, and operational control.",
                "text_es": "Plataforma software para carga compartida, acceso de usuarios y control operativo.",
            },
            {
                "icon": "🌎",
                "label_en": "Deploy",
                "label_es": "Desplegar",
                "text_en": "Turn-key projects for companies, retail, and strategic partners across Colombia and region.",
                "text_es": "Proyectos llave en mano para empresas, retail y aliados estratégicos en Colombia y región.",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Wiki / portfolio",
                "title_es": "Wiki / portafolio",
                "text_en": "Profile aligned with Nexus startup portfolio card MUBON (CLAC24) — CleantechHUB LATAM taxonomy nodes CT-TR-001 and CT-IC-005.",
                "text_es": "Perfil alineado con tarjeta MUBON (CLAC24) — nodos CT-TR-001 y CT-IC-005 taxonomía LATAM CleantechHUB.",
            },
            {
                "icon": "🔌",
                "title_en": "Mobility impact",
                "title_es": "Impacto movilidad",
                "text_en": "Enables lower-emission transport by expanding accessible charging infrastructure.",
                "text_es": "Habilita transporte de menores emisiones al expandir infraestructura de carga accesible.",
            },
        ],
        team_members=[
            {
                "name": "Nelson David Padilla H",
                "initials": "NP",
                "role_en": "Founder &amp; CEO",
                "role_es": "Fundador y CEO",
                "bio_en": "Founder leading MubOn electric mobility infrastructure. Source: public LinkedIn profile.",
                "bio_es": "Fundador al frente de la infraestructura de movilidad eléctrica MubOn. Fuente: perfil LinkedIn público.",
                "linkedin": "https://www.linkedin.com/in/phndavid",
            },
            {
                "name": "Juan Sebastian Torres Nieto",
                "initials": "JT",
                "role_en": "Co-founder &amp; Commercial lead",
                "role_es": "Cofundador y líder comercial",
                "bio_en": "Co-founder referenced in CleantechHUB public spotlight post (Dec 2025).",
                "bio_es": "Cofundador referenciado en spotlight público CleantechHUB (dic 2025).",
                "linkedin": "https://www.linkedin.com/in/juan-sebastian-torres-nieto-a5917614b",
            },
        ],
        dream_en="Secondary CT node: CT-IC-005. Third-party growth metrics (e.g. social posts): not listed as verified KPIs. Pitch deck: [PENDIENTE].",
        dream_es="Nodo CT secundario: CT-IC-005. Métricas de terceros (p. ej. posts sociales): no listadas como KPIs verificados. Pitch deck: [PENDIENTE].",
    ),
    portfolio_profile(
        slug="novatio",
        name="Novatio",
        website="https://novatio.com.co/",
        badge_en="Biogas &amp; Biodigesters &middot; CLAC23 &middot; Acceleration",
        badge_es="Biogás y biodigestores &middot; CLAC23 &middot; Aceleración",
        hero_image=PAGE_IMAGES["novatio"]["hero"],
        images=PAGE_IMAGES["novatio"],
        credits=IMAGE_CREDITS["novatio"],
        hero_sub_en="novatio.com.co &middot; Cali, Colombia &middot; Seed &middot; CT-WA-001 &middot; CT-EN-010",
        hero_sub_es="novatio.com.co &middot; Cali, Colombia &middot; Seed &middot; CT-WA-001 &middot; CT-EN-010",
        pitch_en="Social enterprise engineering biodigesters and biogas plants that turn organic waste into clean energy and biofertilizer for rural families and agribusiness.",
        pitch_es="Empresa social de ingeniería en biodigestores y plantas de biogás que convierten residuos orgánicos en energía limpia y biofertilizante para familias rurales y agroindustria.",
        cta_pitch_en="End-to-end methanization projects: design, construction, operation, and compliance for organic waste valorization.",
        cta_pitch_es="Proyectos de metanización integrales: diseño, construcción, operación y cumplimiento para valorización de residuos orgánicos.",
        ribbon=[
            {"val": "CO", "lab_en": "Country", "lab_es": "País", "sub_en": "Colombia", "sub_es": "Colombia"},
            {"val": "Seed", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CLAC23", "sub_es": "CLAC23"},
            {"val": "CT-WA", "lab_en": "Taxonomy", "lab_es": "Taxonomía", "sub_en": "CT-WA-001", "sub_es": "CT-WA-001"},
            {"val": "[P]", "lab_en": "Metrics", "lab_es": "Métricas", "sub_en": "[PENDIENTE]", "sub_es": "[PENDIENTE]"},
        ],
        problem_head_en="Organic waste and wood fuel use drive emissions and health risks in rural Colombia.",
        problem_head_es="Residuos orgánicos y uso de leña generan emisiones y riesgos de salud en zonas rurales de Colombia.",
        problem_body_en="Farming families and processors lack affordable systems to capture methane from organic waste and displace firewood for cooking — missing energy and fertilizer value.",
        problem_body_es="Familias campesinas y procesadores carecen de sistemas accesibles para capturar metano de residuos orgánicos y reemplazar leña para cocción — perdiendo valor energético y fertilizante.",
        stat_row1=[
            {"num": "CLAC23", "lab_en": "Program", "lab_es": "Programa"},
            {"num": "BIC", "lab_en": "Novatio SAS BIC", "lab_es": "Novatio SAS BIC"},
        ],
        stat_row2=[
            {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
            {"num": "Cali", "lab_en": "City", "lab_es": "Ciudad"},
        ],
        solution_steps=[
            {
                "icon": "♻️",
                "label_en": "Digest",
                "label_es": "Digestionar",
                "text_en": "Design and build tubular biodigesters for farms and industrial biogas plants for agro processors.",
                "text_es": "Diseño y construcción de biodigestores tubulares para fincas y plantas de biogás industriales.",
            },
            {
                "icon": "🔥",
                "label_en": "Energize",
                "label_es": "Energizar",
                "text_en": "Convert organic waste into biogas for heat/electricity and displace wood fuel.",
                "text_es": "Convertir residuos orgánicos en biogás para calor/electricidad y desplazar leña.",
            },
            {
                "icon": "🌱",
                "label_en": "Fertilize",
                "label_es": "Fertilizar",
                "text_en": "Produce biofertilizer co-products and support permits, O&amp;M, and impact reporting.",
                "text_es": "Producir biofertilizantes y apoyar permisos, O&amp;M e informes de impacto.",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Portfolio source",
                "title_es": "Fuente portafolio",
                "text_en": "Nexus card NOVATIO (CLAC23) — CT-WA-001 primary, CT-EN-010 secondary.",
                "text_es": "Tarjeta Nexus NOVATIO (CLAC23) — CT-WA-001 primario, CT-EN-010 secundario.",
            },
            {
                "icon": "🤝",
                "title_en": "Triple impact",
                "title_es": "Triple impacto",
                "text_en": "Benefit corporation (BIC) model integrating environmental, social, and economic outcomes (company site).",
                "text_es": "Modelo BIC integrando resultados ambientales, sociales y económicos (sitio empresa).",
            },
        ],
        team_members=[
            {
                "name": "Arnaud Godet",
                "initials": "AG",
                "role_en": "Co-founder &amp; CEO",
                "role_es": "Cofundador y gerente general",
                "bio_en": "Environmental engineer leading Novatio engineering and biogas projects. Source: novatio.com.co / LinkedIn.",
                "bio_es": "Ingeniero ambiental al frente de proyectos de biogás Novatio. Fuente: novatio.com.co / LinkedIn.",
                "linkedin": "https://www.linkedin.com/in/arnaud-godet-3995a326",
            },
            {
                "name": "Quentin Bulcourt",
                "initials": "QB",
                "role_en": "Co-founder &amp; Commercial manager",
                "role_es": "Cofundador y gerente comercial",
                "bio_en": "Commercial lead for biogas and biomethane projects across LATAM. Source: novatio.com.co / LinkedIn.",
                "bio_es": "Líder comercial de proyectos de biogás y biometano en LATAM. Fuente: novatio.com.co / LinkedIn.",
                "linkedin": "https://www.linkedin.com/in/quentin-bulcourt-6643345b",
            },
        ],
        dream_en="Impact figures in BIC reports: not duplicated here without deck verification. Pitch deck: [PENDIENTE].",
        dream_es="Cifras de impacto en reportes BIC: no duplicadas aquí sin verificación de deck. Pitch deck: [PENDIENTE].",
    ),
    portfolio_profile(
        slug="plasticos-ambientales",
        name="Plásticos Ambientales",
        website="https://plasticosambientales.com/",
        badge_en="Circular Plastics &middot; CLAC24 &middot; Acceleration",
        badge_es="Plásticos circulares &middot; CLAC24 &middot; Aceleración",
        hero_image=PAGE_IMAGES["plasticos-ambientales"]["hero"],
        images=PAGE_IMAGES["plasticos-ambientales"],
        credits=IMAGE_CREDITS["plasticos-ambientales"],
        hero_sub_en="plasticosambientales.com &middot; Sabaneta, Colombia &middot; Seed &middot; CT taxonomy: [PENDIENTE]",
        hero_sub_es="plasticosambientales.com &middot; Sabaneta, Colombia &middot; Seed &middot; Taxonomía CT: [PENDIENTE]",
        pitch_en="Certified recycled plastic raw materials and sustainable packaging — helping businesses close the loop and comply with Colombia's circular economy regulations.",
        pitch_es="Materias primas plásticas recicladas certificadas y empaques sostenibles — ayudando a empresas a cerrar el ciclo y cumplir regulación colombiana de economía circular.",
        cta_pitch_en="Capture post-consumer plastics and supply recycled packaging with audited, traceable processes (NTC 6632:2022 certified).",
        cta_pitch_es="Capturar plásticos post-consumo y suministrar empaques reciclados con procesos auditados y trazables (certificación NTC 6632:2022).",
        ribbon=[
            {"val": "CO", "lab_en": "Country", "lab_es": "País", "sub_en": "Colombia", "sub_es": "Colombia"},
            {"val": "Seed", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CLAC24", "sub_es": "CLAC24"},
            {"val": "CE", "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Circular econ.", "sub_es": "Econ. circular"},
            {"val": "[P]", "lab_en": "Metrics", "lab_es": "Métricas", "sub_en": "[PENDIENTE]", "sub_es": "[PENDIENTE]"},
        ],
        problem_head_en="Packaging and plastic waste streams need verified recycling and compliant circular inputs.",
        problem_head_es="Los flujos de empaques y residuos plásticos requieren reciclaje verificado e insumos circulares conformes.",
        problem_body_en="Brands face regulatory pressure on packaging and plastic recovery while needing reliable, certified recycled materials — especially in flexible and post-consumer streams.",
        problem_body_es="Las marcas enfrentan presión regulatoria sobre empaques y recuperación de plásticos mientras necesitan materiales reciclados confiables y certificados — especialmente en flexibles y post-consumo.",
        stat_row1=[
            {"num": "CLAC24", "lab_en": "Program", "lab_es": "Programa"},
            {"num": "CTH", "lab_en": "Acceleration", "lab_es": "Aceleración"},
        ],
        stat_row2=[
            {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
            {"num": "Sabaneta", "lab_en": "City", "lab_es": "Ciudad"},
        ],
        solution_steps=[
            {
                "icon": "♻️",
                "label_en": "Recover",
                "label_es": "Recuperar",
                "text_en": "Formal collection and processing of post-consumer and industrial plastic waste.",
                "text_es": "Recolección y procesamiento formal de residuos plásticos post-consumo e industriales.",
            },
            {
                "icon": "🏭",
                "label_en": "Transform",
                "label_es": "Transformar",
                "text_en": "Pelletizing and quality control under NTC 6632:2022 certified processes (company site).",
                "text_es": "Peletizado y control de calidad bajo procesos certificados NTC 6632:2022 (sitio empresa).",
            },
            {
                "icon": "📦",
                "label_en": "Supply",
                "label_es": "Suministrar",
                "text_en": "Deliver recycled resins and packaging solutions for compliant circular supply chains.",
                "text_es": "Entregar resinas recicladas y empaques para cadenas circulares conformes.",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Portfolio source",
                "title_es": "Fuente portafolio",
                "text_en": "Nexus card PLÁSTICOS AMBIENTALES SAS (CLAC24) — circular packaging / recycled resins.",
                "text_es": "Tarjeta Nexus PLÁSTICOS AMBIENTALES SAS (CLAC24) — empaques circulares / resinas recicladas.",
            },
            {
                "icon": "✅",
                "title_en": "Certification",
                "title_es": "Certificación",
                "text_en": "Public site states certification under NTC 6632:2022 for recycling and production processes.",
                "text_es": "Sitio público indica certificación NTC 6632:2022 para procesos de reciclaje y producción.",
            },
        ],
        team_members=[
            {
                "name": "[PENDIENTE]",
                "initials": "PA",
                "role_en": "Founder / CEO",
                "role_es": "Fundador / CEO",
                "bio_en": "Founder name not verified on public site or portfolio card — [PENDIENTE].",
                "bio_es": "Nombre de fundador no verificado en sitio público ni tarjeta portafolio — [PENDIENTE].",
            },
            {
                "name": "Sandra Martínez",
                "initials": "SM",
                "role_en": "Administrative Director (public role)",
                "role_es": "Directora administrativa (rol público)",
                "bio_en": "Listed as administrative director on public LinkedIn profile; not labeled as founder.",
                "bio_es": "Figura como directora administrativa en perfil LinkedIn público; no indicada como fundadora.",
                "linkedin": "https://www.linkedin.com/in/sandra-mart%C3%ADnez-ba9357104",
            },
        ],
        dream_en="Formal CT taxonomy node on portfolio card: [PENDIENTE]. Production capacity claims on website: not listed as verified KPIs. Pitch deck: [PENDIENTE].",
        dream_es="Nodo CT formal en tarjeta portafolio: [PENDIENTE]. Claims de capacidad en web: no listados como KPIs verificados. Pitch deck: [PENDIENTE].",
    ),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    used: dict[str, str] = {}
    for slug, imgs in PAGE_IMAGES.items():
        for slot, url in imgs.items():
            if url in used:
                raise SystemExit(f"Duplicate image URL in batch 0: {url} ({used[url]} and {slug}.{slot})")
            used[url] = f"{slug}.{slot}"
    for data in STARTUPS:
        path = OUT / f"{data['slug']}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Wrote", path.name)
    manifest = ROOT / "data" / "sheet-s-pages" / "image-sources-batch0.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps({"batch": 0, "pages": IMAGE_CREDITS, "urls": PAGE_IMAGES}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print("Wrote", manifest.relative_to(ROOT))


if __name__ == "__main__":
    main()
