#!/usr/bin/env python3
"""Prepare batch 4–6 startup records: file-based Wiki drafts + optional Odoo (when up).

Wiki: writes ops/wiki-drafts/<slug>.md only (never calls BookStack — draft API still publishes live).
Odoo: skipped by default (--attempt-odoo to try XML-RPC when services.cleantechhub.net is healthy).

Reads onepager JSON from GitHub refs. Sourced facts only; unknowns marked [PENDIENTE].
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xmlrpc.client
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

OWNER, REPO = "gideonblaauw-creator", "cth-nexus"
ROOT = Path(__file__).resolve().parents[1]
WIKI_DRAFTS = ROOT / "ops" / "wiki-drafts"
ODOO_ENV = Path("/opt/odoo-mcp/.env")

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
    "CT-IN-003": "Circular Economy & Clean Mfg",
    "CT-IN-004": "Industrial Symbiosis",
    "CT-XS-003": "Green Finance",
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
    return "[PENDIENTE]"


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
    host = urlparse(url).netloc
    return host.replace("www.", "") if host else None


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
    badge = strip_html(d.get("badge_en", ""))
    program = badge.split("·")[0].strip() if badge else "[PENDIENTE]"
    return {
        "batch": batch,
        "branch": branch,
        "sha": sha,
        "slug": slug,
        "name": d.get("name") or slug,
        "website": website_host(d),
        "website_url": website_url(d),
        "program": program,
        "country": country_code(d),
        "theme": theme_from_data(d),
        "stage": stage,
        "ct1": ct1,
        "pitch_en": strip_html(d.get("pitch_en", "")),
        "pitch_es": strip_html(d.get("pitch_es", "")),
        "founders": founders,
        "pendiente": pend,
    }


def ct_display(code: str) -> str:
    if not code:
        return "[PENDIENTE]"
    label = CT_LABELS.get(code, code)
    return f"{code} · {label}"


def render_wiki_draft(rec: dict) -> str:
    host = rec.get("website")
    web = f"[{host}]({rec['website_url']})" if host else "—"
    stage = rec["stage"] if rec["stage"] != "[PENDIENTE]" else "[PENDIENTE]"
    theme_map = {"CE": "Circular Economy", "BIO": "Bioeconomy", "EN": "Energy Transition"}
    sector = theme_map.get(rec["theme"], "Circular Economy")
    founder_lines: list[str] = []
    if rec.get("founders"):
        for f in rec["founders"]:
            li = f.get("linkedin")
            role = f.get("role") or "Founder"
            if li:
                founder_lines.append(f"- **{f['name']}** — {role} · [LinkedIn]({li})")
            else:
                founder_lines.append(f"- **{f['name']}** — {role} · LinkedIn: [PENDIENTE]")
    else:
        founder_lines.append("[PENDIENTE]")

    founder_tag = rec["founders"][0]["name"] if rec.get("founders") else "[PENDIENTE]"
    ct_primary = rec.get("ct1") or "[PENDIENTE]"
    fm = f"""status: draft-file-only
bookstack_publish: false
nexus_slug: {rec['slug']}
source_branch: {rec['branch']}
source_sha: {rec['sha']}
batch: {rec['batch']}
country: {rec['country']}
program: {rec.get('program') or '[PENDIENTE]'}
stage: {stage}
ct_primary: {ct_primary}
tag_type: startup-profile
tag_source: nexus-s-pages-batch
tag_founder: {founder_tag}"""
    founders_block = "\n".join(founder_lines)
    pitch_es = rec.get("pitch_es") or "[PENDIENTE]"

    return f"""---
{fm}
---

# {rec['name']}

> HITL: paste into BookStack Startup Portfolio book after review. Do not auto-import.

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

## Description (EN)
{rec.get('pitch_en') or '[PENDIENTE]'}

## Description (ES)
{pitch_es}

## Founders
{founders_block}

## Source
- JSON: `onepagers/data/{rec['slug']}.json` @ `{rec['sha']}` ({rec['branch']})
"""


def write_wiki_draft(rec: dict) -> dict:
    WIKI_DRAFTS.mkdir(parents=True, exist_ok=True)
    path = WIKI_DRAFTS / f"{rec['slug']}.md"
    content = render_wiki_draft(rec)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing.strip() == content.strip():
            return {"path": str(path.relative_to(ROOT)), "action": "unchanged"}
    path.write_text(content, encoding="utf-8")
    return {"path": str(path.relative_to(ROOT)), "action": "written"}


def sync_odoo(rec: dict) -> dict:
    return {"status": "skipped", "reason": "Odoo XML-RPC unavailable (502); run with --attempt-odoo when services are up"}


def attempt_odoo(rec: dict) -> dict:
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
    return {"status": "ok", "note": "Odoo reachable; full upsert not implemented in file-only mode"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-odoo", action="store_true", help="Probe Odoo auth only")
    parser.add_argument("--report", type=Path, default=Path("/tmp/s-pages-batch-4-6-sync-report.json"))
    args = parser.parse_args()

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
                "wiki_draft": write_wiki_draft(rec),
            }
            if args.attempt_odoo:
                row["odoo"] = attempt_odoo(rec)
            else:
                row["odoo"] = sync_odoo(rec)
            report.append(row)

    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(args.report)
    print(json.dumps({
        "slugs": len(report),
        "wiki_written": sum(1 for r in report if r["wiki_draft"].get("action") == "written"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
