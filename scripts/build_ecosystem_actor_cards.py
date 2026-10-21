#!/usr/bin/env python3
"""Build Nexus ecosystem actor cards from enriched wiki drafts (docs/wiki/ecosystem-actors/)."""
from __future__ import annotations

import csv
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
WIKI = REPO / "docs" / "wiki" / "ecosystem-actors"
AUDIT = WIKI / "audit.csv"
DATA_OUT = REPO / "onepagers" / "data" / "ecosystem-actors"
SITES_OUT = REPO / "onepagers" / "sites"
ACTORS_RAW = REPO / "static" / "ecosystem" / "data" / "actors.raw.json"
STARTUP_DATA = REPO / "onepagers" / "data"
BASE_CSS = REPO / "onepagers" / "template" / "styles.css"
SLICE_CSS = REPO / "onepagers" / "template" / "clp26_slice.css"
ACTOR_CSS = REPO / "onepagers" / "template" / "ecosystem_actor.css"
SUMMARY_PATH = WIKI / "nexus-cards-build-summary.json"

PENDIENTE = "PENDIENTE"
NEXUS_BASE = "https://nexus.cleantechhub.net"

CATEGORY_LABEL = {
    "finance": ("Finance", "Finanzas"),
    "international": ("International", "Internacional"),
    "government": ("Government", "Gobierno"),
    "funder": ("Funder", "Financiador"),
    "corporate": ("Corporate", "Empresa"),
    "accelerator": ("Accelerator / incubator", "Aceleradora / incubadora"),
    "academia": ("Academia", "Academia"),
    "ngo_foundation": ("NGO / foundation", "ONG / fundación"),
    "chamber": ("Chamber / association", "Cámara / gremio"),
    "media": ("Media", "Medios"),
    "startup": ("Startup", "Startup"),
    "hub": ("Hub", "Hub"),
    "mentor": ("Mentor", "Mentor"),
    "program": ("Program", "Programa"),
}

SENSITIVE_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"drive\.google\.com", re.I),
    re.compile(r"docs\.google\.com", re.I),
    re.compile(r"canva\.com/design", re.I),
    re.compile(r"\+?\d[\d\s\-()]{7,}\d"),
]

NEXUS_LINK_RE = re.compile(
    r"nexus\.cleantechhub\.net/s/([a-z0-9-]+)|/s/([a-z0-9-]+)",
    re.I,
)

GENERIC_HOSTS = frozenset(
    {"facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com", "linktr.ee"}
)


def bi(en: str, es: str) -> str:
    return f'<span class="en">{html.escape(en)}</span><span class="es">{html.escape(es)}</span>'


def is_pendiente(val: str | None) -> bool:
    if val is None:
        return True
    s = str(val).strip()
    return not s or s.upper() == PENDIENTE or s.startswith("PENDIENTE ")


def scrub_text(val: str | None) -> str | None:
    if val is None:
        return None
    out = str(val)
    for pat in SENSITIVE_PATTERNS:
        if pat.search(out):
            return None
    return out.strip() or None


def norm_domain(url: str | None) -> str | None:
    if not url or is_pendiente(url):
        return None
    u = url if url.startswith("http") else f"https://{url}"
    try:
        h = urlparse(u).netloc.lower().replace("www.", "")
        if not h or h in GENERIC_HOSTS:
            return None
        return h
    except Exception:
        return None


def load_startup_index() -> dict[str, str]:
    by_host: dict[str, str] = {}
    by_name: dict[str, str] = {}
    slugs: set[str] = set()
    json_paths: list[Path] = []
    if STARTUP_DATA.is_dir():
        json_paths.extend(STARTUP_DATA.glob("*.json"))
        json_paths.extend(STARTUP_DATA.glob("clp26-slices/*.json"))
        json_paths.extend(STARTUP_DATA.glob("slices/*.json"))
    for path in json_paths:
        if path.name.startswith("s-pages-"):
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        slug = (doc.get("slug") or path.stem).lower()
        slugs.add(slug)
        raw_name = doc.get("name") or ""
        if isinstance(raw_name, dict):
            raw_name = raw_name.get("value") or raw_name.get("en") or ""
        nm = re.sub(r"[^a-z0-9]+", "", str(raw_name).lower())
        if nm:
            by_name[nm] = slug
        raw_web = doc.get("website")
        if isinstance(raw_web, dict):
            raw_web = raw_web.get("value")
        hk = norm_domain(raw_web if isinstance(raw_web, str) else None)
        if hk and hk not in GENERIC_HOSTS:
            by_host[hk] = slug
    return {"host": by_host, "name": by_name, "slugs": slugs}


