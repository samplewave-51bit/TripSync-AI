"""
TripSync AI - Health & System Readiness Schemas
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    ping: str = "pong"
    timestamp: float


class DatabaseHealth(BaseModel):
    status: str
    dialect: str
    latency_ms: float
    is_healthy: bool
    error: Optional[str] = None


class MLEngineHealth(BaseModel):
    status: str
    model_name: str
    catalog_destinations: int
    feature_count: int
    probe_latency_ms: float
    is_ready_for_serving: bool


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    uptime_seconds: float
    database: DatabaseHealth
    ml_engine: MLEngineHealth
