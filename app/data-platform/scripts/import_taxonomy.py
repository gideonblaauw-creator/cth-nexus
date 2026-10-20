#!/usr/bin/env python3
"""Import taxonomy CSV into origo.db taxonomy_nodes table.

Maps from the 62-column origo-taxonomy CSV to the simplified schema:
  origo_id → id, origo_label → label_short/label_full, sector, description,
  origo_parent → parent_id, latam_relevant → latam_relevance,
  latam_colombia/mexico/chile, cth_data_coverage, cth_clp_coverage,
  bookstack_page_id.
"""

import csv
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import init_all_dbs

SECTOR_ORDER = {
    "AF": 0, "EN": 1, "WA": 2, "IC": 3, "XS": 4,
    "TR": 5, "IN": 6, "BU": 7, "WW": 8, "EX": 9,
}


def parse_bool_col(val: str) -> int:
    if not val:
        return 0
    v = val.strip().upper()
    return 1 if v in ("Y", "YES", "1", "TRUE") else 0


def parse_latam_relevance(val: str) -> str | None:
    if not val:
        return None
    v = val.strip().upper()
    if v in ("Y", "YES", "HIGH"):
        return "high"
    if v in ("N", "NO", "NA"):
        return "na"
    if v in ("MEDIUM", "MED"):
        return "medium"
    if v == "LOW":
        return "low"
    return None


def main(csv_path: str) -> None:
    init_all_dbs()

    conn = sqlite3.connect(settings.origo_db)
    conn.execute("PRAGMA foreign_keys=OFF")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        seq_counter: dict[str, int] = {}
        rows_to_insert = []

        for row in reader:
            node_id = row.get("origo_id", "").strip()
            if not node_id:
                continue

            sector = row.get("sector", "").strip()
            if sector not in SECTOR_ORDER:
                parts = node_id.split("-")
                sector = parts[1] if len(parts) >= 2 else "XS"

            seq_counter.setdefault(sector, 0)
            seq_counter[sector] += 1

            label = row.get("origo_label", "").strip()
            description = row.get("description", "").strip() or None
            parent = row.get("origo_parent", "").strip() or None

            bsp_id = row.get("bookstack_page_id", "").strip()
            bookstack_page_id = int(bsp_id) if bsp_id and bsp_id.isdigit() else None

            rows_to_insert.append((
                node_id,
                sector,
                seq_counter[sector],
                label,
                label,
                description,
                parent,
                parse_latam_relevance(row.get("latam_relevant", "")),
                parse_bool_col(row.get("latam_colombia", "")),
                parse_bool_col(row.get("latam_mexico", "")),
                parse_bool_col(row.get("latam_chile", "")),
                row.get("cth_data_coverage", "N").strip() or "N",
                row.get("cth_clp_coverage", "").strip() or None,
                bookstack_page_id,
                "1.1",
            ))

    conn.execute("DELETE FROM taxonomy_nodes")
    conn.executemany(
        """INSERT INTO taxonomy_nodes
           (id, sector, seq, label_short, label_full, description, parent_id,
            latam_relevance, latam_colombia, latam_mexico, latam_chile,
            cth_data_coverage, cth_clp_coverage, bookstack_page_id, version)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows_to_insert,
    )
    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON")
    conn.close()

    print(f"Imported {len(rows_to_insert)} taxonomy nodes.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_taxonomy.py <path-to-taxonomy-csv>")
        sys.exit(1)
    main(sys.argv[1])
