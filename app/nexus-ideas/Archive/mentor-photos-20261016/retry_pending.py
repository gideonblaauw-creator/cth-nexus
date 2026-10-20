#!/usr/bin/env python3
"""Retry photo fetch for mentors still PENDIENTE; merge into index.html and mentors.csv."""
import csv
import importlib.util
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "pm", Path(__file__).parent / "process_mentors.py"
)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

ARCHIVE = Path(__file__).parent
csv_path = ARCHIVE / "mentors.csv"
rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
pending_names = {r["name"] for r in rows if r["status"] == "PENDIENTE"}

html = pm.HTML_PATH.read_text(encoding="utf-8")
mentors = pm.parse_mentors(html)
descriptions = pm.load_descriptions()

by_name = {m["name"]: m for m in mentors}
found = 0

for i, name in enumerate(sorted(pending_names)):
    m = by_name[name]
    slug = pm.slugify(m["name"])
    local_rel = f"/nexus-assets/mentors/{slug}.jpg"
    local_path = pm.ASSETS / f"{slug}.jpg"
    photo_source = ""
    status = "PENDIENTE"

    for label, url in pm.photo_sources(m):
        time.sleep(5.5)
        data = pm.fetch_bytes(url)
        if not data or pm.is_likely_placeholder(data):
            continue
        try:
            import io
            from PIL import Image

            im = Image.open(io.BytesIO(data))
            im = pm.crop_square(im)
            pm.save_jpeg(im, local_path)
            photo_source = f"{label}:{url}"
            status = "FOUND"
            m["photo"] = local_rel
            found += 1
            print(f"FOUND {name}")
            break
        except Exception as exc:
            print(f"fail {name} {label}: {exc}")

    if status == "PENDIENTE":
        m["photo"] = ""

    for r in rows:
        if r["name"] == name:
            r["photo_source_url"] = photo_source
            r["local_asset_path"] = local_rel if status == "FOUND" else ""
            r["status"] = status
            break

new_desc = descriptions.get(m["id"], "").strip()
if new_desc:
    m["desc"] = new_desc

pm.HTML_PATH.write_text(pm.patch_render_card(pm.patch_html(html, mentors)), encoding="utf-8")

with csv_path.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

total_found = sum(1 for r in rows if r["status"] == "FOUND")
print(f"Retry found {found}; total FOUND {total_found}/{len(rows)}")
