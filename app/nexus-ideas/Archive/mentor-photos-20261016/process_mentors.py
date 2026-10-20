#!/usr/bin/env python3
"""Fetch mentor photos, write assets, patch index.html, emit mentors.csv."""
from __future__ import annotations

import csv
import io
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ARCHIVE = Path("/opt/nexus-idea-browser/Archive/mentor-photos-20261016")
ASSETS = Path("/var/www/nexus-assets/mentors")
HTML_PATH = Path("/opt/cth-nexus/static/mentor-directory/index.html")

UA = "Mozilla/5.0 (compatible; CleantechHUB-Nexus/1.0; +https://nexus.cleantechhub.net)"

FALLBACK_PHOTO_URLS: dict[str, list[tuple[str, str]]] = {
    "M028": [
        (
            "torre-profile",
            "https://res.cloudinary.com/torre-technologies-co/image/upload/v0/origin/starrgate/users/profile_9c482a9afdb77e5a00c21e29280f67f3276a2784.jpg",
        )
    ],
    "M032": [
        (
            "idb-invest",
            "https://idbinvest.org/sites/default/files/member/2022/06/Luc%20Lapointe.jpg",
        )
    ],
    "M057": [
        (
            "kimsa-team",
            "https://static.wixstatic.com/media/9d6db3_412920b86db94199b261006cd4c50aad~mv2.jpg/v1/fill/w_800,h_800,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/Vv%20(2)_edited_edited.jpg",
        )
    ],
    "M061": [
        (
            "prparatodos-site",
            "https://prparatodos.com/wp-content/uploads/2023/09/foto-andrea-banner-ppal-pr-paratodos-650b549030106.webp",
        )
    ],
    "M038": [
        (
            "sched-speaker",
            "https://avatars.sched.co/7/e4/11699342/avatar.jpg.320x320px.jpg?40e",
        )
    ],
}


def slugify(name: str) -> str:
    n = unicodedata.normalize("NFKD", name)
    n = n.encode("ascii", "ignore").decode("ascii")
    n = n.lower()
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    return n


def linkedin_username(url: str) -> str | None:
    if not url:
        return None
    m = re.search(r"linkedin\.com/in/([^/?#]+)", url, re.I)
    if not m:
        return None
    return urllib.parse.unquote(m.group(1).rstrip("/"))


def fetch_bytes(url: str, timeout: int = 30) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ct = (resp.headers.get("content-type") or "").lower()
            data = resp.read()
            if resp.status != 200 or len(data) < 800:
                return None
            if "svg" in ct or data.lstrip().startswith((b"<", b"<?xml")):
                return None
            if "json" in ct:
                return None
            return data
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def is_likely_placeholder(data: bytes) -> bool:
    try:
        im = Image.open(io.BytesIO(data)).convert("L")
    except Exception:
        return True
    if im.width < 80 or im.height < 80:
        return True
    px = list(im.resize((32, 32)).getdata())
    mean = sum(px) / len(px)
    var = sum((p - mean) ** 2 for p in px) / len(px)
    return var < 50


def crop_square(im: Image.Image, size: int = 400) -> Image.Image:
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side))
    return im.resize((size, size), Image.Resampling.LANCZOS)


