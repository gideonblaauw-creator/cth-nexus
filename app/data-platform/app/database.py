from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from app.config import settings


def _init_db(db_path: str, schema_file: str) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    schema_path = Path(__file__).parent.parent / "db" / schema_file
    if schema_path.exists():
        conn = sqlite3.connect(str(path))
        conn.executescript(schema_path.read_text())
        conn.close()


def init_all_dbs() -> None:
    _init_db(settings.origo_db, "schema_origo.sql")
    _init_db(settings.apikeys_db, "schema_apikeys.sql")
    _init_db(settings.provenance_db, "schema_provenance.sql")


def _get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_origo_db() -> Generator[sqlite3.Connection, None, None]:
    conn = _get_connection(settings.origo_db)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_apikeys_db() -> Generator[sqlite3.Connection, None, None]:
    conn = _get_connection(settings.apikeys_db)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_provenance_db() -> Generator[sqlite3.Connection, None, None]:
    conn = _get_connection(settings.provenance_db)
    try:
        yield conn
    finally:
        conn.close()
