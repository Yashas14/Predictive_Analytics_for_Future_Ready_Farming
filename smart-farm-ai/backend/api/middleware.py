"""Request middleware — CORS and per-request logging."""

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
import time
import structlog

logger = structlog.get_logger()


def add_cors_middleware(app):
    """Wide-open CORS for dev. Tighten allow_origins in production."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def logging_middleware(request: Request, call_next):
    """Log method, path, status, and duration for every request."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        "request_processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2)
    )

    return response
