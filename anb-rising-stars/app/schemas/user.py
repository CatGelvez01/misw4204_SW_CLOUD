"""
User schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password1: str = Field(..., min_length=8)
    password2: str = Field(..., min_length=8)
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "city": "Bogotá",
                "country": "Colombia",
            }
        }


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "StrongPass123",
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error response (400)."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {"detail": "El correo electrónico ya está registrado."}
        }


class UnauthorizedResponse(BaseModel):
    """Schema for unauthorized response (401)."""

    detail: str

    class Config:
        json_schema_extra = {"example": {"detail": "Credenciales inválidas."}}


class SignupResponse(BaseModel):
    """Schema for signup response."""

    message: str
    user_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Usuario creado exitosamente.",
                "user_id": 1,
            }
        }


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
        }
