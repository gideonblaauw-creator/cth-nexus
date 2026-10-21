"""SQLite schema and helpers."""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  publisher TEXT,
  url TEXT,
  license TEXT,
  format TEXT,
  update_frequency TEXT,
  status TEXT NOT NULL,
  notes TEXT,
  fetched_at TEXT,
  row_count INTEGER
);

CREATE TABLE IF NOT EXISTS raw_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL REFERENCES sources(id),
  rel_path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  bytes INTEGER NOT NULL,
  fetched_at TEXT NOT NULL,
  UNIQUE(source_id, sha256)
);

CREATE TABLE IF NOT EXISTS stations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL REFERENCES sources(id),
  station_code TEXT NOT NULL,
  name TEXT,
  station_type TEXT,
  sub_type TEXT,
  river TEXT,
  operator TEXT,
  status TEXT,
  year_start INTEGER,
  year_end INTEGER,
  ubigeo TEXT,
  department TEXT,
  province TEXT,
  district TEXT,
  lat REAL,
  lon REAL,
  meta_json TEXT,
  UNIQUE(source_id, station_code)
);

CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL REFERENCES sources(id),
  station_code TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  variable TEXT NOT NULL,
  value REAL,
  unit TEXT,
  quality TEXT,
  UNIQUE(source_id, station_code, observed_at, variable)
);

CREATE TABLE IF NOT EXISTS utility_indicators (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL REFERENCES sources(id),
  indicator_code TEXT NOT NULL,
  provider TEXT,
  department TEXT,
  province TEXT,
  district TEXT,
  ubigeo TEXT,
  period_year INTEGER,
  period_month INTEGER,
  value REAL,
  unit TEXT,
  meta_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_utility_indicators_lookup
  ON utility_indicators(source_id, indicator_code, period_year, ubigeo);

CREATE TABLE IF NOT EXISTS access_by_region (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL REFERENCES sources(id),
  region_level TEXT NOT NULL,
  region_code TEXT,
  region_name TEXT,
  area_type TEXT,
  year INTEGER,
  indicator TEXT NOT NULL,
  numerator REAL,
  denominator REAL,
  percentage REAL,
  meta_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_access_region
  ON access_by_region(source_id, year, region_code, indicator);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    return conn


def upsert_source(
    conn: sqlite3.Connection,
    *,
    source_id: str,
    name: str,
    publisher: str,
    url: str,
    license: str,
    format: str,
    update_frequency: str,
    status: str,
    notes: str | None,
    fetched_at: str | None,
    row_count: int | None,
) -> None:
    conn.execute(
        """
        INSERT INTO sources (
          id, name, publisher, url, license, format, update_frequency,
          status, notes, fetched_at, row_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name,
          publisher=excluded.publisher,
          url=excluded.url,
          license=excluded.license,
          format=excluded.format,
          update_frequency=excluded.update_frequency,
          status=excluded.status,
          notes=excluded.notes,
          fetched_at=excluded.fetched_at,
          row_count=excluded.row_count
        """,
        (
            source_id,
            name,
            publisher,
            url,
            license,
            format,
            update_frequency,
            status,
            notes,
            fetched_at,
            row_count,
        ),
    )
