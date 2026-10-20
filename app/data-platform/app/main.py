from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_all_dbs
from app.middleware.auth import AuthMiddleware
from app.middleware.fpic_guard import FPICGuardMiddleware
from app.middleware.provenance import ProvenanceMiddleware
from app.response import make_request_id, standard_headers
from app.routes import api_keys, catalogue, credentials, health, policy, startups, submissions, taxonomy
from app.routes import public_eudr
from app.services.rate_limiter import limiter

app = FastAPI(
    title="CleantechHUB Data Platform",
    version=settings.DATASET_VERSION,
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
    debug=False,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware stack — order matters: last added = first executed
# Execution order: Provenance → FPIC Guard → Auth → Route
app.add_middleware(ProvenanceMiddleware)
app.add_middleware(FPICGuardMiddleware)
app.add_middleware(AuthMiddleware)

# Routers
app.include_router(startups.router)
app.include_router(taxonomy.router)
app.include_router(catalogue.router)
app.include_router(policy.router)
app.include_router(api_keys.router)
app.include_router(credentials.router)
app.include_router(submissions.router)
app.include_router(health.router)
app.include_router(public_eudr.router)


@app.on_event("startup")
def on_startup():
    init_all_dbs()


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", make_request_id())
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "request_id": request_id},
        headers=standard_headers(request_id),
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    request_id = getattr(request.state, "request_id", make_request_id())
    return JSONResponse(
        status_code=404,
        content={"error": "not_found"},
        headers=standard_headers(request_id),
    )
