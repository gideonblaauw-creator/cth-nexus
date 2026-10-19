#!/usr/bin/env python3
"""Build CLP26 Peru slice one-pagers (/s/{slug}) from slice JSON + deck PDF."""
from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SLICE_DIR = ROOT / "onepagers" / "data" / "clp26-slices"
DECK_DIR = ROOT / "onepagers" / "decks"
TEMPLATE_CSS = ROOT / "onepagers" / "template" / "clp26-slice.css"
OUT_REPO = ROOT / "onepagers" / "sites"
OUT_ARCHIVE = Path("/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20")

HERO_IMAGE = "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80"
BG_DECK = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80"
BG_CTA = "https://images.unsplash.com/photo-1504541331459-5288e5d49ee3?w=1200&q=80"
WIKI_TAXONOMY_PREFIX = "https://wiki.cleantechhub.net/search?term="
NEXUS_BASE = "https://nexus.cleantechhub.net"


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def field_val(slice_doc: dict, key: str) -> str | None:
    node = slice_doc.get(key)
    if not isinstance(node, dict):
        return None
    v = node.get("value")
    if v is None or v == "":
        return None
    return str(v)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def empty_slot() -> str:
    return f'<span class="slot-empty">{bi("[empty]", "[vacío]")}</span>'


def link_or_empty(url: str | None, label: str | None = None) -> str:
    if not url:
        return empty_slot()
    text = esc(label or url)
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{text}</a>'


def taxonomy_cell(code: str | None) -> str:
    if not code:
        return empty_slot()
    url = f"{WIKI_TAXONOMY_PREFIX}{quote(code, safe='')}"
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(code)}</a>'


def youtube_id(url: str) -> str | None:
    u = url.strip()
    if "youtu.be/" in u:
        return u.rsplit("/", 1)[-1].split("?")[0]
    if "youtube.com/watch" in u and "v=" in u:
        return u.split("v=", 1)[1].split("&")[0]
    if "youtube.com/embed/" in u:
        return u.rsplit("/", 1)[-1].split("?")[0]
    return None


def build_page(slice_doc: dict) -> str:
    css = TEMPLATE_CSS.read_text()
    slug = field_val(slice_doc, "slug") or slice_doc.get("slug", "startup")
    name = field_val(slice_doc, "name") or slug
    country = field_val(slice_doc, "country") or ""
    stage = field_val(slice_doc, "stage") or ""
    short_es = field_val(slice_doc, "short_description_es") or ""
    founder_li = field_val(slice_doc, "founder_linkedin")
    website = field_val(slice_doc, "website")
    taxonomy = field_val(slice_doc, "taxonomy_link")
    nexus_ideas = field_val(slice_doc, "nexus_profile_url")
    youtube = field_val(slice_doc, "youtube_pitch_url")

    hero_sub_en = f"CLP26 · Peru · {stage}" if stage else "CLP26 · Peru"
    hero_sub_es = f"CLP26 · Perú · {stage}" if stage else "CLP26 · Perú"
    if country and country != "PE":
        hero_sub_en = f"CLP26 · {country} · {stage}".rstrip(" ·")
        hero_sub_es = hero_sub_en

    pitch_en = short_es
    pitch_es = short_es

    youtube_section = ""
    if youtube:
        vid = youtube_id(youtube)
        if vid:
            embed = f"https://www.youtube.com/embed/{esc(vid)}"
            youtube_section = f"""
<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{BG_DECK}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">▶</div><div class="sec-title">{bi("Pitch video", "Video pitch")}</div><div class="sec-rule"></div></div>
  <div class="video-wrap"><div class="video-panel"><iframe class="video-frame" src="{embed}" title="{esc(name)} pitch" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div></div>
</div>
<div class="accent-bar"></div>"""

    nexus_link = (
        f'<a class="cta-link" href="{esc(nexus_ideas)}" target="_blank" rel="noopener">'
        f'{bi("Nexus profile", "Perfil Nexus")}</a>'
        if nexus_ideas
        else f'<span class="cta-link" style="opacity:.55;cursor:default;">{bi("Nexus profile", "Perfil Nexus")}: {empty_slot()}</span>'
    )
    onepager_url = f"{NEXUS_BASE}/s/{esc(slug)}"
    deck_pdf_url = f"/s/{esc(slug)}/deck.pdf"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(name)} — CLP26 CleantechHUB</title>
<link rel="icon" href="https://cleantechhub.net/favicon.ico">
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&family=PT+Sans:wght@400;700&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div class="site-brand"><span class="brand-text">Cleantech<em>HUB</em></span></div>
<div class="lang-toggle">
  <button class="lb" onclick="document.documentElement.lang='en';this.classList.add('active');this.nextElementSibling.classList.remove('active');">EN</button>
  <button class="lb active" onclick="document.documentElement.lang='es';this.classList.add('active');this.previousElementSibling.classList.remove('active');">ES</button>
</div>

