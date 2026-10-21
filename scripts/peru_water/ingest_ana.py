"""ANA / SNIRH-related open data."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .catalog import ACTIVE
from .db import upsert_source
from .fetch import download, record_raw_file
from .paths import ANA_FAJA_MAX_ROWS, USER_AGENT

IDEp_LAYER = "https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/MapServer/4"
FAJA_URL = (
    "https://www.datosabiertos.gob.pe/sites/default/files/"
    "Faja_Marginal_Datos_Abiertos_Act31082026.csv"
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ingest_stations(conn: sqlite3.Connection) -> int:
    spec = next(s for s in ACTIVE if s.id == "ana_snirh_stations_idep")
    conn.execute("DELETE FROM stations WHERE source_id = ?", (spec.id,))

    offset = 0
    page = 1000
    total = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": page,
        }
        url = f"{IDEp_LAYER}/query?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=90) as resp:
            payload = json.load(resp)
        features = payload.get("features") or []
        if not features:
            break
        for feat in features:
            a = feat.get("attributes") or {}
            geom = feat.get("geometry") or {}
            code = str(a.get("CODIGO") or a.get("COD_EST") or a.get("OBJECTID"))
            conn.execute(
                """
                INSERT OR REPLACE INTO stations (
                  source_id, station_code, name, station_type, sub_type, river,
                  operator, status, year_start, year_end, lat, lon, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    spec.id,
                    code,
                    a.get("Nombre"),
                    a.get("TIP_EST"),
                    a.get("TIP_SUBEST"),
                    a.get("RIO"),
                    a.get("INSTI_OPER"),
                    a.get("ESTADO"),
                    _int(a.get("ANO_INICIO")),
                    _int(a.get("ANO_FINAL")),
                    geom.get("y"),
                    geom.get("x"),
                    json.dumps(a, ensure_ascii=False),
                ),
            )
            total += 1
        offset += len(features)
        if len(features) < page:
            break

    upsert_source(
        conn,
        source_id=spec.id,
        name=spec.name,
        publisher=spec.publisher,
        url=spec.url,
        license=spec.license,
        format=spec.format,
        update_frequency=spec.update_frequency,
        status="pulled",
        notes="Station registry from IDEP ANA_WMS layer Hidrometeorológica (not live SNIRH time series).",
        fetched_at=_now(),
        row_count=total,
    )
    return total


def ingest_fajas_sample(conn: sqlite3.Connection, raw_dir) -> int:
    import csv
    from pathlib import Path

    spec = next(s for s in ACTIVE if s.id == "ana_fajas_marginales_datosabiertos")
    # Sample via ranged download (~20MB) — full national file is ~80MB.
    fr = download(FAJA_URL, spec.id, raw_dir=raw_dir, max_bytes=20 * 1024 * 1024)
    record_raw_file(conn, spec.id, str(fr.path.relative_to(raw_dir.parent)), fr.sha256, fr.bytes, _now())

    # Store polygon attributes as utility/geo features in utility_indicators for light footprint
    conn.execute("DELETE FROM utility_indicators WHERE source_id = ?", (spec.id,))
    path = Path(fr.path)
    rows = 0
    with path.open("r", encoding="latin-1", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if rows >= ANA_FAJA_MAX_ROWS:
                break
            conn.execute(
                """
                INSERT INTO utility_indicators (
                  source_id, indicator_code, department, province, district, ubigeo,
                  value, unit, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    spec.id,
                    "faja_marginal_segment",
                    row.get("NOMDEP"),
                    row.get("NOMPROV"),
                    row.get("NOMDIST"),
                    row.get("CODIGO"),
                    _float(row.get("ANCHOFAJA")),
                    "m",
                    json.dumps(row, ensure_ascii=False),
                ),
            )
            rows += 1

    note = f"Full CSV is ~80MB; ingested first {ANA_FAJA_MAX_ROWS} rows only."
    upsert_source(
        conn,
        source_id=spec.id,
        name=spec.name,
        publisher=spec.publisher,
        url=FAJA_URL,
        license=spec.license,
        format=spec.format,
        update_frequency=spec.update_frequency,
        status="pulled",
        notes=note,
        fetched_at=_now(),
        row_count=rows,
    )
    return rows


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
