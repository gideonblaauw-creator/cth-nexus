#!/usr/bin/env python3
"""Sync Nexus /s/ batch slugs → Odoo (org + founder contacts) and BookStack wiki (draft).

Reads onepager JSON from GitHub refs (batch 4–6). Idempotent: skips filled fields.
"""
from __future__ import annotations

import json
import re
import sys
import xmlrpc.client
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

import requests

OWNER, REPO = "gideonblaauw-creator", "cth-nexus"
BOOK_ID = 1694
CHAPTER_BY_THEME = {"CE": 1751, "BIO": 1752, "EN": 1753}
ODOO_ENV = Path("/opt/odoo-mcp/.env")
BOOK_ENV = Path("/opt/idea-browser/.env")

BATCHES: dict[str, tuple[str, str, list[str]]] = {
    "batch4": ("a91df06", "feat/s-pages-batch-4-9a1a", [
        "ala-terra", "compostpack", "cr-tejas", "deposito-global-recycling", "deterquin",
    ]),
    "batch5": ("82b5da4", "feat/s-pages-batch-5", [
        "dexon-software-sas-bic", "eco-biosis", "eco-industria", "embergy", "fluvia",
    ]),
    "batch6": ("5803c86", "feat/s-pages-batch-6", [
        "galaxy-pack", "glooba", "glu-energy", "griin-energy", "grupo-natural-andino",
    ]),
}

CT_LABELS = {
    "CT-WA-003": "Recycling & Materials Recovery",
    "CT-WA-004": "Extended Producer Responsibility",
    "CT-WW-003": "Watershed Conservation",
    "CT-IC-005": "Precision Ag & Smart Grid",
    "CT-WA-001": "Waste-to-Energy & Biogas",
    "CT-WA-002": "Organic Waste & Composting",
    "CT-EN-001": "Solar PV",
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


def fetch_json(slug: str, ref: str) -> dict:
    url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{ref}/onepagers/data/{slug}.json"
    with urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode())


def strip_html(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"&middot;", " · ", s)
    s = re.sub(r"&[^;]+;", "", s)
    return unescape(re.sub(r"<[^>]+>", "", s))


def ct_from_data(d: dict) -> str:
    for r in d.get("ribbon") or []:
        v = str(r.get("val", ""))
        if v.startswith("CT-"):
            return v
    m = re.search(r"(CT-[A-Z]{2}-\d{3})", strip_html(d.get("hero_sub_en", "")))
    return m.group(1) if m else ""


def country_code(d: dict) -> str:
    for r in d.get("ribbon") or []:
        if r.get("lab_en") == "Country":
            sub = r.get("sub_en") or ""
            if sub == "Mexico":
                return "MX"
            if sub == "Colombia":
                return "CO"
            if sub == "Chile":
                return "CL"
            if sub == "Peru":
                return "PE"
            if sub == "Costa Rica":
                return "CR"
            val = r.get("val", "")
            if val in ("MX", "CO", "CL", "PE", "CR"):
                return val
    return "CO"


def theme_from_data(d: dict) -> str:
    for r in d.get("ribbon") or []:
        if r.get("lab_en") == "Sector":
            v = r.get("val", "")
            if v in ("Food",) or v == "BIO":
                return "BIO"
            if "Energy" in v or v == "EN":
                return "EN"
            return "CE"
    return "CE"


def stage_from_data(d: dict) -> str:
    for r in d.get("ribbon") or []:
        if r.get("lab_en") == "Stage":
            v = r.get("val", "")
            if v.startswith("[P"):
                return "[PENDIENTE]"
            return v
    return "[PENDIENTE"


def website_url(d: dict) -> str | None:
    w = (d.get("website") or "").strip()
    if not w or w == "#":
        return None
    if w.startswith("http"):
        return w
    return f"https://{w}"


def website_host(d: dict) -> str | None:
    url = website_url(d)
    if not url:
        return None
    host = urlparse(url).netloc or urlparse(f"https://{url}").path
    return host.replace("www.", "")


