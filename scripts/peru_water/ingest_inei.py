"""INEI ENAPRES microdata — weighted access proxy by department."""
from __future__ import annotations

import csv
import json
import sqlite3
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from io import TextIOWrapper
from pathlib import Path

from .catalog import ACTIVE
from .db import upsert_source
from .fetch import download, record_raw_file
from .paths import ENAPRES_MAX_ROWS

ENAPRES_ZIP = "https://www.inei.gob.pe/media/DATOS_ABIERTOS/ENAPRES/DATA/2024.zip"
INNER_MODULE = "965-Modulo1858.zip"
INNER_CSV = "965-Modulo1858/CAP_300_URBANO_RURAL_5.csv"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ingest(conn: sqlite3.Connection, raw_dir: Path) -> int:
    spec = next(s for s in ACTIVE if s.id == "inei_enapres_2024_access")
    fr = download(ENAPRES_ZIP, spec.id, raw_dir=raw_dir)
    record_raw_file(conn, spec.id, str(fr.path.name), fr.sha256, fr.bytes, _now())

    conn.execute("DELETE FROM access_by_region WHERE source_id = ?", (spec.id,))

    # P307: principal fuente de agua para beber (see ENAPRES dictionary CAP300)
    weighted: dict[tuple[str, str, str, str], float] = defaultdict(float)
    totals: dict[tuple[str, str, str], float] = defaultdict(float)
    rows_read = 0

    with zipfile.ZipFile(fr.path) as outer:
        inner_bytes = outer.read(INNER_MODULE)
    inner_path = raw_dir / spec.id / INNER_MODULE
    inner_path.parent.mkdir(parents=True, exist_ok=True)
    inner_path.write_bytes(inner_bytes)

    with zipfile.ZipFile(inner_path) as inner:
        with inner.open(INNER_CSV) as raw:
            text = TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
            reader = csv.DictReader(text)
            for row in reader:
                if rows_read >= ENAPRES_MAX_ROWS:
                    break
                rows_read += 1
                dept_code = (row.get("CCDD") or "").strip()
                dept_name = (row.get("NOMBREDD") or "").strip()
                area = (row.get("AREA") or "").strip()
                factor = _float(row.get("FACTOR")) or 0.0
                p307 = (row.get("P307") or "").strip()
                if not dept_code or not p307 or factor <= 0:
                    continue
                key_tot = (dept_code, dept_name, area)
                weighted[(dept_code, dept_name, area, p307)] += factor
                totals[key_tot] += factor

    inserted = 0
    year = 2024
    for (dept_code, dept_name, area, p307), w in weighted.items():
        denom = totals.get((dept_code, dept_name, area), 0.0) or 1.0
        pct = 100.0 * w / denom
        conn.execute(
            """
            INSERT INTO access_by_region (
              source_id, region_level, region_code, region_name, area_type, year,
              indicator, numerator, denominator, percentage, meta_json
            ) VALUES (?, 'department', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                spec.id,
                dept_code,
                dept_name,
                _area_label(area),
                year,
                f"enapres_p307_code_{p307}",
                w,
                denom,
                pct,
                json.dumps({"variable": "P307", "code": p307}, ensure_ascii=False),
            ),
        )
        inserted += 1

    upsert_source(
        conn,
        source_id=spec.id,
        name=spec.name,
        publisher=spec.publisher,
        url=ENAPRES_ZIP,
        license=spec.license,
        format=spec.format,
        update_frequency=spec.update_frequency,
        status="pulled",
        notes=(
            f"Weighted distribution of ENAPRES P307 (drinking water source) by department; "
            f"microdata rows scanned: {rows_read} (cap {ENAPRES_MAX_ROWS})."
        ),
        fetched_at=_now(),
        row_count=inserted,
    )
    return inserted


def _area_label(area: str) -> str:
    return {"1": "urbano", "2": "rural"}.get(area, area or "unknown")


def _float(v) -> float | None:
    try:
        if v in (None, "", " "):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None
