"""
TripSync AI - User Identity & Authentication Model
"""

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User account model for authentication and profile management."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    trips_created = relationship(
        "Trip",
        back_populates="creator",
        cascade="all, delete-orphan",
        foreign_keys="Trip.created_by",
    )
    trip_memberships = relationship(
        "TripMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    preferences = relationship(
        "Preference",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    votes = relationship(
        "Vote",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    budget_items = relationship(
        "BudgetItem",
        back_populates="creator",
    )
