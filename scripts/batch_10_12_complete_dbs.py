#!/usr/bin/env python3
"""Batches 10–12 — Odoo → Wiki drafts → Nexus portfolio cards (HITL).

Wiki content is written to ops/wiki-drafts/<slug>.md (BookStack API is not used;
draft:true publishes live). Reads onepagers/data/{slug}.json from s-pages batches.
Skips suncolombia (owned by batch 0–3). No founder email.

  python3 scripts/batch_10_12_complete_dbs.py sync
  python3 scripts/batch_10_12_complete_dbs.py cards
  python3 scripts/batch_10_12_complete_dbs.py all
"""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
import xmlrpc.client
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data"
PORTFOLIO_HTML = ROOT / "pages" / "p" / "startup-portfolio" / "index.html"
ARCHIVE = ROOT / "Archive" / "s-pages-batch-10-12-20261019"
WIKI_DRAFTS = ROOT / "ops" / "wiki-drafts"
ODOO_ENV = Path("/opt/cth-nexus/.env")

BOOK_STARTUP_PORTFOLIO = 1694
CHAPTER_CIRCULAR = 1751
CHAPTER_BIO = 1752
CHAPTER_ENERGY = 1753

BATCH_10 = [
    "nina-energy",
    "nuevas-tecnologias-fisicoquimicas",
    "oasis-group",
    "pacaceite",
    "parsons-kinetics",
]
BATCH_11 = ["plasfacol", "pleia", "purest-fuels", "kelab", "simbiotic"]
BATCH_12 = ["tavi-technology", "tr-global-group", "valopes", "wheelo"]

ALL_SLUGS = BATCH_10 + BATCH_11 + BATCH_12

BOOK_SLUGS = {1694: "startup-portfolio"}


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


def norm_name(s: str) -> str:
    s = html.unescape(s or "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9 ]+", " ", s).upper()
    return re.sub(r"\s+", " ", s).strip()


def website_host(url: str | None) -> str | None:
    if not url or url.strip() in ("", "#"):
        return None
    u = url.strip()
    u = re.sub(r"^https?://", "", u, flags=re.I)
    return u.rstrip("/").split("/")[0] or None


def parse_ct_codes(text: str) -> tuple[str, str]:
    codes = re.findall(r"CT-[A-Z]{2}-\d{3}", text or "")
    ct1 = codes[0] if codes else ""
    ct2 = codes[1] if len(codes) > 1 else ""
    return ct1, ct2


def theme_from_json(d: dict) -> str:
    sector = ""
    for rib in d.get("ribbon") or []:
        if rib.get("lab_en") == "Sector":
            sector = (rib.get("sub_en") or rib.get("val") or "").lower()
    badge = html.unescape(d.get("badge_en") or "").lower()
    blob = f"{sector} {badge}"
    if any(x in blob for x in ("bio", "agri", "food", "cacao", "coffee")):
        return "BIO"
    if any(x in blob for x in ("energy", "solar", "wind", "hydrogen", "ev", "mobility", "electric")):
        return "EN"
    return "CE"


def stage_from_json(d: dict) -> str:
    for rib in d.get("ribbon") or []:
        if rib.get("lab_en") == "Stage":
            val = (rib.get("val") or "").strip()
            if val and val not in ("PENDIENTE", "[P]", "P"):
                return val
            sub = (rib.get("sub_en") or "").strip()
            if sub and "pendiente" not in sub.lower():
                return sub
    return "[PENDIENTE]"


def country_from_json(d: dict) -> tuple[str, str]:
    rib = (d.get("ribbon") or [{}])[0]
    code = (rib.get("val") or "CO").strip()
    if code in ("PENDIENTE", "[P]", "P"):
        code = "CO"
    name = rib.get("sub_en") or rib.get("sub_es") or code
    return code[:2].upper(), name


def team_members(d: dict) -> list[dict]:
    for sec in d.get("sections") or []:
        if sec.get("type") == "team":
            return sec.get("members") or []
    return []


def taxonomy_text(d: dict) -> str:
    for sec in d.get("sections") or []:
        if sec.get("type") != "impact":
            continue
        for card in sec.get("cards") or []:
            if "taxonom" in (card.get("title_en") or "").lower():
                return html.unescape(card.get("text_en") or "")
    return ""


def founder_display(members: list[dict]) -> str:
    names = [m.get("name", "").strip() for m in members if m.get("name")]
    return ", ".join(names) if names else "[PENDIENTE]"


def chapter_for_theme(theme: str) -> int:
    if theme == "BIO":
        return CHAPTER_BIO
    if theme == "EN":
        return CHAPTER_ENERGY
    return CHAPTER_CIRCULAR


