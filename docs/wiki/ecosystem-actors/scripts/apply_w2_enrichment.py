#!/usr/bin/env python3
"""Apply batch W2 public-source enrichment to ecosystem actor wiki drafts."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
WIKI = REPO / "docs" / "wiki" / "ecosystem-actors"
MANUAL = Path(__file__).with_name("w2_enrichment_manual.json")


def batch_actor_ids() -> list[str]:
    with (WIKI / "audit.csv").open(encoding="utf-8") as f:
        missing = sorted(
            [r for r in csv.DictReader(f) if r.get("wiki_url") == "MISSING"],
            key=lambda r: r["actor_id"],
        )
    return [r["actor_id"] for r in missing[75:150]]


def actor_path(actor_id: str) -> Path:
    return WIKI / "peru" / f"{actor_id}.md"


def nexus_line(slug: str | None) -> str:
    if not slug or slug == "PENDIENTE":
        return "PENDIENTE"
    url = f"https://nexus.cleantechhub.net/s/{slug}"
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status == 200:
                return f"[nexus.cleantechhub.net/s/{slug}]({url})"
    except Exception:
        pass
    return "PENDIENTE"


def set_table_field(text: str, field: str, value: str) -> str:
    pat = rf"(\| {re.escape(field)} \| )([^|]+)( \|)"
    if re.search(pat, text):
        return re.sub(pat, lambda m: f"{m.group(1)}{value}{m.group(3)}", text, count=1)
    # insert after Ciudad for Dirección; after Rol for Año
    if field == "Dirección":
        return re.sub(
            r"(\| Ciudad \| [^\n]+\n)",
            rf"\1| Dirección | {value} |\n",
            text,
            count=1,
        )
    if field == "Año de fundación":
        return re.sub(
            r"(\| Rol en el ecosistema \| [^\n]+\n)",
            rf"\1| Año de fundación | {value} |\n",
            text,
            count=1,
        )
    return text


def apply_one(path: Path, data: dict) -> None:
    text = path.read_text(encoding="utf-8")
    if data.get("display_name"):
        text = re.sub(r"^# .+$", f"# {data['display_name']}", text, count=1, flags=re.MULTILINE)

    text = set_table_field(text, "Ciudad", data["city"])
    text = set_table_field(text, "Dirección", data["address"])
    text = set_table_field(text, "Sitio web", data["website"])
    text = set_table_field(text, "LinkedIn", data["linkedin"])
    text = set_table_field(text, "Rol en el ecosistema", data["rol_ecosistema"])
    text = set_table_field(text, "Año de fundación", data["founded"])
    text = set_table_field(text, "Tarjeta Nexus", data["nexus_display"])

    text = re.sub(
        r"(## Rol y alcance\n\n)(PENDIENTE|[^\n#]+(?:\n[^\n#]+)*)",
        rf"\1{data['descripcion']}\n",
        text,
        count=1,
    )

    fuentes_block = "\n".join(f"- {line}" for line in data["fuentes"])
    text = re.sub(
        r"## Fuentes\n\n(?:- .+\n)+",
        f"## Fuentes\n\n{fuentes_block}\n",
        text,
        count=1,
    )
    path.write_text(text, encoding="utf-8")


def is_filled(val: str) -> bool:
    return bool(val) and val.strip() != "PENDIENTE"


def main() -> int:
    manual: dict = json.loads(MANUAL.read_text(encoding="utf-8"))
    ids = batch_actor_ids()
    missing_manual = [i for i in ids if i not in manual]
    if missing_manual:
        raise SystemExit(f"Missing manual entries: {missing_manual}")

    stats = {
        "website": 0,
        "city": 0,
        "address": 0,
        "description": 0,
        "rol_ecosistema": 0,
        "founded": 0,
        "linkedin": 0,
        "nexus": 0,
    }
    total = len(ids)

    for aid in ids:
        d = manual[aid]
        nexus_disp = nexus_line(d.get("nexus_slug"))
        if d.get("nexus") == "PENDIENTE" and not d.get("nexus_slug"):
            nexus_disp = "PENDIENTE"
        row = {
            "city": d["city"],
            "address": d["address"],
            "website": d["website"],
            "linkedin": d["linkedin"],
            "rol_ecosistema": d["rol_ecosistema"],
            "founded": d["founded"],
            "nexus_display": nexus_disp,
            "descripcion": d["descripcion"],
            "fuentes": [f for f in d["fuentes"] if not f.startswith("PENDIENTE")],
        }
        if not row["fuentes"]:
            row["fuentes"] = [
                "Mapa de actores CTH — `static/ecosystem/data/actors.json`"
            ]
        apply_one(actor_path(aid), {**d, **row, "nexus_display": nexus_disp})

        if is_filled(row["website"]):
            stats["website"] += 1
        if is_filled(row["city"]):
            stats["city"] += 1
        if is_filled(row["address"]):
            stats["address"] += 1
        if is_filled(row["descripcion"]):
            stats["description"] += 1
        if is_filled(row["rol_ecosistema"]):
            stats["rol_ecosistema"] += 1
        if is_filled(row["founded"]):
            stats["founded"] += 1
        if is_filled(row["linkedin"]):
            stats["linkedin"] += 1
        if is_filled(nexus_disp):
            stats["nexus"] += 1

    report = {
        "batch": "W2",
        "actors": total,
        "filled": stats,
        "pendiente": {k: total - v for k, v in stats.items()},
    }
    out = WIKI / "w2-enrichment-summary.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