def founders_from_data(d: dict) -> list[dict]:
    out: list[dict] = []
    for sec in d.get("sections") or []:
        if sec.get("type") != "team":
            continue
        for m in sec.get("members") or []:
            name = (m.get("name") or "").strip()
            if not name or name.startswith("[PENDIENTE"):
                continue
            li = (m.get("linkedin") or "").strip() or None
            out.append({
                "name": name,
                "role": strip_html(m.get("role_en") or m.get("role_es") or ""),
                "linkedin": li,
            })
    return out


def parse_record(slug: str, ref: str, branch: str, sha: str, batch: str) -> dict:
    d = fetch_json(slug, ref)
    ct1 = ct_from_data(d)
    pend: list[str] = []
    stage = stage_from_data(d)
    if stage == "[PENDIENTE]":
        pend.append("stage")
    if not website_host(d):
        pend.append("website")
    if not ct1:
        pend.append("ct_taxonomy")
    founders = founders_from_data(d)
    if not founders:
        pend.append("founder")
    elif any(not f.get("linkedin") for f in founders):
        pend.append("founder_linkedin")
    return {
        "batch": batch,
        "branch": branch,
        "sha": sha,
        "slug": slug,
        "name": d.get("name") or slug,
        "website": website_host(d),
        "website_url": website_url(d),
        "program": strip_html(d.get("badge_en", "")).split("·")[0].strip(),
        "country": country_code(d),
        "theme": theme_from_data(d),
        "stage": stage,
        "ct1": ct1,
        "pitch_en": strip_html(d.get("pitch_en", "")),
        "pitch_es": strip_html(d.get("pitch_es", "")),
        "founders": founders,
        "pendiente": pend,
        "_raw": d,
    }


