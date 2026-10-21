#!/usr/bin/env python3
"""Idempotent refresh of Peru water open-data SQLite DB."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from .catalog import ACTIVE, SKIPPED
from .db import connect, upsert_source
from .ingest_ana import ingest_fajas_sample, ingest_stations
from .ingest_inei import ingest as ingest_inei
from .ingest_senamhi import ingest as ingest_senamhi
from .ingest_sunass import ingest_all as ingest_sunass
from .paths import DB_PATH, RAW_DIR


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def mark_skipped(conn) -> None:
    for spec, reason in SKIPPED:
        upsert_source(
            conn,
            source_id=spec.id,
            name=spec.name,
            publisher=spec.publisher,
            url=spec.url,
            license=spec.license,
            format=spec.format,
            update_frequency=spec.update_frequency,
            status="skipped",
            notes=reason,
            fetched_at=_now(),
            row_count=0,
        )


def _ensure_active_sources(conn) -> None:
    for spec in ACTIVE:
        upsert_source(
            conn,
            source_id=spec.id,
            name=spec.name,
            publisher=spec.publisher,
            url=spec.url,
            license=spec.license,
            format=spec.format,
            update_frequency=spec.update_frequency,
            status="pending",
            notes=None,
            fetched_at=None,
            row_count=None,
        )


def refresh(db_path: Path, raw_dir: Path) -> None:
    conn = connect(db_path)
    mark_skipped(conn)
    _ensure_active_sources(conn)

    ingest_stations(conn)
    ingest_fajas_sample(conn, raw_dir)
    ingest_sunass(conn, raw_dir)
    ingest_senamhi(conn, raw_dir)
    ingest_inei(conn, raw_dir)

    conn.commit()
    conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    args = parser.parse_args(argv)

    refresh(args.db, args.raw_dir)
    print(f"Refresh complete: db={args.db} raw={args.raw_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
