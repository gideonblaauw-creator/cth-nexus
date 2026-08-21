#!/usr/bin/env python3
"""Extract deck PDF assets (backgrounds, team photos) into onepagers/media/{slug}/."""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
MEDIA = ROOT / "onepagers" / "media"
DECK_SOURCE = Path("/opt/claude-files/Projects/Nexus/startup-decks-2026-08-20")
EXTRACT = Path("/tmp/nexus-extract")
SLIDES = Path("/tmp/nexus-slides")

DECK_META = {
    "terra-io": {
        "pdf": "TERRA-IO.pdf",
        "drive_id": "1_JDyQhLmOxrIME9xaBMmLO11XUWIWNJp",
    },
    "green-t": {
        "pdf": "Green-T.pdf",
        "drive_id": "1jmE9tfyYxhaBqlMuT-SWdyL8agxRMUiX",
    },
    "communitylab": {
        "pdf": "CommunityLab.pdf",
        "drive_id": "1iUp6rSR907RR6zseUXh2jvnC_bpUdxQQ",
    },
    "bio-analytics": {
        "pdf": "Bio-analytics.pdf",
        "drive_id": "1Y0_NkNeJpGddCrXNT0quidcFe34E9Pa2",
    },
    "cacelio": {
        "pdf": "Cacelio.pdf",
        "drive_id": "10kg4_s7_y-hAZcdZR2AHPd47sm5kToNx",
    },
}


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-").split("-")[0] if s else "member"


def save_img(src: Path, dest: Path, quality: int = 88) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im.convert("RGB").save(dest, "JPEG", quality=quality, optimize=True)


