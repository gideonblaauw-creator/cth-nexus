"""SENAMHI hydrometeorological open CSV (sampled time series)."""
from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .catalog import ACTIVE
from .db import upsert_source
from .fetch import download, record_raw_file
from .paths import SENAMHI_MAX_ROWS

CSV_URL = (
    "https://www.datosabiertos.gob.pe/sites/default/files/"
    "Variables%20Meteorologicas%20de%20las%20Estaciones%20autom%C3%A1ticas%20de%20"
    "intercambio%20internacional%20-%20%5BServicio%20Nacional%20de%20Meteorolog%C3%ADa%20"
    "e%20Hidrolog%C3%ADa%20del%20Per%C3%BA%20-%20SENAMHI%5D_0.csv"
)
MIN_DATE = 20240101  # YYYYMMDD int — limit historical depth for disk budget


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ingest(conn: sqlite3.Connection, raw_dir: Path) -> tuple[int, int]:
    spec = next(s for s in ACTIVE if s.id == "senamhi_estaciones_automaticas")
    fr = download(CSV_URL, spec.id, raw_dir=raw_dir)
    record_raw_file(conn, spec.id, str(fr.path.name), fr.sha256, fr.bytes, _now())

    conn.execute("DELETE FROM stations WHERE source_id = ?", (spec.id,))
    conn.execute("DELETE FROM observations WHERE source_id = ?", (spec.id,))

    stations_seen: set[str] = set()
    obs_rows = 0
    with fr.path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if obs_rows >= SENAMHI_MAX_ROWS:
                break
            fecha = _int(row.get("FECHA"))
            if fecha is not None and fecha < MIN_DATE:
                continue
            code = (row.get("ESTACION") or "").strip()
            if not code:
                continue
            if code not in stations_seen:
                stations_seen.add(code)
                ubigeo = row.get("UBIGEO")
                conn.execute(
                    """
                    INSERT OR REPLACE INTO stations (
                      source_id, station_code, name, department, province, district,
                      ubigeo, lat, lon, meta_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        spec.id,
                        code,
                        code,
                        row.get("DEPARTAMENTO"),
                        row.get("PROVINCIA"),
                        row.get("DISTRITO"),
                        str(ubigeo).split(".")[0] if ubigeo else None,
                        _float(row.get("LATITUD")),
                        _float(row.get("LONGITUD")),
                        json.dumps(
                            {"altitud": row.get("ALTITUD"), "red": row.get("RED")},
                            ensure_ascii=False,
                        ),
                    ),
                )

            observed_at = _observed_at(fecha, row.get("HORA"))
            for var, col in (
                ("temp_c", "TEMP"),
                ("relative_humidity_pct", "HR"),
                ("precip_mm", "PP"),
            ):
                val = _float(row.get(col))
                if val is None:
                    continue
                conn.execute(
                    """
                    INSERT OR IGNORE INTO observations (
                      source_id, station_code, observed_at, variable, value, unit
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        spec.id,
                        code,
                        observed_at,
                        var,
                        val,
                        {"temp_c": "C", "relative_humidity_pct": "%", "precip_mm": "mm"}[var],
                    ),
                )
                obs_rows += 1

    note = (
        f"Full file ~50MB; ingested <= {SENAMHI_MAX_ROWS} observation rows with FECHA >= {MIN_DATE}."
    )
    upsert_source(
        conn,
        source_id=spec.id,
        name=spec.name,
        publisher=spec.publisher,
        url=CSV_URL,
        license=spec.license,
        format=spec.format,
        update_frequency=spec.update_frequency,
        status="pulled",
        notes=note,
        fetched_at=_now(),
        row_count=obs_rows,
    )
    return len(stations_seen), obs_rows


def _observed_at(fecha: int | None, hora: str | None) -> str:
    if fecha is None:
        return "unknown"
    s = str(fecha).zfill(8)
    iso_date = f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    if not hora:
        return f"{iso_date}T00:00:00Z"
    h = str(hora).zfill(5)
    return f"{iso_date}T{h[0:2]}:{h[2:4]}:{h[4:6]}Z"


def _int(v) -> int | None:
    try:
        if v in (None, "", " "):
            return None
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _float(v) -> float | None:
    try:
        if v in (None, "", " "):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None
