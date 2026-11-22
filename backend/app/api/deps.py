"""
TripSync AI - FastAPI Dependency Injection Primitives
Provides database session and authenticated user injection.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.crud.crud_user import user as crud_user
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Validates JWT access token and returns authenticated database user entity."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if not user_id:
        raise credentials_exception

    user_obj = crud_user.get(db, id=user_id)
    if not user_obj:
        raise credentials_exception

    if not crud_user.is_active(user_obj):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    return user_obj


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Secondary guard ensuring user account is currently active."""
    return current_user
