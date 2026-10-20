#!/usr/bin/env python3
"""Import startups CSV into origo.db startups table.

Maps from the clp-startups-ct-mapping CSV:
  startup_name → name, country, program, nexus_theme, stage,
  ct_primary_node, ct_secondary_1, ct_secondary_2,
  mapping_confidence, mapping_notes.

Auto-generates UUID for id, slugifies name for nexus_id.
"""

import csv
import re
import sqlite3
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import init_all_dbs


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def main(csv_path: str) -> None:
    init_all_dbs()

    conn = sqlite3.connect(settings.origo_db)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows_to_insert = []

        for row in reader:
            name = row.get("startup_name", "").strip()
            if not name:
                continue

            stage = row.get("stage", "").strip() or None
            valid_stages = {"Pre-Seed", "Seed", "Pre-A", "Series A", "Series B+", "Unknown"}
            if stage and stage not in valid_stages:
                stage = "Unknown"

            ct1 = row.get("ct_primary_node", "").strip() or None
            ct2 = row.get("ct_secondary_1", "").strip() or None
            ct3 = row.get("ct_secondary_2", "").strip() or None

            confidence = row.get("mapping_confidence", "").strip() or None
            if confidence and confidence not in ("high", "medium", "low"):
                confidence = "low"

            rows_to_insert.append((
                str(uuid.uuid4()),
                slugify(name),
                name,
                row.get("country", "CO").strip(),
                row.get("program", "").strip() or None,
                stage,
                None,  # website — not in CSV
                None,  # description — not in CSV
                ct1,
                ct2,
                ct3,
                confidence,
                row.get("mapping_notes", "").strip() or None,
                row.get("nexus_theme", "").strip() or None,
                "not_required",
                '["internal","research"]',
                "CC BY-NC-SA 4.0",
            ))

    conn.execute("DELETE FROM startups")
    conn.executemany(
        """INSERT INTO startups
           (id, nexus_id, name, country, program, stage, website, description,
            ct_primary_node, ct_secondary_1, ct_secondary_2,
            mapping_confidence, mapping_notes, nexus_theme,
            fpic_status, permitted_purposes, data_licence)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows_to_insert,
    )
    conn.commit()
    conn.close()

    print(f"Imported {len(rows_to_insert)} startups.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_startups.py <path-to-startups-csv>")
        sys.exit(1)
    main(sys.argv[1])
