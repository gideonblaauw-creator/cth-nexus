#!/usr/bin/env python3
"""Audit ecosystem actors vs public BookStack pages; draft missing wiki pages (file-only)."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import unicodedata
import urllib.parse
from difflib import SequenceMatcher
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "docs" / "wiki" / "ecosystem-actors"
DATA = REPO / "static" / "ecosystem" / "data"
ONEPAGERS = REPO / "onepagers" / "data"
WIKI_BASE = "https://wiki.cleantechhub.net"
PERU_BRANCH = "origin/cursor/eco-peru-update-60de"

DROP_ACTOR_KEYS = frozenset(
    {"notes", "email", "phone", "internal_notes", "drive_url", "website_check", "website_ok"}
)

CATEGORY_ROLE = {
    "funder": "Financiador e inversionista",
    "accelerator": "Aceleradora, incubadora o programa de apoyo",
    "government": "Actor público / regulador",
    "international": "Organización internacional o cooperación",
    "finance": "Institución financiera",
    "ngo_foundation": "ONG o fundación",
    "corporate": "Empresa / sector privado",
    "academia": "Universidad o centro de investigación",
    "chamber": "Cámara o gremio",
    "media": "Medios y difusión",
    "startup": "Startup del ecosistema",
    "policy": "Instrumento de política pública",
}

REL_TYPE_LABEL = {
    "hosts": "Aloja / opera",
    "partner": "Aliado de",
    "funds": "Financia",
    "member": "Miembro de",
    "program": "Programa de",
    "works_on_challenge": "Enfocado en desafío",
}


def norm_name(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def norm_domain(url: str | None) -> str:
    if not url:
        return ""
    u = url.lower().strip()
    if not u.startswith("http"):
        u = "https://" + u
    try:
        return urllib.parse.urlparse(u).netloc.replace("www.", "")
    except Exception:
        return ""


def country_dir(country: str) -> str:
    return norm_name(country).replace(" ", "-")


def curl_get(url: str) -> str:
    return subprocess.check_output(
        ["curl", "-sL", "--max-time", "45", url],
        text=True,
    )


def crawl_book(book_slug: str) -> list[dict]:
    html = curl_get(f"{WIKI_BASE}/books/{book_slug}")
    items: list[dict] = []
    pat = (
        r'href="(https://wiki\.cleantechhub\.net/books/'
        + book_slug
        + r'/page/[^"]+)"\s*\n\s*class="page\s+entity-list-item"'
    )
    for m in re.finditer(pat, html):
        url = m.group(1)
        chunk = html[m.end() : m.end() + 900]
        t = re.search(r'<h4 class="entity-list-item-name break-text">([^<]+)</h4>', chunk)
        title = t.group(1).strip() if t else url.rsplit("/", 1)[-1]
        items.append({"url": url, "title": title, "book": book_slug})
    seen: set[str] = set()
    out: list[dict] = []
    for it in items:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        out.append(it)
    return out


def load_peru_actors() -> list[dict]:
    raw = subprocess.check_output(
        ["git", "show", f"{PERU_BRANCH}:static/ecosystem/data/actors.json"],
        text=True,
        cwd=REPO,
    )
    return json.loads(raw)


def merge_actors(main: list[dict], peru: list[dict]) -> list[dict]:
    by_id: dict[str, dict] = {a["id"]: dict(a) for a in main}
    for a in peru:
        aid = a["id"]
        if aid in by_id:
            for k, v in a.items():
                if k in DROP_ACTOR_KEYS:
                    continue
                if by_id[aid].get(k) in (None, "", []) and v not in (None, "", []):
                    by_id[aid][k] = v
            continue
        name_l = (a.get("name") or "").strip().lower()
        dom = norm_domain(a.get("website"))
        dup = False
        for ex in by_id.values():
            if (ex.get("name") or "").strip().lower() == name_l:
                dup = True
                break
            if dom and dom == norm_domain(ex.get("website")):
                dup = True
                break
        if not dup:
            clean = {k: v for k, v in a.items() if k not in DROP_ACTOR_KEYS}
            by_id[aid] = clean
    return sorted(by_id.values(), key=lambda x: (x.get("country", ""), x.get("name", "")))


def load_nexus_index() -> tuple[dict[str, str], dict[str, str]]:
    by_host: dict[str, str] = {}
    by_name: dict[str, str] = {}
    if not ONEPAGERS.is_dir():
        return by_host, by_name
    for path in ONEPAGERS.glob("*.json"):
        if path.name.startswith("s-pages-"):
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        slug = doc.get("slug") or path.stem
        hk = norm_domain(doc.get("website"))
        if hk:
            by_host[hk] = slug
        nm = re.sub(r"[^a-z0-9]+", "", (doc.get("name") or "").lower())
        if nm:
            by_name[nm] = slug
    return by_host, by_name


def nexus_slug(actor: dict, by_host: dict[str, str], by_name: dict[str, str]) -> str | None:
    hk = norm_domain(actor.get("website"))
    if hk and hk in by_host:
        return by_host[hk]
    nm = re.sub(r"[^a-z0-9]+", "", (actor.get("name") or "").lower())
    return by_name.get(nm)


def wiki_match(
    actor: dict,
    wiki_pages: list[dict],
    wiki_by_norm: dict[str, list[dict]],
) -> tuple[str, str, str]:
    name = actor.get("name") or ""
    exact = wiki_by_norm.get(norm_name(name), [])
    if len(exact) == 1:
        return exact[0]["url"], "high", "catalog-exact-title"
    if len(exact) > 1:
        return exact[0]["url"], "medium", "catalog-ambiguous-title"

    preferred_books = (
        ["startup-portfolio"]
        if actor.get("category") == "startup"
        else ["investor-profiles", "startup-portfolio"]
        if actor.get("category") == "funder"
        else ["investor-profiles", "startup-portfolio"]
    )
    pool = [p for p in wiki_pages if p["book"] in preferred_books] or wiki_pages
    best_sc = 0.0
    best: dict | None = None
    for wp in pool:
        sc = SequenceMatcher(None, norm_name(name), norm_name(wp["title"])).ratio()
        if sc > best_sc:
            best_sc = sc
            best = wp
    if best and best_sc >= 0.96:
        return best["url"], "high", f"fuzzy:{best_sc:.2f}"
    if best and best_sc >= 0.92:
        return best["url"], "medium", f"fuzzy:{best_sc:.2f}"
    return "MISSING", "", ""


def format_relations(actor_id: str, by_id: dict[str, dict], rel_out: dict, rel_in: dict) -> str:
    lines: list[str] = []
    for r in rel_out.get(actor_id, []):
        tgt = by_id.get(r["target"], {})
        label = REL_TYPE_LABEL.get(r["type"], r["type"])
        lines.append(f"- **{label}** → {tgt.get('name', r['target'])} (`{r['target']}`)")
    for r in rel_in.get(actor_id, []):
        src = by_id.get(r["source"], {})
        label = REL_TYPE_LABEL.get(r["type"], r["type"])
        lines.append(f"- **{src.get('name', r['source'])}** — {label} (`{r['source']}`)")
    return "\n".join(lines) if lines else "PENDIENTE"


def format_policies(
    actor_id: str,
    country: str,
    policy_by_id: dict[str, dict],
    pol_rel_by_actor: dict[str, list],
) -> str:
    links = pol_rel_by_actor.get(actor_id, [])
    lines: list[str] = []
    for pr in links:
        pid = pr.get("target", "")
        pol = policy_by_id.get(pid)
        if not pol:
            lines.append(f"- {pid} (PENDIENTE — no encontrado en policies.json)")
            continue
        if pol.get("country") != country:
            continue
        url = pol.get("source_url") or "PENDIENTE"
        lines.append(f"- **{pol.get('name', pid)}** — {url}")
    if lines:
        return "\n".join(lines)
    return "PENDIENTE (sin vínculos en policy_relations.json para este actor)"


def render_startup_draft(actor: dict, ctx: dict) -> str:
    city = actor.get("city") or "PENDIENTE"
    ns = ctx.get("nexus_slug")
    nexus_line = (
        f"[nexus.cleantechhub.net/s/{ns}](https://nexus.cleantechhub.net/s/{ns})"
        if ns
        else "PENDIENTE"
    )
    linkedin = actor.get("linkedin") or "PENDIENTE"
    website = actor.get("website") or "PENDIENTE"
    source = actor.get("source") or "static/ecosystem/data/actors.json (+ Peru PR #58 enrichment)"
    return f"""---
