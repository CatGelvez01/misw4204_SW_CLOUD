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

    video_id: str
    title: str
    status: VideoStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    processed_url: Optional[str] = None
    votes: int = 0

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "video_id": "123456",
                "title": "Mi mejor tiro de 3",
                "status": "processed",
                "uploaded_at": "2025-03-10T14:30:00Z",
                "processed_at": "2025-03-10T14:35:00Z",
                "processed_url": "http://localhost:8080/processed/123456.mp4",
                "votes": 0,
            }
        }


class VideoDetailResponse(BaseModel):
    """Schema for detailed video response."""

    video_id: str
    title: str
    status: VideoStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    original_url: Optional[str] = None
    processed_url: Optional[str] = None
    votes: int = 0

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "video_id": "a1b2c3d4",
                "title": "Tiros de tres en movimiento",
                "status": "processed",
                "uploaded_at": "2025-03-15T14:22:00Z",
                "processed_at": "2025-03-15T15:10:00Z",
                "original_url": "http://localhost:8080/uploads/a1b2c3d4.mp4",
                "processed_url": "http://localhost:8080/processed/a1b2c3d4.mp4",
                "votes": 125,
            }
        }


class VideoDeleteResponse(BaseModel):
    """Schema for video deletion response."""

    message: str
    video_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "El video ha sido eliminado exitosamente.",
                "video_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            }
        }


class VideoUploadResponse(BaseModel):
    """Schema for successful video upload response."""

    message: str
    task_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Video subido correctamente. Procesamiento en curso.",
                "task_id": "abc123def456",
            }
        }


class VideoUploadErrorResponse(BaseModel):
    """Schema for video upload error response."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Solo se permiten archivos MP4.",
            }
        }


class VideoErrorResponse(BaseModel):
    """Schema for video operation error response."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "El video no existe.",
            }
        }


class VideoForbiddenResponse(BaseModel):
    """Schema for forbidden video access response."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "No tienes permiso para acceder a este video.",
            }
        }


class VideoNotFoundResponse(BaseModel):
    """Schema for video not found response."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "El video no existe o no pertenece al usuario.",
            }
        }


class VideoBadRequestResponse(BaseModel):
    """Schema for video bad request response."""

    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "El video no puede ser eliminado porque no cumple las condiciones.",
            }
        }
