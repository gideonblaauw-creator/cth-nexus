#!/usr/bin/env python3
"""Build CLP26 nexus-CO4 one-pagers: slide JPEGs + index.html (no PDF in repo)."""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "onepagers" / "sites"

STARTUPS = [
    {
        "slug": "green-textile-solutions",
        "name": "Green Textile Solutions",
        "short": "Green Textile Solutions",
        "country": "CO",
        "website": "",
        "stage": "Launched",
        "program": "CLP26",
        "theme": "CE",
        "ct1": "CT-WA-003",
        "ct1_label": "Recycling & Materials Recovery",
        "ct2": "CT-IN-003",
        "ct2_label": "Circular Economy & Clean Mfg",
        "drive_id": "1SZd3Sb05WfJp0aakJ895ALVGzshfiSjB",
        "badge_en": "Recycled resin from textile & plastic waste",
        "badge_es": "Resina reciclada de residuos textiles y plásticos",
        "pitch_en": "We transform textile and plastic waste into high-performance recycled resins for circular economy, traceability, and substitution of virgin raw materials.",
        "pitch_es": "Transformamos residuos textiles y plásticos en resinas recicladas de alto desempeño para economía circular, trazabilidad y sustitución de materia prima virgen.",
        "ribbon": [
            ("2,500", "COP / kg", "TREXIL", "Precio TREXIL"),
            ("CE", "Circular economy", "Service", "Servicio circular"),
            ("CO", "Colombia", "CLP26", "CLP26"),
            ("CT-WA-003", "Primary CT", "CT-IN-003", "Secondary CT"),
        ],
        "problem_en": "Companies seek sustainability and social benefits in final products while textile and plastic waste streams remain underused.",
        "problem_es": "Las empresas buscan sostenibilidad y beneficios sociales en productos finales mientras los flujos de residuos textiles y plásticos siguen subaprovechados.",
        "solution_cards": [
            ("♻️", "Collect", "Recoger", "Textile polyester waste and plastics as inputs.", "Residuos textiles de poliéster y plásticos como insumos."),
            ("⚙️", "Transform", "Transformar", "Extrusion to recycled pellets and resins for injection.", "Extrusión a pellets y resinas recicladas para inyección."),
            ("🏭", "Supply", "Suministrar", "Solutions for injection and industrial transformation.", "Soluciones para inyección y transformación industrial."),
            ("📉", "Substitute", "Sustituir", "TREXIL as a polypropylene (PP) substitute — 2,500 pesos/kg referenced in deck.", "TREXIL como sustituto de polipropileno (PP) — 2.500 pesos/kg referenciado en deck."),
        ],
        "impact_en": "Circular economy for textile and plastic waste with lower environmental impact and real traceability for industrial partners.",
        "impact_es": "Economía circular para residuos textiles y plásticos con menor impacto ambiental y trazabilidad real para aliados industriales.",
        "unsplash": "photo-1532996122724-e3c031a396bf",
    },
    {
        "slug": "honeyb",
        "name": "HoneyB",
        "short": "HoneyB",
        "country": "CO",
        "website": "",
        "stage": "Ideation",
        "program": "CLP26",
        "theme": "CE",
        "ct1": "CT-IN-003",
        "ct1_label": "Circular Economy & Clean Mfg",
        "ct2": "",
        "ct2_label": "",
        "drive_id": "1aHABMXFbh3dSBUHHt8zY0_ClgQMM_LsF",
        "badge_en": "Solid shampoo bars (packaging-free)",
        "badge_es": "Barras de shampoo sólido (sin envase)",
        "pitch_en": "70 g solid shampoo for daily B2C use — longer duration, accessible price, and less packaging and water use.",
        "pitch_es": "Shampoo sólido de 70 g para uso diario B2C — mayor duración, precio accesible y menos envases y uso de agua.",
        "ribbon": [
            ("70 g", "Bar size", "Producto", "Tamaño barra"),
            ("USD 9.6", "Reference price", "B2C", "Precio referencia"),
            ("Less", "Packaging", "Water savings", "Ahorro de agua"),
            ("CT-IN-003", "Primary CT", "Ideation", "Ideación"),
        ],
        "problem_en": "Liquid shampoo drives plastic packaging and water use in daily hair care.",
        "problem_es": "El shampoo líquido impulsa envases plásticos y uso de agua en el cuidado capilar diario.",
        "solution_cards": [
            ("🧴", "Product", "Producto", "Solid HONEY'B shampoo — wet, apply, rinse, and store.", "Shampoo sólido HONEY'B — mojar, aplicar, enjuagar y conservar."),
            ("🍯", "Honey", "Miel", "Honey sourced from Fundación Skambra al Desarrollo, Tierralta, Córdoba.", "Miel de Fundación Skambra al Desarrollo, Tierralta, Córdoba."),
            ("⏱️", "Duration", "Duración", "Deck compares ~58 washes vs liquid reference (~40 + 18).", "El deck compara ~58 lavadas vs referencia líquida (~40 + 18)."),
            ("🌍", "Impact", "Impacto", "Year 3 scenario: 60,000 bars sold; 1.5 t PET potentially avoided (deck assumption).", "Escenario año 3: 60.000 barras; 1,5 t PET potencialmente evitadas (supuesto del deck)."),
        ],
        "impact_en": "Contributes to fewer containers and water savings; deck cites TAM shampoo in Colombia USD 209.81 M.",
        "impact_es": "Contribuye a menos envases y ahorro de agua; el deck cita TAM shampoo en Colombia USD 209,81 M.",
        "unsplash": "photo-1542601906990-b4d3fb778b09",
    },
    {
        "slug": "kuo",
        "name": "KUO (SIGR)",
        "short": "KUO (SIGR)",
        "country": "CO",
        "website": "gmail.com",
        "stage": "Prototype",
        "program": "CLP26",
        "theme": "CE",
        "ct1": "CT-WA-003",
        "ct1_label": "Recycling & Materials Recovery",
        "ct2": "CT-IC-004",
        "ct2_label": "Climate Data Platforms",
        "drive_id": "1om8X0SfmujUKCIMS6HWixrYRIjfMBgCd",
        "badge_en": "IoT AI-sorting bins + waste service",
        "badge_es": "Canecas IoT con clasificación IA + servicio de residuos",
        "pitch_en": "We turn your organization's waste into certified data and economic return — SIGR smart bins with AI sorting for Bogotá enterprises.",
        "pitch_es": "Convertimos los residuos de su organización en datos certificados y retorno económico — caneca SIGR con clasificación IA para empresas en Bogotá.",
        "ribbon": [
            ("B2B", "Model", "Bogotá", "Bogotá"),
            ("$3–12M", "COP / month", "Service fee", "Tarifa servicio"),
            ("SIGR", "Hardware", "IoT + IA", "IoT + IA"),
            ("CT-WA-003", "Primary CT", "CT-IC-004", "Secondary CT"),
        ],
        "problem_en": "Large generators lack source separation and certified recovery data — value is lost in the bin.",
        "problem_es": "Los grandes generadores carecen de separación en fuente y datos certificados de aprovechamiento — se pierde valor en la basura.",
        "solution_cards": [
            ("🗑️", "SIGR bin", "Caneca SIGR", "IoT hardware for in-building waste capture.", "Hardware IoT para captura de residuos in situ."),
            ("🤖", "AI sort", "Clasificación IA", "AI-assisted classification of recovered materials.", "Clasificación asistida por IA de materiales recuperados."),
            ("📊", "Data", "Datos", "Certified waste data for organizations.", "Datos certificados de residuos para organizaciones."),
            ("💰", "Return", "Retorno", "Sell classified material — integrated waste management service.", "Venta de material clasificado — servicio integral de residuos."),
        ],
        "impact_en": "Deck cites avoided emissions when recycling vs virgin material (aluminum, PET, steel, cardboard, glass factors shown).",
        "impact_es": "El deck cita emisiones evitadas al reciclar vs material virgen (factores para aluminio, PET, acero, cartón, vidrio).",
        "unsplash": "photo-1611273426055-42c0128027fa",
    },
    {
        "slug": "modular-agrosolutions",
        "name": "Modular Agrosolutions",
        "short": "Modular Agrosolutions",
        "country": "CO",
        "website": "MODTECH.SITE/MA",
        "stage": "Prototype",
        "program": "CLP26",
        "theme": "BIO",
        "ct1": "CT-IC-003",
        "ct1_label": "Supply Chain Traceability",
        "ct2": "CT-AF-007",
        "ct2_label": "Precision Agri Data",
        "drive_id": "1m5F4NSnNsKDQSi4Bx2fjzOihfe7gvPxK",
        "badge_en": "Field traceability & ops platform (deep learning)",
        "badge_es": "Trazabilidad de campo y plataforma operativa (deep learning)",
        "pitch_en": "We replace incomplete, late, fraud-prone manual field data with a traceability and operations infrastructure powered by deep learning.",
        "pitch_es": "Reemplazamos captura manual incompleta, tardía y vulnerable al fraude por infraestructura de trazabilidad y gestión operativa con deep learning.",
        "ribbon": [
            ("Agro", "Industry", "Traceability", "Trazabilidad"),
            ("IA", "Deep learning", "Ops", "Operaciones"),
            ("CO", "Colombia", "CLP26", "CLP26"),
            ("CT-IC-003", "Primary CT", "CT-AF-007", "Secondary CT"),
        ],
        "problem_en": "Manual field data is incomplete, delayed, and vulnerable to fraud in agro-industry operations.",
        "problem_es": "Los datos de campo manuales son incompletos, tardíos y vulnerables al fraude en operaciones agroindustriales.",
        "solution_cards": [
            ("📱", "Capture", "Captura", "Infrastructure for traceability and operational management.", "Infraestructura de trazabilidad y gestión operativa."),
            ("🧠", "Deep learning", "Deep learning", "Resolve field challenges with deep learning models.", "Resolver retos de campo con modelos de deep learning."),
            ("🏭", "Agroindustry", "Agroindustria", "Target: medium and large agro-industrial companies.", "Objetivo: empresas agroindustriales medianas y grandes."),
            ("📈", "Productivity", "Productividad", "Deck positions productivity gains driven by AI.", "El deck posiciona incrementos de productividad impulsados por IA."),
        ],
        "impact_en": "Deck references sustainability / ESG and -800 kg CO₂e/Ha in materials shown.",
        "impact_es": "El deck referencia sostenibilidad / ESG y -800 kg CO₂e/Ha en materiales mostrados.",
        "unsplash": "photo-1500382017468-9049fed747ef",
    },
    {
        "slug": "nextgen-nutrition",
        "name": "NextGen Nutrition (Petfly)",
        "short": "NextGen Nutrition (Petfly)",
        "country": "CO",
        "website": "",
        "stage": "Launched",
        "program": "CLP26",
        "theme": "BIO",
        "ct1": "CT-AF-009",
        "ct1_label": "Bioeconomy & NbS",
        "ct2": "CT-WA-002",
        "ct2_label": "Organic Waste & Composting",
        "drive_id": "1xtJEOklpgJ9SVcZT0ro8iwU_b9nNkg8R",
        "badge_en": "Low-carbon functional pet-food ingredients",
        "badge_es": "Ingredientes funcionales bajos en carbono para mascotas",
        "pitch_en": "High-performance, low-carbon ingredients for formulators — powered by insects, plants, and natural bioactives; 0% meat.",
        "pitch_es": "Ingredientes de alto desempeño y bajo carbono para formuladores — con insectos, plantas y bioactivos naturales; 0% carne.",
        "ribbon": [
            ("USD 490", "/ kg", "Ingredient", "Ingrediente"),
            ("0%", "Meat", "Functional", "Funcional"),
            ("Pets", "Beachhead", "Colombia", "Colombia"),
            ("CT-AF-009", "Primary CT", "CT-WA-002", "Secondary CT"),
        ],
        "problem_en": "Pet nutrition formulators need quality, cost, and sustainability without relying on conventional meat proteins.",
        "problem_es": "Los formuladores de nutrición para mascotas necesitan calidad, costo y sostenibilidad sin depender de proteínas cárnicas convencionales.",
        "solution_cards": [
            ("🐛", "Bioactives", "Bioactivos", "Insects, plants, and natural bioactives as cores.", "Insectos, plantas y bioactivos naturales como núcleos."),
            ("🐕", "Petfly", "Petfly", "First application: functional, hypoallergenic supplements for sensitive pets.", "Primera aplicación: suplementos funcionales e hipoalergénicos para mascotas sensibles."),
            ("♻️", "Loop", "Ciclo", "Waste → health food side streams via bioconversion (deck).", "Desperdicios → corrientes side streams vía bioconversión (deck)."),
            ("🌍", "Climate", "Clima", "Deck: 1 tonne product → 15 t CO₂e mitigated; -93% CO₂ vs meat (as presented).", "Deck: 1 tonelada producto → 15 t CO₂e mitigadas; -93% CO₂ vs carne (como presentado)."),
        ],
        "impact_en": "Low-carbon animal protein alternative with precision formulation for pet health.",
        "impact_es": "Alternativa de proteína animal baja en carbono con formulación de precisión para salud de mascotas.",
        "unsplash": "photo-1587300003388-59208cc962cb",
    },
]


