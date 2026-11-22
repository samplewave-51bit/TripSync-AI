"""
TripSync AI - FastAPI Application Factory & Main Entrypoint
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.v1.api import api_router
from backend.app.core.config import settings
from backend.app.core.database import check_database_health
from backend.app.core.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager:
    1. Initializes structured logging
    2. Probes database connectivity on startup
    3. Pre-warms the ML recommendation engine in memory
    """
    setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")

    # 1. Probe database
    db_status = check_database_health()
    if db_status["is_healthy"]:
        logger.info(f"Database connected successfully ({db_status['dialect']}) in {db_status['latency_ms']}ms")
    else:
        logger.warning(f"Database check warning on startup: {db_status}")

    # 2. Pre-warm ML Recommendation Engine
    try:
        from ml_pipeline.src.inference import RecommendationEngine
        engine = RecommendationEngine.get_instance()
        probe = engine.health_check()
        logger.info(f"ML Recommendation Engine pre-warmed: {probe['model_name']} with {probe['catalog_destinations']} places")
    except Exception as e:
        logger.error(f"Failed to pre-warm ML Recommendation Engine: {str(e)}")

    yield

    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global unhandled exception safety barrier."""
    logger.error(f"Unhandled exception on {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", summary="Root API Index")
def root_index():
    """Root redirect with basic API metadata."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health",
        "ping": f"{settings.API_V1_STR}/ping",
    }
