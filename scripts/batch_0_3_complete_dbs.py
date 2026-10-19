#!/usr/bin/env python3
"""Batches 0–3 — Odoo (skip if down) → wiki file drafts → Nexus portfolio cards (HITL).

Wiki markdown is written to ops/wiki-drafts/<slug>.md only (BookStack API not used).
Reads onepagers/data/{slug}.json, fetching from feat/s-pages-batch-* when missing.

  python3 scripts/batch_0_3_complete_dbs.py fetch
  python3 scripts/batch_0_3_complete_dbs.py sync
  python3 scripts/batch_0_3_complete_dbs.py cards
  python3 scripts/batch_0_3_complete_dbs.py all
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
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "onepagers" / "data"
PORTFOLIO_HTML = ROOT / "pages" / "p" / "startup-portfolio" / "index.html"
ARCHIVE = ROOT / "Archive" / "s-pages-batch-0-3-20261019"
WIKI_DRAFTS = ROOT / "ops" / "wiki-drafts"
ODOO_ENV_PATHS = (Path("/opt/odoo-mcp/.env"), Path("/opt/cth-nexus/.env"))

OWNER, REPO = "gideonblaauw-creator", "cth-nexus"

BATCH_0 = ["b-kapz", "elastic-energy", "mubon", "novatio", "plasticos-ambientales"]
BATCH_1 = ["ainwater", "air4u", "suncolombia", "weia", "zhana-solutions"]
BATCH_2 = ["alfe-aseo-sas", "baruk-company", "bioarea", "calojabones"]
BATCH_3 = ["ciclorganicos", "cobox-logistic", "greenify", "habitat-a-vibe-company"]

ALL_SLUGS = BATCH_0 + BATCH_1 + BATCH_2 + BATCH_3

SLUG_REF: dict[str, str] = {
    **{s: "feat/s-pages-batch-0" for s in BATCH_0},
    **{s: "feat/s-pages-batch-1" for s in BATCH_1},
    **{s: "feat/s-pages-batch-2" for s in BATCH_2},
    **{s: "feat/s-pages-batch-3-ff1c" for s in BATCH_3},
}

SOURCE_SHAS = {
    "feat/s-pages-batch-0": "2e305a90d355636e039e426e292848d27721f33c",
    "feat/s-pages-batch-1": "758e6c329fe12f427bc2992e1e470fca4e95fa76",
    "feat/s-pages-batch-2": "5fdd21137610f83a8acdde99bded41048856aefb",
    "feat/s-pages-batch-3-ff1c": "80ca55c6ec854dbbd7b24ed6549acb73ab08a82e",
}

# Portfolio index.html `n:` labels (exact norm match); overrides fuzzy JSON titles.
CARD_LINE_NAMES: dict[str, str] = {
    "air4u": "AIR 4U",
    "suncolombia": "SUNCOLOMBIA SAS",
    "zhana-solutions": "ZHANA SOLUTIONS",
    "ciclorganicos": "CICLORGÁNICOS (BIO ABONOS GAIA)",
    "plasticos-ambientales": "PLÁSTICOS AMBIENTALES SAS",
    "habitat-a-vibe-company": "HABITAT A VIBE COMPANY SAS",
    "weia": "WEIA",
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


def load_odoo_env() -> dict[str, str]:
    for path in ODOO_ENV_PATHS:
        env = load_env(path)
        if env.get("ODOO_DB") and (env.get("ODOO_URL") or env.get("ODOO_BASE_URL")):
            return env
    return {}


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
    host = u.rstrip("/").split("/")[0] or None
    if host:
        host = host.replace("www.", "")
    return host


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
    if any(x in blob for x in ("bio", "agri", "food", "cacao", "coffee", "agtech")):
        return "BIO"
    if any(
        x in blob
        for x in ("energy", "solar", "wind", "hydrogen", "ev", "mobility", "electric")
    ):
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
    p = d.get("portfolio") or {}
    if p.get("country_code"):
        name = p.get("country_name_en") or p.get("country_name_es") or p["country_code"]
        return str(p["country_code"])[:2].upper(), name
    rib = (d.get("ribbon") or [{}])[0]
    code = (rib.get("val") or "CO").strip()
    if code in ("PENDIENTE", "[P]", "P"):
        code = "CO"
    name = rib.get("sub_en") or rib.get("sub_es") or code
    return code[:2].upper(), name


def program_from_json(d: dict) -> str:
    p = d.get("portfolio") or {}
    raw = (p.get("stat_program") or "").strip()
    if raw:
        return raw.split("·")[0].strip()
    for rib in d.get("ribbon") or []:
        if rib.get("lab_en") == "Stage":
            sub = (rib.get("sub_en") or "").strip()
            if sub.startswith("CLAC") or sub == "CLP":
                return sub
    badge = html.unescape(d.get("badge_en") or "")
    m = re.search(r"\b(CLAC\d+|CLP\d*)\b", badge, re.I)
    if m:
        return m.group(1).upper()
    if re.search(r"Accel", badge, re.I):
        return "Acceleration"
    return "Acceleration"


def team_members(d: dict) -> list[dict]:
    p = d.get("portfolio") or {}
    if p.get("team"):
        return p["team"]
    for sec in d.get("sections") or []:
        if sec.get("type") == "team":
            return sec.get("members") or []
    return []


def taxonomy_text(d: dict) -> str:
    p = d.get("portfolio") or {}
    if p.get("taxonomy_en"):
        return html.unescape(p["taxonomy_en"])
    for sec in d.get("sections") or []:
        if sec.get("type") != "impact":
            continue
        for card in sec.get("cards") or []:
            if "taxonom" in (card.get("title_en") or "").lower():
                return html.unescape(card.get("text_en") or "")
    hero = html.unescape(d.get("hero_sub_en") or "")
    codes = re.findall(r"CT-[A-Z]{2}-\d{3}", hero)
    if codes:
        return ", ".join(codes)
    return ""


def founder_display(members: list[dict]) -> str:
    names = [m.get("name", "").strip() for m in members if m.get("name")]
    return ", ".join(names) if names else "[PENDIENTE]"


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


def fetch_json(slug: str) -> dict:
    ref = SLUG_REF[slug]
    url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{ref}/onepagers/data/{slug}.json"
    with urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode())


def ensure_local_json(slug: str) -> None:
    path = DATA_DIR / f"{slug}.json"
    if path.exists():
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fetch_json(slug), ensure_ascii=False, indent=2) + "\n")


def load_json_spec(slug: str) -> dict:
    ensure_local_json(slug)
    d = json.loads((DATA_DIR / f"{slug}.json").read_text())
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
    program = program_from_json(d)
    return {
        "slug": slug,
        "display_name": display,
        "odoo_company": display,
        "name": display,
        "website": d.get("website") if web else None,
        "website_host": web,
        "country_code": cc,
        "country_name": cname,
        "program": program,
        "program_card": program,
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
        "source_ref": SLUG_REF[slug],
        "source_sha": SOURCE_SHAS[SLUG_REF[slug]],
    }


def card_match_targets(spec: dict) -> set[str]:
    slug = spec["slug"]
    targets = {
        norm_name(spec["display_name"]),
        norm_name(spec["display_name"].replace("&", "and")),
    }
    if slug in CARD_LINE_NAMES:
        targets.add(norm_name(CARD_LINE_NAMES[slug]))
    return targets


class Odoo:
    def __init__(self, env: dict[str, str]) -> None:
        self.url = (env.get("ODOO_URL") or env.get("ODOO_BASE_URL", "")).rstrip("/")
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
        if slug == "suncolombia":
            slug = "suncolombia"
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


def append_before_close(line: str, fragment: str) -> str:
    line = line.rstrip()
    if not line.endswith("}"):
        return line + fragment
    inner = line[:-1].rstrip().rstrip(",")
    return inner + fragment + "}"


def merge_portfolio_entry(line: str, spec: dict) -> str:
    if spec.get("website_host") and re.search(r"\bw:null\b|\bw:\"\"\b", line):
        line = re.sub(r"\bw:null\b", f'w:"{spec["website_host"]}"', line)
        line = re.sub(r'\bw:""\b', f'w:"{spec["website_host"]}"', line)
    if spec.get("ct1") and "ct1:" not in line:
        frag = f',ct1:"{spec["ct1"]}"'
        if spec.get("ct2"):
            frag += f',ct2:"{spec["ct2"]}"'
        line = append_before_close(line, frag)
    if 'slug:"' not in line and "slug:" not in line:
        line = append_before_close(line, f',slug:"{spec["slug"]}"')
    line = line.replace("},,slug:", ",slug:").replace(",,slug:", ",slug:")
    return line


def cmd_fetch() -> int:
    for slug in ALL_SLUGS:
        ensure_local_json(slug)
        print(f"cached {slug}")
    return 0


def cmd_cards() -> int:
    html_text = PORTFOLIO_HTML.read_text()
    report = []
    for slug in ALL_SLUGS:
        spec = load_json_spec(slug)
        targets = card_match_targets(spec)
        found = False
        lines = html_text.splitlines()
        for i, line in enumerate(lines):
            m = re.search(r'\{n:"([^"]+)"', line)
            if not m:
                continue
            if norm_name(m.group(1)) not in targets:
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
            card_name = CARD_LINE_NAMES.get(slug, spec["display_name"].upper())
            d = spec["description_en"].replace('"', '\\"')
            ds = spec["description_es"].replace('"', '\\"')
            entry = (
                f'{{n:"{card_name}",p:"{spec["program_card"]}",'
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
    env = load_odoo_env()
    url = (env.get("ODOO_URL") or env.get("ODOO_BASE_URL") or "").rstrip("/")
    if not url:
        return None, "Odoo env not found (skipped)"
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        common.version()
    except Exception as e:
        return None, f"Odoo unavailable ({url}): {e}"
    try:
        return Odoo(env), None
    except Exception as e:
        return None, f"Odoo auth failed: {e}"


def cmd_sync() -> int:
    report: dict = {
        "date": date.today().isoformat(),
        "branch": "feat/cards-batch-0-3",
        "source_branches": SOURCE_SHAS,
        "startups": [],
        "blockers": [],
        "wiki_delivery": "ops/wiki-drafts/<slug>.md (local HITL; BookStack API not used)",
        "odoo": "skipped — list only when unavailable",
    }
    odoo, odoo_err = probe_odoo()
    if odoo_err:
        report["blockers"].append(odoo_err)
        report["odoo"] = f"skipped: {odoo_err}"

    for slug in ALL_SLUGS:
        spec = load_json_spec(slug)
        row = {
            "slug": slug,
            "source_ref": spec["source_ref"],
            "source_sha": spec["source_sha"],
            "odoo_company_id": None,
            "odoo_status": "skipped (502/unavailable)" if odoo_err else "pending",
            "wiki_path": None,
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
            row["wiki_path"] = rel_path
            row["wiki_status"] = f"{wstat}/{pub}"
        except Exception as e:
            row["wiki_status"] = f"error: {e}"
            report["blockers"].append(f"Wiki draft {slug}: {e}")

        report["startups"].append(row)

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    out = ARCHIVE / "sync-report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "fetch":
        return cmd_fetch()
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
