#!/usr/bin/env python3
"""Generate nexus-CO5 one-pager HTML (img slides, hidden video/founders)."""
from __future__ import annotations

import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITES = ROOT / "onepagers" / "sites"

EXTRA_CSS = """
.deck-slide{width:min(100%,640px);margin-left:auto;margin-right:auto;}
.deck-slide .deck-frame-wrap{position:relative;width:100%;aspect-ratio:16/9;height:auto;overflow:hidden;background:#fff;}
.deck-img{width:100%;height:100%;object-fit:contain;display:block;background:#fff;}
.deck-pager{display:flex;align-items:center;justify-content:center;gap:10px;margin-top:10px;}
.deck-page-btn{font-family:'Open Sans',sans-serif;font-size:10px;font-weight:700;color:#fff;background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.35);border-radius:4px;padding:5px 12px;cursor:pointer;}
.deck-page-btn:disabled{opacity:.4;cursor:default;}
.deck-page-label{font-size:10px;font-weight:700;color:#e8ffd4;min-width:52px;text-align:center;}
.yt-pitch{width:min(100%,640px);margin:0 auto 8px;position:relative;z-index:2;}
.yt-pitch-frame{position:relative;width:100%;aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:#000;}
.yt-pitch-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0;}
@media (max-width:700px){.deck-slide-wrap{padding-left:16px;padding-right:16px;}}
"""

