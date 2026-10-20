#!/usr/bin/env python3
"""Odoo → Wiki **Founder:** meta + founder tag → Nexus list API."""

from __future__ import annotations

import json
import re
import sys
import xmlrpc.client
from datetime import date
from pathlib import Path

import requests

BOOK_ENV = Path("/opt/idea-browser/.env")
ODOO_ENV = Path("/opt/odoo-mcp/.env")
ARCHIVE = Path("/opt/nexus-idea-browser/Archive/epic-angels-20250918")

# Per REIN Hubs Website Handoff — not in Odoo
MANUAL_FOUNDERS = {
    "chum chum": "Verónica Macías",
    "chumchum": "Verónica Macías",
}


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def odoo_founders() -> dict[str, str]:
    env = load_env(ODOO_ENV)
    url, db = env["ODOO_URL"], env["ODOO_DB"]
    user, pwd = env["ODOO_USERNAME"], env["ODOO_PASSWORD"]
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(db, user, pwd, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
    recs = models.execute_kw(
        db, uid, pwd, "res.partner", "search_read",
        [[("x_startup_name", "!=", False)]],
        {"fields": ["name", "x_startup_name"], "limit": 500},
    )
    out: dict[str, str] = {}
    for r in recs:
        startup = (r.get("x_startup_name") or "").strip()
        name = (r.get("name") or "").strip()
        if startup and name:
            out[norm(startup)] = name
    out.update(MANUAL_FOUNDERS)
    return out


def extract_section_founder(md: str) -> str:
    m = re.search(r"## Founder\n(.+?)(?:\n## |\Z)", md, re.S)
    if not m:
        return ""
    val = m.group(1).strip()
    return "" if not val or val.startswith("[PENDIENTE]") else val


def extract_meta_founder(md: str) -> str:
    m = re.search(r"\*\*Founder:\*\*\s*(.+)", md)
    if not m:
        return ""
    val = m.group(1).strip()
    return "" if val.startswith("[PENDIENTE]") else val


def inject_founder_meta(md: str, founder: str) -> str:
    line = f"**Founder:** {founder}"
    if re.search(r"\*\*Founder:\*\*", md):
        return re.sub(r"\*\*Founder:\*\*\s*.+", line, md, count=1)
    if "\n---\n" in md:
        head, rest = md.split("\n---\n", 1)
        return f"{head.rstrip()}\n{line}\n\n---\n{rest}"
    return f"{md.rstrip()}\n{line}\n"


def sync_founder_section(md: str, founder: str) -> str:
    block = f"## Founder\n{founder}\n"
    if "## Founder\n" in md:
        return re.sub(r"## Founder\n.+?(?=\n## |\Z)", block.rstrip() + "\n", md, count=1, flags=re.S)
    return md.rstrip() + f"\n\n{block}"


def merge_tags(tags: list, updates: dict[str, str]) -> list:
    by = {t["name"]: t for t in tags}
    for k, v in updates.items():
        by[k] = {"name": k, "value": v}
    return list(by.values())


def resolve_founder(startup: str, md: str, odoo: dict[str, str]) -> str:
    for src in (extract_meta_founder, extract_section_founder):
        v = src(md)
        if v:
            return v
    key = norm(startup.split(" · ")[0])
    if key in odoo:
        return odoo[key]
    for k, v in odoo.items():
        if key in k or k in key:
            return v
    return ""


def main() -> int:
    env = load_env(BOOK_ENV)
    base = env["BOOKSTACK_URL"].rstrip("/")
    headers = {
        "Authorization": f"Token {env['BOOKSTACK_TOKEN_ID']}:{env['BOOKSTACK_TOKEN_SECRET']}",
        "Content-Type": "application/json",
    }
    odoo = odoo_founders()
    stats = {"pages_updated": 0, "founder_meta_added": 0, "founder_tag_added": 0, "skipped_pendiente": 0}

    page_num = 1
    while True:
        r = requests.get(
            f"{base}/api/search",
            headers=headers,
            params={"query": "{type:page} [app_id]", "count": 100, "page": page_num},
            timeout=60,
        )
        r.raise_for_status()
        batch = r.json().get("data", [])
        if not batch:
            break

        for item in batch:
            pid = item["id"]
            p = requests.get(f"{base}/api/pages/{pid}", headers=headers, timeout=30).json()
            md = p.get("markdown") or ""
            startup = p["name"].split(" · ")[0].strip()
            founder = resolve_founder(startup, md, odoo)
            if not founder:
                stats["skipped_pendiente"] += 1
                continue

            new_md = inject_founder_meta(md, founder)
            if "**Founder:**" not in md:
                stats["founder_meta_added"] += 1
            new_md = sync_founder_section(new_md, founder)

            tags = p.get("tags", [])
            tag_map = {t["name"]: t["value"] for t in tags}
            updates: dict[str, str] = {}
            if tag_map.get("founder") != founder:
                updates["founder"] = founder
                stats["founder_tag_added"] += 1

            payload = {
                "book_id": p["book_id"],
                "chapter_id": p["chapter_id"],
                "name": p["name"],
                "markdown": new_md,
                "tags": merge_tags(tags, updates) if updates else tags,
            }
            if new_md != md or updates:
                requests.put(f"{base}/api/pages/{pid}", headers=headers, json=payload, timeout=30).raise_for_status()
                stats["pages_updated"] += 1

        if len(batch) < 100:
            break
        page_num += 1

    # Epic pages that may need explicit pass (Chum/Cirkula/NUX)
    curated = json.loads(Path("/opt/nexus-idea-browser/src/data/epic-angels-curated.json").read_text())
    epic_urls = []
    for e in curated:
        pid = e.get("bookstack_page_id")
        if not pid:
            continue
        p = requests.get(f"{base}/api/pages/{pid}", headers=headers, timeout=30).json()
        epic_urls.append({
            "startup_name": e["startup_name"],
            "page_id": pid,
            "url": f"{base}/books/idea-browser/page/{p.get('slug', '')}",
            "founder_tag": next((t["value"] for t in p.get("tags", []) if t["name"] == "founder"), ""),
            "founder_meta": extract_meta_founder(p.get("markdown") or ""),
        })

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    report = {"date": date.today().isoformat(), "odoo_partners": len(odoo), **stats, "epic_pages": epic_urls}
    (ARCHIVE / "founders-pipeline-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
