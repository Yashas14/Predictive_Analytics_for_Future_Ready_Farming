"""App entrypoint — FastAPI setup, model loading, route registration."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.middleware import add_cors_middleware, logging_middleware
from backend.api.database import init_db
from backend.api.routes import health, predict, analytics, upload
from backend.ml.pipeline import load_pipeline, load_metadata, ALL_PIPELINE_FEATURES
from backend.ml.explainability import ModelExplainer
from backend.utils.config import settings
from backend.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

# Global model state
_pipeline = None
_explainer = None
_metadata = None


def get_model_pipeline():
    return _pipeline


def get_explainer():
    return _explainer


def get_metadata():
    return _metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model + explainer on startup, cleanup on shutdown."""
    global _pipeline, _explainer, _metadata
    
    setup_logging()
    logger.info("application_starting", version=settings.model_version)
    
    # Initialize database
    init_db()
    logger.info("database_initialized")
    
    # Load model
    try:
        model_path = settings.abs_model_path
        if model_path.exists():
            _pipeline = load_pipeline(model_path)
            _metadata = load_metadata()
            
            # Initialize SHAP explainer
            feature_names = _metadata.get("feature_names", ALL_PIPELINE_FEATURES)
            _explainer = ModelExplainer(_pipeline, feature_names)
            
            logger.info("model_loaded_successfully", path=str(model_path))
        else:
            logger.warning(
                "model_not_found",
                path=str(model_path),
                message="API will start without model. Train the model first."
            )
    except Exception as e:
        logger.error("model_loading_failed", error=str(e))
    
    yield
    
    # Cleanup
    logger.info("application_shutting_down")


app = FastAPI(
    title="AgriSense AI",
    description="Agricultural yield prediction API (RF + XGBoost + LightGBM ensemble with SHAP).",
    version=settings.model_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

add_cors_middleware(app)
app.middleware("http")(logging_middleware)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(predict.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)
app.include_router(upload.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Serve the frontend SPA."""
    frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {
        "name": "AgriSense AI API",
        "version": settings.model_version,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }


# Mount static files AFTER all API routes
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
