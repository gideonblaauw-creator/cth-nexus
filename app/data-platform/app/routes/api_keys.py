from __future__ import annotations

import uuid

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import get_apikeys_db
from app.middleware.auth import generate_api_key
from app.models import ApiKeyCreateRequest
from app.response import make_request_id, standard_headers

router = APIRouter(prefix="/v1/api-keys", tags=["api-keys"])


@router.post("")
def create_api_key(request: Request, body: ApiKeyCreateRequest):
    request_id = getattr(request.state, "request_id", make_request_id())
    headers = standard_headers(request_id)

    client_ip = request.client.host if request.client else "unknown"
    if client_ip not in settings.ALLOWED_INTERNAL_IPS:
        return JSONResponse(
            status_code=403,
            content={"error": "internal_only"},
            headers=headers,
        )

    if body.tier not in ("research", "commercial"):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_tier", "valid": ["research", "commercial"]},
            headers=headers,
        )

    valid_purposes = ["research", "eudr", "csrd", "carbon", "internal"]
    if body.declared_purpose not in valid_purposes:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_purpose", "valid": valid_purposes},
            headers=headers,
        )

    key_id = str(uuid.uuid4())
    raw_key, key_hash = generate_api_key()
    key_prefix = raw_key[:8]

    with get_apikeys_db() as conn:
        conn.execute(
            """INSERT INTO api_keys
               (id, key_hash, key_prefix, tier, declared_purpose,
                organisation, contact_email)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                key_id,
                key_hash,
                key_prefix,
                body.tier,
                body.declared_purpose,
                body.organisation,
                body.contact_email,
            ),
        )
        conn.commit()

    return JSONResponse(
        status_code=201,
        content={
            "id": key_id,
            "raw_key": raw_key,
            "key_prefix": key_prefix,
            "tier": body.tier,
            "declared_purpose": body.declared_purpose,
            "message": "Store this key securely. It will not be shown again.",
        },
        headers=headers,
    )
