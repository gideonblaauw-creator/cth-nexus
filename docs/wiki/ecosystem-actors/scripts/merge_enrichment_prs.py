#!/usr/bin/env python3
"""Merge actor wiki enrichment from micro-batch PR branches into consolidated drafts."""
from __future__ import annotations

import csv
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
WIKI = REPO / "docs" / "wiki" / "ecosystem-actors"
BASE_REF = "cursor/ecosystem-actor-wiki-1020"

BRANCHES = [
    ("W1", "origin/cursor/actor-wiki-w1"),
    ("W2", "origin/cursor/actor-wiki-w2-db83"),
    ("W3", "origin/cursor/actor-wiki-w3"),
    ("W4", "origin/cursor/actor-wiki-w4-af9f"),
    ("W5", "origin/cursor/actor-wiki-w5"),
    ("b1", "origin/cursor/actor-wiki-enrich-b1-f63c"),
    ("b2", "origin/cursor/actor-wiki-enrich-b2"),
    ("b3", "origin/cursor/actor-wiki-enrich-b3-b0d0"),
    ("b4", "origin/cursor/actor-wiki-enrich-b4"),
]

FORBIDDEN_PATTERNS = [
    re.compile(r"https?://(?:drive|docs)\.google\.com[^\s\)]*", re.I),
    re.compile(r"https?://[^\s\)]*canva\.com[^\s\)]*", re.I),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
]

TABLE_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$")


@dataclass
class ParsedDoc:
    branch: str
    raw: str
    frontmatter: str = ""
    body: str = ""
    is_startup: bool = False
    desc_heading: str = ""
    table: dict[str, str] = field(default_factory=dict)
    description: str = ""
    relations: str = ""
    policies: str = ""
    sources: list[str] = field(default_factory=list)


def git_show(ref: str, path: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "show", f"{ref}:{path}"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None


def is_pendiente(val: str | None) -> bool:
    if not val or not str(val).strip():
        return True
    v = str(val).strip()
    return v == "PENDIENTE" or v.startswith("PENDIENTE ")


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s\)\]|]+", text or "")


def sanitize_text(text: str) -> str:
    out = text
    for pat in FORBIDDEN_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    if "internal" in out.lower() and "note" in out.lower():
        lines = [ln for ln in out.splitlines() if "internal" not in ln.lower()]
        out = "\n".join(lines)
    return out


def parse_doc(content: str, branch: str) -> ParsedDoc:
    doc = ParsedDoc(branch=branch, raw=content)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            doc.frontmatter = f"---{parts[1]}---"
            rest = parts[2]
        else:
            rest = content
    else:
        rest = content

    doc.is_startup = "## Snapshot" in rest
    doc.desc_heading = "## Descripción" if doc.is_startup else "## Rol y alcance"

    sections = re.split(r"\n(?=## )", rest, maxsplit=0)

    def table_from_section(sec: str) -> None:
        for row in sec.splitlines():
            m = TABLE_ROW.match(row.strip())
            if m and m.group(1).strip() not in ("Field", "---"):
                doc.table[m.group(1).strip()] = m.group(2).strip()

    for sec in sections:
        if sec.startswith("## Overview") or sec.startswith("## Snapshot"):
            table_from_section(sec)
        elif sec.startswith(doc.desc_heading):
            doc.description = sec.split("\n", 1)[1].strip() if "\n" in sec else ""
        elif sec.startswith("## Relaciones"):
            doc.relations = sec.split("\n", 1)[1].strip() if "\n" in sec else "PENDIENTE"
        elif sec.startswith("## Políticas"):
            doc.policies = sec.split("\n", 1)[1].strip() if "\n" in sec else "PENDIENTE"
        elif sec.startswith("## Fuentes"):
            body = sec.split("\n", 1)[1] if "\n" in sec else ""
            for ln in body.splitlines():
                ln = ln.strip()
                if ln.startswith("- "):
                    doc.sources.append(ln[2:].strip())

    doc.body = rest
    return doc


def field_score(name: str, value: str, sources: list[str], desc: str) -> int:
    if is_pendiente(value):
        return 0
    score = 10
    if "http" in value or "nexus.cleantechhub.net" in value:
        score += 25
    if name == "LinkedIn" and "linkedin.com" in value.lower():
        score += 10
    if name == "Sitio web" and value.startswith("http"):
        score += 10
    ctx = "\n".join(sources) + "\n" + desc
    for u in extract_urls(value):
        if any(u.split("/")[2] in s for s in sources if "http" in s):
            score += 15
    if name == "Año de fundación" and re.search(r"\d{4}", value):
        score += 5
    if len(value) > 40 and name == "Rol en el ecosistema":
        score += 8
    if extract_urls(ctx):
        score += min(10, len(extract_urls(ctx)))
    return score


