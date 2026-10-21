"""Tests for ecosystem actor Nexus card builder."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_ecosystem_actor_cards.py"


def test_build_script_runs_and_summary():
    proc = subprocess.run(
        [sys.executable, str(BUILD)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    summary = json.loads((ROOT / "docs/wiki/ecosystem-actors/nexus-cards-build-summary.json").read_text())
    assert summary["built_count"] >= 350
    assert summary["skipped_startup_duplicate"] == 8
    assert summary["total_card_slugs"] >= summary["built_count"]


def test_sample_card_has_no_pii_and_ecosystem_link():
    sample = ROOT / "onepagers/sites/co-bancoldex/index.html"
    assert sample.is_file()
    html = sample.read_text(encoding="utf-8")
    assert "drive.google.com" not in html.lower()
    assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)
    assert "/ecosystem/?actor=co-bancoldex" in html
    assert "Bancóldex" in html
    assert "PENDIENTE" not in html


def test_actor_json_omits_empty_fields():
    doc = json.loads((ROOT / "onepagers/data/ecosystem-actors/co-bancoldex.json").read_text())
    assert doc["template"] == "ecosystem-actor"
    assert "email" not in doc
    assert doc.get("founding_year") == "1992"
