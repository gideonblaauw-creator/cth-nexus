from __future__ import annotations

import uuid

from app.config import settings
from app.models import Meta


def make_request_id() -> str:
    return str(uuid.uuid4())


def make_meta(total: int, limit: int, offset: int, request_id: str) -> Meta:
    return Meta(
        total=total,
        limit=limit,
        offset=offset,
        request_id=request_id,
        dataset_version=settings.DATASET_VERSION,
        last_updated=settings.LAST_UPDATED,
    )


def standard_headers(request_id: str) -> dict[str, str]:
    return {
        "X-CTH-Environment": settings.DATA_PLATFORM_ENV,
        "X-CTH-Dataset-Version": settings.DATASET_VERSION,
        "X-CTH-Last-Updated": settings.LAST_UPDATED,
        "X-CTH-Licence": "CC BY-NC-SA 4.0",
        "X-Request-ID": request_id,
    }
