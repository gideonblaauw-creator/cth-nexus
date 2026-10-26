#!/usr/bin/env python3
"""Apply ops/ecosystem/location-corrections-draft.json to ecosystem data files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / "ops" / "ecosystem" / "location-corrections-draft.json"
RAW = ROOT / "static" / "ecosystem" / "data" / "actors.raw.json"
PUB = ROOT / "static" / "ecosystem" / "data" / "actors.json"
GEO = ROOT / "ops" / "ecosystem" / "geocode-by-id.json"


def main() -> None:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    pub = json.loads(PUB.read_text(encoding="utf-8"))
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    for aid, blocks in draft.items():
        rp = blocks.get("actors.raw.json") or {}
        for r in raw:
            if r["id"] == aid:
                if "geo" in rp:
                    r["geo"] = rp["geo"]
                for k, v in rp.items():
                    if k != "geo":
                        r[k] = v
        pp = blocks.get("actors.json") or {}
        for r in pub:
            if r["id"] == aid:
                if "geo" in pp:
                    r["geo"] = pp["geo"]
                for k, v in pp.items():
                    if k != "geo":
                        r[k] = v
        g = blocks.get("geocode-by-id.json")
        if g is not None:
            geo[aid] = g
    RAW.write_text(json.dumps(raw, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    PUB.write_text(json.dumps(pub, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    GEO.write_text(json.dumps(geo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Applied location corrections for {len(draft)} ids")


if __name__ == "__main__":
    main()
