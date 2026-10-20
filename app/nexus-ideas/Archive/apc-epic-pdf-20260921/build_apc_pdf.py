#!/usr/bin/env python3
"""Build CTH-branded APC Epic Angels 17-card HTML → PDF."""
import html
import json
import subprocess
import sys
from pathlib import Path

OUT_DIR = Path("/opt/nexus-idea-browser/Archive/apc-epic-pdf-20260921")
PACK = OUT_DIR / "source-pack.json"
HTML_OUT = OUT_DIR / "CTH-Epic-Angels-APC-17-cards-DRAFT-2026-09-21.html"
PDF_OUT = OUT_DIR / "CTH-Epic-Angels-APC-17-cards-DRAFT-2026-09-21.pdf"

BRAND = {
    "deep_blue": "#0C498A",
    "light_cyan": "#B2EEFA",
    "light_green": "#9DC384",
    "forest": "#669348",
    "sky": "#69B5FA",
}


def esc(s):
    return html.escape(str(s) if s is not None else "")


def nexus_display(card):
    if card.get("nexus_status") == "live" and card.get("nexus_url"):
        return esc(card["nexus_url"]), False
    return "[PENDIENTE]", True


def website_display(card):
    if card.get("website_status") == "live" and card.get("website"):
        return esc(card["website"]), False
    return "[PENDIENTE]", True


def card_html(card, idx):
    nexus_val, nexus_pending = nexus_display(card)
    web_val, web_pending = website_display(card)
    nexus_cls = " pending" if nexus_pending else ""
    web_cls = " pending" if web_pending else ""

    return f"""
    <section class="card-page">
      <div class="card-accent"></div>
      <div class="card-inner">
        <div class="card-num">{idx:02d} / 17</div>
        <h2 class="startup">{esc(card['startup_name'])}</h2>
        <div class="field">
          <span class="label">Founder</span>
          <span class="value">{esc(card.get('founder') or '[PENDIENTE]')}</span>
        </div>
        <div class="field one-liner">
          <span class="label">One-liner</span>
          <p class="value">{esc(card.get('one_liner') or card.get('fit_note', ''))}</p>
        </div>
        <div class="field">
          <span class="label">Nexus</span>
          <span class="value url{nexus_cls}">{nexus_val}</span>
        </div>
        <div class="field">
          <span class="label">Website</span>
          <span class="value url{web_cls}">{web_val}</span>
        </div>
        <div class="meta">
          <span>confidence: {esc(card.get('confidence', '—'))}</span>
          <span>women C-level: {esc(card.get('women_clevel_status', '—'))}</span>
        </div>
      </div>
      <footer class="card-footer">
        <span>CleantechHUB × Epic Angels</span>
        <span class="tagline">Inspira. Actúa. Transforma.</span>
      </footer>
    </section>
    """


def build_html(data):
    cards = data["cards"]
    cards_body = "\n".join(card_html(c, i + 1) for i, c in enumerate(cards))

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>CTH × Epic Angels — APC 17 cards DRAFT 2026-09-21</title>
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
@page {{
  size: A4;
  margin: 0;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: 'Open Sans', sans-serif;
  color: {BRAND['deep_blue']};
  background: #fff;
}}
.page {{
  width: 210mm;
  min-height: 297mm;
  page-break-after: always;
  position: relative;
  overflow: hidden;
}}
.page:last-child {{ page-break-after: auto; }}

/* Cover */
.cover {{
  background: linear-gradient(160deg, {BRAND['deep_blue']} 0%, {BRAND['forest']} 55%, {BRAND['light_green']} 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 48px;
}}
.cover-band {{
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 8px;
  background: linear-gradient(90deg,
    {BRAND['deep_blue']} 0%,
    {BRAND['sky']} 25%,
    {BRAND['light_cyan']} 50%,
    {BRAND['light_green']} 75%,
    {BRAND['forest']} 100%);
}}
.draft-banner {{
  background: {BRAND['light_cyan']};
  color: {BRAND['deep_blue']};
  font-weight: 800;
  font-size: 14px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  padding: 14px 28px;
  border-radius: 4px;
  margin-bottom: 48px;
  border: 3px solid #fff;
  box-shadow: 0 4px 20px rgba(0,0,0,.25);
}}
.cover h1 {{
  font-size: 36px;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 12px;
  text-shadow: 0 2px 12px rgba(0,0,0,.3);
}}
.cover .subtitle {{
  font-size: 18px;
  font-weight: 600;
  opacity: .95;
  margin-bottom: 64px;
}}
.cover .tagline {{
  font-size: 22px;
  font-style: italic;
  font-weight: 600;
  color: {BRAND['light_cyan']};
  margin-top: 48px;
}}
.cover .meta-line {{
  position: absolute;
  bottom: 36px;
  font-size: 11px;
  opacity: .85;
  letter-spacing: .5px;
}}
.cover .count-badge {{
  margin-top: 24px;
  font-size: 13px;
  font-weight: 700;
  background: rgba(255,255,255,.15);
  padding: 10px 24px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.35);
}}

