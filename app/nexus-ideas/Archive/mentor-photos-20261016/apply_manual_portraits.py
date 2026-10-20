#!/usr/bin/env python3
"""Apply researched public portrait URLs (no unavatar/LinkedIn) for pending mentors."""
from __future__ import annotations

import csv
import html as html_lib
import importlib.util
import json
import subprocess
import urllib.parse
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "pm", Path(__file__).parent / "process_mentors.py"
)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

ARCHIVE = Path(__file__).parent

# mentor_id -> (source_label, image_url, evidence_page_url, crop_mode)
# crop_mode: square | left_third | wide_banner_center
PORTRAITS: dict[str, tuple[str, str, str, str]] = {
    "M002": (
        "valoraanalitik-reciclave-latam",
        "https://www.valoraanalitik.com/wp-content/uploads/2023/05/Reciclave-Latam.webp",
        "https://www.valoraanalitik.com/dia-del-reciclaje-el-reciclaje-sera-la-industria-del-futuro/",
        "square",
    ),
    "M029": (
        "elheraldo-organicos-del-caribe",
        "https://www.elheraldo.co/resizer/v2/UFUWHTZHF5D2BEAOXEXU77GIYY.jpg?smart=true&auth=0f9626cf4a5233f361a983ea1a9bc8a68fdfaedd9b8d33a609c758739afae6c1&width=1200&height=675",
        "https://www.elheraldo.co/mas-negocios/2019/11/20/organicos-del-caribe-innovara-generando-energia-con-residuos-681850/",
        "square",
    ),
    "M052": (
        "futurelab-team",
        "https://futurelab.com.co/wp-content/uploads/2020/09/IVAN-DAVILA-FUTURE-LAB-INNOVACION-1-360x360.jpg",
        "https://futurelab.com.co/nuestro-adn/",
        "square",
    ),
    "M059": (
        "ambrosetti-speaker",
        "https://eventi.ambrosetti.eu/scenarioprofessioni2024/wp-content/uploads/sites/264/2024/04/DEIDDA-GAGLIARDO-Jacopo-TS-2024-1009x1024.jpg",
        "https://eventi.ambrosetti.eu/scenarioprofessioni2024/speaker/jacopo-deidda-gagliardo/",
        "square",
    ),
    "M065": (
        "dementesbrillantes-expert",
        "https://dementesbrillantes.com.co/impulsatuequipo/wp-content/uploads/2025/01/julian.webp",
        "https://dementesbrillantes.com.co/impulsatuequipo/",
        "square",
    ),
    "M062": (
        "newswire-regeneau-team",
        "https://mmx.prnewswire.com/media/2701489/RegenEAU_RegenEAU_receives_support_from_Fondaction__Cycle_H2O__C.jpg",
        "https://www.newswire.ca/news-releases/regeneau-receives-support-from-fondaction-cycle-h2o-c3e-groupe-mcf-and-desjardins-to-advance-wastewater-heat-recovery-in-support-of-building-energy-efficiency-862285457.html",
        "left_third",
    ),
    "M069": (
        "microfinanzas-interview",
        "https://microfinanzas.pe/wp-content/uploads/2025/06/43.png",
        "https://microfinanzas.pe/mitchell-lazaro-diaz-el-peru-puede-construir-su-propio-nu-bank-pero-no-lo-hara-por-imitacion-sino-por-reinvencion/",
        "square",
    ),
    "M070": (
        "pbs-plana-docente",
        "https://pbs.edu.pe/images/c0b17997f45a44b1b0ec48b4cc736207.png",
        "https://pbs.edu.pe/plana-docente/",
        "square",
    ),
    "M073": (
        "puentecapital-trayectoria",
        "https://puentecapitalperu.com/wp-content/uploads/2026/07/Group-1000001830-e1783473638982.png",
        "https://puentecapitalperu.com/trayectoria/",
        "square",
    ),
}


def fetch_bytes_curl(url: str) -> bytes | None:
    url = html_lib.unescape(url)
    try:
        out = subprocess.check_output(
            ["curl", "-sL", "-A", "Mozilla/5.0 (compatible; CleantechHUB-Nexus/1.0)", url],
            timeout=60,
        )
        return out if len(out) >= 800 else None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def crop_mode(im, mode: str):
    from PIL import Image

    w, h = im.size
    if mode == "left_third":
        side = min(w // 3, h)
        return pm.crop_square(im.crop((0, max(0, (h - side) // 2), side, max(0, (h - side) // 2) + side)))
    if mode == "wide_banner_center":
        side = min(w // 2, h)
        left = (w - side) // 2
        top = (h - side) // 2
        return pm.crop_square(im.crop((left, top, left + side, top + side)))
    return pm.crop_square(im)


def main() -> None:
    rows = list(csv.DictReader((ARCHIVE / "mentors.csv").open(encoding="utf-8")))
    html = pm.HTML_PATH.read_text(encoding="utf-8")
    mentors = pm.parse_mentors(html)
    by_id = {m["id"]: m for m in mentors}
    by_name = {m["name"]: m for m in mentors}

    found_new = 0
    for mid, (label, url, page, crop) in PORTRAITS.items():
        m = by_id[mid]
        row = next(r for r in rows if r["name"] == m["name"])
        if row["status"] == "FOUND":
            continue
        data = pm.fetch_bytes(url) or fetch_bytes_curl(url)
        if not data or pm.is_likely_placeholder(data):
            print("FAIL", m["name"], url)
            continue
        import io
        from PIL import Image

        im = Image.open(io.BytesIO(data))
        im = crop_mode(im, crop)
        slug = pm.slugify(m["name"])
        local_rel = f"/nexus-assets/mentors/{slug}.jpg"
        local_path = pm.ASSETS / f"{slug}.jpg"
        pm.save_jpeg(im, local_path)
        (ARCHIVE / "originals" / f"{slug}.source").write_text(
            f"{label}\n{url}\n{page}\n", encoding="utf-8"
        )
        m["photo"] = local_rel
        row["status"] = "FOUND"
        row["photo_source_url"] = f"{label}:{page} -> {url}"
        row["local_asset_path"] = local_rel
        found_new += 1
        print("FOUND", m["name"], label)

    pm.HTML_PATH.write_text(pm.patch_render_card(pm.patch_html(html, mentors)), encoding="utf-8")
    with (ARCHIVE / "mentors.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    found = sum(1 for r in rows if r["status"] == "FOUND")
    pending = [r["name"] for r in rows if r["status"] == "PENDIENTE"]
    manifest = json.loads((ARCHIVE / "manifest.json").read_text(encoding="utf-8"))
    manifest["photos_found"] = found
    manifest["photos_pending"] = len(pending)
    manifest["second_pass_applied"] = sorted(PORTRAITS.keys())
    manifest["notes"] = (
        "Second pass: org/news/conference portraits only; no unavatar/LinkedIn. "
        f"Added {found_new} photos this run."
    )
    (ARCHIVE / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Total FOUND {found}/{len(rows)}; PENDIENTE {len(pending)}")
    for n in pending:
        print(" PENDIENTE:", n)


if __name__ == "__main__":
    main()
