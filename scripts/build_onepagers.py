#!/usr/bin/env python3
"""Build Nexus startup one-pagers from JSON data + shared template."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data"
SLICE_DIR = DATA_DIR / "slices"
LOCAL_DECKS = ROOT / "onepagers" / "decks"
TEMPLATE_CSS = ROOT / "onepagers" / "template" / "styles.css"
OUT_REPO = ROOT / "onepagers" / "sites"
OUT_MEDIA = ROOT / "onepagers" / "media"
OUT_ARCHIVE = Path("/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20")
DECK_SOURCE = Path("/opt/claude-files/Projects/Nexus/startup-decks-2026-08-20")
SKIP_SLUGS = frozenset({"curuba"})
EMPTY_SLOT = "[PENDIENTE]"


def asset_url(path: str, slug: str) -> str:
    """Resolve ./assets/... to /s/{slug}/assets/... (works without trailing slash)."""
    if not path or path.startswith(("http://", "https://", "/")):
        return path
    rel = path.removeprefix("./")
    return f"/s/{slug}/{rel}"


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


def slice_field(slice_data: dict | None, key: str) -> str | None:
    if not slice_data or key not in slice_data:
        return None
    entry = slice_data[key]
    if isinstance(entry, dict):
        val = entry.get("value")
        if val is None or val == "":
            return None
        return str(val)
    if entry in (None, ""):
        return None
    return str(entry)


def load_slice(slug: str) -> dict | None:
    path = SLICE_DIR / f"{slug}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def apply_slice(d: dict, slice_data: dict | None) -> dict:
    if not slice_data:
        return d
    out = dict(d)
    name = slice_field(slice_data, "name")
    if name:
        out["name"] = name
    if "website" in slice_data:
        site = slice_field(slice_data, "website")
        out["website"] = site or ""
    out["slice"] = slice_data
    return out


def slot_link(url: str | None, label: str) -> str:
    if url:
        return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
    return f'<span class="slot-empty">{EMPTY_SLOT}</span>'


def taxonomy_link_html(slice_data: dict | None) -> str:
    url = slice_field(slice_data, "taxonomy_link")
    if url:
        return slot_link(url, url)
    code = slice_field(slice_data, "taxonomy_code")
    if code:
        wiki = f"https://wiki.cleantechhub.net/search?term={code}"
        return slot_link(wiki, code)
    return f'<span class="slot-empty">{EMPTY_SLOT}</span>'


def profile_meta_section(d: dict, slug: str) -> str:
    slice_data = d.get("slice")
    if not slice_data:
        return ""
    short_es = slice_field(slice_data, "short_description_es") or ""
    short_en = slice_field(slice_data, "short_description_en") or ""
    founder = slice_field(slice_data, "founder_linkedin")
    website = slice_field(slice_data, "website")
    nexus = slice_field(slice_data, "nexus_profile_url") or f"https://nexus.cleantechhub.net/s/{slug}"
    one_pager = slice_field(slice_data, "one_pager_url")
    bg = asset_url(d.get("hero_image", "./assets/bg-problem.jpg"), slug)
    short_block = ""
    if short_es or short_en:
        short_block = (
            f'<div class="profile-short">'
            f'<div class="profile-short-label">{bi("Short description", "Descripción corta")}</div>'
            f'<p class="profile-short-text">{bi(short_en or EMPTY_SLOT, short_es or EMPTY_SLOT)}</p>'
            f"</div>"
        )
    return (
        f'<div class="sec profile-meta-sec" style="position:relative;">'
        f'<div class="sec-bg" style="background-image:url(\'{bg}\');"></div>'
        f'<div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>'
        f'<div class="profile-meta-wrap">'
        f'<div class="profile-meta frost-panel">'
        f'<div class="profile-meta-title">{d["name"]}</div>'
        f'<dl class="profile-meta-grid">'
        f'<div class="profile-meta-row"><dt>{bi("Founder LinkedIn", "LinkedIn fundador(a)")}</dt>'
        f"<dd>{slot_link(founder, 'LinkedIn') if founder else f'<span class=\"slot-empty\">{EMPTY_SLOT}</span>'}</dd></div>"
        f'<div class="profile-meta-row"><dt>{bi("Website", "Sitio web")}</dt>'
        f"<dd>{slot_link(website, website) if website else f'<span class=\"slot-empty\">{EMPTY_SLOT}</span>'}</dd></div>"
        f'<div class="profile-meta-row"><dt>{bi("CT taxonomy", "Taxonomía CT")}</dt><dd>{taxonomy_link_html(slice_data)}</dd></div>'
        f'<div class="profile-meta-row"><dt>{bi("Nexus profile", "Perfil Nexus")}</dt>'
        f'<dd>{slot_link(nexus, nexus)}</dd></div>'
        f'<div class="profile-meta-row"><dt>{bi("One-pager", "One-pager")}</dt>'
        f"<dd>{slot_link(one_pager, one_pager) if one_pager else f'<span class=\"slot-empty\">{EMPTY_SLOT}</span>'}</dd></div>"
        f"</dl>{short_block}</div></div></div><div class=\"accent-bar\"></div>"
    )


def youtube_section(d: dict, slug: str) -> str:
    slice_data = d.get("slice")
    url = slice_field(slice_data, "youtube_pitch_url") if slice_data else None
    if not url:
        return ""
    bg = asset_url("./assets/bg-deck.jpg", slug)
    vid = url
    if "youtube.com/watch" in url:
        vid = url.split("v=")[-1].split("&")[0]
        embed = f"https://www.youtube.com/embed/{vid}"
    elif "youtu.be/" in url:
        vid = url.rstrip("/").split("/")[-1]
        embed = f"https://www.youtube.com/embed/{vid}"
    else:
        embed = url
    return (
        f'<div class="sec" style="position:relative;">'
        f'<div class="sec-bg" style="background-image:url(\'{bg}\');"></div>'
        f'<div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>'
        f'<div class="sec-header"><div class="sec-num">▶</div>'
        f'<div class="sec-title">{bi("Pitch video", "Video pitch")}</div><div class="sec-rule"></div></div>'
        f'<div class="youtube-wrap"><div class="youtube-panel frost-panel">'
        f'<iframe class="youtube-frame" src="{embed}" title="{d["name"]} pitch" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
        f'allowfullscreen loading="lazy"></iframe></div></div></div><div class="accent-bar"></div>'
    )


DECK_SLIDE_JS = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script>
(function(){
  var wrap=document.querySelector('.deck-slide-viewer');
  if(!wrap||!window.pdfjsLib)return;
  pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  var pdfUrl=wrap.getAttribute('data-pdf');
  var canvas=wrap.querySelector('canvas');
  var ctx=canvas.getContext('2d');
  var pageNum=1,pdfDoc=null,pageCount=0;
  var out=wrap.querySelector('.deck-page-out');
  var btnP=wrap.querySelector('.deck-prev');
  var btnN=wrap.querySelector('.deck-next');
  function render(){
    pdfDoc.getPage(pageNum).then(function(page){
      var vp=page.getViewport({scale:1.35});
      canvas.height=vp.height;canvas.width=vp.width;
      page.render({canvasContext:ctx,viewport:vp});
      if(out)out.textContent=pageNum+' / '+pageCount;
      if(btnP)btnP.disabled=pageNum<=1;
      if(btnN)btnN.disabled=pageNum>=pageCount;
    });
  }
  pdfjsLib.getDocument(pdfUrl).promise.then(function(pdf){
    pdfDoc=pdf;pageCount=pdf.numPages;render();
  });
  if(btnP)btnP.addEventListener('click',function(){if(pageNum>1){pageNum--;render();}});
  if(btnN)btnN.addEventListener('click',function(){if(pageNum<pageCount){pageNum++;render();}});
})();
</script>
"""


