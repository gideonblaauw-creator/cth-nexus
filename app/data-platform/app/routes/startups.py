from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.database import get_origo_db
from app.models import StartupOut
from app.response import make_meta, make_request_id, standard_headers

router = APIRouter(prefix="/v1/startups", tags=["startups"])

STARTUP_COLUMNS = [
    "id", "nexus_id", "name", "country", "program", "stage", "website",
    "description", "ct_primary_node", "ct_secondary_1", "ct_secondary_2",
    "mapping_confidence", "mapping_notes", "nexus_theme", "data_licence",
]


@router.get("")
def list_startups(
    request: Request,
    ct_node: str | None = None,
    country: str | None = None,
    stage: str | None = None,
    program: str | None = None,
    confidence: str | None = None,
    limit: int = Query(default=20, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
):
    request_id = getattr(request.state, "request_id", make_request_id())
    fpic_filter = getattr(request.state, "fpic_filter", ("approved", "not_required"))

    conditions = ["fpic_status IN ({})".format(",".join("?" for _ in fpic_filter))]
    params: list = list(fpic_filter)

    if ct_node:
        conditions.append(
            "(ct_primary_node = ? OR ct_secondary_1 = ? OR ct_secondary_2 = ?)"
        )
        params.extend([ct_node, ct_node, ct_node])
    if country:
        conditions.append("country = ?")
        params.append(country)
    if stage:
        conditions.append("stage = ?")
        params.append(stage)
    if program:
        conditions.append("program = ?")
        params.append(program)
    if confidence:
        conditions.append("mapping_confidence = ?")
        params.append(confidence)

    where = " AND ".join(conditions)

    with get_origo_db() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM startups WHERE {where}", params
        ).fetchone()[0]

        rows = conn.execute(
            f"SELECT * FROM startups WHERE {where} ORDER BY name LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

    data = [StartupOut(**dict(r)).model_dump() for r in rows]
    meta = make_meta(total, limit, offset, request_id)
    headers = standard_headers(request_id)

    return JSONResponse(
        content={"data": data, "meta": meta.model_dump()},
        headers=headers,
    )


@router.get("/export")
def export_startups(request: Request):
    request_id = getattr(request.state, "request_id", make_request_id())
    fpic_filter = getattr(request.state, "fpic_filter", ("approved", "not_required"))

    placeholders = ",".join("?" for _ in fpic_filter)

    with get_origo_db() as conn:
        rows = conn.execute(
            f"SELECT * FROM startups WHERE fpic_status IN ({placeholders}) ORDER BY name",
            list(fpic_filter),
        ).fetchall()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=STARTUP_COLUMNS)
    writer.writeheader()
    for r in rows:
        d = dict(r)
        writer.writerow({k: d.get(k) for k in STARTUP_COLUMNS})

    output.seek(0)
    headers = standard_headers(request_id)
    headers["Content-Disposition"] = "attachment; filename=cth-startups-export.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers,
    )


@router.get("/{startup_id}")
def get_startup(request: Request, startup_id: str):
    request_id = getattr(request.state, "request_id", make_request_id())
    fpic_filter = getattr(request.state, "fpic_filter", ("approved", "not_required"))
    placeholders = ",".join("?" for _ in fpic_filter)

    with get_origo_db() as conn:
        row = conn.execute(
            f"SELECT * FROM startups WHERE (id = ? OR nexus_id = ?) "
            f"AND fpic_status IN ({placeholders})",
            [startup_id, startup_id] + list(fpic_filter),
        ).fetchone()

    headers = standard_headers(request_id)

    if not row:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found"},
            headers=headers,
        )

    data = StartupOut(**dict(row)).model_dump()
    return JSONResponse(content={"data": data}, headers=headers)
