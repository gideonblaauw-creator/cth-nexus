"""T-P0-02: POST /policy/evaluate with missing purpose → 400.
T-P0-03: POST /policy/evaluate with invalid purpose → 400.
T-P0-04: Commercial tier, CPI blocked → 403."""

from __future__ import annotations


def test_missing_purpose_returns_400(client):
    """T-P0-02."""
    r = client.post("/policy/evaluate", json={})
    assert r.status_code == 400
    body = r.json()
    assert body["error"] == "purpose_required"
    assert "valid" in body


def test_invalid_purpose_returns_400(client):
    """T-P0-03."""
    r = client.post("/policy/evaluate", json={"purpose": "evil"})
    assert r.status_code == 400
    body = r.json()
    assert body["error"] == "invalid_purpose"
    assert "valid" in body


def test_valid_purpose_returns_allow(client):
    r = client.post(
        "/policy/evaluate",
        json={"purpose": "research", "resource_type": "startup"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["allow"] is True
    assert body["ttl"] == 3600
    assert body["purpose"] == "research"
    assert "request_id" in body


def test_commercial_blocked_via_policy(client):
    """T-P0-04 via policy endpoint."""
    r = client.post(
        "/policy/evaluate",
        json={"purpose": "eudr", "caller_tier": "commercial"},
    )
    assert r.status_code == 403
    assert r.json()["error"] == "commercial_blocked"


def test_fpic_withdrawn_resource(client):
    r = client.post(
        "/policy/evaluate",
        json={"purpose": "research", "resource_id": "withdrawn-id"},
    )
    assert r.status_code == 403
    assert r.json()["error"] == "fpic_withdrawn"