def inject_founder_meta(md: str, founder: str) -> str:
    line = f"**Founder:** {founder}"
    if re.search(r"\*\*Founder:\*\*", md):
        return re.sub(r"\*\*Founder:\*\*\s*.+", line, md, count=1)
    m = re.match(r"(# .+\n\n)", md)
    if m:
        return md.replace(m.group(1), m.group(1) + line + "\n\n", 1)
    return f"{line}\n\n{md}"


def portfolio_markdown(spec: dict, founder: str) -> str:
    site = spec.get("website") or "[PENDIENTE]"
    return f"""# {spec['display_name'].upper()}

**Founder:** {founder}

## Snapshot
| Field | Value |
|-------|-------|
| Sector | {spec['sector']} |
| Stage | {spec['stage']} |
| Country | {spec['country_name']} |
| Program | {spec['program']} |
| Website | {site} |
| CT Taxonomy | {spec['taxonomy']} |
| Nexus | https://nexus.cleantechhub.net/s/{spec['slug']} |

## Description
{spec['description_en']}

## Founder
{founder}
"""


def load_json_spec(slug: str) -> dict:
    path = DATA_DIR / f"{slug}.json"
    if not path.exists():
        raise FileNotFoundError(path)
    d = json.loads(path.read_text())
    members = team_members(d)
    tax = taxonomy_text(d)
    ct1, ct2 = parse_ct_codes(tax)
    cc, cname = country_from_json(d)
    theme = theme_from_json(d)
    web = website_host(d.get("website"))
    founders = []
    for m in members:
        role = html.unescape(m.get("role_en") or "Founder")
        fn = "Founder" if "founder" in role.lower() else role.split("·")[0].strip()
        founders.append(
            {
                "name": html.unescape(m.get("name") or "").strip(),
                "function": fn[:64],
                "linkedin": (m.get("linkedin") or "").strip(),
            }
        )
    display = html.unescape(re.sub(r"<[^>]+>", " ", d.get("name") or slug))
    return {
        "slug": slug,
        "display_name": display,
        "odoo_company": display,
        "name": display,
        "website": d.get("website") if web else None,
        "website_host": web,
        "country_code": cc,
        "country_name": cname,
        "program": "Acceleration",
        "program_card": "CLP",
        "sector": theme,
        "stage": stage_from_json(d),
        "theme": theme,
        "taxonomy": tax or "[PENDIENTE]",
        "ct1": ct1,
        "ct2": ct2,
        "description_en": d.get("pitch_en") or "[PENDIENTE]",
        "description_es": d.get("pitch_es") or d.get("pitch_en") or "[PENDIENTE]",
        "founders": founders,
        "founder_line": founder_display(members),
        "pendiente": [],
    }


class Odoo:
    def __init__(self) -> None:
        env = load_env(ODOO_ENV)
        self.url = env.get("ODOO_URL") or env.get("ODOO_BASE_URL", "")
        self.db = env["ODOO_DB"]
        self.user = env.get("ODOO_USERNAME") or env.get("ODOO_USER", "")
        self.pwd = env["ODOO_PASSWORD"]
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)
        self.uid = common.authenticate(self.db, self.user, self.pwd, {})
        if not self.uid:
            raise RuntimeError("Odoo auth failed")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)

    def kw(self, model: str, method: str, args=None, kwargs=None):
        return self.models.execute_kw(
            self.db, self.uid, self.pwd, model, method, args or [], kwargs or {}
        )

    def upsert_startup(self, s: dict, draft: bool = True) -> dict:
        slug = s["slug"]
        hits = self.kw(
            "res.partner",
            "search_read",
            [[("x_startup_name", "=", slug), ("is_company", "=", True)]],
            {"fields": ["id", "website", "name"], "limit": 1},
        )
        company_id = hits[0]["id"] if hits else None
        company_vals: dict = {
            "is_company": True,
            "x_startup_name": slug,
            "x_nexus_source_program": s["program"],
        }
        if not company_id:
            company_vals["name"] = s["odoo_company"]
            company_vals["active"] = not draft
        if s.get("website_host") and (not company_id or not hits[0].get("website")):
            company_vals["website"] = f"https://{s['website_host']}"

        if company_id:
            write_vals = {k: v for k, v in company_vals.items() if k != "name"}
            if write_vals:
                self.kw("res.partner", "write", [[company_id], write_vals])
        else:
            company_id = self.kw("res.partner", "name_create", [s["odoo_company"]])[0]
            self.kw("res.partner", "write", [[company_id], company_vals])

        founder_ids = []
        for f in s["founders"]:
            if not f.get("name"):
                continue
            fhits = self.kw(
                "res.partner",
                "search_read",
                [[("parent_id", "=", company_id), ("name", "ilike", f["name"].split()[0])]],
                {"fields": ["id", "name", "website"], "limit": 5},
            )
            hit = next((h for h in fhits if h["name"] == f["name"]), fhits[0] if fhits else None)
            vals: dict = {
                "name": f["name"],
                "parent_id": company_id,
                "is_company": False,
                "x_startup_name": slug,
                "function": f.get("function", "Founder"),
            }
            if f.get("linkedin") and (not hit or not hit.get("website")):
                vals["website"] = f["linkedin"]
            if not hit:
                vals["active"] = not draft
            if hit:
                pid = hit["id"]
                write = {k: v for k, v in vals.items() if k != "name"}
                if write:
                    self.kw("res.partner", "write", [[pid], write])
            else:
                pid = self.kw("res.partner", "name_create", [f["name"]])[0]
                self.kw("res.partner", "write", [[pid], vals])
            founder_ids.append(pid)

        status = "existing" if hits else "new"
        return {"company_id": company_id, "founder_ids": founder_ids, "status": status}


