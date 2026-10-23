#!/usr/bin/env python3
"""After build_public_data, keep published geo for pre-existing actors (main branch snapshot)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ACTORS = REPO / "static" / "ecosystem" / "data" / "actors.json"
REPORT = REPO / "ops" / "ecosystem" / "colombia-v1-merge-report.json"


def main() -> None:
    if not REPORT.is_file():
        raise SystemExit(f"Missing {REPORT}; run merge_colombia_actor_list_v1.py first")
    added = set(json.loads(REPORT.read_text(encoding="utf-8")).get("added_ids") or [])
    main_blob = subprocess.check_output(
        ["git", "show", "main:static/ecosystem/data/actors.json"],
        cwd=REPO,
    )
    main_by = {a["id"]: a for a in json.loads(main_blob)}
    actors = json.loads(ACTORS.read_text(encoding="utf-8"))
    n = 0
    for a in actors:
        aid = a["id"]
        if aid in added or aid not in main_by:
            continue
        ref = main_by[aid]
        if a.get("geo") != ref.get("geo"):
            a["geo"] = ref.get("geo")
            n += 1
        if ref.get("city") and a.get("city") != ref.get("city"):
            a["city"] = ref["city"]
    ACTORS.write_text(json.dumps(actors, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Preserved main-branch geo/city on {n} existing actors in {ACTORS}")


if __name__ == "__main__":
    main()
