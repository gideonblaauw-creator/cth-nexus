from __future__ import annotations

import importlib
import sqlite3
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def test_db_dir(tmp_path, monkeypatch):
    """Create temp DB directory and point config at it."""
    monkeypatch.setenv("DB_DIR", str(tmp_path))
    monkeypatch.setenv("DATA_PLATFORM_ENV", "test")
    monkeypatch.setenv("CPI_LICENCE_ACTIVE", "false")
    monkeypatch.setenv("ALLOWED_INTERNAL_IPS", '["127.0.0.1","::1","testclient"]')

    import app.config
    importlib.reload(app.config)
    app.config.settings = app.config.Settings()

    import app.database
    importlib.reload(app.database)

    import app.middleware.auth
    importlib.reload(app.middleware.auth)
    import app.middleware.fpic_guard
    importlib.reload(app.middleware.fpic_guard)
    import app.middleware.provenance
    importlib.reload(app.middleware.provenance)

    import app.routes.startups
    importlib.reload(app.routes.startups)
    import app.routes.taxonomy
    importlib.reload(app.routes.taxonomy)
    import app.routes.policy
    importlib.reload(app.routes.policy)
    import app.routes.api_keys
    importlib.reload(app.routes.api_keys)
    import app.routes.health
    importlib.reload(app.routes.health)
    import app.routes.catalogue
    importlib.reload(app.routes.catalogue)

    import app.main
    importlib.reload(app.main)

    return tmp_path


@pytest.fixture
def client(test_db_dir):
    """TestClient with fresh DBs, taxonomy, and startup seed data."""
    from app.database import init_all_dbs
    from app.main import app

    init_all_dbs()
    _seed_data(test_db_dir)

    return TestClient(app)


def _seed_data(db_dir: Path) -> None:
    origo = sqlite3.connect(str(db_dir / "origo.db"))
    origo.execute("PRAGMA foreign_keys=OFF")

    origo.executemany(
        """INSERT INTO taxonomy_nodes
           (id, sector, seq, label_short, label_full, description, latam_relevance)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            ("CT-EN-001", "EN", 1, "Solar PV", "Solar Photovoltaic", "Solar energy generation", "high"),
            ("CT-EN-002", "EN", 2, "Wind", "Wind Energy", "Wind power generation", "high"),
            ("CT-WA-001", "WA", 1, "Water Treatment", "Water Treatment Tech", "Water purification", "medium"),
        ],
    )

    origo.executemany(
        """INSERT INTO startups
           (id, nexus_id, name, country, program, stage,
            ct_primary_node, mapping_confidence, nexus_theme, fpic_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (str(uuid.uuid4()), "solarcorp", "SolarCorp", "CO", "CLAC23", "Seed",
             "CT-EN-001", "high", "Energy", "not_required"),
            (str(uuid.uuid4()), "windtech", "WindTech", "MX", "CLP25", "Pre-Seed",
             "CT-EN-002", "medium", "Energy", "approved"),
            (str(uuid.uuid4()), "aquapure", "AquaPure", "CO", "CLAC22", "Seed",
             "CT-WA-001", "high", "Water", "not_required"),
            ("withdrawn-id", "withdrawn-startup", "WithdrawnCo", "CO", "CLAC23", "Seed",
             "CT-EN-001", "high", "Energy", "withdrawn"),
            ("pending-id", "pending-startup", "PendingCo", "CO", "CLAC23", "Seed",
             "CT-EN-001", "high", "Energy", "pending"),
        ],
    )

    origo.commit()
    origo.close()
