#!/usr/bin/env python3
"""Assert Epic Angels shareable list and allowlist filter stay at 18."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
EPIC_JSON = ROOT / "nexus" / "nexus-assets" / "epic-angels-shareable.json"
PORTFOLIO_HTML = ROOT / "nexus" / "p" / "startup-portfolio" / "index.html"

from epic_allowlist import EPIC_ALLOWLIST_SLUGS, EPIC_ALLOWLIST_NAMES  # noqa: E402


def main() -> int:
    data = json.loads(EPIC_JSON.read_text(encoding="utf-8"))
    startups = data.get("startups") or []
    if data.get("count") != 18 or len(startups) != 18:
        print(f"FAIL: epic-angels-shareable.json count={data.get('count')} len={len(startups)}", file=sys.stderr)
        return 1
    slugs = {s["slug"] for s in startups}
    if slugs != set(EPIC_ALLOWLIST_SLUGS):
        print(f"FAIL: slug set mismatch {slugs ^ set(EPIC_ALLOWLIST_SLUGS)}", file=sys.stderr)
        return 1
    html = PORTFOLIO_HTML.read_text(encoding="utf-8")
    m = re.search(r"EPIC_ALLOWLIST_SLUGS=new Set\(\[([^\]]+)\]", html)
    if not m:
        print("FAIL: EPIC_ALLOWLIST_SLUGS not found in portfolio HTML", file=sys.stderr)
        return 1
    html_slugs = {s.strip().strip("'\"") for s in m.group(1).split(",") if s.strip()}
    if html_slugs != set(EPIC_ALLOWLIST_SLUGS):
        print("FAIL: HTML allowlist slugs differ from epic_allowlist.py", file=sys.stderr)
        return 1
    print("OK: Epic Angels allowlist verified (18 startups)")
    for name in EPIC_ALLOWLIST_NAMES:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