def save_jpeg(im: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(path, "JPEG", quality=88, optimize=True)


def parse_mentors(html: str) -> list[dict]:
    m = re.search(r"const MENTORS = (\[[\s\S]*?\]);", html)
    if not m:
        raise RuntimeError("MENTORS array not found")
    raw = m.group(1)
    entries = []
    for block in re.finditer(
        r'\{id:"([^"]+)",name:"([^"]+)",role:"([^"]*)",company:"([^"]*)",'
        r'expertise:"([^"]+)",programs:\[([^\]]*)\],status:"([^"]+)",'
        r'linkedin:"([^"]+)",confidence:"([^"]+)"(?:,photo:"([^"]*)")?(?:,desc:"((?:\\.|[^"\\])*)")?\}',
        raw,
    ):
        progs = re.findall(r'"([^"]+)"', block.group(6))
        desc = block.group(11) or ""
        if desc:
            desc = desc.encode().decode("unicode_escape") if "\\" in desc else desc
        entries.append(
            {
                "id": block.group(1),
                "name": block.group(2),
                "role": block.group(3),
                "company": block.group(4),
                "expertise": block.group(5),
                "programs": progs,
                "status": block.group(7),
                "linkedin": block.group(8),
                "confidence": block.group(9),
                "photo": block.group(10) or "",
                "desc": desc,
            }
        )
    if not entries:
        raise RuntimeError("No mentor entries parsed")
    return entries


def load_descriptions() -> dict[str, str]:
    path = ARCHIVE / "descriptions.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def photo_sources(m: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    out.extend(FALLBACK_PHOTO_URLS.get(m["id"], []))
    user = linkedin_username(m["linkedin"])
    if user:
        out.append(("unavatar-linkedin", f"https://unavatar.io/linkedin/{user}"))
    return out


def serialize_mentor(m: dict) -> str:
    progs = ",".join(f'"{p}"' for p in m["programs"])
    photo = f',photo:"{m["photo"]}"' if m.get("photo") else ""
    desc = m.get("desc", "").replace("\\", "\\\\").replace('"', '\\"')
    desc_part = f',desc:"{desc}"' if desc else ""
    return (
        f'{{id:"{m["id"]}",name:"{m["name"]}",role:"{m["role"]}",company:"{m["company"]}",'
        f'expertise:"{m["expertise"]}",programs:[{progs}],status:"{m["status"]}",'
        f'linkedin:"{m["linkedin"]}",confidence:"{m["confidence"]}"{photo}{desc_part}}}'
    )


def patch_html(html: str, mentors: list[dict]) -> str:
    block = "const MENTORS = [\n  " + ",\n  ".join(serialize_mentor(m) for m in mentors) + "\n];"
    return re.sub(r"const MENTORS = \[[\s\S]*?\];", block, html, count=1)


def patch_render_card(html: str) -> str:
    if "card-desc" in html:
        return html
    css = ".card-desc{font-size:11px;color:var(--gray-text);margin-top:8px;line-height:1.45;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}"
    html = html.replace(".card-programs{", css + "\n.card-programs{", 1)
    needle = '      <div class="card-programs">${progs}</div>'
    repl = (
        '      ${m.desc ? `<div class="card-desc">${m.desc}</div>` : ""}\n'
        '      <div class="card-programs">${progs}</div>'
    )
    return html.replace(needle, repl, 1)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    html = HTML_PATH.read_text(encoding="utf-8")
    mentors = parse_mentors(html)
    descriptions = load_descriptions()

    rows = []
    found = pending = 0
    desc_added = 0

    for i, m in enumerate(mentors):
        slug = slugify(m["name"])
        local_rel = f"/nexus-assets/mentors/{slug}.jpg"
        local_path = ASSETS / f"{slug}.jpg"
        photo_source = ""
        status = "PENDIENTE"

        for label, url in photo_sources(m):
            if i > 0 or label != "unavatar-linkedin":
                time.sleep(2.2)
            data = fetch_bytes(url)
            if not data or is_likely_placeholder(data):
                continue
            try:
                im = Image.open(io.BytesIO(data))
                im = crop_square(im)
                save_jpeg(im, local_path)
                photo_source = f"{label}:{url}"
                status = "FOUND"
                m["photo"] = local_rel
                found += 1
                break
            except Exception:
                continue

        if status == "PENDIENTE":
            m["photo"] = ""
            pending += 1

        new_desc = descriptions.get(m["id"], "").strip()
        if new_desc:
            if m.get("desc") != new_desc:
                desc_added += 1
            m["desc"] = new_desc

        rows.append(
            {
                "name": m["name"],
                "profile_url": m["linkedin"],
                "photo_source_url": photo_source,
                "local_asset_path": local_rel if status == "FOUND" else "",
                "description": m.get("desc", ""),
                "status": status,
            }
        )

    new_html = patch_render_card(patch_html(html, mentors))
    HTML_PATH.write_text(new_html, encoding="utf-8")

    csv_path = ARCHIVE / "mentors.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "profile_url",
                "photo_source_url",
                "local_asset_path",
                "description",
                "status",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    manifest = {
        "date": "2026-10-16",
        "source_html": str(HTML_PATH),
        "source_xlsx": str(Path("/opt/cth-nexus/data/CTH_Master_Mentors.xlsx")),
        "total": len(mentors),
        "photos_found": found,
        "photos_pending": pending,
        "descriptions_added": desc_added,
        "assets_dir": str(ASSETS),
    }
    (ARCHIVE / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
