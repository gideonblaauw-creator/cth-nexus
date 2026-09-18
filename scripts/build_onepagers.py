#!/usr/bin/env python3
"""Build Nexus startup one-pagers from JSON data + shared template."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data"
TEMPLATE_CSS = ROOT / "onepagers" / "template" / "styles.css"
OUT_REPO = ROOT / "onepagers" / "sites"
OUT_MEDIA = ROOT / "onepagers" / "media"
OUT_ARCHIVE = Path("/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20")
DECK_SOURCE = Path("/opt/claude-files/Projects/Nexus/startup-decks-2026-08-20")


def asset_url(path: str, slug: str) -> str:
    """Resolve ./assets/... to /s/{slug}/assets/... (works without trailing slash)."""
    if not path or path.startswith(("http://", "https://", "/")):
        return path
    rel = path.removeprefix("./")
    return f"/s/{slug}/{rel}"


def bi(en: str, es: str) -> str:
    return f'<span class="en">{en}</span><span class="es">{es}</span>'


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


def deck_section(d: dict, slug: str) -> str:
    deck = d.get("deck_pdf")
    if not deck:
        return ""
    local_pdf = deck.get("pdf_path") or f"/s/{slug}/deck.pdf"
    bg = asset_url(deck.get("bg", "./assets/bg-deck.jpg"), slug)
    iframe = (
        f'<div class="deck-frame-wrap">'
        f'<embed class="deck-frame" src="{local_pdf}#view=FitH&toolbar=1" '
        f'type="application/pdf" title="{d["name"]} pitch deck">'
        f"</div>"
    )
    fallback = (
        f'<div class="deck-fallback">{bi("Deck not loading?", "¿No carga el deck?")} '
        f'<a href="{local_pdf}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a></div>'
    )
    return (
        f'<div class="sec" style="position:relative;">'
        f'<div class="sec-bg" style="background-image:url(\'{bg}\');"></div>'
        f'<div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>'
        f'<div class="sec-header"><div class="sec-num">📄</div>'
        f'<div class="sec-title">{bi("Pitch Deck", "Pitch Deck")}</div><div class="sec-rule"></div></div>'
        f'<div class="deck-note">{bi("Full-size deck preview below. Numbers on this profile match the deck only.", "Vista previa del deck a tamaño completo. Los números en este perfil provienen solo del deck.")}</div>'
        f'<div class="deck-wrap"><div class="deck-panel">{iframe}{fallback}</div>'
        f'<div class="deck-actions">'
        f'<a class="cta-link" href="{local_pdf}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a>'
        f'<a class="cta-link" href="{local_pdf}" target="_blank" rel="noopener">{bi("Download PDF", "Descargar PDF")}</a>'
        f"</div></div></div><div class=\"accent-bar\"></div>"
    )



def build_page(d: dict) -> str:
    css = TEMPLATE_CSS.read_text()
    slug = d["slug"]
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
    if deck:
        local_pdf = deck.get("pdf_path") or f"/s/{slug}/deck.pdf"
        deck_link = f'<a class="cta-link" href="{local_pdf}" target="_blank" rel="noopener">{bi("Pitch deck (PDF)", "Pitch deck (PDF)")}</a>'

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
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);coor:var(--lg);">{bi(d["badge_en"], d["badge_es"])}</div></div>
  <div class="hero-in">
    <div class="hero-name">{d["name"]}</div>
    <div class="hero-sub">{bi(d["hero_sub_en"], d["hero_sub_es"])}</div>
    <div class="hero-pitch">{bi(d["pitch_en"], d["pitch_es"])}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>

<div class="ribbon" style="background:rgba(12,73,138,.95);":{ribbon}</div>

{deck_section(d, slug)}

sections_html}

<div class="sec" style="position:relative;">
  <div class="sec-bg" style="background-image:url('{asset_url("./assets/bg-cta.jpg", slug)}');"></div>
  <div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>
  <div class="cta">
    <div class="pill" style="background:rgba(157,195,132,.12);border:1px solid rgba(157,195,132,.2);color:var(--lg);margin-bottom:16px;">{bi(d["badge_en"], d["badge_es"])}</div>
    <div class="cta-name">{d["name"]}</div>
    <div class="cta-pitch">{bi(�["cta_pitch_en"], d["cta_pitch_es"])}</div>
    <a class="cta-btn" href="{d.get("website","#")}>{bi(d.get("cta_btn_en","Visit website"), d.get("cta_btn_es","Visitar sitio"))}</a>
    <div class="cta-links">
      <a class="cta-link" href="https://nexus.cleantechhub.net/s/{slug}">{bi(�Nexus Profile", "Perfil Nexus")}</a>
      <a class="cta-link" href="https://nexus.cleantechhub.net/p/startup-portfolio">{bi(�157 Startups", "157 Startups")}</a>
      {deck_link}
    </div>
    <div class="cta-brand"><div class="tg">Inspira. Actúa. Transforma.</div><div class="lg2">Cleantech<em style="color:var(--lg);font-style:normal;">HUB</em></div></div>
    <div class="cta-port">{bi(�CleantechHUB portfolio profile · Latin America", "Perfil portafolio CleantechHUB · América Latina")}</div>
  </div>
</div>
<div class="accent-bar"></div>
</body>
</html>"""


def main() -> None:
    OUT_REPO.mkdir(parents=True, exist_ok=T�ue)
    OUT_ARCHIVE.mkdir(parents=True, exist_ok=T�ue)
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    for json_path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(json_path.read_text())
        slug = data["slug"]
        if only and slug not in only:
            continue
        html = build_page(data)
        pdf_src_name = (data.get("deck_pdf") or {}).get("source_file")
        media_src = OUT_MEDIA / slug
        for base in (OUT_REPO / slug, OUT_ARCHIVE / slug):
            base.mkdir(parents=True, exist_ok=True)
            (base / "index.html").write_text(html)
            if media_src.is_dir():
                dest_assets = base / "assets"
                if dest_assets.exists():
                    shutil.rmtree(dest_assets)
                shutil.copytree(media_src, dest_assets, dirs_exist_ok=False)
            if pdf_src_name:
                src_pdf = DECK_SOURCE / pdf_src_name
                if src_pdf.is_file():
                    shutil.copy2(src_pdf, base / "deck.pdf")
        print(f"Built {slug}")


if __name__ == "__main__":
    main()
