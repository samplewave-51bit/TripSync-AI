"""
TripSync AI - Health, Ping & Diagnostic Endpoints
"""

import time
from fastapi import APIRouter, HTTPException, status

from backend.app.core.config import settings
from backend.app.core.database import check_database_health
from backend.app.core.logging import logger
from backend.app.schemas.health import HealthResponse, PingResponse

router = APIRouter()

# Uptime baseline tracking
START_TIME = time.time()


def get_ml_health_status():
    """Probes the recommendation engine readiness."""
    try:
        from ml_pipeline.src.inference import RecommendationEngine
        engine = RecommendationEngine.get_instance()
        return engine.health_check()
    except Exception as e:
        logger.warning(f"ML engine diagnostic probe warning: {str(e)}")
        return {
            "status": "degraded",
            "model_name": "Unknown",
            "catalog_destinations": 0,
            "feature_count": 0,
            "probe_latency_ms": 0.0,
            "is_ready_for_serving": False,
            "error": str(e),
        }


@router.get("/ping", response_model=PingResponse, summary="Basic connectivity ping")
def ping():
    """Ultra-low overhead ping endpoint for load balancer health probes."""
    return PingResponse(ping="pong", timestamp=time.time())


@router.get("/health", response_model=HealthResponse, summary="Comprehensive system health check")
def health_check():
    """
    Comprehensive health check probing:
    1. FastAPI process responsiveness & uptime
    2. Database connectivity & query execution time
    3. ML Recommendation Engine loading & readiness
    """
    db_health = check_database_health()
    ml_health = get_ml_health_status()

    is_overall_healthy = db_health["is_healthy"] and ml_health.get("is_ready_for_serving", False)

    return HealthResponse(
        status="healthy" if is_overall_healthy else "degraded",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=round(time.time() - START_TIME, 2),
        database=db_health,
        ml_engine=ml_health,
    )


@router.get("/ready", summary="Kubernetes / Render Readiness Probe")
def readiness_probe():
    """Returns 200 OK only when both Database and ML Engine are ready to serve traffic."""
    db_health = check_database_health()
    ml_health = get_ml_health_status()

    if not db_health["is_healthy"] or not ml_health.get("is_ready_for_serving", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "Service not ready to receive traffic",
                "database": db_health,
                "ml_engine": ml_health,
            },
        )
    return {"ready": True, "message": "All backend and ML dependencies initialized."}
