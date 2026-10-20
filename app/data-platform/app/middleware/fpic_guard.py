from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.config import settings

SAFE_FPIC_STATUSES = ("approved", "not_required")


class FPICGuardMiddleware(BaseHTTPMiddleware):
    """ABSOLUTE guard — no override. Queries may not return rows with
    fpic_status = 'pending' or 'withdrawn'. Commercial tier blocked if
    CPI licence inactive."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        tier = getattr(request.state, "tier", "free")

        if tier == "commercial" and not settings.CPI_LICENCE_ACTIVE:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "commercial_blocked",
                    "reason": "cpi_licence_pending",
                },
            )

        request.state.fpic_filter = SAFE_FPIC_STATUSES

        return await call_next(request)
