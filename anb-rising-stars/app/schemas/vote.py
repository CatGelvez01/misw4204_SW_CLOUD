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
