from __future__ import annotations

import uuid

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import get_origo_db, get_provenance_db
from app.response import make_request_id, standard_headers

router = APIRouter(tags=["policy"])

VALID_PURPOSES = ["research", "eudr", "csrd", "carbon", "internal"]
OPA_PURPOSE_URL = "http://localhost:8181/v1/data/cth/purpose"
OPA_COMMERCIAL_URL = "http://localhost:8181/v1/data/cth/commercial"


@router.post("/policy/evaluate")
async def evaluate_policy(request: Request, body: dict | None = None):
    request_id = getattr(request.state, "request_id", make_request_id())
    headers = standard_headers(request_id)

    if body is None:
        body = {}

    purpose = body.get("purpose")
    if not purpose:
        return JSONResponse(
            status_code=400,
            content={
                "error": "purpose_required",
                "valid": VALID_PURPOSES,
            },
            headers=headers,
        )

    if purpose not in VALID_PURPOSES:
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_purpose",
                "valid": VALID_PURPOSES,
            },
            headers=headers,
        )

    caller_tier = body.get("caller_tier") or getattr(request.state, "tier", "free")

    # OPA evaluation — fall back to hardcoded logic if OPA is unreachable
    opa_input = {
        "declared_purpose": purpose,
        "caller_tier": caller_tier,
        "cpi_licence_active": settings.CPI_LICENCE_ACTIVE,
        "fpic_permitted_purposes": body.get("fpic_permitted_purposes"),
        "benefit_agreement_present": body.get("benefit_agreement_present", False),
    }

    try:
        async with httpx.AsyncClient() as client:
            purpose_r = await client.post(
                OPA_PURPOSE_URL, json={"input": opa_input}, timeout=2.0
            )
            purpose_result = purpose_r.json().get("result", {})

            commercial_r = await client.post(
                OPA_COMMERCIAL_URL, json={"input": opa_input}, timeout=2.0
            )
            commercial_result = commercial_r.json().get("result", {})

        if not commercial_result.get("allow", True):
            deny = commercial_result.get("deny_reason", "commercial_blocked")
            _log_policy_eval(request, request_id, purpose, body, "deny", deny)
            return JSONResponse(
                status_code=403,
                content={"error": "commercial_blocked", "reason": deny},
                headers=headers,
            )

        if not purpose_result.get("allow", True):
            deny = purpose_result.get("deny_reason", "purpose_denied")
            _log_policy_eval(request, request_id, purpose, body, "deny", deny)
            return JSONResponse(
                status_code=403,
                content={"error": deny},
                headers=headers,
            )
    except httpx.ConnectError:
        # OPA not running — fall back to hardcoded checks
        if caller_tier == "commercial" and not settings.CPI_LICENCE_ACTIVE:
            _log_policy_eval(
                request, request_id, purpose, body, "deny", "cpi_licence_pending"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "error": "commercial_blocked",
                    "reason": "cpi_licence_pending",
                },
                headers=headers,
            )

    resource_id = body.get("resource_id")
    if resource_id:
        with get_origo_db() as conn:
            row = conn.execute(
                "SELECT fpic_status FROM startups WHERE id = ? OR nexus_id = ?",
                (resource_id, resource_id),
            ).fetchone()
            if row and row["fpic_status"] == "withdrawn":
                _log_policy_eval(
                    request, request_id, purpose, body, "deny", "fpic_withdrawn"
                )
                return JSONResponse(
                    status_code=403,
                    content={"error": "fpic_withdrawn"},
                    headers=headers,
                )

    _log_policy_eval(request, request_id, purpose, body, "allow", None)

    return JSONResponse(
        content={
            "allow": True,
            "ttl": 3600,
            "purpose": purpose,
            "request_id": request_id,
        },
        headers=headers,
    )


def _log_policy_eval(
    request: Request,
    request_id: str,
    purpose: str,
    body: dict,
    decision: str,
    deny_reason: str | None,
) -> None:
    try:
        with get_provenance_db() as conn:
            conn.execute(
                """INSERT INTO policy_evaluations
                   (id, caller_api_key_id, caller_tier, declared_purpose,
                    resource_type, resource_id, decision, deny_reason)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    getattr(request.state, "api_key_id", None),
                    getattr(request.state, "tier", "free"),
                    purpose,
                    body.get("resource_type"),
                    body.get("resource_id"),
                    decision,
                    deny_reason,
                ),
            )
            conn.commit()
    except Exception:
        pass