/* Cards */
.card-page {{
  width: 210mm;
  min-height: 297mm;
  page-break-after: always;
  display: flex;
  flex-direction: column;
  background: #fff;
  position: relative;
}}
.card-accent {{
  height: 6px;
  background: linear-gradient(90deg, {BRAND['deep_blue']}, {BRAND['sky']}, {BRAND['light_green']});
}}
.card-inner {{
  flex: 1;
  padding: 36px 44px 24px;
}}
.card-num {{
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: {BRAND['forest']};
  margin-bottom: 8px;
}}
.startup {{
  font-size: 28px;
  font-weight: 800;
  color: {BRAND['deep_blue']};
  line-height: 1.15;
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 3px solid {BRAND['light_cyan']};
}}
.field {{
  margin-bottom: 20px;
}}
.field .label {{
  display: block;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: {BRAND['forest']};
  margin-bottom: 6px;
}}
.field .value {{
  font-size: 13px;
  font-weight: 600;
  line-height: 1.5;
  color: {BRAND['deep_blue']};
  word-break: break-word;
}}
.field.one-liner .value {{
  font-weight: 400;
  font-size: 12.5px;
  line-height: 1.65;
}}
.field .value.url {{
  font-size: 11.5px;
  color: {BRAND['sky']};
}}
.field .value.pending {{
  color: {BRAND['forest']};
  font-weight: 800;
  letter-spacing: .5px;
}}
.meta {{
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid {BRAND['light_cyan']};
  display: flex;
  gap: 24px;
  font-size: 9px;
  font-weight: 600;
  color: {BRAND['forest']};
  text-transform: uppercase;
  letter-spacing: .4px;
}}
.card-footer {{
  padding: 14px 44px;
  background: {BRAND['deep_blue']};
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 9px;
  font-weight: 600;
}}
.card-footer .tagline {{
  font-style: italic;
  color: {BRAND['light_cyan']};
}}
</style>
</head>
<body>

<section class="page cover">
  <div class="cover-band"></div>
  <div class="draft-banner">DRAFT — NO ENVIAR a APC</div>
  <h1>CleantechHUB × Epic Angels</h1>
  <p class="subtitle">APC Startup Cards — Curated Portfolio</p>
  <p class="count-badge">17 startups · Nexus 17/17 live · 2026-09-21</p>
  <p class="tagline">Inspira. Actúa. Transforma.</p>
  <p class="meta-line">CleantechHUB Nexus / Origo · Internal draft for HITL review</p>
</section>

{cards_body}

</body>
</html>
"""


def counts(data):
    cards = data["cards"]
    n_live = sum(1 for c in cards if c.get("nexus_status") == "live" and c.get("nexus_url"))
    n_pend = len(cards) - n_live
    w_live = sum(1 for c in cards if c.get("website_status") == "live" and c.get("website"))
    w_pend = len(cards) - w_live
    return n_live, n_pend, w_live, w_pend


def main():
    data = json.loads(PACK.read_text(encoding="utf-8"))
    html_content = build_html(data)
    HTML_OUT.write_text(html_content, encoding="utf-8")
    print(f"HTML: {HTML_OUT}")

    # Try weasyprint first, fallback to chromium
    try:
        subprocess.run(
            ["weasyprint", str(HTML_OUT), str(PDF_OUT)],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"PDF (weasyprint): {PDF_OUT}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"weasyprint failed: {e}", file=sys.stderr)
        subprocess.run(
            [
                "chromium",
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                f"--print-to-pdf={PDF_OUT}",
                "--print-to-pdf-no-header",
                f"file://{HTML_OUT}",
            ],
            check=True,
        )
        print(f"PDF (chromium): {PDF_OUT}")

    n_live, n_pend, w_live, w_pend = counts(data)
    print(f"COUNTS nexus_live={n_live} nexus_PENDIENTE={n_pend} website_live={w_live} website_PENDIENTE={w_pend}")
    print(f"CARDS={len(data['cards'])}")


if __name__ == "__main__":
    main()
