"""T-P0-01: GET /v1/startups never returns rows with fpic_status='withdrawn' or 'pending'.
T-P0-04: Commercial tier with CPI_LICENCE_ACTIVE=false → 403."""

from __future__ import annotations


def test_no_withdrawn_rows_in_list(client):
    """T-P0-01: withdrawn/pending rows never appear."""
    r = client.get("/v1/startups?limit=100")
    assert r.status_code == 200
    data = r.json()["data"]
    for startup in data:
        assert startup["name"] != "WithdrawnCo"
        assert startup["name"] != "PendingCo"


def test_no_withdrawn_rows_by_id(client):
    """T-P0-01: direct ID lookup for withdrawn startup returns 404."""
    r = client.get("/v1/startups/withdrawn-id")
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_no_pending_rows_by_id(client):
    """T-P0-01: direct ID lookup for pending startup returns 404."""
    r = client.get("/v1/startups/pending-id")
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_commercial_blocked_when_cpi_inactive(client):
    """T-P0-04: commercial tier with CPI_LICENCE_ACTIVE=false → 403."""
    from app.database import get_apikeys_db
    from app.middleware.auth import generate_api_key

    raw_key, key_hash = generate_api_key()
    with get_apikeys_db() as conn:
        conn.execute(
            """INSERT INTO api_keys
               (id, key_hash, key_prefix, tier, declared_purpose)
               VALUES (?, ?, ?, 'commercial', 'research')""",
            ("test-commercial-key", key_hash, raw_key[:8]),
        )
        conn.commit()

    r = client.get(
        "/v1/startups",
        headers={"Authorization": f"Bearer {raw_key}"},
    )
    assert r.status_code == 403
    assert r.json()["error"] == "commercial_blocked"
