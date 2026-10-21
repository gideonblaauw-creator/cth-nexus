#!/usr/bin/env python3
"""Build ecosystem actor CARD data from enriched wiki drafts (grid JSON, not /s/ pages)."""
from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
WIKI = REPO / "docs" / "wiki" / "ecosystem-actors"
AUDIT = WIKI / "audit.csv"
ACTOR_CARDS = REPO / "static" / "ecosystem" / "data" / "actor_cards.json"
ACTORS_RAW = REPO / "static" / "ecosystem" / "data" / "actors.raw.json"
SITES_OUT = REPO / "onepagers" / "sites"
ONEPAGER_DATA = REPO / "onepagers" / "data"
ECO_ONEPAGER_DATA = ONEPAGER_DATA / "ecosystem-actors"
SUMMARY_PATH = WIKI / "nexus-cards-build-summary.json"

PENDIENTE = "PENDIENTE"
NEXUS_BASE = "https://nexus.cleantechhub.net"

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

COUNTRY_CODE = {
    "Peru": "PE",
    "El Salvador": "SV",
    "Colombia": "CO",
    "Guatemala": "GT",
    "Costa Rica": "CR",
}


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


def load_startup_index() -> dict:
    by_host: dict[str, str] = {}
    by_name: dict[str, str] = {}
    slugs: set[str] = set()
    json_paths: list[Path] = []
    if ONEPAGER_DATA.is_dir():
        json_paths.extend(ONEPAGER_DATA.glob("*.json"))
        json_paths.extend(ONEPAGER_DATA.glob("clp26-slices/*.json"))
        json_paths.extend(ONEPAGER_DATA.glob("slices/*.json"))
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
        if hk:
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
    founding = table.get("Año de fundación")

    def clean_field(v: str | None) -> str | None:
        if is_pendiente(v):
            return None
        return scrub_text(v)

    return ActorRecord(
        actor_id=actor_id,
        name=clean_field(name) or actor_id,
        country=clean_field(table.get("País")) or fm.get("tag_country") or "",
        category=clean_field(table.get("Categoría")) or "org",
        city=clean_field(table.get("Ciudad")),
        website=clean_field(table.get("Sitio web")),
        linkedin=clean_field(table.get("LinkedIn")),
        ecosystem_role=clean_field(table.get("Rol en el ecosistema")),
        founding_year=clean_field(founding) if founding and str(founding).isdigit() else clean_field(founding),
        description=desc,
        is_startup=is_startup,
        draft_path=path,
    )


def ecosystem_card_link(actor_id: str) -> str:
    url = f"{NEXUS_BASE}/ecosystem/?actor={actor_id}"
    return f"[Ecosystem card — {url.replace('https://', '')}]({url})"


def nexus_startup_link(slug: str) -> str:
    url = f"{NEXUS_BASE}/s/{slug}"
    return f"[{url.replace('https://', '')}]({url})"


def patch_wiki_nexus_line(path: Path, link_md: str) -> bool:
    text = path.read_text(encoding="utf-8")
    new_line = f"| Tarjeta Nexus | {link_md} |"
    updated, n = re.subn(r"\| Tarjeta Nexus \| [^\n]+ \|", new_line, text, count=1)
    if n and updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def card_record(rec: ActorRecord, startup_slug: str | None) -> dict:
    short_desc = rec.description
    if short_desc and len(short_desc) > 320:
        short_desc = short_desc[:317].rstrip() + "…"
    out: dict = {
        "id": rec.actor_id,
        "name": rec.name,
        "country": rec.country,
        "category": rec.category,
    }
    for key, val in (
        ("city", rec.city),
        ("website", rec.website),
        ("linkedin", rec.linkedin),
        ("ecosystem_role", rec.ecosystem_role),
        ("description", short_desc),
        ("founding_year", rec.founding_year),
    ):
        if val:
            out[key] = val
    if startup_slug:
        out["nexus_startup_slug"] = startup_slug
    return out