STARTUPS = [
    {
        "slug": "planta-comunitaria-wpc",
        "title": "Planta Comunitaria WPC",
        "display_name": "Planta Comunitaria WPC",
        "tagline_en": "Community WPC plant · Circasia, Quindío",
        "tagline_es": "Planta comunitaria WPC · Circasia, Quindío",
        "badge_en": "CT-WA-003 · Recycling & Materials Recovery",
        "badge_es": "CT-WA-003 · Reciclaje y Recuperación de Materiales",
        "pitch_en": "Transform post-consumer plastic waste into WPC plastic lumber — a climate and conservation solution linking waste management, decent work, and circular economy in the community.",
        "pitch_es": "Transforman residuos plásticos posconsumo en madera plástica WPC — solución climática y de conservación que conecta gestión de residuos, trabajo decente y economía circular en la comunidad.",
        "stage_en": "Colombia · Prototype · CLP26",
        "stage_es": "Colombia · Prototipo · CLP26",
        "drive_id": "10BmZsNrMIfwjcncBr9TkZ2AfWz6w3PJw",
        "pages": 9,
        "hero_img": "https://images.unsplash.com/photo-1611273426055-42c0128027fa?w=1200&q=80",
        "ribbon": [
            ("8.60", "USD / post", "USD / poste", "Deck product", "Producto deck"),
            ("36 t/yr", "Plastic WPC", "Plástico WPC", "Post-consumer", "Posconsumo"),
            ("2.7–3.2 t", "CO₂e / t WPC", "CO₂e / t WPC", "Climate impact", "Impacto climático"),
            ("CE", "Theme", "Tema", "Circular economy", "Economía circular"),
        ],
        "sections": "planta",
    },
    {
        "slug": "proyecto-impacto-ambiental",
        "title": "Proyecto emprendedor con impacto ambiental",
        "display_name": "ECO-BLOQUE",
        "tagline_en": "ECO-BLOQUE 40/35/25 · Industrial thermal biomass",
        "tagline_es": "ECO-BLOQUE 40/35/25 · Biomasa térmica industrial",
        "badge_en": "CT-EN-010 · Biomass & Biogas",
        "badge_es": "CT-EN-010 · Biomasa y Biogás",
        "pitch_en": "Combine coconut fibre (35%) and sargassum (25%) into commercial biomass blocks — turning coastal and agricultural waste crises into industrial thermal energy.",
        "pitch_es": "Combinan fibra de coco (35%) y sargazo (25%) en bloques de biomasa comercial — transformando crisis costeras y agrícolas en energía térmica industrial.",
        "stage_en": "Colombia · Private Beta · CLP26",
        "stage_es": "Colombia · Beta Privada · CLP26",
        "drive_id": "1j2zlPXFyUPZJqj_zhvvgO2MA66ZQAb_e",
        "pages": 14,
        "hero_img": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
        "ribbon": [
            ("40/35/25", "Biomass mix", "Mezcla biomasa", "Deck formulation", "Formulación deck"),
            ("50%", "Fuel substitute", "Sustitución", "Pilot target", "Meta piloto"),
            ("4,284 t", "CO₂ / yr", "CO₂ / año", "Phase 1 (deck)", "Fase 1 (deck)"),
            ("EN", "Theme", "Tema", "Clean energy", "Energía limpia"),
        ],
        "sections": "proyecto",
    },
    {
        "slug": "sie-waka",
        "title": "SIÉ WAKA",
        "display_name": "SIÉ WAKA",
        "tagline_en": "Water data → climate intelligence",
        "tagline_es": "Datos del agua → inteligencia climática",
        "badge_en": "CT-WW-001 · Water Access & Treatment",
        "badge_es": "CT-WW-001 · Acceso y Tratamiento de Agua",
        "pitch_en": "Turning water data into climate intelligence — a SaaS platform paired with compliance-ready water-risk reports and satellite-informed monitoring.",
        "pitch_es": "Convierten datos del agua en inteligencia climática — plataforma SaaS con reportes de riesgo hídrico listos para cumplimiento y monitoreo apoyado en satélite.",
        "stage_en": "Colombia · Public Beta · CLP26",
        "stage_es": "Colombia · Beta Pública · CLP26",
        "drive_id": "1aoVRX80JvOK8shJQQUXF9kIKSkN0gGrB",
        "pages": 9,
        "hero_img": "https://images.unsplash.com/photo-1432453979717-755d69830972?w=1200&q=80",
        "ribbon": [
            ("SaaS", "Platform", "Plataforma", "Deck model", "Modelo deck"),
            ("Satellite", "Inputs", "Entradas", "Monitoring", "Monitoreo"),
            ("WW", "Theme", "Tema", "Water", "Agua"),
            ("CT-IC-001", "Secondary CT", "CT secundario", "Satellite monitoring", "Monitoreo satelital"),
        ],
        "sections": "sie-waka",
    },
    {
        "slug": "terra-io",
        "title": "Terra IO",
        "display_name": "TERRA IO",
        "tagline_en": "Soil intelligence, anywhere · Global South",
        "tagline_es": "Inteligencia de suelo, en cualquier lugar · Sur Global",
        "badge_en": "CT-IC-005 · Precision Ag & Smart Grid",
        "badge_es": "CT-IC-005 · Ag de Precisión y Red Inteligente",
        "pitch_en": "Agro-climatic intelligence infrastructure: offline soil-intelligence IoT nodes and AI that anticipate risks, regenerate territories, and improve productivity.",
        "pitch_es": "Infraestructura de inteligencia agroclimática: nodos IoT de suelo con IA offline que anticipan riesgos, regeneran territorios y mejoran la productividad.",
        "stage_en": "Colombia · Private Beta · CLP26",
        "stage_es": "Colombia · Beta Privada · CLP26",
        "drive_id": "1zLssjXlPVroBKkAian6FHOERDNfXBunp",
        "pages": 9,
        "hero_img": "/s/terra-io/assets/hero.jpg",
        "ribbon": [
            ("$9.8B", "Market 2035+", "Mercado 2035+", "Deck figure", "Cifra deck"),
            ("1.21 kt", "CO₂e / yr", "CO₂e / año", "Year 3 scale", "Escala año 3"),
            ("7.9 Mm³", "Water / yr", "Agua / año", "12,600 Ha base", "Base 12.600 Ha"),
            ("BIO", "Theme", "Tema", "Food & agriculture", "Alimentos y agro"),
        ],
        "sections": "terra-io",
        "use_local_assets": True,
    },
]


def e(s: str) -> str:
    return html.escape(s, quote=True)


