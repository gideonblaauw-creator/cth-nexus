"""SUNASS utility indicators via datosabiertos.gob.pe."""
from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .catalog import ACTIVE
from .db import upsert_source
from .fetch import download, record_raw_file

URLS = {
    "sunass_conexiones_activas": (
        "https://www.datosabiertos.gob.pe/sites/default/files/Conexiones_activas_Dataset.csv"
    ),
    "sunass_estructuras_tarifarias": (
        "https://www.datosabiertos.gob.pe/sites/default/files/EETT_Dataset.csv"
    ),
    "sunass_distritos_emergencia_hidrica": (
        "https://www.datosabiertos.gob.pe/sites/default/files/DSHidricos_Dataset.csv"
    ),
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ingest_all(conn: sqlite3.Connection, raw_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for spec in ACTIVE:
        if spec.id not in URLS:
            continue
        url = URLS[spec.id]
        fr = download(url, spec.id, raw_dir=raw_dir)
        record_raw_file(conn, spec.id, str(fr.path.relative_to(raw_dir.parent)), fr.sha256, fr.bytes, _now())

        conn.execute("DELETE FROM utility_indicators WHERE source_id = ?", (spec.id,))
        if spec.id == "sunass_distritos_emergencia_hidrica":
            conn.execute("DELETE FROM access_by_region WHERE source_id = ?", (spec.id,))

        rows = 0
        delimiter = ";" if spec.id == "sunass_estructuras_tarifarias" else ","
        with fr.path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
            reader = csv.DictReader(fh, delimiter=delimiter)
            for row in reader:
                rows += 1
                if spec.id == "sunass_conexiones_activas":
                    year = _int(row.get("ANIO"))
                    mes_raw = row.get("MES") or ""
                    month = _int(mes_raw)
                    if month and month > 12:
                        month = int(str(month)[-2:])
                        if not year and len(str(mes_raw)) >= 6:
                            year = int(str(mes_raw)[:4])
                    conn.execute(
                        """
                        INSERT INTO utility_indicators (
                          source_id, indicator_code, provider, department, province, district,
                          period_year, period_month, value, unit, meta_json
                        ) VALUES (?, 'conexiones_activas', ?, ?, ?, ?, ?, ?, ?, 'connections', ?)
                        """,
                        (
                            spec.id,
                            row.get("PRESTADOR"),
                            row.get("DEPARTAMENTO"),
                            row.get("PROVINCIA"),
                            row.get("DISTRITO"),
                            year,
                            month,
                            _float(row.get("CONEX_ACTIVAS")),
                            json.dumps(row, ensure_ascii=False),
                        ),
                    )
                elif spec.id == "sunass_estructuras_tarifarias":
                    conn.execute(
                        """
                        INSERT INTO utility_indicators (
                          source_id, indicator_code, provider, department, province, district,
                          period_year, value, unit, meta_json
                        ) VALUES (?, 'tarifa_agua', ?, ?, ?, ?, ?, ?, 'PEN/m3', ?)
                        """,
                        (
                            spec.id,
                            row.get("prestador_nombre"),
                            row.get("localidad_nombre"),
                            None,
                            None,
                            _int((row.get("periodo_anio_mes") or "")[:4]),
                            _float(row.get("tarifa_agua")),
                            json.dumps(row, ensure_ascii=False),
                        ),
                    )
                elif spec.id == "sunass_distritos_emergencia_hidrica":
                    ubigeo = row.get("UBIGEO")
                    cob = _float(row.get("COB_AGUA"))
                    conn.execute(
                        """
                        INSERT INTO utility_indicators (
                          source_id, indicator_code, department, province, district, ubigeo,
                          period_year, value, unit, meta_json
                        ) VALUES (?, 'cobertura_agua_emergencia_pct', ?, ?, ?, ?, ?, ?, 'percent', ?)
                        """,
                        (
                            spec.id,
                            row.get("DEPARTAMENTO"),
                            row.get("PROVINCIA"),
                            row.get("DISTRITO"),
                            ubigeo,
                            _int(row.get("ANIO")),
                            cob,
                            json.dumps(row, ensure_ascii=False),
                        ),
                    )
                    conn.execute(
                        """
                        INSERT INTO access_by_region (
                          source_id, region_level, region_code, region_name, year,
                          indicator, percentage, meta_json
                        ) VALUES (?, 'district', ?, ?, ?, 'cobertura_agua_emergencia', ?, ?)
                        """,
                        (
                            spec.id,
                            ubigeo,
                            row.get("DISTRITO"),
                            _int(row.get("ANIO")),
                            cob,
                            json.dumps({"poblacion": row.get("POBLACION")}, ensure_ascii=False),
                        ),
                    )

        upsert_source(
            conn,
            source_id=spec.id,
            name=spec.name,
            publisher=spec.publisher,
            url=url,
            license=spec.license,
            format=spec.format,
            update_frequency=spec.update_frequency,
            status="pulled",
            notes=None,
            fetched_at=_now(),
            row_count=rows,
        )
        counts[spec.id] = rows
    return counts


def _int(v) -> int | None:
    try:
        return int(v) if v not in (None, "", " ") else None
    except (TypeError, ValueError):
        return None


def _float(v) -> float | None:
    try:
        return float(v) if v not in (None, "", " ") else None
    except (TypeError, ValueError):
        return None
