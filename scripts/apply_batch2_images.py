#!/usr/bin/env python3
"""Apply Nexus image protocol: unique contextual images + credits for batch 2."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "onepagers" / "data"

# Each URL used once across the whole batch (hero + 4 sections + CTA per slug).
IMAGE_PACKS: dict[str, dict] = {
    "alfe-aseo-sas": {
        "hero_image": "https://alfeaseo.com/wp-content/uploads/2026/05/Tarro-reutilizable-con-Pasaporte-Digital-Alfe-4.png",
        "cta_bg": "https://images.unsplash.com/photo-1585421514287-efb74e3441ba?w=1200&q=80",
        "section_bgs": [
            "https://images.unsplash.com/photo-1621619087653-83077a577e0a?w=1200&q=80",
            "https://alfeaseo.com/wp-content/uploads/2026/05/Pasaporte-digital-Tarro-760x1024.jpg",
            "https://alfeaseo.com/wp-content/uploads/2026/05/Pasaporte-digital-3-1.jpg",
            "https://images.unsplash.com/photo-1581578731546-35a1a4560d0c?w=1200&q=80",
        ],
        "image_credits": [
            {
                "slot_en": "Hero",
                "slot_es": "Hero",
                "credit_en": "Source: alfeaseo.com — reusable refill container (ALFE ASEO SAS).",
                "credit_es": "Fuente: alfeaseo.com — envase recargable reutilizable (ALFE ASEO SAS).",
                "link": "https://alfeaseo.com/",
            },
            {
                "slot_en": "01 Problem",
                "slot_es": "01 Problema",
                "credit_en": "Photo: Tanvi Malik on Unsplash — plastic packaging waste.",
                "credit_es": "Foto: Tanvi Malik en Unsplash — residuos de empaque plástico.",
                "link": "https://unsplash.com/photos/83077a577e0a",
            },
            {
                "slot_en": "02 Solution",
                "slot_es": "02 Solución",
                "credit_en": "Source: alfeaseo.com — digital passport refill jar.",
                "credit_es": "Fuente: alfeaseo.com — tarro de recarga con pasaporte digital.",
                "link": "https://alfeaseo.com/",
            },
            {
                "slot_en": "03 Impact",
                "slot_es": "03 Impacto",
                "credit_en": "Source: alfeaseo.com — refill program photography.",
                "credit_es": "Fuente: alfeaseo.com — fotografía del programa de recarga.",
                "link": "https://alfeaseo.com/",
            },
            {
                "slot_en": "04 Leadership",
                "slot_es": "04 Liderazgo",
                "credit_en": "Photo: National Cancer Institute on Unsplash — institutional cleaning context.",
                "credit_es": "Foto: National Cancer Institute en Unsplash — contexto de limpieza institucional.",
                "link": "https://unsplash.com/photos/35a1a4560d0c",
            },
            {
                "slot_en": "CTA",
                "slot_es": "CTA",
                "credit_en": "Photo: Daian Gan on Unsplash — cleaning products.",
                "credit_es": "Foto: Daian Gan en Unsplash — productos de limpieza.",
                "link": "https://unsplash.com/photos/efb74e3441ba",
            },
        ],
    },
    "baruk-company": {
        "hero_image": "https://images.unsplash.com/photo-1592982539628-fe2face54773?w=1200&q=80",
        "cta_bg": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1200&q=80",
        "section_bgs": [
            "https://images.unsplash.com/photo-1488525099488-039e66364da9?w=1200&q=80",
            "https://images.unsplash.com/photo-1530836360253-9b8a5c35990d?w=1200&q=80",
            "https://images.unsplash.com/photo-1605812860429-6028325c4de0?w=1200&q=80",
            "https://images.unsplash.com/photo-1466769199480-121684569904?w=1200&q=80",
        ],
        "image_credits": [
            {
                "slot_en": "Hero",
                "slot_es": "Hero",
                "credit_en": "Photo: Markus Spiske on Unsplash — greenhouse agriculture.",
                "credit_es": "Foto: Markus Spiske en Unsplash — agricultura en invernadero.",
                "link": "https://unsplash.com/photos/fe2face54773",
            },
            {
                "slot_en": "01 Problem",
                "slot_es": "01 Problema",
                "credit_en": "Photo: Luke Michael on Unsplash — food access / rural fields.",
                "credit_es": "Foto: Luke Michael en Unsplash — acceso a alimentos / campos rurales.",
                "link": "https://unsplash.com/photos/039e66364da9",
            },
            {
                "slot_en": "02 Solution",
                "slot_es": "02 Solución",
                "credit_en": "Photo: Jonathan Kemper on Unsplash — controlled greenhouse growing.",
                "credit_es": "Foto: Jonathan Kemper en Unsplash — cultivo en invernadero controlado.",
                "link": "https://unsplash.com/photos/9b8a5c35990d",
            },
            {
                "slot_en": "03 Impact",
                "slot_es": "03 Impacto",
                "credit_en": "Photo: CDC on Unsplash — seeds / food security symbolism.",
                "credit_es": "Foto: CDC en Unsplash — semillas / simbolismo de seguridad alimentaria.",
                "link": "https://unsplash.com/photos/6028325c4de0",
            },
            {
                "slot_en": "04 Leadership",
                "slot_es": "04 Liderazgo",
                "credit_en": "Photo: Zach Vessels on Unsplash — community agriculture.",
                "credit_es": "Foto: Zach Vessels en Unsplash — agricultura comunitaria.",
                "link": "https://unsplash.com/photos/121684569904",
            },
            {
                "slot_en": "CTA",
                "slot_es": "CTA",
                "credit_en": "Photo: American Public Power Association on Unsplash — solar energy for agri-infrastructure.",
                "credit_es": "Foto: American Public Power Association en Unsplash — energía solar para infraestructura agrícola.",
                "link": "https://unsplash.com/photos/2e959784a276",
            },
        ],
    },
    "bioarea": {
        "hero_image": "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=1200&q=80",
        "cta_bg": "https://images.unsplash.com/photo-1564013794819-865e1e26863e?w=1200&q=80",
        "section_bgs": [
            "https://images.unsplash.com/photo-1541888943317-e53d43a5a864?w=1200&q=80",
            "https://images.unsplash.com/photo-1489515217757-90fd23813740?w=1200&q=80",
            "https://images.unsplash.com/photo-1518005020951-eccb27870405?w=1200&q=80",
            "https://images.unsplash.com/photo-1581092160634-7713698ee3c2?w=1200&q=80",
        ],
        "image_credits": [
            {
                "slot_en": "Hero",
                "slot_es": "Hero",
                "credit_en": "Photo: Ricardo Gomez Angel on Unsplash — sustainable architecture sketch.",
                "credit_es": "Foto: Ricardo Gomez Angel en Unsplash — boceto de arquitectura sostenible.",
                "link": "https://unsplash.com/photos/592deb58ef4e",
            },
            {
                "slot_en": "01 Problem",
                "slot_es": "01 Problema",
                "credit_en": "Photo: CHUTTERSNAP on Unsplash — construction site footprint.",
                "credit_es": "Foto: CHUTTERSNAP en Unsplash — huella de obra de construcción.",
                "link": "https://unsplash.com/photos/e53d43a5a864",
            },
            {
                "slot_en": "02 Solution",
                "slot_es": "02 Solución",
                "credit_en": "Photo: Joel Filipe on Unsplash — reclaimed wood / circular materials.",
                "credit_es": "Foto: Joel Filipe en Unsplash — madera recuperada / materiales circulares.",
                "link": "https://unsplash.com/photos/90fd23813740",
            },
            {
                "slot_en": "03 Impact",
                "slot_es": "03 Impacto",
                "credit_en": "Photo: Biel Morro on Unsplash — green building facade.",
                "credit_es": "Foto: Biel Morro en Unsplash — fachada de edificio verde.",
                "link": "https://unsplash.com/photos/eccb27870405",
            },
            {
                "slot_en": "04 Leadership",
                "slot_es": "04 Liderazgo",
                "credit_en": "Photo: ThisisEngineering RAEng on Unsplash — design/engineering workspace.",
                "credit_es": "Foto: ThisisEngineering RAEng en Unsplash — espacio de diseño/ingeniería.",
                "link": "https://unsplash.com/photos/7713698ee3c2",
            },
            {
                "slot_en": "CTA",
                "slot_es": "CTA",
                "credit_en": "Photo: Biel Morro on Unsplash — eco residential exterior.",
                "credit_es": "Foto: Biel Morro en Unsplash — exterior residencial ecológico.",
                "link": "https://unsplash.com/photos/865e1e26863e",
            },
        ],
    },
    "calojabones": {
        "hero_image": "https://somostorna.com/wp-content/uploads/2023/10/DSC_0173-2-2.jpg",
        "cta_bg": "https://images.unsplash.com/photo-1611270629569-7a308123172c?w=1200&q=80",
        "section_bgs": [
            "https://images.unsplash.com/photo-1550946843-6037f2de3a96?w=1200&q=80",
            "https://somostorna.com/wp-content/uploads/2023/10/jabon-liquido-empresas.jpg",
            "https://somostorna.com/wp-content/uploads/2023/10/hogar-productos-sostenibles.jpg",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1200&q=80",
        ],
        "image_credits": [
            {
                "slot_en": "Hero",
                "slot_es": "Hero",
                "credit_en": "Source: somostorna.com — Calo Jabones / Torna production (verified public brand site).",
                "credit_es": "Fuente: somostorna.com — producción Calo Jabones / Torna (sitio público verificado).",
                "link": "https://somostorna.com/nosotros/",
            },
            {
                "slot_en": "01 Problem",
                "slot_es": "01 Problema",
                "credit_en": "Photo: CHUTTERSNAP on Unsplash — used cooking oil / kitchen waste context.",
                "credit_es": "Foto: CHUTTERSNAP en Unsplash — aceite de cocina usado / residuo de cocina.",
                "link": "https://unsplash.com/photos/6037f2de3a96",
            },
            {
                "slot_en": "02 Solution",
                "slot_es": "02 Solución",
                "credit_en": "Source: somostorna.com — industrial biodegradable cleaning line.",
                "credit_es": "Fuente: somostorna.com — línea de limpieza biodegradable industrial.",
                "link": "https://somostorna.com/",
            },
            {
                "slot_en": "03 Impact",
                "slot_es": "03 Impacto",
                "credit_en": "Source: somostorna.com — household sustainable cleaning products.",
                "credit_es": "Fuente: somostorna.com — productos de limpieza sostenibles para hogar.",
                "link": "https://somostorna.com/",
            },
            {
                "slot_en": "04 Leadership",
                "slot_es": "04 Liderazgo",
                "credit_en": "Photo: Kate Trifo on Unsplash — collaborative team / community work.",
                "credit_es": "Foto: Kate Trifo en Unsplash — equipo colaborativo / trabajo comunitario.",
                "link": "https://unsplash.com/photos/1cb2f99b2d8b",
            },
            {
                "slot_en": "CTA",
                "slot_es": "CTA",
                "credit_en": "Photo: Curology on Unsplash — natural soap bars.",
                "credit_es": "Foto: Curology en Unsplash — jabones naturales en barra.",
                "link": "https://unsplash.com/photos/7a308123172c",
            },
        ],
    },
}


def main() -> None:
    used: set[str] = set()
    for slug, pack in IMAGE_PACKS.items():
        path = DATA / f"{slug}.json"
        data = json.loads(path.read_text())
        urls = [pack["hero_image"], pack["cta_bg"], *pack["section_bgs"]]
        for u in urls:
            if u in used:
                raise SystemExit(f"Duplicate image across batch: {u} ({slug})")
            used.add(u)
        data["hero_image"] = pack["hero_image"]
        data["cta_bg"] = pack["cta_bg"]
        data["image_credits"] = pack["image_credits"]
        for sec, bg in zip(data["sections"], pack["section_bgs"], strict=True):
            sec["bg"] = bg
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"Updated {slug} ({len(urls)} unique images)")


if __name__ == "__main__":
    main()