def deck_block(slug: str, pages: int, drive_id: str) -> str:
    drive_url = f"https://drive.google.com/file/d/{drive_id}/view"
    return f"""
<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="sec-header"><div class="sec-num">📄</div><div class="sec-title"><span class="en">Pitch Deck</span><span class="es">Pitch Deck</span></div><div class="sec-rule"></div></div><div class="deck-note"><span class="en">Slide preview below. Numbers on this profile match the deck only.</span><span class="es">Vista previa de slides abajo. Los números en este perfil provienen solo del deck.</span></div><div class="deck-wrap deck-slide-wrap"><div class="deck-panel deck-slide"><div class="deck-frame-wrap"><img class="deck-frame deck-img" src="/s/{e(slug)}/slides/s-1.jpg" alt="{e(slug)} pitch deck slide 1" loading="lazy"></div><div class="deck-pager" data-slides-base="/s/{e(slug)}/slides/s" data-pages="{pages}"><button type="button" class="deck-page-btn" data-dir="-1">Prev</button><span class="deck-page-label">1 / {pages}</span><button type="button" class="deck-page-btn" data-dir="1">Next</button></div><script>(function(){{var root=document.currentScript.previousElementSibling;if(!root)return;var img=root.parentElement.querySelector('.deck-img');var label=root.querySelector('.deck-page-label');var total=+root.dataset.pages||1;var base=root.dataset.slidesBase||'';var page=1;function show(n){{page=Math.max(1,Math.min(total,n));if(img&&base)img.src=base+'-'+page+'.jpg';if(label)label.textContent=page+' / '+total;root.querySelectorAll('.deck-page-btn').forEach(function(b){{var dir=+b.dataset.dir;b.disabled=dir<0?page<=1:page>=total;}});}}root.addEventListener('click',function(ev){{var b=ev.target.closest('.deck-page-btn');if(!b||b.disabled)return;show(page+(+b.dataset.dir||0));}});show(1);}})();</script><div class="deck-fallback"><span class="en">Slides not loading?</span><span class="es">¿No cargan las slides?</span> <a href="{drive_url}" target="_blank" rel="noopener"><span class="en">Open PDF</span><span class="es">Abrir PDF</span></a> · <a href="{drive_url}" target="_blank" rel="noopener"><span class="en">Google Drive</span><span class="es">Google Drive</span></a></div></div><div class="deck-actions"><a class="cta-link" href="{drive_url}" target="_blank" rel="noopener"><span class="en">Open deck in Google Drive</span><span class="es">Abrir deck en Google Drive</span></a></div></div></div><div class="accent-bar"></div>"""


def hidden_video() -> str:
    return """
<div class="sec" hidden>
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1470071459604-3b5ec3a8fe05?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">▶</div><div class="sec-title"><span class="en">Pitch Video</span><span class="es">Video Pitch</span></div><div class="sec-rule"></div></div>
  <div class="yt-pitch"><div class="yt-pitch-frame"><iframe src="" title="Pitch video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div></div>
</div>"""


def hidden_founders() -> str:
    return """
<div class="sec" hidden>
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">07</div><div class="sec-title"><span class="en">Founders</span><span class="es">Fundadores</span></div><div class="sec-rule"></div></div>
  <div class="team-grid"><div class="team-card"><div class="tp-name">—</div><div class="tp-role"><span class="en">Role pending</span><span class="es">Rol pendiente</span></div><a class="tp-link" href="">LinkedIn</a></div></div>
</div>"""


