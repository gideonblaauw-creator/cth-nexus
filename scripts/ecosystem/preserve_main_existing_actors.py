#!/usr/bin/env python3
"""Restore every pre-main actor record verbatim in actors.json (Colombia v1 build)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ACTORS = REPO / "static" / "ecosystem" / "data" / "actors.json"
REPORT = REPO / "ops" / "ecosystem" / "colombia-v1-merge-report.json"


def main() -> None:
    if not REPORT.is_file():
        raise SystemExit(f"Missing {REPORT}")
    added = set(json.loads(REPORT.read_text(encoding="utf-8")).get("added_ids") or [])
    main_blob = subprocess.check_output(
        ["git", "show", "origin/main:static/ecosystem/data/actors.json"],
        cwd=REPO,
    )
    main_list = json.loads(main_blob)
    main_by = {a["id"]: a for a in main_list}
    main_order = [a["id"] for a in main_list]
    cur = json.loads(ACTORS.read_text(encoding="utf-8"))
    cur_new = {a["id"]: a for a in cur if a["id"] in added}
    missing_new = added - set(cur_new)
    if missing_new:
        raise SystemExit(f"Built actors.json missing new ids: {sorted(missing_new)[:5]}")
    out = [main_by[i] for i in main_order]
    for a in cur:
        if a["id"] in added:
            out.append(cur_new[a["id"]])
    ACTORS.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"actors.json: {len(main_by)} main rows preserved + {len(added)} new → {len(out)}")


if __name__ == "__main__":
    main()
