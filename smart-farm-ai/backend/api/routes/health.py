"""Health check route."""

from datetime import datetime
from fastapi import APIRouter
from backend.data.validator import HealthResponse
from backend.utils.config import settings

router = APIRouter(tags=["Health"])

_start_time = datetime.utcnow()
_last_prediction_time = None


def set_last_prediction_time():
    global _last_prediction_time
    _last_prediction_time = datetime.utcnow().isoformat()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Report model status and uptime."""
    uptime = (datetime.utcnow() - _start_time).total_seconds()

    model_loaded = False
    try:
        from backend.api.main import get_model_pipeline
        pipeline = get_model_pipeline()
        model_loaded = pipeline is not None
    except Exception:
        pass

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_version=settings.model_version,
        uptime_seconds=uptime,
        model_loaded=model_loaded,
        last_prediction=_last_prediction_time
    )
