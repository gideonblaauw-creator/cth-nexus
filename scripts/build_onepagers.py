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
            f'<div class="sol-icon">{s.get("icon","â—")}</div>'
            f'<div class="sol-label">{bi(s["label_en"], s["label_es"])}</div>'
            f'<div class="sol-text">{bi(s["text_en"], s["text_es"])}</div></div>'
        )
    return f'<div class="sol-grid">{"".join(cards)}</div>'


def impact_grid(cards: list[dict]) -> str:
    items = []
    for c in cards:
        items.append(
            f'<div class="imp-card"><div class="imp-icon">{c.get("icon","â—")}</div>'
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
    drive_id = deck.get("drive_id")
    view = deck.get("view_url") or (f"https://drive.google.com/file/d/{drive_id}/view" if drive_id else "")
    embed = deck.get("embed_url") or (
        f"https://drive.google.com/file/d/{drive_id}/preview" if drive_id else ""
    )
    local_pdf = deck.get("pdf_path") or f"/s/{slug}/deck.pdf"
    bg = asset_url(deck.get("bg", "./assets/bg-deck.jpg"), slug)
    iframe = ""
    if local_pdf:
        iframe = (
            f'<div class="deck-frame-wrap">'
            f'<embed class="deck-frame" src="{local_pdf}#view=FitH&toolbar=1" '
            f'type="application/pdf" title="{d["name"]} pitch deck">'
            f"</div>"
        )
    elif embed:
        iframe = (
            f'<div class="deck-frame-wrap">'
            f'<iframe class="deck-frame" src="{embed}" title="{d["name"]} pitch deck" '
            f)loading="lazy" allow="autoplay" referrerpolicy="no-referrer-when-downgrade"></iframe>'
            f"</div>"
        )
    fallback = (
        f'<div class="deck-fallback">{bi("Deck not loading?", "Â¿No carga el deck?")} '
        f'<a href="{local_pdf}" target="_blank" rel="noopener">{bi("Open PDF", "Abrir PDF")}</a> Â· '
        f'<a href="{view}" target="_blank" rel="noopener">{bi("Google Drive", "Google Drive")}</a></div>'
    )
    return (
        f'<div class="sec" style="position:relative;">'
        f'<div class="sec-bg" style="background-image:url(\'{bg}\');"></div>'
        f'<div class="sec-ov" style="background:rgba(12,73,138,.30);"></div>'
        f'<div class="sec-header"><div class="sec-num">ğŸ“„</div>'
        f'<div class="sec-title">{bi("Pitch Deck", "Pitch Deck")}</div><div class="sec-rule"></div></div>'
        f'<div class="deck-note">{bi(‰Õ±°µÍ¥é”‘•¬ÁÉ•Ù¥•Ü‰•±½Ü¸9Õµ‰•ÉÃ on this profile match the deck only.", "Vista previa del deck a tamaÃ±o completo. Los nÃºmeros en este perfil provienen solo del deck.")}</div>'
        f'<div class="deck-wrap"><div class="deck-panel">{iframe}{fallback}</div>'
        f'<div class="deck-actions">'
        f'<a class="cta-link" href="{view}" target="_blank" rel="noopener">{bi("Open deck in Google Drive", "Abrir deck en Google Drive")}</a>'
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
                eø­íÍÑ…ÑÍõíÍ•Œ¹•Ğ ‰•áÑÉ…}¡Ñµ°ˆ°ˆˆ¥ôğ½‘¥Øøğ½‘¥Øøğ½‘¥Øøœ(€€€€€€€€€€€€¤(€€€€€€€•±¥˜Í•l‰ÑåÁ”‰t€ôô€‰Í½±ÕÑ¥½¸ˆè(€€€€€€€€€€€¥¹¹•È€ôÍ½±}É¥¡Í•l‰ÍÑ•ÁÌ‰t¤(€€€€€€€•±¥˜Í•l‰ÑåÁ”‰t€ôô€‰¡…ÉĞˆè(€€€€€€€€€€€¥¹¹•È€ô‰…É}¡…ÉĞ¡Í•l‰‰…ÉÌ‰t¤(€€€€€€€€€€€¥˜Í•Œ¹•Ğ ‰¹½Ñ•}•¸ˆ¤è(€€€€€€€€€€€€€€€¥¹¹•È€¬ô˜œñ‘¥Ø±…ÍÌô‰™É½ÍĞµ¹½Ñ”ˆùí‰¤¡Í•l‰¹½Ñ•}•¸‰t°Í•l‰¹½Ñ•}•Ì‰t¥ôğ½‘¥Øøœ(€€€€€€€•±¥˜Í•l‰ÑåÁ”‰t€ôô€‰Ñ…‰±”ˆè(€€€€€€€€€€€¥¹¹•È€ôÑ…‰±”¡Í•l‰¡•…‘•ÉÌ‰t°Í•l‰É½İÌ‰t¤(€€€€€€€•±¥˜Í•l‰ÑåÁ”‰t€ôô€‰Í±¥‘•ÉÌˆè(€€€€€€€€€€€¥¹¹•È€ôÍ±¥‘•ÉÌ¡Í•l‰Í±¥‘•ÉÌ‰t¤(€€€€€€€•±¥˜Í•l‰ÑåÁ”‰t€ôô€‰¥µÁ…Ğˆè(€€€€€€€€€€€¥¹¹•È€ô¥µÁ…Ñ}É¥¡Í•l‰…É‘Ì‰t¤(€€€€€€€€€€€¥˜Í•Œ¹•Ğ ‰Ñ…‰±”ˆ¤è(€€€€€€€€€€€€€€€Ğ€ôÍ•l‰Ñ…‰±”‰t(€€€€€€€€€€€€€€€¥¹¹•È€¬ôÑ…‰±”¡Ñl‰¡•…‘•ÉÌ‰t°Ñl‰É½İÌ‰t¤(€€€€€€€•±¥˜Í•l‰ÑåÁ”‰t€ôô€‰Ñ•…´ˆè(€€€€€€€€€€€¥¹¹•È€ôÑ•…µ}É¥¡Í•l‰µ•µ‰•ÉÌ‰t°Í±Õœ¤(€€€€€€€€€€€¥˜Í•Œ¹•Ğ ‰‘É•…µ}•¸ˆ¤è(€€€€€€€€€€€€€€€¥¹¹•È€¬ô˜œñ‘¥Ø±…ÍÌô‰™É½ÍĞµ¹½Ñ”ˆùí‰¤¡Í•l‰‘É•…µ}•¸‰t°Í•l‰‘É•…µ}•Ì‰t¥ôğ½‘¥Øøœ(€€€€€€€•±¥˜Í•l‰ÑåÁ”‰t€ôô€‰¡Ñµ°ˆè(€€€€€€€€€€€¥¹¹•È€ôÍ•l‰¡Ñµ°‰t((€€€€€€€Í•Ñ¥½¹Í}¡Ñµ°€¬ô€ (€€€€€€€€€€€˜œñ‘¥Ø±…ÍÌô‰Í•ŒˆÍÑå±”ô‰Á½Í¥Ñ¥½¸éÉ•±…Ñ¥Ù”ìˆøœ(€€€€€€€€€€€˜œñ‘¥Ø±…ÍÌô‰Í•Œµ‰œˆÍÑå±”ô‰‰…­É½Õ¹µ¥µ…”éÕÉ°¡pí‰õpœ¤ìˆøğ½‘¥Øøœ(€€€€€€€€€€€˜œñ‘¥Ø±…ÍÌô‰Í•Œµ½ØˆÍÑå±”ô‰‰…­É½Õ¹éí½Ùôìˆøğ½‘¥Øøœ(€€€€€€€€€€€˜œñ‘¥Ø±…ÍÌô‰Í•Œµ¡•…‘•Èˆøñ‘¥Ø±…ÍÌô‰Í•Œµ¹Õ´ˆùí¹Õ´èÀÉ‘ôğ½‘¥Øøœ(€€€€€€€€€€€˜œñ‘¥Ø±…ÍÌô‰Í•ŒµÑ¥Ñ±”ˆùí‰¤¡Ñ¥Ñ±•}•¸°Ñ¥Ñ±•}•Ì¥ôğ½‘¥Øøñ‘¥Ø±…ÍÌô‰Í•ŒµÉÕ±”ˆøğ½‘¥Øøğ½‘¥Øøœ(€€€€€€€€€€€˜í¥¹¹•Éôğ½‘¥Øøœ(€€€€€€€€¤(€€€€€€€¥˜Í•Œ¹•Ğ ‰…•¹Ñ}…™Ñ•Èˆ¤è(€€€€€€€€€€€Í•Ñ¥½¹Í}¡Ñµ°€¬ô€œñ‘¥Ø±…ÍÌô‰…•¹Ğµ‰…Èˆøğ½‘¥Øøœ((€€€‘•¬€ô¹•Ğ ‰‘•­}Á‘˜ˆ¤½Èíô(€€€‘•­}±¥¹¬€ô€ˆˆ(€€€¥˜‘•¬¹•Ğ ‰Ù¥•İ}ÕÉ°ˆ¤½È‘•¬¹•Ğ ‰‘É¥Ù•}¥ˆ¤è(€€€€€€€Ù¥•Ü€ô‘•¬¹•Ğ ‰Ù¥•İ}ÕÉ°ˆ¤½È˜‰¡ÑÑÁÌè¼½‘É¥Ù”¹½½±”¹½´½™¥±”½½í‘•­l‘É¥Ù•}¥uô½Ù¥•Üˆ(€€€€€€€‘•­}±¥¹¬€ô˜œñ„±…ÍÌô‰Ñ„µ±¥¹¬ˆ¡É•˜ô‰íÙ¥•İôˆÑ…É•Ğô‰}‰±…¹¬ˆÉ•°ô‰¹½½Á•¹•Èˆùí‰¤ ‰A¥Ñ ‘•¬€¡A¤ˆ°€‰A¥Ñ ‘•¬€¡A¤ˆ¥ôğ½„øœ((€€€É•ÑÕÉ¸˜ˆˆˆğ…=QeA¡Ñµ°ø(ñ¡Ñµ°±…¹œô‰•¸ˆø(ñ¡•…ø(ñµ•Ñ„¡…ÉÍ•Ğô‰UQ´àˆø(ñµ•Ñ„¹…µ”ô‰Ù¥•İÁ½ÉĞˆ½¹Ñ•¹Ğô‰İ¥‘Ñ õ‘•Ù¥”µİ¥‘Ñ °¥¹¥Ñ¥…°µÍ…±”ôÄˆø(ñÑ¥Ñ±”ùí‘l‰¹…µ”‰uôƒŠP±•…¹Ñ•¡!UMÑ…ÉÑÕÀAÉ½™¥±”ğ½Ñ¥Ñ±”ø(ñ±¥¹¬É•°ô‰¥½¸ˆ¡É•˜ô‰¡ÑÑÁÌè¼½±•…¹Ñ•¡¡Õˆ¹¹•Ğ½™…Ù¥½¸¹¥¼ˆø(ñ±¥¹¬¡É•˜ô‰¡ÑÑÁÌè¼½™½¹ÑÌ¹½½±•…Á¥Ì¹½´½ÍÌÈı™…µ¥±äõ=Á•¸­M…¹Ìéİ¡Ñ ĞÀÀìØÀÀìÜÀÀìàÀÀ™™…µ¥±äõAP­M…¹Ìéİ¡Ñ ĞÀÀìÜÀÀ™‘¥ÍÁ±…äõÍİ…ÀˆÉ•°ô‰ÍÑå±•Í¡••Ğˆø(ñÍÑå±”ø)íÍÍô(ğ½ÍÑå±”ø(ğ½¡•…ø(ñ‰½‘äø(ñ‘¥Ø±…ÍÌô‰Í¥Ñ”µ‰É…¹ˆøñÍÁ…¸±…ÍÌô‰‰É…¹µÑ•áĞˆù±•…¹Ñ• ñ•´ù!Uğ½•´øğ½ÍÁ…¸øğ½‘¥Øø(ñ‘¥Ø±…ÍÌô‰±…¹œµÑ½±”ˆø(€€ñ‰ÕÑÑ½¸±…ÍÌô‰±ˆ…Ñ¥Ù”ˆ½¹±¥¬ô‰‘½Õµ•¹Ğ¹‘½Õµ•¹Ñ±•µ•¹Ğ¹±…¹œô•¸œíÑ¡¥Ì¹±…ÍÍ1¥ÍĞ¹…‘ …Ñ¥Ù”œ¤íÑ¡¥Ì¹¹•áÑ±•µ•¹ÑM¥‰±¥¹œ¹±…ÍÍ1¥ÍĞ¹É•µ½Ù” …Ñ¥Ù”œ¤ìˆù8ğ½‰ÕÑÑ½¸ø(€€ñ‰ÕÑÑ½¸±…ÍÌô‰±ˆˆ½¹±¥¬ô‰‘½Õµ•¹Ğ¹‘½Õµ•¹Ñ±•µ•¹Ğ¹±…¹œô•ÌœíÑ¡¥Ì¹±…ÍÍ1¥ÍĞ¹…‘ …Ñ¥Ù”œ¤íÑ¡¥Ì¹ÁÉ•Ù¥½ÕÍ±•µ•¹ÑM¥‰±¥¹œ¹±…ÍÍ1¥ÍĞ¹É•µ½Ù” …Ñ¥Ù”œ¤ìˆùLğ½‰ÕÑÑ½¸ø(ğ½‘¥Øø((ñ‘¥Ø±…ÍÌô‰Í•Œ¡•É¼ˆø(€€ñ¥µœ±…ÍÌô‰¡•É¼µ¥µœˆÍÉŒô‰í…ÍÍ•Ñ}ÕÉ°¡‘l‰¡•É½}¥µ…”‰t°Í±Õœ¥ôˆ…±Ğô‰í‘l‰¹…µ”‰uôˆ±½…‘¥¹œô‰±…éäˆø(€€ñ‘¥Ø±…ÍÌô‰¡•É¼µ½Øˆøğ½‘¥Øø(€€ñ‘¥Ø±…ÍÌô‰¡•É¼µ‰…‘”ˆøñ‘¥Ø±…ÍÌô‰Á¥±°ˆÍÑå±”ô‰‰…­É½Õ¹éÉ‰„ À°À°À°¸ĞÔ¤í½±½ÈéÙ…È ´µ±œ¤ìˆùí‰¤¡‘l‰‰…‘•}•¸‰t°‘l‰‰…‘•}•Ì‰t¥ôğ½‘¥Øøğ½‘¥Øø(€€ñ‘¥Ø±…ÍÌô‰¡•É¼µ¥¸ˆø(€€€€ñ‘¥Ø±…ÍÌô‰¡•É¼µ¹…µ”ˆùí‘l‰¹…µ”‰uôğ½‘¥Øø(€€€€ñ‘¥Ø±…ÍÌô‰¡•É¼µÍÕˆˆùí‰¤¡‘l‰¡•É½}ÍÕ‰}•¸‰t°‘l‰¡•É½}ÍÕ‰}•Ì‰t¥ôğ½‘¥Øø(€€€€ñ‘¥Ø±…ÍÌô‰¡•É¼µÁ¥Ñ ˆùí‰¤¡‘l‰Á¥Ñ¡}•¸‰t°‘l‰Á¥Ñ¡}•Ì‰t¥ôğ½‘¥Øø(€€ğ½‘¥Øø(€€ñ‘¥Ø±…ÍÌô‰¡•É¼µÑ…±¥¹”ˆù%¹ÍÁ¥É„¸Óé„¸QÉ…¹Í™½Éµ„¸ğ½‘¥Øø(ğ½‘¥Øø((ñ‘¥Ø±…ÍÌô‰É¥‰‰½¸ˆÍÑå±”ô‰‰…­É½Õ¹éÉ‰„ ÄÈ°ÜÌ°ÄÌà°¸äÔ¤ìˆùíÉ¥‰‰½¹ôğ½‘¥Øø()í‘•­}Í•Ñ¥½¸¡°Í±Õœ¥ô()íÍ•Ñ¥½¹Í}¡Ñµ±ô((ñ‘¥Ø±…ÍÌô‰Í•ŒˆÍÑå±”ô‰Á½Í¥Ñ¥½¸éÉ•±…Ñ¥Ù”ìˆø(€€ñ‘¥Ø±…ÍÌô‰Í•Œµ‰œˆÍÑå±”ô‰‰…­É½Õ¹µ¥µ…”éÕÉ° í…ÍÍ•Ñ}ÕÉ° ˆ¸½…ÍÍ•ÑÌ½‰œµÑ„¹©Áœˆ°Í±Õœ¥ôœ¤ìˆøğ½‘¥Øø(€€ñ‘¥Ø±…ÍÌô‰Í•Œµ½ØˆÍÑå±”ô‰‰…­É½Õ¹éÉ‰„ ÄÈ°ÜÌ°ÄÌà°¸ÌÀ¤ìˆøğ½‘¥Øø(€€ñ‘¥Ø±…ÍÌô‰Ñ„ˆø(€€€€ñ‘¥Ø±…ÍÌô‰Á¥±°ˆÍÑå±”ô‰‰…­É½Õ¹éÉ‰„ ÄÔÜ°ÄäÔ°ÄÌÈ°¸ÄÈ¤í‰½É‘•ÈèÅÁàÍ½±¥É‰„ ÄÔÜ°ÄäÔ°ÄÌÈ°¸È¤í½±½ÈéÙ…È ´µ±œ¤íµ…É¥¸µ‰½ÑÑ½´èÄÙÁàìˆùí‰¤¡‘l‰‰…‘•}•¸‰t°‘l‰‰…‘•}•Ì‰t¥ôğ½‘¥Øø(€€€€ñ‘¥Ø±…ÍÌô‰Ñ„µ¹…µ”ˆùí‘l‰¹…µ”‰uôğ½‘¥Øø(€€€€ñ‘¥Ø±…ÍÌô‰Ñ„µÁ¥Ñ ˆùí‰¤¡‘l‰Ñ…}Á¥Ñ¡}•¸‰t°‘l‰Ñ…}Á¥Ñ¡}•Ì‰t¥ôğ½‘¥Øø(€€€€ñ„±…ÍÌô‰Ñ„µ‰Ñ¸ˆ¡É•˜ô‰í¹•Ğ ‰İ•‰Í¥Ñ”ˆ°ˆŒˆ¥ôˆùí‰¤¡¹•Ğ ‰Ñ…}‰Ñ¹}•¸ˆ°‰Y¥Í¥Ğİ•‰Í¥Ñ”ˆ¤°¹•Ğ ‰Ñ…}‰Ñ¹}•Ìˆ°‰Y¥Í¥Ñ…ÈÍ¥Ñ¥¼ˆ¤¥ôğ½„ø(€€€€ñ‘¥Ø±…ÍÌô‰Ñ„µ±¥¹­Ìˆø(€€€€€€ñ„±…ÍÌô‰Ñ„µ±¥¹¬ˆ¡É•˜ô‰¡ÑÑÁÌè¼½¹•áÕÌ¹±•…¹Ñ•¡¡Õˆ¹¹•Ğ½Ì½íÍ±Õôˆùí‰¤ ‰9•áÕÌAÉ½™¥±”ˆ°€‰A•É™¥°9•áÕÌˆ¥ôğ½„ø(€€€€€€ñ„±…ÍÌô‰Ñ„µ±¥¹¬ˆ¡É•˜ô‰¡ÑÑÁÌè¼½¹•áÕÌ¹±•…¹Ñ•¡¡Õˆ¹¹•Ğ½À½ÍÑ…ÉÑÕÀµÁ½ÉÑ™½±¥¼ˆùí‰¤ ˆÄÔÜMÑ…ÉÑÕÁÌˆ°€ˆÄÔÜMÑ…ÉÑÕÁÌˆ¥ôğ½„ø(€€€€€í‘•­}±¥¹­ô(€€€€ğ½‘¥Øø(€€€€ñ‘¥Ø±…ÍÌô‰Ñ„µ‰É…¹ˆøñ‘¥Ø±…ÍÌô‰Ñœˆù%¹ÍÁ¥É„¸Óé„¸QÉ…¹Í™½Éµ„¸ğ½‘¥Øøñ‘¥Ø±…ÍÌô‰±œÈˆù±•…¹Ñ• ñ•´ÍÑå±”ô‰½±½ÈéÙ…È ´µ±œ¤í™½¹ĞµÍÑå±”é¹½Éµ…°ìˆù!Uğ½•´øğ½‘¥Øøğ½‘¥Øø(€€€€ñ‘¥Ø±…ÍÌô‰Ñ„µÁ½ÉĞˆùí‰¤ ‰±•…¹Ñ•¡!UÁ½ÉÑ™½±¥¼ÁÉ½™¥±”ƒ
Ü1…Ñ¥¸µ•É¥„ˆ°€‰A•É™¥°Á½ÉÑ…™½±¥¼±•…¹Ñ•¡!Uƒ
Ü·‘É¥„1…Ñ¥¹„ˆ¥ôğ½‘¥Øø(€€ğ½‘¥Øø(ğ½‘¥Øø(ñ‘¥Ø±…ÍÌô‰…•¹Ğµ‰…Èˆøğ½‘¥Øø(ğ½‰½‘äø(ğ½¡Ñµ°øˆˆˆ(()‘•˜µ…¥¸ ¤€´ø9½¹”è(€€€=UQ}IA<¹µ­‘¥È¡Á…É•¹ÑÌõQÉÕ”°•á¥ÍÑ}½¬õQÉÕ”¤(€€€=UQ}I!%Y¹µ­‘¥È¡Á…É•¹ÑÌõQÉÕ”°•á¥ÍÑ}½¬õQÉÕ”¤(€€€½¹±ä€ôÍåÌ¹…ÉÙlÄét¥˜±•¸¡ÍåÌ¹…ÉØ¤€ø€Ä•±Í”9½¹”(€€€™½È©Í½¹}Á…Ñ ¥¸Í½ÉÑ•¡Q}%H¹±½ˆ ˆ¨¹©Í½¸ˆ¤¤è(€€€€€€€‘…Ñ„€ô©Í½¸¹±½…‘Ì¡©Í½¹}Á…Ñ ¹É•…‘}Ñ•áĞ ¤¤(€€€€€€€Í±Õœ€ô‘…Ñ…l‰Í±Õœ‰t(€€€€€€€¥˜½¹±ä…¹Í±Õœ¹½Ğ¥¸½¹±äè(€€€€€€€€€€€½¹Ñ¥¹Õ”(€€€€€€€¡Ñµ°€ô‰Õ¥±‘}Á…”¡‘…Ñ„¤(€€€€€€€Á‘™}ÍÉ}¹…µ”€ô€¡‘…Ñ„¹•Ğ ‰‘•­}Á‘˜ˆ¤½Èíô¤¹•Ğ ‰Í½ÕÉ•}™¥±”ˆ¤(€€€€€€€µ•‘¥…}ÍÉŒ€ô=UQ}5%€¼Í±Õœ(€€€€€€€™½È‰…Í”¥¸€¡=UQ}IA<€¼Í±Õœ°=UQ}I!%Y€¼Í±Õœ¤è(€€€€€€€€€€€‰…Í”¹µ­‘¥È¡Á…É•¹ÑÌõQÉÕ”°•á¥ÍÑ}½¬õQÉÕ”¤(€€€€€€€€€€€€¡‰…Í”€¼€‰¥¹‘•à¹¡Ñµ°ˆ¤¹İÉ¥Ñ•}Ñ•áĞ¡¡Ñµ°¤(€€€€€€€€€€€¥˜µ•‘¥…}ÍÉŒ¹¥Í}‘¥È ¤è(€€€€€€€€€€€€€€€‘•ÍÑ}…ÍÍ•ÑÌ€ô‰…Í”€¼€‰…ÍÍ•ÑÌˆ(€€€€€€€€€€€€€€€¥˜‘•ÍÑ}…ÍÍ•ÑÌ¹•á¥ÍÑÌ ¤è(€€€€€€€€€€€€€€€€€€€Í¡ÕÑ¥°¹ÉµÑÉ•”¡‘•ÍÑ}…ÍÍ•ÑÌ¤(€€€€€€€€€€€€€€€Í¡ÕÑ¥°¹½ÁåÑÉ•”¡µ•‘¥…}ÍÉŒ°‘•ÍÑ}…ÍÍ•ÑÌ°‘¥ÉÍ}•á¥ÍÑ}½¬õ…±Í”¤(€€€€€€€€€€€¥˜Á‘™}ÍÉ}¹…µ”è(€€€€€€€€€€€€€€€ÍÉ}Á‘˜€ô-}M=UI€¼Á‘™}ÍÉ}¹…µ”(€€€€€€€€€€€€€€€¥˜ÍÉ}Á‘˜¹¥Í}™¥±” ¤è(€€€€€€€€€€€€€€€€€€€Í¡ÕÑ¥°¹½ÁäÈ¡ÍÉ}Á‘˜°‰…Í”€¼€‰‘•¬¹Á‘˜ˆ¤(€€€€€€€ÁÉ¥¹Ğ¡˜‰	Õ¥±ĞíÍ±Õôˆ¤(()¥˜}}¹…µ•}|€ôô€‰}}µ…¥¹}|ˆè(€€€µ…¥¸ ¤(