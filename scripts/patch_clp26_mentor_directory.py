#!/usr/bin/env python3
"""Patch CLP26 mentor cards (M077–M127) in live mentor directory HTML."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE_HTML = Path("/opt/cth-nexus/static/mentor-directory/index.html")
REPO_HTML = ROOT / "site/cth-static/mentor-directory/index.html"
REPO_HTML_ALT = ROOT / "site/mentor-directory/index.html"
ENRICHMENT = ROOT / "data/clp26/mentor_directory_enrichment.json"
ASSETS = Path("/var/www/nexus-assets/mentors")
UA = "Mozilla/5.0 (compatible; CleantechHUB-Nexus/1.0; +https://nexus.cleantechhub.net)"

# Public avatar sources (not LinkedIn login — third-party CDN / org sites)
PORTRAIT_URLS: dict[str, list[tuple[str, str]]] = {
    "alex-kudzuma": [("unavatar", "https://unavatar.io/linkedin/alex-kudzuma")],
    "ana-maria-parra-garcia": [("unavatar", "https://unavatar.io/linkedin/ana-maria-parra-pm")],
    "cinthya-sandoval-cuellar": [("unavatar", "https://unavatar.io/linkedin/cinthya-sandoval-48903770")],
    "felipe-hernandez": [("unavatar", "https://unavatar.io/linkedin/fhvdesign")],
    "gabriela-tenaz": [("unavatar", "https://unavatar.io/linkedin/gabriela-t%C3%A9naz-2914a6127")],
    "gloria-bazan-narvaez": [
        (
            "torre",
            "https://res.cloudinary.com/torre-technologies-co/image/upload/v0/origin/starrgate/users/profile_c352a9d2266c9c079b23b9dd3a65002f28597e02.jpg",
        ),
        ("unavatar", "https://unavatar.io/linkedin/gloria-bazan-narvaez-06581b55"),
    ],
    "karol-m-garzon": [
        ("unavatar", "https://unavatar.io/linkedin/karol-melissa-garz%C3%B3n-cabrera-5516a6382")
    ],
    "lina-ospina": [
        ("unavatar", "https://unavatar.io/linkedin/lina-ospina-mosquera"),
    ],
    "lucia-medina-capacoila": [
        ("unavatar", "https://unavatar.io/linkedin/luciamedinacapacoila")
    ],
    "martin-dolan": [("unavatar", "https://unavatar.io/linkedin/martin-dolan")],
    "paola-andrea-sanchez-gutierrez": [
        (
            "paola-solar-insights",
            "https://paolasolarinsights.com/wp-content/uploads/2026/01/Whisk_04ad83628af37c689bd4d38ab0d71631dr-300x300.jpeg",
        ),
        ("unavatar", "https://unavatar.io/linkedin/paolasolarinsights"),
    ],
}

MENTOR_RE = re.compile(
    r'\{id:"(M\d+)",name:"([^"]+)",role:"((?:\\.|[^"\\])*)",company:"((?:\\.|[^"\\])*)",'
    r'expertise:"((?:\\.|[^"\\])*)",programs:\[([^\]]*)\],status:"([^"]+)",'
    r'linkedin:"((?:\\.|[^"\\])*)"(?:,confidence:"([^"]*)")?(?:,photo:"((?:\\.|[^"\\])*)")?'
    r'(?:,desc:"((?:\\.|[^"\\])*)")?\}'
)


def slugify(name: str) -> str:
    n = unicodedata.normalize("NFKD", name)
    n = n.encode("ascii", "ignore").decode("ascii")
    n = n.lower()
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    return n


def in_scope(mid: str) -> bool:
    n = int(mid[1:])
    return 77 <= n <= 127


def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def fetch_bytes(url: str, timeout: int = 45) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if resp.status != 200 or len(data) < 600:
                return None
            ct = (resp.headers.get("content-type") or "").lower()
            if "svg" in ct or data.lstrip().startswith((b"<", b"<?xml")):
                return None
            return data
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def fetch_bytes_curl(url: str) -> bytes | None:
    try:
        out = subprocess.check_output(
            ["curl", "-sL", "-A", UA, url],
            timeout=60,
        )
        return out if len(out) >= 600 else None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def crop_square(im, size: int = 400):
    from PIL import Image

    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side))
    return im.resize((size, size), Image.Resampling.LANCZOS)


def save_jpeg(im, path: Path) -> None:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(path, "JPEG", quality=88, optimize=True)


def parse_mentors(html: str) -> list[dict]:
    mentors = []
    for m in MENTOR_RE.finditer(html):
        progs = re.findall(r'"([^"]+)"', m.group(6))
        mentors.append(
            {
                "id": m.group(1),
                "name": m.group(2),
                "role": m.group(3),
                "company": m.group(4),
                "expertise": m.group(5),
                "programs": progs,
                "status": m.group(7),
                "linkedin": m.group(8),
                "confidence": m.group(9) or "",
                "photo": m.group(10) or "",
                "desc": m.group(11) or "",
                "span": m.span(),
            }
        )
    if not mentors:
        raise RuntimeError("No mentor entries parsed")
    return mentors


def serialize_mentor(m: dict) -> str:
    progs = ",".join(f'"{p}"' for p in m["programs"])
    conf = f',confidence:"{m["confidence"]}"' if m.get("confidence") else ""
    photo = f',photo:"{js_escape(m["photo"])}"' if m.get("photo") else ""
    desc = f',desc:"{js_escape(m.get("desc", ""))}"' if m.get("desc") else ""
    return (
        f'{{id:"{m["id"]}",name:"{js_escape(m["name"])}",role:"{js_escape(m["role"])}",'
        f'company:"{js_escape(m["company"])}",expertise:"{js_escape(m["expertise"])}",'
        f'programs:[{progs}],status:"{m["status"]}",linkedin:"{js_escape(m["linkedin"])}"'
        f"{conf}{photo}{desc}}}"
    )


def patch_html(html: str, mentors: list[dict]) -> str:
    block = "const MENTORS = [\n  " + ",\n  ".join(serialize_mentor(m) for m in mentors) + "\n];"
    return re.sub(r"const MENTORS = \[[\s\S]*?\];", block, html, count=1)


def scope_guard(before: str, after: str) -> None:
    b = parse_mentors(before)
    a = parse_mentors(after)
    if len(b) != len(a):
        raise SystemExit(f"scope guard: mentor count changed {len(b)} -> {len(a)}")
    for x, y in zip(b, a):
        if x["id"] != y["id"] or x["name"] != y["name"]:
            raise SystemExit("scope guard: mentor order/id/name changed")
        if in_scope(x["id"]):
            continue
        for k in ("role", "company", "expertise", "linkedin", "status", "photo", "desc", "programs"):
            if x.get(k) != y.get(k):
                raise SystemExit(f"scope guard: {x['id']} field {k} changed outside M077–M127")


def add_portraits(mentors: list[dict], enrichment: dict) -> list[str]:
    from PIL import Image

    added: list[str] = []
    by_id = {m["id"]: m for m in mentors}
    for mid, data in enrichment.items():
        if not in_scope(mid):
            continue
        m = by_id[mid]
        if m.get("photo"):
            continue
        slug = slugify(m["name"])
        urls = PORTRAIT_URLS.get(slug, [])
        if not urls:
            continue
        for _label, url in urls:
            raw = fetch_bytes(url) or fetch_bytes_curl(url)
            if not raw:
                continue
            try:
                im = Image.open(io.BytesIO(raw))
            except Exception:
                continue
            if im.width < 80 or im.height < 80:
                continue
            im = crop_square(im)
            rel = f"/nexus-assets/mentors/{slug}.jpg"
            save_jpeg(im, ASSETS / f"{slug}.jpg")
            m["photo"] = rel
            added.append(slug)
            break
    return added


def backup(paths: list[Path], ts: str) -> Path:
    dest = Path(f"/var/backups/nexus-clp26-mentor-patch-{ts}")
    dest.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if p.is_file():
            shutil.copy2(p, dest / p.name)
        elif p.is_dir():
            shutil.copytree(p, dest / p.name, dirs_exist_ok=True)
    return dest


def verify_http(base: str, photos: list[str]) -> dict:
    out = {"page": None, "images": {}}
    try:
        page = subprocess.check_output(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", f"{base}/mentor-directory/"],
            timeout=30,
        ).decode()
        out["page"] = page.strip()
    except subprocess.CalledProcessError as e:
        out["page"] = f"ERR:{e.returncode}"
    for slug in photos:
        url = f"{base}/nexus-assets/mentors/{slug}.jpg"
        try:
            code = subprocess.check_output(
                ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", url],
                timeout=30,
            ).decode().strip()
            out["images"][slug] = code
        except subprocess.CalledProcessError as e:
            out["images"][slug] = f"ERR:{e.returncode}"
    return out


def apply_enrichment(mentors: list[dict], enrichment: dict) -> dict:
    stats = {"expertise": 0, "desc": 0, "programs": 0, "role": 0, "company": 0}
    by_id = {m["id"]: m for m in mentors}
    for mid, patch in enrichment.items():
        if not in_scope(mid) or mid not in by_id:
            continue
        m = by_id[mid]
        for field in ("role", "company", "expertise", "desc"):
            val = patch.get(field, "")
            if val and not m.get(field):
                m[field] = val
                stats[field] += 1
            elif val and m.get(field) != val:
                m[field] = val
                stats[field] += 1
        progs = patch.get("programs") or ["CLP26"]
        if m.get("programs") != progs:
            m["programs"] = progs
            stats["programs"] += 1
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--verify-base", default="https://nexus.cleantechhub.net")
    args = ap.parse_args()

    if not LIVE_HTML.is_file():
        print("missing live html", LIVE_HTML, file=sys.stderr)
        return 1
    enrichment = json.loads(ENRICHMENT.read_text(encoding="utf-8"))
    html_before = LIVE_HTML.read_text(encoding="utf-8")
    mentors = parse_mentors(html_before)
    stats = apply_enrichment(mentors, enrichment)
    photos_added = add_portraits(mentors, enrichment)
    html_after = patch_html(html_before, mentors)
    scope_guard(html_before, html_after)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = None
    if args.apply:
        asset_files = list(ASSETS.glob("*.jpg"))
        backup_dir = backup([LIVE_HTML, ASSETS], ts)
        LIVE_HTML.write_text(html_after, encoding="utf-8")
        for repo_path in (REPO_HTML, REPO_HTML_ALT):
            if repo_path.parent.is_dir():
                repo_path.parent.mkdir(parents=True, exist_ok=True)
                repo_path.write_text(html_after, encoding="utf-8")
        verify = verify_http(args.verify_base, photos_added)
    else:
        verify = {"dry_run": True}

    blank = {k: 0 for k in ("expertise", "desc", "photo")}
    for m in mentors:
        if not in_scope(m["id"]):
            continue
        for k in blank:
            if not m.get(k):
                blank[k] += 1

    report = {
        "stats_filled": stats,
        "photos_added": photos_added,
        "photos_added_count": len(photos_added),
        "still_blank": blank,
        "backup_path": str(backup_dir) if backup_dir else None,
        "verify": verify,
        "rollback": (
            f"cp {backup_dir}/index.html {LIVE_HTML} && "
            f"rsync -a --delete {backup_dir}/mentors/ {ASSETS}/"
            if backup_dir
            else None
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.apply and verify.get("page") != "200":
        print("verify failed for page; rolling back", file=sys.stderr)
        if backup_dir:
            shutil.copy2(backup_dir / "index.html", LIVE_HTML)
            if (backup_dir / "mentors").is_dir():
                shutil.copytree(backup_dir / "mentors", ASSETS, dirs_exist_ok=True)
        return 2
    bad = [s for s, c in verify.get("images", {}).items() if c != "200"]
    if args.apply and bad:
        print("verify failed for images", bad, file=sys.stderr)
        if backup_dir:
            shutil.copy2(backup_dir / "index.html", LIVE_HTML)
            if (backup_dir / "mentors").is_dir():
                shutil.copytree(backup_dir / "mentors", ASSETS, dirs_exist_ok=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
