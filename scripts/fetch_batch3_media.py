#!/usr/bin/env python3
"""Download verified public images for batch-3 onepagers into onepagers/media/{slug}/assets/."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "onepagers" / "media"
DATA = ROOT / "onepagers" / "data"

DOWNLOADS: dict[str, dict[str, str]] = {
    "greenify": {
        "hero.webp": "https://greenify.world/images/impacto-real/460x996bb.webp",
        "problem.png": "https://greenify.world/images/counter/Billboard%20Wall.png",
    },
    "habitat-a-vibe-company": {
        "hero.webp": "https://habitatmineriaurbana.com.co/wp-content/uploads/2025/02/Portada4.webp",
        "problem.jpg": "https://habitatmineriaurbana.com.co/wp-content/uploads/2026/10/BANNER_MINERALES.jpg.jpeg",
        "solution.jpg": "https://habitatmineriaurbana.com.co/wp-content/uploads/2026/08/BANNER-HABITAT_CRONOGRAMA_R-RECOLECCION.jpg.jpeg",
        "impact.webp": "https://habitatmineriaurbana.com.co/wp-content/uploads/2025/10/Portada-1-1-2025.webp",
    },
    "ciclorganicos": {
        "hero.webp": "https://www.ciclorganicos.com/img/hero-compost.webp",
    },
    "cobox-logistic": {
        "hero.webp": "https://storage.googleapis.com/gpt-engineer-file-uploads/m2YOydJavYZaG7cJZ2pbNjutXKR2/social-images/social-1774560380026-CBX_Linkedin.webp",
    },
}

# Verified 200 URLs; each photo used at most once across batch 3.
UNSPLASH: dict[str, dict[str, tuple[str, str]]] = {
    "greenify": {
        "solution": (
            "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200&q=80",
            "Unsplash — Johannes Plenio (forest / carbon stewardship)",
        ),
        "impact": (
            "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80",
            "Unsplash — Campaign Creators (sustainability reporting)",
        ),
        "team": (
            "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80",
            "Unsplash — Jason Goodman (team collaboration)",
        ),
        "cta": (
            "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80",
            "Unsplash — Annie Spratt (canopy / offsets)",
        ),
    },
    "habitat-a-vibe-company": {
        "team": (
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80",
            "Unsplash — Possessed Photography (electronics recycling)",
        ),
        "cta": (
            "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200&q=80",
            "Unsplash — LinkedIn Sales Navigator (circular industry)",
        ),
    },
    "ciclorganicos": {
        "problem": (
            "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80",
            "Unsplash — Zoe Schaeffer (agriculture / food supply)",
        ),
        "solution": (
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80",
            "Unsplash — Geran de Klerk (farmland / soil inputs)",
        ),
        "impact": (
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80",
            "Unsplash — Carlos Muza (agricultural productivity / data)",
        ),
        "team": (
            "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1200&q=80",
            "Unsplash — ThisIsEngineering (composting / industrial biology)",
        ),
        "cta": (
            "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1200&q=80",
            "Unsplash — Ben Duchac (community / field team)",
        ),
    },
    "cobox-logistic": {
        "problem": (
            "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1200&q=80",
            "Unsplash — CHUTTERSNAP (warehouse / SME logistics)",
        ),
        "solution": (
            "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=1200&q=80",
            "Unsplash — Markus Winkler (parcel handling)",
        ),
        "impact": (
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",
            "Unsplash — NASA (logistics technology / visibility)",
        ),
        "team": (
            "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=1200&q=80",
            "Unsplash — CHUTTERSNAP (delivery fleet)",
        ),
        "cta": (
            "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200&q=80",
            "Unsplash — Scott Webb (freight corridor)",
        ),
    },
}

LOCAL_CREDITS: dict[str, dict[str, str]] = {
    "greenify": {
        "hero": "greenify.world — /images/impacto-real/460x996bb.webp",
        "problem": "greenify.world — /images/counter/Billboard Wall.png",
    },
    "habitat-a-vibe-company": {
        "hero": "habitatmineriaurbana.com.co — Portada4.webp (2025-02)",
        "problem": "habitatmineriaurbana.com.co — BANNER_MINERALES (2026-10)",
        "solution": "habitatmineriaurbana.com.co — RAEE collection banner (2026-08)",
        "impact": "habitatmineriaurbana.com.co — Portada-1-1-2025.webp",
    },
    "ciclorganicos": {
        "hero": "ciclorganicos.com — /img/hero-compost.webp",
    },
    "cobox-logistic": {
        "hero": "coboxlogistic.com — social/LinkedIn preview (Google Cloud CDN)",
    },
}


def curl_download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-fsSL", url, "-o", str(dest)], check=True, timeout=120)


def apply_json(slug: str, mapping: dict[str, str], credits: dict[str, str]) -> None:
    path = DATA / f"{slug}.json"
    data = json.loads(path.read_text())
    data["hero_image"] = mapping["hero"]
    sections = data["sections"]
    sections[0]["bg"] = mapping["problem"]
    sections[1]["bg"] = mapping["solution"]
    sections[2]["bg"] = mapping["impact"]
    sections[3]["bg"] = mapping["team"]
    data["image_credits"] = credits
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    for slug, files in DOWNLOADS.items():
        assets = MEDIA / slug / "assets"
        for fname, url in files.items():
            curl_download(url, assets / fname)
            print("downloaded", slug, fname)

    for slug in DOWNLOADS:
        assets = MEDIA / slug / "assets"
        mapping: dict[str, str] = {}
        credits = dict(LOCAL_CREDITS.get(slug, {}))

        for slot, fname in {
            "hero": "hero.webp",
            "problem": next((f for f in ("problem.png", "problem.jpg") if (assets / f).exists()), None),
            "solution": "solution.jpg" if (assets / "solution.jpg").exists() else None,
            "impact": "impact.webp" if (assets / "impact.webp").exists() else None,
        }.items():
            if slot == "hero" and (assets / "hero.webp").exists():
                mapping["hero"] = "./assets/hero.webp"
            elif fname and (assets / fname).exists():
                mapping[slot] = f"./assets/{fname}"

        for slot, (url, credit) in UNSPLASH.get(slug, {}).items():
            dest = assets / f"{slot}.jpg"
            curl_download(url, dest)
            mapping[slot] = f"./assets/{slot}.jpg"
            credits[slot] = credit
            if slot == "cta":
                curl_download(url, assets / "bg-cta.jpg")

        for slot in ("problem", "solution", "impact", "team", "hero"):
            if slot not in mapping:
                raise SystemExit(f"missing image slot {slot} for {slug}")

        apply_json(slug, mapping, credits)
        print("updated", slug)


if __name__ == "__main__":
    main()
