#!/usr/bin/env python3
"""Download unique context images for batch-11 portfolio one-pagers and patch JSON."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "onepagers" / "data"
MEDIA = ROOT / "onepagers" / "media"

U = "https://images.unsplash.com/{id}?w=1200&q=80"

# (file_key, url, credit_en, credit_es)
ASSETS: dict[str, list[tuple[str, str, str, str]]] = {
    "pleia": [
        (
            "hero",
            "https://pleia.co/wp-content/uploads/2022/10/banner-pleia.jpg",
            "Photo: PLEIA (pleia.co)",
            "Foto: PLEIA (pleia.co)",
        ),
        (
            "bg-problem",
            U.format(id="photo-1587300003388-59208cc962cb"),
            "Photo: Alvan Nee / Unsplash",
            "Foto: Alvan Nee / Unsplash",
        ),
        (
            "bg-solution",
            "https://pleia.co/wp-content/uploads/2022/02/imagen-planta-e1747338556329.png",
            "Photo: PLEIA — memorial plant service (pleia.co)",
            "Foto: PLEIA — servicio planta conmemorativa (pleia.co)",
        ),
        (
            "bg-impact",
            "https://pleia.co/wp-content/uploads/2022/02/acompanamiento-psicologico.jpg",
            "Photo: PLEIA — Jardín de la Vida (pleia.co)",
            "Foto: PLEIA — Jardín de la Vida (pleia.co)",
        ),
        (
            "bg-team",
            U.format(id="photo-1548199973-03cce0bbc87b"),
            "Photo: Bruno Emmanuelle / Unsplash",
            "Foto: Bruno Emmanuelle / Unsplash",
        ),
        (
            "bg-cta",
            U.format(id="photo-1500382017468-9049fed747ef"),
            "Photo: Zosia Szopka / Unsplash",
            "Foto: Zosia Szopka / Unsplash",
        ),
    ],
    "plasfacol": [
        (
            "hero",
            "https://store-cdn.venndelo.com/shared/imagen-486140.jpg",
            "Photo: Plasfacol storefront (eco-tienda-plasfacol.venndelo.com)",
            "Foto: Tienda Plasfacol (eco-tienda-plasfacol.venndelo.com)",
        ),
        (
            "bg-problem",
            U.format(id="photo-1504307651254-35680f356dfd"),
            "Photo: Ricardo Gomez Angel / Unsplash",
            "Foto: Ricardo Gomez Angel / Unsplash",
        ),
        (
            "bg-solution",
            U.format(id="photo-1563986768609-322da13575f3"),
            "Photo: Nick Fewings / Unsplash",
            "Foto: Nick Fewings / Unsplash",
        ),
        (
            "bg-impact",
            "https://store-cdn.venndelo.com/shared/image-gancho-de-ropa-x-100-uds-1037780-i484994-s200x200-f1.jpg",
            "Photo: Plasfacol product — recycled-plastic hanger (venndelo.com)",
            "Foto: Producto Plasfacol — gancho plástico reciclado (venndelo.com)",
        ),
        (
            "bg-team",
            U.format(id="photo-1581091226825-a6a2a5aee158"),
            "Photo: ThisIsEngineering / Unsplash",
            "Foto: ThisIsEngineering / Unsplash",
        ),
        (
            "bg-cta",
            U.format(id="photo-1558618666-fcd25c85cd64"),
            "Photo: Zdeněk Macháček / Unsplash",
            "Foto: Zdeněk Macháček / Unsplash",
        ),
    ],
    "purest-fuels": [
        (
            "hero",
            U.format(id="photo-1473341304170-971dccb5ac1e"),
            "Photo: Appolinary Kalashnikova / Unsplash",
            "Foto: Appolinary Kalashnikova / Unsplash",
        ),
        (
            "bg-problem",
            U.format(id="photo-1521791136064-7986c2920216"),
            "Photo: Scott Webb / Unsplash",
            "Foto: Scott Webb / Unsplash",
        ),
        (
            "bg-solution",
            U.format(id="photo-1551288049-bebda4e38f71"),
            "Photo: Luke Chesser / Unsplash",
            "Foto: Luke Chesser / Unsplash",
        ),
        (
            "bg-impact",
            U.format(id="photo-1518837695005-2083093ee35b"),
            "Photo: Matt Hardy / Unsplash",
            "Foto: Matt Hardy / Unsplash",
        ),
        (
            "bg-team",
            U.format(id="photo-1416879595882-3373a0480b5b"),
            "Photo: Markus Spiske / Unsplash",
            "Foto: Markus Spiske / Unsplash",
        ),
        (
            "bg-cta",
            U.format(id="photo-1516734212186-a967f81ad0d7"),
            "Photo: Science in HD / Unsplash",
            "Foto: Science in HD / Unsplash",
        ),
    ],
    "kelab": [
        (
            "hero",
            U.format(id="photo-1450101499163-c8848c66ca85"),
            "Photo: Elevate / Unsplash",
            "Foto: Elevate / Unsplash",
        ),
        (
            "bg-problem",
            U.format(id="photo-1560807707-8cc77767d783"),
            "Photo: National Cancer Institute / Unsplash",
            "Foto: National Cancer Institute / Unsplash",
        ),
        (
            "bg-solution",
            U.format(id="photo-1447933601403-0c6688de566e"),
            "Photo: Nathan Dumlao / Unsplash",
            "Foto: Nathan Dumlao / Unsplash",
        ),
        (
            "bg-impact",
            U.format(id="photo-1518977676601-b53f82aba655"),
            "Photo: Mockup Graphics / Unsplash",
            "Foto: Mockup Graphics / Unsplash",
        ),
        (
            "bg-team",
            U.format(id="photo-1600880292203-757bb62b4baf"),
            "Photo: Austin Distel / Unsplash",
            "Foto: Austin Distel / Unsplash",
        ),
        (
            "bg-cta",
            U.format(id="photo-1529156069898-49953e39b3ac"),
            "Photo: Priscilla Du Preez / Unsplash",
            "Foto: Priscilla Du Preez / Unsplash",
        ),
    ],
    "simbiotic": [
        (
            "hero",
            "https://redsimbiotic.com/wp-content/uploads/2025/08/Traveltech-Turistas-escaneando-codigo-QR-en-Triply-para-descubrir-historias-locales.jpg",
            "Photo: Simbiotic — Triply sustainable tourism (redsimbiotic.com)",
            "Foto: Simbiotic — turismo sostenible Triply (redsimbiotic.com)",
        ),
        (
            "bg-problem",
            "https://redsimbiotic.com/wp-content/uploads/2026/09/IMG_8360.jpg",
            "Photo: Simbiotic (redsimbiotic.com)",
            "Foto: Simbiotic (redsimbiotic.com)",
        ),
        (
            "bg-solution",
            "https://redsimbiotic.com/wp-content/uploads/2022/09/WhatsApp-Image-2022-08-29-at-5.07.45-PM.jpeg",
            "Photo: Simbiotic team (redsimbiotic.com)",
            "Foto: Equipo Simbiotic (redsimbiotic.com)",
        ),
        (
            "bg-impact",
            "https://redsimbiotic.com/wp-content/uploads/2026/07/WhatsApp-Image-2026-07-17-at-10.52.25.jpeg",
            "Photo: Simbiotic — ADN Sostenible (redsimbiotic.com)",
            "Foto: Simbiotic — ADN Sostenible (redsimbiotic.com)",
        ),
        (
            "bg-team",
            U.format(id="photo-1522071820081-009f0129c71c"),
            "Photo: Christina @ wocintechchat.com / Unsplash",
            "Foto: Christina @ wocintechchat.com / Unsplash",
        ),
        (
            "bg-cta",
            U.format(id="photo-1542601906990-b4d3fb778b09"),
            "Photo: Zbynek Burival / Unsplash",
            "Foto: Zbynek Burival / Unsplash",
        ),
    ],
}

SECTION_BG_KEYS = ["bg-problem", "bg-solution", "bg-impact", "bg-team"]


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Nexus/1.0)"})
    data = urllib.request.urlopen(req, timeout=60).read()
    if url.lower().endswith(".png") or data[:8].startswith(b"\x89PNG"):
        ext = ".png"
    elif ".jpeg" in url.lower() or data[:2] == b"\xff\xd8":
        ext = ".jpg"
    else:
        ext = ".jpg"
    if dest.suffix.lower() not in (".jpg", ".jpeg", ".png"):
        dest = dest.with_suffix(ext)
    dest.write_bytes(data)
    return dest


def main() -> None:
    used_urls: set[str] = set()
    for slug, items in ASSETS.items():
        credits: dict[str, tuple[str, str]] = {}
        paths: dict[str, str] = {}
        for key, url, cred_en, cred_es in items:
            if url in used_urls:
                raise SystemExit(f"Duplicate image URL across pages: {url}")
            used_urls.add(url)
            ext = ".png" if url.lower().endswith(".png") else ".jpg"
            fname = ("hero" if key == "hero" else key) + ext
            dest = MEDIA / slug / "assets" / fname
            print(f"Downloading {slug}/{fname} …")
            dest = download(url, dest)
            paths[key] = f"./assets/{dest.name}"
            credits[key] = (cred_en, cred_es)

        json_path = DATA / f"{slug}.json"
        page = json.loads(json_path.read_text())
        page["hero_image"] = paths["hero"]
        page["hero_credit_en"] = credits["hero"][0]
        page["hero_credit_es"] = credits["hero"][1]
        page["cta_bg"] = paths["bg-cta"]
        page["cta_bg_credit_en"] = credits["bg-cta"][0]
        page["cta_bg_credit_es"] = credits["bg-cta"][1]
        for i, sec in enumerate(page["sections"]):
            bg_key = SECTION_BG_KEYS[i]
            sec["bg"] = paths[bg_key]
            sec["bg_credit_en"] = credits[bg_key][0]
            sec["bg_credit_es"] = credits[bg_key][1]
        json_path.write_text(json.dumps(page, indent=2, ensure_ascii=False) + "\n")
        print(f"Updated {json_path.name}")


if __name__ == "__main__":
    main()
