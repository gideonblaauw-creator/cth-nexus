from __future__ import annotations

import hashlib
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.database import get_provenance_db


class ProvenanceMiddleware(BaseHTTPMiddleware):
    """Logs every request to provenance_log (W3C PROV-O style).
    Non-blocking: log failures do not break the response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = getattr(request.state, "request_id", None) or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)

        try:
            client_ip = request.client.host if request.client else "unknown"
            ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()

            with get_provenance_db() as conn:
                conn.execute(
                    """INSERT INTO provenance_log
                       (id, entity_id, entity_type, action, actor_id, actor_tier,
                        declared_purpose, request_id, ip_hash, user_agent,
                        response_status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        str(uuid.uuid4()),
                        None,
                        None,
                        request.method.lower(),
                        getattr(request.state, "api_key_id", None) or "anonymous",
                        getattr(request.state, "tier", "free"),
                        getattr(request.state, "declared_purpose", None),
                        request_id,
                        ip_hash,
                        request.headers.get("user-agent", ""),
                        response.status_code,
                    ),
                )
                conn.commit()
        except Exception:
            pass

        return response