def body_sections(key: str) -> str:
    if key == "planta":
        return """
<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="sec-header"><div class="sec-num">01</div><div class="sec-title"><span class="en">The Solution</span><span class="es">La Solución</span></div><div class="sec-rule"></div></div><div class="split" style="position:relative;z-index:2;"><div class="split-panel"><div class="split-frost"><div class="split-h"><span class="en">Community plastic-to-WPC plant</span><span class="es">Planta comunitaria plástico a WPC</span></div><div class="body-text"><span class="en">Transform post-consumer plastic into WPC lumber (e.g. 6×6 cm × 210 cm posts). Links waste diversion, recycler livelihoods, and lower deforestation pressure.</span><span class="es">Transforman plástico posconsumo en madera plástica WPC (p. ej. postes 6×6 cm × 210 cm). Conecta disposición final, recicladores y menor presión sobre bosques.</span></div></div></div><div class="split-panel"><div class="split-frost split-frost-stats"><div class="stat-row" style="margin-top:0;"><div class="stat-card"><div class="sc-num">36 t</div><div class="sc-lab"><span class="en">Plastic / year</span><span class="es">Plástico / año</span></div></div><div class="stat-card"><div class="sc-num">2.7–3.2 t</div><div class="sc-lab"><span class="en">CO₂e per t WPC</span><span class="es">CO₂e por t WPC</span></div></div></div></div></div></div></div>
<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200&q=80');"></div><div class="sec-ov" style="background:rgba(102,147,72,.30);"></div><div class="sec-header"><div class="sec-num">02</div><div class="sec-title"><span class="en">Climate Impact</span><span class="es">Impacto Climático</span></div><div class="sec-rule"></div></div><div class="impact-grid"><div class="imp-card"><div class="imp-icon">♻️</div><div><div class="imp-title"><span class="en">Less final disposal</span><span class="es">Menos disposición final</span></div><div class="imp-text"><span class="en">Fewer plastics to landfill — less contamination.</span><span class="es">Menos plásticos a disposición final — menos contaminación.</span></div></div></div><div class="imp-card"><div class="imp-icon">🌲</div><div><div class="imp-title"><span class="en">Deforestation</span><span class="es">Deforestación</span></div><div class="imp-text"><span class="en">Less deforestation → lower carbon footprint (deck).</span><span class="es">Menos deforestación → menor huella de carbono (deck).</span></div></div></div></div></div>"""
    if key == "proyecto":
        return """
<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="sec-header"><div class="sec-num">01</div><div class="sec-title"><span class="en">The Problem</span><span class="es">El Problema</span></div><div class="sec-rule"></div></div><div class="split" style="position:relative;z-index:2;"><div class="split-panel"><div class="split-frost"><div class="split-h"><span class="en">Industrial bunker fuel emissions</span><span class="es">Emisiones de combustóleo industrial</span></div><div class="body-text"><span class="en">Phase 1 deck baseline: five companies burn 840,000 gal Bunker No. 6 per year — 8,568 t CO₂.</span><span class="es">Línea base deck Fase 1: cinco empresas queman 840.000 gal Búnker No. 6 al año — 8.568 t CO₂.</span></div></div></div><div class="split-panel"><div class="split-frost split-frost-stats"><div class="stat-row" style="margin-top:0;"><div class="stat-card"><div class="sc-num">50%</div><div class="sc-lab"><span class="en">Fuel substitution</span><span class="es">Sustitución combustible</span></div></div><div class="stat-card"><div class="sc-num">4,284 t</div><div class="sc-lab"><span class="en">CO₂ avoided / yr</span><span class="es">CO₂ evitadas / año</span></div></div></div></div></div></div></div>
<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80');"></div><div class="sec-ov" style="background:rgba(102,147,72,.30);"></div><div class="sec-header"><div class="sec-num">02</div><div class="sec-title"><span class="en">Deal &amp; Circularity</span><span class="es">Trato y Circularidad</span></div><div class="sec-rule"></div></div><div class="frost-note" style="margin-top:0;"><span class="en">Retire and valorize coastal sargassum from hotels, combine with coconut fibre waste, and sell 40/35/25 biomass blocks to industries substituting fossil thermal fuels. Circularity indicator (deck): ≈7,280 t/year of sargassum, coconut fibre and bamboo fibre valorized as fuel (pilot base).</span><span class="es">Retiran y valorizan sargazo costero de hoteles, lo combinan con residuos de fibra de coco y venden bloques 40/35/25 a industrias que sustituyen combustibles fósiles térmicos. Indicador de circularidad (deck): ≈7.280 t/año de sargazo, fibra de coco y bambú valorizados como combustible (base del piloto).</span></div></div>"""
    if key == "sie-waka":
        return """
<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="sec-header"><div class="sec-num">01</div><div class="sec-title"><span class="en">Platform</span><span class="es">Plataforma</span></div><div class="sec-rule"></div></div><div class="split" style="position:relative;z-index:2;"><div class="split-panel"><div class="split-frost"><div class="split-h"><span class="en">Clear decisions. Clear as water.</span><span class="es">Decisiones claras. Claras como el agua.</span></div><div class="body-text"><span class="en">Turning water data into climate intelligence — SaaS paired with compliance-ready water-risk reports; satellite and community data inputs for optimized resource allocation.</span><span class="es">Convierten datos del agua en inteligencia climática — SaaS con reportes de riesgo hídrico listos para cumplimiento; entradas satelitales y comunitarias para asignación optimizada de recursos.</span></div></div></div><div class="split-panel"><div class="split-frost split-frost-stats"><div class="stat-row" style="margin-top:0;"><div class="stat-card"><div class="sc-num">CT-WW-001</div><div class="sc-lab"><span class="en">Primary taxonomy</span><span class="es">Taxonomía primaria</span></div></div><div class="stat-card"><div class="sc-num">CT-IC-001</div><div class="sc-lab"><span class="en">Secondary CT</span><span class="es">CT secundario</span></div></div></div></div></div></div></div>"""
    if key == "terra-io":
        return """
<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('/s/terra-io/assets/bg-problem.jpg');"></div><div class="sec-ov" style="background:rgba(12,73,138,.30);"></div><div class="sec-header"><div class="sec-num">01</div><div class="sec-title"><span class="en">The Offer</span><span class="es">La Oferta</span></div><div class="sec-rule"></div></div><div class="split" style="position:relative;z-index:2;"><div class="split-panel"><div class="split-frost"><div class="split-h"><span class="en">One system — three revenue streams</span><span class="es">Un sistema — tres fuentes de ingreso</span></div><div class="body-text"><span class="en">Enter via cooperatives, deliver value to producers, scale with institutions — shared field devices, reports, API, dashboards, recommendations and alerts (deck).</span><span class="es">Entran vía cooperativas, entregan valor a productores, escalan con instituciones — dispositivos compartidos, reportes, API, tableros, recomendaciones y alertas (deck).</span></div></div></div><div class="split-panel"><div class="split-frost split-frost-stats"><div class="stat-row" style="margin-top:0;"><div class="stat-card"><div class="sc-num">$35–50</div><div class="sc-lab"><span class="en">Producers / mo</span><span class="es">Productores / mes</span></div></div><div class="stat-card"><div class="sc-num">50</div><div class="sc-lab"><span class="en">Plots / contract</span><span class="es">Parcelas / contrato</span></div></div></div></div></div></div></div>
<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url('/s/terra-io/assets/bg-impact.jpg');"></div><div class="sec-ov" style="background:rgba(102,147,72,.30);"></div><div class="sec-header"><div class="sec-num">02</div><div class="sec-title"><span class="en">Climate Impact</span><span class="es">Impacto Climático</span></div><div class="sec-rule"></div></div><div class="impact-grid"><div class="imp-card"><div class="imp-icon">💧</div><div><div class="imp-title"><span class="en">Water</span><span class="es">Agua</span></div><div class="imp-text"><span class="en">7.9 Mm³/year potentially conserved (12,600 Ha effective adoption).</span><span class="es">7,9 Mm³/año potencialmente conservados (12.600 Ha adopción efectiva).</span></div></div></div><div class="imp-card"><div class="imp-icon">🌱</div><div><div class="imp-title"><span class="en">N₂O / CO₂e</span><span class="es">N₂O / CO₂e</span></div><div class="imp-text"><span class="en">1.21 ktCO₂e/year direct emissions potentially avoided (Year 3 scale).</span><span class="es">1,21 ktCO₂e/año emisiones directas potencialmente evitadas (escala año 3).</span></div></div></div></div></div>"""
    return ""


