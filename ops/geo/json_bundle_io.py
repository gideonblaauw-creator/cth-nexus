#!/usr/bin/env python3
"""Canonical JSON serialization for Nexus location bundle files."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# path suffix → (indent, separators, trailing_newline)
_SERIALIZE_RULES: dict[str, tuple[int | None, tuple[str, str] | None, bool]] = {
    "static/ecosystem/data/actors.json": (1, (", ", ": "), True),
    "site/investors/data/investors.json": (None, (", ", ": "), False),
    "site/nexus-assets/previews/startups-redesign-20261016/portfolio-core.json": (
        None,
        (",", ":"),
        False,
    ),
    "site/cth-static/hubs/hubs-data.json": (2, (", ", ": "), True),
    "data/clp26/mentor_cards.json": (2, (", ", ": "), True),
    "data/clp26/jury_cards.json": (2, (", ", ": "), True),
    "app/nexus-ideas/src/data/imd-peru-curated.json": (2, (", ", ": "), False),
    "app/nexus-ideas/src/data/epic-angels-curated.json": (2, (", ", ": "), True),
}


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def format_onepager(obj: dict) -> str:
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    q = r'"(?:[^"\\]|\\.)*"'
    text = re.sub(
        rf"\{{\n\s+\"val\": ({q}),\n\s+\"lab_en\": ({q}),\n\s+\"lab_es\": ({q}),\n\s+\"sub_en\": ({q}),\n\s+\"sub_es\": ({q})\n\s+\}}",
        r'{"val": \1, "lab_en": \2, "lab_es": \3, "sub_en": \4, "sub_es": \5}',
        text,
    )
    return text + "\n"


def write_json(path: Path, data) -> None:
    rel = _rel(path)
    if rel.startswith("onepagers/data/") and rel.endswith(".json"):
        path.write_text(format_onepager(data), encoding="utf-8")
        return

    rule = _SERIALIZE_RULES.get(rel)
    if rule is None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return

    indent, separators, trailing_nl = rule
    if indent is None:
        text = json.dumps(data, ensure_ascii=False, separators=separators)
    else:
        text = json.dumps(data, ensure_ascii=False, indent=indent, separators=separators)
    if trailing_nl:
        text += "\n"
    path.write_text(text, encoding="utf-8")