class BookStack:
    def __init__(self) -> None:
        env = load_env(BOOK_ENV)
        self.base = env["BOOKSTACK_URL"].rstrip("/")
        self.headers = {
            "Authorization": f"Token {env['BOOKSTACK_TOKEN_ID']}:{env['BOOKSTACK_TOKEN_SECRET']}",
            "Content-Type": "application/json",
        }

    def get(self, path: str, **params):
        r = requests.get(f"{self.base}/api{path}", headers=self.headers, params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def put(self, path: str, payload: dict):
        r = requests.put(f"{self.base}/api{path}", headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def post(self, path: str, payload: dict):
        r = requests.post(f"{self.base}/api{path}", headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def find_page(self, name: str, slug: str) -> dict | None:
        for q in (f'{{tags:nexus_slug={slug}}}', f'"{name}" {{type:page}}', slug):
            data = self.get("/search", query=q, count=15)
            for item in data.get("data", []):
                if item.get("type") != "page":
                    continue
                page = self.get(f"/pages/{item['id']}")
                tags = {t["name"]: t.get("value") for t in page.get("tags", [])}
                if tags.get("nexus_slug") == slug:
                    return page
                if item.get("name", "").lower() == name.lower():
                    return page
                if slug.replace("-", " ") in item.get("name", "").lower():
                    return page
        return None

    def merge_tags(self, tags: list[dict], updates: dict[str, str]) -> list[dict]:
        by_name = {t["name"]: t for t in tags}
        for k, v in updates.items():
            if v:
                by_name[k] = {"name": k, "value": v}
        return list(by_name.values())


def ct_display(code: str) -> str:
    if not code:
        return "[PENDIENTE]"
    label = CT_LABELS.get(code, code)
    return f"{code} · {label}"


def ensure_founders_md(md: str, founders: list[dict]) -> str:
    if "## Founder" in md or "## Founders" in md:
        return md
    if not founders:
        block = "## Founders\n\n[PENDIENTE]\n"
    else:
        lines = ["## Founders", ""]
        for f in founders:
            li = f.get("linkedin")
            if li:
                lines.append(f"- **{f['name']}** — {f.get('role') or 'Founder'} · [LinkedIn]({li})")
            else:
                lines.append(f"- **{f['name']}** — {f.get('role') or 'Founder'} · LinkedIn: [PENDIENTE]")
        lines.append("")
        block = "\n".join(lines)
    if md.strip():
        return md.rstrip() + "\n\n---\n\n" + block
    return block


def patch_ct_snapshot(md: str, ct_code: str) -> str:
    if not ct_code:
        return md
    disp = ct_display(ct_code)
    if "| CT Taxonomy |" not in md:
        return md
    if re.search(r"\| CT Taxonomy \| \[PENDIENTE\]", md):
        return re.sub(r"\| CT Taxonomy \| \[PENDIENTE\] \|", f"| CT Taxonomy | {disp} |", md, count=1)
    if re.search(r"\| CT Taxonomy \| — \|", md):
        return re.sub(r"\| CT Taxonomy \| — \|", f"| CT Taxonomy | {disp} |", md, count=1)
    return md


def render_new_page(rec: dict) -> str:
    host = rec.get("website")
    web = f"[{host}]({rec['website_url']})" if host else "—"
    stage = rec["stage"] if rec["stage"] != "[PENDIENTE]" else "[PENDIENTE]"
    theme_map = {"CE": "Circular Economy", "BIO": "Bioeconomy", "EN": "Energy Transition"}
    sector = theme_map.get(rec["theme"], "Circular Economy")
    md = f"""# {rec['name']}

## Snapshot
| Field | Value |
|-------|-------|
| Sector | {sector} |
| Stage | {stage} |
| Country | {rec['country']} |
| Program | {rec.get('program') or '[PENDIENTE]'} |
| Website | {web} |
| CT Taxonomy | {ct_display(rec.get('ct1') or '')} |
| Nexus one-pager | [nexus.cleantechhub.net/s/{rec['slug']}](https://nexus.cleantechhub.net/s/{rec['slug']}) |

## Description
{rec.get('pitch_en') or '[PENDIENTE]'}

"""
    return ensure_founders_md(md, rec.get("founders") or [])


def sync_wiki(bs: BookStack, rec: dict) -> dict:
    existing = bs.find_page(rec["name"], rec["slug"])
    chapter_id = CHAPTER_BY_THEME.get(rec["theme"], 1751)
    ct_code = rec.get("ct1") or ""
    founder0 = (rec.get("founders") or [{}])[0].get("name") if rec.get("founders") else ""
    tag_updates = {
        "type": "startup-profile",
        "nexus_slug": rec["slug"],
        "source": "nexus-s-pages-batch",
        "country": rec["country"],
        "stage": rec["stage"] if rec["stage"] != "[PENDIENTE]" else "pending",
    }
    if ct_code:
        tag_updates["ct_primary"] = ct_code
    if founder0:
        tag_updates["founder"] = founder0

    if existing:
        md = existing.get("markdown") or ""
        md = patch_ct_snapshot(md, ct_code)
        md = ensure_founders_md(md, rec.get("founders") or [])
        tags = bs.merge_tags(existing.get("tags", []), tag_updates)
        payload = {
            "book_id": existing["book_id"],
            "chapter_id": existing.get("chapter_id") or chapter_id,
            "name": existing["name"],
            "markdown": md,
            "tags": tags,
            "draft": True,
        }
        bs.put(f"/pages/{existing['id']}", payload)
        slug_path = existing.get("slug") or ""
        url = f"{bs.base}/books/startup-portfolio/page/{slug_path}" if slug_path else f"{bs.base}/books/startup-portfolio"
        return {"wiki_id": existing["id"], "wiki_url": url, "action": "updated_draft", "status": "existing"}

    md = render_new_page(rec)
    tags = [{"name": k, "value": v} for k, v in tag_updates.items() if v]
    created = bs.post("/pages", {
        "book_id": BOOK_ID,
        "chapter_id": chapter_id,
        "name": rec["name"],
        "markdown": md,
        "tags": tags,
        "draft": True,
    })
    slug_path = created.get("slug") or ""
    url = f"{bs.base}/books/startup-portfolio/page/{slug_path}"
    return {"wiki_id": created["id"], "wiki_url": url, "action": "created_draft", "status": "new"}


def odoo_exec(models, db, uid, pwd, model, method, *args, **kwargs):
    return models.execute_kw(db, uid, pwd, model, method, list(args), kwargs)


def sync_odoo(rec: dict) -> dict:
    env = load_env(ODOO_ENV)
    if not env.get("ODOO_URL"):
        return {"status": "skipped", "error": "ODOO_URL missing"}
    url = env["ODOO_URL"]
    db = env["ODOO_DB"]
    user = env.get("ODOO_USERNAME") or env.get("ODOO_USER", "")
    pwd = env["ODOO_PASSWORD"]
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, user, pwd, {})
    except Exception as e:
        return {"status": "error", "error": str(e)}
    if not uid:
        return {"status": "error", "error": "auth failed"}

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
    name = rec["name"]
    domain = [
        "&",
        "|",
        ("name", "ilike", name),
        ("x_startup_name", "ilike", rec["slug"]),
        ("is_company", "=", True),
    ]
    existing = odoo_exec(models, db, uid, pwd, "res.partner", "search_read", [domain], {
        "fields": ["id", "name", "website", "comment", "x_startup_name"],
        "limit": 5,
    })
    values: dict = {"is_company": True, "active": True}
    if rec.get("website_url"):
        values["website"] = rec["website_url"]
    if rec.get("slug"):
        values["x_startup_name"] = rec["slug"]

    partner_id: int | None = None
    action = "existing"
    if existing:
        partner_id = existing[0]["id"]
        write_vals = {}
        if rec.get("website_url") and not (existing[0].get("website") or "").strip():
            write_vals["website"] = rec["website_url"]
        if rec.get("slug") and not (existing[0].get("x_startup_name") or "").strip():
            write_vals["x_startup_name"] = rec["slug"]
        if write_vals:
            odoo_exec(models, db, uid, pwd, "res.partner", "write", [[partner_id], write_vals])
            action = "updated_blanks"
    else:
        values["name"] = name
        partner_id = odoo_exec(models, db, uid, pwd, "res.partner", "create", [values])
        action = "created_draft"

    founder_ids: list[int] = []
    for f in rec.get("founders") or []:
        if not f.get("linkedin"):
            continue
        fd = [("name", "=", f["name"]), ("is_company", "=", False)]
        fex = odoo_exec(models, db, uid, pwd, "res.partner", "search_read", [fd], {
            "fields": ["id", "website"], "limit": 1,
        })
        fvals = {"name": f["name"], "is_company": False, "website": f["linkedin"], "active": True}
        if fex:
            fid = fex[0]["id"]
            if not (fex[0].get("website") or "").strip():
                odoo_exec(models, db, uid, pwd, "res.partner", "write", [[fid], {"website": f["linkedin"]}])
        else:
            fid = odoo_exec(models, db, uid, pwd, "res.partner", "create", [fvals])
        founder_ids.append(fid)

    return {"status": "ok", "odoo_id": partner_id, "action": action, "founder_contacts": founder_ids}


def main() -> int:
    bs = BookStack()
    report: list[dict] = []
    for batch, (sha, branch, slugs) in BATCHES.items():
        for slug in slugs:
            rec = parse_record(slug, sha, branch, sha, batch)
            row = {
                "slug": slug,
                "batch": batch,
                "branch": branch,
                "sha": sha,
                "pendiente": rec["pendiente"],
            }
            row["odoo"] = sync_odoo(rec)
            try:
                row["wiki"] = sync_wiki(bs, rec)
            except Exception as e:
                row["wiki"] = {"status": "error", "error": str(e)}
            report.append(row)

    out = Path("/tmp/s-pages-batch-4-6-sync-report.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(out)
    print(json.dumps({"slugs": len(report), "odoo_ok": sum(1 for r in report if r["odoo"].get("status") == "ok")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