status: draft-file-only
bookstack_publish: false
target_book_id: 3042
target_book: nexus-agent-review
actor_id: {actor['id']}
tag_type: ecosystem-startup
tag_country: {actor.get('country', 'PENDIENTE')}
---

# {actor.get('name', 'PENDIENTE')}

> Borrador para revisión (libro 3042 `nexus-agent-review`). No publicar sin aprobación.

## Snapshot

| Field | Value |
| --- | --- |
| Categoría | {actor.get('category', 'PENDIENTE')} |
| País | {actor.get('country', 'PENDIENTE')} |
| Ciudad | {city} |
| Sitio web | {website} |
| LinkedIn | {linkedin} |
| Rol en el ecosistema | {CATEGORY_ROLE.get(actor.get('category', ''), 'PENDIENTE')} |
| Tarjeta Nexus | {nexus_line} |

## Descripción

PENDIENTE

## Relaciones (ecosistema)

{ctx['relations']}

## Políticas vinculadas ({actor.get('country', '')})

{ctx['policies']}

## Fuentes

- {source}
- Mapa de actores CTH — `static/ecosystem/data/actors.json`
"""


def render_org_draft(actor: dict, ctx: dict) -> str:
    city = actor.get("city") or "PENDIENTE"
    ns = ctx.get("nexus_slug")
    nexus_line = (
        f"[nexus.cleantechhub.net/s/{ns}](https://nexus.cleantechhub.net/s/{ns})"
        if ns
        else "PENDIENTE"
    )
    linkedin = actor.get("linkedin") or "PENDIENTE"
    website = actor.get("website") or "PENDIENTE"
    source = actor.get("source") or "static/ecosystem/data/actors.json (+ Peru PR #58 enrichment)"
    challenges = actor.get("challenges")
    ch_line = ", ".join(challenges) if challenges else "PENDIENTE"
    return f"""---
