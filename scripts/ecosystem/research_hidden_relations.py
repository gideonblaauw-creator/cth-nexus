#!/usr/bin/env python3
"""Probe hidden graph edges for verbatim dual-actor quotes on candidate URLs."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from relation_source_fetch import (
    challenge_topic_in_evidence,
    fetch_body,
    label_matches_text,
    quote_in_body,
)

ROOT = Path(__file__).resolve().parents[2]
REL = ROOT / "static/ecosystem/data/relations.json"
ACTORS = ROOT / "static/ecosystem/data/actors.json"
CSV_PATH = ROOT / "ops/ecosystem/actor_relations_verified.csv"
EVIDENCE = ROOT / "ops/ecosystem/graph_relation_evidence.json"

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
    "administered_by": (),
    "works_on_challenge": (),
}

# Extra candidate URLs per edge key (graph type)
EXTRA_URLS: dict[tuple[str, str, str], list[str]] = {
    (
        "pe-proinnovate-startup-peru",
        "pe-nexum-pucp",
        "cofunds",
    ): [
        "https://www.gob.pe/institucion/proinnovate/noticias/648295-incubadoras-y-aceleradoras-de-negocios-fortalecidas-por-proinnovate-impulsaron-el-despegue-comercial-e-internacionalizacion-de-startups",
    ],
    (
        "pe-minam-ministerio-del-ambiente",
        "pe-programa-bosques-minam",
        "runs_program",
    ): ["https://www.gob.pe/bosques"],
    (
        "pe-minam-ministerio-del-ambiente",
        "challenge:PE-1-bosques",
        "works_on_challenge",
    ): ["https://www.gob.pe/bosques"],
    (
        "pe-policy-programa-bosques-minam",
        "pe-minam-ministerio-del-ambiente",
        "administered_by",
    ): ["https://www.gob.pe/bosques"],
    (
        "pe-policy-ley-marco-cambio-climatico-30754",
        "pe-minam-ministerio-del-ambiente",
        "administered_by",
    ): [
        "https://www.gob.pe/institucion/minam/informes-publicaciones/698117-ley-marco-sobre-cambio-climatico"
    ],
    (
        "pe-policy-startup-peru-proinnovate",
        "pe-proinnovate-startup-peru",
        "administered_by",
    ): ["https://www.gob.pe/proinnovate"],
    (
        "pe-policy-startup-peru-proinnovate",
        "pe-produce-ministerio-de-la-produccion",
        "administered_by",
    ): ["https://www.gob.pe/proinnovate"],
    (
        "pe-policy-taxonomia-verde-bonos",
        "pe-sbs-superintendencia-de-banca-seguros-y-afp",
        "administered_by",
    ): [
        "https://www.sbs.gob.pe/presentacion-de-la-taxonomia-verde-del-sistema-financiero-peruano"
    ],
    (
        "co-minenergia",
        "co-ipse",
        "regulates_layer",
    ): [
        "https://ipse.gov.co/documento_prensa/documento/documentos_de_%20investigacion/Art%C3%ADculo%20Mundoel%C3%A9ctrico.pdf"
    ],
    (
        "co-gcf-green-climate-fund",
        "co-ipse",
        "funds_layer",
    ): [
        "https://ipse.gov.co/documento_prensa/documento/publicaciones/2023/GU%C3%8DA%20INVERSI%C3%93N%20PRIVADA%202023.pdf"
    ],
    (
        "pe-profonanpe",
        "challenge:PE-1-bosques",
        "works_on_challenge",
    ): ["https://profonanpe.org.pe/"],
    (
        "pe-serfor",
        "challenge:PE-1-bosques",
        "works_on_challenge",
    ): ["https://www.gob.pe/serfor"],
    (
        "pe-sernanp",
        "challenge:PE-1-bosques",
        "works_on_challenge",
    ): ["https://www.gob.pe/sernanp"],
}


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def csv_index() -> dict[tuple[str, str, str], dict]:
    out: dict[tuple[str, str, str], dict] = {}
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


def find_sentence(body: str, src_name: str, tgt_name: str, challenge_id: str | None) -> str | None:
    text = norm_ws(body)
    chunks = re.split(r"(?<=[.!?])\s+", text)
    for s in chunks:
        if len(s) < 40 or len(s) > 700:
            continue
        if challenge_id:
            if not label_matches_text(s, src_name):
                continue
            if not challenge_topic_in_evidence(challenge_id, s):
                continue
            return s.strip()
        if label_matches_text(s, src_name) and label_matches_text(s, tgt_name):
            return s.strip()
    # sliding window for broken PDF/HTML lines
    words = text.split()
    for width in range(12, min(120, len(words))):
        for i in range(0, len(words) - width):
            s = " ".join(words[i : i + width])
            if len(s) < 40:
                continue
            if challenge_id:
                if label_matches_text(s, src_name) and challenge_topic_in_evidence(challenge_id, s):
                    return s
            elif label_matches_text(s, src_name) and label_matches_text(s, tgt_name):
                return s
    return None


def main() -> None:
    actors = {a["id"]: a for a in json.loads(ACTORS.read_text(encoding="utf-8"))}
    catalog = {
        (r["source"], r["target"], r["type"])
        for r in json.loads(EVIDENCE.read_text(encoding="utf-8"))["relations"]
    }
    hidden = [
        r
        for r in json.loads(REL.read_text(encoding="utf-8"))
        if not r.get("verified") and (r["source"], r["target"], r["type"]) not in catalog
    ]
    idx = csv_index()
    hits: list[dict] = []
    fails: list[str] = []

    for rel in hidden:
        key = (rel["source"], rel["target"], rel["type"])
        src_name = actors.get(rel["source"], {}).get("name") or rel["source"]
        tgt_name = actors.get(rel["target"], {}).get("name") or rel["target"]
        challenge_id = rel["target"] if rel["type"] == "works_on_challenge" else None
        if challenge_id:
            tgt_name = ""

        urls: list[str] = []
        row = csv_for_edge(*key, idx)
        if row and row.get("source_url"):
            urls.append(row["source_url"].strip())
        urls.extend(EXTRA_URLS.get(key, []))
        if rel["source"].startswith("pe-policy-") and not urls:
            pol = actors.get(rel["source"], {})
            if pol.get("website"):
                urls.append(pol["website"])
        seen = set()
        urls = [u for u in urls if u and u not in seen and not seen.add(u)]

        found = False
        for url in urls:
            try:
                body = fetch_body(url)
            except Exception as exc:
                fails.append(f"{key} fetch {url}: {exc}")
                continue
            sent = find_sentence(body, src_name, tgt_name, challenge_id)
            if not sent:
                continue
            if not quote_in_body(sent, body):
                continue
            hits.append(
                {
                    "source": rel["source"],
                    "target": rel["target"],
                    "type": rel["type"],
                    "source_url": url,
                    "source_title": (row or {}).get("source_title") or url,
                    "evidence": sent,
                }
            )
            found = True
            break
        if not found and not urls:
            fails.append(f"{key}: no candidate URL")

    out_path = ROOT / "ops/ecosystem/research_hidden_hits.json"
    out_path.write_text(json.dumps({"hits": hits, "fail_count": len(fails)}, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"hidden": len(hidden), "new_hits": len(hits), "out": str(out_path)}, indent=2))
    for h in hits:
        print("HIT", h["type"], h["source"][:30], "->", h["target"][:30])
        print(" ", h["evidence"][:120], "...")


if __name__ == "__main__":
    main()
