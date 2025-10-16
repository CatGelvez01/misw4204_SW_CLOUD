"""
Video schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.video import VideoStatus


class VideoUpload(BaseModel):
    """Schema for video upload."""

    title: str = Field(..., min_length=1, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Mi mejor tiro de 3",
            }
        }


class VideoResponse(BaseModel):
    """Schema for video response."""

    video_id: int = Field(..., alias="id")
    title: str
    status: VideoStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    processed_url: Optional[str] = None
    votes: int = 0

    class Config:
        from_attributes = True
        populate_by_name = True


class VideoDetailResponse(BaseModel):
    """Schema for detailed video response."""

    video_id: int = Field(..., alias="id")
    title: str
    status: VideoStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    original_url: Optional[str] = None
    processed_url: Optional[str] = None
    votes: int = 0

    class Config:
        from_attributes = True
        populate_by_name = True


class VideoDeleteResponse(BaseModel):
    """Schema for video deletion response."""

    message: str
    video_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "message": "El video ha sido eliminado exitosamente.",
                "video_id": "a1b2c3d4",
            }
        }
