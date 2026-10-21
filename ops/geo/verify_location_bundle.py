#!/usr/bin/env python3
"""Verify location assembler changes: counts, ids, non-location fields vs main."""
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BUNDLE_PATHS = [
    "static/ecosystem/data/actors.json",
    "site/cth-static/hubs/hubs-data.json",
    "site/nexus-assets/previews/startups-redesign-20261016/portfolio-core.json",
    "site/investors/data/investors.json",
    "data/clp26/mentor_cards.json",
    "data/clp26/jury_cards.json",
    "app/nexus-ideas/src/data/imd-peru-curated.json",
    "app/nexus-ideas/src/data/epic-angels-curated.json",
]

LOCATION_TOP_KEYS = frozenset(
    {
        "geo",
        "loc",
        "location",
        "city",
        "country",
        "c",
        "location_precision",
        "location_source_url",
        "location_note",
        "hq_city",
        "hq_source_url",
        "hq_evidence",
    }
)


def git_main_json(rel: str):
    raw = subprocess.check_output(["git", "show", f"origin/main:{rel}"], cwd=ROOT)
    return json.loads(raw)


def load_head(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _strip_ribbon_country(ribbon: list) -> None:
    for rib in ribbon or []:
        if rib.get("lab_en") == "Country" or rib.get("lab_es") in ("País", "Pa&iacute;s", "Country"):
            rib.pop("sub_en", None)
            rib.pop("sub_es", None)
            rib.pop("val", None)


def strip_location(obj):
    if isinstance(obj, dict):
        if "ribbon" in obj and isinstance(obj["ribbon"], list):
            o = deepcopy(obj)
            o.pop("location", None)
            if isinstance(o.get("portfolio"), dict):
                p = o["portfolio"]
                for k in ("location_en", "location_es", "country_code", "country_name_en", "country_name_es"):
                    p.pop(k, None)
            _strip_ribbon_country(o["ribbon"])
            for k in list(o.keys()):
                if k in LOCATION_TOP_KEYS:
                    o.pop(k, None)
            return {k: strip_location(v) for k, v in o.items()}
        if "portfolio" in obj and isinstance(obj["portfolio"], dict):
            o = deepcopy(obj)
            p = o["portfolio"]
            for k in ("location_en", "location_es", "country_code", "country_name_en", "country_name_es"):
                p.pop(k, None)
            for k in list(o.keys()):
                if k in LOCATION_TOP_KEYS:
                    o.pop(k, None)
            _strip_ribbon_country(o.get("ribbon"))
            return o
        o = {k: strip_location(v) for k, v in obj.items() if k not in LOCATION_TOP_KEYS}
        return o
    if isinstance(obj, list):
        return [strip_location(x) for x in obj]
    return obj


def actor_key(a: dict) -> str:
    return a["id"]


def portfolio_key(s: dict) -> str:
    return s.get("n", "")


def investor_key(i: dict) -> int:
    return int(i["id"])


def idea_key(i: dict) -> str:
    return i.get("slug") or i.get("startup_name") or ""


def mentor_key(m: dict, idx: int) -> str:
    return m.get("nexus_id") or f"idx-{idx}"


def jury_key(j: dict, idx: int) -> str:
    return f"juror-{idx + 1}"


def hub_key(h: dict) -> str:
    return h["id"]


def compare_collection(name: str, main_list: list, head_list: list, key_fn) -> list[str]:
    errs: list[str] = []
    if len(main_list) != len(head_list):
        errs.append(f"{name}: count main={len(main_list)} head={len(head_list)}")

    def keyed(lst: list) -> dict:
        out = {}
        for i, x in enumerate(lst):
            import inspect

            if len(inspect.signature(key_fn).parameters) >= 2:
                k = key_fn(x, i)
            else:
                k = key_fn(x)
            out[k] = x
        return out

    main_by = keyed(main_list)
    head_by = keyed(head_list)
    if set(main_by) != set(head_by):
        missing = set(main_by) - set(head_by)
        extra = set(head_by) - set(main_by)
        if missing:
            errs.append(f"{name}: missing ids {list(missing)[:5]}")
        if extra:
            errs.append(f"{name}: extra ids {list(extra)[:5]}")
        return errs
    for k in main_by:
        m = strip_location(main_by[k])
        h = strip_location(head_by[k])
        if m != h:
            errs.append(f"{name}: non-location field drift for {k}")
    return errs


def verify_onepagers() -> list[str]:
    errs: list[str] = []
    data_dir = ROOT / "onepagers/data"
    for path in sorted(data_dir.glob("*.json")):
        rel = path.relative_to(ROOT).as_posix()
        try:
            main = git_main_json(rel)
        except subprocess.CalledProcessError:
            continue
        head = json.loads(path.read_text(encoding="utf-8"))
        if strip_location(main) != strip_location(head):
            errs.append(f"onepager {path.stem}: non-location drift")
    return errs


def main() -> int:
    errs: list[str] = []

    main_actors = git_main_json(BUNDLE_PATHS[0])
    head_actors = load_head(BUNDLE_PATHS[0])
    errs.extend(compare_collection("actors", main_actors, head_actors, actor_key))

    main_hubs = git_main_json(BUNDLE_PATHS[1])["hubs"]
    head_hubs = load_head(BUNDLE_PATHS[1])["hubs"]
    errs.extend(compare_collection("hubs", main_hubs, head_hubs, hub_key))

    main_port = git_main_json(BUNDLE_PATHS[2])["startups"]
    head_port = load_head(BUNDLE_PATHS[2])["startups"]
    errs.extend(compare_collection("portfolio", main_port, head_port, portfolio_key))

    main_inv = git_main_json(BUNDLE_PATHS[3])["investors"]
    head_inv = load_head(BUNDLE_PATHS[3])["investors"]
    errs.extend(compare_collection("investors", main_inv, head_inv, investor_key))

    main_m = git_main_json(BUNDLE_PATHS[4])["mentors"]
    head_m = load_head(BUNDLE_PATHS[4])["mentors"]
    errs.extend(compare_collection("mentors", main_m, head_m, lambda m, i: mentor_key(m, i)))

    main_j = git_main_json(BUNDLE_PATHS[5])["jurors"]
    head_j = load_head(BUNDLE_PATHS[5])["jurors"]
    errs.extend(compare_collection("jury", main_j, head_j, lambda j, i: jury_key(j, i)))

    main_imd = git_main_json(BUNDLE_PATHS[6])
    head_imd = load_head(BUNDLE_PATHS[6])
    errs.extend(compare_collection("imd_curated", main_imd, head_imd, idea_key))

    main_epic = git_main_json(BUNDLE_PATHS[7])
    head_epic = load_head(BUNDLE_PATHS[7])
    errs.extend(compare_collection("epic_curated", main_epic, head_epic, idea_key))

    errs.extend(verify_onepagers())

    if errs:
        print("VERIFY FAILED:")
        for e in errs[:50]:
            print(" ", e)
        if len(errs) > 50:
            print(f"  ... +{len(errs) - 50} more")
        return 1

    print("VERIFY OK: record counts and non-location fields match origin/main for all bundles.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
