#!/usr/bin/env python3
"""Assign unique, context-specific images for batch-9 /s/ pages."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "onepagers" / "data"
BATCH = ("mayugo", "mitsidi", "monte-jazmin", "moviltronics", "myma")

# Each page: hero, sections[0..3].bg, cta_image — all URLs unique across batch.
PAGES = {
    "mayugo": {
        "hero_image": "https://images.unsplash.com/photo-1516321317523-f80f84f32e42?w=1200&q=80",
        "section_bgs": [
            "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1200&q=80",
            "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&q=80",
            "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80",
            "https://images.unsplash.com/photo-1573167243312-0368182c8f49?w=1200&q=80",
        ],
        "cta_image": "https://images.unsplash.com/photo-1488190211105-38b0de8150a3?w=1200&q=80",
        "image_sources": {
            "hero": "Unsplash — Christopher Gower (online learning / laptop)",
            "section_01_problem": "Unsplash — Campaign Creators (workplace collaboration)",
            "section_02_solution": "Unsplash — Alexis Brown (team learning)",
            "section_03_impact": "Unsplash — Element5 Digital (education materials)",
            "section_04_leadership": "Unsplash — Christina @ wocintechchat.com (team)",
            "cta": "Unsplash — Thought Catalog (remote learning desk)",
        },
    },
    "mitsidi": {
        "hero_image": "https://api-cms.mitsidi.com/media/mitPeople-1.jpg",
        "section_bgs": [
            "https://api-cms.mitsidi.com/media/servicos.jpg",
            "https://api-cms.mitsidi.com/media/solucoesMod.jpg",
            "https://www.mitsidi.com/images/mitPeople.jpg",
            "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200&q=80",
        ],
        "cta_image": "https://api-cms.mitsidi.com/media/banner_expandir_corrigido.png",
        "image_sources": {
            "hero": "Mitsidi public CMS (mitPeople-1.jpg) — mitsidi.com",
            "section_01_problem": "Mitsidi public CMS (servicos.jpg) — mitsidi.com",
            "section_02_solution": "Mitsidi public CMS (solucoesMod.jpg) — mitsidi.com",
            "section_03_impact": "Mitsidi public site (/images/mitPeople.jpg)",
            "section_04_leadership": "Unsplash — Appolinary Kalishnikova (transmission lines / energy)",
            "cta": "Mitsidi public CMS (banner_expandir_corrigido.png) — Expandir event",
        },
    },
    "monte-jazmin": {
        "hero_image": "https://montejazmin.com/wp-content/uploads/2021/07/monte-jazmin.jpg",
        "section_bgs": [
            "https://montejazmin.com/wp-content/uploads/2021/07/cabana-1280x853.jpg",
            "https://montejazmin.com/wp-content/uploads/2021/07/coringa.jpg",
            "https://images.unsplash.com/photo-1442512595332-4457cc699a65?w=1200&q=80",
            "https://images.unsplash.com/photo-1464220885542-480007334a45?w=1200&q=80",
        ],
        "cta_image": "https://images.unsplash.com/photo-1511927071968-6c06b314579a?w=1200&q=80",
        "image_sources": {
            "hero": "Monte Jazmín verified website (monte-jazmin.jpg)",
            "section_01_problem": "Monte Jazmín verified website (cabana.jpg — rural lodging)",
            "section_02_solution": "Monte Jazmín verified website (coringa.jpg — farm/coffee)",
            "section_03_impact": "Unsplash — Nathan Dumlao (coffee harvest)",
            "section_04_leadership": "Unsplash — Rodrigo Flores (coffee plantation)",
            "cta": "Unsplash — Nathan Dumlao (specialty coffee cup)",
        },
    },
    "moviltronics": {
        "hero_image": "https://moviltronics.com/cdn/shop/files/M30062_0000_4.jpg",
        "section_bgs": [
            "https://moviltronics.com/cdn/shop/files/J50001_0000_2.jpg",
            "https://moviltronics.com/cdn/shop/files/M80015_0000_5.jpg",
            "https://moviltronics.com/cdn/shop/files/preview_images/29ce2302cc434f189362586f789d94d9.thumbnail.0000000000.jpg?v=1762372955&width=1200",
            "https://moviltronics.com/cdn/shop/files/M30062_0001_3.jpg",
        ],
        "cta_image": "https://moviltronics.com/cdn/shop/files/preview_images/b45aa806dcef4a71935e63b54d0be778.thumbnail.0000000000.jpg?v=1762376159&width=1200",
        "image_sources": {
            "hero": "Moviltronics verified storefront CDN (electric mobility product)",
            "section_01_problem": "Moviltronics verified storefront CDN (J50001 product photo)",
            "section_02_solution": "Moviltronics verified storefront CDN (M80015 product photo)",
            "section_03_impact": "Moviltronics verified storefront CDN (mobility category preview)",
            "section_04_leadership": "Moviltronics verified storefront CDN (M30062 product photo)",
            "cta": "Moviltronics verified storefront CDN (store preview image)",
        },
    },
    "myma": {
        "hero_image": "https://images.unsplash.com/photo-1542601906990-b4d66bb7bdd9?w=1200&q=80",
        "section_bgs": [
            "https://images.unsplash.com/photo-156916313939-4ac43dd3f8b8?w=1200&q=80",
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1200&q=80",
            "https://images.unsplash.com/photo-1416871960315-e1f36b8fcf59?w=1200&q=80",
            "https://images.unsplash.com/photo-1611273424745-0320e97a5a7e?w=1200&q=80",
        ],
        "cta_image": "https://images.unsplash.com/photo-1532996122724-e3c031a396bf?w=1200&q=80",
        "image_sources": {
            "hero": "Unsplash — Vladislav Klapin (urban green / environmental context)",
            "section_01_problem": "Unsplash — Johannes Plenio (forest / ecosystem)",
            "section_02_solution": "Unsplash — ThisIsEngineering (environmental engineering)",
            "section_03_impact": "Unsplash — Matthew Smith (water / watershed)",
            "section_04_leadership": "Unsplash — Karsten Würth (sustainability / nature stewardship)",
            "cta": "Unsplash — Liam Briese (air / atmosphere monitoring context)",
        },
    },
}


def main() -> None:
    all_urls: list[str] = []
    for spec in PAGES.values():
        all_urls.extend(
            [spec["hero_image"], *spec["section_bgs"], spec["cta_image"]]
        )
    if len(all_urls) != len(set(all_urls)):
        dupes = {u for u in all_urls if all_urls.count(u) > 1}
        raise SystemExit(f"Duplicate image URLs in batch: {dupes}")

    for slug in BATCH:
        path = DATA / f"{slug}.json"
        data = json.loads(path.read_text())
        spec = PAGES[slug]
        data["hero_image"] = spec["hero_image"]
        data["cta_image"] = spec["cta_image"]
        data["image_sources"] = spec["image_sources"]
        for i, sec in enumerate(data["sections"]):
            if "bg" in sec:
                sec["bg"] = spec["section_bgs"][i]
        credit_en = "Image credits: " + "; ".join(
            f"{k}: {v}" for k, v in spec["image_sources"].items()
        )
        credit_es = "Créditos de imagen: " + "; ".join(
            f"{k}: {v}" for k, v in spec["image_sources"].items()
        )
        if data["sections"][-1].get("dream_en"):
            data["sections"][-1]["dream_en"] += " " + credit_en
            data["sections"][-1]["dream_es"] += " " + credit_es
        else:
            data["sections"][-1]["dream_en"] = credit_en
            data["sections"][-1]["dream_es"] = credit_es
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print("patched", slug)


if __name__ == "__main__":
    main()
