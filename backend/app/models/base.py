"""
TripSync AI - Base Declarative Models & Common Mixins
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy DeclarativeBase for TripSync AI schema."""
    pass


class UUIDPrimaryKeyMixin:
    """Provides standard UUIDv4 primary key across all entities."""
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )


class TimestampMixin:
    """Provides standardized created_at and updated_at audit timestamps."""
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
