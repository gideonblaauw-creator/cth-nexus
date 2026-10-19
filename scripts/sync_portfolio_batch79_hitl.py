#!/usr/bin/env python3
"""HITL sync: BookStack Startup Portfolio (book 1694) for /s/ batch 8–9 slugs.

Reads onepager JSON from feat/s-pages-batch-8/9. Creates missing wiki pages as draft;
updates only blank founder / CT taxonomy fields on existing pages; sets draft=True.
Writes audit JSON under ops/audits/.

Odoo is handled separately (blocked if services.cleantechhub.net returns 502).
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
BOOK_ID = 1694
CHAPTER = {"CE": 1751, "BIO": 1752, "EN": 1753}
BOOK_ENV = Path("/opt/idea-browser/.env")
BATCH_REFS = {
    "origin/feat/s-pages-batch-8": ROOT,  # JSON read via git show from merge remote
}
MERGE_ROOT = Path("/home/debian/cth-nexus-merge")

EXISTING_PAGE = {
    "kigui": 1784,
    "kimsa": 1804,
    "monte-jazmin": 1845,
    "moviltronics": 1813,
}

COUNTRY_CODE = {
    "Guatemala": "GT",
    "Mexico": "MX",
    "México": "MX",
    "Colombia": "CO",
    "Costa Rica": "CR",
    "Peru": "PE",
    "Perú": "PE",
    "Brasil": "BR",
    "Brazil": "BR",
}

CT_LABEL = {
    "CT-WA-002": "Organic Waste & Composting",
    "CT-IC-002": "AI-Powered MRV, Carbon Markets & Credits",
    "CT-XS-001": "Carbon Offset Projects",
    "CT-AF-001": "Sustainable Agriculture & Food Systems",
    "CT-TR-001": "Sustainable Transport",
    "CT-EN-001": "Energy Generation & Distribution",
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


def strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).replace("\xa0", " ").strip()


def git_show_json(slug: str) -> dict:
    for ref in ("origin/feat/s-pages-batch-8", "origin/feat/s-pages-batch-9"):
        path = f"onepagers/data/{slug}.json"
        try:
            raw = subprocess.check_output(
                ["git", "show", f"{ref}:{path}"],
                cwd=MERGE_ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            )
            return json.loads(raw)
        except subprocess.CalledProcessError:
            continue
    raise FileNotFoundError(slug)


def parse_record(page: dict) -> dict:
    slug = page["slug"]
    name = page["name"]
    website = page.get("website", "")
    domain = (
        re.sub(r"^https?://", "", website).rstrip("/").replace("www.", "")
        if website
        else ""
    )
    country_name = strip_html(
        next(
            (r.get("sub_en") for r in page.get("ribbon", []) if r.get("lab_en") == "Country"),
            "",
        )
    )
    cc = COUNTRY_CODE.get(country_name, "")
    hero = strip_html(page.get("hero_sub_en", ""))
    stage = "[PENDIENTE]"
    m = re.search(r"Stage:\s*([^·]+)", hero)
    if m:
        stage = m.group(1).strip()
    badge = strip_html(page.get("badge_en", ""))
    program = "Acceleration"
    for token in ("CLP", "CLAC21", "CLAC22", "CLAC23", "CLAC24", "CLAC25"):
        if token in badge:
            program = token
            break
    theme = "CE"
    if any(x in badge for x in ("Energy", "Carbon MRV", "Electric", "EV")):
        theme = "EN"
    elif any(x in badge for x in ("Bio", "Coffee", "Agr")):
        theme = "BIO"
    if slug == "istmo-verde":
        theme = "EN"
    ct1 = ct2 = ""
    for sec in page.get("sections", []):
        if sec.get("type") != "impact":
            continue
        for card in sec.get("cards", []):
            if "Taxonomy" not in card.get("title_en", ""):
                continue
            txt = strip_html(card.get("text_en", ""))
            codes = re.findall(r"CT-[A-Z]{2}-\d{3}", txt)
            if codes:
                ct1, *rest = codes
                ct2 = rest[0] if rest else ""
            elif "[PENDIENTE]" in txt:
                ct1 = "[PENDIENTE]"
    if not ct1:
        ct1 = "[PENDIENTE]"
    members = []
    for sec in page.get("sections", []):
        if sec.get("type") == "team":
            for mem in sec.get("members", []):
                members.append(
                    {
                        "name": strip_html(mem.get("name", "")),
                        "linkedin": mem.get("linkedin"),
                    }
                )
    founders = [m["name"] for m in members if m["name"]]
    founder_str = ", ".join(founders) if founders else "[PENDIENTE]"
    pitch_en = strip_html(page.get("pitch_en", ""))
    pitch_es = strip_html(page.get("pitch_es", ""))
    return {
        "slug": slug,
        "name": name,
        "website": website,
        "domain": domain,
        "country_name": country_name,
        "cc": cc,
        "stage": stage,
        "program": program,
        "theme": theme,
        "ct1": ct1,
        "ct2": ct2,
        "founder_str": founder_str,
        "pitch_en": pitch_en,
        "pitch_es": pitch_es,
    }


def ct_display(ct_code: str) -> str:
    if ct_code.startswith("CT-"):
        return CT_LABEL.get(ct_code, ct_code)
    return ct_code


def render_markdown(rec: dict) -> str:
    ct_line = ct_display(rec["ct1"])
    if rec["ct2"] and rec["ct2"].startswith("CT-"):
        ct_line += f"; {ct_display(rec['ct2'])}"
    sector = {"CE": "Circular Economy", "BIO": "Bioeconomy", "EN": "Energy Transition"}[rec["theme"]]
    web_cell = f"[{rec['domain']}]({rec['website']})" if rec["website"] else "—"
    return f"""# {rec['name']}

