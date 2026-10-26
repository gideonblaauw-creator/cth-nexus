#!/usr/bin/env python3
"""Remove street address strings from public Colombia v1 rows in actors.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ACTORS = REPO / "static" / "ecosystem" / "data" / "actors.json"
REPORT = REPO / "ops" / "ecosystem" / "colombia-v1-merge-report.json"

STREET_FIELD = re.compile(
    r"(?i)^\s*(?:\|?\s*)?(?:\*\*)?(?:direcci[oó]n|address|street(?:\s+address)?)(?:\*\*)?\s*[:|]"
)


def scrub_actor(a: dict) -> None:
    a.pop("address", None)
    g = a.get("geo")
    if isinstance(g, dict):
        g.pop("address", None)
        if g.get("location_note") and "direcci" in str(g.get("location_note", "")).lower():
            g.pop("location_note", None)
    card = a.get("card")
    if isinstance(card, dict):
        desc = card.get("description")
        if isinstance(desc, str):
            lines = [ln for ln in desc.split("\n") if not STREET_FIELD.search(ln.replace("*", ""))]
            card["description"] = "\n".join(lines).strip()


def main() -> None:
    added = set(json.loads(REPORT.read_text(encoding="utf-8")).get("added_ids") or [])
    actors = json.loads(ACTORS.read_text(encoding="utf-8"))
    n = 0
    for a in actors:
        if a["id"] not in added:
            continue
        scrub_actor(a)
        n += 1
    ACTORS.write_text(json.dumps(actors, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Stripped public address fields on {n} Colombia v1 rows")


if __name__ == "__main__":
    main()