def match_startup_slug(actor_id: str, name: str, website: str | None, idx: dict) -> str | None:
    hk = norm_domain(website)
    if hk and hk in idx["host"]:
        return idx["host"][hk]
    nm = re.sub(r"[^a-z0-9]+", "", (name or "").lower())
    if nm and nm in idx["name"]:
        return idx["name"][nm]
    if actor_id.lower() in idx["slugs"]:
        return actor_id.lower()
    # Ecosystem actor id pe-{startup-slug} → existing CLP26 /s/ one-pager
    if "-" in actor_id:
        tail = actor_id.split("-", 1)[1].lower()
        if tail in idx["slugs"]:
            return tail
    return None


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    fm: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, parts[2]


def parse_table(body: str, section: str) -> dict[str, str]:
    m = re.search(
        rf"## {re.escape(section)}\s*\n+\| Field \| Value \|\s*\n\| --- \| --- \|\s*\n(.*?)(?=\n## |\Z)",
        body,
        re.S,
    )
    if not m:
        return {}
    table: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 2:
            table[cells[0]] = cells[1]
    return table


def parse_description(body: str, is_startup: bool) -> str | None:
    heading = "## Descripción" if is_startup else "## Rol y alcance"
    m = re.search(rf"{re.escape(heading)}\s*\n+\n?(.*?)(?=\n## |\Z)", body, re.S)
    if not m:
        return None
    text = m.group(1).strip()
    if is_pendiente(text):
        return None
    return scrub_text(text)


def extract_nexus_slug_from_table(table: dict[str, str]) -> str | None:
    raw = table.get("Tarjeta Nexus", "")
    if is_pendiente(raw):
        return None
    m = NEXUS_LINK_RE.search(raw)
    if m:
        return (m.group(1) or m.group(2)).lower()
    return None


@dataclass
class ActorRecord:
    actor_id: str
    name: str
    country: str
    category: str
    city: str | None = None
    website: str | None = None
    linkedin: str | None = None
    ecosystem_role: str | None = None
    founding_year: str | None = None
    description: str | None = None
    is_startup: bool = False
    draft_path: Path = field(default_factory=Path)
    existing_nexus_slug: str | None = None


def load_actor_from_md(path: Path) -> ActorRecord | None:
    raw = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(raw)
    actor_id = fm.get("actor_id") or path.stem
    is_startup = fm.get("tag_type") == "ecosystem-startup" or "Snapshot" in body[:800]
    section = "Snapshot" if is_startup else "Overview"
    table = parse_table(body, section)
    name_m = re.search(r"^#\s+(.+)$", body, re.M)
    name = (name_m.group(1).strip() if name_m else table.get("name") or actor_id)
    desc = parse_description(body, is_startup)
    website = table.get("Sitio web")
    linkedin = table.get("LinkedIn")
    city = table.get("Ciudad")
    founding = table.get("Año de fundación")
    role = table.get("Rol en el ecosistema")
    category = table.get("Categoría") or "org"

    def clean_field(v: str | None) -> str | None:
        if is_pendiente(v):
            return None
        return scrub_text(v)

    return ActorRecord(
        actor_id=actor_id,
        name=clean_field(name) or actor_id,
        country=clean_field(table.get("País")) or fm.get("tag_country") or "",
        category=clean_field(category) or "org",
        city=clean_field(city),
        website=clean_field(website),
        linkedin=clean_field(linkedin),
        ecosystem_role=clean_field(role),
        founding_year=clean_field(founding) if founding and founding.isdigit() else clean_field(founding),
        description=desc,
        is_startup=is_startup,
        draft_path=path,
        existing_nexus_slug=extract_nexus_slug_from_table(table),
    )


