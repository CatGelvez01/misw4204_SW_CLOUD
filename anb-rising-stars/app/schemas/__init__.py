"""Pydantic schemas for request/response validation."""

from app.schemas.user import (
    UserRegister,
    UserLogin,
    ErrorResponse,
    UnauthorizedResponse,
    SignupResponse,
    TokenResponse,
)
from app.schemas.video import (
    VideoUpload,
    VideoResponse,
    VideoDetailResponse,
    VideoDeleteResponse,
    VideoUploadResponse,
    VideoUploadErrorResponse,
    VideoForbiddenResponse,
    VideoNotFoundResponse,
    VideoBadRequestResponse,
)
from app.schemas.vote import VoteResponse, RankingEntry

__all__ = [
    "UserRegister",
    "UserLogin",
    "ErrorResponse",
    "UnauthorizedResponse",
    "SignupResponse",
    "TokenResponse",
    "VideoUpload",
    "VideoResponse",
    "VideoDetailResponse",
    "VideoDeleteResponse",
    "VideoUploadResponse",
    "VideoUploadErrorResponse",
    "VideoForbiddenResponse",
    "VideoNotFoundResponse",
    "VideoBadRequestResponse",
    "VoteResponse",
    "RankingEntry",
]
