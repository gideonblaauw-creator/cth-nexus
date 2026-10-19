from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.config import settings
from app.database import get_origo_db
from app.response import make_request_id, standard_headers

router = APIRouter(tags=["health"])

LLMS_TXT = """# CleantechHUB Data Platform
# https://data.cleantechhub.net

User-agent: *
Allow: /v1/taxonomy/nodes
Allow: /v1/startups
Allow: /catalogue
Disallow: /v1/api-keys
Disallow: /v1/admin

# Dataset: LATAM Cleantech Taxonomy v1.1 — 106 nodes, 10 sectors
# Dataset: LATAM Startup Portfolio — 102 startups mapped to taxonomy
# Licence: CC BY-NC-SA 4.0
# Contact: data@cleantechhub.net
# Purpose declaration required for bulk use: POST /policy/evaluate
"""


@router.get("/health")
def health_check(request: Request):
    request_id = getattr(request.state, "request_id", make_request_id())
    headers = standard_headers(request_id)

    db_status = "ok"
    try:
        with get_origo_db() as conn:
            conn.execute("SELECT 1").fetchone()
    except Exception:
        db_status = "error"

    status = "ok" if db_status == "ok" else "degraded"

    return JSONResponse(
        content={
            "status": status,
            "db": db_status,
            "version": settings.DATASET_VERSION,
        },
        headers=headers,
    )


@router.get("/llms.txt")
def llms_txt():
    return PlainTextResponse(content=LLMS_TXT, media_type="text/plain")
