#!/usr/bin/env python3
"""Generate onepager JSON for sheet-s-pages batch 3 (portfolio-sync layout)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "onepagers" / "data"

THEME_SECTOR = {
    "BIO": ("Bio &amp; Agriculture", "Bio y Agricultura"),
    "CE": ("Circular Economy", "Economía Circular"),
    "EN": ("Energy", "Energía"),
}

CT_LABELS = {
    "CT-WA-002": "Organic Waste &amp; Composting",
    "CT-AF-010": "Organic &amp; Regenerative Ag",
    "CT-EN-001": "Solar PV",
    "CT-IC-003": "Supply Chain Platforms",
}


def portfolio_sync_page(
    *,
    slug: str,
    name: str,
    website: str,
    country_en: str,
    country_es: str,
    country_code: str,
    city_en: str,
    city_es: str,
    program: str,
    stage: str,
    theme: str,
    badge_en: str,
    badge_es: str,
    pitch_en: str,
    pitch_es: str,
    problem_en: str,
    problem_es: str,
    focus_en: str,
    focus_es: str,
    market_en: str,
    market_es: str,
    taxonomy_en: str,
    taxonomy_es: str,
    hero_image: str,
    members: list[dict],
    ct1: str = "",
    ct2: str = "",
    kpi_ribbon_val: str = "[P]",
    cta_pitch_en: str = "",
    cta_pitch_es: str = "",
) -> dict:
    sector_en, sector_es = THEME_SECTOR.get(theme, ("Cleantech", "Cleantech"))
    ct_bits = []
    if ct1:
        lab = CT_LABELS.get(ct1, ct1)
        ct_bits.append(f"{ct1} · {lab}")
    if ct2:
        lab = CT_LABELS.get(ct2, ct2)
        ct_bits.append(f"{ct2} · {lab}")
    tax_line_en = taxonomy_en or (" · ".join(ct_bits) if ct_bits else "[PENDIENTE]")
    tax_line_es = taxonomy_es or tax_line_en

    sub_en = f"{website.replace('https://', '')} &middot; {country_en}"
    if city_en and city_en != "PENDIENTE":
        sub_en += f" &middot; {city_en}"
    sub_en += f" &middot; {sector_en} &middot; Stage: {stage}"
    sub_es = f"{website.replace('https://', '')} &middot; {country_es}"
    if city_es and city_es != "PENDIENTE":
        sub_es += f" &middot; {city_es}"
    sub_es += f" &middot; {sector_es} &middot; Etapa: {stage}"

    if not cta_pitch_en:
        cta_pitch_en = pitch_en
    if not cta_pitch_es:
        cta_pitch_es = pitch_es

    return {
        "slug": slug,
        "name": name,
        "website": website,
        "badge_en": badge_en,
        "badge_es": badge_es,
        "hero_image": hero_image,
        "hero_sub_en": sub_en,
        "hero_sub_es": sub_es,
        "pitch_en": pitch_en,
        "pitch_es": pitch_es,
        "cta_pitch_en": cta_pitch_en,
        "cta_pitch_es": cta_pitch_es,
        "cta_btn_en": "Visit website",
        "cta_btn_es": "Visitar sitio",
        "ribbon": [
            {
                "val": country_code,
                "lab_en": "Country",
                "lab_es": "País",
                "sub_en": country_en,
                "sub_es": country_es,
            },
            {
                "val": stage,
                "lab_en": "Stage",
                "lab_es": "Etapa",
                "sub_en": program,
                "sub_es": program,
            },
            {
                "val": theme,
                "lab_en": "Sector",
                "lab_es": "Sector",
                "sub_en": sector_en.replace("&amp;", "&"),
                "sub_es": sector_es,
            },
            {
                "val": kpi_ribbon_val,
                "lab_en": "Metrics",
                "lab_es": "Métricas",
                "sub_en": "[PENDIENTE]" if kpi_ribbon_val == "[P]" else "Portfolio",
                "sub_es": "[PENDIENTE]" if kpi_ribbon_val == "[P]" else "Portafolio",
            },
        ],
        "problem_stats": [
            [
                {
                    "num": "[P]",
                    "lab_en": "KPIs pending",
                    "lab_es": "KPIs pendientes",
                },
                {
                    "num": country_code,
                    "lab_en": country_en,
                    "lab_es": country_es,
                },
            ]
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
                "bg": hero_image,
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
                        "text_en": focus_en,
                        "text_es": focus_es,
                    },
                    {
                        "icon": "📋",
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
                "bg": hero_image,
            },
            {
                "num": 3,
                "type": "impact",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "Impact &amp; Program",
                "title_es": "Impacto y Programa",
                "cards": [
                    {
                        "icon": "📚",
                        "title_en": "Wiki source",
                        "title_es": "Fuente Wiki",
                        "text_en": "Profile synced from BookStack Startup Portfolio + public web sources (Acceleration cohort).",
                        "text_es": "Perfil sincronizado desde BookStack Startup Portfolio + fuentes web públicas (cohorte Acceleration).",
                    },
                    {
                        "icon": "🏷️",
                        "title_en": "Taxonomy",
                        "title_es": "Taxonomía",
                        "text_en": tax_line_en,
                        "text_es": tax_line_es,
                    },
                ],
                "bg": hero_image,
            },
            {
                "num": 4,
                "type": "team",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "Leadership",
                "title_es": "Liderazgo",
                "members": members,
                "dream_en": f"Program: {program}. City: {city_en}. Pitch deck on profile: [PENDIENTE]. Verified KPIs: [PENDIENTE].",
                "dream_es": f"Programa: {program}. Ciudad: {city_es}. Pitch deck en perfil: [PENDIENTE]. KPIs verificados: [PENDIENTE].",
                "bg": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&q=80",
            },
        ],
    }


PAGES = [
    portfolio_sync_page(
        slug="greenify",
        name="Greenify",
        website="https://greenify.world",
        country_en="Colombia",
        country_es="Colombia",
        country_code="CO",
        city_en="PENDIENTE",
        city_es="PENDIENTE",
        program="Acceleration",
        stage="PENDIENTE",
        theme="EN",
        badge_en="Carbon Footprint Platform &middot; Cero Huella SAS",
        badge_es="Plataforma de Huella de Carbono &middot; Cero Huella SAS",
        pitch_en="App and SaaS platform helping people and companies measure, reduce, and offset CO₂ emissions through certified projects, education, and gamified climate action.",
        pitch_es="App y plataforma SaaS que ayudan a personas y empresas a medir, reducir y compensar emisiones de CO₂ mediante proyectos certificados, educación y acción climática gamificada.",
        problem_en="Organizations and individuals lack simple, trusted tools to quantify carbon footprints and turn sustainability commitments into measurable action.",
        problem_es="Organizaciones y personas carecen de herramientas simples y confiables para cuantificar la huella de carbono y convertir compromisos de sostenibilidad en acción medible.",
        focus_en="Digital carbon management combining measurement, reduction guidance, and verified offset pathways (Cero Huella SAS / Greenify).",
        focus_es="Gestión digital de carbono que combina medición, guía de reducción y vías de compensación verificada (Cero Huella SAS / Greenify).",
        market_en="Based in Colombia. Public site: greenify.world. Mobile app published under Cero Huella SAS (Apple App Store).",
        market_es="Con base en Colombia. Sitio público: greenify.world. App móvil publicada por Cero Huella SAS (Apple App Store).",
        taxonomy_en="Climate software &amp; carbon management — CT taxonomy code: [PENDIENTE].",
        taxonomy_es="Software climático y gestión de carbono — código taxonomía CT: [PENDIENTE].",
        hero_image="https://images.unsplash.com/photo-1473341304170-971dccb5ac71?w=1200&q=80",
        members=[
            {
                "name": "Diego Felipe Castaño Valero",
                "role_en": "Co-founder &amp; CFO &middot; Greenify",
                "role_es": "Cofundador y CFO &middot; Greenify",
                "bio_en": "Public-facing role: Co-founder &amp; CFO at Greenify_Col (LinkedIn).",
                "bio_es": "Rol público: Cofundador y CFO en Greenify_Col (LinkedIn).",
                "linkedin": "https://www.linkedin.com/in/diego-felipe-casta%C3%B1o-valero-aa3aab62",
                "initials": "DC",
            },
        ],
    ),
    portfolio_sync_page(
        slug="habitat-a-vibe-company",
        name="Hábitat Minería Urbana",
        website="https://habitatmineriaurbana.com.co",
        country_en="Colombia",
        country_es="Colombia",
        country_code="CO",
        city_en="Bogotá / Tocancipá",
        city_es="Bogotá / Tocancipá",
        program="CLAC24 · Acceleration",
        stage="Seed",
        theme="CE",
        badge_en="Urban Mining &middot; E-waste &middot; CLAC24",
        badge_es="Minería Urbana &middot; RAEE &middot; CLAC24",
        pitch_en="Urban mining company recovering plastics and metals from electrical and electronic waste, converting them into raw materials while generating employment for recyclers in low-income communities.",
        pitch_es="Empresa de minería urbana que recupera plásticos y metales de residuos eléctricos y electrónicos, convirtiéndolos en materias primas mientras genera empleo para recicladores en comunidades vulnerables.",
        problem_en="Electrical and electronic waste streams lose valuable materials while informal handling creates environmental and social risks in Colombian cities.",
        problem_es="Los flujos de residuos eléctricos y electrónicos pierden materiales valiosos mientras el manejo informal genera riesgos ambientales y sociales en ciudades colombianas.",
        focus_en="Licensed collection, dismantling, and recovery of WEEE (RAEE) for circular raw materials — CI Hábitat a Vibe Company SAS.",
        focus_es="Recolección, desensamble y recuperación licenciada de RAEE para materias primas circulares — CI Hábitat a Vibe Company SAS.",
        market_en="Based in Colombia (Bogotá / Tocancipá). Public site: habitatmineriaurbana.com.co.",
        market_es="Con base en Colombia (Bogotá / Tocancipá). Sitio público: habitatmineriaurbana.com.co.",
        taxonomy_en="Urban mining &amp; e-waste recovery — CT taxonomy: [PENDIENTE].",
        taxonomy_es="Minería urbana y recuperación de RAEE — taxonomía CT: [PENDIENTE].",
        hero_image="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80",
        members=[
            {
                "name": "Javier Eduardo Pacheco",
                "role_en": "Director of Circular Economy &middot; Hábitat Minería Urbana",
                "role_es": "Director de Economía Circular &middot; Hábitat Minería Urbana",
                "bio_en": "Public-facing role: Director of Circular Economy (LinkedIn). E-waste and urban mining specialist.",
                "bio_es": "Rol público: Director de Economía Circular (LinkedIn). Especialista en RAEE y minería urbana.",
                "linkedin": "https://www.linkedin.com/in/javier-eduardo-pacheco-a09091197",
                "initials": "JP",
            },
            {
                "name": "José Isaí Santamaría Roncancio",
                "role_en": "Director of Sustainability &middot; CI Hábitat a Vibe Company SAS",
                "role_es": "Director de Sostenibilidad &middot; CI Hábitat a Vibe Company SAS",
                "bio_en": "Public-facing role: Director of Sustainability at CI Hábitat a Vibe Company SAS (LinkedIn).",
                "bio_es": "Rol público: Director de Sostenibilidad en CI Hábitat a Vibe Company SAS (LinkedIn).",
                "linkedin": "https://www.linkedin.com/in/jos%C3%A9-isa%C3%AD-santamar%C3%ADa-roncancio-a0316a5b",
                "initials": "JS",
            },
        ],
    ),
    portfolio_sync_page(
        slug="ciclorganicos",
        name="Ciclorgánicos",
        website="https://www.ciclorganicos.com",
        country_en="Colombia",
        country_es="Colombia",
        country_code="CO",
        city_en="Medellín / Caldas",
        city_es="Medellín / Caldas",
        program="CLAC22 · Acceleration",
        stage="Seed",
        theme="BIO",
        badge_en="Organic Waste &middot; Compost &middot; CLAC22",
        badge_es="Residuos Orgánicos &middot; Compost &middot; CLAC22",
        pitch_en="Collects organic residues from the food industry and composts them into certified biofertilizers with traceable waste-reduction data.",
        pitch_es="Recolecta residuos orgánicos de la industria alimentaria y los composta en biofertilizantes certificados con datos trazables de reducción de residuos.",
        problem_en="Organic waste from food industry and cities generates methane and lost nutrients when sent to landfill instead of regenerative soil inputs.",
        problem_es="Los residuos orgánicos de la industria alimentaria y las ciudades generan metano y pierden nutrientes cuando van a relleno en lugar de insumos regenerativos para el suelo.",
        focus_en="Collection, mechanical composting, and certified soil improvers (Bio Abonos GAIA S.A.S. BIC — Ciclorgánicos).",
        focus_es="Recolección, compostaje con volteo mecánico y mejoradores de suelo certificados (Bio Abonos GAIA S.A.S. BIC — Ciclorgánicos).",
        market_en="Based in Antioquia, Colombia. Public site: ciclorganicos.com. Portfolio notes ~200 tonnes/month collected (CleantechHUB card).",
        market_es="Con base en Antioquia, Colombia. Sitio público: ciclorganicos.com. Tarjeta CleantechHUB: ~200 toneladas/mes recolectadas.",
        taxonomy_en="CT-WA-002 · Organic Waste &amp; Composting; CT-AF-010 · Organic &amp; Regenerative Ag.",
        taxonomy_es="CT-WA-002 · Residuos orgánicos y compostaje; CT-AF-010 · Ag orgánica y regenerativa.",
        hero_image="https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80",
        ct1="CT-WA-002",
        ct2="CT-AF-010",
        members=[
            {
                "name": "Jaime Alberto Escobar",
                "role_en": "General Manager &middot; Ciclorgánicos / Bio Abonos GAIA",
                "role_es": "Gerente General &middot; Ciclorgánicos / Bio Abonos GAIA",
                "bio_en": "Public-facing role: General Manager at Ciclorgánicos (LinkedIn). Leads organic waste valorization and compost operations.",
                "bio_es": "Rol público: Gerente General en Ciclorgánicos (LinkedIn). Lidera valorización de residuos orgánicos y operaciones de compostaje.",
                "linkedin": "https://www.linkedin.com/in/jaime-alberto-e-7684b6162",
                "initials": "JE",
            },
        ],
        cta_pitch_en="Close the loop on organic waste — from food industry residues to certified compost and GAIA soil improvers.",
        cta_pitch_es="Cierre el ciclo de residuos orgánicos — de la industria alimentaria al compost certificado y mejoradores GAIA.",
    ),
    portfolio_sync_page(
        slug="cobox-logistic",
        name="Cobox Logistic",
        website="https://www.coboxlogistic.com",
        country_en="Peru",
        country_es="Perú",
        country_code="PE",
        city_en="Lima",
        city_es="Lima",
        program="Acceleration",
        stage="PENDIENTE",
        theme="CE",
        badge_en="Collaborative Logistics &middot; Green Miles",
        badge_es="Logística Colaborativa &middot; Green Miles",
        pitch_en="Collaborative logistics platform centralizing last-mile delivery, fulfillment, and reverse logistics for SMEs and e-commerce, with sustainability via Green Miles carbon measurement.",
        pitch_es="Plataforma de logística colaborativa que centraliza última milla, fulfillment y logística inversa para MYPES y e-commerce, con sostenibilidad vía medición Green Miles.",
        problem_en="Micro and small businesses face high logistics costs, fragmented carriers, and limited visibility — while last-mile emissions stay unmeasured.",
        problem_es="Las micro y pequeñas empresas enfrentan altos costos logísticos, transportistas fragmentados y poca visibilidad — mientras las emisiones de última milla no se miden.",
        focus_en="Multi-carrier logistics orchestration, fulfillment, COD, and reverse logistics (Recycle Route) on one digital platform.",
        focus_es="Orquestación logística multi-operador, fulfillment, contraentrega y logística inversa (Recycle Route) en una sola plataforma digital.",
        market_en="Based in Lima, Peru. Public site: coboxlogistic.com. Press reports cite ~40% logistics cost reduction for SME users (Calidad &amp; Negocios, 2025).",
        market_es="Con base en Lima, Perú. Sitio público: coboxlogistic.com. Prensa cita ~40% de reducción de costos logísticos para MYPES (Calidad &amp; Negocios, 2025).",
        taxonomy_en="Circular logistics &amp; supply-chain digitization — CT taxonomy: [PENDIENTE].",
        taxonomy_es="Logística circular y digitalización de cadena — taxonomía CT: [PENDIENTE].",
        hero_image="https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1200&q=80",
        members=[
            {
                "name": "Jaime Polo Fernández",
                "role_en": "Co-founder &amp; COO &middot; Cobox Logistic",
                "role_es": "Cofundador y COO &middot; Cobox Logistic",
                "bio_en": "Public-facing role: Co-founder / COO (LinkedIn, Cobox Logistic company posts).",
                "bio_es": "Rol público: Cofundador / COO (LinkedIn, publicaciones de Cobox Logistic).",
                "linkedin": "https://www.linkedin.com/in/jaime-polo-fernandez",
                "initials": "JP",
            },
            {
                "name": "Max Elias Figueroa Huaman",
                "role_en": "Co-founder &middot; Cobox Logistic",
                "role_es": "Cofundador &middot; Cobox Logistic",
                "bio_en": "Public-facing role: Co-founder (Calidad &amp; Negocios, 2025; INCUBA UNPRG, 2025). LinkedIn URL: [PENDIENTE].",
                "bio_es": "Rol público: Cofundador (Calidad &amp; Negocios, 2025; INCUBA UNPRG, 2025). URL LinkedIn: [PENDIENTE].",
                "initials": "MF",
            },
        ],
    ),
]


def main() -> None:
    for page in PAGES:
        path = OUT / f"{page['slug']}.json"
        path.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n")
        print("Wrote", path.name)


if __name__ == "__main__":
    main()
