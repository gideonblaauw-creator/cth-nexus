#!/usr/bin/env python3
"""Verify websites for Epic Angels curated entries and emit shareable flags."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

CURATED_PATH = Path("/opt/nexus-idea-browser/src/data/epic-angels-curated.json")
CLP26_PATH = Path("/opt/cth-nexus/data/clp26_colombia_ideas.json")
ARCHIVE = Path("/opt/nexus-idea-browser/Archive/epic-angels-20250918")
BOOK_ENV = Path("/opt/idea-browser/.env")

SOCIAL_OR_AGGREGATOR = {
    "linktr.ee", "instagram.com", "www.instagram.com",
    "facebook.com", "www.facebook.com", "linkedin.com", "www.linkedin.com",
    "twitter.com", "x.com", "tiktok.com", "youtube.com", "youtu.be",
}

PARKING_HINTS = (
    "domain for sale", "buy this domain", "this domain is parked",
    "parked free", "godaddy", "sedo parking", "hugedomains", "namecheap",
    "is available for purchase", "domain has expired",
)

USER_AGENT = "CTH-EpicAngels-Verify/1.0 (+https://nexus.cleantechhub.net)"


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw or raw in ("—", "-", "None"):
        return ""
    if not re.match(r"^https?://", raw, re.I):
        raw = "https://" + raw
    return raw


def clp26_websites() -> dict[str, str]:
    if not CLP26_PATH.exists():
        return {}
    data = json.loads(CLP26_PATH.read_text())
    out: dict[str, str] = {}
    for idea in data:
        w = normalize_url(idea.get("website") or "")
        if w:
            out[idea["startup_name"].lower()] = w
    return out


def bookstack_website(page_id: int, headers: dict) -> str:
    env = load_env(BOOK_ENV)
    base = env["BOOKSTACK_URL"].rstrip("/")
    r = requests.get(f"{base}/api/pages/{page_id}", headers=headers, timeout=30)
    r.raise_for_status()
    md = r.json().get("markdown") or ""
    m = re.search(r"\*\*Website:\*\*\s*(.+)", md)
    return normalize_url(m.group(1)) if m else ""


def is_social_or_aggregator(url: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    full = urlparse(url).netloc.lower()
    return full in SOCIAL_OR_AGGREGATOR or host in SOCIAL_OR_AGGREGATOR


def looks_like_parking(html: str, final_url: str) -> bool:
    text = (html or "").lower()[:8000]
    if any(h in text for h in PARKING_HINTS):
        return True
    # Very short body on non-error page often means placeholder
    if len(text.strip()) < 200 and "404" not in text:
        return False
    return False


def verify_url(url: str) -> dict:
    result = {
        "website": url,
        "website_verified": False,
        "shareable": False,
        "verify_status": "missing",
        "verify_note": "",
        "final_url": "",
        "http_status": None,
    }
    if not url:
        result["verify_note"] = "No website on record"
        return result

    if is_social_or_aggregator(url):
        result["verify_status"] = "social_or_aggregator"
        result["verify_note"] = "Social/link aggregator — not APC shareable company site"
        return result

    try:
        r = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=20,
            allow_redirects=True,
        )
        result["http_status"] = r.status_code
        result["final_url"] = r.url
        if r.status_code >= 400:
            result["verify_status"] = "http_error"
            result["verify_note"] = f"HTTP {r.status_code}"
            return result
        if looks_like_parking(r.text, r.url):
            result["verify_status"] = "parking"
            result["verify_note"] = "Parking or placeholder page"
            return result
        result["website_verified"] = True
        result["shareable"] = True
        result["verify_status"] = "ok"
        result["verify_note"] = f"HTTP {r.status_code}"
        if r.url != url:
            result["verify_note"] += f" → {r.url}"
    except requests.RequestException as exc:
        result["verify_status"] = "request_failed"
        result["verify_note"] = str(exc)[:120]

    return result


def pick_website(entry: dict, clp26: dict[str, str], headers: dict) -> str:
    pid = entry.get("bookstack_page_id")
    bs = bookstack_website(pid, headers) if pid else ""
    if bs:
        return bs
    for key in [entry["startup_name"].lower()] + [a.lower() for a in entry.get("aliases", [])]:
        if key in clp26:
            return clp26[key]
        for k, v in clp26.items():
            if key in k or k in key:
                return v
    return ""


def main() -> int:
    env = load_env(BOOK_ENV)
    headers = {
        "Authorization": f"Token {env['BOOKSTACK_TOKEN_ID']}:{env['BOOKSTACK_TOKEN_SECRET']}",
    }
    curated = json.loads(CURATED_PATH.read_text())
    clp26 = clp26_websites()
    report = []

    for entry in curated:
        url = pick_website(entry, clp26, headers)
        v = verify_url(url)
        entry["website"] = url
        entry["website_verified"] = v["website_verified"]
        entry["shareable"] = v["shareable"]
        entry["website_verify_status"] = v["verify_status"]
        entry["website_verify_note"] = v["verify_note"]
        if v.get("final_url") and v["final_url"] != url:
            entry["website_final_url"] = v["final_url"]
        report.append({
            "startup_name": entry["startup_name"],
            **v,
        })

    CURATED_PATH.write_text(json.dumps(curated, indent=2, ensure_ascii=False) + "\n")

    shareable = [e for e in curated if e.get("shareable")]
    apc_list = [
        {
            "startup_name": e["startup_name"],
            "website": e.get("website_final_url") or e["website"],
            "app_id": e.get("app_id"),
            "bookstack_page_id": e.get("bookstack_page_id"),
            "confidence": e.get("confidence"),
            "women_clevel_status": e.get("women_clevel_status"),
        }
        for e in shareable
    ]

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / "apc-share-list.json").write_text(
        json.dumps({"generated": date.today().isoformat(), "shareable_count": len(apc_list), "startups": apc_list}, indent=2, ensure_ascii=False) + "\n"
    )
    (ARCHIVE / "website-verification-report.json").write_text(
        json.dumps({"generated": date.today().isoformat(), "total": len(report), "shareable": len(shareable), "entries": report}, indent=2, ensure_ascii=False) + "\n"
    )
    cp = ARCHIVE / "curated.json"
    cp.write_text(CURATED_PATH.read_text())

    print(json.dumps({
        "total": len(curated),
        "shareable": len(shareable),
        "shareable_names": [e["startup_name"] for e in shareable],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
