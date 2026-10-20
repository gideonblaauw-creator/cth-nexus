#!/usr/bin/env python3
"""Assert no image URL or local asset bytes repeat across sheet batch /s/ pages."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "onepagers" / "data"

BATCH_SLUGS = """
b-kapz elastic-energy mubon novatio plasticos-ambientales ainwater air4u suncolombia weia zhana-solutions
alfe-aseo-sas baruk-company bioarea calojabones ciclorganicos cobox-logistic greenify habitat-a-vibe-company
ala-terra compostpack cr-tejas deposito-global-recycling deterquin dexon-software-sas-bic eco-biosis eco-industria
embergy fluvia galaxy-pack glooba glu-energy griin-energy grupo-natural-andino greendex hunter-tecnologia i-can-jump
ilikko isd-ingenieria-y-servicios istmo-verde kigui kimsa kleantab linko-workers mayugo mitsidi monte-jazmin
moviltronics myma nina-energy nuevas-tecnologias-fisicoquimicas oasis-group pacaceite parsons-kinetics kelab plasfacol
pleia purest-fuels simbiotic tavi-technology tr-global-group valopes wheelo
""".split()


def image_refs(data: dict) -> list[str]:
    refs: list[str] = []
    for key in ("hero_image", "cta_bg"):
        if data.get(key):
            refs.append(str(data[key]))
    for sec in data.get("sections") or []:
        if sec.get("bg"):
            refs.append(str(sec["bg"]))
    for m in data.get("team") or []:
        if m.get("photo"):
            refs.append(str(m["photo"]))
    deck = data.get("deck_pdf") or {}
    if deck.get("bg"):
        refs.append(str(deck["bg"]))
    return refs


def resolve_local(slug: str, ref: str) -> Path | None:
    if ref.startswith(("http://", "https://", "/")):
        return None
    rel = ref.removeprefix("./")
    candidates = [
        ROOT / "onepagers" / "media" / slug / rel,
        ROOT / "onepagers" / "media" / slug / "assets" / Path(rel).name,
        ROOT / "onepagers" / "sites" / slug / rel,
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def main() -> int:
    url_map: dict[str, list[str]] = defaultdict(list)
    hash_map: dict[str, list[tuple[str, str]]] = defaultdict(list)
    missing: list[tuple[str, str]] = []

    for slug in BATCH_SLUGS:
        path = DATA / f"{slug}.json"
        if not path.is_file():
            print(f"MISSING JSON: {slug}", file=sys.stderr)
            return 1
        data = json.loads(path.read_text())
        for ref in image_refs(data):
            if ref.startswith(("http://", "https://")):
                url_map[ref].append(slug)
            else:
                local = resolve_local(slug, ref)
                if not local:
                    missing.append((slug, ref))
                    continue
                digest = hashlib.sha256(local.read_bytes()).hexdigest()
                hash_map[digest].append((slug, str(local)))

    url_dupes = {u: slugs for u, slugs in url_map.items() if len(set(slugs)) > 1}
    hash_dupes = {
        h: items for h, items in hash_map.items() if len({s for s, _ in items}) > 1
    }

    if missing:
        print("Missing local assets (may be URL-only pages):", len(missing))
        for slug, ref in missing[:10]:
            print(f"  {slug}: {ref}")

    if url_dupes:
        print(f"FAIL: {len(url_dupes)} duplicate image URLs across slugs")
        for u, slugs in sorted(url_dupes.items(), key=lambda x: -len(x[1]))[:30]:
            print(f"  {sorted(set(slugs))}: {u[:90]}")

    if hash_dupes:
        print(f"FAIL: {len(hash_dupes)} duplicate local file hashes across slugs")
        for h, items in sorted(hash_dupes.items(), key=lambda x: -len(x[1])):
            slugs = sorted({s for s, _ in items})
            print(f"  {slugs}: {items[0][1]}")

    if url_dupes or hash_dupes:
        return 1
    print(f"OK: {len(BATCH_SLUGS)} slugs, all image URLs and local assets unique across pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