def download_pdf(file_id: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    if b"<!DOCTYPE html" in data[:512] or b"<html" in data[:512].lower():
        m = re.search(rb"confirm=([0-9A-Za-z_]+)", data)
        if m:
            url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={m.group(1).decode()}"
            with urllib.request.urlopen(url, timeout=120) as resp:
                data = resp.read()
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"Download for {file_id} did not yield a PDF ({len(data)} bytes)")
    dest.write_bytes(data)


def pdf_to_slides(pdf: Path, slides_dir: Path) -> int:
    slides_dir.mkdir(parents=True, exist_ok=True)
    for old in slides_dir.glob("s-*.jpg"):
        old.unlink()
    prefix = slides_dir / "s"
    subprocess.run(
        ["pdftoppm", "-jpeg", "-scale-to", "1600", str(pdf), str(prefix)],
        check=True,
    )
    generated = sorted(slides_dir.glob("s-*.jpg"))
    if not generated:
        # pdftoppm names s-01.jpg, s-02.jpg ...
        generated = sorted(slides_dir.glob("s-*.jpg"))
    # Normalize names to s-1.jpg, s-2.jpg ...
    numbered = sorted(slides_dir.glob("s-*.jpg"), key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))
    for i, path in enumerate(numbered, start=1):
        target = slides_dir / f"s-{i}.jpg"
        if path != target:
            path.rename(target)
    return len(list(slides_dir.glob("s-*.jpg")))


