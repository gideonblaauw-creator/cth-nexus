"""T-P0-08: generate_api_key() raw key never stored in api_keys table.
T-P1-03: Revoked API key → 403."""

from __future__ import annotations

import hashlib

from app.database import get_apikeys_db
from app.middleware.auth import generate_api_key


def test_raw_key_never_stored(client):
    """T-P0-08."""
    raw, stored_hash = generate_api_key()
    assert raw != stored_hash
    assert hashlib.sha256(raw.encode()).hexdigest() == stored_hash
    assert raw.startswith("ctk_")


def test_revoked_key_returns_403(client):
    """T-P1-03."""
    raw_key, key_hash = generate_api_key()
    with get_apikeys_db() as conn:
        conn.execute(
            """INSERT INTO api_keys
               (id, key_hash, key_prefix, tier, declared_purpose, revoked_at)
               VALUES (?, ?, ?, 'research', 'research', datetime('now'))""",
            ("revoked-key", key_hash, raw_key[:8]),
        )
        conn.commit()

    r = client.get(
        "/v1/startups",
        headers={"Authorization": f"Bearer {raw_key}"},
    )
    assert r.status_code == 403
    assert r.json()["error"] == "invalid_api_key"