def profile_row(label_en: str, label_es: str, value: str | None, link: bool = False) -> str:
    if not value:
        return ""
    esc = html.escape(value)
    inner = f'<a href="{esc}" target="_blank" rel="noopener">{esc}</a>' if link else esc
    return f"""      <div class="profile-row">
        <div class="profile-label">{bi(label_en, label_es)}</div>
        <div class="profile-value">{inner}</div>
      </div>"""


def build_html(d: dict) -> str:
    slug = d["slug"]
    name = html.escape(d["name"])
    css = BASE_CSS.read_text() + "\n" + SLICE_CSS.read_text() + "\n" + ACTOR_CSS.read_text()
    cat = d.get("category") or "org"
    cat_en, cat_es = CATEGORY_LABEL.get(cat, (cat.replace("_", " ").title(), cat))
    badge_bits = [html.escape(d.get("country") or ""), bi(cat_en, cat_es)]
    badge = " · ".join(x for x in badge_bits if x)

    loc_bits = []
    if d.get("city"):
        loc_bits.append(html.escape(d["city"]))
    if d.get("country"):
        loc_bits.append(html.escape(d["country"]))
    location = ", ".join(loc_bits)

    rows = [
        profile_row("Location", "Ubicación", location or None),
        profile_row("Website", "Sitio web", d.get("website"), link=True),
        profile_row("LinkedIn", "LinkedIn (organization)", d.get("linkedin"), link=True),
        profile_row("Role in the ecosystem", "Rol en el ecosistema", d.get("ecosystem_role")),
        profile_row("Founded", "Año de fundación", d.get("founding_year")),
    ]
    rows = [r for r in rows if r]
    eco_url = f"{NEXUS_BASE}/ecosystem/?actor={html.escape(slug, quote=True)}"
    rows.append(
        f"""      <div class="profile-row profile-row--full">
        <div class="profile-label">{bi("Ecosystem map", "Mapa del ecosistema")}</div>
        <div class="profile-value"><a href="{eco_url}" rel="noopener">{bi("Open in Nexus Ecosystem", "Abrir en Ecosistema Nexus")}</a></div>
      </div>"""
    )

    desc_block = ""
    if d.get("description"):
        desc_block = f"""
<div class="desc-sec">
  <div class="sec-header" style="padding-left:0;padding-right:0;padding-top:24px;">
    <div class="sec-num">◆</div>
    <div class="sec-title">{bi("About", "Acerca de")}</div>
    <div class="sec-rule"></div>
  </div>
  <div class="desc-panel"><div class="desc-text">{html.escape(d["description"])}</div></div>
</div>
<div class="accent-bar"></div>"""

    pitch = html.escape(d.get("description") or d.get("ecosystem_role") or "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — CleantechHUB Ecosystem Actor</title>
<link rel="icon" href="https://cleantechhub.net/favicon.ico">
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&family=PT+Sans:wght@400;700&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div class="site-brand"><span class="brand-text">Cleantech<em>HUB</em></span></div>
<div class="lang-toggle">
  <button class="lb active" onclick="document.documentElement.lang='en';this.classList.add('active');this.nextElementSibling.classList.remove('active');">EN</button>
  <button class="lb" onclick="document.documentElement.lang='es';this.classList.add('active');this.previousElementSibling.classList.remove('active');">ES</button>
</div>

<div class="sec hero hero--slice hero--actor">
  <div class="hero-ov"></div>
  <div class="hero-badge"><div class="pill" style="background:rgba(0,0,0,.45);color:var(--lg);">{badge}</div></div>
  <div class="hero-in">
    <div class="hero-name">{name}</div>
    <div class="hero-pitch">{pitch}</div>
  </div>
  <div class="hero-tagline">Inspira. Actúa. Transforma.</div>
</div>

<div class="profile-sec">
  <div class="profile-panel">
    <div class="profile-grid">
{chr(10).join(rows)}
    </div>
  </div>
</div>
<div class="accent-bar"></div>
{desc_block}
<div class="footer-sec">
  <div class="cta-port">CleantechHUB · Nexus Ecosystem Actor</div>
</div>
</body>
</html>
"""


def nexus_markdown_link(slug: str) -> str:
    url = f"{NEXUS_BASE}/s/{slug}"
    return f"[{url.replace('https://', '')}]({url})"


def patch_wiki_nexus_line(path: Path, link_md: str) -> bool:
    text = path.read_text(encoding="utf-8")
    new_line = f"| Tarjeta Nexus | {link_md} |"
    updated, n = re.subn(
        r"\| Tarjeta Nexus \| [^\n]+ \|",
        new_line,
        text,
        count=1,
    )
    if n == 0:
        return False
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def patch_actors_raw(slug_by_id: dict[str, str]) -> int:
    if not ACTORS_RAW.exists():
        return 0
    actors = json.loads(ACTORS_RAW.read_text(encoding="utf-8"))
    touched = 0
    for a in actors:
        aid = a.get("id")
        if aid not in slug_by_id:
            continue
        nexus = dict(a.get("nexus") or {})
        if nexus.get("card_slug") != slug_by_id[aid]:
            nexus["card_slug"] = slug_by_id[aid]
            a["nexus"] = nexus
            touched += 1
    ACTORS_RAW.write_text(json.dumps(actors, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return touched


def update_audit(slug_by_id: dict[str, str], skipped: set[str]) -> None:
    if not AUDIT.exists():
        return
    rows = list(csv.DictReader(AUDIT.open(encoding="utf-8")))
    fieldnames = rows[0].keys() if rows else []
    for row in rows:
        aid = row.get("actor_id")
        if aid in skipped:
            row["enrich_nexus"] = "FILLED"
        elif aid in slug_by_id:
            row["enrich_nexus"] = "FILLED"
    with AUDIT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    idx = load_startup_index()
    DATA_OUT.mkdir(parents=True, exist_ok=True)

    md_files = sorted(p for p in WIKI.glob("*/*.md") if not p.name.startswith("TEMPLATE"))
    built: list[str] = []
    skipped_startup: list[dict] = []
    skipped_existing_site: list[str] = []
    errors: list[str] = []
    slug_by_id: dict[str, str] = {}

    for path in md_files:
        rec = load_actor_from_md(path)
        if not rec:
            errors.append(str(path))
            continue

        # Only skip when website/name matching finds a startup one-pager — never trust
        # stale Tarjeta Nexus table links (e.g. erroneous planta-comunitaria-wpc aliases).
        startup_slug = match_startup_slug(rec.actor_id, rec.name, rec.website, idx)
        if (
            startup_slug
            and startup_slug in idx["slugs"]
            and startup_slug != rec.actor_id.lower()
        ):
            slug_by_id[rec.actor_id] = startup_slug
            patch_wiki_nexus_line(rec.draft_path, nexus_markdown_link(startup_slug))
            skipped_startup.append(
                {"actor_id": rec.actor_id, "startup_slug": startup_slug, "reason": "existing_s_card"}
            )
            eco_json = DATA_OUT / f"{rec.actor_id}.json"
            eco_site = SITES_OUT / rec.actor_id
            if eco_json.is_file():
                eco_json.unlink()
            if eco_site.is_dir():
                shutil.rmtree(eco_site)
            continue

        payload = {
            "template": "ecosystem-actor",
            "slug": rec.actor_id,
            "actor_id": rec.actor_id,
            "name": rec.name,
            "country": rec.country,
            "city": rec.city,
            "category": rec.category,
            "ecosystem_role": rec.ecosystem_role,
            "website": rec.website,
            "linkedin": rec.linkedin,
            "founding_year": rec.founding_year,
            "description": rec.description,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        json_path = DATA_OUT / f"{rec.actor_id}.json"
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        site_dir = SITES_OUT / rec.actor_id
        site_dir.mkdir(parents=True, exist_ok=True)
        (site_dir / "index.html").write_text(build_html(payload), encoding="utf-8")

        slug_by_id[rec.actor_id] = rec.actor_id
        patch_wiki_nexus_line(rec.draft_path, nexus_markdown_link(rec.actor_id))
        built.append(rec.actor_id)

    skipped_ids = {x["actor_id"] for x in skipped_startup}
    patch_actors_raw(slug_by_id)
    update_audit(slug_by_id, skipped_ids)

    summary = {
        "built_count": len(built),
        "skipped_startup_duplicate": len(skipped_startup),
        "skipped_existing_site": len(skipped_existing_site),
        "total_card_slugs": len(slug_by_id),
        "built_sample": built[:5],
        "skipped_startup": skipped_startup,
        "errors": errors,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