def desc_score(text: str, sources: list[str]) -> int:
    if is_pendiente(text):
        return 0
    score = 15 + min(200, len(text) // 4)
    score += 10 * len(extract_urls(text))
    score += min(15, len([s for s in sources if "http" in s]))
    return score


def pick_best(
    field: str,
    candidates: list[tuple[str, str, ParsedDoc]],
) -> tuple[str, list[tuple[str, str]]]:
    """Return (value, conflicts)."""
    scored: list[tuple[int, str, str, ParsedDoc]] = []
    for branch, val, doc in candidates:
        sc = field_score(field, val, doc.sources, doc.description)
        if field in ("Rol y alcance", "Descripción"):
            sc = desc_score(val, doc.sources)
        if sc > 0:
            scored.append((sc, branch, val, doc))
    if not scored:
        return "PENDIENTE", []
    scored.sort(key=lambda x: (-x[0], x[1]))
    best_val = scored[0][2]
    conflicts = []
    for sc, branch, val, _ in scored[1:]:
        if val.strip() != best_val.strip() and not is_pendiente(val):
            conflicts.append((branch, val))
    return best_val, conflicts


def merge_docs(docs: list[ParsedDoc]) -> tuple[ParsedDoc, list[dict]]:
    base = docs[0]
    merged = ParsedDoc(branch="merged", raw="", frontmatter=base.frontmatter)
    merged.is_startup = base.is_startup
    merged.desc_heading = base.desc_heading
    merged.relations = base.relations
    merged.policies = base.policies

    all_fields = set()
    for d in docs:
        all_fields.update(d.table.keys())

    conflict_log: list[dict] = []
    for fname in sorted(all_fields):
        cands = [(d.branch, d.table.get(fname, "PENDIENTE"), d) for d in docs]
        val, conflicts = pick_best(fname, cands)
        merged.table[fname] = val
        if conflicts:
            conflict_log.append(
                {
                    "field": fname,
                    "kept": val,
                    "kept_from": cands[0][0] if cands else "",
                    "alternates": [{"branch": b, "value": v} for b, v in conflicts[:3]],
                }
            )

    desc_cands = [(d.branch, d.description, d) for d in docs]
    merged.description, dc = pick_best(merged.desc_heading, desc_cands)
    if dc:
        conflict_log.append({"section": merged.desc_heading, "alternates": dc})

    source_seen: set[str] = set()
    merged.sources = []
    for d in docs:
        for s in d.sources:
            s_clean = sanitize_text(s.strip())
            if not s_clean or s_clean in source_seen:
                continue
            if is_pendiente(s_clean):
                continue
            if "verificación" in s_clean.lower() or "http 200" in s_clean.lower():
                continue
            source_seen.add(s_clean)
            merged.sources.append(s_clean)

    site = merged.table.get("Sitio web", "")
    if "revistaganamas.com.pe" in site:
        merged.sources = [
            s
            for s in merged.sources
            if "ganamas.com.pe" not in s.lower() or "revistaganamas" in s.lower()
        ]

    for d in docs:
        if not is_pendiente(d.relations) and is_pendiente(merged.relations):
            merged.relations = d.relations
        if not is_pendiente(d.policies) and is_pendiente(merged.policies):
            merged.policies = d.policies

    return merged, conflict_log


def render_doc(p: ParsedDoc) -> str:
    lines = [p.frontmatter, ""]

    body_src = p.raw.split("---", 2)[-1] if p.raw.startswith("---") else p.raw
    header = ""
    m = re.match(
        r"(?s)(^\s*#\s+.+?\n\n> Borrador para revisión[^\n]+\n)",
        body_src,
    )
    if m:
        header = m.group(1)
    if not header:
        aid = re.search(r"actor_id:\s*(\S+)", p.frontmatter)
        header = f"# {aid.group(1) if aid else 'Actor'}\n\n> Borrador para revisión (libro 3042 `nexus-agent-review`). No publicar sin aprobación.\n"

    lines.append(header.rstrip())
    lines.append("")
    section = "## Snapshot" if p.is_startup else "## Overview"
    lines.append(section)
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")

    if p.is_startup:
        order = [
            "Categoría",
            "País",
            "Ciudad",
            "Sitio web",
            "LinkedIn",
            "Rol en el ecosistema",
            "Año de fundación",
            "Tarjeta Nexus",
        ]
    else:
        order = [
            "Categoría",
            "Tipo",
            "País",
            "Ciudad",
            "Sitio web",
            "LinkedIn",
            "Rol en el ecosistema",
            "Dirección",
            "Año de fundación",
            "Desafíos (códigos)",
            "Tarjeta Nexus",
        ]

    written = set()
    for key in order:
        if key in p.table:
            lines.append(f"| {key} | {p.table[key]} |")
            written.add(key)
    for key, val in p.table.items():
        if key not in written:
            lines.append(f"| {key} | {val} |")

    lines.append("")
    lines.append(p.desc_heading)
    lines.append("")
    lines.append(p.description if not is_pendiente(p.description) else "PENDIENTE")
    lines.append("")
    lines.append("## Relaciones (ecosistema)")
    lines.append("")
    lines.append(p.relations if p.relations else "PENDIENTE")
    lines.append("")
    lines.append("## Políticas vinculadas")
    # country from frontmatter
    country = "Peru"
    cm = re.search(r"tag_country:\s*(.+)", p.frontmatter)
    if cm:
        country = cm.group(1).strip()
    lines[-1] = f"## Políticas vinculadas ({country})"
    lines.append("")
    lines.append(p.policies if p.policies else "PENDIENTE (sin vínculos en policy_relations.json para este actor)")
    lines.append("")
    lines.append("## Fuentes")
    lines.append("")
    if p.sources:
        for s in p.sources:
            lines.append(f"- {s}")
    else:
        lines.append("- Mapa de actores CTH — `static/ecosystem/data/actors.json`")
    lines.append("")
    return sanitize_text("\n".join(lines))


def audit_field_status(table: dict[str, str], description: str) -> dict[str, str]:
    def st(key: str | None, desc: bool = False) -> str:
        if desc:
            return "FILLED" if not is_pendiente(description) else "PENDIENTE"
        val = table.get(key or "", "PENDIENTE")
        return "FILLED" if not is_pendiente(val) else "PENDIENTE"

    founded = st("Año de fundación")
    if founded == "PENDIENTE" and re.search(r"\*\*Año de fundación:\*\*", description):
        founded = "FILLED"
    return {
        "website": st("Sitio web"),
        "city": st("Ciudad"),
        "description": st(None, desc=True),
        "founding_year": founded,
        "linkedin": st("LinkedIn"),
        "nexus": st("Tarjeta Nexus"),
    }


def main() -> int:
    md_files = sorted(WIKI.glob("*/*.md"))
    all_conflicts: list[dict] = []
    stats = {k: {"FILLED": 0, "PENDIENTE": 0} for k in ("website", "city", "description", "founding_year", "linkedin", "nexus")}
    merged_count = 0

    for path in md_files:
        rel = str(path.relative_to(REPO))
        versions: list[ParsedDoc] = []
        base_raw = git_show("HEAD", rel) or path.read_text(encoding="utf-8")
        versions.append(parse_doc(base_raw, "base"))

        for label, ref in BRANCHES:
            remote = git_show(ref, rel)
            if remote and remote.strip() != base_raw.strip():
                versions.append(parse_doc(remote, label))

        if len(versions) == 1:
            merged_doc = versions[0]
            cl = []
        else:
            merged_doc, cl = merge_docs(versions)
            if cl:
                all_conflicts.append({"path": rel, "conflicts": cl})
            merged_count += 1
        merged_doc.raw = base_raw

        out = render_doc(merged_doc)
        path.write_text(out, encoding="utf-8")

        fs = audit_field_status(merged_doc.table, merged_doc.description)
        for k, v in fs.items():
            stats[k][v] += 1

    # audit.csv
    base_audit_fields = [
        "actor_id",
        "name",
        "country",
        "category",
        "website",
        "wiki_url",
        "match_confidence",
        "match_method",
    ]
    audit_rows: list[dict] = []
    with (WIKI / "audit.csv").open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k: row.get(k, "") for k in base_audit_fields}
            aid = row["actor_id"]
            draft = WIKI / row["country"].lower().replace(" ", "-") / f"{aid}.md"
            if row["country"] == "El Salvador":
                draft = WIKI / "el-salvador" / f"{aid}.md"
            elif row["country"] == "Colombia":
                draft = WIKI / "colombia" / f"{aid}.md"
            elif row["country"] == "Peru":
                draft = WIKI / "peru" / f"{aid}.md"

            enrich = {
                "draft_path": "",
                "enrich_website": "N/A",
                "enrich_city": "N/A",
                "enrich_description": "N/A",
                "enrich_founding_year": "N/A",
                "enrich_linkedin": "N/A",
                "enrich_nexus": "N/A",
            }
            if row.get("wiki_url") != "MISSING":
                pass
            elif draft.is_file():
                doc = parse_doc(draft.read_text(encoding="utf-8"), "final")
                fs = audit_field_status(doc.table, doc.description)
                enrich["draft_path"] = str(draft.relative_to(REPO))
                for k, col in [
                    ("website", "enrich_website"),
                    ("city", "enrich_city"),
                    ("description", "enrich_description"),
                    ("founding_year", "enrich_founding_year"),
                    ("linkedin", "enrich_linkedin"),
                    ("nexus", "enrich_nexus"),
                ]:
                    enrich[col] = fs[k]
            else:
                enrich["draft_path"] = "MISSING"

            audit_rows.append({**row, **enrich})

    fieldnames = base_audit_fields + [
        "draft_path",
        "enrich_website",
        "enrich_city",
        "enrich_description",
        "enrich_founding_year",
        "enrich_linkedin",
        "enrich_nexus",
    ]
    with (WIKI / "audit.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(audit_rows)

    manifest_path = WIKI / "bookstack-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["enrichment"] = {
        "merged_batches": [b[0] for b in BRANCHES],
        "draft_files_merged": merged_count,
        "field_totals_drafted": stats,
        "conflicts_resolved": len(all_conflicts),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = {
        "merged_files": merged_count,
        "total_draft_md": len(md_files),
        "field_stats": stats,
        "conflicts_resolved": len(all_conflicts),
        "sample_conflicts": all_conflicts[:15],
    }
    (WIKI / "enrichment-merge-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
