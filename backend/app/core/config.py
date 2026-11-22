"""
TripSync AI - Application Configuration & Environment Settings
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings managed via Pydantic BaseSettings."""

    # Project Information
    PROJECT_NAME: str = "TripSync AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "tripsync-insecure-secret-key-change-in-production-32bytesmin"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://tripsync-ai.pages.dev",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Database Configuration (PostgreSQL 15+ / SQLite fallback for testing)
    DATABASE_URL: str = "sqlite:///./tripsync.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # Zero-Cost Resource Pooling Configuration (Render Free Tier 512MB RAM)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 2
    DB_POOL_RECYCLE: int = 300  # Recycle connections every 5 mins to prevent stale sockets
    DB_POOL_TIMEOUT: int = 10   # 10s timeout to prevent hanging requests

    # ML Recommendation Engine Path
    ML_MODEL_PATH: str = "ml_pipeline/models/champion_model.joblib"
    ML_CATALOG_PATH: str = "ml_pipeline/data/processed/places_cleaned.csv"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
