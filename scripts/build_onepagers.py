#!/usr/bin/env python3
"""Build Nexus startup one-pagers from JSON data + shared template."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data"
TEMPLATE_CSS = ROOT / "onepagers" / "template" / "styles.css"
OUT_REPO = ROOT / "onepagers" / "sites"
OUT_ARCHIVE = Path("/opt/claude-files/Projects/Nexus/startup-pages-draft-2026-08-20")


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


def table(headers, rows) -> str:
    th = "".join(f"<th>{bi(a, b)}</th>" for a, b in headers)
    body = ""
    for row in rows:
        tds = []
        for i, (a, b) in enumerate(row):
            cls = ' class="hl"' if i == len(row) - 1 else ""
            tds.append(f"<td{cls}>{bi(a, b)}</td>")
        body += f"<tr>{''.join(tds)}</tr>"
    return f'<div class="comp-wrap"><table class="comp-tbl"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def sliders(items) -> str:
    parts = ['<div class="slider-wrap">']
    for i, s in enumerate(items):
        sid = f"sl{i}"
        parts.append(f'<div class="slider-item"><div class="sl-label">{bi(s["label_en"], s["label_es"])}</div><div class="sl-val" id="{sid}-out">{s["prefix"]}{s["min"]}{s["suffix"]}</div><input class="sl-range" type="range" id="{sid}" min="{s["min"]}" max="{s["max"]}" step="{s.get("step",1)}" value="{s["min"]}" data-prefix="{s["prefix"]}" data-suffix="{s["suffix"]}" oninput="document.getElementById(\'{sid}-out\').textContent=this.dataset.prefix+this.value+this.dataset.suffix"><div class="sl-hint">{bi(s["hint_en"], s["hint_es"])}</div></div>')
    parts.append("</div>")
    return "".join(parts)


def sol_grid(steps) -> str:
    cards = []
    for n, s in enumerate(steps, 1):
        cards.append(f'<div class="sol-card"><div class="sol-step">{n}</div><div class="sol-icon">{s.get("icon","●")}</div><div class="sol-label">{bi(s["label_en"], s["label_es"])}</div><div class="sol-text">{bi(s["text_en"], s["text_es"])}</div></div>')
    return f'<div class="sol-grid">{"".join(cards)}</div>'


def impact_grid(cards) -> str:
    items = []
    for c in cards:
        items.append(f'<div class="imp-card"><div class="imp-icon">{c.get("icon","●")}</div><div><div class="imp-title">{bi(c["title_en"], c["title_es"])}</div><div class="imp-text">{bi(c["text_en"], c["text_es"])}</div></div></div>')
    return f'<div class="impact-grid">{"".join(items)}</div>'


def team_grid(members) -> str:
    cards = []
    for m in members:
        ini = m.get("initials") or "".join(w[0] for w in m["name"].split()[:2]).upper()
        cards.append(f'<div class="team-card"><div class="tp-avatar" style="background:linear-gradient(135deg,var(--fo),var(--lg));">{ini}</div><div class="tp-name">{m["name"]}</div><div class="tp-role">{bi(m["role_en"], m["role_es"])}</div><div class="tp-bio">{bi(m.get("bio_en",""), m.get("bio_es",""))}</div></div>')
    return f'<div class="team-grid">{"".join(cards)}</div>'


def build_page(d: dict) -> str:
    css = TEMPLATE_CSS.read_text()
    ribbon = "".join(f'<div class="ribbon-cell"><div class="rc-val">{k["val"]}</div><div class="rc-lab">{bi(k["lab_en"], k["lab_es"])}</div><div class="rc-sub">{bi(k.get("sub_en",""), k.get("sub_es",""))}</div></div>' for k in d["ribbon"])
    stats = ""
    if d.get("problem_stats"):
        rows = []
        for idx, row in enumerate(d["problem_stats"]):
            style = ' style="margin-top:0;"' if idx == 0 else ""
            rows.append(f'<div class="stat-row"{style}>' + "".join(f'<div class="stat-card"><div class="sc-num">{s["num"]}</div><div class="sc-lab">{bi(s["lab_en"], s["lab_es"])}</div></div>' for s in row) + "</div>")
        stats = "".join(rows)
    sections_html = ""
    for sec in d["sections"]:
        num = sec["num"]
        title_en, title_es = sec["title_en"], sec["title_es"]
        ov = sec.get("overlay", "rgba(12,73,138,.93)")
        bg = sec.get("bg", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80")
        inner = ""
        t = sec["type"]
        if t == "split": inner = f'<div class="split" style="position:relative;z-index:2;"><div class="split-panel"><div class="split-h">{bi(sec["head_en"], sec["head_es"])}</div><div class="body-text">{bi(sec["body_en"], sec["body_es"])}</div></div><div class="split-panel">{stats}{sec.get("extra_html","")}</div></div>'
        elif t == "solution": inner = sol_grid(sec["steps"])
        elif t == "chart": inner = bar_chart(sec["bars"]) + (f'<div style="padding:0 48px 20px;font-size:10px;color:rgba(255,255,255,.45);">{bi(sec["note_en"], sec["note_es"])}</div>' if sec.get("note_en") else "")
        elif t == "table": inner = table(sec["headers"], sec["rows"])
        elif t == "sliders": inner = sliders(sec["sliders"])
        elif t == "impact": inner = impact_grid(sec["cards"]) + (table(sec["table"]["headers"], sec["table"]["rows"]) if sec.get("table") else "")
        elif t == "team": inner = team_grid(sec["members"]) + (f'<div style="padding:0 48px 28px;font-size:12px;line-height:1.6;color:rgba(255,255,255,.55);">{bi(sec["dream_en"], sec["dream_es"])}</div>' if sec.get("dream_en") else "")
        elif t == "html": inner = sec["html"]
        sections_html += f'<div class="sec" style="position:relative;"><div class="sec-bg" style="background-image:url(\'{bg}\');"></div><div class="sec-ov" style="background:{ov};"></div><div class="sec-header"><div class="sec-num">{num:02d}</div><div class="sec-title">{bi(title_en, title_es)}</div><div class="sec-rule"></div></div>{inner}</div>' + ('<div class="accent-bar"></div>' if sec.get("accent_after") else "")
    slug = d["slug"]
    return f"<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{d['name']} — CleantechHUB Startup Profile</title><link rel=\"icon\" href=\"https://cleantechhub.net/favicon.ico\"><link href=\"https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&family=PT+Sans:wght@400;700&display=swap\" rel=\"stylesheet\"><style>{css}</style></head><body><div class=\"lang-toggle\"><button class=\"lb active\" onclick=\"document.documentElement.lang='en';this.classList.add('active');this.nextElementSibling.classList.remove('active');\">EN</button><button class=\"lb\" onclick=\"document.documentElement.lang='es';this.classList.add('active');this.previousElementSibling.classList.remove('active');\">ES</button></div><div class=\"sec hero\"><img class=\"hero-img\" src=\"{d['hero_image']}\" alt=\"{d['name']}\" loading=\"lazy\"><div class=\"hero-ov\"></div><div class=\"hero-badge\"><div class=\"pill\" style=\"background:rgba(0,0,0,.45);color:var(--lg);\">{bi(d['badge_en'], d['badge_es'])}</div></div><div class=\"hero-logo\">CleantechHUB</div><div class=\"hero-in\"><div class=\"hero-name\">{d['name']}</div><div class=\"hero-sub\">{bi(d['hero_sub_en'], d['hero_sub_es'])}</div><div class=\"hero-pitch\">{bi(d['pitch_en'], d['pitch_es'])}</div></div><div class=\"hero-tagline\">Inspira. Actúa. Transforma.</div></div><div class=\"ribbon\" style=\"background:rgba(12,73,138,.95);\">{ribbon}</div>{sections_html}<div class=\"sec\" style=\"position:relative;\"><div class=\"sec-bg\" style=\"background-image:url('https://images.unsplash.com/photo-1504541331459-5288e5d49ee3?w=1200&q=80');\"></div><div class=\"sec-ov\" style=\"background:radial-gradient(ellipse at 50% 40%,rgba(12,73,138,.8),rgba(5,30,56,.96));\"></div><div class=\"cta\"><div class=\"pill\" style=\"background:rgba(157,195,132,.12);border:1px solid rgba(157,195,132,.2);color:var(--lg);margin-bottom:16px;\">{bi(d['badge_en'], d['badge_es'])}</div><div class=\"cta-name\">{d['name']}</div><div class=\"cta-pitch\">{bi(d['cta_pitch_en'], d['cta_pitch_es'])}</div><a class=\"cta-btn\" href=\"{d.get('website','#')}\">{bi(d.get('cta_btn_en','Visit website'), d.get('cta_btn_es','Visitar sitio'))}</a><div class=\"cta-links\"><a class=\"cta-link\" href=\"https://nexus.cleantechhub.net/s/{slug}\">{bi('Nexus Profile (draft)', 'Perfil Nexus (borrador)')}</a><a class=\"cta-link\" href=\"https://nexus.cleantechhub.net/p/startup-portfolio\">{bi('157 Startups', '157 Startups')}</a></div><div class=\"cta-brand\"><div class=\"tg\">Inspira. Actúa. Transforma.</div><div class=\"lg2\">CleantechHUB</div></div><div class=\"cta-port\">{bi('Draft preview — not deployed to /opt/nexus-onepagers', 'Vista previa borrador — no desplegado en /opt/nexus-onepagers')}</div></div></div><div class=\"accent-bar\"></div></body></html>"


def main() -> None:
    OUT_REPO.mkdir(parents=True, exist_ok=True)
    OUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
    for json_path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(json_path.read_text())
        html = build_page(data)
        slug = data["slug"]
        for base in (OUT_REPO / slug, OUT_ARCHIVE / slug):
            base.mkdir(parents=True, exist_ok=True)
            (base / "index.html").write_text(html)
        print(f"Built {slug}")


if __name__ == "__main__":
    main()
