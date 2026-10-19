#!/usr/bin/env python3
"""Write ops/wiki-drafts/<slug>.md from onepager JSON (no BookStack API)."""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

MERGE = Path("/home/debian/cth-nexus-merge")
OUT = Path(__file__).resolve().parents[1] / "ops" / "wiki-drafts"

BATCH_SLUGS: list[tuple[str, str]] = [
    ("origin/feat/s-pages-batch-7", "greendex"),
    ("origin/feat/s-pages-batch-7", "hunter-tecnologia"),
    ("origin/feat/s-pages-batch-7", "i-can-jump"),
    ("origin/feat/s-pages-batch-7", "ilikko"),
    ("origin/feat/s-pages-batch-7", "isd-ingenieria-y-servicios"),
    ("origin/feat/s-pages-batch-8", "istmo-verde"),
    ("origin/feat/s-pages-batch-8", "kigui"),
    ("origin/feat/s-pages-batch-8", "kimsa"),
    ("origin/feat/s-pages-batch-8", "kleantab"),
    ("origin/feat/s-pages-batch-8", "linko-workers"),
    ("origin/feat/s-pages-batch-9", "mayugo"),
    ("origin/feat/s-pages-batch-9", "mitsidi"),
    ("origin/feat/s-pages-batch-9", "monte-jazmin"),
    ("origin/feat/s-pages-batch-9", "moviltronics"),
    ("origin/feat/s-pages-batch-9", "myma"),
]

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

SECTOR = {"CE": "Circular Economy", "BIO": "Bioeconomy", "EN": "Energy Transition"}


def strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).replace("\xa0", " ").strip()


def load_page(ref: str, slug: str) -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{ref}:onepagers/data/{slug}.json"],
        cwd=MERGE,
        text=True,
    )
    return json.loads(raw)


def parse(page: dict) -> dict:
    slug = page["slug"]
    website = page.get("website", "")
    country = strip_html(
        next(
            (r.get("sub_en") for r in page.get("ribbon", []) if r.get("lab_en") == "Country"),
            "",
        )
    )
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
    if slug == "istmo-verde" or any(x in badge for x in ("Energy", "Carbon MRV", "Electric")):
        theme = "EN"
    elif any(x in badge for x in ("Bio", "Coffee", "Agr")):
        theme = "BIO"
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
                        "role": strip_html(mem.get("role_en", "")),
                    }
                )
    founders = [m["name"] for m in members if m["name"]]
    pendiente = []
    if ct1 == "[PENDIENTE]":
        pendiente.append("CT taxonomy (primary)")
    if stage == "[PENDIENTE]":
        pendiente.append("Stage")
    for mem in members:
        if not mem.get("linkedin"):
            pendiente.append(f"LinkedIn: {mem['name']}")
    return {
        "slug": slug,
        "name": page["name"],
        "website": website,
        "country": country,
        "cc": COUNTRY_CODE.get(country, ""),
        "stage": stage,
        "program": program,
        "theme": theme,
        "sector": SECTOR[theme],
        "ct1": ct1,
        "ct2": ct2,
        "founder_str": ", ".join(founders) if founders else "[PENDIENTE]",
        "pitch_en": strip_html(page.get("pitch_en", "")),
        "pitch_es": strip_html(page.get("pitch_es", "")),
        "members": members,
        "pendiente": pendiente,
        "source_ref": None,
    }


def render(rec: dict, source_ref: str) -> str:
    ct_line = rec["ct1"]
    if rec["ct2"]:
        ct_line += f", {rec['ct2']}"
    web = f"[{rec['website']}]({rec['website']})" if rec["website"] else "—"
    lines = [
        "<!-- HITL: BookStack Startup Portfolio — do NOT paste until Gideon approves -->",
        "",
        f"# {rec['name']}",
        "",
        f"**Founder:** {rec['founder_str']}",
        "",
        "## Snapshot",
        "| Field | Value |",
        "|-------|-------|",
        f"| Sector | {rec['sector']} |",
        f"| Stage | {rec['stage']} |",
        f"| Country | {rec['country']} |",
        f"| Program | {rec['program']} |",
        f"| Website | {web} |",
        f"| CT Taxonomy | {ct_line} |",
        f"| Nexus /s/ | https://nexus.cleantechhub.net/s/{rec['slug']} |",
        "",
        "## Description (EN)",
        rec["pitch_en"],
        "",
        "## Descripción (ES)",
        rec["pitch_es"],
        "",
        "## Leadership (sourced)",
    ]
    for mem in rec["members"]:
        li = mem["linkedin"] or "[PENDIENTE]"
        if mem["linkedin"]:
            li = f"[LinkedIn]({mem['linkedin']})"
        lines.append(f"- **{mem['name']}** — {mem['role']} — {li}")
    lines.extend(
        [
            "",
            "## Source Notes",
            f"Generated from `{source_ref}` one-pager JSON. No live wiki write.",
            "",
            "## PENDIENTE",
        ]
    )
    if rec["pendiente"]:
        for p in rec["pendiente"]:
            lines.append(f"- {p}")
    else:
        lines.append("- —")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for ref, slug in BATCH_SLUGS:
        page = load_page(ref, slug)
        rec = parse(page)
        rec["source_ref"] = f"{ref}:onepagers/data/{slug}.json"
        path = OUT / f"{slug}.md"
        path.write_text(render(rec, rec["source_ref"]), encoding="utf-8")
        print(f"Wrote {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
