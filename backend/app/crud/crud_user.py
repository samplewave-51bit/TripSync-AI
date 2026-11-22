"""
TripSync AI - User Repository with Authentication Primitives
"""

from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash, verify_password
from backend.app.crud.base import CRUDBase
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """Repository handling user entity lookups, authentication, and password updates."""

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    def create_with_password(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email.lower().strip(),
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name.strip(),
            avatar_url=obj_in.avatar_url,
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user_obj = self.get_by_email(db, email=email)
        if not user_obj:
            return None
        if not verify_password(password, user_obj.hashed_password):
            return None
        return user_obj

    def update_user(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            db_obj.hashed_password = hashed_password

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def is_active(self, user_obj: User) -> bool:
        return user_obj.is_active


user = CRUDUser(User)
