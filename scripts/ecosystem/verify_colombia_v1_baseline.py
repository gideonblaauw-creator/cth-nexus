#!/usr/bin/env python3
"""Verify Colombia v1 PR: existing ids match origin/main; new rows have no public street text."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "ops" / "ecosystem" / "colombia-v1-merge-report.json"
FILES = (
    ("static/ecosystem/data/actors.json", "actors.json"),
    ("static/ecosystem/data/actors.raw.json", "actors.raw.json"),
    ("ops/ecosystem/geocode-by-id.json", "geocode-by-id.json"),
)


def load_main(path: str):
    return json.loads(subprocess.check_output(["git", "show", f"origin/main:{path}"], cwd=REPO))


def actor_map(blob, key="id"):
    if isinstance(blob, dict):
        return blob
    return {a[key]: a for a in blob}


def has_street_public(actor: dict) -> bool:
    if actor.get("address"):
        return True
    g = actor.get("geo") or {}
    if g.get("address"):
        return True
    return False


def main() -> int:
    added = set(json.loads(REPORT.read_text(encoding="utf-8")).get("added_ids") or [])
    exit_code = 0
    for path, label in FILES:
        main_blob = load_main(path)
        cur_blob = json.loads((REPO / path).read_text(encoding="utf-8"))
        if path.endswith("geocode-by-id.json"):
            main_by, cur_by = main_blob, cur_blob
        else:
            main_by = {a["id"]: a for a in main_blob}
            cur_by = {a["id"]: a for a in cur_blob}
        main_ids = set(main_by)
        diffs = []
        for aid in sorted(main_ids):
            if json.dumps(main_by[aid], ensure_ascii=False) != json.dumps(
                cur_by.get(aid), ensure_ascii=False
            ):
                diffs.append(aid)
        print(f"{label}: existing ids differing from main: {len(diffs)}")
        if diffs:
            print("  sample:", diffs[:8])
            exit_code = 1
    actors = json.loads((REPO / "static/ecosystem/data/actors.json").read_text())
    street_rows = [a["id"] for a in actors if a["id"] in added and has_street_public(a)]
    print(f"actors.json: new rows with street text in public fields: {len(street_rows)}")
    if street_rows:
        print("  sample:", street_rows[:8])
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
