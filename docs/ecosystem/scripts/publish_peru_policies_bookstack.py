#!/usr/bin/env python3
"""Publish docs/wiki/peru-policies to BookStack book 3042 only."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WIKI = ROOT / "docs/wiki/peru-policies"
MANIFEST = WIKI / "bookstack-manifest.json"
BOOK_ID = 3042
BASE = os.environ.get("BOOKSTACK_URL", "https://wiki.cleantechhub.net").rstrip("/")
TOKEN = os.environ.get("BOOKSTACK_TOKEN", "")


def api(method: str, path: str, payload: dict | None = None, params: dict | None = None):
    if not TOKEN:
        raise SystemExit("BOOKSTACK_TOKEN not set (expected token_id:token_secret)")
    url = f"{BASE}/api/{path.lstrip('/')}"
    if params:
        q = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        url = f"{url}?{q}"
    data = None
    headers = {"Authorization": f"Token {TOKEN}", "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    time.sleep(0.55)
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise RuntimeError(f"{method} {path} -> {e.code}: {err[:500]}") from e


def find_chapter(book_id: int, name: str):
    data = api("GET", "chapters", params={"filter[book_id]": book_id, "count": 100})
    for ch in data.get("data", []):
        if ch.get("name") == name:
            return ch["id"]
    return None


def main():
    manifest = json.loads(MANIFEST.read_text())
    chapter_name = manifest["chapter_name"]
    ch_id = find_chapter(BOOK_ID, chapter_name)
    if not ch_id:
        ch = api(
            "POST",
            "chapters",
            {
                "book_id": BOOK_ID,
                "name": chapter_name,
                "description": "Nexus PE climate policy catalog (private review).",
            },
        )
        ch_id = ch["id"]
        print(f"Created chapter id={ch_id}", flush=True)

    published = []
    for entry in manifest["pages"]:
        path = WIKI / entry["file"]
        md = path.read_text(encoding="utf-8")
        page = api(
            "POST",
            "pages",
            {
                "book_id": BOOK_ID,
                "chapter_id": ch_id,
                "name": entry["name"],
                "markdown": md,
                "tags": [{"name": "nexus-ecosystem", "value": "pe-policies-review"}],
            },
        )
        slug = page.get("slug") or str(page["id"])
        published.append(
            {
                "id": page["id"],
                "name": page["name"],
                "slug": slug,
                "url": f"{BASE}/books/nexus-agent-review/page/{slug}",
            }
        )
        print(json.dumps(published[-1]), flush=True)

    (WIKI / "bookstack-published.json").write_text(
        json.dumps({"chapter_id": ch_id, "pages": published}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
