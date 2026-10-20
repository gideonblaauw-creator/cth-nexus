from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.database import get_origo_db
from app.models import StartupOut, TaxonomyNodeOut
from app.response import make_meta, make_request_id, standard_headers

router = APIRouter(prefix="/v1/taxonomy", tags=["taxonomy"])


@router.get("/nodes")
def list_nodes(
    request: Request,
    sector: str | None = None,
    latam_relevance: str | None = None,
    cth_data_coverage: str | None = None,
    limit: int = Query(default=200, le=500, ge=1),
    offset: int = Query(default=0, ge=0),
):
    request_id = getattr(request.state, "request_id", make_request_id())

    conditions: list[str] = []
    params: list = []

    if sector:
        conditions.append("sector = ?")
        params.append(sector)
    if latam_relevance:
        conditions.append("latam_relevance = ?")
        params.append(latam_relevance)
    if cth_data_coverage:
        conditions.append("cth_data_coverage = ?")
        params.append(cth_data_coverage)

    where = " AND ".join(conditions) if conditions else "1=1"

    with get_origo_db() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM taxonomy_nodes WHERE {where}", params
        ).fetchone()[0]

        rows = conn.execute(
            f"SELECT * FROM taxonomy_nodes WHERE {where} ORDER BY sector, seq "
            f"LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

    data = [TaxonomyNodeOut(**dict(r)).model_dump() for r in rows]
    meta = make_meta(total, limit, offset, request_id)
    headers = standard_headers(request_id)

    return JSONResponse(
        content={"data": data, "meta": meta.model_dump()},
        headers=headers,
    )


@router.get("/nodes/{node_id}")
def get_node(request: Request, node_id: str):
    request_id = getattr(request.state, "request_id", make_request_id())
    headers = standard_headers(request_id)

    with get_origo_db() as conn:
        row = conn.execute(
            "SELECT * FROM taxonomy_nodes WHERE id = ?", (node_id,)
        ).fetchone()

        if not row:
            return JSONResponse(
                status_code=404,
                content={"error": "not_found"},
                headers=headers,
            )

        fpic_filter = getattr(
            request.state, "fpic_filter", ("approved", "not_required")
        )
        placeholders = ",".join("?" for _ in fpic_filter)
        linked = conn.execute(
            f"SELECT * FROM startups "
            f"WHERE (ct_primary_node = ? OR ct_secondary_1 = ? OR ct_secondary_2 = ?) "
            f"AND fpic_status IN ({placeholders})",
            [node_id, node_id, node_id] + list(fpic_filter),
        ).fetchall()

    node_data = TaxonomyNodeOut(**dict(row)).model_dump()
    node_data["linked_startups"] = [
        StartupOut(**dict(s)).model_dump() for s in linked
    ]

    return JSONResponse(content={"data": node_data}, headers=headers)