def ribbon_html(cells) -> str:
    parts = []
    for val, lab_en, lab_es, sub_en, sub_es in cells:
        parts.append(
            f'<div class="ribbon-cell"><div class="rc-val">{e(val)}</div>'
            f'<div class="rc-lab"><span class="en">{e(lab_en)}</span><span class="es">{e(lab_es)}</span></div>'
            f'<div class="rc-sub"><span class="en">{e(sub_en)}</span><span class="es">{e(sub_es)}</span></div></div>'
        )
    return f'<div class="ribbon" style="background:rgba(12,73,138,.95);">{"".join(parts)}</div>'


def build_page(s: dict) -> str:
    slug = s["slug"]
    drive_url = f"https://drive.google.com/file/d/{s['drive_id']}/view"
    cta_bg = "/s/terra-io/assets/bg-cta.jpg" if s.get("use_local_assets") else "https://images.unsplash.com/photo-1470071459604-3b5ec3a8fe05?w=1200&q=80"
    website_btn = ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(s['title'])} — CleantechHUB Startup Profile</title>
<link rel="icon" href="https://cleantechhub.net/favicon.ico">
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&family=PT+Sans:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{{--db:#0C498A;--cy:#B2EEFA;--lg:#9DC384;--fo:#669348;--sk:#69B5FA;--page:#fff;--ov:0.30;--panel:rgba(12,73,138,.94);--panel-border:rgba(255,255,255,.48);}}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Open Sans','PT Sans',sans-serif;background:var(--page);color:var(--db);max-width:1080px;margin:0 auto;}}
[lang="es"] .en{{display:none;}} [lang="en"] .es{{display:none;}}
.site-brand{{position:fixed;top:12px;left:50%;transform:translateX(-50%);width:100%;max-width:1080px;padding:0 48px;z-index:99;pointer-events:none;}}
.site-brand .brand-text{{pointer-events:auto;display:inline-block;font-size:13px;font-weight:800;letter-spacing:.4px;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.6);}}
.site-brand .brand-text em{{color:var(--lg);font-style:normal;}}
.lang-toggle{{position:fixed;top:12px;right:12px;z-index:100;display:flex;border-radius:5px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,.35);}}
.lb{{padding:6px 14px;font-size:10px;font-weight:700;border:none;cursor:pointer;font-family:'Open Sans',sans-serif;transition:all .2s;}}
.lb.active{{background:var(--db);color:#fff;}}.lb:not(.active){{background:#fff;color:var(--db);}}
.sec{{position:relative;overflow:hidden;}}
.sec-bg{{position:absolute;inset:0;background-size:cover;background-position:center;z-index:0;}}
.sec-ov{{position:absolute;inset:0;z-index:1;}}
.sec-header{{display:flex;align-items:center;gap:14px;padding:28px 48px 16px;position:relative;z-index:2;}}
.sec-num{{font-size:11px;font-weight:800;color:var(--db);background:var(--lg);width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 2px 8px rgba(0,0,0,.35);}}
.sec-title{{font-size:18px;font-weight:800;letter-spacing:-.3px;color:#fff;text-shadow:0 2px 14px rgba(0,0,0,.75);}}
.sec-rule{{height:1px;background:linear-gradient(90deg,rgba(255,255,255,.55),rgba(255,255,255,0));flex:1;margin-left:8px;}}
.accent-bar{{height:3px;background:linear-gradient(90deg,var(--db) 20%,var(--fo) 20% 40%,var(--lg) 40% 60%,var(--sk) 60% 80%,var(--cy) 80%);}}
.pill{{display:inline-block;padding:5px 12px;border-radius:4px;font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;}}
.hero{{height:420px;position:relative;}}
.hero-img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0;}}
.hero-ov{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(12,73,138,.12) 0%,rgba(12,73,138,.30) 55%,rgba(12,73,138,.48) 100%);z-index:1;}}
.hero-in{{position:relative;z-index:2;height:100%;display:flex;flex-direction:column;justify-content:flex-end;padding:0 48px 36px;}}
.hero-badge{{position:absolute;top:56px;left:48px;z-index:3;}}
.hero-name{{font-size:56px;font-weight:800;line-height:1;color:#fff;text-shadow:0 4px 24px rgba(0,0,0,.55);}}
.hero-sub{{font-size:14px;font-weight:700;color:#e8ffd4;margin-top:8px;text-shadow:0 2px 10px rgba(0,0,0,.5);}}
.hero-pitch{{font-size:14px;line-height:1.6;color:#fff;margin-top:14px;max-width:540px;text-shadow:0 2px 12px rgba(0,0,0,.55);}}
.hero-tagline{{font-size:10px;font-style:italic;color:#e8ffd4;opacity:.9;position:absolute;bottom:36px;right:48px;text-shadow:0 2px 8px rgba(0,0,0,.5);}}
.ribbon{{display:grid;grid-template-columns:repeat(4,1fr);}}
.ribbon-cell{{padding:22px 24px;text-align:center;border-right:1px solid rgba(255,255,255,.12);}}
.ribbon-cell:last-child{{border-right:none;}}
.rc-val{{font-size:28px;font-weight:800;line-height:1;color:#fff;}}
.rc-lab{{font-size:9px;font-weight:700;color:#e8ffd4;letter-spacing:.6px;text-transform:uppercase;margin-top:4px;}}
.rc-sub{{font-size:9px;color:rgba(255,255,255,.75);margin-top:2px;}}
.split{{display:grid;grid-template-columns:1fr 1fr;align-items:stretch;}}
.split-panel{{position:relative;overflow:hidden;padding:36px 40px;display:flex;flex-direction:column;}}
.split-h{{font-size:22px;font-weight:800;line-height:1.2;margin-bottom:12px;color:#fff;}}
.body-text{{font-size:13px;line-height:1.65;color:rgba(255,255,255,.95);}}
.frost-panel,.stat-card,.sol-card,.slider-item,.imp-card,.team-card,.comp-tbl,.mini-chart,.split-frost,.deck-panel,.frost-note{{background:var(--panel);backdrop-filter:blur(12px) saturate(1.35);-webkit-backdrop-filter:blur(12px) saturate(1.35);border:1px solid var(--panel-border);box-shadow:0 8px 32px rgba(0,0,0,.42);}}
.stat-row{{display:flex;gap:10px;margin-top:14px;}}
.stat-card{{flex:1;border-radius:8px;padding:14px;text-align:center;}}
.sc-num{{font-size:26px;font-weight:800;color:#e8ffd4;line-height:1;}}
.sc-lab{{font-size:9px;font-weight:700;color:rgba(255,255,255,.9);margin-top:3px;line-height:1.3;}}
.impact-grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:0 48px 28px;position:relative;z-index:2;}}
.imp-card{{border-radius:8px;padding:22px 20px;display:flex;gap:14px;align-items:flex-start;}}
.imp-icon{{font-size:22px;flex-shrink:0;}}
.imp-title{{font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:#e8ffd4;margin-bottom:4px;}}
.imp-text{{font-size:12px;line-height:1.5;color:rgba(255,255,255,.92);}}
.team-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;padding:0 48px 28px;position:relative;z-index:2;}}
.team-card{{border-radius:8px;padding:24px 20px;text-align:center;}}
.tp-name{{font-size:14px;font-weight:700;color:#fff;}}
.tp-role{{font-size:10px;font-weight:600;color:#e8ffd4;margin-top:3px;}}
.tp-link{{display:inline-block;margin-top:10px;font-size:9px;font-weight:700;color:#e8ffd4;text-decoration:none;border-bottom:1px solid rgba(232,255,212,.5);}}
.frost-note{{margin:0 48px 20px;padding:14px 18px;border-radius:8px;font-size:11px;line-height:1.55;color:rgba(255,255,255,.92);position:relative;z-index:2;}}
.cta{{text-align:center;padding:44px 48px;position:relative;z-index:2;}}
.cta-name{{font-size:44px;font-weight:800;color:#fff;text-shadow:0 3px 16px rgba(0,0,0,.55);}}
.cta-pitch{{font-size:14px;line-height:1.6;max-width:560px;margin:12px auto 0;color:rgba(255,255,255,.92);text-shadow:0 2px 10px rgba(0,0,0,.45);}}
.cta-links{{display:flex;gap:10px;justify-content:center;margin-top:16px;flex-wrap:wrap;}}
.cta-link{{font-size:10px;font-weight:700;color:#fff;text-decoration:none;padding:8px 16px;background:var(--panel);border:1px solid var(--panel-border);border-radius:6px;box-shadow:0 4px 16px rgba(0,0,0,.35);}}
.cta-brand{{margin-top:24px;}}
.cta-brand .tg{{font-size:12px;font-style:italic;color:#e8ffd4;opacity:.95;}}
.cta-brand .lg2{{font-size:14px;font-weight:800;margin-top:4px;color:#fff;}}
.cta-port{{font-size:9px;color:rgba(255,255,255,.8);margin-top:10px;}}
.deck-wrap{{padding:0 48px 32px;position:relative;z-index:2;}}
.deck-panel{{padding:16px;border-radius:8px;}}
.deck-frame-wrap{{width:100%;border-radius:6px;overflow:hidden;background:#fff;box-shadow:0 14px 40px rgba(0,0,0,.5);line-height:0;}}
.deck-fallback{{margin-top:12px;font-size:10px;color:rgba(255,255,255,.85);text-align:center;text-shadow:0 1px 8px rgba(0,0,0,.5);}}
.deck-fallback a{{color:#e8ffd4;font-weight:700;}}
.deck-actions{{display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap;}}
.deck-note{{padding:0 48px 8px;font-size:10px;color:rgba(255,255,255,.9);text-align:center;position:relative;z-index:2;text-shadow:0 1px 8px rgba(0,0,0,.5);}}
.split-frost{{padding:24px 28px;border-radius:8px;flex:1;display:flex;flex-direction:column;justify-content:center;min-height:100%;}}
.split-frost-stats .stat-row{{flex:1;align-items:stretch;margin-top:0;}}
.split-frost-stats .stat-card{{background:transparent;border:none;box-shadow:none;display:flex;flex-direction:column;justify-content:center;}}
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
  <img class="hero-img" src="{e(s['hero_img'])}" alt="{e(s['display_name'])}" loading="lazy">
  <div class="hero-ov"></div>
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);"><span class="en">{e(s['badge_en'])}</span><span class="es">{e(s['badge_es'])}</span></div></div>
  <div class="hero-in">
    <div class="hero-name">{e(s['display_name'])}</div>
    <div class="hero-sub"><span class="en">{e(s['tagline_en'])} · {e(s['stage_en'])}</span><span class="es">{e(s['tagline_es'])} · {e(s['stage_es'])}</span></div>
    <div class="hero-pitch"><span class="en">{e(s['pitch_en'])}</span><span class="es">{e(s['pitch_es'])}</span></div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>
{ribbon_html(s['ribbon'])}
{deck_block(slug, s['pages'], s['drive_id'])}
{body_sections(s['sections'])}
{hidden_video()}
{hidden_founders()}
<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{cta_bg}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="cta">
    <div class="pill" style="background:rgba(157,195,132,.12);border:1px solid rgba(157,195,132,.2);color:var(--lg);margin-bottom:16px;"><span class="en">{e(s['badge_en'])}</span><span class="es">{e(s['badge_es'])}</span></div>
    <div class="cta-name">{e(s['display_name'])}</div>
    <div class="cta-pitch"><span class="en">{e(s['pitch_en'])}</span><span class="es">{e(s['pitch_es'])}</span></div>
    <div class="cta-links">
      <a class="cta-link" href="https://nexus.cleantechhub.net/s/{e(slug)}"><span class="en">Nexus Profile</span><span class="es">Perfil Nexus</span></a>
      <a class="cta-link" href="https://nexus.cleantechhub.net/p/startup-portfolio"><span class="en">157 Startups</span><span class="es">157 Startups</span></a>
      <a class="cta-link" href="{drive_url}" target="_blank" rel="noopener"><span class="en">Pitch deck (PDF)</span><span class="es">Pitch deck (PDF)</span></a>
    </div>
    <div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div>
    <div class="cta-port"><span class="en">CleantechHUB portfolio profile · Latin America · Draft (HITL)</span><span class="es">Perfil portafolio CleantechHUB · América Latina · Borrador (HITL)</span></div>
  </div>
</div>
<div class="accent-bar"></div>
</body>
</html>
"""


def main() -> None:
    for s in STARTUPS:
        out = SITES / s["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build_page(s), encoding="utf-8")
        print("wrote", out)


if __name__ == "__main__":
    main()
