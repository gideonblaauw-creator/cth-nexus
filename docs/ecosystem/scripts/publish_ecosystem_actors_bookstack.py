#!/usr/bin/env python3
"""
Publish ecosystem actor drafts to BookStack book 3042 (nexus-agent-review).

Requires BOOKSTACK_TOKEN (and optional BOOKSTACK_URL). Do not run without review approval.
Pattern aligned with docs/ecosystem/scripts/publish_peru_policies_bookstack.py (manifest-driven).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / "docs" / "wiki" / "ecosystem-actors" / "bookstack-manifest.json"

BOOKSTACK_URL = os.environ.get("BOOKSTACK_URL", "https://wiki.cleantechhub.net").rstrip("/")
BOOKSTACK_TOKEN = os.environ.get("BOOKSTACK_TOKEN", "")

_last_request = 0.0


def throttle() -> None:
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < 0.5:
        time.sleep(0.5 - elapsed)


def api(method: str, path: str, **kwargs):
    throttle()
    if not BOOKSTACK_TOKEN:
        raise SystemExit("BOOKSTACK_TOKEN is required")
    url = f"{BOOKSTACK_URL}/api/{path.lstrip('/')}"
    headers = {"Authorization": f"Token {BOOKSTACK_TOKEN}"}
    resp = requests.request(method, url, headers=headers, timeout=60, **kwargs)
    _last_request = time.time()
    if resp.status_code == 429:
        time.sleep(float(resp.headers.get("Retry-After", 2)))
        resp = requests.request(method, url, headers=headers, timeout=60, **kwargs)
    resp.raise_for_status()
    return resp.json() if resp.content else {}


def list_chapters(book_id: int) -> dict[str, int]:
    data = api("GET", "chapters", params={"count": 500, "filter[book_id]": book_id})
    by_slug: dict[str, int] = {}
    for ch in data.get("data", []):
        by_slug[ch.get("slug", "")] = ch["id"]
        by_slug[ch.get("name", "").lower()] = ch["id"]
    return by_slug


def ensure_chapter(book_id: int, slug: str, name: str, cache: dict[str, int]) -> int:
    if slug in cache:
        return cache[slug]
    created = api(
        "POST",
        "chapters",
        json={"book_id": book_id, "name": name, "tags": [{"name": "country", "value": name}]},
    )
    cache[slug] = created["id"]
    return created["id"]


def find_page_by_name(book_id: int, name: str) -> dict | None:
    page = 1
    while True:
        data = api("GET", "search", params={"query": name, "page": page, "count": 50})
        for item in data.get("data", []):
            if item.get("type") != "page":
                continue
            if item.get("book_id") == book_id and item.get("name") == name:
                return item
        if page * 50 >= data.get("total", 0):
            break
        page += 1
    return None


def publish_page(book_id: int, chapter_id: int, entry: dict, dry_run: bool) -> None:
    md_path = REPO / entry["markdown_path"]
    markdown = md_path.read_text(encoding="utf-8")
    # Strip YAML front matter for BookStack body
    if markdown.startswith("---"):
        parts = markdown.split("---", 2)
        if len(parts) >= 3:
            markdown = parts[2].lstrip("\n")
    title = entry["title"]
    tags = entry.get("tags", [])
    existing = find_page_by_name(book_id, title)
    payload = {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "name": title,
        "markdown": markdown,
        "tags": tags,
    }
    if dry_run:
        action = "update" if existing else "create"
        print(f"[dry-run] would {action} page: {title}")
        return
    if existing:
        api("PUT", f"pages/{existing['id']}", json=payload)
        print(f"updated page {existing['id']}: {title}")
    else:
        created = api("POST", "pages", json=payload)
        print(f"created page {created['id']}: {title}")


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    if not MANIFEST.is_file():
        print(f"Missing manifest: {MANIFEST}", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    book_id = int(manifest["book_id"])
    chapters_meta = manifest.get("chapters", {})
    chapter_cache = list_chapters(book_id)

    for slug, display in chapters_meta.items():
        ensure_chapter(book_id, slug, display, chapter_cache)

    for entry in manifest.get("pages", []):
        ch_slug = entry.get("chapter", "")
        ch_name = chapters_meta.get(ch_slug, ch_slug)
        chapter_id = ensure_chapter(book_id, ch_slug, ch_name, chapter_cache)
        publish_page(book_id, chapter_id, entry, dry_run=dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