def copy_as_jpg(src: Path, dest: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    save_img(src, dest)


def crop_region(slide: Path, dest: Path, box: tuple[float, float, float, float]) -> None:
    with Image.open(slide) as im:
        im = im.convert("RGB")
        w, h = im.size
        x0, y0, x1, y1 = box
        crop = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
        dest.parent.mkdir(parents=True, exist_ok=True)
        crop.save(dest, "JPEG", quality=88, optimize=True)


def crop_team_row(
    slide: Path,
    dest_dir: Path,
    names: list[str],
    y0: float = 0.11,
    y1: float = 0.43,
    x_pad: float = 0.12,
) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(slide) as im:
        im = im.convert("RGB")
        w, h = im.size
        top, bottom = int(h * y0), int(h * y1)
        col_w = w / len(names)
        for i, name in enumerate(names):
            x0 = int(i * col_w + col_w * x_pad)
            x1 = int((i + 1) * col_w - col_w * x_pad)
            out = dest_dir / f"{slugify(name)}.jpg"
            im.crop((x0, top, x1, bottom)).save(out, "JPEG", quality=88, optimize=True)


def pick_extract(slug: str, filename: str) -> Path:
    p = EXTRACT / slug / filename
    if not p.exists():
        raise FileNotFoundError(f"Missing extracted image: {p}")
    return p


def setup_terra_io(assets: Path) -> None:
    copy_as_jpg(pick_extract("terra-io", "img-000.jp2"), assets / "hero.jpg")
    for name in (
        "bg-problem",
        "bg-pricing",
        "bg-table",
        "bg-market",
        "bg-impact",
        "bg-team",
        "bg-deck",
        "bg-cta",
    ):
        src_name = {
            "bg-problem": "img-003.jp2",
            "bg-pricing": "img-034.jp2",
            "bg-table": "img-052.jp2",
            "bg-market": "img-090.jp2",
            "bg-impact": "img-092.jp2",
            "bg-team": "img-094.jp2",
            "bg-deck": "img-000.jp2",
            "bg-cta": "img-000.jp2",
        }[name]
        copy_as_jpg(pick_extract("terra-io", src_name), assets / f"{name}.jpg")
    crop_team_row(
        SLIDES / "terra-io" / "page-9.jpg",
        assets / "team",
        [
            "David Mastrascusa",
            "Nora Torres",
            "Adriana Buelvas",
            "Natalia Navarrete",
            "Camilo Nauffal",
        ],
    )


def setup_green_t(assets: Path) -> None:
    copy_as_jpg(pick_extract("green-t", "img-004.jpg"), assets / "hero.jpg")
    slide = SLIDES / "green-t" / "page-04.jpg"
    crop_region(slide, assets / "bg-problem.jpg", (0.0, 0.35, 0.45, 1.0))
    crop_region(SLIDES / "green-t" / "page-03.jpg", assets / "bg-solution.jpg", (0.55, 0.15, 1.0, 0.75))
    crop_region(SLIDES / "green-t" / "page-05.jpg", assets / "bg-market.jpg", (0.0, 0.4, 1.0, 1.0))
    crop_region(SLIDES / "green-t" / "page-06.jpg", assets / "bg-table.jpg", (0.0, 0.0, 0.5, 1.0))
    crop_region(SLIDES / "green-t" / "page-07.jpg", assets / "bg-impact.jpg", (0.0, 0.35, 1.0, 1.0))
    copy_as_jpg(pick_extract("green-t", "img-004.jpg"), assets / "bg-team.jpg")
    copy_as_jpg(pick_extract("green-t", "img-004.jpg"), assets / "bg-deck.jpg")
    copy_as_jpg(pick_extract("green-t", "img-004.jpg"), assets / "bg-cta.jpg")
    crop_team_row(
        SLIDES / "green-t" / "page-09.jpg",
        assets / "team",
        ["Jorge Velásquez", "Johan David Moreno", "Mauricio Velasquez Sierra"],
        y0=0.16,
        y1=0.56,
        x_pad=0.08,
    )


def setup_communitylab(assets: Path) -> None:
    copy_as_jpg(pick_extract("communitylab", "img-000.png"), assets / "hero.jpg")
    copy_as_jpg(pick_extract("communitylab", "img-115.jpg"), assets / "bg-problem.jpg")
    copy_as_jpg(pick_extract("communitylab", "img-115.jpg"), assets / "bg-solution.jpg")
    crop_region(SLIDES / "communitylab" / "page-3.jpg", assets / "bg-market.jpg", (0.0, 0.35, 1.0, 1.0))
    crop_region(SLIDES / "communitylab" / "page-1.jpg", assets / "bg-table.jpg", (0.35, 0.0, 1.0, 1.0))
    copy_as_jpg(pick_extract("communitylab", "img-115.jpg"), assets / "bg-impact.jpg")
    copy_as_jpg(pick_extract("communitylab", "img-000.png"), assets / "bg-team.jpg")
    copy_as_jpg(pick_extract("communitylab", "img-000.png"), assets / "bg-deck.jpg")
    copy_as_jpg(pick_extract("communitylab", "img-000.png"), assets / "bg-cta.jpg")
    crop_team_row(
        SLIDES / "communitylab" / "page-9.jpg",
        assets / "team",
        [
            "Beatriz Eugenia Correa Pérez",
            "Manuela Cardenas",
            "Alfredo José Roldán Piedrahita",
            "Felipe Hernandez",
        ],
        y0=0.10,
        y1=0.38,
        x_pad=0.10,
    )


def setup_bio_analytics(assets: Path) -> None:
    copy_as_jpg(pick_extract("bio-analytics", "img-006.png"), assets / "hero.jpg")
    copy_as_jpg(pick_extract("bio-analytics", "img-002.png"), assets / "bg-problem.jpg")
    copy_as_jpg(pick_extract("bio-analytics", "img-006.png"), assets / "bg-solution.jpg")
    copy_as_jpg(pick_extract("bio-analytics", "img-002.png"), assets / "bg-market.jpg")
    copy_as_jpg(pick_extract("bio-analytics", "img-002.png"), assets / "bg-table.jpg")
    copy_as_jpg(pick_extract("bio-analytics", "img-006.png"), assets / "bg-impact.jpg")
    copy_as_jpg(pick_extract("bio-analytics", "img-006.png"), assets / "bg-team.jpg")
    copy_as_jpg(pick_extract("bio-analytics", "img-006.png"), assets / "bg-deck.jpg")
    copy_as_jpg(pick_extract("bio-analytics", "img-006.png"), assets / "bg-cta.jpg")
    # Team slide is a tall PNG — crop four portraits from top row
    with Image.open(pick_extract("bio-analytics", "img-004.png")) as im:
        im = im.convert("RGB")
        w, h = im.size
        names = [
            "Diego Gómez Morales",
            "Sofía Medellín Becerra",
            "Natalia Ramirez Ortiz",
            "Daniel Gómez Morales",
        ]
        col_w = w / 5
        top, bottom = int(h * 0.08), int(h * 0.42)
        idx_map = [0, 1, 2, 4]  # skip Patricia (index 3) to match JSON roster
        for name, idx in zip(names, idx_map):
            x0 = int(idx * col_w + col_w * 0.08)
            x1 = int((idx + 1) * col_w - col_w * 0.08)
            out = assets / "team" / f"{slugify(name)}.jpg"
            out.parent.mkdir(parents=True, exist_ok=True)
            im.crop((x0, top, x1, bottom)).save(out, "JPEG", quality=88, optimize=True)


def setup_cacelio(assets: Path) -> None:
    crop_region(SLIDES / "cacelio" / "page-01.jpg", assets / "hero.jpg", (0.45, 0.0, 1.0, 1.0))
    crop_region(SLIDES / "cacelio" / "page-02.jpg", assets / "bg-problem.jpg", (0.55, 0.0, 1.0, 1.0))
    crop_region(SLIDES / "cacelio" / "page-02.jpg", assets / "bg-solution.jpg", (0.0, 0.0, 0.45, 1.0))
    crop_region(SLIDES / "cacelio" / "page-03.jpg", assets / "bg-market.jpg", (0.0, 0.3, 1.0, 1.0))
    crop_region(SLIDES / "cacelio" / "page-04.jpg", assets / "bg-table.jpg", (0.0, 0.25, 1.0, 1.0))
    crop_region(SLIDES / "cacelio" / "page-08.jpg", assets / "bg-impact.jpg", (0.0, 0.0, 1.0, 0.55))
    crop_region(SLIDES / "cacelio" / "page-10.jpg", assets / "bg-team.jpg", (0.0, 0.0, 1.0, 0.75))
    copy_as_jpg(pick_extract("cacelio", "img-011.png"), assets / "bg-deck.jpg")
    crop_region(SLIDES / "cacelio" / "page-10.jpg", assets / "bg-cta.jpg", (0.0, 0.0, 1.0, 0.75))
    crop_team_row(
        SLIDES / "cacelio" / "page-09.jpg",
        assets / "team",
        ["David Sánchez Nielsen", "Sebastian Camilo Acosta"],
        y0=0.12,
        y1=0.42,
        x_pad=0.18,
    )


SETUP = {
    "terra-io": setup_terra_io,
    "green-t": setup_green_t,
    "communitylab": setup_communitylab,
    "bio-analytics": setup_bio_analytics,
    "cacelio": setup_cacelio,
}


def patch_json(slug: str) -> None:
    data_path = ROOT / "onepagers" / "data" / f"{slug}.json"
    data = json.loads(data_path.read_text())
    meta = DECK_META[slug]
    pdf_name = meta["pdf"]
    drive_id = meta["drive_id"]
    data["deck_pdf"] = {
        "drive_id": drive_id,
        "view_url": f"https://drive.google.com/file/d/{drive_id}/view",
        "embed_url": f"https://drive.google.com/file/d/{drive_id}/preview",
        "pdf_path": f"/s/{slug}/deck.pdf",
        "source_file": pdf_name,
        "bg": "./assets/bg-deck.jpg",
    }
    data["hero_image"] = "./assets/hero.jpg"
    bg_map = {
        "split": "bg-problem",
        "solution": "bg-solution",
        "sliders": "bg-pricing",
        "chart": "bg-market",
        "table": "bg-table",
        "impact": "bg-impact",
        "team": "bg-team",
    }
    for sec in data.get("sections", []):
        st = sec.get("type")
        if st in bg_map:
            sec["bg"] = f"./assets/{bg_map[st]}.jpg"
        elif st == "sliders" and slug == "terra-io":
            sec["bg"] = "./assets/bg-pricing.jpg"
        overlay = sec.get("overlay", "")
        if ".93)" in overlay or ".91)" in overlay:
            sec["overlay"] = overlay.replace(".93)", ".30)").replace(".91)", ".30)")
    for member in _iter_team(data):
        key = slugify(member["name"])
        photo = f"./assets/team/{key}.jpg"
        member["photo"] = photo
        member.pop("initials", None)
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def _iter_team(data: dict):
    for sec in data.get("sections", []):
        if sec.get("type") == "team":
            for m in sec.get("members", []):
                yield m


def main(argv: list[str]) -> int:
    slugs = argv or list(SETUP.keys())
    for slug in slugs:
        if slug not in SETUP:
            print(f"Unknown slug: {slug}", file=sys.stderr)
            return 1
        out = MEDIA / slug
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        print(f"Setting up media for {slug}...")
        SETUP[slug](out)
        patch_json(slug)
        print(f"  media -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
