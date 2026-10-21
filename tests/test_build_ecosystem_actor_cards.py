"""Tests for ecosystem actor card JSON builder (grid cards, not /s/ pages)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_ecosystem_actor_cards.py"
PUBLIC = ROOT / "scripts" / "ecosystem" / "build_public_data.py"
CARDS = ROOT / "static" / "ecosystem" / "data" / "actor_cards.json"


def test_build_produces_card_json_not_onepager_sites():
    proc = subprocess.run(
        [sys.executable, str(BUILD)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    bundle = json.loads(CARDS.read_text(encoding="utf-8"))
    assert bundle["count"] >= 360
    assert len(bundle["cards"]) == bundle["count"]
    sample = next(c for c in bundle["cards"] if c["id"] == "co-bancoldex")
    assert sample.get("description")
    assert "ecosystem_role" in sample
    assert "nexus_startup_slug" not in sample
    assert not (ROOT / "onepagers/sites/co-bancoldex/index.html").exists()
    assert not (ROOT / "onepagers/data/ecosystem-actors/co-bancoldex.json").exists()


def test_startup_one_pager_links_only_vigia_yakusmart():
    subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, check=True, capture_output=True)
    cards = {c["id"]: c for c in json.loads(CARDS.read_text())["cards"]}
    assert cards["pe-vigia"].get("nexus_startup_slug") == "vigia"
    assert cards["pe-yakusmart"].get("nexus_startup_slug") == "yakusmart"
    assert "nexus_startup_slug" not in cards["sv-camagro"]
    assert "planta-comunitaria-wpc" not in CARDS.read_text()


def test_public_actors_include_card_block():
    subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, check=True, capture_output=True)
    subprocess.run([sys.executable, str(PUBLIC)], cwd=ROOT, check=True, capture_output=True)
    actors = json.loads((ROOT / "static/ecosystem/data/actors.json").read_text())
    by_id = {a["id"]: a for a in actors}
    b = by_id["co-bancoldex"]
    assert b.get("card", {}).get("description")
    assert b.get("nexus", {}).get("card_slug") is None
    assert by_id["pe-vigia"]["nexus"]["card_slug"] == "vigia"
    raw = json.dumps(actors)
    assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", raw)
    assert "drive.google.com" not in raw.lower()
