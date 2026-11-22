"""
TripSync AI - Authentication & User Profile Endpoints
Provides registration, login (JSON and OAuth2 form), current user inspection, and profile updates.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import create_access_token
from backend.app.crud.crud_user import user as crud_user
from backend.app.models.user import User
from backend.app.schemas.user import Token, UserCreate, UserLogin, UserResponse, UserUpdate

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register new traveler account")
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Creates a new user profile, validates email uniqueness, and issues an initial JWT token."""
    existing_user = crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists in the system.",
        )

    user_obj = crud_user.create_with_password(db, obj_in=user_in)
    access_token = create_access_token(subject=user_obj.id)

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserResponse.model_validate(user_obj),
    )


@router.post("/login", response_model=Token, summary="Authenticate user via JSON credentials")
def login(
    *,
    db: Session = Depends(get_db),
    login_data: UserLogin,
) -> Any:
    """Authenticates email and password via JSON payload, returning a signed JWT access token."""
    user_obj = crud_user.authenticate(
        db, email=login_data.email, password=login_data.password
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud_user.is_active(user_obj):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    access_token = create_access_token(subject=user_obj.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserResponse.model_validate(user_obj),
    )


@router.post("/login/access-token", response_model=Token, summary="OAuth2 standard form login")
def login_access_token(
    *,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """OAuth2 compatible token login for Swagger UI and form submissions."""
    user_obj = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud_user.is_active(user_obj):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    access_token = create_access_token(subject=user_obj.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserResponse.model_validate(user_obj),
    )


@router.get("/me", response_model=UserResponse, summary="Retrieve current authenticated traveler profile")
def read_current_user(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Returns profile details of the user associated with the Bearer JWT token."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, summary="Update current traveler profile")
def update_current_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Updates profile attributes (name, avatar, or password) for the authenticated user."""
    updated_user = crud_user.update_user(db, db_obj=current_user, obj_in=user_in)
    return UserResponse.model_validate(updated_user)
