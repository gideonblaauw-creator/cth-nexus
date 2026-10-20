#!/usr/bin/env python3
"""Generate nexus-CO3 one-pagers (JPEG deck slides, empty founders, hidden video)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "onepagers" / "template" / "styles.css").read_text()
EXTRA_CSS = """
.deck-slide .deck-img{width:100%;height:100%;object-fit:contain;position:absolute;inset:0;background:#fff;}
"""

STARTUPS = [
    {
        "slug": "communitylab",
        "name": "communitylab S.A.S",
        "display_short": "communitylab",
        "website": "https://communitylab.co",
        "website_label": "communitylab.co",
        "stage": "Launched",
        "ct1": "CT-IN-004",
        "ct1_label": "Industrial Symbiosis",
        "ct2": "CT-WA-003",
        "ct2_label": "Recycling & Materials Recovery",
        "drive_id": "17-r1ja_35K3QrKbLr-jwvV1FGfyJDts_",
        "pages": 9,
        "hero_image": "/s/communitylab/assets/hero.jpg",
        "badge_en": "Industrial Symbiosis · Waste Sensors &amp; SICircular",
        "badge_es": "Simbiosis Industrial · Sensores de Residuos y SICircular",
        "pitch_en": "From waste to resource: a software and sensor platform helps factories measure waste flows and turn verified data into circular economy value with SICircular.",
        "pitch_es": "Del residuo al recurso: una plataforma de software y sensores ayuda a las fábricas a medir flujos de residuos y convertir datos verificados en valor de economía circular con SICircular.",
        "ribbon": [
            ("B2B", "Platform", "Plataforma", "SICircular SaaS", "SICircular SaaS"),
            ("Sensors", "Hardware", "Hardware", "Measure & trace", "Medir y trazar"),
            ("Symbiosis", "Marketplace", "Marketplace", "Industrial links", "Enlaces industriales"),
            ("Launched", "Stage", "Etapa", "CLP26 · CO", "CLP26 · CO"),
        ],
        "sections": [
            ("01", "The Problem", "El Problema", "rgba(12,73,138,.30)", "/s/communitylab/assets/bg-problem.jpg",
             "Waste is lost value in industrial plants", "Los residuos son valor perdido en plantas industriales",
             "Industrial waste often lacks reliable measurement and traceability, so circular opportunities and compliance indicators stay invisible.",
             "En plantas industriales faltan medición y trazabilidad confiables de residuos, por lo que oportunidades circulares e indicadores de cumplimiento permanecen invisibles."),
            ("02", "SICircular Solution", "Solución SICircular", "rgba(102,147,72,.30)", "/s/communitylab/assets/bg-solution.jpg",
             "Modular circular architecture", "Arquitectura circular modular",
             "Sistema Integral Circular combines analytics software with sensors and cameras to measure flows, connect symbiosis opportunities, quantify impacts, and support normative compliance.",
             "El Sistema Integral Circular combina software analítico con sensores y cámaras para medir flujos, conectar oportunidades de simbiosis, cuantificar impactos y apoyar cumplimiento normativo."),
            ("03", "Market &amp; Model", "Mercado y Modelo", "rgba(12,73,138,.30)", "/s/communitylab/assets/bg-market.jpg",
             "B2B factories and restaurant chains", "B2B fábricas y cadenas de restaurantes",
             "Deck positions verified market share around USD 16,238/year per client as a reference point; success-fee upside remains to be validated operationally.",
             "El deck posiciona cuota de mercado verificada alrededor de USD 16.238/año por cliente como referencia; el upside por tarifa de éxito aún debe validarse operativamente."),
            ("04", "Climate Impact", "Impacto Climático", "rgba(102,147,72,.30)", "/s/communitylab/assets/bg-impact.jpg",
             "Waste as a climate lever", "Residuos como palanca climática",
             "Deck scenario: replicating SICircular across 100 food-processing plants could avoid consuming more than 77,000 barrels of oil and strengthen informal circular networks through formalized valorization.",
             "Escenario del deck: replicar SICircular en 100 plantas de procesamiento de alimentos podría evitar consumir más de 77.000 barriles de petróleo y fortalecer redes circulares informales mediante valorización formalizada."),
        ],
        "cta_en": "Turn waste data into auditable circular revenue — measure, trace, and connect industrial symbiosis.",
        "cta_es": "Convierte datos de residuos en ingresos circulares auditables — mide, traza y conecta simbiosis industrial.",
    },
    {
        "slug": "construyendo-redes-de-paz",
        "name": "Construyendo Redes de Paz",
        "display_short": "Construyendo Redes de Paz",
        "website": "#",
        "website_label": "Colombia · Prototype",
        "stage": "Prototype",
        "ct1": "CT-AF-002",
        "ct1_label": "Cacao Value Chain",
        "ct2": "CT-IC-003",
        "ct2_label": "Supply Chain Traceability",
        "drive_id": "1UE0fZvM5jY1yGfrJTgun-m5r4n-02BAG",
        "pages": 9,
        "hero_image": "https://images.unsplash.com/photo-1511381939411-e44015466634?w=1200&q=80",
        "badge_en": "CT-AF-002 · Organic Traceable Fine Cacao",
        "badge_es": "CT-AF-002 · Cacao Fino Orgánico Trazable",
        "pitch_en": "Fine-flavor organic cacao with full traceability and verified social impact from the parcel — building rural peace through regenerative value chains.",
        "pitch_es": "Cacao fino de aroma, orgánico, con trazabilidad completa e impacto social verificado desde la parcela — construyendo paz rural mediante cadenas regenerativas.",
        "ribbon": [
            ("Organic", "Cacao", "Cacao", "Fine flavor", "Fino de aroma"),
            ("Trace", "End-to-end", "Extremo a extremo", "Supply chain", "Cadena de suministro"),
            ("~$4K", "Deal ref.", "Ref. trato", "Deck anchor", "Referencia deck"),
            ("Prototype", "Stage", "Etapa", "CLP26 · CO", "CLP26 · CO"),
        ],
        "sections": [
            ("01", "The Offer", "La Oferta", "rgba(12,73,138,.30)", "https://images.unsplash.com/photo-1511381939411-e44015466634?w=1200&q=80",
             "Traceable organic cacao as climate-smart commodity", "Cacao orgánico trazable como commodity climático",
             "Deck positions organic traceable cacao for high-quality markets, linking producer stability with verified origin and environmental performance versus synthetic-input systems.",
             "El deck posiciona cacao orgánico trazable para mercados de alta calidad, vinculando estabilidad del productor con origen verificado y desempeño ambiental frente a sistemas con insumos sintéticos."),
            ("02", "Value Chain", "Cadena de Valor", "rgba(102,147,72,.30)", "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80",
             "From parcel to premium buyer", "De la parcela al comprador premium",
             "Model integrates cooperative production, net pricing logic, and product sales metrics described in the deck financial slides.",
             "El modelo integra producción cooperativa, lógica de precio neto y métricas de productos vendidos descritas en las láminas financieras del deck."),
            ("03", "Market Sizing", "Dimensionamiento", "rgba(12,73,138,.30)", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80",
             "Global cacao demand", "Demanda global de cacao",
             "Deck cites TAM/SAM/SOM figures for organic traceable cacao markets (Global / Americas / Colombia) — use deck tables as source of truth for diligence.",
             "El deck cita cifras TAM/SAM/SOM para mercados de cacao orgánico trazable (Global / Américas / Colombia) — usar tablas del deck como fuente para diligencia."),
            ("04", "Climate &amp; Social Impact", "Impacto Climático y Social", "rgba(102,147,72,.30)", "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
             "Lower emissions vs synthetic inputs", "Menores emisiones vs insumos sintéticos",
             "Deck claims up to 70% less nitrous oxide compared with cacao using synthetic fertilizers, plus rural employment and profit share returning to farming families.",
             "El deck afirma hasta 70% menos óxido nitroso comparado con cacao que usa fertilizantes sintéticos, además de empleo rural y reparto de utilidades a familias campesinas."),
        ],
        "cta_en": "Premium organic cacao with traceability that keeps value with producers and lowers field emissions.",
        "cta_es": "Cacao orgánico premium con trazabilidad que retiene valor en productores y reduce emisiones en campo.",
        "cta_btn_en": "CleantechHUB profile",
        "cta_btn_es": "Perfil CleantechHUB",
    },
    {
        "slug": "dantium",
        "name": "DANTIUM",
        "display_short": "DANTIUM",
        "website": "#",
        "website_label": "Colombia · Prototype",
        "stage": "Prototype",
        "ct1": "CT-WA-003",
        "ct1_label": "Recycling & Materials Recovery",
        "ct2": "CT-EN-006",
        "ct2_label": "Distributed Generation",
        "drive_id": "1U-YYierLCPrYKDel6Lj2wiNdampgLxL5",
        "pages": 9,
        "hero_image": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1200&q=80",
        "badge_en": "CT-WA-003 · Recycled Polymer Rural Infrastructure",
        "badge_es": "CT-WA-003 · Infraestructura Rural en Polímero Reciclado",
        "pitch_en": "Modular perimeter infrastructure: recycled polymer composite posts with autonomous solar PV, LED lighting, and presence sensors — replacing wood in agricultural fencing.",
        "pitch_es": "Infraestructura perimetral modular: postes compuestos de polímero reciclado con fotovoltaica autónoma, iluminación LED y sensores de presencia — sustituyendo madera en cercas agropecuarias.",
        "ribbon": [
            ("+50 yr", "Durability", "Durabilidad", "Deck lifespan", "Vida útil deck"),
            ("Solar", "Autonomy", "Autonomía", "PV integrated", "FV integrado"),
            ("18 t", "Plastic / km", "Plástico / km", "Deck recovery", "Recuperación deck"),
            ("Prototype", "Stage", "Etapa", "CLP26 · CO", "CLP26 · CO"),
        ],
        "sections": [
            ("01", "The Deal", "El Trato", "rgba(12,73,138,.30)", "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1200&q=80",
             "Perimeter that does not degrade", "Perímetro que no se degrada",
             "DANTIUM manufactures and commercializes recycled polymer posts with solar, lighting, and sensors for agricultural fencing where wood fails and logistics matter.",
             "DANTIUM fabrica y comercializa postes de polímero reciclado con solar, iluminación y sensores para cercas agropecuarias donde la madera falla y la logística importa."),
            ("02", "Beachhead", "Beachhead", "rgba(102,147,72,.30)", "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80",
             "Medium & large livestock producers", "Productores ganaderos medianos y grandes",
             "Deck targets Colombia agricultural producers actively seeking green transformed-plastic materials, with global and national TAM figures on the market slide.",
             "El deck apunta a productores agropecuarios en Colombia que buscan materiales plásticos transformados verdes, con cifras TAM global y nacional en la lámina de mercado."),
            ("03", "Circularity Math", "Matemática Circular", "rgba(12,73,138,.30)", "https://images.unsplash.com/photo-1532996122724-e3c031a396bf?w=1200&q=80",
             "Plastic kept from open burning", "Plástico alejado de quema a cielo abierto",
             "Deck cites 2.7–3.1 t CO₂e avoided per ton of recovered plastic kept from open burning (CIEL 2019 / EPA WARM 2020 references on slide).",
             "El deck cita 2,7–3,1 t CO₂e evitadas por tonelada de plástico recuperado alejado de quema a cielo abierto (referencias CIEL 2019 / EPA WARM 2020 en lámina)."),
            ("04", "Climate Impact", "Impacto Climático", "rgba(102,147,72,.30)", "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
             "Km-scale plastic recovery", "Recuperación de plástico a escala km",
             "One km of DANTIUM fencing reclaims 18 tons of plastic, avoiding an estimated 48.6–55.8 t CO₂e per deck scenario; supports income for grassroots recyclers.",
             "Un km de cerca DANTIUM recupera 18 toneladas de plástico, evitando un estimado 48,6–55,8 t CO₂e según escenario del deck; apoya ingresos de recicladores de base."),
        ],
        "cta_en": "Durable rural security infrastructure that locks recovered plastic into productive land boundaries.",
        "cta_es": "Infraestructura rural segura y durable que fija plástico recuperado en límites productivos del territorio.",
        "cta_btn_en": "CleantechHUB profile",
        "cta_btn_es": "Perfil CleantechHUB",
    },
    {
        "slug": "e-wai",
        "name": "e.WAI",
        "display_short": "e.WAI",
        "website": "#",
        "website_label": "Colombia · Public Beta",
        "stage": "Public Beta",
        "ct1": "CT-WW-003",
        "ct1_label": "Watershed Conservation",
        "ct2": "CT-IC-004",
        "ct2_label": "Climate Data Platforms",
        "drive_id": "10Xi9AAFKp5Eu-UGIgnvSrZH9afJuRnn5",
        "pages": 9,
        "hero_image": "https://images.unsplash.com/photo-1432453979717-755d69830972?w=1200&q=80",
        "badge_en": "CT-WW-003 · AI Water Compliance Platform",
        "badge_es": "CT-WW-003 · Plataforma IA de Cumplimiento Hídrico",
        "pitch_en": "Hydric intelligence on time: AI water-monitoring platform that turns lab and sensor data into automated environmental compliance reports for consultants and accredited labs.",
        "pitch_es": "Inteligencia hídrica a tiempo: plataforma de monitoreo hídrico con IA que convierte datos de laboratorio y sensores en reportes automáticos de cumplimiento ambiental para consultoras y laboratorios acreditados.",
        "ribbon": [
            ("$85", "Report price", "Precio reporte", "Deck anchor", "Referencia deck"),
            ("99%", "Time saved", "Tiempo ahorrado", "vs manual (deck)", "vs manual (deck)"),
            ("721", "Water sources", "Fuentes hídricas", "Impact scenario", "Escenario impacto"),
            ("Public Beta", "Stage", "Etapa", "CLP26 · CO", "CLP26 · CO"),
        ],
        "sections": [
            ("01", "The Problem", "El Problema", "rgba(12,73,138,.30)", "https://images.unsplash.com/photo-1432453979717-755d69830972?w=1200&q=80",
             "Manual transformation is the bottleneck", "La transformación manual es el cuello de botella",
             "Environmental teams fear fines more than software cost; deck cites 3–5 days per manual report versus minutes with e.WAI, with setup under two hours as a purchase trigger in interviews.",
             "Los equipos ambientales temen multas más que el costo del software; el deck cita 3–5 días por reporte manual versus minutos con e.WAI, con setup bajo dos horas como disparador de compra en entrevistas."),
            ("02", "The Product", "El Producto", "rgba(102,147,72,.30)", "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80",
             "From hydric data to compliance PDFs", "De datos hídricos a PDFs de cumplimiento",
             "Interactive map, universal ingestor, automatic normative reports, and anomaly detection — built for environmental consultants and accredited laboratories.",
             "Mapa interactivo, ingestor universal, reportes normativos automáticos y detección de anomalías — diseñado para consultoras ambientales y laboratorios acreditados."),
            ("03", "Market", "Mercado", "rgba(12,73,138,.30)", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80",
             "Consultancies &amp; labs beachhead", "Beachhead consultoras y laboratorios",
             "Deck segmentation: global TAM 3.9B context, 4,294 potential LATAM SAM consultancies, Colombia year-3 SOM target 17.5M with 859 client objective on slide.",
             "Segmentación del deck: contexto TAM global 3,9B, 4.294 consultoras SAM potenciales LATAM, objetivo SOM Colombia año 3 17,5M con 859 clientes en lámina."),
            ("04", "Climate Impact", "Impacto Climático", "rgba(102,147,72,.30)", "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
             "Timely watershed protection", "Protección oportuna de cuencas",
             "Deck scenario: 721 verified water sources, 721 regulated industries identified, enabling timely hydric protection aligned with compliance obligations (IDEAM / SECOP / RUES references on slide).",
             "Escenario del deck: 721 fuentes hídricas verificadas, 721 industrias reguladas identificadas, habilitando protección hídrica oportuna alineada con obligaciones de cumplimiento (referencias IDEAM / SECOP / RUES en lámina)."),
        ],
        "cta_en": "Automate hydric compliance reporting — from days of manual work to minutes with zero manual errors.",
        "cta_es": "Automatiza reportes de cumplimiento hídrico — de días de trabajo manual a minutos sin errores manuales.",
        "cta_btn_en": "CleantechHUB profile",
        "cta_btn_es": "Perfil CleantechHUB",
    },
    {
        "slug": "el-ocambulo",
        "name": "El Ocámbulo",
        "display_short": "El Ocámbulo",
        "website": "#",
        "website_label": "Colombia · Launched",
        "stage": "Launched",
        "ct1": "CT-AF-009",
        "ct1_label": "Bioeconomy & NbS",
        "ct2": "CT-WA-002",
        "ct2_label": "Organic Waste & Composting",
        "drive_id": "12rS4mpXFukjMqSKGLRhhcCoNH2CxlLnt",
        "pages": 9,
        "hero_image": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=1200&q=80",
        "badge_en": "CT-AF-009 · Gourmet Mushrooms from Wood Residues",
        "badge_es": "CT-AF-009 · Hongos Gourmet desde Residuos de Madera",
        "pitch_en": "Reliable gourmet mushroom supply for Colombia: fresh Pleurotus (Orellana) protein grown on underused sawdust and wood shavings — processing, harvest, and distribution.",
        "pitch_es": "Suministro confiable de hongos gourmet para Colombia: proteína fresca de Pleurotus (Orellana) cultivada sobre aserrín y viruta subutilizados — procesamiento, cosecha y distribución.",
        "ribbon": [
            ("$12/kg", "Direct sale", "Venta directa", "Deck pricing", "Precio deck"),
            ("375", "Clients Y3", "Clientes A3", "Bogotá beachhead", "Beachhead Bogotá"),
            ("Alt.", "Protein", "Proteína", "Market-ready", "Lista para mercado"),
            ("Launched", "Stage", "Etapa", "CLP26 · CO", "CLP26 · CO"),
        ],
        "sections": [
            ("01", "The Deal", "El Trato", "rgba(12,73,138,.30)", "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=1200&q=80",
             "Wood residue to gourmet protein", "Residuo de madera a proteína gourmet",
             "Fresh Orellana as alternative, versatile protein ready for market; sawdust and shavings processed into a raw material for new food formats.",
             "Orellana fresca como proteína alternativa y versátil lista para mercado; aserrín y viruta procesados en materia prima para nuevos formatos alimentarios."),
            ("02", "Customer Discovery", "Descubrimiento de Cliente", "rgba(102,147,72,.30)", "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80",
             "Consumer confirmed, channel shows scale", "Consumidor confirmó, canal mostró escala",
             "Deck notes consumer validation of the product and channel feedback on how to scale distribution in Colombia.",
             "El deck señala validación del producto por el consumidor y retroalimentación del canal sobre cómo escalar distribución en Colombia."),
            ("03", "Market", "Mercado", "rgba(12,73,138,.30)", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80",
             "Gourmet &amp; sustainable protein", "Proteína gourmet y sostenible",
             "Deck beachhead: natural stores, fruvers, supermarkets and specialized distributors in Bogotá; wider Colombia TAM context on slide.",
             "Beachhead del deck: tiendas naturales, fruvers, supermercados y distribuidores especializados en Bogotá; contexto TAM Colombia más amplio en lámina."),
            ("04", "Climate Impact", "Impacto Climático", "rgba(102,147,72,.30)", "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
             "Valorizing underused wood", "Valorizar madera subutilizada",
             "Converts underused wood residues into high-value food, aligned with Colombia climate goals (NDC) referenced on the climate impact slide.",
             "Convierte residuos de madera subutilizados en alimento de alto valor, alineado con metas climáticas de Colombia (NDC) referenciadas en lámina de impacto climático."),
        ],
        "cta_en": "Build a network that transforms wood waste into reliable gourmet mushroom protein for Colombia.",
        "cta_es": "Construir una red que transforme residuos de madera en proteína confiable de hongos gourmet para Colombia.",
        "cta_btn_en": "CleantechHUB profile",
        "cta_btn_es": "Perfil CleantechHUB",
    },
]


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def ribbon_html(rows):
    cells = []
    for val, lab_en, lab_es, sub_en, sub_es in rows:
        cells.append(
            f'<div class="ribbon-cell"><div class="rc-val">{val}</div>'
            f'<div class="rc-lab">{bi(lab_en, lab_es)}</div>'
            f'<div class="rc-sub">{bi(sub_en, sub_es)}</div></div>'
        )
    return "".join(cells)


def deck_block(d: dict) -> str:
    slug = d["slug"]
    n = d["pages"]
    drive = f"https://drive.google.com/file/d/{d['drive_id']}/view"
    bg = d.get("deck_bg") or "https://images.unsplash.com/photo-1611273426055-42c0128027fa?w=1200&q=80"
    if slug == "communitylab":
        bg = "/s/communitylab/assets/bg-deck.jpg"
    return f"""
<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{bg}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">📄</div><div class="sec-title">{bi("Pitch Deck", "Pitch Deck")}</div><div class="sec-rule"></div></div>
  <div class="deck-note">{bi("Slide preview from deck PDF (JPEG). Numbers on this profile match the deck only.", "Vista previa desde PDF del deck (JPEG). Los números en este perfil provienen solo del deck.")}</div>
  <div class="deck-wrap deck-slide-wrap"><div class="deck-panel deck-slide">
    <div class="deck-frame-wrap"><img class="deck-frame deck-img" id="deck-slide-{slug}" src="/s/{slug}/slides/s-1.jpg" alt="{d['name']} slide 1" loading="lazy"></div>
    <div class="deck-pager" data-base="/s/{slug}/slides/s" data-pages="{n}">
      <button type="button" class="deck-page-btn" data-dir="-1">Prev</button>
      <span class="deck-page-label">1 / {n}</span>
      <button type="button" class="deck-page-btn" data-dir="1">Next</button>
    </div>
    <script>(function(){{var root=document.currentScript.previousElementSibling;if(!root)return;var img=document.getElementById('deck-slide-{slug}');var label=root.querySelector('.deck-page-label');var total=+root.dataset.pages||1;var page=1;var base=root.dataset.base;function show(n){{page=Math.max(1,Math.min(total,n));if(img)img.src=base+'-'+page+'.jpg';if(label)label.textContent=page+' / '+total;root.querySelectorAll('.deck-page-btn').forEach(function(b){{var dir=+b.dataset.dir;b.disabled=dir<0?page<=1:page>=total;}});}}root.addEventListener('click',function(e){{var b=e.target.closest('.deck-page-btn');if(!b||b.disabled)return;show(page+(+b.dataset.dir||0));}});show(1);}})();</script>
    <div class="deck-fallback">{bi("Need the full deck?", "¿Necesitas el deck completo?")} <a href="{drive}" target="_blank" rel="noopener">{bi("Open PDF in Google Drive", "Abrir PDF en Google Drive")}</a></div>
  </div>
  <div class="deck-actions">
    <a class="cta-link" href="{drive}" target="_blank" rel="noopener">{bi("Open deck in Google Drive", "Abrir deck en Google Drive")}</a>
  </div></div>
</div><div class="accent-bar"></div>"""


def section_block(num, title_en, title_es, ov, bg, head_en, head_es, body_en, body_es):
    return f"""
<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{bg}');"></div>
  <div class="sec-ov" style="background:{ov};"></div>
  <div class="sec-header"><div class="sec-num">{num}</div><div class="sec-title">{bi(title_en, title_es)}</div><div class="sec-rule"></div></div>
  <div class="split" style="position:relative;z-index:2;"><div class="split-panel"><div class="split-frost">
    <div class="split-h">{bi(head_en, head_es)}</div>
    <div class="body-text">{bi(body_en, body_es)}</div>
  </div></div><div class="split-panel"><div class="split-frost"><div class="body-text">{bi("Taxonomy", "Taxonomía")}: {bi("See hero badge · deck is source for financials", "Ver badge hero · el deck es fuente para finanzas")}</div></div></div></div>
</div>"""


def build(d: dict) -> str:
    slug = d["slug"]
    sections = "".join(section_block(*s) for s in d["sections"])
    btn_en = d.get("cta_btn_en", "Visit website")
    btn_es = d.get("cta_btn_es", "Visitar sitio")
    web = d["website"]
    drive = f"https://drive.google.com/file/d/{d['drive_id']}/view"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{d['name']} — CleantechHUB Startup Profile</title>
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
  <img class="hero-img" src="{d['hero_image']}" alt="{d['name']}" loading="lazy">
  <div class="hero-ov"></div>
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);">{bi(d['badge_en'], d['badge_es'])}</div></div>
  <div class="hero-in">
    <div class="hero-name">{d['display_short']}</div>
    <div class="hero-sub">{bi(d['website_label'] + ' · ' + d['stage'], d['website_label'] + ' · ' + d['stage'])}</div>
    <div class="hero-pitch">{bi(d['pitch_en'], d['pitch_es'])}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>

<div class="ribbon" style="background:rgba(12,73,138,.95);">{ribbon_html(d['ribbon'])}</div>

<div class="sec" hidden>
  <div class="sec-header"><div class="sec-num">▶</div><div class="sec-title">{bi("Pitch Video", "Video Pitch")}</div><div class="sec-rule"></div></div>
  <div class="deck-wrap"><div class="yt-pitch"><div class="yt-pitch-frame"><iframe src="" title="YouTube pitch"></iframe></div></div></div>
</div>

{deck_block(d)}

{sections}

<div class="sec" hidden>
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">07</div><div class="sec-title">{bi("Founders", "Fundadores")}</div><div class="sec-rule"></div></div>
  <div class="team-grid">
    <div class="team-card"><div class="tp-name">—</div><div class="tp-role">{bi("Role pending", "Rol pendiente")}</div><div class="tp-bio">{bi("LinkedIn pending HITL", "LinkedIn pendiente HITL")}</div></div>
  </div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="cta">
    <div class="pill" style="background:rgba(157,195,132,.12);border:1px solid rgba(157,195,132,.2);color:var(--lg);margin-bottom:16px;">{bi(d['badge_en'], d['badge_es'])}</div>
    <div class="cta-name">{d['display_short']}</div>
    <div class="cta-pitch">{bi(d['cta_en'], d['cta_es'])}</div>
    <a class="cta-btn" href="{web}">{bi(btn_en, btn_es)}</a>
    <div class="cta-links">
      <a class="cta-link" href="https://nexus.cleantechhub.net/s/{slug}">{bi("Nexus Profile", "Perfil Nexus")}</a>
      <a class="cta-link" href="https://nexus.cleantechhub.net/p/startup-portfolio">{bi("157 Startups", "157 Startups")}</a>
      <a class="cta-link" href="{drive}" target="_blank" rel="noopener">{bi("Pitch deck (PDF)", "Pitch deck (PDF)")}</a>
    </div>
    <div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div>
    <div class="cta-port">{bi("CleantechHUB portfolio profile · Latin America", "Perfil portafolio CleantechHUB · América Latina")}</div>
  </div>
</div>
<div class="accent-bar"></div>
</body>
</html>"""


def main():
    for d in STARTUPS:
        out = ROOT / "onepagers" / "sites" / d["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build(d))
        print("wrote", out)


if __name__ == "__main__":
    main()
