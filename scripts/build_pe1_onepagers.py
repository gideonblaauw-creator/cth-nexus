#!/usr/bin/env python3
"""Generate CLP26 PE1 one-pager HTML (nexus-PE1 brief)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "onepagers" / "template" / "styles.css").read_text()
EXTRA_CSS = """
.deck-slide-img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;display:block;background:#fff;}
.tax-pending{color:#ffe08a;font-weight:700;}
"""

SLIDE_COUNT = 9
PAGER_JS = """<script>(function(){var root=document.currentScript.previousElementSibling;if(!root)return;var img=root.parentElement.querySelector('.deck-slide-img');var label=root.querySelector('.deck-page-label');var total=+root.dataset.pages||1;var prefix=root.dataset.prefix||'';var ext=root.dataset.ext||'.jpg';var page=1;function show(n){page=Math.max(1,Math.min(total,n));if(img)img.src=prefix+page+ext;if(label)label.textContent=page+' / '+total;root.querySelectorAll('.deck-page-btn').forEach(function(b){var dir=+b.dataset.dir;b.disabled=dir<0?page<=1:page>=total;});}root.addEventListener('click',function(e){var b=e.target.closest('.deck-page-btn');if(!b||b.disabled)return;show(page+(+b.dataset.dir||0));});show(1);})();</script>"""


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def deck_section(slug: str, name: str, drive_id: str, bg: str) -> str:
    view = f"https://drive.google.com/file/d/{drive_id}/view"
    prefix = f"/s/{slug}/slides/s-"
    return f'''<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('{bg}');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="sec-header"><div class="sec-num">📄</div><div class="sec-title">{bi("Pitch Deck", "Pitch Deck")}</div><div class="sec-rule"></div></div><div class="deck-note">{bi("Slide images from the deck — numbers on this profile match the deck only.", "Diapositivas del deck — los números en este perfil provienen solo del deck.")}</div><div class="deck-wrap deck-slide-wrap"><div class="deck-panel deck-slide"><div class="deck-frame-wrap"><img class="deck-frame deck-slide-img" src="{prefix}1.jpg" alt="{name} pitch deck slide 1" loading="lazy"></div><div class="deck-pager" data-prefix="{prefix}" data-pages="{SLIDE_COUNT}" data-ext=".jpg"><button type="button" class="deck-page-btn" data-dir="-1">{bi("Prev", "Anterior")}</button><span class="deck-page-label">1 / {SLIDE_COUNT}</span><button type="button" class="deck-page-btn" data-dir="1">{bi("Next", "Siguiente")}</button></div>{PAGER_JS}<div class="deck-fallback">{bi("Need the full file?", "¿Necesita el archivo completo?")} <a href="{view}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a></div></div><div class="deck-actions"><a class="cta-link" href="{view}" target="_blank" rel="noopener">{bi("Open deck in Google Drive", "Abrir deck en Google Drive")}</a></div></div></div><div class="accent-bar"></div>'''


def hidden_video(bg: str) -> str:
    return f'''<div class="sec" hidden><div class="sec-bg" style="background-image:url('{bg}');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="sec-header"><div class="sec-num">▶</div><div class="sec-title">{bi("Pitch Video", "Video pitch")}</div><div class="sec-rule"></div></div><div class="deck-wrap"><div class="yt-pitch"><div class="yt-pitch-frame"><iframe src="" title="YouTube pitch" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div></div></div></div>'''


def hidden_founders(bg: str) -> str:
    return f'''<div class="sec" hidden aria-hidden="true"><div class="sec-bg" style="background-image:url('{bg}');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="sec-header"><div class="sec-num">07</div><div class="sec-title">{bi("Founders", "Fundadores")}</div><div class="sec-rule"></div></div><div class="team-grid"><div class="team-card"><div class="tp-avatar" style="background:linear-gradient(135deg,var(--fo),var(--lg));">—</div><div class="tp-name">{bi("[Name pending]", "[Nombre pendiente]")}</div><div class="tp-role">{bi("[Role]", "[Rol]")}</div><a class="tp-link" href="#">{bi("LinkedIn", "LinkedIn")}</a></div></div></div>'''


STARTUPS = [
    {
        "slug": "agrolens",
        "name": "AgroLens",
        "drive_id": "1SL-H4P4mSW4wIyNEitwjLQCma79_MyRZ",
        "hero_img": "https://images.unsplash.com/photo-1625246333195-78d9c090ad85?w=1200&q=80",
        "badge_en": "CT-AF-007 · Precision Agri Data",
        "badge_es": "CT-AF-007 · Datos Agrícolas de Precisión",
        "sub_en": "PE · CLP26 · Private Beta · Hass avocado monitoring",
        "sub_es": "PE · CLP26 · Beta privada · Monitoreo palta Hass",
        "pitch_en": "Recurring integral agricultural monitoring for export avocado — drone, station, and platform operated by AgroLens so growers know where to act sooner.",
        "pitch_es": "Monitoreo agrícola integral recurrente para palta de exportación — dron, estación y plataforma operados por AgroLens para que el productor sepa dónde actuar antes.",
        "ribbon": [
            ("$100", "Per ha / year", "Deck pricing", "Por ha / año", "Precio deck"),
            ("$15k", "150 ha / year", "Example deal", "150 ha / año", "Ejemplo deal"),
            ("18", "Customers", "→ $270k ARR", "Clientes", "→ US$270k ARR"),
            ("92%", "Problem relevant", "Validation", "Problema relevante", "Validación"),
        ],
        "problem_en": "Current monitoring is manual, late, or forces growers to buy and operate hardware. Agroexport managers and agronomists see climate stress and inspection gaps as a real, costly problem.",
        "problem_es": "El monitoreo actual es manual, tardío o obliga al productor a comprar y operar hardware. Gerentes y agrónomos de agroexportación ven el estrés climático y la inspección tardía como un problema real y costoso.",
        "problem_stats": [("92%", "Problem relevant", "Problema relevante"), ("84%", "Prefers service", "Prefiere servicio"), ("$18.5k", "WTP vs offer", "Disposición pago"), ("18", "Customers today", "Clientes hoy")],
        "solution_steps": [
            ("🛰️", "Monitor", "Monitorear", "Recurring drone + station coverage across the farm.", "Cobertura recurrente con dron y estación en el fundo."),
            ("🧠", "Model", "Modelar", "Computer-vision and agronomic models flag zones needing action.", "Modelos de visión y agronomía marcan zonas que requieren acción."),
            ("🌐", "Platform", "Plataforma", "Web platform used by the customer team for weekly review.", "Plataforma web usada por el equipo del cliente para revisión semanal."),
            ("🚁", "Operate", "Operar", "AgroLens installs, maintains, and runs field deployments.", "AgroLens instala, mantiene y ejecuta despliegues en campo."),
        ],
        "market_note_en": "18 customers at US$270k ARR; deck cites Peruvian SAM scale toward US$6.5M ARR and 431 potential clients in Hass avocado.",
        "market_note_es": "18 clientes con US$270k ARR; el deck cita escala SAM Perú hacia US$6,5M ARR y 431 clientes potenciales en palta Hass.",
        "impact": [
            ("🌡️", "Early stress", "Estrés temprano", "Detect climate stress before manual inspection reaches every zone.", "Detectar estrés climático antes de que la inspección manual cubra cada zona."),
            ("⏱️", "Time to act", "Tiempo para actuar", "Weekly fundo review gives agronomists more time to respond.", "Revisión semanal del fundo da más tiempo al agrónomo para responder."),
            ("📍", "2,700 ha", "2.700 ha", "Year-3 target: 2,700 ha under recurring monitoring.", "Meta año 3: 2.700 ha bajo monitoreo recurrente."),
            ("🥑", "Hass focus", "Foco Hass", "Beachhead: 150 ha Hass farms; validation across mango and blueberry.", "Beachhead: fundos Hass 150 ha; validación en mango y arándano."),
        ],
        "frost_en": "Secondary CT: CT-IC-005 · Precision Ag & Smart Grid. Website: [PENDIENTE]. Founders: pending LinkedIn HITL.",
        "frost_es": "CT secundario: CT-IC-005 · Ag de Precisión y Red Inteligente. Web: [PENDIENTE]. Fundadores: pendiente LinkedIn HITL.",
        "cta_en": "Recurring monitoring as a service — US$100/ha/year on 150 ha Hass export farms.",
        "cta_es": "Monitoreo recurrente como servicio — US$100/ha/año en fundos Hass de exportación de 150 ha.",
    },
    {
        "slug": "andean-biofactories",
        "name": "Andean Biofactories",
        "drive_id": "137esrBbb4nMgiEfNTudV3TfX5_8epFG0",
        "hero_img": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80",
        "badge_en": "CT-AF-010 · Organic & Regenerative Ag",
        "badge_es": "CT-AF-010 · Ag Orgánica y Regenerativa",
        "sub_en": "PE · CLP26 · Sketches · Community biofactory",
        "sub_es": "PE · CLP26 · Bocetos · Biofactoría comunitaria",
        "pitch_en": "Community biofactory-as-a-service cultivating local food, health, and independence — sold to mining companies as social investment with measurable community nutrition outcomes.",
        "pitch_es": "Biofactoría comunitaria como servicio que cultiva alimento, salud e independencia local — vendida a mineras como inversión social con resultados medibles en nutrición comunitaria.",
        "ribbon": [
            ("$24k", "Per community / yr", "Deck offer", "Por comunidad / año", "Oferta deck"),
            ("12", "Miners today", "Peru signals", "Mineras hoy", "Señales Perú"),
            ("$5.7M", "Social invest.", "Last 3 years", "Inversión social", "Últimos 3 años"),
            ("100", "Communities", "2031 vision", "Comunidades", "Visión 2031"),
        ],
        "problem_en": "Highland communities face costly, hard-to-access protein and anemia linked to carb-heavy diets. Public and private programs buy results, not one-off donations.",
        "problem_es": "Comunidades altoandinas enfrentan proteína costosa y difícil acceso, y anemia ligada a dietas altas en carbohidratos. Programas públicos y privados compran resultados, no donaciones puntuales.",
        "problem_stats": [("$24k", "Annual fee", "Tarifa anual"), ("Mining", "Beachhead buyer", "Comprador beachhead"), ("Modular", "Biofactory", "Biofactoría"), ("Local", "Fortified food", "Alimento fortificado")],
        "solution_steps": [
            ("🏭", "Biofactory", "Biofactoría", "Modular automated community biofactory producing local food.", "Biofactoría comunitaria modular y automatizada que produce alimento local."),
            ("🤝", "Adoption", "Adopción", "Continuous integral service so the community can operate with support.", "Servicio integral continuo para que la comunidad adopte con acompañamiento."),
            ("📊", "ESG", "ESG", "Mining clients fund social budgets with reportable nutrition impact.", "Clientes mineros financian presupuesto social con impacto en nutrición reportable."),
            ("🍪", "Output", "Resultado", "Fortified products such as fortified biscuits for beneficiaries.", "Productos fortificados como galleta fortificada para beneficiarios."),
        ],
        "market_note_en": "Deck segments mining social investment in Peru (e.g. US$5.7M over three years) and scales a vision across LATAM miners and Andean communities.",
        "market_note_es": "El deck segmenta inversión social minera en Perú (p. ej. US$5,7M en tres años) y escala una visión en mineras LATAM y comunidades andinas.",
        "impact": [
            ("🌄", "Food sovereignty", "Soberanía alimentaria", "Local production, knowledge, and accompaniment for community nutrition.", "Producción local, conocimiento y acompañamiento para nutrición comunitaria."),
            ("👥", "Beneficiaries", "Beneficiarios", "Programs compared by cost per beneficiary in deck segmentation.", "Programas comparados por costo por beneficiario en segmentación del deck."),
            ("🎯", "2031", "2031", "Vision: 100 high-Andean communities producing sustainable nutrition year-round.", "Visión: 100 comunidades altoandinas produciendo nutrición sostenible todo el año."),
            ("⚙️", "Team", "Equipo", "Multidisciplinary team spanning data, machines, quality, and biotech.", "Equipo multidisciplinario en datos, máquinas, calidad y biotecnología."),
        ],
        "frost_en": "Secondary CT: CT-AF-009 · Bioeconomy & NbS. Website: [PENDIENTE]. Founders: pending LinkedIn HITL.",
        "frost_es": "CT secundario: CT-AF-009 · Bioeconomía y NbS. Web: [PENDIENTE]. Fundadores: pendiente LinkedIn HITL.",
        "cta_en": "Turn mining social investment into measurable local nutrition — US$24k/community/year.",
        "cta_es": "Convertir inversión social minera en nutrición local medible — US$24k/comunidad/año.",
    },
    {
        "slug": "fivra",
        "name": "FIVRA",
        "drive_id": "1XBoqfBw718P4SHTV_KG8fNcTV68UT5Oq",
        "hero_img": "https://images.unsplash.com/photo-1558176638-b876e8132b4f?w=1200&q=80",
        "badge_en": "CT-IN-003 · Circular Economy & Clean Mfg",
        "badge_es": "CT-IN-003 · Economía Circular y Manufactura Limpia",
        "sub_en": "PE · CLP26 · Public Beta · AI textile tech packs",
        "sub_es": "PE · CLP26 · Beta pública · Fichas técnicas textiles con IA",
        "pitch_en": "AI-generated textile tech packs that cut production waste — from about US$4 per ficha, built for entrepreneurs with limited technical knowledge in LATAM apparel.",
        "pitch_es": "Fichas técnicas textiles generadas con IA para reducir desperdicio — desde ~US$4 por ficha, para emprendedores con poco conocimiento técnico en confección LATAM.",
        "ribbon": [
            ("$4", "From / ficha", "Deck entry", "Desde / ficha", "Entrada deck"),
            ("-60%", "Remuestreos", "Deck claim", "Remuestreos", "Cifra deck"),
            ("500", "Clients Y1", "Impact model", "Clientes A1", "Modelo impacto"),
            ("46k", "Peru firms", "Statista ref.", "Empresas PE", "Ref. Statista"),
        ],
        "problem_en": "Textile entrepreneurs lack accessible tools to start production with fewer errors and less fabric waste before cutting.",
        "problem_es": "Emprendedores textiles carecen de herramientas accesibles para iniciar producción con menos errores y menos desperdicio de tela antes del corte.",
        "problem_stats": [("$4", "Starter price", "Precio entrada"), ("IA", "Tech packs", "Fichas IA"), ("LATAM", "Textile focus", "Foco textil"), ("-60%", "Samples", "Muestras")],
        "solution_steps": [
            ("📋", "Tech pack", "Ficha técnica", "Complete specs, back view via AI, production risk analysis.", "Especificaciones completas, vista posterior con IA, análisis de riesgos."),
            ("♻️", "Materials", "Materiales", "Suggestions for more sustainable materials in each ficha.", "Sugerencias de materiales más sostenibles en cada ficha."),
            ("✂️", "Waste", "Desperdicio", "Fabric waste optimization before production runs.", "Optimización de desperdicio de tela antes de producir."),
            ("📦", "Plans", "Planes", "Starter, Basic, and Pro packages for ficha purchases.", "Paquetes Starter, Basic y Pro para adquisición de fichas."),
        ],
        "market_note_en": "Beachhead: agile textile entrepreneurs in LATAM; deck cites Peru company counts and Lima entrepreneur figures from listed sources.",
        "market_note_es": "Beachhead: emprendedores textiles ágiles en LATAM; el deck cita conteos de empresas en Perú y emprendedores en Lima según fuentes indicadas.",
        "impact": [
            ("🧵", "Fichas sold", "Fichas vendidas", "Impact model: 500 clients × 66 fichas/year → 33,000 fichas/year.", "Modelo: 500 clientes × 66 fichas/año → 33.000 fichas/año."),
            ("📉", "Resampling", "Remuestreos", "Up to ~60% fewer resampling rounds in deck scenario.", "Hasta ~60% menos remuestreos en escenario del deck."),
            ("⚖️", "~5.9 t", "~5,9 t", "Potential textile sample waste avoided (~0.3 kg/sample).", "Desperdicio potencial de muestras textiles evitado (~0,3 kg/muestra)."),
            ("🌱", "Pre-cut", "Pre-corte", "Acts before cutting: fewer unnecessary samples and better production decisions.", "Actúa antes del corte: menos muestras innecesarias y mejores decisiones."),
        ],
        "frost_en": "Website: [PENDIENTE]. Founders: pending LinkedIn HITL.",
        "frost_es": "Web: [PENDIENTE]. Fundadores: pendiente LinkedIn HITL.",
        "cta_en": "Prevent textile waste before the first cut — AI tech packs from US$4/ficha.",
        "cta_es": "Prevenir desperdicio textil antes del primer corte — fichas con IA desde US$4/ficha.",
    },
    {
        "slug": "hardtech",
        "name": "HardTech",
        "drive_id": "1kuMsv2sFItitkiHVFccNUmFyW22FZQF3",
        "hero_img": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
        "badge_en": "Taxonomy pending",
        "badge_es": "Taxonomía pendiente",
        "badge_class": "tax-pending",
        "sub_en": "PE · CLP26 · Prototype · SiC ingots",
        "sub_es": "PE · CLP26 · Prototipo · Lingotes SiC",
        "pitch_en": "Patented lower-energy synthesis of silicon carbide (SiC) ingots for microelectronics manufacturers — B2B advanced material at US$15k/ingot in the deck.",
        "pitch_es": "Síntesis patentada de lingotes de carburo de silicio (SiC) con menor energía para fabricantes de microelectrónica — materia prima B2B a US$15k/lingote en el deck.",
        "ribbon": [
            ("$15k", "Per ingot", "Deck offer", "Por lingote", "Oferta deck"),
            ("5", "Days / ingot", "HardTech", "Días / lingote", "HardTech"),
            ("-5,400", "t CO₂ eq.", "vs conventional", "t CO₂ eq.", "vs convencional"),
            ("USPTO", "63/724,867", "Patent pending", "Patente", "Pendiente"),
        ],
        "problem_en": "Conventional high-temperature SiC synthesis is energy-intensive and slow; manufacturers need reliable advanced SiC feedstock.",
        "problem_es": "La síntesis convencional de SiC a alta temperatura consume mucha energía y es lenta; fabricantes requieren materia prima SiC avanzada confiable.",
        "problem_stats": [("7→5", "Days / ingot", "Días / lingote"), ("B2B", "SiC ingots", "Lingotes SiC"), ("USA", "Market refs", "Refs. mercado"), ("Demand", "Verified", "Demanda")],
        "solution_steps": [
            ("🔥", "Process", "Proceso", "Patented furnace synthesis with thermal reduction and closed loop.", "Síntesis en horno patentada con reducción térmica y circuito cerrado."),
            ("⚡", "Energy", "Energía", "Deck shows lower equivalent CO₂ vs conventional ingot cycle.", "El deck muestra menor CO₂ equivalente vs ciclo convencional."),
            ("📜", "IP", "PI", "USPTO patent application 63/724,867 cited in deck.", "Solicitud USPTO 63/724,867 citada en el deck."),
            ("🏭", "Customer", "Cliente", "Target: microelectronics and integrated circuit manufacturers.", "Objetivo: fabricantes de microelectrónica e circuitos integrados."),
        ],
        "market_note_en": "Deck references US manufacturer segments and year 1 / year 3 sales framing; taxonomy CT node left empty pending HITL (LOW_CONFIDENCE_TAXONOMY).",
        "market_note_es": "El deck referencia segmentos de fabricantes en EE.UU. y marco ventas año 1 / 3; nodo CT vacío pendiente HITL (LOW_CONFIDENCE_TAXONOMY).",
        "impact": [
            ("🌍", "CO₂", "CO₂", "Deck: 13,616 t vs 19,063 t CO₂ equivalent per ingot cycle (5 vs 7 days).", "Deck: 13.616 t vs 19.063 t CO₂ equivalente por ciclo (5 vs 7 días)."),
            ("💧", "ODS 6", "ODS 6", "Aligned with UN SDGs including water and affordable energy.", "Alineado con ODS ONU incluyendo agua y energía asequible."),
            ("🏭", "ODS 9", "ODS 9", "Industry innovation and infrastructure alignment in deck.", "Alineación con industria e innovación en el deck."),
            ("📋", "Taxonomy", "Taxonomía", "Visible note: taxonomy pending — do not assign CT code until reviewed.", "Nota visible: taxonomía pendiente — no asignar código CT hasta revisión."),
        ],
        "frost_en": "Taxonomy pending (flag: LOW_CONFIDENCE_TAXONOMY). Website: [PENDIENTE]. Founders: pending LinkedIn HITL — do not import names from deck slides.",
        "frost_es": "Taxonomía pendiente (flag: LOW_CONFIDENCE_TAXONOMY). Web: [PENDIENTE]. Fundadores: pendiente LinkedIn HITL — no importar nombres del deck.",
        "cta_en": "Cleaner, faster SiC ingot synthesis for power-electronics supply chains.",
        "cta_es": "Síntesis de lingotes SiC más limpia y rápida para cadenas de electrónica de potencia.",
    },
]


def ribbon_html(cells: list[tuple]) -> str:
    parts = []
    for val, lab_en, sub_en, lab_es, sub_es in cells:
        parts.append(
            f'<div class="ribbon-cell"><div class="rc-val">{val}</div>'
            f'<div class="rc-lab">{bi(lab_en, lab_es)}</div>'
            f'<div class="rc-sub">{bi(sub_en, sub_es)}</div></div>'
        )
    return f'<div class="ribbon" style="background:rgba(12,73,138,.95);">{"".join(parts)}</div>'


def stat_rows(stats: list[tuple]) -> str:
    row1 = "".join(
        f'<div class="stat-card"><div class="sc-num">{a}</div><div class="sc-lab">{bi(b, c)}</div></div>'
        for a, b, c in stats[:2]
    )
    row2 = "".join(
        f'<div class="stat-card"><div class="sc-num">{a}</div><div class="sc-lab">{bi(b, c)}</div></div>'
        for a, b, c in stats[2:4]
    )
    return (
        f'<div class="stat-row" style="margin-top:0;">{row1}</div><div class="stat-row">{row2}</div>'
    )


def sol_grid(steps: list[tuple]) -> str:
    cards = []
    for i, (icon, lab_en, lab_es, txt_en, txt_es) in enumerate(steps, 1):
        cards.append(
            f'<div class="sol-card"><div class="sol-step">{i}</div><div class="sol-icon">{icon}</div>'
            f'<div class="sol-label">{bi(lab_en, lab_es)}</div><div class="sol-text">{bi(txt_en, txt_es)}</div></div>'
        )
    return f'<div class="sol-grid">{"".join(cards)}</div>'


def impact_grid(items: list[tuple]) -> str:
    cards = []
    for icon, t_en, t_es, x_en, x_es in items:
        cards.append(
            f'<div class="imp-card"><div class="imp-icon">{icon}</div><div>'
            f'<div class="imp-title">{bi(t_en, t_es)}</div><div class="imp-text">{bi(x_en, x_es)}</div></div></div>'
        )
    return f'<div class="impact-grid">{"".join(cards)}</div>'


def sec(num: int, title_en: str, title_es: str, bg: str, inner: str, ov: str = "rgba(12,73,138,.30)") -> str:
    return (
        f'<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url(\'{bg}\');"></div>'
        f'<div class="sec-ov" style="background:{ov};"></div>'
        f'<div class="sec-header"><div class="sec-num">{num:02d}</div>'
        f'<div class="sec-title">{bi(title_en, title_es)}</div><div class="sec-rule"></div></div>{inner}</div>'
    )


def build(d: dict) -> str:
    slug = d["slug"]
    name = d["name"]
    bg = d["hero_img"]
    badge_cls = d.get("badge_class", "")
    pill_inner = bi(d["badge_en"], d["badge_es"])
    if badge_cls:
        pill_inner = f'<span class="{badge_cls}">{pill_inner}</span>'

    problem = sec(
        1,
        "The Problem",
        "El Problema",
        bg,
        f'<div class="split" style="position:relative;z-index:2;"><div class="split-panel"><div class="split-frost">'
        f'<div class="split-h">{bi("Problem", "Problema")}</div><div class="body-text">{bi(d["problem_en"], d["problem_es"])}</div>'
        f'</div></div><div class="split-panel"><div class="split-frost split-frost-stats">{stat_rows(d["problem_stats"])}</div></div></div>',
    )
    solution = sec(
        2,
        "The Solution",
        "La Solución",
        "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80",
        sol_grid(d["solution_steps"]),
        "rgba(102,147,72,.30)",
    )
    market = sec(
        3,
        "Market",
        "Mercado",
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80",
        f'<div class="frost-note" style="margin-top:0;">{bi(d["market_note_en"], d["market_note_es"])}</div>',
        "rgba(102,147,72,.30)",
    )
    impact = sec(
        4,
        "Climate Impact",
        "Impacto Climático",
        "https://images.unsplash.com/photo-1470071459604-3b5ec3a8fe05?w=1200&q=80",
        impact_grid(d["impact"]) + f'<div class="frost-note">{bi(d["frost_en"], d["frost_es"])}</div>',
    )

    cta = f'''<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('{bg}');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="cta"><div class="pill" style="background:rgba(157,195,132,.12);border:1px solid rgba(157,195,132,.2);color:var(--lg);margin-bottom:16px;">{pill_inner}</div><div class="cta-name">{name}</div><div class="cta-pitch">{bi(d["cta_en"], d["cta_es"])}</div><div class="cta-links"><a class="cta-link" href="https://nexus.cleantechhub.net/s/{slug}">{bi("Nexus Profile", "Perfil Nexus")}</a><a class="cta-link" href="https://nexus.cleantechhub.net/p/startup-portfolio">{bi("157 Startups", "157 Startups")}</a><a class="cta-link" href="https://drive.google.com/file/d/{d["drive_id"]}/view" target="_blank" rel="noopener">{bi("Pitch deck (PDF)", "Pitch deck (PDF)")}</a></div><div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div><div class="cta-port">{bi("Draft one-pager · CLP26 Peru · not deployed", "One-pager borrador · CLP26 Perú · no desplegado")}</div></div></div><div class="accent-bar"></div>'''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — CleantechHUB Startup Profile</title>
<link rel="icon" href="https://cleantechhub.net/favicon.ico">
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&family=PT+Sans:wght@400;700&display=swap" rel="stylesheet">
<style>
{CSS}
{EXTRA_CSS}
</style>
</head>
<body>
<div class="site-brand"><span class="brand-text">Cleantech<em>HUB</em></span></div>
<div class="lang-toggle">
  <button class="lb active" onclick="document.documentElement.lang='en';this.classList.add('active');this.nextElementSibling.classList.remove('active');">EN</button>
  <button class="lb" onclick="document.documentElement.lang='es';this.classList.add('active');this.previousElementSibling.classList.remove('active');">ES</button>
</div>
<div class="sec hero">
  <img class="hero-img" src="{bg}" alt="{name}" loading="lazy">
  <div class="hero-ov"></div>
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);">{pill_inner}</div></div>
  <div class="hero-in">
    <div class="hero-name">{name}</div>
    <div class="hero-sub">{bi(d["sub_en"], d["sub_es"])}</div>
    <div class="hero-pitch">{bi(d["pitch_en"], d["pitch_es"])}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>
{ribbon_html(d["ribbon"])}
{deck_section(slug, name, d["drive_id"], bg)}
{problem}
{solution}
{market}
{impact}
{hidden_video(bg)}
{hidden_founders(bg)}
{cta}
</body>
</html>
"""


def main() -> None:
    for d in STARTUPS:
        out = ROOT / "onepagers" / "sites" / d["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build(d), encoding="utf-8")
        print("Wrote", out)


if __name__ == "__main__":
    main()