def bar_chart(cols: list[dict], max_h: int = 90) -> str:
    vals = [c.get("height", 30) for c in cols]
    mx = max(vals) if vals else 1
    parts = ['<div class="rev-chart">']
    for c in cols:
        h = max(4, int(c.get("height", 30) * max_h / mx))
        cls = "proj" if c.get("proj") else "actual"
        parts.append(
            f'<div class="rev-col"><div class="rev-val">{c["val"]}</div>'
            f'<div class="rev-bar {cls}" style="height:{h}px;"></div>'
            f'<div class="rev-label">{c["label"]}</div></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def mini_chart(cols: list[dict]) -> str:
    mx = max(c["pct"] for c in cols) or 1
    parts = ['<div class="mini-chart">']
    for c in cols:
        h = max(8, int(c["pct"] * 42 / mx))
        hl = " hl" if c.get("hl") else ""
        parts.append(
            f'<div class="mini-col"><div class="mini-val{hl}">{c["val"]}</div>'
            f'<div class="mini-bar{hl}" style="height:{h}px;"></div>'
            f'<div class="mini-lab">{bi(c["lab_en"], c["lab_es"])}</div></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def table(headers: list[tuple[str, str]], rows: list[list[tuple[str, str]]]) -> str:
    th = "".join(f"<th>{bi(a, b)}</th>" for a, b in headers)
    body = ""
    for row in rows:
        tds = []
        for i, (a, b) in enumerate(row):
            cls = ' class="hl"' if i == len(row) - 1 else ""
            tds.append(f"<td{cls}>{bi(a, b)}</td>")
        body += f"<tr>{''.join(tds)}</tr>"
    return f'<div class="comp-wrap"><table class="comp-tbl"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def sliders(items: list[dict]) -> str:
    parts = ['<div class="slider-wrap">']
    for i, s in enumerate(items):
        sid = f"sl{i}"
        val = s.get("default", s["min"])
        disabled = s["min"] == s["max"]
        dis = " disabled" if disabled else ""
        parts.append(
            f'<div class="slider-item">'
            f'<div class="sl-label">{bi(s["label_en"], s["label_es"])}</div>'
            f'<div class="sl-val" id="{sid}-out">{s["prefix"]}{val}{s["suffix"]}</div>'
            f'<input class="sl-range" type="range" id="{sid}" min="{s["min"]}" max="{s["max"]}" step="{s.get("step",1)}" value="{val}"{dis} '
            f'data-prefix="{s["prefix"]}" data-suffix="{s["suffix"]}" oninput="document.getElementById(\'{sid}-out\').textContent=this.dataset.prefix+this.value+this.dataset.suffix">'
            f'<div class="sl-hint">{bi(s["hint_en"], s["hint_es"])}</div></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def sol_grid(steps: list[dict]) -> str:
    cards = []
    for n, s in enumerate(steps, 1):
        cards.append(
            f'<div class="sol-card"><div class="sol-step">{n}</div>'
            f'<div class="sol-icon">{s.get("icon","●")}</div>'
            f'<div class="sol-label">{bi(s["label_en"], s["label_es"])}</div>'
            f'<div class="sol-text">{bi(s["text_en"], s["text_es"])}</div></div>'
        )
    return f'<div class="sol-grid">{"".join(cards)}</div>'


def impact_grid(cards: list[dict]) -> str:
    items = []
    for c in cards:
        items.append(
            f'<div class="imp-card"><div class="imp-icon">{c.get("icon","●")}</div>'
            f'<div><div class="imp-title">{bi(c["title_en"], c["title_es"])}</div>'
            f'<div class="imp-text">{bi(c["text_en"], c["text_es"])}</div></div></div>'
        )
    return f'<div class="impact-grid">{"".join(items)}</div>'


def team_grid(members: list[dict], slug: str) -> str:
    cards = []
    for m in members:
        if m.get("photo"):
            photo = asset_url(m["photo"], slug)
            avatar = (
                f'<img class="tp-photo" src="{photo}" alt="{m["name"]}" loading="lazy">'
            )
        else:
            ini = m.get("initials") or "".join(w[0] for w in m["name"].split()[:2]).upper()
            avatar = (
                f'<div class="tp-avatar" style="background:linear-gradient(135deg,var(--fo),var(--lg));">{ini}</div>'
            )
        link = ""
        if m.get("linkedin"):
            link = (
                f'<a class="tp-link" href="{m["linkedin"]}" target="_blank" rel="noopener">LinkedIn</a>'
            )
        cards.append(
            f'<div class="team-card">{avatar}'
            f'<div class="tp-name">{m["name"]}</div>'
            f'<div class="tp-role">{bi(m["role_en"], m["role_es"])}</div>'
            f'<div class="tp-bio">{bi(m.get("bio_en",""), m.get("bio_es",""))}</div>{link}</div>'
        )
    return f'<div class="team-grid">{"".join(cards)}</div>'


def deck_section(d: dict, slug: str, has_local_deck: bool) -> str:
    deck = d.get("deck_pdf") or {}
    local_pdf = deck.get("pdf_path") or f"/s/{slug}/deck.pdf"
    if not has_local_deck and not deck.get("drive_id") and not deck.get("embed_url"):
        return ""
    bg = asset_url(deck.get("bg", "./assets/bg-deck.jpg"), slug)
    if has_local_deck:
        viewer = (
            f'<div class="deck-slide-viewer" data-pdf="{local_pdf}">'
            f'<div class="deck-slide-canvas-wrap"><canvas></canvas></div>'
            f'<div class="deck-slide-nav">'
            f'<button type="button" class="deck-nav-btn deck-prev" aria-label="Previous slide">‹</button>'
            f'<span class="deck-page-out">1 / ?</span>'
            f'<button type="button" class="deck-nav-btn deck-next" aria-label="Next slide">›</button>'
            f"</div></div>"
        )
        note = bi(
            "One slide at a time — use arrows to browse the deck.",
            "Una diapositiva a la vez — use las flechas para recorrer el deck.",
        )
        fallback = (
            f'<div class="deck-fallback">{bi("Deck not loading?", "¿No carga el deck?")} '
            f'<a href="{local_pdf}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a></div>'
        )
        body = f'<div class="deck-wrap"><div class="deck-panel">{viewer}{fallback}</div>'
        actions = (
            f'<div class="deck-actions">'
            f'<a class="cta-link" href="{local_pdf}" target="_blank" rel="noopener">'
            f'{bi("Download PDF", "Descargar PDF")}</a></div>'
        )
        extra_js = DECK_SLIDE_JS
    else:
        drive_id = deck.get("drive_id")
        view = deck.get("view_url") or (f"https://drive.google.com/file/d/{drive_id}/view" if drive_id else "")
        embed = deck.get("embed_url") or (
            f"https://drive.google.com/file/d/{drive_id}/preview" if drive_id else ""
        )
        iframe = (
            f'<div class="deck-frame-wrap">'
            f'<iframe class="deck-frame" src="{embed}" title="{d["name"]} pitch deck" '
            f'loading="lazy" allow="autoplay" referrerpolicy="no-referrer-when-downgrade"></iframe>'
            f"</div>"
        )
        note = bi(
            "Full-size deck preview below. Numbers on this profile match the deck only.",
            "Vista previa del deck a tamaño completo. Los números en este perfil provienen solo del deck.",
        )
        body = f'<div class="deck-wrap"><div class="deck-panel">{iframe}</div>'
        actions = (
            f'<div class="deck-actions">'
            f'<a class="cta-link" href="{view}" target="_blank" rel="noopener">'
            f'{bi("Open deck in Google Drive", "Abrir deck en Google Drive")}</a>'
            f'<a class="cta-link" href="{local_pdf}" target="_blank" rel="noopener">'
            f'{bi("Download PDF", "Descargar PDF")}</a></div>'
        )
        extra_js = ""
    return (
        f'<div class="sec" style="position:relative;">'
        f'<div class="sec-bg" style="background-image:url(\'{bg}\');"></div>'
        f'<div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>'
        f'<div class="sec-header"><div class="sec-num">📄</div>'
        f'<div class="sec-title">{bi("Pitch Deck", "Pitch Deck")}</div><div class="sec-rule"></div></div>'
        f'<div class="deck-note">{note}</div>'
        f"{body}{actions}</div></div><div class=\"accent-bar\"></div>{extra_js}"
    )



def build_page(d: dict, has_local_deck: bool = False) -> str:
    css = TEMPLATE_CSS.read_text()
    slug = d["slug"]
    website = d.get("website") or ""
    website_btn = ""
    if website and website not in ("#", ""):
        website_btn = (
            f'<a class="cta-btn" href="{website}">'
            f'{bi(d.get("cta_btn_en", "Visit website"), d.get("cta_btn_es", "Visitar sitio"))}</a>'
        )
    ribbon = "".join(
        f'<div class="ribbon-cell"><div class="rc-val">{k["val"]}</div>'
        f'<div class="rc-lab">{bi(k["lab_en"], k["lab_es"])}</div>'
        f'<div class="rc-sub">{bi(k.get("sub_en",""), k.get("sub_es",""))}</div></div>'
        for k in d["ribbon"]
    )

    stats = ""
    if d.get("problem_stats"):
        rows = []
        for idx, row in enumerate(d["problem_stats"]):
            style = ' style="margin-top:0;"' if idx == 0 else ""
            rows.append(
                f'<div class="stat-row"{style}>'
                + "".join(
                    f'<div class="stat-card"><div class="sc-num">{s["num"]}</div>'
                    f'<div class="sc-lab">{bi(s["lab_en"], s["lab_es"])}</div></div>'
                    for s in row
                )
                + "</div>"
            )
        stats = "".join(rows)

    sections_html = ""
    for sec in d["sections"]:
        num = sec["num"]
        title_en, title_es = sec["title_en"], sec["title_es"]
        ov = sec.get("overlay", "rgba(12,73,138,.30)")
        bg = asset_url(sec.get("bg", "./assets/bg-problem.jpg"), slug)
        inner = ""
        if sec["type"] == "split":
            inner = (
                f'<div class="split" style="position:relative;z-index:2;">'
                f'<div class="split-panel"><div class="split-frost">'
                f'<div class="split-h">{bi(sec["head_en"], sec["head_es"])}</div>'
                f'<div class="body-text">{bi(sec["body_en"], sec["body_es"])}</div></div></div>'
                f'<div class="split-panel"><div class="split-frost split-frost-stats">'
                f'{stats}{sec.get("extra_html","")}</div></div></div>'
            )
        elif sec["type"] == "solution":
            inner = sol_grid(sec["steps"])
        elif sec["type"] == "chart":
            inner = bar_chart(sec["bars"])
            if sec.get("note_en"):
                inner += f'<div class="frost-note">{bi(sec["note_en"], sec["note_es"])}</div>'
        elif sec["type"] == "table":
            inner = table(sec["headers"], sec["rows"])
        elif sec["type"] == "sliders":
            inner = sliders(sec["sliders"])
        elif sec["type"] == "impact":
            inner = impact_grid(sec["cards"])
            if sec.get("table"):
                t = sec["table"]
                inner += table(t["headers"], t["rows"])
        elif sec["type"] == "team":
            inner = team_grid(sec["members"], slug)
            if sec.get("dream_en"):
                inner += f'<div class="frost-note">{bi(sec["dream_en"], sec["dream_es"])}</div>'
        elif sec["type"] == "html":
            inner = sec["html"]

        sections_html += (
            f'<div class="sec" style="position:relative;">'
            f'<div class="sec-bg" style="background-image:url(\'{bg}\');"></div>'
            f'<div class="sec-ov" style="background:{ov};"></div>'
            f'<div class="sec-header"><div class="sec-num">{num:02d}</div>'
            f'<div class="sec-title">{bi(title_en, title_es)}</div><div class="sec-rule"></div></div>'
            f'{inner}</div>'
        )
        if sec.get("accent_after"):
            sections_html += '<div class="accent-bar"></div>'

    deck = d.get("deck_pdf") or {}
    deck_link = ""
    local_pdf = f"/s/{slug}/deck.pdf"
    if has_local_deck:
        deck_link = (
            f'<a class="cta-link" href="{local_pdf}" target="_blank" rel="noopener">'
            f'{bi("Pitch deck (PDF)", "Pitch deck (PDF)")}</a>'
        )
    elif deck.get("view_url") or deck.get("drive_id"):
        view = deck.get("view_url") or f"https://drive.google.com/file/d/{deck['drive_id']}/view"
        deck_link = (
            f'<a class="cta-link" href="{view}" target="_blank" rel="noopener">'
            f'{bi("Pitch deck (PDF)", "Pitch deck (PDF)")}</a>'
        )

    profile_meta = profile_meta_section(d, slug)
    youtube = youtube_section(d, slug)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{d["name"]} — CleantechHUB Startup Profile</title>
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
  <img class="hero-img" src="{asset_url(d["hero_image"], slug)}" alt="{d["name"]}" loading="lazy">
  <div class="hero-ov"></div>
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);">{bi(d["badge_en"], d["badge_es"])}</div></div>
  <div class="hero-in">
    <div class="hero-name">{d["name"]}</div>
    <div class="hero-sub">{bi(d["hero_sub_en"], d["hero_sub_es"])}</div>
    <div class="hero-pitch">{bi(d["pitch_en"], d["pitch_es"])}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>

<div class="ribbon" style="background:rgba(12,73,138,.95);">{ribbon}</div>

{profile_meta}

{youtube}

{deck_section(d, slug, has_local_deck)}

{sections_html}

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{asset_url("./assets/bg-cta.jpg", slug)}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="cta">
    <div class="pill" style="background:rgba(157,195,132,.12);border:1px solid rgba(157,195,132,.2);color:var(--lg);margin-bottom:16px;">{bi(d["badge_en"], d["badge_es"])}</div>
    <div class="cta-name">{d["name"]}</div>
    <div class="cta-pitch">{bi(d["cta_pitch_en"], d["cta_pitch_es"])}</div>
    {website_btn}
    <div class="cta-links">
      <a class="cta-link" href="https://nexus.cleantechhub.net/s/{slug}">{bi("Nexus Profile", "Perfil Nexus")}</a>
      <a class="cta-link" href="https://nexus.cleantechhub.net/p/startup-portfolio">{bi("157 Startups", "157 Startups")}</a>
      {deck_link}
    </div>
    <div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div>
    <div class="cta-port">{bi("CleantechHUB portfolio profile · Latin America", "Perfil portafolio CleantechHUB · América Latina")}</div>
  </div>
</div>
<div class="accent-bar"></div>
</body>
</html>"""


def output_bases() -> list[Path]:
    bases = [OUT_REPO]
    if OUT_ARCHIVE.is_dir():
        bases.append(OUT_ARCHIVE)
    else:
        try:
            OUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
            bases.append(OUT_ARCHIVE)
        except (OSError, PermissionError):
            pass
    return bases


def main() -> None:
    OUT_REPO.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    for json_path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(json_path.read_text())
        slug = data["slug"]
        if slug in SKIP_SLUGS:
            continue
        if only and slug not in only:
            continue
        slice_data = load_slice(slug)
        data = apply_slice(data, slice_data)
        local_deck = LOCAL_DECKS / f"{slug}.pdf"
        has_local_deck = local_deck.is_file()
        html = build_page(data, has_local_deck=has_local_deck)
        pdf_src_name = (data.get("deck_pdf") or {}).get("source_file")
        media_src = OUT_MEDIA / slug
        for base in [b / slug for b in output_bases()]:
            base.mkdir(parents=True, exist_ok=True)
            (base / "index.html").write_text(html)
            if media_src.is_dir():
                dest_assets = base / "assets"
                if dest_assets.exists():
                    shutil.rmtree(dest_assets)
                shutil.copytree(media_src, dest_assets, dirs_exist_ok=False)
            if has_local_deck:
                shutil.copy2(local_deck, base / "deck.pdf")
            elif pdf_src_name:
                src_pdf = DECK_SOURCE / pdf_src_name
                if src_pdf.is_file():
                    shutil.copy2(src_pdf, base / "deck.pdf")
        print(f"Built {slug}")


if __name__ == "__main__":
    main()
