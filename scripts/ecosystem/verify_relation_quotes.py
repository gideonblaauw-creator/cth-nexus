#!/usr/bin/env python3
"""CI check: public graph relations must have verbatim quotes on source_url pages."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from relation_source_fetch import (
    challenge_topic_in_evidence,
    fetch_body,
    label_matches_text,
    quote_in_body,
)

ROOT = Path(__file__).resolve().parents[2]
REL_PATH = ROOT / "static/ecosystem/data/relations.json"
ACTORS_PATH = ROOT / "static/ecosystem/data/actors.json"
EVIDENCE_PATH = ROOT / "ops/ecosystem/graph_relation_evidence.json"


def main() -> int:
    rels = json.loads(REL_PATH.read_text(encoding="utf-8"))
    actors = {a["id"]: a for a in json.loads(ACTORS_PATH.read_text(encoding="utf-8"))}
    catalog = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    by_key = {(r["source"], r["target"], r["type"]): r for r in catalog["relations"]}
    graph_keys = {(r["source"], r["target"], r["type"]) for r in rels}

    public = [r for r in rels if r.get("verified") is True and r.get("source_url")]
    errors: list[str] = []

    if any(r["source"] == r["target"] for r in rels):
        errors.append("self-loop edges must be removed from relations.json")

    for key in by_key:
        if key not in graph_keys:
            errors.append(f"catalog entry not present in relations.json: {key}")

    for r in public:
        key = (r["source"], r["target"], r["type"])
        cat = by_key.get(key)
        if not cat:
            errors.append(f"missing catalog entry for public edge {key}")
            continue
        if r.get("evidence") != cat.get("evidence"):
            errors.append(f"evidence drift on {key}")
        url = r["source_url"]
        try:
            body = fetch_body(url)
        except Exception as exc:
            errors.append(f"fetch failed {key}: {exc}")
            continue
        ev = r.get("evidence") or ""
        if not quote_in_body(ev, body):
            errors.append(f"verbatim quote not found on page for {key}")

        src_row = actors.get(r["source"], {})
        tgt_row = actors.get(r["target"], {})
        src_name = src_row.get("name") or r["source"]
        tgt_name = tgt_row.get("name") or r["target"]
        if r["type"] == "works_on_challenge":
            if not label_matches_text(body, src_name) or not label_matches_text(ev, src_name):
                errors.append(f"works_on_challenge actor naming failed for {key}")
            elif not challenge_topic_in_evidence(r["target"], ev):
                errors.append(f"works_on_challenge topic keywords failed for {key}")
        elif r["type"] == "administered_by":
            pol_name = src_name
            if not label_matches_text(ev, pol_name) or not label_matches_text(ev, tgt_name):
                errors.append(f"administered_by naming check failed for {key}")
        else:
            if not label_matches_text(ev, src_name) or not label_matches_text(ev, tgt_name):
                errors.append(f"dual-actor naming check failed for {key}")

    hidden = [r for r in rels if not (r.get("verified") is True and r.get("source_url"))]
    if any(r.get("verified") is not False for r in hidden):
        errors.append("non-public edges must set verified:false")

    if errors:
        print("verify_relation_quotes FAILED:\n" + "\n".join(f"- {e}" for e in errors))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "public": len(public),
                "hidden": len(hidden),
                "catalog": len(catalog["relations"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
