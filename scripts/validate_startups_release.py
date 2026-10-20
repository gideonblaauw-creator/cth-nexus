#!/usr/bin/env python3
"""Static validation for startups-65 release."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_SLUGS = """
b-kapz elastic-energy mubon novatio plasticos-ambientales ainwater air4u suncolombia weia zhana-solutions
alfe-aseo-sas baruk-company bioarea calojabones ciclorganicos cobox-logistic greenify habitat-a-vibe-company
ala-terra compostpack cr-tejas deposito-global-recycling deterquin dexon-software-sas-bic eco-biosis eco-industria
embergy fluvia galaxy-pack glooba glu-energy griin-energy grupo-natural-andino greendex hunter-tecnologia i-can-jump
ilikko isd-ingenieria-y-servicios istmo-verde kigui kimsa kleantab linko-workers mayugo mitsidi monte-jazmin
moviltronics myma nina-energy nuevas-tecnologias-fisicoquimicas oasis-group pacaceite parsons-kinetics kelab plasfacol
pleia purest-fuels simbiotic tavi-technology tr-global-group valopes wheelo
""".split()

PORTFOLIO_PATHS = [
    ROOT / "pages" / "p" / "startup-portfolio" / "index.html",
    ROOT / "site" / "nexus-www" / "startup-portfolio.html",
]

DRIVE = re.compile(r"drive\.google\.com|docs\.google\.com/document/d/", re.I)


def main() -> int:
    errors: list[str] = []

    for slug in BATCH_SLUGS:
        html = ROOT / "onepagers" / "sites" / slug / "index.html"
        if not html.is_file():
            errors.append(f"missing /s/ page: {slug}")
            continue
        text = html.read_text(errors="replace")
        if "<html" not in text.lower() or "Cleantech" not in text:
            errors.append(f"invalid html skeleton: {slug}")
        if DRIVE.search(text):
            errors.append(f"Drive link in onepager: {slug}")

    for pf in PORTFOLIO_PATHS:
        if not pf.is_file():
            continue
        body = pf.read_text(errors="replace")
        if DRIVE.search(body):
            errors.append(f"Drive link in portfolio: {pf.relative_to(ROOT)}")
        uses_dynamic_onepager = "href=\"/s/'+" in body or "href='/s/'+" in body
        for slug in BATCH_SLUGS:
            if f'slug:"{slug}"' not in body and f"slug:'{slug}'" not in body:
                errors.append(f"portfolio missing card slug:{slug} in {pf.name}")
            elif not uses_dynamic_onepager and f"/s/{slug}" not in body:
                errors.append(f"portfolio card {slug} missing /s/{slug} link in {pf.name}")

    sunco = 0
    for pf in PORTFOLIO_PATHS:
        if pf.is_file():
            sunco += pf.read_text(errors="ignore").count("suncolombia")
    if sunco < 1:
        errors.append("suncolombia card not found in portfolio")

    dup_sunco_names = 0
    for pf in PORTFOLIO_PATHS:
        if pf.is_file():
            t = pf.read_text(errors="ignore")
            dup_sunco_names += len(re.findall(r"Sunco Energy|SUNCO ENERGY", t, re.I))
    if dup_sunco_names > 0:
        errors.append("duplicate Sunco Energy card label (expected SUNCOLOMBIA/suncolombia only)")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" ", e)
        return 1
    print(f"OK: {len(BATCH_SLUGS)} /s/ pages, portfolio links, no Drive URLs, suncolombia card.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
