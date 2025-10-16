"""
Vote schemas for request/response validation.
"""

from pydantic import BaseModel


class VoteResponse(BaseModel):
    """Schema for vote response."""

    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Voto registrado exitosamente.",
            }
        }


class VoteDuplicateResponse(BaseModel):
    """Schema for duplicate vote error response."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Ya has votado por este video.",
            }
        }


class VoteNotFoundResponse(BaseModel):
    """Schema for video not found in vote error response."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "El video no existe.",
            }
        }


class RankingBadRequestResponse(BaseModel):
    """Schema for invalid ranking query parameter response."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Parámetro inválido en la consulta.",
            }
        }


class RankingEntry(BaseModel):
    """Schema for ranking entry."""

    position: int
    username: str
    city: str
    votes: int

    class Config:
        json_schema_extra = {
            "example": {
                "position": 1,
                "username": "superplayer",
                "city": "Bogotá",
                "votes": 1530,
            }
        }