<div class="sec hero">
  <img class="hero-img" src="{HERO_IMAGE}" alt="{esc(name)}" loading="lazy">
  <div class="hero-ov"></div>
  <div class="hero-in">
    <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);">{bi("CLP26 Peru cohort", "Cohorte CLP26 Perú")}</div></div>
    <div class="hero-name">{esc(name)}</div>
    <div class="hero-sub">{bi(hero_sub_en, hero_sub_es)}</div>
    <div class="hero-pitch">{bi(pitch_en, pitch_es) if short_es else empty_slot()}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{HERO_IMAGE}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">i</div><div class="sec-title">{bi("Startup profile", "Perfil startup")}</div><div class="sec-rule"></div></div>
  <div class="meta-wrap"><div class="meta-panel"><div class="meta-grid">
    <div class="meta-item"><div class="meta-lab">{bi("Name", "Nombre")}</div><div class="meta-val">{esc(name)}</div></div>
    <div class="meta-item"><div class="meta-lab">{bi("Founder LinkedIn", "LinkedIn fundador")}</div><div class="meta-val">{link_or_empty(founder_li, "LinkedIn")}</div></div>
    <div class="meta-item"><div class="meta-lab">{bi("Website", "Sitio web")}</div><div class="meta-val">{link_or_empty(website)}</div></div>
    <div class="meta-item"><div class="meta-lab">{bi("CT taxonomy", "Taxonomía CT")}</div><div class="meta-val">{taxonomy_cell(taxonomy)}</div></div>
    <div class="meta-item" style="grid-column:1/-1;"><div class="meta-lab">{bi("Short description", "Descripción breve")}</div><div class="meta-val">{esc(short_es) if short_es else empty_slot()}</div></div>
  </div></div></div>
</div>
<div class="accent-bar"></div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{BG_DECK}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">📄</div><div class="sec-title">{bi("Pitch deck", "Pitch deck")}</div><div class="sec-rule"></div></div>
  <div class="deck-note">{bi("One slide at a time — use arrows to browse the deck.", "Una diapositiva a la vez — use las flechas para recorrer el deck.")}</div>
  <div class="deck-wrap"><div class="deck-panel">
    <div class="deck-canvas-wrap"><canvas id="deck-canvas" class="deck-canvas"></canvas></div>
    <div class="deck-nav">
      <button type="button" id="deck-prev" aria-label="Previous slide">{bi("← Previous", "← Anterior")}</button>
      <span class="deck-page-label" id="deck-page-label">—</span>
      <button type="button" id="deck-next" aria-label="Next slide">{bi("Next →", "Siguiente →")}</button>
    </div>
    <div class="deck-actions">
      <a class="cta-link" href="{deck_pdf_url}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a>
      <a class="cta-link" href="{deck_pdf_url}" download>{bi("Download PDF", "Descargar PDF")}</a>
    </div>
  </div></div>
</div>
<div class="accent-bar"></div>
{youtube_section}

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{BG_CTA}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="cta">
    <div class="cta-links">
      {nexus_link}
      <a class="cta-link" href="{onepager_url}">{bi("One-pager", "One-pager")}</a>
      <a class="cta-link" href="{deck_pdf_url}" target="_blank" rel="noopener">{bi("Deck (PDF)", "Deck (PDF)")}</a>
    </div>
    <div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div>
    <div class="cta-port">{bi("Draft — not deployed to /opt/nexus-onepagers", "Borrador — no desplegado en /opt/nexus-onepagers")}</div>
  </div>
</div>
<div class="accent-bar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script>
(function() {{
  var pdfUrl = "{deck_pdf_url}";
  var canvas = document.getElementById("deck-canvas");
  var label = document.getElementById("deck-page-label");
  var prev = document.getElementById("deck-prev");
  var next = document.getElementById("deck-next");
  var pdfDoc = null;
  var pageNum = 1;
  var pageRendering = false;
  var pageNumPending = null;

  if (!window["pdfjsLib"]) {{
    label.textContent = "PDF.js unavailable";
    return;
  }}
  pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

  function renderPage(num) {{
    pageRendering = true;
    pdfDoc.getPage(num).then(function(page) {{
      var viewport = page.getViewport({{ scale: 1.5 }});
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      return page.render({{ canvasContext: canvas.getContext("2d"), viewport: viewport }}).promise;
    }}).then(function() {{
      pageRendering = false;
      label.textContent = num + " / " + pdfDoc.numPages;
      prev.disabled = num <= 1;
      next.disabled = num >= pdfDoc.numPages;
      if (pageNumPending !== null) {{
        renderPage(pageNumPending);
        pageNumPending = null;
      }}
    }});
  }}

  function queueRenderPage(num) {{
    if (pageRendering) {{
      pageNumPending = num;
    }} else {{
      renderPage(num);
    }}
  }}

  prev.addEventListener("click", function() {{
    if (pageNum <= 1) return;
    pageNum--;
    queueRenderPage(pageNum);
  }});
  next.addEventListener("click", function() {{
    if (!pdfDoc || pageNum >= pdfDoc.numPages) return;
    pageNum++;
    queueRenderPage(pageNum);
  }});

  pdfjsLib.getDocument(pdfUrl).promise.then(function(doc) {{
    pdfDoc = doc;
    renderPage(pageNum);
  }}).catch(function() {{
    label.textContent = "Deck load failed";
  }});
}})();
</script>
</body>
</html>"""


def main() -> None:
    OUT_REPO.mkdir(parents=True, exist_ok=True)
    archive_bases: list[Path] = []
    if OUT_ARCHIVE.parent.exists():
        OUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
        archive_bases.append(OUT_ARCHIVE)

    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    for json_path in sorted(SLICE_DIR.glob("*.json")):
        slice_doc = json.loads(json_path.read_text())
        slug = field_val(slice_doc, "slug") or json_path.stem
        if only and slug not in only:
            continue
        deck_src = DECK_DIR / f"{slug}.pdf"
        if not deck_src.is_file():
            print(f"SKIP {slug}: missing {deck_src}", file=sys.stderr)
            continue
        html = build_page(slice_doc)
        for root in (OUT_REPO, *archive_bases):
            base = root / slug
            base.mkdir(parents=True, exist_ok=True)
            (base / "index.html").write_text(html)
            shutil.copy2(deck_src, base / "deck.pdf")
        print(f"Built {slug}")


if __name__ == "__main__":
    main()
