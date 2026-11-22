"""
TripSync AI - AI Recommendations, Voting, Budgeting & Itinerary Models
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.app.models.base import Base, UUIDPrimaryKeyMixin


class Recommendation(Base, UUIDPrimaryKeyMixin):
    """Snapshot of AI Social Choice recommendation outputs for a trip."""
    __tablename__ = "recommendations"

    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    attraction_id = Column(String(36), ForeignKey("attractions.id", ondelete="CASCADE"), nullable=False, index=True)
    group_score = Column(Float, nullable=False)
    lowest_member_score = Column(Float, nullable=False)
    agreement_index = Column(Float, default=1.0, nullable=False)
    rank = Column(Integer, nullable=False)
    explanation_breakdown = Column(JSON, default=dict, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trip = relationship("Trip", back_populates="recommendations")
    attraction = relationship("Attraction", back_populates="recommendations")


class Vote(Base, UUIDPrimaryKeyMixin):
    """Member preference vote on candidate attractions or destinations."""
    __tablename__ = "votes"

    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String(32), default="ATTRACTION", nullable=False)  # ATTRACTION or DESTINATION
    target_id = Column(String(36), nullable=False, index=True)
    vote_value = Column(Integer, default=1, nullable=False)  # +1 (approve), -1 (veto), 0 (abstain)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("trip_id", "user_id", "target_type", "target_id", name="uq_trip_vote"),
    )

    # Relationships
    trip = relationship("Trip", back_populates="votes")
    user = relationship("User", back_populates="votes")


class BudgetItem(Base, UUIDPrimaryKeyMixin):
    """Collaborative expense item tracked within a trip."""
    __tablename__ = "budget_items"

    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(100), default="Activities", nullable=False)
    title = Column(String(255), nullable=False)
    estimated_cost = Column(Float, default=0.0, nullable=False)
    actual_cost = Column(Float, default=0.0, nullable=False)
    split_method = Column(String(32), default="EQUAL", nullable=False)  # EQUAL, CUSTOM
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trip = relationship("Trip", back_populates="budget_items")
    creator = relationship("User", back_populates="budget_items")


class ItineraryDay(Base, UUIDPrimaryKeyMixin):
    """Calendar day grouping for trip scheduling."""
    __tablename__ = "itinerary_days"

    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=True)

    # Relationships
    trip = relationship("Trip", back_populates="itinerary_days")
    items = relationship("ItineraryItem", back_populates="day", cascade="all, delete-orphan", order_by="ItineraryItem.sort_order")


class ItineraryItem(Base, UUIDPrimaryKeyMixin):
    """Scheduled attraction stop within an itinerary day."""
    __tablename__ = "itinerary_items"

    itinerary_day_id = Column(String(36), ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False, index=True)
    attraction_id = Column(String(36), ForeignKey("attractions.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(String(10), nullable=True)  # "09:30"
    end_time = Column(String(10), nullable=True)    # "11:30"
    sort_order = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    day = relationship("ItineraryDay", back_populates="items")
    attraction = relationship("Attraction", back_populates="itinerary_items")
