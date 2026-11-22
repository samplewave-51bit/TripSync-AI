"""
TripSync AI Models Package - Aggregated Declarative Model Exports
"""

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.destination import Attraction, Destination
from backend.app.models.planning import (
    BudgetItem,
    ItineraryDay,
    ItineraryItem,
    Recommendation,
    Vote,
)
from backend.app.models.trip import Preference, Trip, TripMember
from backend.app.models.user import User

__all__ = [
    "Base",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "User",
    "Trip",
    "TripMember",
    "Preference",
    "Destination",
    "Attraction",
    "Recommendation",
    "Vote",
    "BudgetItem",
    "ItineraryDay",
    "ItineraryItem",
]
