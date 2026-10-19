#!/usr/bin/env python3
"""Build CLP26 slice one-pagers (/s/{slug}) from slice JSON + deck PDF."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data" / "clp26-slices"
OUT_SITES = ROOT / "onepagers" / "sites"
BASE_CSS = ROOT / "onepagers" / "template" / "styles_nexus.css"
SLICE_CSS = ROOT / "onepagers" / "template" / "clp26_slice.css"
HERO_BG = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80"
DECK_BG = "https://images.unsplash.com/photo-1504541331459-5288e5d49ee3?w=1200&q=80"
CTA_BG = "https://images.unsplash.com/photo-1504541331459-5288e5d49ee3?w=1200&q=80"
WIKI_TAXONOMY = "https://wiki.cleantechhub.net/search?term={code}"
NEXUS_BASE = "https://nexus.cleantechhub.net"


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def field_val(blob: dict, key: str) -> str | None:
    node = blob.get(key)
    if not isinstance(node, dict):
        return None
    v = node.get("value")
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    return str(v)


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def pdf_page_count(path: Path) -> int:
    try:
        import pypdf  # type: ignore

        return len(pypdf.PdfReader(str(path)).pages)
    except Exception:
        pass
    try:
        out = subprocess.check_output(
            ["pdfinfo", str(path)], stderr=subprocess.DEVNULL, text=True
        )
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return 1


def meta_item(label_en: str, label_es: str, inner_html: str) -> str:
    return (
        f'<div class="meta-item"><div class="meta-label">{bi(label_en, label_es)}</div>'
        f'<div class="meta-value">{inner_html}</div></div>'
    )


def link_or_empty(url: str | None, text: str | None = None) -> str:
    if not url:
        return '<span class="slot-empty" aria-hidden="true">—</span>'
    label = esc(text or url)
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{label}</a>'


def build_page(data: dict, pages: int) -> str:
    slug = data["slug"]
    name = field_val(data, "name") or slug
    country = field_val(data, "country") or ""
    stage = field_val(data, "stage") or ""
    desc = field_val(data, "short_description_es") or ""
    founder_li = field_val(data, "founder_linkedin")
    website = field_val(data, "website")
    tax_code = field_val(data, "taxonomy_link")
    nexus = field_val(data, "nexus_profile_url")
    youtube = field_val(data, "youtube_pitch_url")

    tax_url = WIKI_TAXONOMY.format(code=esc(tax_code)) if tax_code else None
    one_pager_url = f"{NEXUS_BASE}/s/{slug}"

    hero_sub_en = " · ".join(x for x in [country, stage, "CLP26"] if x)
    hero_sub_es = hero_sub_en

    meta_html = "".join(
        [
            meta_item(
                "Founder LinkedIn",
                "LinkedIn del fundador",
                link_or_empty(founder_li, "LinkedIn"),
            ),
            meta_item("Website", "Sitio web", link_or_empty(website, website)),
            meta_item(
                "CT Taxonomy",
                "Taxonomía CT",
                link_or_empty(tax_url, tax_code) if tax_code else link_or_empty(None),
            ),
            meta_item(
                "Nexus profile",
                "Perfil Nexus",
                link_or_empty(nexus, "Nexus profile"),
            ),
            meta_item(
                "One-pager",
                "One-pager",
                f'<a href="{esc(one_pager_url)}">{esc(one_pager_url)}</a>',
            ),
        ]
    )

    website_cta = ""
    if website:
        website_cta = f'<a class="cta-link" href="{esc(website)}">{bi("Visit website", "Visitar sitio")}</a>'

    youtube_block = ""
    if youtube:
        embed = youtube
        if "watch?v=" in youtube:
            vid = youtube.split("watch?v=")[-1].split("&")[0]
            embed = f"https://www.youtube.com/embed/{vid}"
        youtube_block = f"""
<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{HERO_BG}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">▶</div>
    <div class="sec-title">{bi("Pitch video", "Video pitch")}</div><div class="sec-rule"></div></div>
  <div class="youtube-wrap"><div class="youtube-panel frost-panel">
    <iframe class="youtube-frame" src="{esc(embed)}" title="{esc(name)} pitch" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
  </div></div>