def bi(en: str, es: str) -> str:
    return f'<span class="en">{html.escape(en)}</span><span class="es">{html.escape(es)}</span>'


def build_html(s: dict, slide_count: int) -> str:
    slug = s["slug"]
    drive_url = f"https://drive.google.com/file/d/{s['drive_id']}/view"
    ct_badge = f"{s['ct1']} · {s['ct1_label']}"
    if s.get("ct2"):
        ct_badge += f" / {s['ct2']} · {s['ct2_label']}"
    website = (s.get("website") or "").strip()
    web_sub = html.escape(website) if website else "Colombia"
    web_btn = ""
    if website and "." in website:
        href = website if website.startswith("http") else f"https://{website.lower()}"
        web_btn = f'<a class="cta-btn" href="{html.escape(href)}">{bi("Visit website", "Visitar sitio")}</a>'
    else:
        web_btn = f'<span class="cta-btn" style="opacity:.65;pointer-events:none;">{bi("Website pending", "Sitio pendiente")}</span>'

    ribbon_cells = ""
    for a, b_en, c_en, c_es in s["ribbon"]:
        ribbon_cells += (
            f'<div class="ribbon-cell"><div class="rc-val">{html.escape(a)}</div>'
            f'<div class="rc-lab">{bi(b_en, c_en)}</div>'
            f'<div class="rc-sub">{bi(c_en, c_es)}</div></div>'
        )

    sol_cards = ""
    for icon, lab_en, lab_es, txt_en, txt_es in s["solution_cards"]:
        sol_cards += (
            f'<div class="sol-card"><div class="sol-icon">{icon}</div>'
            f'<div class="sol-label">{bi(lab_en, lab_es)}</div>'
            f'<div class="sol-text">{bi(txt_en, txt_es)}</div></div>'
        )

    unsplash = s["unsplash"]
    title = html.escape(s["name"])

    deck_pager_script = (
        "(function(){var root=document.currentScript.previousElementSibling;if(!root)return;"
        "var img=root.parentElement.querySelector('.deck-slide-img');"
        "var label=root.querySelector('.deck-page-label');"
        "var total=+root.dataset.pages||1;var page=1;"
        "function show(n){page=Math.max(1,Math.min(total,n));"
        "if(img)img.src='slides/s-'+page+'.jpg';"
        "if(label)label.textContent=page+' / '+total;"
        "root.querySelectorAll('.deck-page-btn').forEach(function(b){var dir=+b.dataset.dir;"
        "b.disabled=dir<0?page<=1:page>=total;});}"
        "root.addEventListener('click',function(e){var b=e.target.closest('.deck-page-btn');"
        "if(!b||b.disabled)return;show(page+(+b.dataset.dir||0));});show(1);})();"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — CleantechHUB Startup Profile</title>
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
.frost-panel,.stat-card,.sol-card,.imp-card,.team-card,.comp-tbl,.split-frost,.deck-panel,.frost-note{{background:var(--panel);backdrop-filter:blur(12px) saturate(1.35);-webkit-backdrop-filter:blur(12px) saturate(1.35);border:1px solid var(--panel-border);box-shadow:0 8px 32px rgba(0,0,0,.42);}}
.stat-row{{display:flex;gap:10px;margin-top:14px;}}
.stat-card{{flex:1;border-radius:8px;padding:14px;text-align:center;}}
.sc-num{{font-size:26px;font-weight:800;color:#e8ffd4;line-height:1;}}
.sc-lab{{font-size:9px;font-weight:700;color:rgba(255,255,255,.9);margin-top:3px;line-height:1.3;}}
.sol-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:0 48px 32px;position:relative;z-index:2;}}
.sol-card{{border-radius:8px;padding:22px 18px;text-align:center;}}
.sol-icon{{font-size:24px;margin-bottom:6px;}}
.sol-label{{font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#e8ffd4;margin-bottom:6px;}}
.sol-text{{font-size:11px;line-height:1.5;color:rgba(255,255,255,.92);}}
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
.cta-btn{{display:inline-block;background:linear-gradient(180deg,#d4f5b8 0%,var(--lg) 100%);color:#053a6e;font-size:14px;font-weight:800;padding:14px 36px;border-radius:6px;text-decoration:none;margin-top:20px;border:2px solid #fff;box-shadow:0 6px 22px rgba(0,0,0,.45);}}
.cta-links{{display:flex;gap:10px;justify-content:center;margin-top:16px;flex-wrap:wrap;}}
.cta-link{{font-size:10px;font-weight:700;color:#fff;text-decoration:none;padding:8px 16px;background:var(--panel);border:1px solid var(--panel-border);border-radius:6px;box-shadow:0 4px 16px rgba(0,0,0,.35);}}
.cta-brand{{margin-top:24px;}}
.cta-brand .tg{{font-size:12px;font-style:italic;color:#e8ffd4;opacity:.95;}}
.cta-brand .lg2{{font-size:14px;font-weight:800;margin-top:4px;color:#fff;}}
.cta-port{{font-size:9px;color:rgba(255,255,255,.8);margin-top:10px;}}
.split-frost{{padding:24px 28px;border-radius:8px;flex:1;display:flex;flex-direction:column;justify-content:center;min-height:100%;}}
.split-frost-stats .stat-row{{flex:1;align-items:stretch;margin-top:0;}}
.split-frost-stats .stat-card{{background:transparent;border:none;box-shadow:none;}}
.deck-wrap{{padding:0 48px 32px;position:relative;z-index:2;}}
.deck-panel{{padding:16px;border-radius:8px;}}
.deck-frame-wrap{{width:100%;border-radius:6px;overflow:hidden;background:#fff;box-shadow:0 14px 40px rgba(0,0,0,.5);line-height:0;}}
.deck-slide-img{{width:100%;height:auto;display:block;background:#fff;}}
.deck-fallback{{margin-top:12px;font-size:10px;color:rgba(255,255,255,.85);text-align:center;text-shadow:0 1px 8px rgba(0,0,0,.5);}}
.deck-fallback a{{color:#e8ffd4;font-weight:700;}}
.deck-actions{{display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap;}}
.deck-note{{padding:0 48px 8px;font-size:10px;color:rgba(255,255,255,.9);text-align:center;position:relative;z-index:2;text-shadow:0 1px 8px rgba(0,0,0,.5);}}
.deck-slide{{width:min(100%,640px);margin-left:auto;margin-right:auto;}}
.deck-pager{{display:flex;align-items:center;justify-content:center;gap:10px;margin-top:10px;}}
.deck-page-btn{{font-family:'Open Sans',sans-serif;font-size:10px;font-weight:700;color:#fff;background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.35);border-radius:4px;padding:5px 12px;cursor:pointer;}}
.deck-page-btn:disabled{{opacity:.4;cursor:default;}}
.deck-page-label{{font-size:10px;font-weight:700;color:#e8ffd4;min-width:52px;text-align:center;}}
.yt-pitch{{width:min(100%,640px);margin:0 auto 8px;position:relative;z-index:2;}}
.yt-pitch-frame{{position:relative;width:100%;aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:#000;}}
.yt-pitch-frame iframe{{position:absolute;inset:0;width:100%;height:100%;border:0;}}
</style>
</head>
<body>
<div class="site-brand"><span class="brand-text">Cleantech<em>HUB</em></span></div>
<div class="lang-toggle">
  <button class="lb active" onclick="document.documentElement.lang='en';this.classList.add('active');this.nextElementSibling.classList.remove('active');">EN</button>
  <button class="lb" onclick="document.documentElement.lang='es';this.classList.add('active');this.previousElementSibling.classList.remove('active');">ES</button>
</div>

<div class="sec hero">
  <img class="hero-img" src="https://images.unsplash.com/{unsplash}?w=1200&q=80" alt="{title}" loading="lazy">
  <div class="hero-ov"></div>
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);">{bi(s['badge_en'], s['badge_es'])}</div></div>
  <div class="hero-in">
    <div class="hero-name">{html.escape(s['short'])}</div>
    <div class="hero-sub">{bi(f"{web_sub} · Colombia · {s['stage']}", f"{web_sub} · Colombia · {s['stage']}")} · {bi(ct_badge, ct_badge)}</div>
    <div class="hero-pitch">{bi(s['pitch_en'], s['pitch_es'])}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>

<div class="ribbon" style="background:rgba(12,73,138,.95);">{ribbon_cells}</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/{unsplash}?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">📄</div><div class="sec-title">{bi("Pitch Deck", "Pitch Deck")}</div><div class="sec-rule"></div></div>
  <div class="deck-note">{bi("Slide images from deck — numbers on this profile match the deck only.", "Imágenes del deck — los números en este perfil provienen solo del deck.")}</div>
  <div class="deck-wrap deck-slide-wrap">
    <div class="deck-panel deck-slide">
      <div class="deck-frame-wrap"><img class="deck-slide-img" src="slides/s-1.jpg" alt="{title} pitch deck slide"></div>
      <div class="deck-pager" data-pages="{slide_count}"><button type="button" class="deck-page-btn" data-dir="-1">Prev</button><span class="deck-page-label">1 / {slide_count}</span><button type="button" class="deck-page-btn" data-dir="1">Next</button></div>
      <script>{deck_pager_script}</script>
      <div class="deck-fallback">{bi("Need the file?", "¿Necesita el archivo?")} <a href="{drive_url}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a></div>
    </div>
    <div class="deck-actions"><a class="cta-link" href="{drive_url}" target="_blank" rel="noopener">{bi("Open deck in Google Drive", "Abrir deck en Google Drive")}</a></div>
  </div>
</div>
<div class="accent-bar"></div>

<div class="sec" hidden>
  <div class="sec-header"><div class="sec-num">▶</div><div class="sec-title">{bi("Pitch Video", "Video pitch")}</div><div class="sec-rule"></div></div>
  <div class="deck-wrap"><div class="yt-pitch"><div class="yt-pitch-frame"><iframe src="" title="YouTube pitch" allowfullscreen></iframe></div></div></div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">01</div><div class="sec-title">{bi("The Problem", "El Problema")}</div><div class="sec-rule"></div></div>
  <div class="split" style="position:relative;z-index:2;">
    <div class="split-panel"><div class="split-frost"><div class="split-h">{bi("Problem context", "Contexto del problema")}</div><div class="body-text">{bi(s['problem_en'], s['problem_es'])}</div></div></div>
    <div class="split-panel"><div class="split-frost split-frost-stats"><div class="stat-row" style="margin-top:0;"><div class="stat-card"><div class="sc-num">{html.escape(s['stage'])}</div><div class="sc-lab">{bi("Stage", "Etapa")}</div></div><div class="stat-card"><div class="sc-num">CO</div><div class="sc-lab">{bi("Country", "País")}</div></div></div><div class="stat-row"><div class="stat-card"><div class="sc-num">{html.escape(s['ct1'])}</div><div class="sc-lab">{bi("Primary CT", "CT primario")}</div></div><div class="stat-card"><div class="sc-num">{html.escape(s.get('ct2') or '—')}</div><div class="sc-lab">{bi("Secondary CT", "CT secundario")}</div></div></div></div></div>
  </div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(102,147,72,.30);"></div>
  <div class="sec-header"><div class="sec-num">02</div><div class="sec-title">{bi("The Solution", "La Solución")}</div><div class="sec-rule"></div></div>
  <div class="sol-grid">{sol_cards}</div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(102,147,72,.30);"></div>
  <div class="sec-header"><div class="sec-num">03</div><div class="sec-title">{bi("Climate & Impact", "Clima e Impacto")}</div><div class="sec-rule"></div></div>
  <div class="impact-grid"><div class="imp-card"><div class="imp-icon">🌱</div><div><div class="imp-title">{bi("Impact", "Impacto")}</div><div class="imp-text">{bi(s['impact_en'], s['impact_es'])}</div></div></div></div>
</div>

<div class="sec" hidden>
  <div class="sec-header"><div class="sec-num">07</div><div class="sec-title">{bi("Founders", "Fundadores")}</div><div class="sec-rule"></div></div>
  <div class="team-grid"><div class="team-card"><div class="tp-name"></div><div class="tp-role"></div><a class="tp-link" href=""></a></div></div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('https://images.unsplash.com/{unsplash}?w=1200&q=80');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="cta">
    <div class="pill" style="background:rgba(157,195,132,.12);border:1px solid rgba(157,195,132,.2);color:var(--lg);margin-bottom:16px;">{bi(s['badge_en'], s['badge_es'])}</div>
    <div class="cta-name">{html.escape(s['short'])}</div>
    <div class="cta-pitch">{bi(s['pitch_en'], s['pitch_es'])}</div>
    {web_btn}
    <div class="cta-links">
      <a class="cta-link" href="https://nexus.cleantechhub.net/s/{slug}">{bi("Nexus Profile", "Perfil Nexus")}</a>
      <a class="cta-link" href="https://nexus.cleantechhub.net/p/startup-portfolio">{bi("157 Startups", "157 Startups")}</a>
      <a class="cta-link" href="{drive_url}" target="_blank" rel="noopener">{bi("Pitch deck (PDF)", "Pitch deck (PDF)")}</a>
    </div>
    <div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div>
    <div class="cta-port">{bi("CleantechHUB portfolio profile · Latin America", "Perfil portafolio CleantechHUB · América Latina")}</div>
  </div>
</div>
<div class="accent-bar"></div>
</body>
</html>
"""


def update_shareable_json(slide_counts: dict[str, int]) -> None:
    path = ROOT / "nexus" / "nexus-assets" / "epic-angels-shareable.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    startups = data["startups"]
    by_slug = {s["slug"]: i for i, s in enumerate(startups)}

    for s in STARTUPS:
        entry = {
            "slug": s["slug"],
            "name": s["name"],
            "country": s["country"],
            "website": s.get("website") or "",
            "program": "CLP26",
            "theme": s["theme"],
            "stage": s["stage"],
            "ct1": s["ct1"],
            "founder": "",
            "youtube": "",
            "onepager": s["slug"],
        }
        if s.get("ct2"):
            entry["ct2"] = s["ct2"]
        flags = s.get("flags") or []
        if flags:
            entry["flags"] = flags
        if s["slug"] in by_slug:
            startups[by_slug[s["slug"]]] = entry
        else:
            startups.append(entry)

    data["startups"] = startups
    data["count"] = len(startups)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    slide_counts: dict[str, int] = {}
    tmp = ROOT / ".tmp-co4-decks"
    tmp.mkdir(exist_ok=True)

    for s in STARTUPS:
        slug = s["slug"]
        site = SITES / slug
        site.mkdir(parents=True, exist_ok=True)
        pdf = tmp / f"{slug}.pdf"
        print(f"=== {slug} ===")
        if not pdf.is_file() or not pdf.read_bytes()[:4].startswith(b"%PDF"):
            download_pdf(s["drive_id"], pdf)
        n = pdf_to_slides(pdf, site / "slides")
        slide_counts[slug] = n
        print(f"  slides: {n}")
        (site / "index.html").write_text(build_html(s, n), encoding="utf-8")

    update_shareable_json(slide_counts)
    print(json.dumps(slide_counts, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