**Founder:** {rec['founder_str']}

## Snapshot
| Field | Value |
|-------|-------|
| Sector | {sector} |
| Stage | {rec['stage']} |
| Country | {rec['country_name']} |
| Program | {rec['program']} |
| Website | {web_cell} |
| CT Taxonomy | {ct_line} |
| Nexus /s/ | https://nexus.cleantechhub.net/s/{rec['slug']} |

## Description
{rec['pitch_en']}

## Source Notes
Sourced from Nexus one-pager JSON (feat/s-pages-batch-8/9). HITL draft — unpublished pending Gideon review.
"""


class BS:
    def __init__(self) -> None:
        env = load_env(BOOK_ENV)
        self.base = env["BOOKSTACK_URL"].rstrip("/")
        self.headers = {
            "Authorization": f"Token {env['BOOKSTACK_TOKEN_ID']}:{env['BOOKSTACK_TOKEN_SECRET']}",
            "Content-Type": "application/json",
        }

    def get_page(self, pid: int) -> dict:
        r = requests.get(f"{self.base}/api/pages/{pid}", headers=self.headers, timeout=60)
        r.raise_for_status()
        return r.json()

    def put_page(self, pid: int, payload: dict) -> dict:
        r = requests.put(f"{self.base}/api/pages/{pid}", headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def post_page(self, payload: dict) -> dict:
        r = requests.post(f"{self.base}/api/pages", headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def merge_tags(self, tags: list, updates: dict[str, str]) -> list:
        by = {t["name"]: t for t in tags}
        for k, v in updates.items():
            if v:
                by[k] = {"name": k, "value": v}
        return list(by.values())


def inject_founder(md: str, founder: str) -> str:
    if founder.startswith("[PENDIENTE]"):
        return md
    if re.search(r"\*\*Founder:\*\*", md):
        val = re.search(r"\*\*Founder:\*\*\s*(.+)", md)
        if val and val.group(1).strip() not in ("", "[PENDIENTE]"):
            return md
        return re.sub(r"\*\*Founder:\*\*\s*.+", f"**Founder:** {founder}", md, count=1)
    title_line = md.splitlines()[0] if md else ""
    if title_line.startswith("# "):
        return title_line + f"\n\n**Founder:** {founder}\n" + "\n".join(md.splitlines()[1:])
    return f"**Founder:** {founder}\n\n" + md


def update_ct_row(md: str, ct_line: str) -> str:
    if "| CT Taxonomy |" not in md:
        return md
    row = re.search(r"\| CT Taxonomy \|([^|]+)\|", md)
    if row and row.group(1).strip() not in ("", "—", "[PENDIENTE]"):
        return md
    return re.sub(r"\| CT Taxonomy \|[^|]+\|", f"| CT Taxonomy | {ct_line} |", md, count=1)


def main() -> int:
    slugs = [
        "istmo-verde",
        "kigui",
        "kimsa",
        "kleantab",
        "linko-workers",
        "mayugo",
        "mitsidi",
        "monte-jazmin",
        "moviltronics",
        "myma",
    ]
    bs = BS()
    audit = {"date": date.today().isoformat(), "book_id": BOOK_ID, "wiki": []}

    for slug in slugs:
        rec = parse_record(git_show_json(slug))
        ct_tag = rec["ct1"] if rec["ct1"].startswith("CT-") else ""
        tag_updates = {
            "nexus_slug": slug,
            "source": "CTH-Acceleration",
            "country": rec["country_name"],
            "stage": rec["stage"],
        }
        if ct_tag:
            tag_updates["ct_taxonomy"] = ct_tag
        if rec["founder_str"] and not rec["founder_str"].startswith("[PENDIENTE]"):
            tag_updates["founder"] = rec["founder_str"]

        if slug in EXISTING_PAGE:
            pid = EXISTING_PAGE[slug]
            page = bs.get_page(pid)
            md = page.get("markdown") or ""
            new_md = inject_founder(md, rec["founder_str"])
            new_md = update_ct_row(new_md, ct_display(rec["ct1"]))
            tags = bs.merge_tags(page.get("tags", []), tag_updates)
            if new_md != md or tags != page.get("tags", []):
                bs.put_page(
                    pid,
                    {
                        "book_id": page["book_id"],
                        "chapter_id": page["chapter_id"],
                        "name": page["name"],
                        "markdown": new_md,
                        "tags": tags,
                        "draft": True,
                    },
                )
                action = "updated_draft"
            else:
                bs.put_page(
                    pid,
                    {
                        "book_id": page["book_id"],
                        "chapter_id": page["chapter_id"],
                        "name": page["name"],
                        "markdown": md,
                        "tags": tags,
                        "draft": True,
                    },
                )
                action = "marked_draft_only"
            url = f"{bs.base}/books/startup-portfolio/page/{page.get('slug', '')}"
            audit["wiki"].append({"slug": slug, "page_id": pid, "action": action, "url": url})
            continue

        chapter_id = CHAPTER[rec["theme"]]
        page_title = rec["name"].upper() if rec["name"].isupper() else rec["name"]
        md = render_markdown(rec)
        tags = [{"name": k, "value": v} for k, v in tag_updates.items() if v]
        created = bs.post_page(
            {
                "book_id": BOOK_ID,
                "chapter_id": chapter_id,
                "name": page_title,
                "markdown": md,
                "tags": tags,
                "draft": True,
            }
        )
        url = f"{bs.base}/books/startup-portfolio/page/{created.get('slug', '')}"
        audit["wiki"].append(
            {
                "slug": slug,
                "page_id": created["id"],
                "action": "created_draft",
                "url": url,
            }
        )

    out = ROOT / "ops" / "audits" / f"portfolio-batch79-wiki-{date.today().isoformat()}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
