#!/usr/bin/env python3
"""Apply Nexus image protocol: unique contextual images per batch-6 /s/ page."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "onepagers" / "data"

U = lambda pid: f"https://images.unsplash.com/{pid}?w=1200&q=80"

PAGES: dict[str, dict] = {
    "galaxy-pack": {
        "hero_image": "https://galaxypack.co/wp-content/uploads/2025/06/portada-banner.jpg",
        "cta_bg": U("photo-1565793298595-6ec666cafd36"),
        "section_bgs": [
            "https://galaxypack.co/wp-content/uploads/2024/04/banner-inicio-2-fondo-2.png",
            "https://galaxypack.co/wp-content/uploads/2025/06/banner-cubrepallets.png",
            U("photo-1586528116311-aedba830c192"),
            U("photo-1573164713714-d95e43605808"),
        ],
        "image_credits_en": "Hero, Problem, Solution: galaxypack.co. Impact/Unsplash: CHUTTERSNAP (photo-1586528116311). Leadership/Unsplash: Campaign Creators (photo-1573164713714). CTA/Unsplash: CHUTTERSNAP (photo-1565793298595).",
        "image_credits_es": "Hero, Problema, Soluci&oacute;n: galaxypack.co. Impacto/Unsplash: CHUTTERSNAP (photo-1586528116311). Liderazgo/Unsplash: Campaign Creators (photo-1573164713714). CTA/Unsplash: CHUTTERSNAP (photo-1565793298595).",
    },
    "glooba": {
        "hero_image": U("photo-1454165804606-c3d57bc86b40"),
        "cta_bg": U("photo-1504384308090-c894fdcc538b"),
        "section_bgs": [
            U("photo-1486406146928-c627a92ad1ab"),
            U("photo-1556761175-b413da4baf72"),
            U("photo-1460925895917-afdab827c52f"),
            U("photo-1522071820081-009f0129c71c"),
        ],
        "image_credits_en": "All photos: Unsplash — Hero: Campaign Creators (photo-1454165804606). Problem: Victor (photo-1486406146928). Solution: Kaleidico (photo-1556761175). Impact: Carlos Muza (photo-1460925895917). Leadership: Headway (photo-1522071820081). CTA: Marcos Paulo Prado (photo-1504384308090).",
        "image_credits_es": "Todas las fotos: Unsplash — Hero: Campaign Creators (photo-1454165804606). Problema: Victor (photo-1486406146928). Soluci&oacute;n: Kaleidico (photo-1556761175). Impacto: Carlos Muza (photo-1460925895917). Liderazgo: Headway (photo-1522071820081). CTA: Marcos Paulo Prado (photo-1504384308090).",
    },
    "glu-energy": {
        "hero_image": "https://www.glu-energy.com/uploads/glu_energy_ecosystem.png",
        "cta_bg": U("photo-1559305610-1f977d2bf25f"),
        "section_bgs": [
            "https://www.glu-energy.com/uploads/Picture26.jpg",
            "https://www.glu-energy.com/uploads/Picture27.png",
            U("photo-1497436072904-37f7849041de"),
            U("photo-1518455027359-763f1d6f9667"),
        ],
        "image_credits_en": "Hero, Problem, Solution: glu-energy.com. Impact/Unsplash: Andreas G&uuml;ckl (photo-1497436072904). Leadership/Unsplash: American Public Power Association (photo-1518455027359). CTA/Unsplash: Zane Lee (photo-1559305610).",
        "image_credits_es": "Hero, Problema, Soluci&oacute;n: glu-energy.com. Impacto/Unsplash: Andreas G&uuml;ckl (photo-1497436072904). Liderazgo/Unsplash: American Public Power Association (photo-1518455027359). CTA/Unsplash: Zane Lee (photo-1559305610).",
    },
    "griin-energy": {
        "hero_image": "https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=1440,h=1783,fit=crop/YZ98J1jo3RcxaO7x/img_5777-Yyv0vZeXM0T4Jypq.PNG",
        "cta_bg": U("photo-1592839752740-1c271a7e3499"),
        "section_bgs": [
            "https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=1200,fit=crop,q=95/YZ98J1jo3RcxaO7x/griin-oportunidad-bodega-indal-2-YD0l2RXMP2IZnvJz.png",
            "https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=1200,fit=crop/YZ98J1jo3RcxaO7x/el-poder-solar-al-alcance-de-todos-YZ98J1OqNQhWXVJj.png",
            U("photo-1508514177221-188b1cf16e9d"),
            U("photo-1473341304170-971dccb5ac1e"),
        ],
        "image_credits_en": "Hero, Problem, Solution: griin.com.co (Zyrosite CDN). Impact/Unsplash: Andreas G&uuml;ckl (photo-1508514177221). Leadership/Unsplash: Matthew Henry (photo-1473341304170). CTA/Unsplash: American Public Power Association (photo-1592839752740).",
        "image_credits_es": "Hero, Problema, Soluci&oacute;n: griin.com.co (CDN Zyrosite). Impacto/Unsplash: Andreas G&uuml;ckl (photo-1508514177221). Liderazgo/Unsplash: Matthew Henry (photo-1473341304170). CTA/Unsplash: American Public Power Association (photo-1592839752740).",
    },
    "grupo-natural-andino": {
        "hero_image": U("photo-1416879595882-3373a0480b5b"),
        "cta_bg": U("photo-1466692478222-5f3b0e4b6c3a"),
        "section_bgs": [
            U("photo-1532996122724-e3c031a396bf"),
            U("photo-1595278069443-2792a57bd1f8"),
            U("photo-1625246333195-78d9c38ad449"),
            U("photo-1574944983790-729784346989"),
        ],
        "image_credits_en": "All photos: Unsplash — Hero: Markus Spiske (photo-1416879595882). Problem: Jilbert Ebrahimi (photo-1532996122724). Solution: Noah Buscher (photo-1595278069443). Impact: Zoe Schaeffer (photo-1625246333195). Leadership: Tim Mossholder (photo-1574944983790). CTA: Kyle Glenn (photo-1466692478222). Public copy: gna.com.co.",
        "image_credits_es": "Todas las fotos: Unsplash — Hero: Markus Spiske (photo-1416879595882). Problema: Jilbert Ebrahimi (photo-1532996122724). Soluci&oacute;n: Noah Buscher (photo-1595278069443). Impacto: Zoe Schaeffer (photo-1625246333195). Liderazgo: Tim Mossholder (photo-1574944983790). CTA: Kyle Glenn (photo-1466692478222). Texto p&uacute;blico: gna.com.co.",
    },
}


def main() -> None:
    all_urls: list[str] = []
    for slug, spec in PAGES.items():
        path = DATA / f"{slug}.json"
        data = json.loads(path.read_text())
        data["hero_image"] = spec["hero_image"]
        data["cta_bg"] = spec["cta_bg"]
        data["image_credits_en"] = spec["image_credits_en"]
        data["image_credits_es"] = spec["image_credits_es"]
        for sec, bg in zip(data["sections"], spec["section_bgs"], strict=True):
            sec["bg"] = bg
        urls = [spec["hero_image"], spec["cta_bg"], *spec["section_bgs"]]
        all_urls.extend(urls)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print("Updated", slug)
    dupes = {u for u in all_urls if all_urls.count(u) > 1}
    if dupes:
        raise SystemExit(f"Duplicate image URLs across batch: {dupes}")
    print("OK:", len(all_urls), "unique slots checked")


if __name__ == "__main__":
    main()
