#!/usr/bin/env python3
"""Write onepager JSON for sheet-s-pages batch index 4 (Portafolio Acceleration)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "onepagers" / "data"


def portfolio_page(
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
    problem_stats: list,
    solution_steps: list,
    impact_cards: list,
    team_members: list,
    dream_en: str,
    dream_es: str,
    problem_bg: str,
    solution_bg: str,
    impact_bg: str,
    team_bg: str,
    cta_bg: str,
    image_credits_en: str,
    image_credits_es: str,
    cta_btn_en: str = "Visit website",
    cta_btn_es: str = "Visitar sitio",
) -> dict:
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
        "cta_btn_en": cta_btn_en,
        "cta_btn_es": cta_btn_es,
        "cta_bg": cta_bg,
        "image_credits_en": image_credits_en,
        "image_credits_es": image_credits_es,
        "ribbon": ribbon,
        "problem_stats": problem_stats,
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
                "bg": problem_bg,
            },
            {
                "num": 2,
                "type": "solution",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "The Solution",
                "title_es": "La Solución",
                "steps": solution_steps,
                "bg": solution_bg,
            },
            {
                "num": 3,
                "type": "impact",
                "overlay": "rgba(102,147,72,.30)",
                "title_en": "Impact &amp; Program",
                "title_es": "Impacto y Programa",
                "cards": impact_cards,
                "bg": impact_bg,
            },
            {
                "num": 4,
                "type": "team",
                "overlay": "rgba(12,73,138,.30)",
                "title_en": "Leadership",
                "title_es": "Liderazgo",
                "members": team_members,
                "dream_en": dream_en,
                "dream_es": dream_es,
                "bg": team_bg,
            },
        ],
    }


PAGES = [
    portfolio_page(
        slug="ala-terra",
        name="¡Ala Terra!",
        website="https://alaterra.com.mx",
        badge_en="Food systems &middot; CleantechHUB Acceleration",
        badge_es="Sistemas alimentarios &middot; Aceleración CleantechHUB",
        hero_image="https://assets.cdn.filesafe.space/RIkiXtFxRLDEnKoJeszB/media/6ac919e9bbad531ac8581ef8.png",
        hero_sub_en="alaterra.com.mx &middot; Mexico &middot; Guadalajara &middot; Food systems &middot; Stage: [PENDIENTE] &middot; CT-WA-003",
        hero_sub_es="alaterra.com.mx &middot; México &middot; Guadalajara &middot; Sistemas alimentarios &middot; Etapa: [PENDIENTE] &middot; CT-WA-003",
        pitch_en="Rescues local surplus fruit into 100% fruit + chile snacks with no added sugar and no warning labels — school-friendly, reducing food waste.",
        pitch_es="Rescata fruta local excedente en snacks 100% fruta + chilito, sin azúcar añadida y sin sellos — aptos para escuelas, reduciendo desperdicio alimentario.",
        cta_pitch_en="Healthy, label-free fruit snacks that turn rescued produce into shelf-stable products aligned with Mexico's Vida Saludable norms.",
        cta_pitch_es="Snacks saludables sin sellos que convierten fruta rescatada en productos de anaquel, alineados con la normativa Vida Saludable en México.",
        ribbon=[
            {"val": "MX", "lab_en": "Country", "lab_es": "País", "sub_en": "Mexico", "sub_es": "México"},
            {"val": "[P]", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CTH Accel.", "sub_es": "Acel. CTH"},
            {"val": "Food", "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Cleantech", "sub_es": "Cleantech"},
            {"val": "CT-WA-003", "lab_en": "CT Taxonomy", "lab_es": "Taxonomía CT", "sub_en": "CTH", "sub_es": "CTH"},
        ],
        problem_head_en="Cosmetic standards and supply chains leave edible fruit unsold, adding to food waste and lost value for growers.",
        problem_head_es="Los estándares estéticos y las cadenas de suministro dejan fruta comestible sin vender, aumentando el desperdicio y la pérdida de valor para productores.",
        problem_body_en="¡Ala Terra! addresses food waste from fruit that does not meet conventional market appearance, while offering healthier snack options for families and schools.",
        problem_body_es="¡Ala Terra! aborda el desperdicio de fruta que no cumple estándares estéticos del mercado, mientras ofrece opciones de snack más saludables para familias y escuelas.",
        problem_stats=[
            [
                {"num": "CTH", "lab_en": "Acceleration", "lab_es": "Aceleración"},
                {"num": "CTH", "lab_en": "Hub", "lab_es": "Hub"},
            ],
            [
                {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
                {"num": "MX", "lab_en": "Mexico", "lab_es": "México"},
            ],
        ],
        solution_steps=[
            {
                "icon": "🍍",
                "label_en": "Focus",
                "label_es": "Enfoque",
                "text_en": "Rescue local fruit (e.g. mango, pineapple, banana) and process it into 100% fruit strips with chile — no added sugar.",
                "text_es": "Rescata fruta local (p. ej. mango, piña, plátano) y la procesa en tiras 100% fruta con chilito — sin azúcar añadida.",
            },
            {
                "icon": "🔗",
                "label_en": "Program",
                "label_es": "Programa",
                "text_en": "¡Ala Terra! — CleantechHUB Acceleration portfolio (Portafolio CTH).",
                "text_es": "¡Ala Terra! — portafolio Aceleración CleantechHUB (Portafolio CTH).",
            },
            {
                "icon": "🌎",
                "label_en": "Market",
                "label_es": "Mercado",
                "text_en": "Based in Mexico (Jalisco). Public site: alaterra.com.mx.",
                "text_es": "Con base en México (Jalisco). Sitio público: alaterra.com.mx.",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Wiki / portfolio source",
                "title_es": "Fuente portafolio",
                "text_en": "Profile aligned with CleantechHUB Acceleration sheet entry &ldquo;Come ala terra&rdquo; and public brand ¡Ala Terra!.",
                "text_es": "Perfil alineado con la entrada &ldquo;Come ala terra&rdquo; del Portafolio Aceleración CTH y la marca pública ¡Ala Terra!.",
            },
            {
                "icon": "🎯",
                "title_en": "Taxonomy",
                "title_es": "Taxonomía",
                "text_en": "Food waste &amp; rescued produce &middot; CT-WA-003 (pending full CTH validation).",
                "text_es": "Desperdicio alimentario y fruta rescatada &middot; CT-WA-003 (validación CTH completa pendiente).",
            },
        ],
        team_members=[
            {
                "name": "Ana Cristina Dorantes",
                "role_en": "CEO &amp; Co-founder &middot; ¡Ala Terra!",
                "role_es": "CEO y cofundadora &middot; ¡Ala Terra!",
                "bio_en": "Public-facing founder/CEO of ¡Ala Terra! and CEO of FOODLAB (Mexico). Source: company site + LinkedIn.",
                "bio_es": "Fundadora/CEO pública de ¡Ala Terra! y CEO de FOODLAB (México). Fuente: sitio de la empresa + LinkedIn.",
                "initials": "AD",
                "linkedin": "https://www.linkedin.com/in/ana-cristina-dorantes-27502148",
            },
            {
                "name": "[PENDIENTE]",
                "role_en": "Co-founder &middot; ¡Ala Terra!",
                "role_es": "Cofundador(a) &middot; ¡Ala Terra!",
                "bio_en": "Site references &ldquo;fundadoras&rdquo; (plural); second named co-founder not verified from public sources.",
                "bio_es": "El sitio menciona &ldquo;fundadoras&rdquo; (plural); segunda cofundadora nombrada no verificada en fuentes públicas.",
                "initials": "?",
            },
        ],
        dream_en="Program: CleantechHUB Acceleration. City (HQ): Guadalajara area [public LinkedIn]. Verified KPIs: [PENDIENTE]. Pitch deck: [PENDIENTE].",
        dream_es="Programa: Aceleración CleantechHUB. Ciudad (HQ): área Guadalajara [LinkedIn público]. KPIs verificados: [PENDIENTE]. Pitch deck: [PENDIENTE].",
        problem_bg="https://images.unsplash.com/photo-1542838132-92c53300491e?w=1200&q=80",
        solution_bg="https://images.unsplash.com/photo-1601493700633-866a8a0a4b4c?w=1200&q=80",
        impact_bg="https://images.unsplash.com/photo-1560493676-2b0e20a0eae2?w=1200&q=80",
        team_bg="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=1200&q=80",
        cta_bg="https://images.unsplash.com/photo-1511690743690-d985d126e174?w=1200&q=80",
        image_credits_en=(
            "Hero: product photo, <a href=\"https://alaterra.com.mx\" rel=\"noopener\" target=\"_blank\">alaterra.com.mx</a>. "
            "Sec.1 Unsplash <a href=\"https://unsplash.com/photos/1542838132-92c53300491e\" rel=\"noopener\" target=\"_blank\">food market produce</a>. "
            "Sec.2 Unsplash <a href=\"https://unsplash.com/photos/1601493700633-866a8a0a4b4c\" rel=\"noopener\" target=\"_blank\">dried fruit snacks</a>. "
            "Sec.3 Unsplash <a href=\"https://unsplash.com/photos/1560493676-2b0e20a0eae2\" rel=\"noopener\" target=\"_blank\">fruit orchard</a>. "
            "Sec.4 Unsplash <a href=\"https://unsplash.com/photos/1573496359142-b8d87734a5a2\" rel=\"noopener\" target=\"_blank\">team collaboration</a>. "
            "CTA Unsplash <a href=\"https://unsplash.com/photos/1511690743690-d985d126e174\" rel=\"noopener\" target=\"_blank\">healthy meal prep</a>."
        ),
        image_credits_es=(
            "Hero: foto de producto, <a href=\"https://alaterra.com.mx\" rel=\"noopener\" target=\"_blank\">alaterra.com.mx</a>. "
            "Sec.1 Unsplash <a href=\"https://unsplash.com/photos/1542838132-92c53300491e\" rel=\"noopener\" target=\"_blank\">mercado de frutas</a>. "
            "Sec.2 Unsplash <a href=\"https://unsplash.com/photos/1601493700633-866a8a0a4b4c\" rel=\"noopener\" target=\"_blank\">snacks de fruta deshidratada</a>. "
            "Sec.3 Unsplash <a href=\"https://unsplash.com/photos/1560493676-2b0e20a0eae2\" rel=\"noopener\" target=\"_blank\">huerto frutal</a>. "
            "Sec.4 Unsplash <a href=\"https://unsplash.com/photos/1573496359142-b8d87734a5a2\" rel=\"noopener\" target=\"_blank\">equipo colaborando</a>. "
            "CTA Unsplash <a href=\"https://unsplash.com/photos/1511690743690-d985d126e174\" rel=\"noopener\" target=\"_blank\">comida saludable</a>."
        ),
    ),
    portfolio_page(
        slug="compostpack",
        name="COMPOSTPACK",
        website="https://compostpack.com",
        badge_en="Circular Economy &middot; CLAC23",
        badge_es="Economía circular &middot; CLAC23",
        hero_image="https://compostpack.com/_astro/hero-bg.3beQTwYG_AvyNh.webp",
        hero_sub_en="compostpack.com &middot; Colombia &middot; Bogotá &middot; Circular economy &middot; Stage: Seed &middot; CT-WA-004 &middot; CT-IN-003",
        hero_sub_es="compostpack.com &middot; Colombia &middot; Bogotá &middot; Economía circular &middot; Etapa: Seed &middot; CT-WA-004 &middot; CT-IN-003",
        pitch_en="Develops and commercializes certified compostable bioplastics and packaging that decompose without microplastics for food and retail.",
        pitch_es="Desarrolla y comercializa bioplásticos y empaques compostables certificados que se descomponen sin microplásticos para alimentos y retail.",
        cta_pitch_en="Compostable resin grades (CPK) for bags, thermoforming, and injection — genuinely compostable materials for a cleaner packaging chain.",
        cta_pitch_es="Grados de resina compostable (CPK) para bolsas, termoformado e inyección — materiales genuinamente compostables para una cadena de empaque más limpia.",
        ribbon=[
            {"val": "Seed", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CLAC23", "sub_es": "CLAC23"},
            {"val": "CE", "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Circular", "sub_es": "Circular"},
            {"val": "CT-WA-004", "lab_en": "CT Taxonomy", "lab_es": "Taxonomía CT", "sub_en": "CT-IN-003", "sub_es": "CT-IN-003"},
            {"val": "CO", "lab_en": "Country", "lab_es": "País", "sub_en": "Colombia", "sub_es": "Colombia"},
        ],
        problem_head_en="Single-use plastic packaging accumulates in soils and waterways; Colombia needs circular alternatives that meet international compostability standards.",
        problem_head_es="Los empaques plásticos de un solo uso se acumulan en suelos y cuerpos de agua; Colombia necesita alternativas circulares que cumplan normas internacionales de compostabilidad.",
        problem_body_en="COMPOSTPACK manufactures compostable bioplastics from biological sources, targeting contamination from conventional plastics in packaging and retail.",
        problem_body_es="COMPOSTPACK fabrica bioplásticos compostables a partir de fuentes biológicas, abordando la contaminación por plásticos convencionales en empaques y retail.",
        problem_stats=[
            [
                {"num": "CLAC23", "lab_en": "Program", "lab_es": "Programa"},
                {"num": "CTH", "lab_en": "Hub", "lab_es": "Hub"},
            ],
            [
                {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
                {"num": "CO", "lab_en": "Colombia", "lab_es": "Colombia"},
            ],
        ],
        solution_steps=[
            {
                "icon": "🌱",
                "label_en": "Focus",
                "label_es": "Enfoque",
                "text_en": "Compostable biopolymer grades (CPK) for extrusion, thermoforming, and injection — starch-rich feedstocks.",
                "text_es": "Grados de biopolímeros compostables (CPK) para extrusión, termoformado e inyección — materias primas ricas en almidón.",
            },
            {
                "icon": "🔗",
                "label_en": "Program",
                "label_es": "Programa",
                "text_en": "COMPOSTPACK — CLAC23 CleantechHUB portfolio.",
                "text_es": "COMPOSTPACK — portafolio CLAC23 CleantechHUB.",
            },
            {
                "icon": "🌎",
                "label_en": "Market",
                "label_es": "Mercado",
                "text_en": "Based in Bogotá, Colombia. Public site: compostpack.com.",
                "text_es": "Con base en Bogotá, Colombia. Sitio público: compostpack.com.",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Wiki source",
                "title_es": "Fuente Wiki",
                "text_en": "Profile synced from BookStack Startup Portfolio + public site (compostable packaging, UNCCD supporter).",
                "text_es": "Perfil sincronizado desde BookStack Startup Portfolio + sitio público (empaques compostables, apoyo UNCCD).",
            },
            {
                "icon": "🎯",
                "title_en": "Taxonomy",
                "title_es": "Taxonomía",
                "text_en": "Extended Producer Responsibility &amp; Circular Economy &amp; Clean Manufacturing (CT-WA-004, CT-IN-003).",
                "text_es": "Responsabilidad extendida del productor y economía circular y manufactura limpia (CT-WA-004, CT-IN-003).",
            },
        ],
        team_members=[
            {
                "name": "Freddy Carrión Rivas",
                "role_en": "Co-founder &amp; Manager &middot; COMPOSTPACK",
                "role_es": "Cofundador y gerente &middot; COMPOSTPACK",
                "bio_en": "Co-founder; leads Compostpack (Carpios group). Public interviews and LinkedIn list manager role since 2018.",
                "bio_es": "Cofundador; lidera Compostpack (grupo Carpios). Entrevistas públicas y LinkedIn listan rol de gerente desde 2018.",
                "initials": "FC",
                "linkedin": "https://www.linkedin.com/in/freddycarrion",
            }
        ],
        dream_en="Program: CLAC23. HQ: Bogotá (public site). Additional founders: [PENDIENTE]. Verified revenue/KPIs: [PENDIENTE].",
        dream_es="Programa: CLAC23. HQ: Bogotá (sitio público). Cofundadores adicionales: [PENDIENTE]. Ingresos/KPIs verificados: [PENDIENTE].",
        problem_bg="https://compostpack.com/_astro/bio-1.DPQUHzAZ_1iqsYP.webp",
        solution_bg="https://compostpack.com/_astro/packaging.B07ehvl2_Nh3FK.webp",
        impact_bg="https://compostpack.com/_astro/cicle.C0gTuyTd_1wVAk7.webp",
        team_bg="https://compostpack.com/_astro/about-img.Bj8waJdW_Z2dJUwv.webp",
        cta_bg="https://compostpack.com/_astro/kitchen.CNSoMGiK_ZhNWiI.webp",
        image_credits_en=(
            "Hero–CTA: product &amp; application photos, <a href=\"https://compostpack.com\" rel=\"noopener\" target=\"_blank\">compostpack.com</a> "
            "(hero-bg, bio-1, packaging, cicle, about-img, kitchen assets)."
        ),
        image_credits_es=(
            "Hero–CTA: fotos de producto y aplicación, <a href=\"https://compostpack.com\" rel=\"noopener\" target=\"_blank\">compostpack.com</a> "
            "(hero-bg, bio-1, packaging, cicle, about-img, kitchen)."
        ),
    ),
    portfolio_page(
        slug="cr-tejas",
        name="CR Tejas",
        website="#",
        badge_en="Sustainable construction &middot; CleantechHUB Acceleration",
        badge_es="Construcción sostenible &middot; Aceleración CleantechHUB",
        hero_image="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200&q=80",
        hero_sub_en="[PENDIENTE] &middot; Costa Rica &middot; [PENDIENTE] city &middot; Stage: [PENDIENTE] &middot; CT: [PENDIENTE]",
        hero_sub_es="[PENDIENTE] &middot; Costa Rica &middot; ciudad [PENDIENTE] &middot; Etapa: [PENDIENTE] &middot; CT: [PENDIENTE]",
        pitch_en="Costa Rica venture listed in CleantechHUB Acceleration portfolio as CR Tejas — public one-liner pending verification.",
        pitch_es="Empresa de Costa Rica listada en el portafolio de Aceleración CleantechHUB como CR Tejas — one-liner público pendiente de verificación.",
        cta_pitch_en="CleantechHUB Acceleration cohort company from Portafolio CTH sheet (Costa Rica).",
        cta_pitch_es="Empresa cohorte Aceleración CleantechHUB del Portafolio CTH (Costa Rica).",
        cta_btn_en="CleantechHUB",
        cta_btn_es="CleantechHUB",
        ribbon=[
            {"val": "CR", "lab_en": "Country", "lab_es": "País", "sub_en": "Costa Rica", "sub_es": "Costa Rica"},
            {"val": "[P]", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CTH Accel.", "sub_es": "Acel. CTH"},
            {"val": "[P]", "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Pending", "sub_es": "Pendiente"},
            {"val": "[P]", "lab_en": "CT Taxonomy", "lab_es": "Taxonomía CT", "sub_en": "Pending", "sub_es": "Pendiente"},
        ],
        problem_head_en="[PENDIENTE] — Insufficient verified public information to describe the climate problem statement for CR Tejas.",
        problem_head_es="[PENDIENTE] — Información pública verificada insuficiente para describir el problema climático de CR Tejas.",
        problem_body_en="CleantechHUB portfolio entry &ldquo;CR Tejas&rdquo; (Costa Rica, Acceleration). Website, solution detail, and CT taxonomy: [PENDIENTE].",
        problem_body_es="Entrada de portafolio CleantechHUB &ldquo;CR Tejas&rdquo; (Costa Rica, Aceleración). Sitio web, detalle de solución y taxonomía CT: [PENDIENTE].",
        problem_stats=[
            [
                {"num": "CTH", "lab_en": "Acceleration", "lab_es": "Aceleración"},
                {"num": "CTH", "lab_en": "Hub", "lab_es": "Hub"},
            ],
            [
                {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
                {"num": "CR", "lab_en": "Costa Rica", "lab_es": "Costa Rica"},
            ],
        ],
        solution_steps=[
            {
                "icon": "🏠",
                "label_en": "Focus",
                "label_es": "Enfoque",
                "text_en": "[PENDIENTE] — Awaiting verified public description of CR Tejas product/service.",
                "text_es": "[PENDIENTE] — Descripción pública verificada del producto/servicio de CR Tejas pendiente.",
            },
            {
                "icon": "🔗",
                "label_en": "Program",
                "label_es": "Programa",
                "text_en": "CR Tejas — CleantechHUB Acceleration (Portafolio CTH sheet).",
                "text_es": "CR Tejas — Aceleración CleantechHUB (hoja Portafolio CTH).",
            },
            {
                "icon": "🌎",
                "label_en": "Market",
                "label_es": "Mercado",
                "text_en": "Costa Rica. Verified website: [PENDIENTE].",
                "text_es": "Costa Rica. Sitio web verificado: [PENDIENTE].",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Portfolio source",
                "title_es": "Fuente portafolio",
                "text_en": "Listed in Gideon Portafolio CTH / sheet-s-pages batch (Acceleration, Costa Rica).",
                "text_es": "Listada en Portafolio CTH de Gideon / batch sheet-s-pages (Aceleración, Costa Rica).",
            },
            {
                "icon": "🎯",
                "title_en": "Taxonomy",
                "title_es": "Taxonomía",
                "text_en": "CT node assignment: [PENDIENTE] (not in public Nexus portfolio card set).",
                "text_es": "Nodo CT: [PENDIENTE] (no aparece en tarjetas públicas del portafolio Nexus).",
            },
        ],
        team_members=[
            {
                "name": "[PENDIENTE]",
                "role_en": "Founder &middot; CR Tejas",
                "role_es": "Fundador(a) &middot; CR Tejas",
                "bio_en": "Founder name and public LinkedIn URL not verified via open web search.",
                "bio_es": "Nombre del fundador y URL pública de LinkedIn no verificados vía búsqueda web abierta.",
                "initials": "?",
            }
        ],
        dream_en="Program: CleantechHUB Acceleration. All KPIs, website, founders, city: [PENDIENTE].",
        dream_es="Programa: Aceleración CleantechHUB. KPIs, sitio web, fundadores, ciudad: [PENDIENTE].",
        problem_bg="https://images.unsplash.com/photo-1621451537820-82a5f0f4e3c4?w=1200&q=80",
        solution_bg="https://images.unsplash.com/photo-1600607687644-aac4c3f77262?w=1200&q=80",
        impact_bg="https://images.unsplash.com/photo-1600047509797-3c03256c43ae?w=1200&q=80",
        team_bg="https://images.unsplash.com/photo-1504307659764-4472212f024e?w=1200&q=80",
        cta_bg="https://images.unsplash.com/photo-1605276371049-43ff84389e45?w=1200&q=80",
        image_credits_en=(
            "All photos Unsplash (Costa Rica / eco-roofing context; no verified CR Tejas website). "
            "Hero <a href=\"https://unsplash.com/photos/be6161a56a0c\" rel=\"noopener\" target=\"_blank\">Daniel Moises D. Magallanes</a>. "
            "Sec.1 <a href=\"https://unsplash.com/photos/82a5f0f4e3c4\" rel=\"noopener\" target=\"_blank\">plastic waste</a>. "
            "Sec.2 <a href=\"https://unsplash.com/photos/aac4c3f77262\" rel=\"noopener\" target=\"_blank\">modern roofline</a>. "
            "Sec.3 <a href=\"https://unsplash.com/photos/3c03256c43ae\" rel=\"noopener\" target=\"_blank\">green home</a>. "
            "Sec.4 <a href=\"https://unsplash.com/photos/4472212f024e\" rel=\"noopener\" target=\"_blank\">construction team</a>. "
            "CTA <a href=\"https://unsplash.com/photos/43ff84389e45\" rel=\"noopener\" target=\"_blank\">tropical rooftop</a>."
        ),
        image_credits_es=(
            "Todas las fotos Unsplash (contexto tejas/eco-techo CR; sin sitio verificado de CR Tejas). "
            "Hero <a href=\"https://unsplash.com/photos/be6161a56a0c\" rel=\"noopener\" target=\"_blank\">Daniel Moises D. Magallanes</a>. "
            "Sec.1 <a href=\"https://unsplash.com/photos/82a5f0f4e3c4\" rel=\"noopener\" target=\"_blank\">residuos plásticos</a>. "
            "Sec.2 <a href=\"https://unsplash.com/photos/aac4c3f77262\" rel=\"noopener\" target=\"_blank\">cubierta moderna</a>. "
            "Sec.3 <a href=\"https://unsplash.com/photos/3c03256c43ae\" rel=\"noopener\" target=\"_blank\">vivienda verde</a>. "
            "Sec.4 <a href=\"https://unsplash.com/photos/4472212f024e\" rel=\"noopener\" target=\"_blank\">equipo de obra</a>. "
            "CTA <a href=\"https://unsplash.com/photos/43ff84389e45\" rel=\"noopener\" target=\"_blank\">techo tropical</a>."
        ),
    ),
    portfolio_page(
        slug="deposito-global-recycling",
        name="Deposito Global Recycling",
        website="#",
        badge_en="Circular Economy &middot; CleantechHUB Acceleration",
        badge_es="Economía circular &middot; Aceleración CleantechHUB",
        hero_image="https://images.unsplash.com/photo-1605810230434-3341a1193435?w=1200&q=80",
        hero_sub_en="[PENDIENTE] &middot; Colombia &middot; Cali &middot; Stage: [PENDIENTE] &middot; CT: [PENDIENTE]",
        hero_sub_es="[PENDIENTE] &middot; Colombia &middot; Cali &middot; Etapa: [PENDIENTE] &middot; CT: [PENDIENTE]",
        pitch_en="Colombian company Deposito Global Recycling S.A.S. (Cali) listed in CleantechHUB Acceleration portfolio — cleantech positioning pending public verification.",
        pitch_es="Empresa colombiana Deposito Global Recycling S.A.S. (Cali) en portafolio Aceleración CleantechHUB — posicionamiento cleantech pendiente de verificación pública.",
        cta_pitch_en="Legal entity registered in Cali, Valle del Cauca; public website and climate solution narrative: [PENDIENTE].",
        cta_pitch_es="Persona jurídica registrada en Cali, Valle del Cauca; sitio web y narrativa climática pública: [PENDIENTE].",
        cta_btn_en="CleantechHUB",
        cta_btn_es="CleantechHUB",
        ribbon=[
            {"val": "CO", "lab_en": "Country", "lab_es": "País", "sub_en": "Colombia", "sub_es": "Colombia"},
            {"val": "[P]", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CTH Accel.", "sub_es": "Acel. CTH"},
            {"val": "CE", "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Assumed", "sub_es": "Supuesto"},
            {"val": "[P]", "lab_en": "CT Taxonomy", "lab_es": "Taxonomía CT", "sub_en": "Pending", "sub_es": "Pendiente"},
        ],
        problem_head_en="[PENDIENTE] — No verified public materials describing the environmental problem Deposito Global Recycling addresses.",
        problem_head_es="[PENDIENTE] — Sin materiales públicos verificados que describan el problema ambiental que aborda Deposito Global Recycling.",
        problem_body_en="Registry data lists retail of hardware/paint/glass (Cali); alignment with recycling/circular operations requires CTH confirmation — not asserted here.",
        problem_body_es="Datos registrales listan comercio de ferretería/pintura/vidrio (Cali); alineación con reciclaje/circularidad requiere confirmación CTH — no se afirma aquí.",
        problem_stats=[
            [
                {"num": "CTH", "lab_en": "Acceleration", "lab_es": "Aceleración"},
                {"num": "CTH", "lab_en": "Hub", "lab_es": "Hub"},
            ],
            [
                {"num": "[P]", "lab_en": "KPIs pending", "lab_es": "KPIs pendientes"},
                {"num": "CO", "lab_en": "Colombia", "lab_es": "Colombia"},
            ],
        ],
        solution_steps=[
            {
                "icon": "♻️",
                "label_en": "Focus",
                "label_es": "Enfoque",
                "text_en": "[PENDIENTE] — Solution description not available from verified public marketing or CTH wiki.",
                "text_es": "[PENDIENTE] — Descripción de la solución no disponible en marketing público verificado ni wiki CTH.",
            },
            {
                "icon": "🔗",
                "label_en": "Program",
                "label_es": "Programa",
                "text_en": "Deposito Global Recycling SAS — CleantechHUB Acceleration sheet entry.",
                "text_es": "Deposito Global Recycling SAS — entrada hoja Aceleración CleantechHUB.",
            },
            {
                "icon": "🌎",
                "label_en": "Market",
                "label_es": "Mercado",
                "text_en": "Cali, Valle del Cauca, Colombia (registry). Website: [PENDIENTE].",
                "text_es": "Cali, Valle del Cauca, Colombia (registro). Sitio web: [PENDIENTE].",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Registry source",
                "title_es": "Fuente registral",
                "text_en": "Active SAS registration in Cali (public business directories); activity code: retail hardware/paint/glass — interpret with care.",
                "text_es": "Matrícula SAS activa en Cali (directorios públicos); código de actividad: comercio ferretería/pintura/vidrio — interpretar con cautela.",
            },
            {
                "icon": "🎯",
                "title_en": "Taxonomy",
                "title_es": "Taxonomía",
                "text_en": "CT taxonomy: [PENDIENTE]. Not listed on public Nexus portfolio grid.",
                "text_es": "Taxonomía CT: [PENDIENTE]. No listada en la grilla pública del portafolio Nexus.",
            },
        ],
        team_members=[
            {
                "name": "[PENDIENTE]",
                "role_en": "Leadership &middot; Deposito Global Recycling",
                "role_es": "Liderazgo &middot; Deposito Global Recycling",
                "bio_en": "Legal representatives / founders not identified from public-safe sources.",
                "bio_es": "Representantes legales / fundadores no identificados en fuentes públicas seguras.",
                "initials": "?",
            }
        ],
        dream_en="Program: CleantechHUB Acceleration. City: Cali (registry). KPIs, website, founders: [PENDIENTE].",
        dream_es="Programa: Aceleración CleantechHUB. Ciudad: Cali (registro). KPIs, sitio web, fundadores: [PENDIENTE].",
        problem_bg="https://images.unsplash.com/photo-1618477387244-4fe1e0532c8b?w=1200&q=80",
        solution_bg="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80",
        impact_bg="https://images.unsplash.com/photo-1466611336591-6d7dc2924b5c?w=1200&q=80",
        team_bg="https://images.unsplash.com/photo-1586528116311-0b29ce79f1a6?w=1200&q=80",
        cta_bg="https://images.unsplash.com/photo-1611284447374-40f2c1a89c45?w=1200&q=80",
        image_credits_en=(
            "All Unsplash (recycling / materials trade context; no verified company website). "
            "Hero <a href=\"https://unsplash.com/photos/3341a1193435\" rel=\"noopener\" target=\"_blank\">recycling facility</a>. "
            "Sec.1 <a href=\"https://unsplash.com/photos/4fe1e0532c8b\" rel=\"noopener\" target=\"_blank\">plastic bottles</a>. "
            "Sec.2 <a href=\"https://unsplash.com/photos/fcd25c85cd64\" rel=\"noopener\" target=\"_blank\">sorting line</a>. "
            "Sec.3 <a href=\"https://unsplash.com/photos/6d7dc2924b5c\" rel=\"noopener\" target=\"_blank\">forest stewardship</a>. "
            "Sec.4 <a href=\"https://unsplash.com/photos/0b29ce79f1a6\" rel=\"noopener\" target=\"_blank\">warehouse</a>. "
            "CTA <a href=\"https://unsplash.com/photos/40f2c1a89c45\" rel=\"noopener\" target=\"_blank\">scrap materials</a>."
        ),
        image_credits_es=(
            "Todo Unsplash (contexto reciclaje/comercio de materiales; sin sitio verificado de la empresa). "
            "Hero <a href=\"https://unsplash.com/photos/3341a1193435\" rel=\"noopener\" target=\"_blank\">planta de reciclaje</a>. "
            "Sec.1 <a href=\"https://unsplash.com/photos/4fe1e0532c8b\" rel=\"noopener\" target=\"_blank\">botellas plásticas</a>. "
            "Sec.2 <a href=\"https://unsplash.com/photos/fcd25c85cd64\" rel=\"noopener\" target=\"_blank\">línea de clasificación</a>. "
            "Sec.3 <a href=\"https://unsplash.com/photos/6d7dc2924b5c\" rel=\"noopener\" target=\"_blank\">bosque</a>. "
            "Sec.4 <a href=\"https://unsplash.com/photos/0b29ce79f1a6\" rel=\"noopener\" target=\"_blank\">bodega</a>. "
            "CTA <a href=\"https://unsplash.com/photos/40f2c1a89c45\" rel=\"noopener\" target=\"_blank\">materiales reciclables</a>."
        ),
    ),
    portfolio_page(
        slug="deterquin",
        name="DETERQUIN",
        website="https://deterquin.com",
        badge_en="Circular Economy &middot; CLAC25",
        badge_es="Economía circular &middot; CLAC25",
        hero_image="https://deterquin.com/sites/default/files/soluciones/slider-principal-pagina-web-FINAL-11-12-23.jpg",
        hero_sub_en="deterquin.com &middot; Colombia &middot; Cali &middot; Circular economy &middot; Stage: Seed &middot; CT-WA-004",
        hero_sub_es="deterquin.com &middot; Colombia &middot; Cali &middot; Economía circular &middot; Etapa: Seed &middot; CT-WA-004",
        pitch_en="Eco-friendly ultraconcentrated detergents and starch-based adhesives for industrial laundry and hospitality, cutting plastic via Eco Pacs format.",
        pitch_es="Detergentes ultraconcentrados eco-amigables y adhesivos a base de almidón para lavandería industrial y hostelería, reduciendo plástico con formato Eco Pacs.",
        cta_pitch_en="360° cleaning and laundry programs with concentrated chemistry, technical support, and sustainability positioning for institutional clients.",
        cta_pitch_es="Programas 360° de limpieza y lavandería con química concentrada, soporte técnico y enfoque de sostenibilidad para clientes institucionales.",
        ribbon=[
            {"val": "Seed", "lab_en": "Stage", "lab_es": "Etapa", "sub_en": "CLAC25", "sub_es": "CLAC25"},
            {"val": "CE", "lab_en": "Sector", "lab_es": "Sector", "sub_en": "Circular", "sub_es": "Circular"},
            {"val": "CT-WA-004", "lab_en": "CT Taxonomy", "lab_es": "Taxonomía CT", "sub_en": "CTH", "sub_es": "CTH"},
            {"val": "CO", "lab_en": "Country", "lab_es": "País", "sub_en": "Colombia", "sub_es": "Colombia"},
        ],
        problem_head_en="Industrial cleaning and laundry rely on bulky plastic packaging and concentrated chemicals with high water-shipping footprint.",
        problem_head_es="La limpieza y lavandería industrial dependen de empaques plásticos voluminosos y químicos concentrados con alta huella logística de agua.",
        problem_body_en="DETERQUIN develops ultraconcentrated, eco-friendly detergents and starch-based adhesives, including Eco Pacs designed to reduce plastic waste in professional cleaning.",
        problem_body_es="DETERQUIN desarrolla detergentes ultraconcentrados eco-amigables y adhesivos a base de almidón, incluido Eco Pacs para reducir residuos plásticos en limpieza profesional.",
        problem_stats=[
            [
                {"num": "CLAC25", "lab_en": "Program", "lab_es": "Programa"},
                {"num": "CTH", "lab_en": "Hub", "lab_es": "Hub"},
            ],
            [
                {"num": "50k", "lab_en": "kg plastic avoided (site)", "lab_es": "kg plástico evitado (web)"},
                {"num": "CO", "lab_en": "Colombia", "lab_es": "Colombia"},
            ],
        ],
        solution_steps=[
            {
                "icon": "🧴",
                "label_en": "Focus",
                "label_es": "Enfoque",
                "text_en": "Ultraconcentrated detergents, professional cleaning programs, and starch-based eco adhesives for industry.",
                "text_es": "Detergentes ultraconcentrados, programas de limpieza profesional y adhesivos eco a base de almidón para industria.",
            },
            {
                "icon": "🔗",
                "label_en": "Program",
                "label_es": "Programa",
                "text_en": "DETERQUIN SAS — CLAC25 CleantechHUB portfolio.",
                "text_es": "DETERQUIN SAS — portafolio CLAC25 CleantechHUB.",
            },
            {
                "icon": "🌎",
                "label_en": "Market",
                "label_es": "Mercado",
                "text_en": "Based in Cali, Colombia. Public site: deterquin.com.",
                "text_es": "Con base en Cali, Colombia. Sitio público: deterquin.com.",
            },
        ],
        impact_cards=[
            {
                "icon": "📋",
                "title_en": "Wiki source",
                "title_es": "Fuente Wiki",
                "text_en": "Profile synced from BookStack Startup Portfolio + public website.",
                "text_es": "Perfil sincronizado desde BookStack Startup Portfolio + sitio web público.",
            },
            {
                "icon": "📊",
                "title_en": "Reported impact (website)",
                "title_es": "Impacto reportado (web)",
                "text_en": "Public site cites 50,000 kg less plastic, 694,000 fewer plastic bottles, and 101,000 kg less CO₂ (not independently audited here).",
                "text_es": "El sitio público cita 50.000 kg menos de plástico, 694.000 botellas menos y 101.000 kg menos de CO₂ (sin auditoría independiente aquí).",
            },
        ],
        team_members=[
            {
                "name": "Gonzalo Andrés Duque González",
                "role_en": "Operations &amp; R&amp;D Manager &middot; DETERQUIN",
                "role_es": "Gerente Operaciones e I+D &middot; DETERQUIN",
                "bio_en": "Leads operations and R&amp;D at family-owned Deterquin; founder of Eco Pacs spin-off. Source: LinkedIn + public profiles.",
                "bio_es": "Lidera operaciones e I+D en Deterquin familiar; fundador del spin-off Eco Pacs. Fuente: LinkedIn + perfiles públicos.",
                "initials": "GD",
                "linkedin": "https://www.linkedin.com/in/gonzalo-andr%C3%A9s-duque-gonzalez-7b311b36",
            },
            {
                "name": "Lina Maria Duque Gonzalez",
                "role_en": "Commercial General Manager &middot; DETERQUIN",
                "role_es": "Gerente General Comercial &middot; DETERQUIN",
                "bio_en": "Commercial general manager at Deterquin (family company, Cali). Source: LinkedIn.",
                "bio_es": "Gerente general comercial en Deterquin (empresa familiar, Cali). Fuente: LinkedIn.",
                "initials": "LD",
                "linkedin": "https://www.linkedin.com/in/lina-maria-duque-gonzalez-51b01757",
            },
        ],
        dream_en="Program: CLAC25. HQ: Cali (public site). ISO 9001 cited on third-party directory — [PENDIENTE] primary-source link. Pitch deck: [PENDIENTE].",
        dream_es="Programa: CLAC25. HQ: Cali (sitio público). ISO 9001 citada en directorio tercero — enlace fuente primaria [PENDIENTE]. Pitch deck: [PENDIENTE].",
        problem_bg="https://deterquin.com/sites/default/files/home/deterquin-limpieza-profesional-home-1.jpg",
        solution_bg="https://deterquin.com/sites/default/files/imagenes/slider-principal-pagina-web-eco-pacs--hogar-linea-hogar.jpg",
        impact_bg="https://deterquin.com/sites/default/files/soluciones/eco-amigables.jpg",
        team_bg="https://deterquin.com/sites/default/files/soluciones/lavanderia-y-cuidado-textil.jpg",
        cta_bg="https://deterquin.com/sites/default/files/home/home-procesamiento-de-alimentos-y-bebidas-2.jpg",
        image_credits_en=(
            "Hero–CTA: marketing photos, <a href=\"https://deterquin.com\" rel=\"noopener\" target=\"_blank\">deterquin.com</a> "
            "(home slider, professional cleaning, Eco Pacs, eco adhesives, laundry, food-processing lines)."
        ),
        image_credits_es=(
            "Hero–CTA: fotos de marketing, <a href=\"https://deterquin.com\" rel=\"noopener\" target=\"_blank\">deterquin.com</a> "
            "(slider principal, limpieza profesional, Eco Pacs, eco-amigables, lavandería, alimentos y bebidas)."
        ),
    ),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        path = OUT / f"{page['slug']}.json"
        path.write_text(json.dumps(page, indent=2, ensure_ascii=False) + "\n")
        print("wrote", path.name)


if __name__ == "__main__":
    main()
