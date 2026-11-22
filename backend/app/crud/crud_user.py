"""
TripSync AI - User Repository
"""

from typing import Any, Optional
from sqlalchemy.orm import Session

from backend.app.crud.base import CRUDBase
from backend.app.models.user import User


class CRUDUser(CRUDBase[User, Any, Any]):
    """Repository handling user entity lookups."""

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()


user = CRUDUser(User)