</div>
<div class="accent-bar"></div>
"""

    css = BASE_CSS.read_text() + "\n" + SLICE_CSS.read_text()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(name)} — CleantechHUB Startup Profile</title>
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

<div class="sec hero">
  <img class="hero-img" src="{HERO_BG}" alt="{esc(name)}" loading="lazy">
  <div class="hero-ov"></div>
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);">{bi("CLP26 · National", "CLP26 · Nacional")}</div></div>
  <div class="hero-in">
    <div class="hero-name">{esc(name)}</div>
    <div class="hero-sub">{bi(esc(hero_sub_en), esc(hero_sub_es))}</div>
    <div class="hero-pitch">{esc(desc)}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{HERO_BG}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">◎</div>
    <div class="sec-title">{bi("Profile links", "Enlaces del perfil")}</div><div class="sec-rule"></div></div>
  <div class="meta-wrap"><div class="meta-panel frost-panel"><div class="meta-grid">{meta_html}</div></div></div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{HERO_BG}');"></div>
  <div class="sec-ov" style="background:rgba(102,147,72,.30);"></div>
  <div class="sec-header"><div class="sec-num">✎</div>
    <div class="sec-title">{bi("Short description", "Descripción breve")}</div><div class="sec-rule"></div></div>
  <div class="desc-wrap"><div class="desc-panel frost-panel"><div class="desc-text">{esc(desc)}</div></div></div>
</div>

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{DECK_BG}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="sec-header"><div class="sec-num">📄</div>
    <div class="sec-title">{bi("Pitch deck", "Pitch deck")}</div><div class="sec-rule"></div></div>
  <div class="deck-note">{bi("One slide at a time — use arrows to navigate.", "Una diapositiva a la vez — use las flechas para navegar.")}</div>
  <div class="deck-wrap"><div class="deck-panel frost-panel">
    <div class="deck-frame-wrap">
      <iframe class="deck-frame-single" id="deck-frame" title="{esc(name)} pitch deck" src="/s/{slug}/deck.pdf#page=1&view=FitH&toolbar=0"></iframe>
    </div>
    <div class="deck-nav">
      <button type="button" class="deck-nav-btn" id="deck-prev" aria-label="Previous slide">{bi("← Previous", "← Anterior")}</button>
      <div class="deck-nav-status" id="deck-status">{bi("Slide 1", "Diapositiva 1")}</div>
      <button type="button" class="deck-nav-btn" id="deck-next" aria-label="Next slide">{bi("Next →", "Siguiente →")}</button>
    </div>
    <div class="deck-fallback">{bi("Deck not loading?", "¿No carga el deck?")} <a href="/s/{slug}/deck.pdf" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a></div>
  </div>
  <div class="deck-actions">
    <a class="cta-link" href="/s/{slug}/deck.pdf" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a>
    <a class="cta-link" href="/s/{slug}/deck.pdf" download>{bi("Download PDF", "Descargar PDF")}</a>
  </div></div>
</div>
<div class="accent-bar"></div>
{youtube_block}

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{CTA_BG}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="cta">
    <div class="cta-name">{esc(name)}</div>
    <div class="cta-pitch">{esc(desc)}</div>
    <div class="cta-links">
      {website_cta}
      <a class="cta-link" href="{esc(one_pager_url)}">{bi("One-pager", "One-pager")}</a>
      <a class="cta-link" href="/s/{slug}/deck.pdf" target="_blank" rel="noopener">{bi("Pitch deck (PDF)", "Pitch deck (PDF)")}</a>
      <a class="cta-link" href="https://nexus.cleantechhub.net/p/startup-portfolio">{bi("157 Startups", "157 Startups")}</a>
    </div>
    <div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div>
    <div class="cta-port">{bi("Draft preview — not deployed to /opt/nexus-onepagers", "Vista previa borrador — no desplegado en /opt/nexus-onepagers")}</div>
  </div>
</div>
<div class="accent-bar"></div>
<script>
(function() {{
  var page = 1;
  var maxPage = {pages};
  var frame = document.getElementById('deck-frame');
  var status = document.getElementById('deck-status');
  var prev = document.getElementById('deck-prev');
  var next = document.getElementById('deck-next');
  var pdfBase = '/s/{slug}/deck.pdf';
  function label() {{
    var en = document.documentElement.lang === 'es' ? 'Diapositiva ' + page : 'Slide ' + page;
    status.textContent = en + (maxPage > 1 ? ' / ' + maxPage : '');
  }}
  function go() {{
    frame.src = pdfBase + '#page=' + page + '&view=FitH&toolbar=0';
    prev.disabled = page <= 1;
    next.disabled = page >= maxPage;
    label();
  }}
  prev.addEventListener('click', function() {{ if (page > 1) {{ page--; go(); }} }});
  next.addEventListener('click', function() {{ if (page < maxPage) {{ page++; go(); }} }});
  go();
}})();
</script>
</body>
</html>"""


def main(argv: list[str]) -> None:
    slugs = argv[1:] if len(argv) > 1 else None
    try:
        import pypdf  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "pypdf"], stderr=subprocess.DEVNULL
        )

    for json_path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(json_path.read_text())
        slug = data.get("slug") or json_path.stem
        if slugs and slug not in slugs:
            continue
        out_dir = OUT_SITES / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        deck_src = ROOT / "onepagers" / "decks" / f"{slug}.pdf"
        if not deck_src.is_file():
            raise SystemExit(f"Missing deck PDF: {deck_src}")
        shutil.copy2(deck_src, out_dir / "deck.pdf")
        pages = pdf_page_count(out_dir / "deck.pdf")
        html = build_page(data, pages)
        (out_dir / "index.html").write_text(html)
        print(f"Built {slug} ({pages} deck pages)")


if __name__ == "__main__":
    main(sys.argv)
