"""
Authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.models import User
from app.schemas import (
    UserRegister,
    UserLogin,
    ErrorResponse,
    UnauthorizedResponse,
    SignupResponse,
    TokenResponse,
)

router = APIRouter()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=SignupResponse,
    responses={400: {"model": ErrorResponse, "description": "Validación fallida"}},
)
async def signup(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new player.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        SignupResponse: Success message with user ID

    Raises:
        HTTPException: If email already exists or passwords don't match
    """
    # Validate passwords match
    if user_data.password1 != user_data.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden.",
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado.",
        )

    # Create new user
    hashed_password = hash_password(user_data.password1)
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=hashed_password,
        city=user_data.city,
        country=user_data.country,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Usuario creado exitosamente.",
        "user_id": new_user.id,
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": UnauthorizedResponse, "description": "Credenciales inválidas"}
    },
)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    Args:
        credentials: User login credentials
        db: Database session

    Returns:
        TokenResponse: JWT token and expiration time

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )
