#!/usr/bin/env python3
"""Odoo → BookStack sync for Epic Angels pipeline (Lane B).

1. Pull CLP26 founders from Odoo res.partner (x_startup_name, name).
2. Create/update BookStack idea pages (Chum Chum, Cirkula, NUX + founder tags).
3. Write audit JSON under Archive/.

Uses /opt/idea-browser/.env for BookStack write token.
Uses /opt/odoo-mcp/.env for Odoo XML-RPC read.
"""

from __future__ import annotations

import json
import os
import re
import sys
import xmlrpc.client
from datetime import date
from pathlib import Path

import requests

BOOK_ENV = Path("/opt/idea-browser/.env")
ODOO_ENV = Path("/opt/odoo-mcp/.env")
ARCHIVE = Path("/opt/nexus-idea-browser/Archive/epic-angels-20250918")
BOOK_ID = 621

COUNTRY_FLAGS = {
    "Colombia": "🇨🇴",
    "Peru": "🇵🇪",
    "México": "🇲🇽",
    "Mexico": "🇲🇽",
}


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def odoo_founders() -> dict[str, str]:
    env = load_env(ODOO_ENV)
    url = env["ODOO_URL"]
    db = env["ODOO_DB"]
    user = env["ODOO_USERNAME"]
    pwd = env["ODOO_PASSWORD"]
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(db, user, pwd, {})
    if not uid:
        raise RuntimeError("Odoo auth failed")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
    recs = models.execute_kw(
        db, uid, pwd,
        "res.partner", "search_read",
        [[("x_clp_cohort", "=", "CLP 2026"), ("x_startup_name", "!=", False)]],
        {"fields": ["name", "x_startup_name"], "limit": 500},
    )
    out: dict[str, str] = {}
    for r in recs:
        startup = (r.get("x_startup_name") or "").strip()
        name = (r.get("name") or "").strip()
        if startup and name:
            out[normalize(startup)] = name
    return out


