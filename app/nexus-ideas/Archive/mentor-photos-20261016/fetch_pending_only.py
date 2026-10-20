#!/usr/bin/env python3
"""Fetch photos for mentors still missing local assets (fallbacks first, no HTML rewrite of descriptions)."""
import csv
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "pm", Path(__file__).parent / "process_mentors.py"
)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

ARCHIVE = Path(__file__).parent
rows = list(csv.DictReader((ARCHIVE / "mentors.csv").open(encoding="utf-8")))
html = pm.HTML_PATH.read_text(encoding="utf-8")
mentors = pm.parse_mentors(html)
by_name = {m["name"]: m for m in mentors}

for r in rows:
    if r["status"] == "FOUND":
        continue
    m = by_name[r["name"]]
    slug = pm.slugify(m["name"])
    local_rel = f"/nexus-assets/mentors/{slug}.jpg"
    local_path = pm.ASSETS / f"{slug}.jpg"
    for label, url in pm.photo_sources(m):
        if label == "unavatar-linkedin":
            continue  # skip while IP is rate-limited
        data = pm.fetch_bytes(url)
        if not data or pm.is_likely_placeholder(data):
            continue
        try:
            import io
            from PIL import Image

            im = pm.crop_square(Image.open(io.BytesIO(data)))
            pm.save_jpeg(im, local_path)
            m["photo"] = local_rel
            r["status"] = "FOUND"
            r["photo_source_url"] = f"{label}:{url}"
            r["local_asset_path"] = local_rel
            print("FOUND", m["name"], label)
            break
        except Exception as exc:
            print("ERR", m["name"], exc)

pm.HTML_PATH.write_text(pm.patch_render_card(pm.patch_html(html, mentors)), encoding="utf-8")
with (ARCHIVE / "mentors.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

found = sum(1 for r in rows if r["status"] == "FOUND")
print(f"Total FOUND {found}/{len(rows)}")
