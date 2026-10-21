"""El Salvador map pins: no stacked city guesses; address + country badge policy."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTORS = ROOT / "static" / "ecosystem" / "data" / "actors.json"

SAN_SALVADOR_CITY = (13.6976, -89.1912)
MAX_ACTORS_PER_CITY_COORD = 3


def _sv_actors() -> list[dict]:
    actors = json.loads(ACTORS.read_text(encoding="utf-8"))
    return [a for a in actors if a["id"].startswith("sv-")]


def _round_coord(lat: float, lng: float) -> tuple[float, float]:
    return (round(lat, 4), round(lng, 4))


def test_sv_actor_count_unchanged():
    sv = _sv_actors()
    assert len(sv) == 77


def test_sv_precision_address_and_country_badge():
    sv = _sv_actors()
    prec = Counter((a.get("geo") or {}).get("precision") for a in sv)
    assert prec.get("city", 0) == 0
    assert 14 <= prec.get("address", 0) <= 18
    assert 59 <= prec.get("country", 0) <= 63
    assert sum(prec.values()) == 77


def test_sv_city_precision_coordinate_cap():
    sv = _sv_actors()
    by_coord: Counter[tuple[float, float, str]] = Counter()
    for a in sv:
        g = a.get("geo") or {}
        if g.get("precision") != "city" or g.get("lat") is None:
            continue
        key = (*_round_coord(g["lat"], g["lng"]), "city")
        by_coord[key] += 1
    for coord, count in by_coord.items():
        assert count <= MAX_ACTORS_PER_CITY_COORD, f"{count} sv actors at {coord}"
    assert by_coord.get((*SAN_SALVADOR_CITY, "city"), 0) <= MAX_ACTORS_PER_CITY_COORD


def test_no_sv_actor_city_guess_source():
    sv = _sv_actors()
    for a in sv:
        src = ((a.get("geo") or {}).get("source_url") or "").lower()
        assert "actor-city" not in src, a["id"]
