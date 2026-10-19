"""Phase 3 migration — adds governance_ledger, territorial_boundaries,
methodology_registry, and submissions tables. Safe to re-run (CREATE IF NOT EXISTS).
"""
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB_DIR = BASE / "db"


def migrate():
    print("Phase 3 migration — applying schema additions...")

    # Provenance DB: governance_ledger
    prov_db = sqlite3.connect(str(DB_DIR / "provenance.db"))
    prov_schema = (BASE / "db" / "schema_provenance.sql").read_text()
    prov_db.executescript(prov_schema)
    prov_db.close()
    print("  provenance.db: governance_ledger + triggers applied")

    # Origo DB: territorial_boundaries + methodology_registry + submissions
    origo_db = sqlite3.connect(str(DB_DIR / "origo.db"))
    origo_schema = (BASE / "db" / "schema_origo.sql").read_text()
    origo_db.executescript(origo_schema)

    # Seed methodology registry
    origo_db.execute("PRAGMA foreign_keys=ON")
    existing = origo_db.execute("SELECT COUNT(*) FROM methodology_registry").fetchone()[0]
    if existing == 0:
        origo_db.executemany(
            """INSERT OR IGNORE INTO methodology_registry
               (id, name, methodology_type, version, description, valid_from, valid_until)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    "kobo-gps-v2.3",
                    "KoboToolbox GPS v2.3",
                    "gps_polygon",
                    "2.3",
                    "KoboToolbox field GPS polygon collection",
                    "2025-01-01",
                    None,
                ),
                (
                    "planet-ndvi-2025q4",
                    "Planet NDVI Mosaic 2025-Q4",
                    "satellite_ndvi",
                    "2025-Q4",
                    "Planet Labs monthly NDVI mosaic for EUDR deforestation assessment",
                    "2025-10-01",
                    "2026-09-30",
                ),
                (
                    "manual-tape-v1",
                    "Manual Tape Survey v1",
                    "manual_survey",
                    "1.0",
                    "Manual tape measure polygon for small parcels <0.5ha",
                    "2024-01-01",
                    None,
                ),
            ],
        )
        origo_db.commit()
        print("  origo.db: methodology_registry seeded with 3 base methodologies")
    else:
        print(f"  origo.db: methodology_registry already has {existing} rows — skipped seeding")

    origo_db.close()
    print("  origo.db: territorial_boundaries + submissions tables applied")

    print("Phase 3 migration complete.")


if __name__ == "__main__":
    migrate()
