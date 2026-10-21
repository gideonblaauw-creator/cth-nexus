#!/usr/bin/env python3
"""Fetch public relation sources and check evidence substring presence."""
from __future__ import annotations

import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL_PATH = ROOT / "static" / "ecosystem" / "data" / "relations.json"
UA = "CleantechHUB-Nexus-Ecosystem/1.0 (ops@cleantechhub.net)"


def norm_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "")
    return s.strip().lower()


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
        raw = resp.read()
    try:
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return raw.decode("latin-1", errors="replace")


def main() -> int:
    rels = json.loads(REL_PATH.read_text(encoding="utf-8"))
    public = [r for r in rels if r.get("verified") is True and r.get("source_url")]
    ok = 0
    fail = []
    for r in public:
        url = r["source_url"]
        ev = r.get("evidence") or ""
        try:
            body = fetch(url)
        except Exception as e:
            fail.append((r, f"fetch: {e}"))
            continue
        if norm_text(ev) in norm_text(body):
            ok += 1
        else:
            fail.append((r, "quote not found"))
    print(json.dumps({"public": len(public), "quote_ok": ok, "quote_fail": len(fail)}, indent=2))
    for r, why in fail[:40]:
        print(f"FAIL {r['source']} -> {r['target']} ({r['type']}): {why}")
        print(f"  url: {r.get('source_url')}")
        print(f"  evidence: {(r.get('evidence') or '')[:120]}...")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