def merge_into_actors_raw(cards: list[dict]) -> tuple[int, int]:
    raw: list[dict] = []
    if ACTORS_RAW.is_file():
        raw = json.loads(ACTORS_RAW.read_text(encoding="utf-8"))
    by_id = {a["id"]: a for a in raw}
    updated = 0
    added = 0
    for c in cards:
        aid = c["id"]
        startup = c.get("nexus_startup_slug")
        nexus = {"card_slug": startup} if startup else {"card_slug": None}
        card_block = {
            k: c[k]
            for k in ("ecosystem_role", "description", "founding_year")
            if k in c
        }
        if aid in by_id:
            a = by_id[aid]
            for k in ("name", "country", "city", "website", "linkedin", "category"):
                if c.get(k):
                    a[k] = c[k]
            a["nexus"] = nexus
            if card_block:
                a["card"] = card_block
            updated += 1
        else:
            by_id[aid] = {
                "id": aid,
                "name": c["name"],
                "type": "org",
                "category": c.get("category") or "org",
                "country": c.get("country") or "",
                "city": c.get("city"),
                "website": c.get("website"),
                "linkedin": c.get("linkedin"),
                "nexus": nexus,
                "card": card_block or None,
                "source": "ecosystem-actor-wiki",
            }
            added += 1
    merged = list(by_id.values())
    ACTORS_RAW.write_text(json.dumps(merged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return updated, added


def remove_ecosystem_onepager_artifacts(actor_ids: set[str], startup_slugs: set[str]) -> int:
    removed = 0
    for aid in actor_ids:
        if aid in startup_slugs:
            continue
        site = SITES_OUT / aid
        if site.is_dir():
            import shutil

            shutil.rmtree(site)
            removed += 1
        json_path = ECO_ONEPAGER_DATA / f"{aid}.json"
        if json_path.is_file():
            json_path.unlink()
    if ECO_ONEPAGER_DATA.is_dir() and not any(ECO_ONEPAGER_DATA.iterdir()):
        ECO_ONEPAGER_DATA.rmdir()
    return removed


def update_audit(card_ids: set[str]) -> None:
    if not AUDIT.is_file():
        return
    rows = list(csv.DictReader(AUDIT.open(encoding="utf-8")))
    fieldnames = list(rows[0].keys()) if rows else []
    for row in rows:
        if row.get("actor_id") in card_ids:
            row["enrich_nexus"] = "FILLED"
    with AUDIT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    idx = load_startup_index()
    md_files = sorted(p for p in WIKI.glob("*/*.md") if not p.name.startswith("TEMPLATE"))
    cards: list[dict] = []
    startup_links: list[dict] = []
    errors: list[str] = []
    all_ids: set[str] = set()

    for path in md_files:
        rec = load_actor_from_md(path)
        if not rec:
            errors.append(str(path))
            continue
        all_ids.add(rec.actor_id)
        startup_slug = match_startup_slug(rec.actor_id, rec.name, rec.website, idx)
        if (
            startup_slug
            and startup_slug in idx["slugs"]
            and startup_slug != rec.actor_id.lower()
        ):
            startup_links.append({"actor_id": rec.actor_id, "startup_slug": startup_slug})
            patch_wiki_nexus_line(rec.draft_path, nexus_startup_link(startup_slug))
            cards.append(card_record(rec, startup_slug))
        else:
            patch_wiki_nexus_line(rec.draft_path, ecosystem_card_link(rec.actor_id))
            cards.append(card_record(rec, None))

    cards.sort(key=lambda c: c["id"])
    ACTOR_CARDS.write_text(
        json.dumps(
            {
                "version": 1,
                "source": "docs/wiki/ecosystem-actors",
                "count": len(cards),
                "cards": cards,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )

    updated, added = merge_into_actors_raw(cards)
    removed_sites = remove_ecosystem_onepager_artifacts(all_ids, idx["slugs"])
    update_audit(all_ids)

    summary = {
        "cards_built": len(cards),
        "startup_one_pager_links": len(startup_links),
        "startup_links": startup_links,
        "actors_raw_updated": updated,
        "actors_raw_added": added,
        "onepager_sites_removed": removed_sites,
        "errors": errors,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
