"""Per-country actor counts for ecosystem map/card filters."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTORS = ROOT / "static" / "ecosystem" / "data" / "actors.json"
CARDS = ROOT / "static" / "ecosystem" / "data" / "actor_cards.json"

COUNTRY_META = {
    "PE": "Peru",
    "SV": "El Salvador",
    "CO": "Colombia",
}

ID_PREFIX_COUNTRY = {
    "pe": "PE",
    "sv": "SV",
    "co": "CO",
}

# Matches default category chips in static/ecosystem/ecosystem.mjs
CATEGORY_KEYS = {
    "government",
    "accelerator",
    "international",
    "funder",
    "ngo_foundation",
    "academia",
    "corporate",
    "finance",
    "chamber",
    "startup",
    "media",
    "hub",
    "mentor",
    "program",
}


def _country_code_from_name(name: str | None) -> str | None:
    if not name:
        return None
    norm = name.strip().casefold()
    for code, label in COUNTRY_META.items():
        if label.casefold() == norm:
            return code
    return None


def actor_country_code(actor: dict) -> str | None:
    from_field = _country_code_from_name(actor.get("country"))
    if from_field:
        return from_field
    prefix = str(actor.get("id", "")).split("-")[0].lower()
    return ID_PREFIX_COUNTRY.get(prefix)


def _eligible(actor: dict) -> bool:
    return actor.get("category") in CATEGORY_KEYS


def test_public_actors_country_matches_id_prefix():
    actors = json.loads(ACTORS.read_text(encoding="utf-8"))
    for actor in actors:
        prefix = actor["id"].split("-")[0]
        if prefix not in ID_PREFIX_COUNTRY:
            continue
        assert actor_country_code(actor) == ID_PREFIX_COUNTRY[prefix]
        assert actor.get("country") == COUNTRY_META[ID_PREFIX_COUNTRY[prefix]]


def test_card_grid_country_counts_partition_eligible_actors():
    actors = json.loads(ACTORS.read_text(encoding="utf-8"))
    eligible = [a for a in actors if _eligible(a)]
    by_country = Counter(actor_country_code(a) for a in eligible)
    assert None not in by_country
    assert set(by_country) <= set(COUNTRY_META)
    assert sum(by_country.values()) == len(eligible)
    # Snapshot counts — update if data intentionally changes
    assert by_country["CO"] == 8
    assert by_country["SV"] == 77
    assert by_country["PE"] == 286


def test_actor_cards_json_country_counts():
    bundle = json.loads(CARDS.read_text(encoding="utf-8"))
    cards = bundle["cards"]
    by_name = Counter(c.get("country") for c in cards)
    assert by_name["Colombia"] == 8
    assert by_name["El Salvador"] == 77
    assert by_name["Peru"] == 281
    assert sum(by_name.values()) == len(cards)
