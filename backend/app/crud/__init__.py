"""
TripSync AI CRUD Repositories Package
"""

from backend.app.crud.crud_attraction import attraction, destination
from backend.app.crud.crud_user import user

__all__ = ["attraction", "destination", "user"]
