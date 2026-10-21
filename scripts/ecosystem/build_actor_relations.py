#!/usr/bin/env python3
"""Build vetted actor-to-actor relations for ecosystem cards (public sources only)."""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERIFIED_CSV = REPO / "ops" / "ecosystem" / "actor_relations_verified.csv"
OUT_JSON = REPO / "static" / "ecosystem" / "data" / "actor_relations.json"
REVIEW_CSV = REPO / "ops" / "ecosystem" / "actor_relations_review.csv"
ACTORS_JSON = REPO / "static" / "ecosystem" / "data" / "actors.json"

ALLOWED_TYPES = frozenset(
    {
        "partnership",
        "funding",
        "program_participation",
        "membership",
        "parent_subsidiary",
        "co_organized_event",
        "hub_startup",
    }
)

SENSITIVE = [
    re.compile(r"@[\w.-]+\.\w+"),
    re.compile(r"drive\.google\.com", re.I),
    re.compile(r"docs\.google\.com", re.I),
    re.compile(r"canva\.com/design", re.I),
]

CSV_FIELDS = [
    "from_id",
    "to_id",
    "type",
    "description",
    "source_url",
    "source_title",
    "confidence",
]


def load_actor_ids() -> set[str]:
    actors = json.loads(ACTORS_JSON.read_text(encoding="utf-8"))
    return {a["id"] for a in actors}


def scrub_url(url: str) -> str:
    u = url.strip()
    for pat in SENSITIVE:
        if pat.search(u):
            raise ValueError(f"sensitive URL rejected: {u}")
    if not u.startswith("http"):
        raise ValueError(f"source_url must be http(s): {u}")
    return u


def read_verified_rows() -> list[dict[str, str]]:
    if not VERIFIED_CSV.is_file():
        raise SystemExit(f"missing {VERIFIED_CSV}")
    rows: list[dict[str, str]] = []
    with VERIFIED_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not any((row.get(k) or "").strip() for k in CSV_FIELDS):
                continue
            rows.append({k: (row.get(k) or "").strip() for k in CSV_FIELDS})
    return rows


def build() -> dict:
    actor_ids = load_actor_ids()
    accessed = date.today().isoformat()
    relations: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for row in read_verified_rows():
        for k in CSV_FIELDS:
            if not row.get(k):
                raise ValueError(f"missing {k} in row {row}")
        if row["type"] not in ALLOWED_TYPES:
            raise ValueError(f"invalid type {row['type']}")
        if row["from_id"] not in actor_ids or row["to_id"] not in actor_ids:
            raise ValueError(f"unknown actor id in {row}")
        if row["from_id"] == row["to_id"]:
            raise ValueError(f"self-loop: {row}")
        key = (row["from_id"], row["to_id"], row["type"])
        if key in seen:
            continue
        seen.add(key)
        url = scrub_url(row["source_url"])
        conf = row["confidence"].lower()
        if conf not in {"high", "medium"}:
            raise ValueError(f"confidence must be high|medium: {row}")
        relations.append(
            {
                "from_id": row["from_id"],
                "to_id": row["to_id"],
                "type": row["type"],
                "description": row["description"],
                "source_url": url,
                "source_title": row["source_title"],
                "date_accessed": accessed,
                "confidence": conf,
            }
        )

    relations.sort(key=lambda r: (r["from_id"], r["to_id"], r["type"]))
    bundle = {
        "version": 1,
        "source": str(VERIFIED_CSV.relative_to(REPO)),
        "date_built": accessed,
        "count": len(relations),
        "relations": relations,
    }
    return bundle


def write_review_csv(relations: list[dict]) -> None:
    REVIEW_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "from_id",
        "to_id",
        "type",
        "description",
        "source_url",
        "source_title",
        "date_accessed",
        "confidence",
    ]
    with REVIEW_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in relations:
            w.writerow({k: r[k] for k in fields})


def main() -> int:
    bundle = build()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(bundle, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_review_csv(bundle["relations"])
    print(json.dumps({"count": bundle["count"], "out": str(OUT_JSON)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
