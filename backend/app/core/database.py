"""
TripSync AI - Database Engine, Session Factory & Connectivity Probes
Configured for zero-cost deployment on PostgreSQL 15+ (Supabase/Render) with SQLite fallback.
"""

import time
from typing import Any, Dict, Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from backend.app.core.config import settings
from backend.app.core.logging import logger

# Construct engine with pool parameters appropriate for dialect
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs: Dict[str, Any] = {
    "echo": settings.DEBUG,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production PostgreSQL pool bounds for 512MB RAM zero-cost limits
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_pre_ping": True,  # Eliminates stale connection errors on idle Free tier
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding isolated database session with automatic closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_health() -> Dict[str, Any]:
    """Probes database responsiveness, query execution time, and dialect."""
    t0 = time.perf_counter()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "status": "connected" if result == 1 else "unhealthy",
                "dialect": engine.dialect.name,
                "latency_ms": latency_ms,
                "is_healthy": bool(result == 1),
            }
    except Exception as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        logger.error(f"Database health probe failed: {str(e)}")
        return {
            "status": "disconnected",
            "dialect": engine.dialect.name,
            "latency_ms": latency_ms,
            "is_healthy": False,
            "error": str(e),
        }