def normalize(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class BS:
    def __init__(self) -> None:
        env = load_env(BOOK_ENV)
        self.base = env["BOOKSTACK_URL"].rstrip("/")
        self.api = f"{self.base}/api"
        self.headers = {
            "Authorization": f"Token {env['BOOKSTACK_TOKEN_ID']}:{env['BOOKSTACK_TOKEN_SECRET']}",
            "Content-Type": "application/json",
        }

    def get(self, path: str, **params):
        r = requests.get(f"{self.api}{path}", headers=self.headers, params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def post(self, path: str, payload: dict):
        r = requests.post(f"{self.api}{path}", headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def put(self, path: str, payload: dict):
        r = requests.put(f"{self.api}{path}", headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def find_chapter(self, book_id: int, name: str) -> dict | None:
        book = self.get(f"/books/{book_id}")
        for item in book.get("contents", []):
            if item.get("type") == "chapter" and item.get("name") == name:
                return item
        return None

    def ensure_chapter(self, book_id: int, name: str) -> int:
        existing = self.find_chapter(book_id, name)
        if existing:
            return existing["id"]
        ch = self.post("/chapters", {"book_id": book_id, "name": name, "tags": []})
        return ch["id"]

    def find_page_by_title(self, title: str) -> dict | None:
        data = self.get("/search", query=f'"{title}" {{type:page}}', count=5)
        for item in data.get("data", []):
            if item.get("name") == title:
                return item
        return None


def extract_founder_md(md: str) -> str:
    m = re.search(r"## Founder\n(.+?)(?:\n## |\Z)", md, re.S)
    if not m:
        return ""
    val = m.group(1).strip()
    if not val or val.startswith("[PENDIENTE]"):
        return ""
    return val


def merge_tags(tags: list[dict], updates: dict[str, str]) -> list[dict]:
    by_name = {t["name"]: t for t in tags}
    for name, value in updates.items():
        by_name[name] = {"name": name, "value": value}
    return list(by_name.values())


def render_page(idea: dict) -> str:
    flag = COUNTRY_FLAGS.get(idea["country"], "")
    city = idea.get("city", "")
    country_line = f"{flag} {idea['country']}" + (f" · {city}" if city else "")
    ct = idea.get("ct_taxonomy") or "[PENDIENTE]"
    lines = [
        f"# {idea['startup_name']}",
        "",
        f"**Country:** {country_line}",
        f"**Category:** {idea['category']}",
        f"**CT Taxonomy:** {ct}",
        f"**Impact Areas:** {idea.get('impact_areas', 'Circular Economy')}",
        f"**Stage:** {idea['stage']}",
        f"**Team Size:** —",
        f"**Website:** {idea.get('website') or '—'}",
        f"**Funded:** {idea.get('funded', '—')}",
        "",
        "---",
        "",
        "## Elevator Pitch",
        idea.get("description", "[PENDIENTE — add elevator pitch]"),
        "",
        "## Climate Problem",
        idea.get("problem", "[PENDIENTE]"),
        "",
        "## Solution",
        idea.get("solution", "[PENDIENTE]"),
        "",
        "## Source Notes",
        idea.get("source_notes", "[PENDIENTE]"),
        "",
        "## Founder",
        idea.get("founder") or "[PENDIENTE]",
        "",
    ]
    return "\n".join(lines)


def build_new_pages(odoo: dict[str, str]) -> list[dict]:
    return [
        {
            "startup_name": "Chum Chum",
            "page_title": "Chum Chum · Food & Agriculture",
            "chapter": "REIN Network — Portfolio",
            "country": "México",
            "city": "",
            "category": "Food & Agriculture",
            "stage": "Launched",
            "source": "REIN-Hub",
            "app_id": "20081",
            "ct_taxonomy": "[PENDIENTE]",
            "founder": "Verónica Macías",
            "description": (
                "Converts surplus produce and food-industry byproducts into sauces, purées, "
                "and food-service products for corporate, hospitality, and healthcare clients."
            ),
            "problem": "Food loss across the value chain in Mexico's food system.",
            "solution": "Upcycling surplus and byproducts into new food-service products.",
            "source_notes": (
                "Founder: REIN Hubs Website Handoff (CTH internal doc, 2026). "
                "Impact table: BookStack page 210 (Impacto Regional REIN 2019–2025)."
            ),
            "funded": "—",
            "aliases": ["ChumChum"],
        },
        {
            "startup_name": "Cirkula",
            "page_title": "Cirkula · Food & Agriculture",
            "chapter": "Hub Perú — Portfolio",
            "country": "Peru",
            "city": "",
            "category": "Food & Agriculture",
            "stage": "Private Beta",
            "source": "Hub-Peru",
            "app_id": "20082",
            "ct_taxonomy": "[PENDIENTE]",
            "founder": "[PENDIENTE]",
            "description": (
                "Digital platform connecting restaurants and consumers to reduce food waste "
                "(anti-desperdicio marketplace)."
            ),
            "problem": "Food waste from restaurants and food retail in Peru.",
            "solution": "Marketplace/app connecting restaurants and consumers for surplus food.",
            "source_notes": (
                "Hub Perú wiki pages 183, 206, 211; investor portal page 15 "
                "(Pre-Seed ext. ~USD 450k). No founder name in Odoo res.partner or wiki."
            ),
            "funded": "Pre-Seed ext. ~USD 450k (investor portal page 15)",
            "aliases": [],
        },
        {
            "startup_name": "NUX",
            "page_title": "NUX · Not Assigned/ Unknown",
            "chapter": "CLP26 Colombia",
            "country": "Colombia",
            "city": "",
            "category": "Not Assigned/ Unknown",
            "stage": "Unknown",
            "source": "CLP26",
            "app_id": "20083",
            "ct_taxonomy": "[PENDIENTE]",
            "founder": "[PENDIENTE]",
            "description": (
                "CLP26 Colombia cohort mention in Epic Angels curation pack; "
                "full application not found in clp26_colombia_ideas.json or Odoo res.partner."
            ),
            "problem": "[PENDIENTE]",
            "solution": "[PENDIENTE]",
            "source_notes": (
                "CLP26 Colombia end-report PDF mention (Epic Angels desk). "
                "Not in Odoo res.partner (CLP 2026). Gideon to refine mapping."
            ),
            "funded": "—",
            "aliases": [],
        },
    ]


def main() -> int:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    bs = BS()
    odoo = odoo_founders()
    audit = {
        "date": date.today().isoformat(),
        "odoo_model": "res.partner",
        "odoo_fields": ["name", "x_startup_name", "x_clp_cohort", "x_program_status", "function", "title"],
        "odoo_clp26_count": len(odoo),
        "pages_created": [],
        "pages_updated": [],
        "founder_tags_added": 0,
    }

    # ── Create missing Epic pages ──
    for idea in build_new_pages(odoo):
        existing = bs.find_page_by_title(idea["page_title"])
        chapter_id = bs.ensure_chapter(BOOK_ID, idea["chapter"])
        md = render_page(idea)
        tags = [
            {"name": "country", "value": idea["country"]},
            {"name": "category", "value": idea["category"]},
            {"name": "stage", "value": idea["stage"]},
            {"name": "source", "value": idea["source"]},
            {"name": "app_id", "value": idea["app_id"]},
        ]
        founder_val = idea.get("founder", "")
        if founder_val and not founder_val.startswith("[PENDIENTE]"):
            tags.append({"name": "founder", "value": founder_val})

        if existing:
            page = bs.get(f"/pages/{existing['id']}")
            payload = {
                "book_id": BOOK_ID,
                "chapter_id": chapter_id,
                "name": idea["page_title"],
                "markdown": md,
                "tags": merge_tags(page.get("tags", []), {t["name"]: t["value"] for t in tags}),
            }
            bs.put(f"/pages/{existing['id']}", payload)
            audit["pages_updated"].append({
                "id": existing["id"],
                "title": idea["page_title"],
                "url": f"{bs.base}/books/idea-browser/page/{existing.get('slug', '')}",
                "action": "updated",
            })
            page_id = existing["id"]
            slug = existing.get("slug", "")
        else:
            created = bs.post("/pages", {
                "book_id": BOOK_ID,
                "chapter_id": chapter_id,
                "name": idea["page_title"],
                "markdown": md,
                "tags": tags,
            })
            page_id = created["id"]
            slug = created.get("slug", "")
            audit["pages_created"].append({
                "id": page_id,
                "title": idea["page_title"],
                "url": f"{bs.base}/books/idea-browser/page/{slug}",
                "action": "created",
            })
        idea["bookstack_page_id"] = page_id
        idea["slug"] = slug

    # ── Backfill founder tags on all idea pages ──
    page_num = 1
    empty_before = 0
    filled_after = 0
    while True:
        data = bs.get("/search", query="{type:page} [app_id]", count=100, page=page_num)
        results = data.get("data", [])
        if not results:
            break
        for item in results:
            pid = item["id"]
            page = bs.get(f"/pages/{pid}")
            tags = page.get("tags", [])
            tag_map = {t["name"]: t["value"] for t in tags}
            if tag_map.get("founder"):
                continue
            empty_before += 1
            md = page.get("markdown") or ""
            startup = page["name"].split(" · ")[0].strip()
            founder = extract_founder_md(md)
            if not founder:
                odoo_name = odoo.get(normalize(startup), "")
                founder = odoo_name
            if not founder:
                continue
            new_tags = merge_tags(tags, {"founder": founder})
            bs.put(f"/pages/{pid}", {
                "book_id": page["book_id"],
                "chapter_id": page["chapter_id"],
                "name": page["name"],
                "markdown": md,
                "tags": new_tags,
            })
            filled_after += 1
            audit["founder_tags_added"] += 1
            audit["pages_updated"].append({
                "id": pid,
                "title": page["name"],
                "founder": founder,
                "action": "founder_tag",
            })
        if len(results) < 100:
            break
        page_num += 1

    audit["founder_empty_before"] = empty_before
    audit["founder_filled_this_run"] = filled_after

    out_path = ARCHIVE / "odoo-wiki-sync-audit.json"
    out_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False))
    print(json.dumps({
        "created": len(audit["pages_created"]),
        "updated": len(audit["pages_updated"]),
        "founder_tags_added": audit["founder_tags_added"],
        "audit": str(out_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
