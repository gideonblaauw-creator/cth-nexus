#!/usr/bin/env python3
"""Replace duplicate image URLs/files across the 62 sheet batch pages with unique Unsplash photos."""
from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "onepagers" / "data"
MEDIA = ROOT / "onepagers" / "media"
BUILDER = ROOT / "scripts" / "build_onepagers.py"

from check_onepager_image_uniqueness import BATCH_SLUGS, image_refs, resolve_local  # noqa: E402

import re  # noqa: E402

_PHOTO_RE = re.compile(r"photo-\d+-[0-9a-f]{8,}")


def _load_pool() -> list[tuple[str, str]]:
    ids: list[str] = []
    for path in (ROOT / "scripts").glob("*.py"):
        ids.extend(_PHOTO_RE.findall(path.read_text(errors="ignore")))
    for path in (ROOT / "onepagers" / "data").glob("*.json"):
        ids.extend(_PHOTO_RE.findall(path.read_text(errors="ignore")))
    seen: set[str] = set()
    pool: list[tuple[str, str]] = []
    for pid in ids:
        if pid in seen:
            continue
        seen.add(pid)
        pool.append((pid, "Unsplash contributor"))
    return pool


# Fallback if repo scan is empty.
POOL = _load_pool() or [
    ("photo-1470071459604-3b5ec3a7fe05", "Quino Al"),
    ("photo-1486406146926-c627a92ad1ab", "Victor"),
    ("photo-1497435334941-8f4e114e509e", "Johannes Plenio"),
    ("photo-1497436073146-47bd4214358c", "Andreas Gückl"),
    ("photo-1503327327322-56f962d3fc57", "CHUTTERSNAP"),
    ("photo-1504384308090-c894fdcc538d", "Marcos Paulo Prado"),
    ("photo-1508517748547-fbab89ddf9d9", "American Public Power Association"),
    ("photo-1517245386807-bb43f82c33c4", "Headway"),
    ("photo-1518173941573-c443e494106a", "Lucas Sankey"),
    ("photo-1518709268805-4e9042af2176", "Lukasz Szmigiel"),
    ("photo-1521737604893-d14cc237f11d", "Brooke Cagle"),
    ("photo-1532601220698-5029272cc54e", "CHUTTERSNAP"),
    ("photo-1542744173-8e7e53415bb0", "Campaign Creators"),
    ("photo-1548337138-4961de642fff", "CHUTTERSNAP"),
    ("photo-1553877522-43269d4ea984", "UX Indonesia"),
    ("photo-1556761175-5973dc0f32e7", "Kaleidico"),
    ("photo-1556742049-0cfed4f6a45d", "Clay Banks"),
    ("photo-1563452617894-61fc735e623f", "Daiga Ellaby"),
    ("photo-1578916171725-1653917a8149", "NeONBRAND"),
    ("photo-1581579186482-1f4a1a8a1f94", "No Revisions"),
    ("photo-1585421514734-121ea5978633", "Sarah Chai"),
    ("photo-1586201375761-83865001e26c", "Gilberto Olimpio"),
    ("photo-1600880292203-75762f0790e8", "Brooke Cagle"),
    ("photo-1604187351-d62eae8d5e72", "CHUTTERSNAP"),
    ("photo-1604719312566-8912caf2334a", "Nathan Dumlao"),
    ("photo-1610813673314-1a6a2a2649ea", "CHUTTERSNAP"),
    ("photo-1610832958506-aa56368197cf", "Micheile Henderson"),
    ("photo-1611273426858-450d7456a79a", "Li-An Lim"),
    ("photo-1612815167568-60f89d18be55", "Volodymyr Hryshchenko"),
    ("photo-1613665814317-58a502507d47", "American Public Power Association"),
    ("photo-1621905251189-08cb45d6a269", "CHUTTERSNAP"),
    ("photo-1628177142136-43d9810e5622", "Daian Gan"),
    ("photo-1628348714456-2889e6d6660e", "Towfiqu barbhuiya"),
    ("photo-1632829871091-68de131ce026", "KOBU Agency"),
    ("photo-1466611653911-950815379e64", "CHUTTERSNAP"),
]


def u(pid: str) -> str:
    return f"https://images.unsplash.com/{pid}?w=1200&q=80"


