#!/usr/bin/env python3
"""CI check: public graph relations must have verbatim quotes on source_url pages.

evidence_type defaults to public_quote. cth_cohort rows (Gideon decision 25,
22 Oct 2026) skip the live quote fetch only when the programme is CTH-run, the
row has no personal email, phone, or home address, and any money or pilot
outcome has consent_ref. Otherwise they fail.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from cth_cohort_guardrails import (
    EVIDENCE_TYPE_COHORT,
    EVIDENCE_TYPE_PUBLIC,
    cth_cohort_blockers,
    evidence_type_of,
    personal_contact_kinds,
    programme_ids_from_config,
)
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
SCHEMA_PATH = ROOT / "ops/ecosystem/graph_relation_evidence.schema.json"
PROGRAMMES_PATH = ROOT / "ops/ecosystem/cth_run_programmes.json"


def load_evidence_type_schema() -> tuple[str, set[str]]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    prop = schema["properties"]["evidence_type"]
    allowed = set(prop["enum"])
    default = prop.get("default") or EVIDENCE_TYPE_PUBLIC
    if default not in allowed:
        raise SystemExit(f"evidence_type default {default!r} is not in the schema enum")
    return default, allowed


def naming_errors(rel: dict, actors: dict, body: str | None) -> list[str]:
    """Naming checks. body is None when the live page was not fetched."""
    key = (rel["source"], rel["target"], rel["type"])
    ev = rel.get("evidence") or ""
    src_row = actors.get(rel["source"], {})
    tgt_row = actors.get(rel["target"], {})
    src_name = src_row.get("name") or rel["source"]
    tgt_name = tgt_row.get("name") or rel["target"]
    if rel["type"] == "works_on_challenge":
        ev_ok = label_matches_text(ev, src_name)
        body_ok = True if body is None else label_matches_text(body, src_name)
        if not body_ok or not ev_ok:
            return [f"works_on_challenge actor naming failed for {key}"]
        if not challenge_topic_in_evidence(rel["target"], ev):
            return [f"works_on_challenge topic keywords failed for {key}"]
        return []
    if rel["type"] == "administered_by":
        if not label_matches_text(ev, src_name) or not label_matches_text(ev, tgt_name):
            return [f"administered_by naming check failed for {key}"]
        return []
    if not label_matches_text(ev, src_name) or not label_matches_text(ev, tgt_name):
        return [f"dual-actor naming check failed for {key}"]
    return []


def main() -> int:
    default_type, allowed_types = load_evidence_type_schema()
    programmes = programme_ids_from_config(
        json.loads(PROGRAMMES_PATH.read_text(encoding="utf-8"))
    )
    if not programmes:
        print("verify_relation_quotes FAILED:\n- CTH-run programme config is empty")
        return 1

    rels = json.loads(REL_PATH.read_text(encoding="utf-8"))
    actors = {a["id"]: a for a in json.loads(ACTORS_PATH.read_text(encoding="utf-8"))}
    catalog = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    by_key = {(r["source"], r["target"], r["type"]): r for r in catalog["relations"]}
    graph_keys = {(r["source"], r["target"], r["type"]) for r in rels}

    public = [r for r in rels if r.get("verified") is True and r.get("source_url")]
    errors: list[str] = []
    public_quote = 0
    cth_cohort = 0

    if any(r["source"] == r["target"] for r in rels):
        errors.append("self-loop edges must be removed from relations.json")

    for r in rels:
        if r.get("type") == "theme_match" or "theme_match" in r:
            errors.append(
                "theme_match is not a graph relation "
                f"({r.get('source')}, {r.get('target')}, {r.get('type')})"
            )
    for row in catalog.get("relations", []):
        if row.get("type") == "theme_match" or "theme_match" in row:
            errors.append(
                "theme_match is not an evidence-catalog relation "
                f"({row.get('source')}, {row.get('target')}, {row.get('type')})"
            )

    for key in by_key:
        if key not in graph_keys:
            errors.append(f"catalog entry not present in relations.json: {key}")

    for row in catalog["relations"]:
        etype = evidence_type_of(row, default_type)
        if etype not in allowed_types:
            key = (row.get("source"), row.get("target"), row.get("type"))
            errors.append(f"invalid evidence_type {etype!r} on {key}")

    for r in public:
        key = (r["source"], r["target"], r["type"])
        cat = by_key.get(key)
        if not cat:
            errors.append(f"missing catalog entry for public edge {key}")
            continue
        if r.get("evidence") != cat.get("evidence"):
            errors.append(f"evidence drift on {key}")
        etype = evidence_type_of(cat, default_type)
        rel_type = r.get("evidence_type")
        if rel_type not in (None, "") and evidence_type_of(r, default_type) != etype:
            errors.append(f"evidence_type drift on {key}")
        if etype not in allowed_types:
            continue
        if etype == EVIDENCE_TYPE_COHORT:
            blockers = cth_cohort_blockers(cat, programmes)
            edge_pii = [
                kind
                for kind in personal_contact_kinds(r)
                if not any(kind in reason for reason in blockers)
            ]
            if edge_pii:
                blockers.append("published edge has personal " + ", ".join(edge_pii))
            if blockers:
                errors.extend(f"cth_cohort {key}: {reason}" for reason in blockers)
                continue
            cth_cohort += 1
            errors.extend(naming_errors(r, actors, body=None))
            continue

        public_quote += 1
        url = r["source_url"]
        try:
            body = fetch_body(url)
        except Exception as exc:
            errors.append(f"fetch failed {key}: {exc}")
            continue
        ev = r.get("evidence") or ""
        if not quote_in_body(ev, body):
            errors.append(f"verbatim quote not found on page for {key}")
        errors.extend(naming_errors(r, actors, body))

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
                "public_quote": public_quote,
                "cth_cohort": cth_cohort,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