status: draft-file-only
bookstack_publish: false
target_book_id: 3042
target_book: nexus-agent-review
actor_id: {actor['id']}
tag_type: ecosystem-org
tag_country: {actor.get('country', 'PENDIENTE')}
---

# {actor.get('name', 'PENDIENTE')}

> Borrador para revisión (libro 3042 `nexus-agent-review`). No publicar sin aprobación.

## Overview

| Field | Value |
| --- | --- |
| Categoría | {actor.get('category', 'PENDIENTE')} |
| Tipo | {actor.get('type', 'org')} |
| País | {actor.get('country', 'PENDIENTE')} |
| Ciudad | {city} |
| Sitio web | {website} |
| LinkedIn | {linkedin} |
| Rol en el ecosistema | {CATEGORY_ROLE.get(actor.get('category', ''), 'PENDIENTE')} |
| Desafíos (códigos) | {ch_line} |
| Tarjeta Nexus | {nexus_line} |

## Rol y alcance

PENDIENTE

## Relaciones (ecosistema)

{ctx['relations']}

## Políticas vinculadas ({actor.get('country', '')})

{ctx['policies']}

## Fuentes

- {source}
- Mapa de actores CTH — `static/ecosystem/data/actors.json`
"""


def main() -> int:
    print("Crawling public BookStack books…")
    wiki_pages = crawl_book("startup-portfolio") + crawl_book("investor-profiles")
    wiki_by_norm: dict[str, list[dict]] = {}
    for wp in wiki_pages:
        wiki_by_norm.setdefault(norm_name(wp["title"]), []).append(wp)
        wiki_by_norm.setdefault(norm_name(wp["url"].rsplit("/", 1)[-1]), []).append(wp)

    main_actors = json.loads((DATA / "actors.json").read_text(encoding="utf-8"))
    peru_actors = load_peru_actors()
    actors = merge_actors(main_actors, peru_actors)
    by_id = {a["id"]: a for a in actors}

    relations = json.loads((DATA / "relations.json").read_text(encoding="utf-8"))
    rel_out: dict[str, list] = {}
    rel_in: dict[str, list] = {}
    for r in relations:
        rel_out.setdefault(r["source"], []).append(r)
        rel_in.setdefault(r["target"], []).append(r)

    policies = json.loads((DATA / "policies.json").read_text(encoding="utf-8"))
    policy_by_id: dict[str, dict] = {}
    for p in policies:
        if p.get("id"):
            policy_by_id[p["id"]] = p

    policy_rel = json.loads((DATA / "policy_relations.json").read_text(encoding="utf-8"))
    pol_rel_by_actor: dict[str, list] = {}
    for pr in policy_rel:
        pol_rel_by_actor.setdefault(pr["source"], []).append(pr)

    nexus_host, nexus_name = load_nexus_index()

    OUT.mkdir(parents=True, exist_ok=True)
    audit_path = OUT / "audit.csv"
    manifest_pages: list[dict] = []

    existing = 0
    drafted = 0
    audit_rows: list[dict] = []

    for actor in actors:
        wiki_url, conf, method = wiki_match(actor, wiki_pages, wiki_by_norm)
        if wiki_url != "MISSING":
            existing += 1
        audit_rows.append(
            {
                "actor_id": actor["id"],
                "name": actor.get("name", ""),
                "country": actor.get("country", ""),
                "category": actor.get("category", ""),
                "website": actor.get("website", ""),
                "wiki_url": wiki_url,
                "match_confidence": conf,
                "match_method": method,
            }
        )

        if wiki_url == "MISSING":
            cdir = country_dir(actor.get("country", "unknown"))
            slug = actor["id"]
            rel_md = format_relations(actor["id"], by_id, rel_out, rel_in)
            pol_md = format_policies(
                actor["id"],
                actor.get("country", ""),
                policy_by_id,
                pol_rel_by_actor,
            )
            ns = nexus_slug(actor, nexus_host, nexus_name)
            ctx = {"relations": rel_md, "policies": pol_md, "nexus_slug": ns}
            if actor.get("category") == "startup":
                body = render_startup_draft(actor, ctx)
            else:
                body = render_org_draft(actor, ctx)
            out_file = OUT / cdir / f"{slug}.md"
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(body, encoding="utf-8")
            drafted += 1
            manifest_pages.append(
                {
                    "actor_id": actor["id"],
                    "title": actor.get("name", ""),
                    "chapter": cdir,
                    "markdown_path": str(out_file.relative_to(REPO)),
                    "tags": [
                        {"name": "tag_type", "value": "ecosystem-actor"},
                        {"name": "actor_id", "value": actor["id"]},
                        {"name": "country", "value": actor.get("country", "")},
                        {"name": "category", "value": actor.get("category", "")},
                    ],
                }
            )

    with audit_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "actor_id",
                "name",
                "country",
                "category",
                "website",
                "wiki_url",
                "match_confidence",
                "match_method",
            ],
        )
        w.writeheader()
        w.writerows(audit_rows)

    manifest = {
        "book_id": 3042,
        "book_slug": "nexus-agent-review",
        "book_name": "nexus-agent-review",
        "note": "Agent drafts only — private review book until Gideon approves.",
        "chapters": {
            "colombia": "Colombia",
            "el-salvador": "El Salvador",
            "peru": "Peru",
        },
        "pages": manifest_pages,
    }
    (OUT / "bookstack-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    summary = {
        "total_actors": len(actors),
        "with_existing_wiki": existing,
        "missing": len(actors) - existing,
        "drafted": drafted,
        "wiki_catalog_pages": len(wiki_pages),
    }
    (OUT / "build-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
