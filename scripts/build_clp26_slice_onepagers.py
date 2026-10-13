#!/usr/bin/env python3
"""Build CLP26 slice Nexus one-pagers (curuba-style shell, slice JSON fields only)."""
from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data" / "clp26-slices"
BASE_CSS = ROOT / "onepagers" / "template" / "styles.css"
SLICE_CSS = ROOT / "onepagers" / "template" / "clp26_slice.css"
OUT_REPO = ROOT / "onepagers" / "sites"
TAXONOMY_WIKI = "https://wiki.cleantechhub.net/search?term={code}"

SLUGS_DEFAULT = ("ecomuna", "q-mind", "pina-kakaw")


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def field_value(raw: dict, key: str) -> str | None:
    node = raw.get(key)
    if node is None:
        return None
    if isinstance(node, dict) and "value" in node:
        val = node["value"]
    else:
        val = node
    if val is None:
        return None
    if isinstance(val, str) and not val.strip():
        return None
    return str(val)


def normalize_slice(raw: dict) -> dict:
    slug = field_value(raw, "slug") or raw.get("slug", "")
    code = field_value(raw, "taxonomy_link") or field_value(raw, "taxonomy_code")
    taxonomy_url = TAXONOMY_WIKI.format(code=quote(code, safe="")) if code else None
    return {
        "slug": slug,
        "name": field_value(raw, "name") or "",
        "founder_linkedin": field_value(raw, "founder_linkedin"),
        "website": field_value(raw, "website"),
        "taxonomy_code": code,
        "taxonomy_url": taxonomy_url,
        "short_description": field_value(raw, "short_description_es")
        or field_value(raw, "short_description"),
        "youtube_pitch_url": field_value(raw, "youtube_pitch_url"),
        "nexus_profile_url": field_value(raw, "nexus_profile_url"),
        "one_pager_url": field_value(raw, "one_pager_url") or field_value(raw, "one_pager_link"),
        "country": field_value(raw, "country"),
        "stage": field_value(raw, "stage"),
    }


def profile_slot(value: str | None, link: bool = False) -> str:
    if not value:
        return '<span class="profile-empty" aria-hidden="true"></span>'
    esc = html.escape(value)
    if link:
        return f'<a href="{esc}" target="_blank" rel="noopener">{esc}</a>'
    return esc


def build_page(d: dict) -> str:
    slug = d["slug"]
    name = html.escape(d["name"])
    desc = html.escape(d["short_description"] or "")
    css = BASE_CSS.read_text() + "\n" + SLICE_CSS.read_text()

    badge_bits = ["CLP26"]
    if d.get("country"):
        badge_bits.append(html.escape(d["country"]))
    if d.get("stage"):
        badge_bits.append(html.escape(d["stage"]))
    badge = " · ".join(badge_bits)

    founder = profile_slot(d.get("founder_linkedin"), link=True)
    website = profile_slot(d.get("website"), link=True)
    if d.get("taxonomy_url") and d.get("taxonomy_code"):
        code_esc = html.escape(d["taxonomy_code"])
        taxonomy = (
            f'<a href="{html.escape(d["taxonomy_url"])}" target="_blank" rel="noopener">{code_esc}</a>'
        )
    else:
        taxonomy = profile_slot(None)
    nexus = profile_slot(d.get("nexus_profile_url"), link=True)
    onepager = profile_slot(d.get("one_pager_url"), link=True)

    youtube_block = ""
    yt = d.get("youtube_pitch_url")
    if yt:
        yt_esc = html.escape(yt, quote=True)
        youtube_block = f"""
<div class="sec youtube-sec">
  <div class="sec-header" style="padding-left:0;padding-right:0;">
    <div class="sec-num">▶</div>
    <div class="sec-title">{bi("Pitch video", "Video pitch")}</div>
    <div class="sec-rule"></div>
  </div>
  <div class="youtube-wrap">
    <iframe src="{yt_esc}" title="{name} pitch" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
  </div>
</div>
<div class="accent-bar"></div>
"""

    pdf_url = f"/s/{slug}/deck.pdf"
    deck_js = f"""
<script type="module">
import * as pdfjsLib from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.mjs';
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.mjs';
const url = '{pdf_url}';
const canvas = document.getElementById('deck-canvas');
const ctx = canvas.getContext('2d');
const label = document.getElementById('deck-page-label');
const prev = document.getElementById('deck-prev');
const next = document.getElementById('deck-next');
let pdfDoc = null;
let pageNum = 1;
let pageCount = 0;
async function renderPage(num) {{
  const page = await pdfDoc.getPage(num);
  const viewport = page.getViewport({{ scale: 1.5 }});
  canvas.width = viewport.width;
  canvas.height = viewport.height;
  await page.render({{ canvasContext: ctx, viewport }}).promise;
  label.textContent = num + ' / ' + pageCount;
  prev.disabled = num <= 1;
  next.disabled = num >= pageCount;
}}
prev.addEventListener('click', () => {{ if (pageNum > 1) {{ pageNum--; renderPage(pageNum); }} }});
next.addEventListener('click', () => {{ if (pageNum < pageCount) {{ pageNum++; renderPage(pageNum); }} }});
pdfjsLib.getDocument(url).promise.then(doc => {{
  pdfDoc = doc;
  pageCount = doc.numPages;
  renderPage(1);
}}).catch(() => {{
  label.textContent = '—';
  prev.disabled = true;
  next.disabled = true;
}});
</script>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — CleantechHUB Startup Profile</title>
<link rel="icon" href="https://cleantechhub.net/favicon.ico">
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&family=PT+Sans:wght@400;700&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div class="site-brand"><span class="brand-text">Cleantech<em>HUB</em></span></div>
<div class="lang-toggle">
  <button class="lb active" onclick="document.documentElement.lang='en';this.classList.add('active');this.nextElementSibling.classList.remove('active');">EN</button>
  <button class="lb" onclick="document.documentElement.lang='es';this.classList.add('active');this.previousElementSibling.classList.remove('active');">ES</button>
</div>

<div class="sec hero hero--slice">
  <div class="hero-ov"></div>
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);">{badge}</div></div>
  <div class="hero-in">
    <div class="hero-name">{name}</div>
    <div class="hero-pitch">{desc}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>

<div class="profile-sec">
  <div class="profile-panel">
    <div class="profile-grid">
      <div class="profile-row">
        <div class="profile-label">{bi("Founder LinkedIn", "LinkedIn del fundador")}</div>
        <div class="profile-value">{founder}</div>
      </div>
      <div class="profile-row">
        <div class="profile-label">{bi("Website", "Sitio web")}</div>
        <div class="profile-value">{website}</div>
      </div>
      <div class="profile-row">
        <div class="profile-label">{bi("CT Taxonomy", "Taxonomía CT")}</div>
        <div class="profile-value">{taxonomy}</div>
      </div>
      <div class="profile-row">
        <div class="profile-label">{bi("Short description", "Descripción breve")}</div>
        <div class="profile-value">{desc or profile_slot(None)}</div>
      </div>
      <div class="profile-row">
        <div class="profile-label">{bi("Nexus profile", "Perfil Nexus")}</div>
        <div class="profile-value">{nexus}</div>
      </div>
      <div class="profile-row">
        <div class="profile-label">{bi("One-pager", "One-pager")}</div>
        <div class="profile-value">{onepager}</div>
      </div>
    </div>
  </div>
</div>
<div class="accent-bar"></div>

<div class="sec deck-sec">
  <div class="sec-header" style="padding-left:0;padding-right:0;">
    <div class="sec-num">📄</div>
    <div class="sec-title">{bi("Pitch deck", "Pitch deck")}</div>
    <div class="sec-rule"></div>
  </div>
  <div class="deck-viewer">
    <div class="deck-canvas-wrap"><canvas id="deck-canvas" class="deck-canvas" aria-label="Pitch deck slide"></canvas></div>
    <div class="deck-controls">
      <button type="button" class="deck-btn" id="deck-prev">{bi("Previous", "Anterior")}</button>
      <span class="deck-page-label" id="deck-page-label">…</span>
      <button type="button" class="deck-btn" id="deck-next">{bi("Next", "Siguiente")}</button>
    </div>
  </div>
  <div class="deck-open"><a href="{pdf_url}" target="_blank" rel="noopener">{bi("Open deck PDF", "Abrir PDF del deck")}</a></div>
</div>
<div class="accent-bar"></div>

{youtube_block}

<div class="sec footer-sec">
  <div class="cta-name">{name}</div>
  <div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div>
  <div class="cta-port">{bi("Draft preview — not deployed to /opt/nexus-onepagers", "Vista previa borrador — no desplegado en /opt/nexus-onepagers")}</div>
</div>
<div class="accent-bar"></div>
{deck_js}
</body>
</html>"""


