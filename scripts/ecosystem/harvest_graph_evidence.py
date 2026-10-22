#!/usr/bin/env python3
"""Harvest verbatim dual-actor quotes for graph edges (writes ops JSON draft)."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from relation_fields import strip_theme_match
from relation_source_fetch import (
    challenge_topic,
    fetch_body,
    name_tokens,
    norm_ws,
    quote_in_body,
)

ROOT = Path(__file__).resolve().parents[2]
REL = ROOT / "static/ecosystem/data/relations.json"
ACTORS = ROOT / "static/ecosystem/data/actors.json"
STORY = ROOT / "static/ecosystem/data/story-chapters.json"
CSV_PATH = ROOT / "ops/ecosystem/actor_relations_verified.csv"
OUT = ROOT / "ops/ecosystem/graph_relation_evidence.json"

CSV_GRAPH = {
    "hosts": ("program_participation",),
    "partner": ("partnership",),
    "runs_program": ("program_participation",),
    "cofunds": ("program_participation", "membership", "funding"),
    "part_of_group": ("parent_subsidiary",),
    "owns": ("parent_subsidiary",),
    "participates": ("program_participation",),
    "created": ("parent_subsidiary",),
    "runs_initiative": ("program_participation",),
    "oversees": ("program_participation",),
    "incubated": ("hub_startup", "program_participation", "co_organized_event"),
    "funds_layer": ("funding", "program_participation"),
    "regulates_layer": ("partnership", "program_participation"),
}

EXTRA_ALIASES: dict[str, list[str]] = {
    "pe-proinnovate-startup-peru": ["ProInnóvate", "Startup Perú", "ProInnovate"],
    "pe-produce-ministerio-de-la-produccion": ["PRODUCE", "Ministerio de la Producción"],
    "pe-mef-ministerio-de-economia-y-finanzas": ["MEF", "Economía y Finanzas"],
    "pe-minam-ministerio-del-ambiente": ["MINAM"],
    "co-ipse": ["IPSE"],
    "co-fenoge": ["FENOGE"],
    "co-upme": ["UPME"],
    "co-minenergia": ["Ministerio de Minas y Energía", "Minenergia"],
    "pe-emprende-up-climatech-rein-hub-peru": ["Emprende UP", "ClimaTech", "REIN Hub"],
    "pe-cleantechhub": ["CleantechHUB", "CleantechHUBs"],
    "pe-nexum-pucp": ["Nexum"],
    "pe-rebike-up": ["Rebike", "ReBike"],
    "pe-yakusmart": ["YakuSmart"],
    "pe-yakufil": ["Yakufil"],
}


def labels(actor_id: str, by_id: dict) -> list[str]:
    a = by_id.get(actor_id) or {}
    out = [a.get("name") or actor_id]
    out.extend(EXTRA_ALIASES.get(actor_id, []))
    return [x for x in out if x]


def csv_index() -> dict[tuple[str, str, str], dict]:
    out = {}
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out[(row["from_id"], row["to_id"], row["type"])] = row
    return out


def csv_for_edge(src: str, tgt: str, typ: str, idx: dict) -> dict | None:
    for ct in CSV_GRAPH.get(typ, ()):
        hit = idx.get((src, tgt, ct)) or idx.get((tgt, src, ct))
        if hit:
            return hit
    return None


def find_quote(body: str, la: list[str], lb: list[str]) -> str | None:
    text = norm_ws(body)
    sents = re.split(r"(?<=[.!?])\s+", text)
    for s in sents:
        if len(s) < 35 or len(s) > 600:
            continue
        ok_a = any(names_ok(s, x) for x in la)
        ok_b = any(names_ok(s, x) for x in lb)
        if ok_a and ok_b:
            return s.strip()
    return None


def names_ok(sentence: str, label: str) -> bool:
    tl = sentence.lower()
    tokens = name_tokens(label)
    if not tokens:
        return label.lower() in tl
    hits = sum(1 for t in tokens if t.lower() in tl)
    need = min(2, len(tokens))
    return hits >= need


def main() -> None:
    rels = strip_theme_match(json.loads(REL.read_text(encoding="utf-8")))
    by_id = {a["id"]: a for a in json.loads(ACTORS.read_text(encoding="utf-8"))}
    story = json.loads(STORY.read_text(encoding="utf-8"))
    cidx = csv_index()
    accepted = []
    tried = 0
    for r in rels:
        if r["source"] == r["target"]:
            continue
        src, tgt, typ = r["source"], r["target"], r["type"]
        tried += 1
        csv_row = csv_for_edge(src, tgt, typ, cidx)
        url = (r.get("source_url") or (csv_row or {}).get("source_url") or "").strip()
        if not url:
            continue
        la = labels(src, by_id)
        if typ == "works_on_challenge":
            lb = [challenge_topic(tgt, story), "bosques", "agua", "agua", "hídric"]
        elif typ == "administered_by":
            lb = labels(tgt, by_id)
            la = labels(src, by_id)
        else:
            lb = labels(tgt, by_id)
        try:
            body = fetch_body(url)
        except Exception:
            continue
        quote = None
        if csv_row and quote_in_body(csv_row["description"], body):
            quote = norm_ws(csv_row["description"])
        if not quote:
            quote = find_quote(body, la, lb)
        if not quote or not quote_in_body(quote, body):
            continue
        accepted.append(
            {
                "source": src,
                "target": tgt,
                "type": typ,
                "source_url": url,
                "source_title": (csv_row or {}).get("source_title") or url,
                "evidence": quote,
            }
        )
    OUT.write_text(
        json.dumps({"version": 1, "relations": accepted}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"tried": tried, "accepted": len(accepted), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
