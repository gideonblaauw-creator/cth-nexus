#!/usr/bin/env python3
"""Generate Peru climate policy wiki markdown (BookStack + docs/wiki/peru-policies/)."""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POLICIES = ROOT / "data/policies.json"
RELS = ROOT / "policy_relations.json"
ACTORS = ROOT / "docs/ecosystem/prototype/data/actors.json"
MAPA_POLICIES = ROOT / "data/ecosystem-policy/staging/peru-mapa-actores-2026/policies.json"
OUT = ROOT / "docs/wiki/peru-policies"
MANIFEST = OUT / "bookstack-manifest.json"

MAPA_CITE = (
    "Jennifer González, *Mapa de Actores & Aliados del Emprendimiento Climático del Perú* "
    "(20 Oct 2026). Staging JSON: `data/ecosystem-policy/staging/peru-mapa-actores-2026/`."
)

CHALLENGE_LABEL = {
    "challenge:PE-1-bosques": "Bosques & Amazonía (PE-1)",
    "challenge:PE-2-agua": "Agua & cuencas (PE-2)",
}

ISSUER_WEB: dict[str, str] = {}


def load_issuer_websites() -> None:
    actors = json.loads(ACTORS.read_text(encoding="utf-8"))
    for a in actors:
        if a.get("country") != "Peru" or a.get("category") != "government":
            continue
        web = (a.get("website") or "").strip()
        if web:
            ISSUER_WEB[a["id"]] = web
    # Common ministries (gob.pe)
    defaults = {
        "minam": "https://www.gob.pe/minam",
        "minem": "https://www.gob.pe/minem",
        "midagri": "https://www.gob.pe/midagri",
        "produce": "https://www.gob.pe/produce",
        "mef": "https://www.gob.pe/mef",
    }
    for a in actors:
        if a.get("country") != "Peru":
            continue
        aid = a["id"]
        if aid in ISSUER_WEB:
            continue
        name = (a.get("name") or "").lower()
        for key, url in defaults.items():
            if key in name.replace(" ", ""):
                ISSUER_WEB[aid] = url
                break