def empty_fields(d: dict) -> list[str]:
    out: list[str] = []
    if not d.get("founder_linkedin"):
        out.append("founder_linkedin")
    if not d.get("website"):
        out.append("website")
    if not d.get("taxonomy_code"):
        out.append("taxonomy_link")
    if not d.get("youtube_pitch_url"):
        out.append("youtube_pitch_url")
    if not d.get("nexus_profile_url"):
        out.append("nexus_profile_url")
    if not d.get("one_pager_url"):
        out.append("one_pager_link")
    return out


def main(argv: list[str]) -> None:
    slugs = argv or list(SLUGS_DEFAULT)
    decks_src = {
        "ecomuna": Path("/home/ubuntu/.cursor/projects/workspace/uploads/ecomuna_7c22.pdf"),
        "q-mind": Path("/home/ubuntu/.cursor/projects/workspace/uploads/q-mind_6d45.pdf"),
        "pina-kakaw": Path("/home/ubuntu/.cursor/projects/workspace/uploads/pina-kakaw_a0e7.pdf"),
    }
    slice_src = {
        "ecomuna": Path("/home/ubuntu/.cursor/projects/workspace/uploads/ecomuna_8285.json"),
        "q-mind": Path("/home/ubuntu/.cursor/projects/workspace/uploads/q-mind_6588.json"),
        "pina-kakaw": Path("/home/ubuntu/.cursor/projects/workspace/uploads/pina-kakaw_d3aa.json"),
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for slug in slugs:
        src_json = slice_src.get(slug) or DATA_DIR / f"{slug}.json"
        if not src_json.is_file():
            print(f"Skip {slug}: missing slice JSON", file=sys.stderr)
            continue
        raw = json.loads(src_json.read_text())
        data = normalize_slice(raw)
        (DATA_DIR / f"{slug}.json").write_text(json.dumps(data, indent=2) + "\n")

        out_dir = OUT_REPO / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(build_page(data))

        deck_src = decks_src.get(slug)
        if deck_src and deck_src.is_file():
            shutil.copy2(deck_src, out_dir / "deck.pdf")
        else:
            print(f"Warning: missing deck PDF for {slug}", file=sys.stderr)

        missing = empty_fields(data)
        print(f"Built {slug}; empty fields: {', '.join(missing) or '(none)'}")


if __name__ == "__main__":
    main(sys.argv[1:])
