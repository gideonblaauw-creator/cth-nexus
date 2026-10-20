"""T-P0-05: Every API request generates a provenance_log INSERT.
T-P0-06: UPDATE provenance_log raises ABORT.
T-P0-07: DELETE FROM provenance_log raises ABORT."""

from __future__ import annotations

import sqlite3

from app.database import get_provenance_db


def test_request_creates_provenance_entry(client):
    """T-P0-05."""
    with get_provenance_db() as conn:
        before = conn.execute("SELECT COUNT(*) FROM provenance_log").fetchone()[0]

    client.get("/v1/startups?limit=1")

    with get_provenance_db() as conn:
        after = conn.execute("SELECT COUNT(*) FROM provenance_log").fetchone()[0]

    assert after > before


def test_provenance_update_raises(client):
    """T-P0-06."""
    client.get("/health")

    with get_provenance_db() as conn:
        row = conn.execute("SELECT id FROM provenance_log LIMIT 1").fetchone()
        assert row is not None
        try:
            conn.execute(
                "UPDATE provenance_log SET action = 'tampered' WHERE id = ?",
                (row["id"],),
            )
            assert False, "UPDATE should have raised"
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            assert "append-only" in str(e)


def test_provenance_delete_raises(client):
    """T-P0-07."""
    client.get("/health")

    with get_provenance_db() as conn:
        row = conn.execute("SELECT id FROM provenance_log LIMIT 1").fetchone()
        assert row is not None
        try:
            conn.execute(
                "DELETE FROM provenance_log WHERE id = ?", (row["id"],)
            )
            assert False, "DELETE should have raised"
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            assert "cannot be deleted" in str(e)
