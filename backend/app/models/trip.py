"""
TripSync AI - Trip Collaboration, Membership & Member Preferences Models
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Trip(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Collaborative group travel workspace entity."""
    __tablename__ = "trips"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    invite_code = Column(String(32), unique=True, index=True, nullable=False)
    status = Column(String(32), default="PLANNING", nullable=False)  # PLANNING, CONFIRMED, COMPLETED

    # Relationships
    creator = relationship("User", back_populates="trips_created", foreign_keys=[created_by])
    members = relationship("TripMember", back_populates="trip", cascade="all, delete-orphan")
    preferences = relationship("Preference", back_populates="trip", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="trip", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="trip", cascade="all, delete-orphan")
    budget_items = relationship("BudgetItem", back_populates="trip", cascade="all, delete-orphan")
    itinerary_days = relationship("ItineraryDay", back_populates="trip", cascade="all, delete-orphan")


class TripMember(Base, UUIDPrimaryKeyMixin):
    """Junction table associating users with trips in specific roles."""
    __tablename__ = "trip_members"

    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), default="MEMBER", nullable=False)  # OWNER, EDITOR, MEMBER, VIEWER
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("trip_id", "user_id", name="uq_trip_member"),
    )

    # Relationships
    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="trip_memberships")


class Preference(Base, UUIDPrimaryKeyMixin):
    """Individual member travel constraints and preference survey per trip."""
    __tablename__ = "preferences"

    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    budget_min = Column(Float, default=0.0, nullable=False)
    budget_max = Column(Float, default=50000.0, nullable=False)
    pace_preference = Column(String(32), default="MODERATE", nullable=False)  # FAST, MODERATE, SLOW
    category_weights = Column(JSON, default=dict, nullable=False)  # {"culture": 0.8, "nature": 0.5, ...}
    dietary_restrictions = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("trip_id", "user_id", name="uq_trip_user_preference"),
    )

    # Relationships
    trip = relationship("Trip", back_populates="preferences")
    user = relationship("User", back_populates="preferences")