def merge_wiki_draft(existing: str, spec: dict, founder: str) -> str:
    """Fill blank / PENDIENTE fields in an existing draft; leave other content intact."""
    md = existing
    if "[PENDIENTE]" in md and spec.get("taxonomy") and spec["taxonomy"] != "[PENDIENTE]":
        md = re.sub(
            r"(\| CT Taxonomy \| )\[PENDIENTE\]",
            rf"\1{spec['taxonomy']}",
            md,
            count=1,
        )
    site = spec.get("website") or "[PENDIENTE]"
    if "| Website | [PENDIENTE]" in md and site != "[PENDIENTE]":
        md = re.sub(r"(\| Website \| )\[PENDIENTE\]", rf"\1{site}", md, count=1)
    if not re.search(r"\*\*Founder:\*\*", md):
        md = inject_founder_meta(md, founder)
    elif "**Founder:** [PENDIENTE]" in md and founder != "[PENDIENTE]":
        md = re.sub(r"\*\*Founder:\*\*\s*\[PENDIENTE\]", f"**Founder:** {founder}", md, count=1)
    return md


def write_wiki_draft(spec: dict, founder: str) -> tuple[str, str, str]:
    """Write HITL wiki markdown under ops/wiki-drafts/. Returns status, rel path, draft."""
    WIKI_DRAFTS.mkdir(parents=True, exist_ok=True)
    path = WIKI_DRAFTS / f"{spec['slug']}.md"
    rel = f"ops/wiki-drafts/{spec['slug']}.md"
    md_new = portfolio_markdown(spec, founder)
    if path.exists():
        merged = merge_wiki_draft(path.read_text(), spec, founder)
        if merged != path.read_text():
            path.write_text(merged)
            return "existing", rel, "updated"
        return "existing", rel, "unchanged"
    path.write_text(md_new)
    return "new", rel, "draft"


def merge_portfolio_entry(line: str, spec: dict) -> str:
    """Fill blank w / ct / slug on an existing S[] object line."""
    if "slug:" in line and spec["slug"] not in line:
        if re.search(r"slug:\s*['\"]", line):
            pass
        else:
            line = line.rstrip().rstrip("}") + f',slug:"{spec["slug"]}"' + "}"
    if spec.get("website_host") and re.search(r'\bw:null\b|\bw:""\b', line):
        line = re.sub(r'\bw:null\b', f'w:"{spec["website_host"]}"', line)
        line = re.sub(r'\bw:""\b', f'w:"{spec["website_host"]}"', line)
    if spec.get("ct1") and "ct1:" not in line:
        line = line.rstrip().rstrip("}") + f',ct1:"{spec["ct1"]}"' + "}"
        if spec.get("ct2"):
            line = re.sub(r"\}$", f',ct2:"{spec["ct2"]}"' + "}", line)
    if 'slug:"' not in line and "slug:" not in line:
        line = line.rstrip().rstrip("}") + f',slug:"{spec["slug"]}"' + "}"
    line = line.replace("},,slug:", ",slug:")
    return line


