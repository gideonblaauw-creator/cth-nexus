#!/usr/bin/env python3
"""
Publish Peru policy pages to BookStack from a manifest (reference pattern).

This repository snapshot may not include the Peru policies manifest yet; this script
documents the shared publish flow used by publish_ecosystem_actors_bookstack.py.

Requires BOOKSTACK_TOKEN. Do not run in CI without credentials.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = REPO / "docs" / "wiki" / "peru-policies" / "bookstack-manifest.json"

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
    resp.raise_for_status()
    return resp.json() if resp.content else {}


def main() -> int:
    manifest_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MANIFEST
    if not manifest_path.is_file():
        print(
            f"Manifest not found: {manifest_path}\n"
            "Pass path to bookstack-manifest.json when Peru policy drafts land.",
            file=sys.stderr,
        )
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    book_id = int(manifest["book_id"])
    print(f"Would publish {len(manifest.get('pages', []))} pages to book {book_id}")
    print("Use publish_ecosystem_actors_bookstack.py as the maintained implementation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
