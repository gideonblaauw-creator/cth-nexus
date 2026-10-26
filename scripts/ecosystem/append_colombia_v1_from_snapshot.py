#!/usr/bin/env python3
"""Append Colombia v1 actors to main baseline without mutating existing ids."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "static" / "ecosystem" / "data" / "actors.raw.json"
GEO = ROOT / "ops" / "ecosystem" / "geocode-by-id.json"
SNAP = ROOT / "ops" / "ecosystem" / "colombia-v1-new-actors.snapshot.json"
REPORT = ROOT / "ops" / "ecosystem" / "colombia-v1-merge-report.json"


def load_main(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"origin/main:{path}"], cwd=ROOT)


def main() -> None:
    if not SNAP.is_file():
        raise SystemExit(f"Missing {SNAP}")
    new_rows = json.loads(SNAP.read_text(encoding="utf-8"))
    added_ids = [a["id"] for a in new_rows]
    baseline_raw = json.loads(load_main("static/ecosystem/data/actors.raw.json"))
    baseline_ids = {a["id"] for a in baseline_raw}
    for a in new_rows:
        if a["id"] in baseline_ids:
            raise SystemExit(f"Refusing to overwrite existing id {a['id']}")
    co_indices = [i for i, x in enumerate(baseline_raw) if str(x.get("id", "")).startswith("co-")]
    insert_at = co_indices[-1] + 1 if co_indices else len(baseline_raw)
    out_raw = baseline_raw[:insert_at] + new_rows + baseline_raw[insert_at:]
    RAW.write_text(json.dumps(out_raw, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    baseline_geo = json.loads(load_main("ops/ecosystem/geocode-by-id.json"))
    for a in new_rows:
        aid = a["id"]
        if aid in baseline_geo:
            raise SystemExit(f"Refusing to overwrite geocode-by-id for {aid}")
        g = a.get("geo")
        if isinstance(g, dict) and g.get("precision") == "address":
            baseline_geo[aid] = g
    GEO.write_text(json.dumps(baseline_geo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if REPORT.is_file():
        rep = json.loads(REPORT.read_text(encoding="utf-8"))
    else:
        rep = {}
    rep["added_ids"] = added_ids
    rep["added"] = len(added_ids)
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Appended {len(new_rows)} actors; raw total {len(out_raw)}; geocode keys {len(baseline_geo)}")


if __name__ == "__main__":
    main()
