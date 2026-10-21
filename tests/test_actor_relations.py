"""Vetted actor-to-actor relations for ecosystem cards."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "ecosystem" / "build_actor_relations.py"
REL_JSON = ROOT / "static" / "ecosystem" / "data" / "actor_relations.json"
ACTORS = ROOT / "static" / "ecosystem" / "data" / "actors.json"
CARDS = ROOT / "static" / "ecosystem" / "data" / "actor_cards.json"


def _load_relations() -> list[dict]:
    subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, check=True, capture_output=True)
    bundle = json.loads(REL_JSON.read_text(encoding="utf-8"))
    return bundle["relations"]


def test_actor_relations_reference_valid_ids_and_sources():
    actor_ids = {a["id"] for a in json.loads(ACTORS.read_text(encoding="utf-8"))}
    rels = _load_relations()
    assert rels, "expected at least one vetted relation"
    for r in rels:
        assert r["from_id"] in actor_ids
        assert r["to_id"] in actor_ids
        assert r["from_id"] != r["to_id"]
        url = r.get("source_url") or ""
        assert url.startswith("http"), r
        assert not re.search(r"drive\.google|canva\.com/design", url, re.I)
        assert r.get("source_title")
        assert r.get("date_accessed")


def test_actor_cards_include_descriptions_where_available():
    cards = json.loads(CARDS.read_text(encoding="utf-8"))["cards"]
    with_desc = [c for c in cards if c.get("description")]
    assert len(with_desc) >= 360
    sample = next(c for c in cards if c["id"] == "co-bancoldex")
    assert sample.get("description")
