#!/usr/bin/env python3
"""Fetch official sites for Colombia v1 actors and extract street candidates (fast)."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "docs" / "colombia" / "actor-list-v1.csv"
OUT = ROOT / "ops" / "ecosystem" / "colombia-v1-address-candidates.json"
UA = "CleantechHUB-Nexus-Ecosystem/1.0 (colombia-v1 geo harvest)"
TIMEOUT = 12
WORKERS = 12

PATHS = ("", "/contacto", "/contactenos")

ADDR_RE = re.compile(
    r"(?i)\b((?:Calle|Carrera|Cra\.?|Cl\.?|Av\.?|Avenida|Diagonal|Transversal)\s"
    r"[\d\w\sº°#\.-]{4,85})"
)


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return "co-" + re.sub(r"-+", "-", s)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read(400_000).decode("utf-8", errors="replace")


def base_url(website: str) -> str:
    w = website.strip()
    if not w.startswith("http"):
        w = "https://" + w
    p = urllib.parse.urlparse(w)
    return f"{p.scheme}://{p.netloc}"


def extract_addresses(html: str) -> list[str]:
    text = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    found: list[str] = []
    for m in ADDR_RE.finditer(text):
        s = m.group(1).strip(" ,.;")
        if 10 <= len(s) <= 100 and s not in found:
            found.append(s)
        if len(found) >= 3:
            break
    return found


def harvest_one(spec: dict) -> tuple[str, dict]:
    aid = spec["id"]
    site = spec["website"]
    hits: list[dict] = []
    if site:
        b = base_url(site)
        for path in PATHS:
            url = b if not path else b.rstrip("/") + path
            try:
                html = fetch(url)
            except (urllib.error.URLError, TimeoutError, OSError, ValueError):
                continue
            addrs = extract_addresses(html)
            if addrs:
                hits.append({"url": url, "addresses": addrs})
                break
    return aid, {"hits": hits, **spec}


def main() -> None:
    if not CSV_PATH.is_file():
        raise SystemExit(f"Missing {CSV_PATH}")
    rows = list(csv.DictReader(CSV_PATH.read_text(encoding="utf-8").splitlines()))
    existing = json.loads(
        (ROOT / "static" / "ecosystem" / "data" / "actors.json").read_text(encoding="utf-8")
    )
    existing_ids = {a["id"] for a in existing}
    todo: list[dict] = []
    seen: set[str] = set()
    for r in rows:
        aid = (r.get("ecosystem_id") or "").strip() or slugify(r["name"])
        if aid in existing_ids or aid in seen:
            continue
        seen.add(aid)
        todo.append(
            {
                "id": aid,
                "name": r["name"],
                "city": r["city"],
                "website": (r.get("website") or "").strip(),
                "category": r["category"],
            }
        )
    out: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(harvest_one, s) for s in todo]
        for fut in as_completed(futs):
            aid, row = fut.result()
            out[aid] = row
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with_hits = sum(1 for v in out.values() if v["hits"])
    print(f"Wrote {len(out)} actors; {with_hits} with address candidates → {OUT}")


if __name__ == "__main__":
    main()
