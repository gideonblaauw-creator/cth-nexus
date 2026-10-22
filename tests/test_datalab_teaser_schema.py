"""Validate Datalab teaser JSON against ops/datalab/teaser.schema.json (Move 1 draft)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "ops" / "datalab" / "teaser.schema.json"
VALID_FIXTURE = ROOT / "ops" / "datalab" / "fixtures" / "teaser-fenoge-ipse.valid.json"
INVALID_FIXTURE = ROOT / "ops" / "datalab" / "fixtures" / "teaser-too-many-matches.invalid.json"
CELSIA_TEASER = ROOT / "docs" / "teasers" / "celsia" / "celsia-teaser.json"
WAVE1_TEASERS_16_20 = [
    ROOT / "docs" / "teasers" / "juan-valdez" / "juan-valdez-teaser.json",
    ROOT / "docs" / "teasers" / "alpina" / "alpina-teaser.json",
    ROOT / "docs" / "teasers" / "argos" / "argos-teaser.json",
    ROOT / "docs" / "teasers" / "pavimentos-colombia" / "pavimentos-colombia-teaser.json",
    ROOT / "docs" / "teasers" / "interaseo" / "interaseo-teaser.json",
]

FENOGE_FAQ = "https://fenoge.gov.co/preguntas-frecuentes/"
FENOGE_IPSE_QUOTE = (
    "¿Cuáles son los mecanismos para presentar las propuestas al FENOGE? "
    "1. De forma directa: Ante el IPSE o la UPME, según corresponda para planes, "
    "programas o proyectos de personas jurídicas."
)


@pytest.fixture(scope="module")
def teaser_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate(instance: dict, schema: dict) -> None:
    jsonschema.validate(instance=instance, schema=schema)


def test_schema_file_exists():
    assert SCHEMA_PATH.is_file()


def test_valid_fixture_passes_schema(teaser_schema: dict):
    doc = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
    _validate(doc, teaser_schema)


def test_valid_fixture_uses_fenoge_ipse_quote():
    doc = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
    assert doc["company"]["name"] == ""
    match = doc["gaps"][0]["matches"][0]
    assert match["public_source_url"] == FENOGE_FAQ
    assert match["public_quote"] == FENOGE_IPSE_QUOTE
    assert doc["gaps"][0]["evidence_quote"] == FENOGE_IPSE_QUOTE


def test_invalid_fixture_fails_schema(teaser_schema: dict):
    doc = json.loads(INVALID_FIXTURE.read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        _validate(doc, teaser_schema)


def test_schema_rejects_match_without_public_source_url(teaser_schema: dict):
    doc = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
    broken = copy.deepcopy(doc)
    del broken["gaps"][0]["matches"][0]["public_source_url"]
    with pytest.raises(jsonschema.ValidationError):
        _validate(broken, teaser_schema)


def test_schema_rejects_match_without_public_quote(teaser_schema: dict):
    doc = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
    broken = copy.deepcopy(doc)
    del broken["gaps"][0]["matches"][0]["public_quote"]
    with pytest.raises(jsonschema.ValidationError):
        _validate(broken, teaser_schema)


def test_schema_rejects_gap_with_more_than_five_matches(teaser_schema: dict):
    doc = json.loads(INVALID_FIXTURE.read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        _validate(doc, teaser_schema)


@pytest.mark.skipif(
    not CELSIA_TEASER.is_file(),
    reason=(
        "docs/teasers/celsia/celsia-teaser.json not on main yet "
        "(expected from PR #109 when merged)"
    ),
)
def test_celsia_wave1_teaser_passes_schema(teaser_schema: dict):
    doc = json.loads(CELSIA_TEASER.read_text(encoding="utf-8"))
    _validate(doc, teaser_schema)


@pytest.mark.parametrize(
    "teaser_path",
    WAVE1_TEASERS_16_20,
    ids=[p.parent.name for p in WAVE1_TEASERS_16_20],
)
def test_wave1_teasers_16_20_pass_schema(teaser_path: Path, teaser_schema: dict):
    assert teaser_path.is_file(), f"missing teaser JSON: {teaser_path}"
    doc = json.loads(teaser_path.read_text(encoding="utf-8"))
    _validate(doc, teaser_schema)
