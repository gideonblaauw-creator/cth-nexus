#!/usr/bin/env python3
"""Apply verbatim-evidence catalog to static/ecosystem/data/relations.json.

Public edges require a row in ops/ecosystem/graph_relation_evidence.json whose quote
was validated against source_url. Self-loop edges are removed from the bundle.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL_PATH = ROOT / "static" / "ecosystem" / "data" / "relations.json"
EVIDENCE_PATH = ROOT / "ops" / "ecosystem" / "graph_relation_evidence.json"
UNVERIFIED_MD = ROOT / "ops" / "ecosystem" / "UNVERIFIED-RELATIONS.md"

# Edges removed from the public catalog after a live quote check failed.
# Sync reprints these reasons so a later run does not drop them.
HIDDEN_REASONS: dict[tuple[str, str, str], str] = {
    (
        "pe-forest-trends",
        "challenge:PE-1-bosques",
        "works_on_challenge",
    ): (
        "Live check 2026-10-21: the catalog quote is not on "
        "https://www.forest-trends.org and the actor-name check failed."
    ),
    (
        "pe-profonanpe",
        "challenge:PE-1-bosques",
        "works_on_challenge",
    ): (
        "Source https://profonanpe.org.pe/ is unreachable from this host "
        "(connection times out). Hidden until the quote can be re-verified."
    ),
    (
        "pe-sunass",
        "challenge:PE-2-agua",
        "works_on_challenge",
    ): (
        "Live check 2026-10-22: the catalog quote is only the SUNASS name "
        "(\"Superintendencia Nacional de Servicios de Saneamiento - SUNASS\") "
        "and does not source the Agua & cuencas challenge."
    ),
    (
        "pe-utec-universidad-de-ingenieria-y-tecnologia",
        "pe-utec-ventures",
        "hosts",
    ): (
        "Source https://utecventures.com/ accepts TLS but the HTTP response "
        "hangs from this host. Hidden until the site responds reliably for "
        "verbatim quote verification."
    ),
}


def load_catalog() -> dict[tuple[str, str, str], dict[str, str]]:
    if not EVIDENCE_PATH.is_file():
        raise SystemExit(f"missing {EVIDENCE_PATH}; run scripts/ecosystem/build_graph_relation_evidence.py")
    data = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in data.get("relations", []):
        key = (row["source"], row["target"], row["type"])
        out[key] = row
    return out


def apply_verification() -> dict[str, int]:
    catalog = load_catalog()
    relations = json.loads(REL_PATH.read_text(encoding="utf-8"))
    before = len(relations)
    relations = [r for r in relations if r["source"] != r["target"]]
    removed_loops = before - len(relations)

    hidden: list[dict] = []
    verified = 0
    today = date.today().isoformat()

    for rel in relations:
        key = (rel["source"], rel["target"], rel["type"])
        meta = catalog.get(key)
        if meta:
            rel["verified"] = True
            rel["source_url"] = meta["source_url"]
            rel["source_title"] = meta.get("source_title") or ""
            rel["evidence"] = meta.get("evidence") or ""
            rel["date_accessed"] = today
            verified += 1
        else:
            rel["verified"] = False
            for k in ("source_url", "source_title", "evidence", "date_accessed", "source_note"):
                rel.pop(k, None)
            hidden.append(rel)

    REL_PATH.write_text(json.dumps(relations, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_unverified_md(hidden, verified, len(relations), removed_loops)
    return {
        "total": len(relations),
        "verified": verified,
        "hidden": len(hidden),
        "self_loops_removed": removed_loops,
    }


def write_unverified_md(
    hidden: list[dict], verified: int, total: int, removed_loops: int
) -> None:
    lines = [
        "# Unverified ecosystem graph relations",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Public graph edges must appear in `ops/ecosystem/graph_relation_evidence.json` "
        "with a **verbatim** quote present on `source_url` (checked by "
        "`scripts/ecosystem/verify_relation_quotes.py`). Self-loop edges are removed "
        "from the bundle rather than hidden.",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| Total edges in bundle | {total} |",
        f"| Public (verified + source_url + catalog quote) | {verified} |",
        f"| Hidden pending source | {len(hidden)} |",
        f"| Self-loops removed (this sync) | {removed_loops} |",
        "",
        f"Evidence catalog: `{EVIDENCE_PATH.relative_to(ROOT)}` ({verified} public rows).",
        "",
        "Policy bundle (`static/ecosystem/data/policy_relations.json`): separate story chapter; "
        "not modified by this sync.",
        "",
        "## Hidden edges",
        "",
        "| source | target | type |",
        "|--------|--------|------|",
    ]
    ordered = sorted(hidden, key=lambda x: (x["type"], x["source"], x["target"]))
    for r in ordered:
        lines.append(f"| `{r['source']}` | `{r['target']}` | `{r['type']}` |")
    lines.append("")
    noted = [
        r
        for r in ordered
        if (r["source"], r["target"], r["type"]) in HIDDEN_REASONS
    ]
    if noted:
        lines.extend(["## Why these edges are hidden", ""])
        for r in noted:
            reason = HIDDEN_REASONS[(r["source"], r["target"], r["type"])]
            lines.append(
                f"- `{r['source']}` → `{r['target']}` (`{r['type']}`): {reason}"
            )
        lines.append("")
    UNVERIFIED_MD.parent.mkdir(parents=True, exist_ok=True)
    UNVERIFIED_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    stats = apply_verification()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
