from __future__ import annotations

import hashlib
import secrets
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.database import get_apikeys_db


def generate_api_key() -> tuple[str, str]:
    raw = "ctk_" + secrets.token_urlsafe(32)
    stored = hashlib.sha256(raw.encode()).hexdigest()
    return raw, stored


def verify_api_key(provided: str, stored_hash: str) -> bool:
    h = hashlib.sha256(provided.encode()).hexdigest()
    return secrets.compare_digest(h, stored_hash)


KEYED_PATHS: set[str] = set()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.api_key_id = None
        request.state.tier = "free"
        request.state.declared_purpose = None

        auth_header = request.headers.get("Authorization", "")
        api_key: str | None = None
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]
        elif request.query_params.get("api_key"):
            api_key = request.query_params["api_key"]

        if api_key:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            with get_apikeys_db() as conn:
                row = conn.execute(
                    "SELECT id, tier, declared_purpose, revoked_at "
                    "FROM api_keys WHERE key_hash = ?",
                    (key_hash,),
                ).fetchone()
            if row is None:
                return JSONResponse(
                    status_code=403,
                    content={"error": "invalid_api_key"},
                )
            if row["revoked_at"] is not None:
                return JSONResponse(
                    status_code=403,
                    content={"error": "invalid_api_key"},
                )
            request.state.api_key_id = row["id"]
            request.state.tier = row["tier"]
            request.state.declared_purpose = row["declared_purpose"]

            with get_apikeys_db() as conn:
                conn.execute(
                    "UPDATE api_keys SET last_used_at = datetime('now') WHERE id = ?",
                    (row["id"],),
                )
                conn.commit()

        if request.url.path in KEYED_PATHS and not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "api_key_required", "docs": "/v1/docs"},
            )

        return await call_next(request)
