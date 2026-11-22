"""
TripSync AI - Indian Tourism Destinations & Attractions Catalog Models
"""

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from backend.app.models.base import Base, UUIDPrimaryKeyMixin


class Destination(Base, UUIDPrimaryKeyMixin):
    """Regional tourism destination cluster (City / Region in India)."""
    __tablename__ = "destinations"

    name = Column(String(255), nullable=False, index=True)  # City name (e.g. Jaipur, Agra, Mumbai)
    state = Column(String(100), nullable=False, index=True) # State name (e.g. Rajasthan, Uttar Pradesh)
    zone = Column(String(50), nullable=False, index=True)   # Northern, Southern, etc.
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    avg_cost_per_day = Column(Float, default=2500.0, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list, nullable=False)

    # Relationships
    attractions = relationship("Attraction", back_populates="destination")


class Attraction(Base, UUIDPrimaryKeyMixin):
    """Iconic tourist point of interest from verified Indian places dataset."""
    __tablename__ = "attractions"

    place_id = Column(Integer, unique=True, index=True, nullable=False)  # 1 to 323
    destination_id = Column(String(36), ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    zone = Column(String(50), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)  # Temple, Beach, Fort, Lake, etc.
    rating = Column(Float, default=0.0, nullable=False)
    entrance_fee_inr = Column(Float, default=0.0, nullable=False)
    time_needed_hrs = Column(Float, default=1.5, nullable=False)
    reviews_lakhs = Column(Float, default=0.0, nullable=False)
    weekly_off = Column(String(50), default="Open All Days", nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    significance = Column(String(255), nullable=True)
    dslr_allowed = Column(Boolean, default=True, nullable=False)
    best_time_to_visit = Column(String(100), default="All Day", nullable=False)
    budget_tier = Column(String(50), default="Budget", nullable=False)
    macro_category = Column(String(100), default="culture_heritage", nullable=False)
    thematic_vectors = Column(JSON, default=dict, nullable=False)

    # Relationships
    destination = relationship("Destination", back_populates="attractions")
    recommendations = relationship("Recommendation", back_populates="attraction", cascade="all, delete-orphan")
    itinerary_items = relationship("ItineraryItem", back_populates="attraction", cascade="all, delete-orphan")