def esc_cell(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ")


def status_label(p: dict) -> str:
    if p.get("registry") == "SINIA" or p.get("sinia_number"):
        return "Vigente"
    st = p.get("status") or "in_force"
    return {"in_force": "Vigente", "active": "Activo", "submitted": "Presentado"}.get(st, st)


def type_label(p: dict) -> str:
    if p.get("sinia_type"):
        return str(p["sinia_type"])
    return p.get("instrument") or "—"


def number_label(p: dict) -> str:
    if p.get("sinia_number"):
        return str(p["sinia_number"])
    m = re.search(r"(?:N°|Nº|Ley|Decreto)[^\d]*(\d[\d./-]*)", p.get("name") or "", re.I)
    return m.group(1) if m else "—"


def date_label(p: dict) -> str:
    if p.get("sinia_date"):
        return str(p["sinia_date"])[:10]
    if p.get("year"):
        return str(p["year"])
    return "—"


def issuer_with_web(p: dict, verified_issuers: dict[str, list[str]]) -> str:
    parts = []
    for name in p.get("issuing_authority") or []:
        parts.append(name)
    for aid, aname in verified_issuers.get(p["id"], []):
        web = ISSUER_WEB.get(aid)
        if web:
            parts.append(f"[{aname}]({web})")
        else:
            parts.append(aname)
    if not parts:
        return "—"
    return "; ".join(dict.fromkeys(parts))


def challenge_links(p: dict, ch_map: dict[str, list[tuple[str, bool]]]) -> str:
    items = ch_map.get(p["id"], [])
    if not items:
        return "—"
    out = []
    for label, suggested in items:
        out.append(f"{label} *(Sugerido)*" if suggested else label)
    return "; ".join(out)


def build_row(p, verified_issuers, ch_map):
    return [
        esc_cell(p.get("name") or ""),
        esc_cell(number_label(p)),
        esc_cell(type_label(p)),
        esc_cell(status_label(p)),
        esc_cell(date_label(p)),
        esc_cell(issuer_with_web(p, verified_issuers)),
        esc_cell(challenge_links(p, ch_map)),
        esc_cell(p.get("source_url") or "—"),
        esc_cell(p.get("registry") or "—"),
    ]


def mapa_extra_rows() -> list[dict]:
    if not MAPA_POLICIES.exists():
        return []
    rows = json.loads(MAPA_POLICIES.read_text(encoding="utf-8"))
    extras = []
    for r in rows:
        extras.append(
            {
                "id": f"mapa:{r['id']}",
                "name": r.get("name") or "",
                "sinia_number": r.get("instrument_id"),
                "sinia_type": r.get("kind"),
                "sinia_date": str(r.get("year") or ""),
                "issuing_authority": [],
                "source_url": (r.get("urls") or [None])[0] or "—",
                "registry": "Mapa de Actores 2026 (staging)",
                "status": "in_force",
                "instrument": r.get("kind"),
                "year": r.get("year"),
            }
        )
    return extras


def related_policy_ids(p: dict, policies_by_id: dict) -> set[str]:
    ids = {p["id"]}
    num = str(p.get("sinia_number") or "")
    if num:
        for op in policies_by_id.values():
            if str(op.get("sinia_number") or "") == num:
                ids.add(op["id"])
    for legacy in (
        "policy:pe-ley-30754-2018",
        "policy:pe-ds-013-2019-minam",
        "policy:pe-ndc-2020",
        "policy:pe-encc-2050-2024",
        "policy:pe-startup-peru-clima",
    ):
        if legacy in policies_by_id and num and num.replace("-", "") in (policies_by_id[legacy].get("name") or ""):
            ids.add(legacy)
    return ids


def key_policy_detail(
    pid: str, policies_by_id: dict, rels, verified_issuers, actor_names: dict[str, str]
) -> str:
    p = policies_by_id.get(pid)
    if not p:
        return f"# Missing policy `{pid}`\n"
    rel_ids = related_policy_ids(p, policies_by_id)
    lines = [
        f"# {p.get('name')}",
        "",
        f"**Nexus id:** `{pid}`  ",
        f"**Registry:** {p.get('registry', '—')}  ",
        f"**Status:** {status_label(p)}  ",
        f"**Source:** [{p.get('source_url')}]({p.get('source_url')})  ",
        "",
        "## Mapa de Actores (staging)",
        "",
        MAPA_CITE,
        "",
        "## Issuing institutions (verified `issues_policy` only when named on source)",
        "",
    ]
    ip = [
        r
        for r in rels
        if r["type"] == "issues_policy" and r["target"] in rel_ids and r.get("verified")
    ]
    if ip:
        for r in ip:
            aid = r["source"]
            aname = actor_names.get(aid, aid)
            web = ISSUER_WEB.get(aid, "")
            if web:
                lines.append(f"- [{aname}]({web}) — {r.get('notes', '')}")
            else:
                lines.append(f"- `{aid}` — {r.get('notes', '')}")
    else:
        lines.append("- *(No verified government issuer edge in Nexus graph for this id.)*")

    lines.extend(["", "## Linked challenges", ""])
    ac = [r for r in rels if r["type"] == "addresses_challenge" and r["source"] in rel_ids]
    if ac:
        for r in ac:
            ch = CHALLENGE_LABEL.get(r["target"], r["target"])
            tag = " **Sugerido**" if r.get("suggested") else ""
            lines.append(f"- {ch}{tag}")
    else:
        lines.append("- —")

    if p.get("descriptors"):
        lines.extend(["", "## SINIA descriptors", "", ", ".join(p["descriptors"])])
    if p.get("pdf_url"):
        lines.extend(["", "## PDF", "", f"[Documento]({p['pdf_url']})"])
    if p.get("sectors"):
        lines.extend(["", "## Sectors (Nexus tags)", "", ", ".join(p["sectors"])])
    lines.append("")
    return "\n".join(lines)


def find_sinia_policy(policies: list[dict], number_sub: str, name_hint: str) -> dict | None:
    for p in policies:
        if p.get("country") != "Peru":
            continue
        num = str(p.get("sinia_number") or "")
        if number_sub in num and name_hint.lower() in (p.get("name") or "").lower():
            return p
    for p in policies:
        if p.get("country") != "Peru":
            continue
        if number_sub in str(p.get("sinia_number") or "") and "30754" in number_sub:
            return p
    return None


def main():
    load_issuer_websites()
    policies = [p for p in json.loads(POLICIES.read_text(encoding="utf-8")) if p.get("country") == "Peru"]
    rels = json.loads(RELS.read_text(encoding="utf-8"))

    verified_issuers: dict[str, list[tuple[str, str]]] = defaultdict(list)
    actor_names = {a["id"]: a.get("name", a["id"]) for a in json.loads(ACTORS.read_text())}
    for r in rels:
        if r["type"] != "issues_policy" or not r.get("verified"):
            continue
        if not r["target"].startswith("policy:"):
            continue
        verified_issuers[r["target"]].append((r["source"], actor_names.get(r["source"], r["source"])))

    ch_map: dict[str, list[tuple[str, bool]]] = defaultdict(list)
    for r in rels:
        if r["type"] != "addresses_challenge":
            continue
        if not r["source"].startswith("policy:"):
            continue
        ch_map[r["source"]].append(
            (CHALLENGE_LABEL.get(r["target"], r["target"]), bool(r.get("suggested")))
        )

    policies_by_id = {p["id"]: p for p in policies}
    mapa_extras = mapa_extra_rows()
    all_catalog = policies + mapa_extras

    OUT.mkdir(parents=True, exist_ok=True)
    header = [
        "Name",
        "Number",
        "Type",
        "Status",
        "Date",
        "Issuing agency (website)",
        "Linked challenges",
        "Source URL",
        "Registry",
    ]

    csv_path = OUT / "pe-policies-catalog.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for p in sorted(all_catalog, key=lambda x: (date_label(x), x.get("name") or "")):
            w.writerow(build_row(p, verified_issuers, ch_map))

    # Markdown overview (summary + pointer to CSV; full MD table too large for BookStack)
    overview = [
        "# Peru — climate & environmental policies (catalog)",
        "",
        f"Generated {date.today().isoformat()} from Nexus `data/policies.json` (SINIA Vigente scrape) "
        f"and **Mapa de Actores** staging.",
        "",
        "## Provenance",
        "",
        f"- **SINIA (MINAM):** {sum(1 for p in policies if p.get('registry') == 'SINIA')} in-force norms (`registry: SINIA`).",
        f"- **Curated / other registries:** {sum(1 for p in policies if p.get('registry') != 'SINIA')} rows.",
        f"- **Mapa de Actores staging:** {len(mapa_extras)} reference rows (deck § marco normativo).",
        "",
        MAPA_CITE,
        "",
        "## Full catalog",
        "",
        f"The complete table ({len(all_catalog)} rows) is in [`pe-policies-catalog.csv`](pe-policies-catalog.csv) "
        "in this repository folder. Linked challenges marked *(Sugerido)* in the CSV/chapter parts are "
        "sector-inferred, not issuer-verified.",
        "",
        "## Key instruments (detailed pages)",
        "",
        "- [Ley 30754 — Ley Marco sobre Cambio Climático](ley-30754-lmcc.md)",
        "- [DS 013-2019-MINAM — Reglamento LMCC](ds-013-2019-minam-reglamento-lmcc.md)",
        "- [NDC Perú (actualización 2020)](ndc-peru-2020.md)",
        "- [Política Nacional ENCC al 2050](encc-2050-politica-nacional.md)",
        "- [StartUp Perú & incentivos climáticos](incentivos-startup-peru-clima.md)",
        "",
    ]
    (OUT / "00-overview.md").write_text("\n".join(overview), encoding="utf-8")

    # Split markdown tables for BookStack (max ~1500 rows each)
    chunk_size = 1500
    part_files = []
    sorted_pol = sorted(all_catalog, key=lambda x: (date_label(x), x.get("name") or ""))
    for i in range(0, len(sorted_pol), chunk_size):
        chunk = sorted_pol[i : i + chunk_size]
        part = i // chunk_size + 1
        fname = f"catalog-part-{part:02d}.md"
        part_files.append(fname)
        md = [
            f"# Catálogo PE — parte {part}",
            "",
            f"Rows {i + 1}–{i + len(chunk)} of {len(sorted_pol)}.",
            "",
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(["---"] * len(header)) + " |",
        ]
        for p in chunk:
            md.append("| " + " | ".join(build_row(p, verified_issuers, ch_map)) + " |")
        md.append("")
        (OUT / fname).write_text("\n".join(md), encoding="utf-8")

    # Key policy pages
    ley30754 = find_sinia_policy(policies, "30754", "Marco") or policies_by_id.get("policy:pe-ley-30754-2018")
    ds013 = find_sinia_policy(policies, "013-2019-MINAM", "Reglamento") or policies_by_id.get(
        "policy:pe-ds-013-2019-minam"
    )
    key_pages = {
        "ley-30754-lmcc.md": ley30754["id"] if ley30754 else "policy:pe-ley-30754-2018",
        "ds-013-2019-minam-reglamento-lmcc.md": ds013["id"] if ds013 else "policy:pe-ds-013-2019-minam",
        "ndc-peru-2020.md": "policy:pe-ndc-2020",
        "encc-2050-politica-nacional.md": "policy:pe-encc-2050-2024",
        "incentivos-startup-peru-clima.md": "policy:pe-startup-peru-clima",
    }
    for fname, pid in key_pages.items():
        body = key_policy_detail(pid, policies_by_id, rels, verified_issuers, actor_names)
        (OUT / fname).write_text(body, encoding="utf-8")

    manifest = {
        "book_id": 3042,
        "book_slug": "nexus-agent-review",
        "chapter_name": "Peru, climate policies",
        "generated": date.today().isoformat(),
        "pages": [
            {"file": "00-overview.md", "name": "Peru policies — overview"},
            *[{"file": f, "name": f"Catálogo PE parte {i + 1}"} for i, f in enumerate(part_files)],
            *[
                {"file": k, "name": k.replace(".md", "").replace("-", " ").title()}
                for k in key_pages
            ],
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(all_catalog), "parts": len(part_files), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