def cmd_cards() -> int:
    html_text = PORTFOLIO_HTML.read_text()
    report = []
    for slug in ALL_SLUGS:
        spec = load_json_spec(slug)
        targets = {
            norm_name(spec["display_name"]),
            norm_name(spec["display_name"].replace("&", "and")),
        }
        if slug == "kelab":
            targets.add("R R KELAB")
        if slug == "purest-fuels":
            targets.add("PUREST FUELS")
            targets.add("POWER HHO SUROCCIDENTE SAS")
        if slug == "nuevas-tecnologias-fisicoquimicas":
            targets.add("NUEVAS TECNOLOGIAS FISICOQUIMICAS")
        found = False
        lines = html_text.splitlines()
        for i, line in enumerate(lines):
            m = re.search(r'\{n:"([^"]+)"', line)
            if not m:
                continue
            if norm_name(m.group(1)) not in targets and not any(
                t in norm_name(m.group(1)) for t in targets
            ):
                continue
            new_line = merge_portfolio_entry(line, spec)
            if new_line != line:
                lines[i] = new_line
            found = True
            report.append({"slug": slug, "card": "updated", "matched": m.group(1)})
            break
        if not found:
            host = spec.get("website_host")
            w = f'"{host}"' if host else "null"
            ct = ""
            if spec.get("ct1"):
                ct = f',ct1:"{spec["ct1"]}"'
                if spec.get("ct2"):
                    ct += f',ct2:"{spec["ct2"]}"'
            d = spec["description_en"].replace('"', '\\"')
            ds = spec["description_es"].replace('"', '\\"')
            entry = (
                f'{{n:"{spec["display_name"].upper()}",p:"{spec["program_card"]}",'
                f'c:"{spec["country_code"]}",w:{w},t:"{spec["theme"]}",'
                f'st:"{spec["stage"]}",slug:"{slug}",d:"{d}",ds:"{ds}"{ct}}},'
            )
            for i, line in enumerate(lines):
                if line.strip() == "];" and "const S=[" in "\n".join(lines[max(0, i - 400) : i]):
                    lines.insert(i, entry)
                    found = True
                    report.append({"slug": slug, "card": "inserted", "matched": None})
                    break
        html_text = "\n".join(lines)
    PORTFOLIO_HTML.write_text(html_text)
    print(json.dumps(report, indent=2))
    return 0


def probe_odoo() -> tuple[Odoo | None, str | None]:
    env = load_env(ODOO_ENV)
    url = env.get("ODOO_URL") or env.get("ODOO_BASE_URL", "")
    if not url:
        return None, "Odoo env missing ODOO_URL"
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        common.version()
    except Exception as e:
        return None, f"Odoo unavailable ({url}): {e}"
    try:
        return Odoo(), None
    except Exception as e:
        return None, f"Odoo auth failed: {e}"


def cmd_sync() -> int:
    report: dict = {
        "date": date.today().isoformat(),
        "branch": "feat/cards-batch-10-12",
        "startups": [],
        "blockers": [],
        "wiki_delivery": "ops/wiki-drafts/<slug>.md (local HITL; BookStack API not used)",
    }
    odoo, odoo_err = probe_odoo()
    if odoo_err:
        report["blockers"].append(odoo_err)

    for slug in ALL_SLUGS:
        spec = load_json_spec(slug)
        row = {
            "slug": slug,
            "odoo_company_id": None,
            "odoo_status": "skipped",
            "wiki_url": None,
            "wiki_status": None,
            "card_status": "pending cards cmd",
            "pendiente": [],
        }
        if spec["stage"] == "[PENDIENTE]":
            row["pendiente"].append("stage")
        if spec["taxonomy"] == "[PENDIENTE]" or "pending" in spec["taxonomy"].lower():
            row["pendiente"].append("ct_taxonomy")
        if not spec.get("website_host"):
            row["pendiente"].append("website")
        for f in spec["founders"]:
            if not f.get("linkedin"):
                row["pendiente"].append(f"linkedin:{f.get('name','')}")

        if odoo:
            try:
                ores = odoo.upsert_startup(spec, draft=True)
                row["odoo_company_id"] = ores["company_id"]
                row["odoo_status"] = ores["status"]
            except Exception as e:
                row["odoo_status"] = f"error: {e}"
                report["blockers"].append(f"Odoo {slug}: {e}")

        try:
            wstat, rel_path, pub = write_wiki_draft(spec, spec["founder_line"])
            row["wiki_url"] = rel_path
            row["wiki_status"] = f"{wstat}/{pub}"
        except Exception as e:
            row["wiki_status"] = f"error: {e}"
            report["blockers"].append(f"Wiki draft {slug}: {e}")

        report["startups"].append(row)

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    out = ARCHIVE / "pipeline-audit.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "sync":
        return cmd_sync()
    if cmd == "cards":
        return cmd_cards()
    if cmd == "all":
        rc = cmd_sync()
        if rc:
            return rc
        return cmd_cards()
    print(f"Unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
