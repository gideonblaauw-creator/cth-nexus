#!/usr/bin/env python3
"""
Tag 25 selected Colombia startups with `selected:clp26` in BookStack.

Usage:
    python tag_selected_startups.py                  # dry-run (default)
    python tag_selected_startups.py --apply           # actually tag pages

Reads:
  - CLP26_Colombia_Selected_Startups.xlsx (25 selected startups)
  - clp26_colombia_ideas.json (80 Colombia applications with bookstack_page_id)

Requires BOOKSTACK_TOKEN env var (or in ../.env).
"""
import os
import sys
import json
import re
import argparse

import openpyxl

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from api.handlers.bookstack import BookStackClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
PROJECT_DIR = os.path.join(SCRIPT_DIR, "..", "..")
XLSX_PATH = os.environ.get("XLSX_PATH") or (
    os.path.join(DATA_DIR, "CLP26_Colombia_Selected_Startups.xlsx")
    if os.path.exists(os.path.join(DATA_DIR, "CLP26_Colombia_Selected_Startups.xlsx"))
    else os.path.join(PROJECT_DIR, "CLP26_Colombia_Selected_Startups.xlsx")
)
JSON_PATH = os.environ.get("JSON_PATH") or (
    os.path.join(DATA_DIR, "clp26_colombia_ideas.json")
    if os.path.exists(os.path.join(DATA_DIR, "clp26_colombia_ideas.json"))
    else os.path.join(PROJECT_DIR, "clp26_colombia_ideas.json")
)


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def normalize(name):
    name = name.strip().strip('"').strip("'")
    name = re.sub(r"\b(s\.?a\.?s\.?|b\.?i\.?c\.?|ltda|s\.?a\.?)\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\s+", " ", name).strip().lower()
    return name


def load_selected_startups():
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    wb.close()
    result = []
    for row in rows:
        if not row or not row[1]:
            continue
        result.append({
            "rank": row[0],
            "name": str(row[1]).strip(),
            "category": str(row[2] or ""),
            "email": str(row[3] or ""),
            "score": row[4],
            "track": str(row[5] or ""),
        })
    return result


def load_ideas_json():
    with open(JSON_PATH) as f:
        return json.load(f)


def match_startups(selected, ideas):
    idea_index = {}
    for idea in ideas:
        key = normalize(idea["startup_name"])
        idea_index[key] = idea

    matches = []
    for sel in selected:
        sel_norm = normalize(sel["name"])
        best = None
        for key, idea in idea_index.items():
            if sel_norm == key or sel_norm in key or key in sel_norm:
                best = idea
                break
        if not best:
            tokens = sel_norm.split()
            for key, idea in idea_index.items():
                if tokens[0] in key:
                    best = idea
                    break
        matches.append({
            "selected": sel,
            "idea": best,
            "matched": best is not None,
        })
    return matches


def track_tag_value(track_str):
    if "principal" in track_str.lower() or "ranking" in track_str.lower():
        return "ranking_principal"
    if "uec" in track_str.lower() or "pre-seleccionado" in track_str.lower():
        return "uec"
    return "other"


def print_match_table(matches):
    print(f"\n{'#':>3}  {'Selected Name':<42} {'Matched To':<42} {'Page ID':>8}  {'Track':<20}")
    print("-" * 120)
    for i, m in enumerate(matches, 1):
        sel_name = m["selected"]["name"][:40]
        if m["matched"]:
            idea_name = m["idea"]["startup_name"][:40]
            page_id = m["idea"]["bookstack_page_id"]
        else:
            idea_name = "*** NO MATCH ***"
            page_id = "-"
        track = track_tag_value(m["selected"]["track"])
        print(f"{i:>3}  {sel_name:<42} {idea_name:<42} {str(page_id):>8}  {track:<20}")

    matched = sum(1 for m in matches if m["matched"])
    print(f"\nMatched: {matched}/{len(matches)}")
    if matched < len(matches):
        print("WARNING: Some startups could not be matched. Review manually.")


def apply_tags(matches, client):
    results = []
    for m in matches:
        if not m["matched"]:
            results.append({"name": m["selected"]["name"], "status": "skipped", "reason": "no match"})
            continue

        page_id = m["idea"]["bookstack_page_id"]
        track = track_tag_value(m["selected"]["track"])

        try:
            page = client.get_page(page_id)
            existing_tags = page.get("tags", [])

            has_selected = any(
                t.get("name") == "selected" and t.get("value") == "clp26"
                for t in existing_tags
            )

            new_tags = [{"name": t["name"], "value": t["value"]} for t in existing_tags]
            if not has_selected:
                new_tags.append({"name": "selected", "value": "clp26"})

            has_track = any(t.get("name") == "track" for t in existing_tags)
            if not has_track:
                new_tags.append({"name": "track", "value": track})

            if len(new_tags) > len(existing_tags):
                client.update_page_tags(page_id, new_tags)
                status = "tagged"
            else:
                status = "already_tagged"

            results.append({
                "name": m["selected"]["name"],
                "page_id": page_id,
                "status": status,
                "tags_before": len(existing_tags),
                "tags_after": len(new_tags),
            })
            print(f"  [{status:>14}] {m['selected']['name']} (page {page_id})")

        except Exception as e:
            results.append({"name": m["selected"]["name"], "page_id": page_id, "status": "error", "error": str(e)})
            print(f"  [{'error':>14}] {m['selected']['name']}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Tag selected CLP26 startups in BookStack")
    parser.add_argument("--apply", action="store_true", help="Actually apply tags (default is dry-run)")
    args = parser.parse_args()

    load_env()

    print("Loading selected startups from Excel...")
    selected = load_selected_startups()
    print(f"  {len(selected)} selected startups loaded")

    print("Loading ideas JSON...")
    ideas = load_ideas_json()
    print(f"  {len(ideas)} Colombia ideas loaded")

    print("\nMatching selected startups to BookStack pages...")
    matches = match_startups(selected, ideas)
    print_match_table(matches)

    if not args.apply:
        print("\nDRY RUN — no tags applied. Use --apply to tag pages.")
        return

    print("\nApplying tags...")
    client = BookStackClient()
    results = apply_tags(matches, client)

    tagged = sum(1 for r in results if r["status"] == "tagged")
    already = sum(1 for r in results if r["status"] == "already_tagged")
    errors = sum(1 for r in results if r["status"] == "error")
    print(f"\nDone: {tagged} tagged, {already} already tagged, {errors} errors")


if __name__ == "__main__":
    main()