def collect_state() -> tuple[dict[str, list[str]], dict[str, list[tuple[str, str]]]]:
    url_map: dict[str, list[str]] = defaultdict(list)
    hash_map: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for slug in BATCH_SLUGS:
        data = json.loads((DATA / f"{slug}.json").read_text())
        for ref in image_refs(data):
            if ref.startswith(("http://", "https://")):
                url_map[ref].append(slug)
            else:
                local = resolve_local(slug, ref)
                if local:
                    digest = hashlib.sha256(local.read_bytes()).hexdigest()
                    hash_map[digest].append((slug, str(local)))
    return url_map, hash_map


def append_credit(data: dict, en: str, es: str) -> None:
    data["image_credits_en"] = (data.get("image_credits_en") or "") + " " + en
    data["image_credits_es"] = (data.get("image_credits_es") or "") + " " + es


def replace_in_data(data: dict, old: str, new: str, credit_name: str) -> bool:
    changed = False
    for key in ("hero_image", "cta_bg"):
        if data.get(key) == old:
            data[key] = new
            append_credit(
                data,
                f"Replacement photo: Unsplash — {credit_name}.",
                f"Foto de reemplazo: Unsplash — {credit_name}.",
            )
            changed = True
    for sec in data.get("sections") or []:
        if sec.get("bg") == old:
            sec["bg"] = new
            append_credit(
                data,
                f"Section photo: Unsplash — {credit_name}.",
                f"Foto de sección: Unsplash — {credit_name}.",
            )
            changed = True
    return changed


def download_local(slot_path: Path, url: str) -> None:
    slot_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "cth-nexus-image-fix/1.0"})
    slot_path.write_bytes(urllib.request.urlopen(req, timeout=60).read())


def main() -> None:
    global POOL
    POOL = _load_pool() or POOL
    pool_i = 0
    used_urls: set[str] = set()

    def next_url() -> tuple[str, str]:
        nonlocal pool_i
        while pool_i < len(POOL):
            pid, name = POOL[pool_i]
            pool_i += 1
            url = u(pid)
            if url not in used_urls:
                used_urls.add(url)
                return url, name
        raise SystemExit(f"Unsplash pool exhausted at {pool_i}/{len(POOL)}")

    # Seed used with all current URLs
    url_map, hash_map = collect_state()
    used_urls.update(url_map.keys())

    # Fix URL duplicates: keep first slug alphabetically, replace others
    for old_url, slugs in sorted(url_map.items(), key=lambda x: x[0]):
        uniq = sorted(set(slugs))
        if len(uniq) <= 1:
            continue
        for slug in uniq[1:]:
            new_url, name = next_url()
            path = DATA / f"{slug}.json"
            data = json.loads(path.read_text())
            if replace_in_data(data, old_url, new_url, name):
                path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
                print(f"URL {slug}: {old_url[:50]}… -> {new_url[:50]}…")

    # Fix local file hash duplicates across slugs
    url_map, hash_map = collect_state()
    for digest, items in hash_map.items():
        slugs = sorted({s for s, _ in items})
        if len(slugs) <= 1:
            continue
        for slug in slugs[1:]:
            new_url, name = next_url()
            path = DATA / f"{slug}.json"
            data = json.loads(path.read_text())
            for ref in image_refs(data):
                local = resolve_local(slug, ref)
                if local and hashlib.sha256(local.read_bytes()).hexdigest() == digest:
                    dest = MEDIA / slug / "assets" / local.name
                    for _ in range(5):
                        try:
                            download_local(dest, new_url)
                            break
                        except Exception:
                            new_url, name = next_url()
                    else:
                        raise RuntimeError(f"Could not download replacement for {slug}")
                    append_credit(
                        data,
                        f"Unique section asset: Unsplash — {name}.",
                        f"Activo único: Unsplash — {name}.",
                    )
                    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
                    print(f"FILE {slug}: replaced {local.name}")
                    break

    subprocess.run([sys.executable, str(BUILDER)], check=True, cwd=ROOT)


if __name__ == "__main__":
    import sys

    check = ROOT / "scripts" / "check_onepager_image_uniqueness.py"
    for attempt in range(12):
        print(f"--- dedupe pass {attempt + 1} ---")
        main()
        if subprocess.call([sys.executable, str(check)]) == 0:
            raise SystemExit(0)
    raise SystemExit(1)
