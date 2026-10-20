from __future__ import annotations

import httpx
import pytest

BASE = "http://localhost:8011"

TEST_POLYGON = {
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [-75.8, 4.8], [-75.7, 4.8], [-75.7, 4.9],
            [-75.8, 4.9], [-75.8, 4.8],
        ]],
    },
    "commodity": "coffee",
    "source_country": "CO",
}


# ── TRACK A: Risk Screener ───────────────────────────────────────────────────────

def test_risk_screen_returns_valid_response():
    r = httpx.post(f"{BASE}/public/eudr/risk-screen", json=TEST_POLYGON, timeout=45.0)
    assert r.status_code == 200
    body = r.json()
    assert "deforestation_flag" in body
    assert "agroforestry_risk" in body
    assert body["agroforestry_risk"] in ("low", "medium", "high", "unknown")
    assert body["jrc_mapping_status"] in ("mapped", "no_jrc_match", "disputed")


def test_risk_screen_invalid_geometry():
    bad = {"geometry": {"type": "LineString", "coordinates": []}}
    r = httpx.post(f"{BASE}/public/eudr/risk-screen", json=bad)
    assert r.status_code == 400


# ── TRACK B: Taxonomy ────────────────────────────────────────────────────────────

def test_commodities_list():
    r = httpx.get(f"{BASE}/public/eudr/commodities")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert body["count"] > 0
    names = [c["name"].lower() for c in body["data"]]
    assert any("coffee" in n for n in names), f"coffee not found in {names}"


def test_commodity_hs_codes():
    r = httpx.get(f"{BASE}/public/eudr/commodities/coffee/hs-codes")
    assert r.status_code == 200
    body = r.json()
    assert "hs_codes" in body
    assert len(body["hs_codes"]) > 0


def test_commodity_not_found():
    r = httpx.get(f"{BASE}/public/eudr/commodities/NONEXISTENT_XYZ/hs-codes")
    assert r.status_code == 404


def test_countries_list():
    r = httpx.get(f"{BASE}/public/eudr/countries")
    assert r.status_code == 200
    body = r.json()
    isos = [c["iso"] for c in body["data"]]
    assert "CO" in isos
